"""Tests for merchant shop-hour enforcement via TriggerHandler and ScheduleManager."""

from typing import Any, Optional
import unittest
from unittest import mock

from core.entities import NPC
from core.npc_schedules import ScheduleEntry, NPCSchedule, ScheduleManager
from core.time_system import TimeOfDay
from core.world import Map, Tile, World
from engine.world import TriggerHandler


class _DummyPlayer:
    """Minimal player stub with position and inventory."""

    def __init__(self, x: int = 0, y: int = 0) -> None:
        self.x = x
        self.y = y
        self.inventory: Optional[Any] = None

    def set_position(self, x: int, y: int) -> None:
        self.x = x
        self.y = y


class _DummyManager:
    """Minimal SceneManager-like stub that can return managers by name."""

    def __init__(self) -> None:
        self._managers: dict[str, Any] = {}

    def get_manager(self, name: str, _: str) -> Any:
        return self._managers.get(name)

    def set_manager(self, name: str, manager: Any) -> None:
        self._managers[name] = manager


class _DummyScene:
    """Minimal WorldScene-like stub for TriggerHandler tests."""

    def __init__(self, world: World, player: _DummyPlayer) -> None:
        self.world = world
        self.player = player
        self.manager = _DummyManager()
        self.puzzle_manager = None
        self.quest_manager = None
        self.assets = None
        self.scale = 1

        # Methods TriggerHandler expects but we won't exercise here
        self._last_blocked_trigger: Optional[str] = None

        # Track side effects
        self.started_dialogues: list[str] = []
        self.inline_messages: list[str] = []
        self.pending_shop_for: Optional[str] = None
        self.opened_shops: list[NPC] = []

    # Scene helper for manager access used by TriggerHandler
    def get_manager_attr(self, name: str, context: str) -> Any:  # noqa: ARG002
        if not self.manager:
            return None
        return self.manager.get_manager(name, context)

    # Hooks used by TriggerHandler in shop interaction path
    def _start_dialogue(self, dialogue_id: str) -> None:
        self.started_dialogues.append(dialogue_id)

    def _show_inline_message(self, message: str) -> None:
        self.inline_messages.append(message)

    def _resolve_dialogue_for_npc(self, npc: NPC) -> Optional[str]:  # noqa: D401
        """Return the NPC's dialogue_id directly for tests."""
        return npc.dialogue_id

    def _open_shop(self, npc: NPC) -> None:
        self.opened_shops.append(npc)

    # WorldScene normally provides this helper; tests patch its return value.
    def _find_nearby_npc(self) -> Optional[NPC]:
        return None


class TestMerchantScheduleEnforcement(unittest.TestCase):
    """Tests that merchant NPCs respect ScheduleManager-based shop hours."""

    def _make_world_with_single_npc(self, npc: NPC) -> World:
        """Create a minimal world containing a single NPC on a simple map."""
        tiles = [[Tile(tile_id="floor", walkable=True, sprite_id="floor")]]
        test_map = Map(map_id="test_map", width=1, height=1, tiles=tiles)

        world = World()
        world.add_map(test_map)
        world.set_current_map("test_map")
        world.set_map_entities("test_map", [npc])
        return world

    def _make_schedule_manager_for_npc(
        self, npc_id: str, open_periods: set[TimeOfDay], closed_periods: set[TimeOfDay]
    ) -> ScheduleManager:
        """Create a ScheduleManager with explicit open/closed entries for an NPC."""
        entries: list[ScheduleEntry] = []
        for period in open_periods:
            entries.append(
                ScheduleEntry(
                    time_periods=[period],
                    map_id="test_map",
                    x=0,
                    y=0,
                    activity="working",
                    shop_available=True,
                    alternative_dialogue_id=None,
                )
            )
        for period in closed_periods:
            entries.append(
                ScheduleEntry(
                    time_periods=[period],
                    map_id="test_map",
                    x=0,
                    y=0,
                    activity="sleeping",
                    shop_available=False,
                    alternative_dialogue_id="closed_dialogue",
                )
            )

        schedule = NPCSchedule(
            npc_id=npc_id,
            default_map_id="test_map",
            default_x=0,
            default_y=0,
            entries=entries,
        )
        return ScheduleManager(schedules={npc_id: schedule})

    def test_role_based_merchant_respects_closed_hours(self) -> None:
        """Merchant with role='merchant' and schedule closes shop during closed period."""
        npc = NPC(
            entity_id="merchant_npc",
            name="Test Merchant",
            x=0,
            y=0,
            sprite_id="npc",
        )
        npc.role = "merchant"
        npc.dialogue_id = "merchant_dialogue"

        world = self._make_world_with_single_npc(npc)
        player = _DummyPlayer(x=0, y=0)
        scene = _DummyScene(world, player)

        # Merchant is open at NOON but closed at NIGHT
        schedule_mgr = self._make_schedule_manager_for_npc(
            npc.entity_id,
            open_periods={TimeOfDay.NOON},
            closed_periods={TimeOfDay.NIGHT},
        )
        day_night_cycle = mock.Mock()
        day_night_cycle.get_time_of_day.return_value = TimeOfDay.NIGHT

        scene.manager.set_manager("schedule_manager", schedule_mgr)
        scene.manager.set_manager("day_night_cycle", day_night_cycle)

        # No tutorial manager to keep the test focused on schedule behavior
        handler = TriggerHandler(scene)

        with mock.patch.object(scene, "_find_nearby_npc", return_value=npc):
            handler.interact()

        # Shop should not open during closed hours
        self.assertEqual(scene.opened_shops, [])
        # Either alternative dialogue or closed inline message should be shown
        self.assertTrue(
            scene.started_dialogues or scene.inline_messages,
            "Expected closed shop to show dialogue or inline message.",
        )

    def test_role_based_merchant_default_open_without_schedule(self) -> None:
        """Merchant with role='merchant' but no schedule remains open (backwards compatible)."""
        npc = NPC(
            entity_id="unscheduled_merchant",
            name="Always Open Merchant",
            x=0,
            y=0,
            sprite_id="npc",
        )
        npc.role = "merchant"

        world = self._make_world_with_single_npc(npc)
        player = _DummyPlayer(x=0, y=0)
        scene = _DummyScene(world, player)

        # No schedule_manager registered
        handler = TriggerHandler(scene)

        with mock.patch.object(scene, "_find_nearby_npc", return_value=npc):
            handler.interact()

        # Shop should open immediately since there's no schedule to restrict it
        self.assertEqual(scene.opened_shops, [npc])

    def test_shop_id_merchant_behavior_unchanged(self) -> None:
        """Merchant with shop_id still uses schedule manager and closes appropriately."""
        npc = NPC(
            entity_id="shop_id_merchant",
            name="ShopId Merchant",
            x=0,
            y=0,
            sprite_id="npc",
        )
        npc.role = "merchant"
        npc.shop_id = "test_shop"

        world = self._make_world_with_single_npc(npc)
        player = _DummyPlayer(x=0, y=0)
        scene = _DummyScene(world, player)

        schedule_mgr = self._make_schedule_manager_for_npc(
            npc.entity_id,
            open_periods={TimeOfDay.MORNING},
            closed_periods={TimeOfDay.EVENING},
        )
        day_night_cycle = mock.Mock()
        day_night_cycle.get_time_of_day.return_value = TimeOfDay.EVENING

        scene.manager.set_manager("schedule_manager", schedule_mgr)
        scene.manager.set_manager("day_night_cycle", day_night_cycle)

        handler = TriggerHandler(scene)

        with mock.patch.object(scene, "_find_nearby_npc", return_value=npc):
            handler.interact()

        # Shop should be closed in the configured closed period
        self.assertEqual(scene.opened_shops, [])
        self.assertTrue(
            scene.started_dialogues or scene.inline_messages,
            "Expected closed shop to show dialogue or inline message.",
        )


if __name__ == "__main__":
    unittest.main()

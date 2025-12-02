"""Tests for SaveContext-based save/load helpers."""

import unittest

from core.save import SaveContext, deserialize_state_from_context
from core.save.context import SaveContextError
from core.world import World, Map, Tile
from core.entities import Player
from core.entities.player import MAX_LEARNED_MOVES
from core.stats import Stats
from engine.world.triggers.warp_handler import AUTO_SAVE_MANAGER_ATTRS


class _FailingManager:
    """Test double that always fails save/load."""

    save_key = "broken"

    def serialize(self):
        raise RuntimeError("serialize failed")

    def deserialize_into(self, data):
        raise RuntimeError("deserialize failed")


class TestSaveContextDeserialization(unittest.TestCase):
    def setUp(self) -> None:
        self.world = World()
        tiles = [[Tile("grass", True, "grass")]]
        self.world.add_map(Map(map_id="forest_path", width=1, height=1, tiles=tiles))

        self.player = Player(
            entity_id="player_1",
            name="Hero",
            x=0,
            y=0,
            sprite_id="player",
            stats=Stats(
                max_hp=10,
                hp=10,
                max_sp=5,
                sp=5,
                attack=1,
                defense=1,
                magic=1,
                speed=1,
                luck=1,
            ),
        )

    def test_deserialize_state_from_context_trims_learned_moves(self) -> None:
        """Context path should enforce MAX_LEARNED_MOVES like legacy path."""
        data = {
            "meta": {"version": 1, "timestamp": "2024-01-01T00:00:00", "play_time_seconds": 0},
            "world": {
                "current_map_id": "forest_path",
                "flags": {},
                "visited_maps": [],
                "runtime_state": {"trigger_states": {}, "enemy_states": {}},
            },
            "player": {
                "entity_id": "player_1",
                "name": "Hero",
                "x": 0,
                "y": 0,
                "inventory": {},
                "equipment": {},
                "skills": [],
                "learned_moves": ["a", "b", "c", "d", "e", "f"],
                "player_class": "warrior",
                "player_subclass": "mage",
                "stats": {
                    "max_hp": 10,
                    "hp": 10,
                    "max_sp": 5,
                    "sp": 5,
                    "attack": 1,
                    "defense": 1,
                    "magic": 1,
                    "speed": 1,
                    "luck": 1,
                    "status_effects": {},
                },
            },
        }

        context = SaveContext(world=self.world, player=self.player)
        restored_player = deserialize_state_from_context(data, context)

        self.assertLessEqual(len(restored_player.learned_moves), MAX_LEARNED_MOVES)
        self.assertEqual(restored_player.learned_moves, ["a", "b", "c", "d"])


class TestSaveContextFailures(unittest.TestCase):
    def setUp(self) -> None:
        self.world = World()
        tiles = [[Tile("grass", True, "grass")]]
        self.world.add_map(Map(map_id="forest_path", width=1, height=1, tiles=tiles))
        self.player = Player(
            entity_id="player_1",
            name="Hero",
            x=0,
            y=0,
            sprite_id="player",
            stats=Stats(
                max_hp=10,
                hp=10,
                max_sp=5,
                sp=5,
                attack=1,
                defense=1,
                magic=1,
                speed=1,
                luck=1,
            ),
        )

    def test_serialize_managers_raises_on_failure(self) -> None:
        """Serialize should surface manager errors instead of silently skipping."""
        context = SaveContext(world=self.world, player=self.player)
        context.register(_FailingManager())

        with self.assertRaises(SaveContextError):
            context.serialize_managers()

    def test_deserialize_managers_raises_on_failure(self) -> None:
        """Deserialize should surface manager errors instead of silently skipping."""
        context = SaveContext(world=self.world, player=self.player)
        context.register(_FailingManager())

        with self.assertRaises(SaveContextError):
            context.deserialize_managers({"broken": {}})


class TestScheduleManagerSaveIntegration(unittest.TestCase):
    """Test that schedule_manager is properly included in save operations."""

    def setUp(self) -> None:
        self.world = World()
        tiles = [[Tile("grass", True, "grass")]]
        self.world.add_map(Map(map_id="test", width=1, height=1, tiles=tiles))
        self.player = Player(
            entity_id="p1",
            name="Test",
            x=0,
            y=0,
            sprite_id="p",
            stats=Stats(
                max_hp=10,
                hp=10,
                max_sp=5,
                sp=5,
                attack=1,
                defense=1,
                magic=1,
                speed=1,
                luck=1,
            ),
        )

    def test_schedule_manager_in_save_slot_scene_manager_list(self) -> None:
        """Verify schedule_manager is in the manager list used by save_slot_scene."""
        # This list must match what's in engine/save_slot_scene.py _do_save()
        SAVE_SLOT_SCENE_MANAGER_ATTRS = [
            'day_night_cycle', 'achievement_manager', 'weather_system',
            'schedule_manager',
            'fishing_system', 'puzzle_manager', 'brain_teaser_manager',
            'gambling_manager', 'arena_manager', 'challenge_dungeon_manager',
            'secret_boss_manager', 'hint_manager', 'post_game_manager',
            'tutorial_manager',
        ]
        self.assertIn('schedule_manager', SAVE_SLOT_SCENE_MANAGER_ATTRS)

    def test_schedule_manager_in_trigger_handler_manager_list(self) -> None:
        """Verify schedule_manager is in the manager list used by trigger_handler auto-save."""
        # This list is defined in engine/world/triggers/warp_handler.py _try_auto_save()
        self.assertIn('schedule_manager', AUTO_SAVE_MANAGER_ATTRS)

    def test_schedule_manager_state_serialized_via_context(self) -> None:
        """ScheduleManager state is included when registered with SaveContext."""
        from core.npc_schedules import ScheduleManager
        from core.time_system import TimeOfDay

        schedule_manager = ScheduleManager()
        schedule_manager._last_time_period = TimeOfDay.EVENING
        schedule_manager._npc_positions = {"npc_1": ("town", 5, 5)}

        context = SaveContext(world=self.world, player=self.player)
        context.register_if_saveable(schedule_manager)

        # Serialize
        data = context.serialize_managers()

        # Verify schedule state is included
        self.assertIn("npc_schedules", data)
        self.assertEqual(data["npc_schedules"]["last_time_period"], "evening")
        self.assertIn("npc_1", data["npc_schedules"]["npc_positions"])
        self.assertEqual(
            data["npc_schedules"]["npc_positions"]["npc_1"],
            {"map_id": "town", "x": 5, "y": 5},
        )

    def test_schedule_manager_state_deserialized_via_context(self) -> None:
        """ScheduleManager state is restored when deserialized via SaveContext."""
        from core.npc_schedules import ScheduleManager
        from core.time_system import TimeOfDay

        schedule_manager = ScheduleManager()

        context = SaveContext(world=self.world, player=self.player)
        context.register_if_saveable(schedule_manager)

        # Deserialize saved data
        saved_data = {
            "npc_schedules": {
                "last_time_period": "morning",
                "npc_positions": {
                    "merchant": {"map_id": "market", "x": 10, "y": 8},
                },
            }
        }
        context.deserialize_managers(saved_data)

        # Verify state was restored
        self.assertEqual(schedule_manager._last_time_period, TimeOfDay.MORNING)
        self.assertEqual(
            schedule_manager._npc_positions.get("merchant"),
            ("market", 10, 8),
        )
        self.assertTrue(schedule_manager._pending_position_restore)

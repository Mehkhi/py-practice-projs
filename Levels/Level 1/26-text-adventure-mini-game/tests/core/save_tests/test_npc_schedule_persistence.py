"""Integration tests for NPC schedule persistence through SaveManager + SaveContext.

These tests ensure that ScheduleManager state (last_time_period and npc_positions)
round-trips correctly when using the context-based SaveManager API that writes
real save files to disk.
"""

import os
import tempfile
import unittest

from core.npc_schedules import NPCSchedule, ScheduleEntry, ScheduleManager
from core.save import SaveContext
from core.save_load import SaveManager
from core.time_system import TimeOfDay
from core.world import Map, Tile, World
from core.entities import NPC, Player
from core.stats import Stats


class TestNpcSchedulePersistenceWithContext(unittest.TestCase):
    """Full round-trip tests for ScheduleManager using SaveManager + SaveContext."""

    def setUp(self) -> None:
        # Use a temporary directory so we don't touch the real saves folder
        self.temp_dir = tempfile.mkdtemp()
        self.save_manager = SaveManager(save_dir=self.temp_dir)

        # Minimal world with two maps so we can verify map changes if needed
        tiles_home = [[Tile("grass", True, "grass") for _ in range(3)] for _ in range(3)]
        tiles_inn = [[Tile("grass", True, "grass") for _ in range(3)] for _ in range(3)]

        self.world = World()
        self.home_map = Map("home", 3, 3, tiles_home)
        self.inn_map = Map("inn", 3, 3, tiles_inn)
        self.world.add_map(self.home_map)
        self.world.add_map(self.inn_map)
        self.world.set_current_map("home")

        # Simple player – stats are required by Player but not important for this test
        stats = Stats(
            max_hp=10,
            hp=10,
            max_sp=5,
            sp=5,
            attack=1,
            defense=1,
            magic=1,
            speed=1,
            luck=1,
        )
        self.player = Player(
            entity_id="player_1",
            name="Hero",
            x=0,
            y=0,
            sprite_id="player",
            stats=stats,
        )

        # NPC that will be controlled by ScheduleManager
        self.npc = NPC(
            entity_id="npc_1",
            name="Sleeper",
            x=0,
            y=0,
            sprite_id="npc",
        )
        self.world.set_map_entities("home", [self.npc])

    def tearDown(self) -> None:
        # Clean up temp directory and any files we created
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _create_schedule_manager(self) -> ScheduleManager:
        """Create a ScheduleManager with a simple schedule for npc_1."""
        # At NIGHT the NPC should be at the inn (2, 1)
        night_entry = ScheduleEntry(
            time_periods=[TimeOfDay.NIGHT],
            map_id="inn",
            x=2,
            y=1,
        )
        schedule = NPCSchedule(
            npc_id="npc_1",
            default_map_id="home",
            default_x=0,
            default_y=0,
            entries=[night_entry],
        )
        return ScheduleManager(schedules={"npc_1": schedule})

    def test_schedule_manager_state_round_trips_via_context_save(self) -> None:
        """ScheduleManager last_time_period and npc_positions survive a full context round-trip."""
        schedule_manager = self._create_schedule_manager()

        # First update world so that ScheduleManager tracks a last_time_period
        # and records the NPC's position. We don't move the NPC here – we just
        # want non-empty internal state.
        moved_initial = schedule_manager.update(self.world, TimeOfDay.NIGHT)
        # It's fine if nothing moved (e.g., if NPC wasn't found), but we expect
        # _last_time_period and _npc_positions to be populated for npc_1.
        self.assertIn("npc_1", schedule_manager._npc_positions)

        context = SaveContext(world=self.world, player=self.player)
        context.register_if_saveable(schedule_manager)

        # Save to an actual file using the context-based API
        self.save_manager.save_to_slot_with_context(1, context)
        save_path = os.path.join(self.temp_dir, "save_1.json")
        self.assertTrue(os.path.exists(save_path))

        # Build a fresh world + player + schedule_manager to prove we only rely on saved data
        new_world = World()
        new_world.add_map(self.home_map)
        new_world.add_map(self.inn_map)
        new_world.set_current_map("home")

        new_npc = NPC(
            entity_id="npc_1",
            name="Sleeper",
            x=0,
            y=0,
            sprite_id="npc",
        )
        new_world.set_map_entities("home", [new_npc])

        new_player = Player(
            entity_id="player_1",
            name="Hero",
            x=0,
            y=0,
            sprite_id="player",
            stats=self.player.stats,
        )

        new_schedule_manager = self._create_schedule_manager()

        new_context = SaveContext(world=new_world, player=new_player)
        new_context.register_if_saveable(new_schedule_manager)

        # Load via the context-based API
        self.save_manager.load_from_slot_with_context(1, new_context)

        # After load, ScheduleManager should have restored last_time_period and npc_positions.
        # The saved state should exactly match what was serialized before the round-trip.
        self.assertEqual(new_schedule_manager._last_time_period, TimeOfDay.NIGHT)
        self.assertIn("npc_1", new_schedule_manager._npc_positions)
        map_id, x, y = new_schedule_manager._npc_positions["npc_1"]
        self.assertEqual((map_id, x, y), ("inn", 2, 1))

        # Because npc_positions was populated, the pending restore flag should be set
        self.assertTrue(new_schedule_manager._pending_position_restore)

        # On the next update, the NPC should be moved to the saved position first,
        # then the normal schedule update logic will run.
        moved_after_load = new_schedule_manager.update(new_world, TimeOfDay.NIGHT)
        self.assertIn("npc_1", moved_after_load)

        # NPC should now be on the inn map at the scheduled coordinates
        inn_entities = new_world.get_map_entities("inn")
        self.assertIn(new_npc, inn_entities)
        self.assertEqual((new_npc.x, new_npc.y), (2, 1))

    def test_schedule_manager_round_trip_without_positions_forces_refresh(self) -> None:
        """Context round-trip with no npc_positions should still allow schedule-driven movement.

        This simulates older saves that only recorded last_time_period; after load
        we expect ScheduleManager to perform a fresh schedule update rather than
        trying to restore explicit positions.
        """
        schedule_manager = self._create_schedule_manager()

        # Manually set last_time_period but leave npc_positions empty, as if from
        # an older save file.
        schedule_manager._last_time_period = TimeOfDay.NIGHT
        schedule_manager._npc_positions = {}

        context = SaveContext(world=self.world, player=self.player)
        context.register_if_saveable(schedule_manager)

        # Save to disk with the legacy-style state (no positions)
        self.save_manager.save_to_slot_with_context(1, context)

        # Fresh world/NPC/player/manager as before
        new_world = World()
        new_world.add_map(self.home_map)
        new_world.add_map(self.inn_map)
        new_world.set_current_map("home")

        new_npc = NPC(
            entity_id="npc_1",
            name="Sleeper",
            x=0,
            y=0,
            sprite_id="npc",
        )
        new_world.set_map_entities("home", [new_npc])

        new_player = Player(
            entity_id="player_1",
            name="Hero",
            x=0,
            y=0,
            sprite_id="player",
            stats=self.player.stats,
        )

        new_schedule_manager = self._create_schedule_manager()

        new_context = SaveContext(world=new_world, player=new_player)
        new_context.register_if_saveable(new_schedule_manager)

        # Load via context API
        self.save_manager.load_from_slot_with_context(1, new_context)

        # Because there were no npc_positions, the manager should have kept
        # last_time_period but be configured for a fresh schedule refresh.
        self.assertEqual(new_schedule_manager._last_time_period, TimeOfDay.NIGHT)
        self.assertEqual(new_schedule_manager._npc_positions, {})
        self.assertFalse(new_schedule_manager._pending_position_restore)
        # _force_schedule_refresh is internal, but behaviorally we expect the next
        # update to move the NPC according to the schedule.

        moved = new_schedule_manager.update(new_world, TimeOfDay.NIGHT)
        self.assertIn("npc_1", moved)

        # After update, NPC should be on the inn map at the scheduled coordinates
        inn_entities = new_world.get_map_entities("inn")
        self.assertIn(new_npc, inn_entities)
        self.assertEqual((new_npc.x, new_npc.y), (2, 1))


if __name__ == "__main__":
    unittest.main()

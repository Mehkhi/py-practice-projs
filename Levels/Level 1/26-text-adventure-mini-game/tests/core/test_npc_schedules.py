"""Unit tests for core/npc_schedules.py - NPC scheduling system."""

import unittest
from unittest.mock import Mock, MagicMock

from core.npc_schedules import ScheduleEntry, NPCSchedule, ScheduleManager
from core.time_system import TimeOfDay
from core.world import Map, World, Tile
from core.entities import NPC


class TestScheduleEntry(unittest.TestCase):
    def test_schedule_entry_creation(self):
        entry = ScheduleEntry(
            time_periods=[TimeOfDay.MORNING, TimeOfDay.NOON],
            map_id="forest_path",
            x=5,
            y=7,
            activity="working",
        )
        self.assertEqual(len(entry.time_periods), 2)
        self.assertEqual(entry.map_id, "forest_path")
        self.assertEqual(entry.x, 5)
        self.assertEqual(entry.y, 7)
        self.assertEqual(entry.activity, "working")

    def test_schedule_entry_optional_activity(self):
        entry = ScheduleEntry(
            time_periods=[TimeOfDay.NIGHT],
            map_id="home",
            x=2,
            y=3,
        )
        self.assertIsNone(entry.activity)


class TestNPCSchedule(unittest.TestCase):
    def test_npc_schedule_creation(self):
        entry = ScheduleEntry(
            time_periods=[TimeOfDay.MORNING],
            map_id="shop",
            x=3,
            y=4,
        )
        schedule = NPCSchedule(
            npc_id="merchant",
            default_map_id="home",
            default_x=1,
            default_y=1,
            entries=[entry],
        )
        self.assertEqual(schedule.npc_id, "merchant")
        self.assertEqual(schedule.default_map_id, "home")
        self.assertEqual(len(schedule.entries), 1)

    def test_npc_schedule_empty_entries(self):
        schedule = NPCSchedule(
            npc_id="npc",
            default_map_id="map",
            default_x=0,
            default_y=0,
        )
        self.assertEqual(len(schedule.entries), 0)


class TestScheduleManager(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        # Create a simple schedule for testing
        entry1 = ScheduleEntry(
            time_periods=[TimeOfDay.MORNING, TimeOfDay.NOON],
            map_id="shop",
            x=5,
            y=7,
            activity="working",
        )
        entry2 = ScheduleEntry(
            time_periods=[TimeOfDay.EVENING, TimeOfDay.NIGHT],
            map_id="home",
            x=2,
            y=3,
            activity="sleeping",
        )
        schedule = NPCSchedule(
            npc_id="test_npc",
            default_map_id="default_map",
            default_x=0,
            default_y=0,
            entries=[entry1, entry2],
        )
        self.manager = ScheduleManager(schedules={"test_npc": schedule})

    def test_get_npc_location_matching_entry(self):
        """Test that correct entry is selected for each time period."""
        # Test MORNING matches first entry
        map_id, x, y = self.manager.get_npc_location("test_npc", TimeOfDay.MORNING)
        self.assertEqual(map_id, "shop")
        self.assertEqual(x, 5)
        self.assertEqual(y, 7)

        # Test NOON matches first entry
        map_id, x, y = self.manager.get_npc_location("test_npc", TimeOfDay.NOON)
        self.assertEqual(map_id, "shop")
        self.assertEqual(x, 5)
        self.assertEqual(y, 7)

        # Test EVENING matches second entry
        map_id, x, y = self.manager.get_npc_location("test_npc", TimeOfDay.EVENING)
        self.assertEqual(map_id, "home")
        self.assertEqual(x, 2)
        self.assertEqual(y, 3)

    def test_get_npc_location_default_fallback(self):
        """Test that default location is used when no entry matches."""
        # DAWN is not in any entry, should use default
        map_id, x, y = self.manager.get_npc_location("test_npc", TimeOfDay.DAWN)
        self.assertEqual(map_id, "default_map")
        self.assertEqual(x, 0)
        self.assertEqual(y, 0)

    def test_get_npc_location_missing_npc(self):
        """Test that missing NPC returns empty location."""
        map_id, x, y = self.manager.get_npc_location("nonexistent", TimeOfDay.MORNING)
        self.assertEqual(map_id, "")
        self.assertEqual(x, 0)
        self.assertEqual(y, 0)

    def test_get_npc_activity_matching_entry(self):
        """Test that correct activity is returned for matching time period."""
        activity = self.manager.get_npc_activity("test_npc", TimeOfDay.MORNING)
        self.assertEqual(activity, "working")

        activity = self.manager.get_npc_activity("test_npc", TimeOfDay.EVENING)
        self.assertEqual(activity, "sleeping")

    def test_get_npc_activity_no_match(self):
        """Test that None is returned when no entry matches."""
        activity = self.manager.get_npc_activity("test_npc", TimeOfDay.DAWN)
        self.assertIsNone(activity)

    def test_get_npc_activity_missing_npc(self):
        """Test that None is returned for missing NPC."""
        activity = self.manager.get_npc_activity("nonexistent", TimeOfDay.MORNING)
        self.assertIsNone(activity)

    def test_update_skips_same_period(self):
        """Test that update doesn't process when time period hasn't changed."""
        # Create a mock world
        world = Mock(spec=World)
        world.maps = {}
        world.map_entities = {}
        world.npc_interaction_active = False
        world.get_entity_by_id = Mock(return_value=None)

        # First update should process
        result1 = self.manager.update(world, TimeOfDay.MORNING)
        # Second update with same period should skip
        result2 = self.manager.update(world, TimeOfDay.MORNING)

        # First update may return empty list (no NPCs found), but second should definitely be empty
        # because it was skipped
        self.assertEqual(result2, [])

    def test_update_moves_npcs(self):
        """Test that NPCs actually move when time period changes."""
        # Create mock maps
        shop_map = Mock(spec=Map)
        shop_map.map_id = "shop"
        shop_map.is_walkable = Mock(return_value=True)

        home_map = Mock(spec=Map)
        home_map.map_id = "home"
        home_map.is_walkable = Mock(return_value=True)

        # Create mock NPC
        npc = Mock(spec=NPC)
        npc.entity_id = "test_npc"
        npc.x = 0
        npc.y = 0
        npc.set_position = Mock()

        # Create world with NPC on shop map
        world = Mock(spec=World)
        world.maps = {"shop": shop_map, "home": home_map}
        world.map_entities = {"shop": [npc]}
        world.npc_interaction_active = False
        world.get_entity_by_id = Mock(return_value=("shop", npc))
        world.move_entity_to_map = Mock(return_value=True)

        # Update to EVENING (should move to home)
        moved = self.manager.update(world, TimeOfDay.EVENING)

        # Verify NPC was moved
        self.assertIn("test_npc", moved)
        # Verify move_entity_to_map was called
        world.move_entity_to_map.assert_called_once_with("test_npc", "shop", "home", 2, 3)

    def test_update_skips_when_position_unchanged(self):
        """Test that update skips NPCs that are already in correct position."""
        # Create mock map
        shop_map = Mock(spec=Map)
        shop_map.map_id = "shop"
        shop_map.is_walkable = Mock(return_value=True)

        # Create mock NPC already at correct position
        npc = Mock(spec=NPC)
        npc.entity_id = "test_npc"
        npc.x = 5
        npc.y = 7
        npc.set_position = Mock()

        # Create world
        world = Mock(spec=World)
        world.maps = {"shop": shop_map}
        world.map_entities = {"shop": [npc]}
        world.npc_interaction_active = False
        world.get_entity_by_id = Mock(return_value=("shop", npc))
        world.move_entity_to_map = Mock(return_value=True)

        # Update to MORNING (NPC already at shop 5,7)
        moved = self.manager.update(world, TimeOfDay.MORNING)

        # NPC should not be moved (already in correct position)
        self.assertNotIn("test_npc", moved)
        npc.set_position.assert_not_called()

    def test_find_nearest_walkable(self):
        """Test finding nearest walkable tile when target is blocked."""
        # Create a map with walkable tiles
        tiles = [
            [Tile("wall", False, "wall"), Tile("grass", True, "grass"), Tile("grass", True, "grass")],
            [Tile("grass", True, "grass"), Tile("wall", False, "wall"), Tile("grass", True, "grass")],
            [Tile("grass", True, "grass"), Tile("grass", True, "grass"), Tile("grass", True, "grass")],
        ]
        map_obj = Map("test_map", 3, 3, tiles)

        manager = ScheduleManager()

        # Target position (1, 1) is blocked, should find nearest walkable
        result = manager._find_nearest_walkable(map_obj, 1, 1, max_radius=3)
        self.assertIsNotNone(result)
        x, y = result
        # Should find one of the adjacent walkable tiles
        self.assertTrue((x, y) in [(0, 1), (2, 1), (1, 0), (1, 2), (0, 0), (0, 2), (2, 0), (2, 2)])

    def test_find_nearest_walkable_target_walkable(self):
        """Test that target position is returned if it's walkable."""
        tiles = [
            [Tile("grass", True, "grass"), Tile("grass", True, "grass")],
            [Tile("grass", True, "grass"), Tile("grass", True, "grass")],
        ]
        map_obj = Map("test_map", 2, 2, tiles)

        manager = ScheduleManager()
        result = manager._find_nearest_walkable(map_obj, 1, 1, max_radius=3)
        self.assertEqual(result, (1, 1))

    def test_find_nearest_walkable_no_walkable_found(self):
        """Test that None is returned when no walkable tile is found."""
        # Create a map with all walls
        tiles = [
            [Tile("wall", False, "wall"), Tile("wall", False, "wall")],
            [Tile("wall", False, "wall"), Tile("wall", False, "wall")],
        ]
        map_obj = Map("test_map", 2, 2, tiles)

        manager = ScheduleManager()
        result = manager._find_nearest_walkable(map_obj, 1, 1, max_radius=1)
        self.assertIsNone(result)

    def test_blocked_position_handling(self):
        """Test that NPC finds alternate position if target is blocked."""
        # Create maps
        shop_tiles = [
            [Tile("wall", False, "wall"), Tile("grass", True, "grass")],
            [Tile("grass", True, "grass"), Tile("grass", True, "grass")],
        ]
        shop_map = Map("shop", 2, 2, shop_tiles)

        # Create NPC starting at different position
        npc = Mock(spec=NPC)
        npc.entity_id = "test_npc"
        npc.x = 1
        npc.y = 1
        npc.set_position = Mock()

        # Create schedule with blocked target position
        entry = ScheduleEntry(
            time_periods=[TimeOfDay.MORNING],
            map_id="shop",
            x=0,  # Blocked position
            y=0,
        )
        schedule = NPCSchedule(
            npc_id="test_npc",
            default_map_id="shop",
            default_x=1,
            default_y=1,
            entries=[entry],
        )
        manager = ScheduleManager(schedules={"test_npc": schedule})

        # Create world
        world = Mock(spec=World)
        world.maps = {"shop": shop_map}
        world.map_entities = {"shop": [npc]}
        world.npc_interaction_active = False
        world.get_entity_by_id = Mock(return_value=("shop", npc))
        # move_entity_to_map will find nearest walkable and succeed
        world.move_entity_to_map = Mock(return_value=True)

        # Update should find alternate position (NPC needs to move from 1,1 to 0,0, but 0,0 is blocked)
        moved = manager.update(world, TimeOfDay.MORNING)
        self.assertIn("test_npc", moved)
        # Should have called move_entity_to_map
        world.move_entity_to_map.assert_called_once()
        # Verify it was called with the correct parameters
        call_args = world.move_entity_to_map.call_args[0]
        self.assertEqual(call_args[0], "test_npc")
        self.assertEqual(call_args[1], "shop")
        self.assertEqual(call_args[2], "shop")
        self.assertEqual(call_args[3], 0)  # target x
        self.assertEqual(call_args[4], 0)  # target y


class TestScheduleManagerSaveable(unittest.TestCase):
    def test_save_key_exists(self):
        """Test that save_key is defined."""
        self.assertTrue(hasattr(ScheduleManager, "save_key"))
        self.assertEqual(ScheduleManager.save_key, "npc_schedules")

    def test_serialize_returns_dict(self):
        """Test that serialize returns a dictionary with expected keys."""
        manager = ScheduleManager()
        data = manager.serialize()
        self.assertIsInstance(data, dict)
        self.assertIn("last_time_period", data)
        self.assertIn("npc_positions", data)

    def test_serialize_with_last_time_period(self):
        """Test serialization when last_time_period is set."""
        manager = ScheduleManager()
        manager._last_time_period = TimeOfDay.NOON
        data = manager.serialize()
        self.assertEqual(data["last_time_period"], TimeOfDay.NOON.value)

    def test_serialize_includes_npc_positions(self):
        """Test that serialize captures tracked NPC positions."""
        manager = ScheduleManager()
        manager._npc_positions = {"npc_1": ("town_square", 2, 3)}

        data = manager.serialize()

        self.assertIn("npc_positions", data)
        self.assertEqual(
            data["npc_positions"]["npc_1"],
            {"map_id": "town_square", "x": 2, "y": 3},
        )

    def test_serialize_without_last_time_period(self):
        """Test serialization when no time period has been processed."""
        manager = ScheduleManager()
        manager._last_time_period = None
        data = manager.serialize()
        self.assertIsNone(data["last_time_period"])

    def test_deserialize_into_restores_state(self):
        """Test that deserialize_into restores last_time_period."""
        manager = ScheduleManager()
        manager.deserialize_into({"last_time_period": TimeOfDay.EVENING.value})
        self.assertEqual(manager._last_time_period, TimeOfDay.EVENING)

    def test_deserialize_into_handles_missing_data(self):
        """Test that missing data clears last_time_period without error."""
        manager = ScheduleManager()
        manager._last_time_period = TimeOfDay.MORNING
        manager.deserialize_into({})
        self.assertIsNone(manager._last_time_period)

    def test_deserialize_restores_positions_on_update(self):
        """Saved positions should be applied even if time period matches."""
        tiles = [[Tile("grass", True, "grass") for _ in range(3)] for _ in range(3)]
        world = World()
        world.add_map(Map("home", 3, 3, tiles))
        world.add_map(Map("inn", 3, 3, tiles))

        npc = NPC(
            entity_id="npc_1",
            name="Sleeper",
            x=0,
            y=0,
            sprite_id="npc",
        )
        world.set_map_entities("home", [npc])

        schedule = NPCSchedule(
            npc_id="npc_1",
            default_map_id="home",
            default_x=0,
            default_y=0,
            entries=[],
        )
        manager = ScheduleManager(schedules={"npc_1": schedule})

        manager.deserialize_into(
            {
                "last_time_period": TimeOfDay.NIGHT.value,
                "npc_positions": {"npc_1": {"map_id": "inn", "x": 2, "y": 1}},
            }
        )

        moved = manager.update(world, TimeOfDay.NIGHT)

        self.assertIn("npc_1", moved)
        self.assertIn(npc, world.get_map_entities("inn"))
        self.assertEqual((npc.x, npc.y), (2, 1))

    def test_deserialize_without_positions_forces_schedule_update(self):
        """Old saves without npc_positions should still allow repositioning."""
        tiles = [[Tile("grass", True, "grass") for _ in range(3)] for _ in range(3)]
        world = World()
        world.add_map(Map("home", 3, 3, tiles))
        world.add_map(Map("shop", 3, 3, tiles))

        npc = NPC(
            entity_id="npc_legacy",
            name="Legacy NPC",
            x=0,
            y=0,
            sprite_id="npc",
        )
        world.set_map_entities("home", [npc])

        entry = ScheduleEntry(
            time_periods=[TimeOfDay.MORNING],
            map_id="shop",
            x=1,
            y=1,
        )
        schedule = NPCSchedule(
            npc_id="npc_legacy",
            default_map_id="home",
            default_x=0,
            default_y=0,
            entries=[entry],
        )
        manager = ScheduleManager(schedules={"npc_legacy": schedule})
        manager._last_time_period = TimeOfDay.MORNING

        manager.deserialize_into({"last_time_period": TimeOfDay.MORNING.value})

        moved = manager.update(world, TimeOfDay.MORNING)

        self.assertIn("npc_legacy", moved)
        self.assertIn(npc, world.get_map_entities("shop"))
        self.assertEqual((npc.x, npc.y), (1, 1))


class TestScheduleLoading(unittest.TestCase):
    def test_schedule_loading(self):
        """Test that JSON loading produces valid ScheduleManager."""
        from core.data_loader import load_npc_schedules
        import os

        # Load schedules from actual file
        filepath = os.path.join("data", "npc_schedules.json")
        manager = load_npc_schedules(filepath)

        # Should have loaded schedules
        self.assertIsInstance(manager, ScheduleManager)
        # Should have at least one schedule (we created 3 in the JSON)
        self.assertGreater(len(manager.schedules), 0)

        # Verify a specific schedule was loaded correctly
        if "forest_merchant" in manager.schedules:
            schedule = manager.schedules["forest_merchant"]
            self.assertEqual(schedule.npc_id, "forest_merchant")
            self.assertEqual(schedule.default_map_id, "forest_path")
            self.assertGreater(len(schedule.entries), 0)

    def test_schedule_loading_missing_file(self):
        """Test that loading missing file returns empty manager."""
        from core.data_loader import load_npc_schedules

        manager = load_npc_schedules("nonexistent_file.json")
        self.assertIsInstance(manager, ScheduleManager)
        self.assertEqual(len(manager.schedules), 0)


if __name__ == "__main__":
    unittest.main()

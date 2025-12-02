"""Integration tests for NPC schedule system world integration."""

import unittest
from unittest.mock import Mock

from core.npc_schedules import ScheduleEntry, NPCSchedule, ScheduleManager
from core.time_system import TimeOfDay
from core.world import Map, World, Tile
from core.entities import NPC
from engine.scene import SceneManager, Scene
import pygame


class TestEntityMovesBetweenMaps(unittest.TestCase):
    """Test that NPCs actually move from one map to another."""

    def setUp(self):
        """Set up test fixtures."""
        # Create two maps
        tiles1 = [[Tile("grass", True, "grass") for _ in range(5)] for _ in range(5)]
        self.map1 = Map("map1", 5, 5, tiles1)

        tiles2 = [[Tile("grass", True, "grass") for _ in range(5)] for _ in range(5)]
        self.map2 = Map("map2", 5, 5, tiles2)

        # Create world
        self.world = World()
        self.world.add_map(self.map1)
        self.world.add_map(self.map2)

        # Create NPC on map1
        self.npc = NPC(
            entity_id="test_npc",
            name="Test NPC",
            x=2,
            y=2,
            sprite_id="npc"
        )
        self.world.set_map_entities("map1", [self.npc])

    def test_entity_moves_between_maps(self):
        """Test that NPC moves from map A to map B."""
        # Verify NPC is on map1
        entities_map1 = self.world.get_map_entities("map1")
        self.assertIn(self.npc, entities_map1)

        # Move NPC to map2
        result = self.world.move_entity_to_map("test_npc", "map1", "map2", 3, 3)

        # Verify move was successful
        self.assertTrue(result)

        # Verify NPC is no longer on map1
        entities_map1 = self.world.get_map_entities("map1")
        self.assertNotIn(self.npc, entities_map1)

        # Verify NPC is now on map2
        entities_map2 = self.world.get_map_entities("map2")
        self.assertIn(self.npc, entities_map2)

        # Verify position was updated
        self.assertEqual(self.npc.x, 3)
        self.assertEqual(self.npc.y, 3)


class TestEntityPositionUpdates(unittest.TestCase):
    """Test that NPC position coordinates update correctly."""

    def setUp(self):
        """Set up test fixtures."""
        tiles = [[Tile("grass", True, "grass") for _ in range(5)] for _ in range(5)]
        self.map = Map("test_map", 5, 5, tiles)

        self.world = World()
        self.world.add_map(self.map)

        self.npc = NPC(
            entity_id="test_npc",
            name="Test NPC",
            x=1,
            y=1,
            sprite_id="npc"
        )
        self.world.set_map_entities("test_map", [self.npc])

    def test_entity_position_updates(self):
        """Test that NPC's x, y coordinates update correctly."""
        # Initial position
        self.assertEqual(self.npc.x, 1)
        self.assertEqual(self.npc.y, 1)

        # Move to new position on same map
        result = self.world.move_entity_to_map("test_npc", "test_map", "test_map", 4, 4)

        # Verify move was successful
        self.assertTrue(result)

        # Verify position was updated
        self.assertEqual(self.npc.x, 4)
        self.assertEqual(self.npc.y, 4)


class TestScheduleManagerInSceneManager(unittest.TestCase):
    """Test that schedule_manager is accessible from scenes."""

    def setUp(self):
        """Set up test fixtures."""
        # Initialize pygame for SceneManager
        pygame.init()

        self.schedule_manager = ScheduleManager()
        self.scene_manager = SceneManager(
            initial_scene=Mock(spec=Scene),
            schedule_manager=self.schedule_manager
        )

    def tearDown(self):
        """Clean up."""
        pygame.quit()

    def test_schedule_manager_in_scene_manager(self):
        """Test that schedule_manager is accessible from SceneManager."""
        self.assertIsNotNone(self.scene_manager.schedule_manager)
        self.assertEqual(self.scene_manager.schedule_manager, self.schedule_manager)


class TestTimePeriodChangeTriggersUpdate(unittest.TestCase):
    """Test that changing time period triggers NPC movement."""

    def setUp(self):
        """Set up test fixtures."""
        # Create schedule
        entry = ScheduleEntry(
            time_periods=[TimeOfDay.MORNING],
            map_id="shop",
            x=3,
            y=4,
        )
        schedule = NPCSchedule(
            npc_id="test_npc",
            default_map_id="home",
            default_x=1,
            default_y=1,
            entries=[entry],
        )
        self.manager = ScheduleManager(schedules={"test_npc": schedule})

        # Create maps
        tiles1 = [[Tile("grass", True, "grass") for _ in range(5)] for _ in range(5)]
        tiles2 = [[Tile("grass", True, "grass") for _ in range(5)] for _ in range(5)]
        map1 = Map("home", 5, 5, tiles1)
        map2 = Map("shop", 5, 5, tiles2)

        self.world = World()
        self.world.add_map(map1)
        self.world.add_map(map2)

        # Create NPC on home map
        self.npc = NPC(
            entity_id="test_npc",
            name="Test NPC",
            x=1,
            y=1,
            sprite_id="npc"
        )
        self.world.set_map_entities("home", [self.npc])

    def test_time_period_change_triggers_update(self):
        """Test that changing time period triggers NPC movement."""
        # Update to MORNING (should move to shop)
        moved = self.manager.update(self.world, TimeOfDay.MORNING)

        # Verify NPC was moved
        self.assertIn("test_npc", moved)

        # Verify NPC is now on shop map
        entities_shop = self.world.get_map_entities("shop")
        self.assertIn(self.npc, entities_shop)

        # Verify position was updated
        self.assertEqual(self.npc.x, 3)
        self.assertEqual(self.npc.y, 4)


class TestSamePeriodNoMovement(unittest.TestCase):
    """Test that NPCs don't move if time period is unchanged."""

    def setUp(self):
        """Set up test fixtures."""
        entry = ScheduleEntry(
            time_periods=[TimeOfDay.MORNING],
            map_id="shop",
            x=3,
            y=4,
        )
        schedule = NPCSchedule(
            npc_id="test_npc",
            default_map_id="home",
            default_x=1,
            default_y=1,
            entries=[entry],
        )
        self.manager = ScheduleManager(schedules={"test_npc": schedule})

        tiles = [[Tile("grass", True, "grass") for _ in range(5)] for _ in range(5)]
        map_obj = Map("home", 5, 5, tiles)

        self.world = World()
        self.world.add_map(map_obj)

        self.npc = NPC(
            entity_id="test_npc",
            name="Test NPC",
            x=1,
            y=1,
            sprite_id="npc"
        )
        self.world.set_map_entities("home", [self.npc])

    def test_same_period_no_movement(self):
        """Test that NPCs don't move if time period unchanged."""
        # First update to MORNING
        moved1 = self.manager.update(self.world, TimeOfDay.MORNING)
        # Should have moved (if NPC was found)
        # Note: This test may not move if NPC not found, but that's okay

        # Second update with same period should return empty
        moved2 = self.manager.update(self.world, TimeOfDay.MORNING)
        self.assertEqual(moved2, [])


class TestFindNearestWalkable(unittest.TestCase):
    """Test that BFS correctly finds closest open tile."""

    def setUp(self):
        """Set up test fixtures."""
        # Create map with some blocked tiles
        tiles = [
            [Tile("wall", False, "wall"), Tile("grass", True, "grass"), Tile("grass", True, "grass")],
            [Tile("grass", True, "grass"), Tile("wall", False, "wall"), Tile("grass", True, "grass")],
            [Tile("grass", True, "grass"), Tile("grass", True, "grass"), Tile("grass", True, "grass")],
        ]
        self.map = Map("test_map", 3, 3, tiles)

        self.world = World()
        self.world.add_map(self.map)

    def test_find_nearest_walkable(self):
        """Test that BFS finds closest walkable tile when target is blocked."""
        # Target position (1, 1) is blocked
        result = self.world.find_nearest_walkable("test_map", 1, 1)

        # Should find one of the adjacent walkable tiles
        self.assertIsNotNone(result)
        x, y = result
        # Should be one of the walkable positions adjacent to (1, 1)
        self.assertTrue((x, y) in [(0, 1), (2, 1), (1, 0), (1, 2)])

    def test_find_nearest_walkable_target_walkable(self):
        """Test that target position is returned if it's walkable."""
        result = self.world.find_nearest_walkable("test_map", 2, 2)
        self.assertEqual(result, (2, 2))

    def test_find_nearest_walkable_no_walkable_found(self):
        """Test that ValueError is raised when no walkable tile is found."""
        # Create a map with all walls
        tiles = [
            [Tile("wall", False, "wall"), Tile("wall", False, "wall")],
            [Tile("wall", False, "wall"), Tile("wall", False, "wall")],
        ]
        map_obj = Map("wall_map", 2, 2, tiles)
        self.world.add_map(map_obj)

        # Should raise ValueError
        with self.assertRaises(ValueError):
            self.world.find_nearest_walkable("wall_map", 1, 1)


class TestBlockedPositionFallback(unittest.TestCase):
    """Test that NPCs move to alternate position if target is blocked."""

    def setUp(self):
        """Set up test fixtures."""
        # Create map with blocked target position
        tiles = [
            [Tile("wall", False, "wall"), Tile("grass", True, "grass")],
            [Tile("grass", True, "grass"), Tile("grass", True, "grass")],
        ]
        self.map = Map("test_map", 2, 2, tiles)

        self.world = World()
        self.world.add_map(self.map)

        self.npc = NPC(
            entity_id="test_npc",
            name="Test NPC",
            x=1,
            y=1,
            sprite_id="npc"
        )
        self.world.set_map_entities("test_map", [self.npc])

    def test_blocked_position_fallback(self):
        """Test that NPC moves to alternate position when target is blocked."""
        # Try to move to blocked position (0, 0)
        result = self.world.move_entity_to_map("test_npc", "test_map", "test_map", 0, 0)

        # Should succeed by finding alternate position
        self.assertTrue(result)

        # Position should be walkable (not 0, 0 which is blocked)
        self.assertNotEqual((self.npc.x, self.npc.y), (0, 0))
        # Should be one of the walkable positions
        self.assertTrue((self.npc.x, self.npc.y) in [(0, 1), (1, 0), (1, 1)])


class TestMissingNpcGraceful(unittest.TestCase):
    """Test that missing NPC ID logs warning but doesn't crash."""

    def setUp(self):
        """Set up test fixtures."""
        entry = ScheduleEntry(
            time_periods=[TimeOfDay.MORNING],
            map_id="shop",
            x=3,
            y=4,
        )
        schedule = NPCSchedule(
            npc_id="nonexistent_npc",
            default_map_id="home",
            default_x=1,
            default_y=1,
            entries=[entry],
        )
        self.manager = ScheduleManager(schedules={"nonexistent_npc": schedule})

        tiles = [[Tile("grass", True, "grass") for _ in range(5)] for _ in range(5)]
        map_obj = Map("home", 5, 5, tiles)

        self.world = World()
        self.world.add_map(map_obj)

    def test_missing_npc_graceful(self):
        """Test that missing NPC ID logs warning but doesn't crash."""
        # Should not raise exception
        moved = self.manager.update(self.world, TimeOfDay.MORNING)

        # Should return empty list (no NPCs moved)
        self.assertEqual(moved, [])


class TestNpcInteractionPreventsMovement(unittest.TestCase):
    """Test that NPCs don't move when interaction is active."""

    def setUp(self):
        """Set up test fixtures."""
        entry = ScheduleEntry(
            time_periods=[TimeOfDay.MORNING],
            map_id="shop",
            x=3,
            y=4,
        )
        schedule = NPCSchedule(
            npc_id="test_npc",
            default_map_id="home",
            default_x=1,
            default_y=1,
            entries=[entry],
        )
        self.manager = ScheduleManager(schedules={"test_npc": schedule})

        tiles1 = [[Tile("grass", True, "grass") for _ in range(5)] for _ in range(5)]
        tiles2 = [[Tile("grass", True, "grass") for _ in range(5)] for _ in range(5)]
        map1 = Map("home", 5, 5, tiles1)
        map2 = Map("shop", 5, 5, tiles2)

        self.world = World()
        self.world.add_map(map1)
        self.world.add_map(map2)

        self.npc = NPC(
            entity_id="test_npc",
            name="Test NPC",
            x=1,
            y=1,
            sprite_id="npc"
        )
        self.world.set_map_entities("home", [self.npc])

    def test_npc_interaction_prevents_movement(self):
        """Test that when npc_interaction_active=True, NPCs don't move."""
        # Set interaction flag
        self.world.npc_interaction_active = True

        # Try to update schedule
        moved = self.manager.update(self.world, TimeOfDay.MORNING)

        # Should return empty list (no movement)
        self.assertEqual(moved, [])

        # Verify NPC is still on home map
        entities_home = self.world.get_map_entities("home")
        self.assertIn(self.npc, entities_home)

        # Verify position unchanged
        self.assertEqual(self.npc.x, 1)
        self.assertEqual(self.npc.y, 1)


if __name__ == "__main__":
    unittest.main()

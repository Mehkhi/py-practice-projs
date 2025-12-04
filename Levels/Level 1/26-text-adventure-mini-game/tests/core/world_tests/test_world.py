"""Unit tests for core/world.py - Map loading, triggers, warps."""

import json
import os
import tempfile
import unittest

from core.world import (
    Tile,
    Warp,
    Trigger,
    EntityRef,
    Map,
    World,
    load_map_from_json,
    get_map_graph,
    analyze_map_connectivity,
    _validate_warps,
)


class TestTile(unittest.TestCase):
    def test_tile_creation(self):
        tile = Tile(tile_id="grass", walkable=True, sprite_id="grass_sprite")
        self.assertEqual(tile.tile_id, "grass")
        self.assertTrue(tile.walkable)
        self.assertEqual(tile.sprite_id, "grass_sprite")

    def test_tile_non_walkable(self):
        tile = Tile(tile_id="wall", walkable=False, sprite_id="wall_sprite")
        self.assertFalse(tile.walkable)


class TestWarp(unittest.TestCase):
    def test_warp_basic(self):
        warp = Warp(x=5, y=10, target_map_id="cave", target_x=0, target_y=0)
        self.assertEqual(warp.x, 5)
        self.assertEqual(warp.y, 10)
        self.assertEqual(warp.target_map_id, "cave")
        self.assertIsNone(warp.requires_flag)
        self.assertIsNone(warp.requires_item)

    def test_warp_with_requirements(self):
        warp = Warp(
            x=1,
            y=2,
            target_map_id="secret",
            target_x=3,
            target_y=4,
            requires_flag="has_key",
            requires_item="magic_key",
            blocked_by_flag="door_sealed",
            fail_dialogue_id="need_key_dialogue",
        )
        self.assertEqual(warp.requires_flag, "has_key")
        self.assertEqual(warp.requires_item, "magic_key")
        self.assertEqual(warp.blocked_by_flag, "door_sealed")
        self.assertEqual(warp.fail_dialogue_id, "need_key_dialogue")


class TestTrigger(unittest.TestCase):
    def test_trigger_creation(self):
        trigger = Trigger(
            id="battle_1",
            x=5,
            y=5,
            trigger_type="battle",
            data={"encounter_id": "wolves"},
            once=True,
        )
        self.assertEqual(trigger.id, "battle_1")
        self.assertEqual(trigger.trigger_type, "battle")
        self.assertTrue(trigger.once)
        self.assertFalse(trigger.fired)

    def test_trigger_repeatable(self):
        trigger = Trigger(
            id="heal_spot",
            x=3,
            y=3,
            trigger_type="script",
            data={"action": "heal"},
            once=False,
        )
        self.assertFalse(trigger.once)


class TestEntityRef(unittest.TestCase):
    def test_entity_ref(self):
        ref = EntityRef(entity_id="npc_guide", x=10, y=15)
        self.assertEqual(ref.entity_id, "npc_guide")
        self.assertEqual(ref.x, 10)
        self.assertEqual(ref.y, 15)


class TestMap(unittest.TestCase):
    def setUp(self):
        self.tiles = [
            [Tile("grass", True, "grass"), Tile("grass", True, "grass"), Tile("wall", False, "wall")],
            [Tile("grass", True, "grass"), Tile("grass", True, "grass"), Tile("grass", True, "grass")],
            [Tile("water", False, "water"), Tile("grass", True, "grass"), Tile("grass", True, "grass")],
        ]
        self.warps = [Warp(x=2, y=0, target_map_id="cave", target_x=0, target_y=0)]
        self.triggers = [
            Trigger(id="t1", x=1, y=1, trigger_type="dialogue", data={"dialogue_id": "hello"}, once=True)
        ]
        self.entities = [EntityRef(entity_id="npc_1", x=0, y=1)]
        self.map = Map(
            map_id="test_map",
            width=3,
            height=3,
            tiles=self.tiles,
            warps=self.warps,
            triggers=self.triggers,
            entities=self.entities,
        )

    def test_map_dimensions(self):
        self.assertEqual(self.map.width, 3)
        self.assertEqual(self.map.height, 3)
        self.assertEqual(self.map.map_id, "test_map")

    def test_is_walkable_valid(self):
        self.assertTrue(self.map.is_walkable(0, 0))
        self.assertTrue(self.map.is_walkable(1, 1))

    def test_is_walkable_blocked(self):
        self.assertFalse(self.map.is_walkable(2, 0))  # wall
        self.assertFalse(self.map.is_walkable(0, 2))  # water

    def test_is_walkable_out_of_bounds(self):
        self.assertFalse(self.map.is_walkable(-1, 0))
        self.assertFalse(self.map.is_walkable(0, -1))
        self.assertFalse(self.map.is_walkable(10, 0))
        self.assertFalse(self.map.is_walkable(0, 10))

    def test_get_trigger_at(self):
        trigger = self.map.get_trigger_at(1, 1)
        self.assertIsNotNone(trigger)
        self.assertEqual(trigger.id, "t1")

    def test_get_trigger_at_empty(self):
        trigger = self.map.get_trigger_at(0, 0)
        self.assertIsNone(trigger)

    def test_get_trigger_at_fired_once(self):
        self.map.fire_trigger("t1")
        trigger = self.map.get_trigger_at(1, 1)
        self.assertIsNone(trigger)  # once=True and fired

    def test_get_warp_at(self):
        warp = self.map.get_warp_at(2, 0)
        self.assertIsNotNone(warp)
        self.assertEqual(warp.target_map_id, "cave")

    def test_get_warp_at_empty(self):
        warp = self.map.get_warp_at(0, 0)
        self.assertIsNone(warp)

    def test_fire_trigger(self):
        result = self.map.fire_trigger("t1")
        self.assertTrue(result)
        self.assertTrue(self.triggers[0].fired)

    def test_fire_trigger_not_found(self):
        result = self.map.fire_trigger("nonexistent")
        self.assertFalse(result)

    def test_validate_consistent_map(self):
        # Should not raise or print warnings for consistent map
        self.map.validate()

    def test_map_auto_corrects_dimensions(self):
        # Declared dimensions don't match actual tiles
        tiles = [[Tile("grass", True, "grass")] * 2] * 2
        map_obj = Map(map_id="mismatch", width=5, height=5, tiles=tiles)
        # Should use actual tile dimensions
        self.assertEqual(map_obj.width, 2)
        self.assertEqual(map_obj.height, 2)


class TestWorld(unittest.TestCase):
    def setUp(self):
        self.world = World()
        tiles = [[Tile("grass", True, "grass")] * 3] * 3
        self.map1 = Map(map_id="forest_path", width=3, height=3, tiles=tiles)
        self.map2 = Map(map_id="cave", width=3, height=3, tiles=tiles)
        self.world.add_map(self.map1)
        self.world.add_map(self.map2)

    def test_add_and_get_map(self):
        self.assertIn("forest_path", self.world.maps)
        self.assertIn("cave", self.world.maps)

    def test_get_current_map(self):
        current = self.world.get_current_map()
        self.assertEqual(current.map_id, "forest_path")

    def test_set_current_map(self):
        self.world.set_current_map("cave")
        self.assertEqual(self.world.current_map_id, "cave")

    def test_set_current_map_invalid(self):
        with self.assertRaises(ValueError):
            self.world.set_current_map("nonexistent")

    def test_set_and_get_flag(self):
        self.world.set_flag("quest_complete", True)
        self.assertTrue(self.world.get_flag("quest_complete"))

    def test_get_flag_default(self):
        self.assertFalse(self.world.get_flag("unknown_flag"))
        self.assertTrue(self.world.get_flag("unknown_flag", default=True))

    def test_set_and_get_map_entities(self):
        entities = ["entity1", "entity2"]
        self.world.set_map_entities("forest_path", entities)
        result = self.world.get_map_entities("forest_path")
        self.assertEqual(result, entities)

    def test_get_map_entities_empty(self):
        result = self.world.get_map_entities("nonexistent")
        self.assertEqual(result, [])


class TestLoadMapFromJson(unittest.TestCase):
    def test_load_basic_map(self):
        map_data = {
            "map_id": "test",
            "width": 2,
            "height": 2,
            "tiles": [
                [{"tile_id": "grass", "walkable": True, "sprite_id": "grass"}] * 2,
                [{"tile_id": "grass", "walkable": True, "sprite_id": "grass"}] * 2,
            ],
            "warps": [],
            "triggers": [],
            "entities": [],
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(map_data, f)
            temp_path = f.name

        try:
            loaded_map = load_map_from_json(temp_path)
            self.assertEqual(loaded_map.map_id, "test")
            self.assertEqual(loaded_map.width, 2)
            self.assertEqual(loaded_map.height, 2)
        finally:
            os.unlink(temp_path)

    def test_load_map_with_warps(self):
        map_data = {
            "map_id": "warp_test",
            "width": 3,
            "height": 3,
            "tiles": [[{"tile_id": "grass", "walkable": True}] * 3] * 3,
            "warps": [
                {"x": 0, "y": 0, "target_map_id": "dest", "target_x": 1, "target_y": 1}
            ],
            "triggers": [],
            "entities": [],
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(map_data, f)
            temp_path = f.name

        try:
            loaded_map = load_map_from_json(temp_path)
            self.assertEqual(len(loaded_map.warps), 1)
            self.assertEqual(loaded_map.warps[0].target_map_id, "dest")
        finally:
            os.unlink(temp_path)

    def test_load_map_with_triggers(self):
        map_data = {
            "map_id": "trigger_test",
            "width": 2,
            "height": 2,
            "tiles": [[{"tile_id": "grass", "walkable": True}] * 2] * 2,
            "warps": [],
            "triggers": [
                {"id": "t1", "x": 0, "y": 0, "trigger_type": "battle", "data": {}, "once": True}
            ],
            "entities": [],
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(map_data, f)
            temp_path = f.name

        try:
            loaded_map = load_map_from_json(temp_path)
            self.assertEqual(len(loaded_map.triggers), 1)
            self.assertEqual(loaded_map.triggers[0].id, "t1")
        finally:
            os.unlink(temp_path)

    def test_load_map_with_entities(self):
        map_data = {
            "map_id": "entity_test",
            "width": 2,
            "height": 2,
            "tiles": [[{"tile_id": "grass", "walkable": True}] * 2] * 2,
            "warps": [],
            "triggers": [],
            "entities": [{"entity_id": "npc_1", "x": 1, "y": 1}],
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(map_data, f)
            temp_path = f.name

        try:
            loaded_map = load_map_from_json(temp_path)
            self.assertEqual(len(loaded_map.entities), 1)
            self.assertEqual(loaded_map.entities[0].entity_id, "npc_1")
        finally:
            os.unlink(temp_path)

    def test_load_map_pads_malformed_tiles(self):
        # Tiles smaller than declared dimensions
        map_data = {
            "map_id": "pad_test",
            "width": 4,
            "height": 4,
            "tiles": [
                [{"tile_id": "grass", "walkable": True}] * 2,
                [{"tile_id": "grass", "walkable": True}] * 2,
            ],
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(map_data, f)
            temp_path = f.name

        try:
            loaded_map = load_map_from_json(temp_path)
            self.assertEqual(loaded_map.width, 4)
            self.assertEqual(loaded_map.height, 4)
            # Padded tiles should be non-walkable void
            self.assertFalse(loaded_map.is_walkable(3, 3))
        finally:
            os.unlink(temp_path)


class TestMapConnectivity(unittest.TestCase):
    """Tests for map connectivity analysis and warp validation."""

    def _make_tiles(self, width: int = 5, height: int = 5):
        """Create a grid of walkable tiles without shared references."""
        return [[Tile("grass", True, "grass") for _ in range(width)] for _ in range(height)]

    def setUp(self):
        """Set up test world with sample maps."""
        self.world = World()

        # Create a simple connected map structure
        # Use _make_tiles() to avoid shared list references
        self.map1 = Map(map_id="start", width=5, height=5, tiles=self._make_tiles())
        self.map2 = Map(map_id="middle", width=5, height=5, tiles=self._make_tiles())
        self.map3 = Map(map_id="end", width=5, height=5, tiles=self._make_tiles())
        self.map4 = Map(map_id="orphaned", width=5, height=5, tiles=self._make_tiles())

        # Map1 -> Map2 -> Map3 (linear chain)
        self.map1.warps = [Warp(x=4, y=2, target_map_id="middle", target_x=0, target_y=2)]
        self.map2.warps = [Warp(x=4, y=2, target_map_id="end", target_x=0, target_y=2)]
        # Map3 has no exits (dead end)
        self.map3.warps = []

        self.world.add_map(self.map1)
        self.world.add_map(self.map2)
        self.world.add_map(self.map3)
        self.world.add_map(self.map4)

    def test_get_map_graph(self):
        """Test building map connectivity graph."""
        graph = get_map_graph(self.world)

        self.assertIn("start", graph)
        self.assertIn("middle", graph)
        self.assertIn("end", graph)
        self.assertIn("orphaned", graph)

        # Check connections
        self.assertEqual(len(graph["start"]), 1)
        self.assertEqual(graph["start"][0][0], "middle")
        self.assertFalse(graph["start"][0][1])  # Not conditional

        self.assertEqual(len(graph["middle"]), 1)
        self.assertEqual(graph["middle"][0][0], "end")

        self.assertEqual(len(graph["end"]), 0)  # Dead end
        self.assertEqual(len(graph["orphaned"]), 0)  # No connections

    def test_get_map_graph_conditional_warps(self):
        """Test graph building with conditional warps."""
        # Add conditional warp
        conditional_warp = Warp(
            x=2, y=4, target_map_id="end", target_x=2, target_y=0,
            requires_flag="has_key"
        )
        self.map1.warps.append(conditional_warp)

        graph = get_map_graph(self.world)

        # Should have 2 connections from start
        self.assertEqual(len(graph["start"]), 2)

        # Find the conditional one
        conditional_found = False
        for target, is_conditional in graph["start"]:
            if target == "end" and is_conditional:
                conditional_found = True
        self.assertTrue(conditional_found)

    def test_analyze_map_connectivity_dead_ends(self):
        """Test dead end detection."""
        dead_ends, disconnected, orphaned, graph = analyze_map_connectivity(
            self.world, "start"
        )

        # Map3 has no exits, should be a dead end
        self.assertIn("end", dead_ends)
        # Orphaned map has no exits
        self.assertIn("orphaned", dead_ends)

    def test_analyze_map_connectivity_disconnected(self):
        """Test disconnected map detection."""
        dead_ends, disconnected, orphaned, graph = analyze_map_connectivity(
            self.world, "start"
        )

        # Orphaned map is not reachable from start
        self.assertIn("orphaned", disconnected)

    def test_analyze_map_connectivity_orphaned(self):
        """Test orphaned map detection."""
        dead_ends, disconnected, orphaned, graph = analyze_map_connectivity(
            self.world, "start"
        )

        # Orphaned map is never referenced as a target
        self.assertIn("orphaned", orphaned)
        # Start map should NOT be in orphaned (it's the entry point)
        self.assertNotIn("start", orphaned)

    def test_analyze_map_connectivity_all_reachable(self):
        """Test that connected maps are all reachable."""
        dead_ends, disconnected, orphaned, graph = analyze_map_connectivity(
            self.world, "start"
        )

        # start, middle, and end should be reachable
        self.assertNotIn("start", disconnected)
        self.assertNotIn("middle", disconnected)
        self.assertNotIn("end", disconnected)

    def test_validate_warps_invalid_target_map(self):
        """Test warp validation with non-existent target map."""
        invalid_warp = Warp(x=0, y=0, target_map_id="nonexistent", target_x=0, target_y=0)
        self.map1.warps.append(invalid_warp)

        # Should log warning but not raise exception
        _validate_warps(self.world)
        # Test passes if no exception is raised

    def test_validate_warps_out_of_bounds_target(self):
        """Test warp validation with out-of-bounds target coordinates."""
        invalid_warp = Warp(x=0, y=0, target_map_id="middle", target_x=10, target_y=10)
        self.map1.warps.append(invalid_warp)

        # Should log warning but not raise exception
        _validate_warps(self.world)
        # Test passes if no exception is raised

    def test_validate_warps_negative_coordinates(self):
        """Test warp validation with negative target coordinates."""
        invalid_warp = Warp(x=0, y=0, target_map_id="middle", target_x=-1, target_y=-1)
        self.map1.warps.append(invalid_warp)

        # Should log warning but not raise exception
        _validate_warps(self.world)
        # Test passes if no exception is raised

    def test_validate_warps_valid_warps(self):
        """Test that valid warps don't trigger warnings."""
        # All warps in setUp are valid
        # Should not raise exceptions or log warnings for valid warps
        _validate_warps(self.world)
        # Test passes if no exception is raised

    def test_analyze_map_connectivity_conditional_only_exits(self):
        """Test that maps with only conditional exits are marked as dead ends."""
        # Remove non-conditional warp from map1
        self.map1.warps = [
            Warp(x=0, y=0, target_map_id="middle", target_x=0, target_y=0, requires_flag="key")
        ]

        dead_ends, disconnected, orphaned, graph = analyze_map_connectivity(
            self.world, "start"
        )

        # Map1 now only has conditional exits, should be considered a dead end
        # (since conditional exits may never be accessible)
        self.assertIn("start", dead_ends)

    def test_analyze_map_connectivity_invalid_start_map(self):
        """Test connectivity analysis with non-existent start map."""
        dead_ends, disconnected, orphaned, graph = analyze_map_connectivity(
            self.world, "nonexistent"
        )

        # All maps should be disconnected if start doesn't exist
        self.assertEqual(len(disconnected), len(self.world.maps))

    def test_validate_warps_logs_warning_for_invalid_target(self):
        """Test that _validate_warps logs warning with correct message for invalid target."""
        from unittest.mock import patch

        invalid_warp = Warp(x=0, y=0, target_map_id="nonexistent", target_x=0, target_y=0)
        self.map1.warps.append(invalid_warp)

        with patch('core.map_loader.log_warning') as mock_warn:
            _validate_warps(self.world)
            mock_warn.assert_called()
            # Verify the warning mentions the non-existent map
            call_args = mock_warn.call_args[0][0]
            self.assertIn("nonexistent", call_args)
            self.assertIn("non-existent", call_args.lower())

    def test_validate_warps_logs_warning_for_out_of_bounds(self):
        """Test that _validate_warps logs warning with bounds info."""
        from unittest.mock import patch

        invalid_warp = Warp(x=0, y=0, target_map_id="middle", target_x=10, target_y=10)
        self.map1.warps.append(invalid_warp)

        with patch('core.map_loader.log_warning') as mock_warn:
            _validate_warps(self.world)
            mock_warn.assert_called()
            call_args = mock_warn.call_args[0][0]
            self.assertIn("out-of-bounds", call_args.lower())
            self.assertIn("10", call_args)

    def test_validate_warps_logs_warning_for_negative_coords(self):
        """Test that _validate_warps logs warning for negative coordinates."""
        from unittest.mock import patch

        invalid_warp = Warp(x=0, y=0, target_map_id="middle", target_x=-1, target_y=-1)
        self.map1.warps.append(invalid_warp)

        with patch('core.map_loader.log_warning') as mock_warn:
            _validate_warps(self.world)
            mock_warn.assert_called()
            call_args = mock_warn.call_args[0][0]
            self.assertIn("negative", call_args.lower())
            self.assertIn("-1", call_args)

    def test_validate_warps_logs_warning_for_non_walkable_target(self):
        """Test that _validate_warps logs warning for non-walkable target tile."""
        from unittest.mock import patch

        # Make target tile non-walkable
        self.map2.tiles[2][2] = Tile("wall", False, "wall")
        invalid_warp = Warp(x=0, y=0, target_map_id="middle", target_x=2, target_y=2)
        self.map1.warps.append(invalid_warp)

        with patch('core.map_loader.log_warning') as mock_warn:
            _validate_warps(self.world)
            mock_warn.assert_called()
            call_args = mock_warn.call_args[0][0]
            self.assertIn("non-walkable", call_args.lower())


class TestWarpWithTransitionValidation(unittest.TestCase):
    """Tests for TriggerHandler.warp_with_transition() runtime validation."""

    def _make_tiles(self, width: int = 5, height: int = 5):
        """Create a grid of walkable tiles without shared references."""
        return [[Tile("grass", True, "grass") for _ in range(width)] for _ in range(height)]

    def setUp(self):
        """Set up mock scene and world for testing warp validation."""
        from unittest.mock import Mock, MagicMock

        self.world = World()

        # Create test maps
        self.map1 = Map(map_id="start", width=5, height=5, tiles=self._make_tiles())
        self.map2 = Map(map_id="target", width=5, height=5, tiles=self._make_tiles())

        self.world.add_map(self.map1)
        self.world.add_map(self.map2)
        self.world.current_map_id = "start"

        # Create mock scene with required attributes
        self.mock_scene = Mock()
        self.mock_scene.world = self.world
        self.mock_scene._pending_warp = None
        self.mock_scene.transition = Mock()
        self.mock_scene.transition.fade_out_in = Mock()

    def test_warp_to_nonexistent_map_aborts(self):
        """Test that warping to non-existent map logs warning and aborts."""
        from unittest.mock import patch
        from engine.world.trigger_handler import TriggerHandler

        handler = TriggerHandler(self.mock_scene)

        with patch('engine.world.triggers.warp_handler.log_warning') as mock_warn:
            handler.warp_with_transition("nonexistent", 0, 0)

            mock_warn.assert_called_once()
            self.assertIn("non-existent", mock_warn.call_args[0][0].lower())
            # Transition should not be called
            self.mock_scene.transition.fade_out_in.assert_not_called()

    def test_warp_to_negative_coords_aborts(self):
        """Test that warping to negative coordinates logs warning and aborts."""
        from unittest.mock import patch
        from engine.world.trigger_handler import TriggerHandler

        handler = TriggerHandler(self.mock_scene)

        with patch('engine.world.triggers.warp_handler.log_warning') as mock_warn:
            handler.warp_with_transition("target", -1, -1)

            mock_warn.assert_called_once()
            self.assertIn("negative", mock_warn.call_args[0][0].lower())
            self.mock_scene.transition.fade_out_in.assert_not_called()

    def test_warp_to_out_of_bounds_aborts(self):
        """Test that warping to out-of-bounds coordinates logs warning and aborts."""
        from unittest.mock import patch
        from engine.world.trigger_handler import TriggerHandler

        handler = TriggerHandler(self.mock_scene)

        with patch('engine.world.triggers.warp_handler.log_warning') as mock_warn:
            handler.warp_with_transition("target", 10, 10)

            mock_warn.assert_called_once()
            self.assertIn("out-of-bounds", mock_warn.call_args[0][0].lower())
            self.mock_scene.transition.fade_out_in.assert_not_called()

    def test_warp_to_non_walkable_tile_aborts(self):
        """Test that warping to non-walkable tile logs warning and aborts."""
        from unittest.mock import patch
        from engine.world.trigger_handler import TriggerHandler

        # Make target tile non-walkable
        self.map2.tiles[2][2] = Tile("wall", False, "wall")

        handler = TriggerHandler(self.mock_scene)

        with patch('engine.world.triggers.warp_handler.log_warning') as mock_warn:
            handler.warp_with_transition("target", 2, 2)

            mock_warn.assert_called_once()
            self.assertIn("non-walkable", mock_warn.call_args[0][0].lower())
            self.mock_scene.transition.fade_out_in.assert_not_called()

    def test_valid_warp_initiates_transition(self):
        """Test that valid warp coordinates initiate fade transition."""
        from engine.world.trigger_handler import TriggerHandler

        handler = TriggerHandler(self.mock_scene)
        handler.warp_with_transition("target", 2, 2)

        # Transition should be called for valid warp
        self.mock_scene.transition.fade_out_in.assert_called_once()
        # Pending warp should be set
        self.assertEqual(self.mock_scene._pending_warp, ("target", 2, 2))


if __name__ == "__main__":
    unittest.main()

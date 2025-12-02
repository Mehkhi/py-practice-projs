"""Unit tests for edge cases - Invalid data, missing assets, corrupted saves, empty collections, zero HP/SP."""

import copy
import json
import os
import tempfile
import unittest
from typing import Any, Dict, Optional
from unittest.mock import patch, MagicMock

import pygame

from core.data_loader import load_json_file
from core.save_load import SaveManager
from core.items import Inventory, Item
from core.entities import Player, PartyMember
from core.stats import Stats, StatusEffect
from core.world import World, Map, Tile
from engine.assets import AssetManager


def _deep_merge(base: Dict[str, Any], overrides: Dict[str, Any]) -> Dict[str, Any]:
    """Deep merge two dictionaries, with overrides taking precedence."""
    result = copy.deepcopy(base)
    for key, value in overrides.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = copy.deepcopy(value)
    return result


class TestInvalidJSONData(unittest.TestCase):
    """Test invalid JSON data handling in data_loader."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "test.json")

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_load_json_missing_file(self):
        """Test loading non-existent file returns default."""
        result = load_json_file("nonexistent_file.json")
        self.assertEqual(result, {})

    def test_load_json_missing_file_custom_default(self):
        """Test loading non-existent file returns custom default."""
        custom_default = {"key": "value"}
        result = load_json_file("nonexistent_file.json", default=custom_default)
        self.assertEqual(result, custom_default)

    def test_load_json_malformed_missing_value(self):
        """Test malformed JSON (missing value after colon) returns default."""
        with open(self.test_file, 'w') as f:
            f.write('{"key": }')  # Missing value

        result = load_json_file(self.test_file)
        self.assertEqual(result, {})

    def test_load_json_unclosed_brackets(self):
        """Test unclosed brackets returns default."""
        with open(self.test_file, 'w') as f:
            f.write('{"key": "value"')

        result = load_json_file(self.test_file)
        self.assertEqual(result, {})

    def test_load_json_trailing_comma(self):
        """Test trailing comma (invalid JSON) returns default."""
        with open(self.test_file, 'w') as f:
            f.write('{"key": "value",}')

        result = load_json_file(self.test_file)
        self.assertEqual(result, {})

    def test_load_json_wrong_structure_array(self):
        """Test valid JSON but wrong structure (array instead of dict)."""
        with open(self.test_file, 'w') as f:
            json.dump([1, 2, 3], f)

        # Should return the array (not dict), but function expects dict
        result = load_json_file(self.test_file)
        # Function doesn't validate structure, so it returns what's parsed
        self.assertIsInstance(result, list)

    def test_load_json_null_value(self):
        """Test JSON with null value."""
        with open(self.test_file, 'w') as f:
            json.dump({"key": None}, f)

        result = load_json_file(self.test_file)
        self.assertEqual(result["key"], None)

    def test_load_json_empty_file(self):
        """Test empty file returns default."""
        with open(self.test_file, 'w') as f:
            f.write("")

        result = load_json_file(self.test_file)
        self.assertEqual(result, {})

    def test_load_json_whitespace_only(self):
        """Test file with only whitespace returns default."""
        with open(self.test_file, 'w') as f:
            f.write("   \n\t  ")

        result = load_json_file(self.test_file)
        self.assertEqual(result, {})

    def test_load_json_unicode_encoding(self):
        """Test JSON with unicode characters."""
        with open(self.test_file, 'w', encoding='utf-8') as f:
            json.dump({"name": "テスト", "emoji": "🎮"}, f, ensure_ascii=False)

        result = load_json_file(self.test_file)
        self.assertEqual(result["name"], "テスト")
        self.assertEqual(result["emoji"], "🎮")


class TestMissingAssets(unittest.TestCase):
    """Test missing asset files handling in AssetManager."""

    def setUp(self):
        # Initialize pygame for asset tests
        pygame.init()
        self.temp_dir = tempfile.mkdtemp()
        self.assets_dir = os.path.join(self.temp_dir, "assets")
        os.makedirs(self.assets_dir, exist_ok=True)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        if pygame.get_init():
            pygame.quit()

    def test_get_image_missing_sprite_creates_placeholder(self):
        """Test that missing sprite generates placeholder."""
        manager = AssetManager(assets_dir=self.assets_dir)
        image = manager.get_image("nonexistent_sprite")

        self.assertIsNotNone(image)
        self.assertIsInstance(image, pygame.Surface)
        self.assertGreater(image.get_width(), 0)
        self.assertGreater(image.get_height(), 0)

    def test_get_image_missing_sprite_cached(self):
        """Test that placeholder is cached after first generation."""
        manager = AssetManager(assets_dir=self.assets_dir)
        image1 = manager.get_image("nonexistent_sprite")
        image2 = manager.get_image("nonexistent_sprite")

        # Should be the same object (cached)
        self.assertIs(image1, image2)

    def test_get_image_missing_sprite_custom_size(self):
        """Test placeholder generation with custom size."""
        manager = AssetManager(assets_dir=self.assets_dir, scale=1)  # Use scale=1 to avoid scaling
        image = manager.get_image("nonexistent_sprite", size=(32, 32))

        self.assertIsNotNone(image)
        # Size is scaled by manager.scale (default 2), so with scale=1, size should match
        self.assertEqual(image.get_width(), 32)
        self.assertEqual(image.get_height(), 32)

    def test_get_sound_missing_file_graceful(self):
        """Test that missing sound file doesn't crash."""
        manager = AssetManager(assets_dir=self.assets_dir)
        # Should not raise exception
        manager.play_sound("nonexistent_sound")
        # No assertion needed - just verify no exception

    def test_get_font_missing_font_fallback(self):
        """Test missing font falls back to pygame default font."""
        manager = AssetManager(assets_dir=self.assets_dir)
        font = manager.get_font("nonexistent_font")

        # Should always return a fallback font, never None
        self.assertIsNotNone(font, "Fallback font should always be provided")
        self.assertIsInstance(font, pygame.font.Font)

    def test_get_font_missing_font_with_size(self):
        """Test missing font with size override returns valid font."""
        manager = AssetManager(assets_dir=self.assets_dir)
        font = manager.get_font("nonexistent_font", size=32)

        # Should return a font with the requested size
        self.assertIsNotNone(font, "Fallback font should always be provided")
        self.assertIsInstance(font, pygame.font.Font)

    def test_load_sprites_missing_directory(self):
        """Test loading sprites from non-existent directory."""
        manager = AssetManager(assets_dir="nonexistent_assets_dir")
        # Should not crash
        image = manager.get_image("any_sprite")
        self.assertIsNotNone(image)

    def test_load_sounds_missing_directory(self):
        """Test loading sounds from non-existent directory."""
        manager = AssetManager(assets_dir=self.assets_dir)
        # Should not crash - audio directory doesn't exist
        manager.play_sound("any_sound")
        # No assertion needed - just verify no exception

    def test_placeholder_has_alpha_channel(self):
        """Test that placeholder surface supports transparency."""
        manager = AssetManager(assets_dir=self.assets_dir)
        image = manager.get_image("test_placeholder")
        # Check that surface was created with SRCALPHA flag
        self.assertTrue(image.get_flags() & pygame.SRCALPHA)

    def test_placeholder_consistent_between_calls(self):
        """Test that same sprite_id produces same cached placeholder."""
        manager = AssetManager(assets_dir=self.assets_dir)
        # Get placeholder via public API twice
        image1 = manager.get_image("test_sprite_color")
        image2 = manager.get_image("test_sprite_color")
        # Should be the exact same cached object
        self.assertIs(image1, image2)

    def test_placeholder_different_for_different_ids(self):
        """Test that different sprite_ids produce different placeholders."""
        manager = AssetManager(assets_dir=self.assets_dir)
        image1 = manager.get_image("sprite_alpha")
        image2 = manager.get_image("sprite_beta")
        # Different sprite_ids should produce different objects
        self.assertIsNot(image1, image2)

    def test_placeholder_custom_size_via_public_api(self):
        """Test that placeholder respects custom size via public API."""
        manager = AssetManager(assets_dir=self.assets_dir, scale=1)
        # Test various sizes via public get_image API
        for size in [(8, 8), (16, 16), (32, 32), (64, 64)]:
            image = manager.get_image(f"size_test_{size[0]}", size)
            self.assertEqual(image.get_width(), size[0], f"Width mismatch for size {size}")
            self.assertEqual(image.get_height(), size[1], f"Height mismatch for size {size}")


class TestCorruptedSaveFiles(unittest.TestCase):
    """Test additional corrupted save file edge cases."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.save_manager = SaveManager(save_dir=self.temp_dir)

        self.world = World()
        tiles = [[Tile("grass", True, "grass")] * 3] * 3
        self.world.add_map(Map(map_id="forest_path", width=3, height=3, tiles=tiles))

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _make_valid_save_data(self, **overrides) -> Dict[str, Any]:
        """Create a valid save data dict with optional deep-merge overrides."""
        base = {
            "meta": {
                "version": 1,
                "timestamp": "2024-01-01T00:00:00",
                "play_time_seconds": 0
            },
            "world": {
                "current_map_id": "forest_path",
                "flags": {},
                "runtime_state": {"trigger_states": {}, "enemy_states": {}}
            },
            "player": {
                "entity_id": "player_1",
                "name": "Hero",
                "x": 5,
                "y": 10,
                "inventory": {},
                "equipment": {},
                "skills": [],
                "stats": {
                    "max_hp": 100,
                    "hp": 80,
                    "max_sp": 50,
                    "sp": 40,
                    "attack": 10,
                    "defense": 5,
                    "magic": 8,
                    "speed": 6,
                    "luck": 3,
                    "status_effects": {}
                }
            }
        }
        return _deep_merge(base, overrides)

    def _write_save_data(self, save_data: Dict[str, Any], slot: int = 1) -> str:
        """Write save data to a slot and return the path."""
        save_path = os.path.join(self.temp_dir, f"save_{slot}.json")
        with open(save_path, 'w') as f:
            json.dump(save_data, f)
        return save_path

    def test_load_save_negative_hp(self):
        """Test save with negative HP values loads without crashing."""
        save_data = self._make_valid_save_data(player={"stats": {"hp": -50}})
        self._write_save_data(save_data)

        # Should load but HP should be clamped or handled
        player = self.save_manager.load_from_slot(1, self.world)
        self.assertIsNotNone(player)
        self.assertIsNotNone(player.stats)

    def test_load_save_negative_level(self):
        """Test save with negative level loads without validation (documents current behavior)."""
        save_data = self._make_valid_save_data(player={"stats": {"level": -5, "exp": 0}})
        self._write_save_data(save_data)

        player = self.save_manager.load_from_slot(1, self.world)
        self.assertIsNotNone(player)
        # NOTE: Current behavior loads negative level as-is without validation.
        # This test documents that the system handles invalid data gracefully without crashing.
        # TODO: Consider whether level should be validated/clamped on load.
        self.assertEqual(player.stats.level, -5)

    def test_load_save_extremely_large_values(self):
        """Test save with extremely large integer values."""
        large_stats = {
            "max_hp": 999999999,
            "hp": 999999999,
            "max_sp": 999999999,
            "sp": 999999999,
            "attack": 999999999,
            "defense": 999999999,
            "magic": 999999999,
            "speed": 999999999,
            "luck": 999999999,
            "level": 999,
            "exp": 999999999,
            "status_effects": {}
        }
        save_data = self._make_valid_save_data(player={"stats": large_stats})
        self._write_save_data(save_data)

        # Should load without crashing
        player = self.save_manager.load_from_slot(1, self.world)
        self.assertIsNotNone(player)
        self.assertEqual(player.stats.max_hp, 999999999)

    def test_load_save_invalid_formation_position(self):
        """Test save with invalid formation_position value uses default."""
        party_member = {
            "entity_id": "member_1",
            "name": "Member",
            "x": 0,
            "y": 0,
            "formation_position": "invalid_position",
            "stats": {
                "max_hp": 80, "hp": 80, "max_sp": 40, "sp": 40,
                "attack": 8, "defense": 4, "magic": 6, "speed": 6, "luck": 4,
                "status_effects": {}
            }
        }
        save_data = self._make_valid_save_data(player={"party": [party_member]})
        self._write_save_data(save_data)

        # Should load with default formation position
        player = self.save_manager.load_from_slot(1, self.world)
        self.assertIsNotNone(player)

    def test_load_save_invalid_role(self):
        """Test save with invalid role value loads gracefully."""
        party_member = {
            "entity_id": "member_1",
            "name": "Member",
            "x": 0,
            "y": 0,
            "role": "invalid_role_xyz",
            "stats": {
                "max_hp": 80, "hp": 80, "max_sp": 40, "sp": 40,
                "attack": 8, "defense": 4, "magic": 6, "speed": 6, "luck": 4,
                "status_effects": {}
            }
        }
        save_data = self._make_valid_save_data(player={"party": [party_member]})
        self._write_save_data(save_data)

        # Should load with default role or handle gracefully
        player = self.save_manager.load_from_slot(1, self.world)
        self.assertIsNotNone(player)

    def test_load_save_nested_invalid_data(self):
        """Test save with invalid data in nested structures."""
        save_data = self._make_valid_save_data(
            world={"flags": {"nested": {"invalid": "data", "number": "not_a_number"}}},
            player={"inventory": {"item1": "not_a_number"}}  # Should be int
        )
        self._write_save_data(save_data)

        # Should handle gracefully or recover
        player = self.save_manager.load_from_slot(1, self.world)
        self.assertIsNotNone(player)

    def test_load_save_truncated_json(self):
        """Test truncated JSON file raises ValueError (cannot recover)."""
        save_path = os.path.join(self.temp_dir, "save_1.json")
        with open(save_path, 'w') as f:
            f.write('{"meta": {"version": 1, "timestamp": "2024-01-01T00:00:00"')  # Incomplete

        # Should raise ValueError wrapping JSONDecodeError
        with self.assertRaises(ValueError) as ctx:
            self.save_manager.load_from_slot(1, self.world)
        self.assertIn("corrupted", str(ctx.exception).lower())

    def test_load_save_float_inventory_quantity(self):
        """Test save with float inventory quantity (documents current behavior)."""
        save_data = self._make_valid_save_data(player={"inventory": {"health_potion": 1.5}})
        self._write_save_data(save_data)

        # Should load without crashing - float will be used as-is
        player = self.save_manager.load_from_slot(1, self.world)
        self.assertIsNotNone(player)

    def test_load_save_extremely_long_name(self):
        """Test save with extremely long player name."""
        long_name = "A" * 10000
        save_data = self._make_valid_save_data(player={"name": long_name})
        self._write_save_data(save_data)

        # Should load without crashing
        player = self.save_manager.load_from_slot(1, self.world)
        self.assertIsNotNone(player)
        self.assertEqual(player.name, long_name)


class TestEmptyCollections(unittest.TestCase):
    """Test operations on empty inventories and parties."""

    def setUp(self):
        self.inventory = Inventory()
        self.player = self._make_player()

    def _make_player(self, **overrides) -> Player:
        """Create a test player with default values."""
        defaults = dict(
            entity_id="player",
            name="Hero",
            x=0,
            y=0,
            sprite_id="player",
            stats=Stats(100, 100, 50, 50, 10, 5, 8, 7, 5)
        )
        defaults.update(overrides)
        return Player(**defaults)

    def _make_party_member(self, entity_id: str, name: str) -> PartyMember:
        """Create a test party member."""
        return PartyMember(
            entity_id=entity_id,
            name=name,
            x=0,
            y=0,
            sprite_id="party_member",
            stats=Stats(80, 80, 40, 40, 8, 4, 6, 6, 4)
        )

    def test_inventory_remove_from_empty(self):
        """Test removing items from empty inventory."""
        result = self.inventory.remove("health_potion", 1)
        self.assertFalse(result)
        self.assertEqual(self.inventory.get_quantity("health_potion"), 0)

    def test_inventory_has_from_empty(self):
        """Test checking for items in empty inventory."""
        self.assertFalse(self.inventory.has("health_potion", 1))
        self.assertEqual(self.inventory.get_quantity("health_potion"), 0)

    def test_inventory_get_total_count_empty(self):
        """Test get_total_item_count on empty inventory."""
        self.assertEqual(self.inventory.get_total_item_count(), 0)

    def test_inventory_get_sorted_items_empty(self):
        """Test sorting empty inventory."""
        sorted_items = self.inventory.get_sorted_items()
        self.assertEqual(sorted_items, [])

    def test_inventory_get_sorted_items_empty_with_items_db(self):
        """Test sorting empty inventory with items_db."""
        items_db = {
            "health_potion": Item(id="health_potion", name="Health Potion", description="", item_type="consumable", effect_id="")
        }
        sorted_items = self.inventory.get_sorted_items(items_db=items_db)
        self.assertEqual(sorted_items, [])

    def test_inventory_get_filtered_items_empty(self):
        """Test filtering empty inventory."""
        filtered = self.inventory.get_filtered_items(item_type="consumable")
        self.assertEqual(filtered, {})

    def test_inventory_hotbar_can_reference_nonexistent_items(self):
        """Test hotbar can reference non-existent items (UI may show empty slot)."""
        # Hotbar is a reference system - it doesn't validate item existence.
        # This allows pre-assigning hotbar slots before items are acquired.
        self.inventory.set_hotbar_item(1, "health_potion")
        self.assertEqual(self.inventory.get_hotbar_item(1), "health_potion")

    def test_inventory_clear_empty(self):
        """Test clearing already empty inventory."""
        self.inventory.clear()
        self.assertEqual(self.inventory.get_all_items(), {})
        self.assertEqual(len(self.inventory.hotbar_slots), 0)

    def test_inventory_add_empty_string_item_id(self):
        """Test adding an empty string item_id (documents current behavior)."""
        # Current behavior allows empty string IDs - no validation
        self.inventory.add("", 1)
        self.assertTrue(self.inventory.has("", 1))

    def test_party_get_battle_party_no_members(self):
        """Test get_battle_party with no party members (player only)."""
        battle_party = self.player.get_battle_party()
        self.assertEqual(len(battle_party), 1)
        self.assertEqual(battle_party[0], self.player)

    def test_party_get_alive_members_empty(self):
        """Test get_alive_party_members on empty party."""
        alive = self.player.get_alive_party_members()
        self.assertEqual(alive, [])

    def test_party_is_party_wiped_only_dead_player(self):
        """Test is_party_wiped with only dead player."""
        self.player.stats.hp = 0
        self.assertTrue(self.player.is_party_wiped())

    def test_party_is_party_wiped_alive_player(self):
        """Test is_party_wiped with alive player (no party members)."""
        self.assertFalse(self.player.is_party_wiped())

    def test_party_remove_member_from_empty(self):
        """Test removing party member from empty party."""
        removed = self.player.remove_party_member("nonexistent_member")
        self.assertIsNone(removed)

    def test_party_get_member_from_empty(self):
        """Test getting party member from empty party."""
        member = self.player.get_party_member("nonexistent_member")
        self.assertIsNone(member)

    def test_party_add_member_at_max_capacity(self):
        """Test adding party member when at max capacity."""
        # Fill party to max capacity
        for i in range(self.player.max_party_size):
            member = self._make_party_member(f"member_{i}", f"Member {i}")
            self.player.add_party_member(member)

        # Try to add one more
        extra_member = self._make_party_member("extra_member", "Extra")
        result = self.player.add_party_member(extra_member)
        self.assertFalse(result)
        self.assertEqual(len(self.player.party), self.player.max_party_size)


class TestZeroHPSP(unittest.TestCase):
    """Test zero HP/SP edge cases."""

    def setUp(self):
        self.stats_zero_hp = Stats(100, 0, 50, 50, 10, 5, 8, 7, 5)  # Zero HP
        self.stats_zero_sp = Stats(100, 100, 50, 0, 10, 5, 8, 7, 5)  # Zero SP
        self.stats_both_zero = Stats(100, 0, 50, 0, 10, 5, 8, 7, 5)  # Both zero

    def test_is_dead_zero_hp(self):
        """Test is_dead() returns True when HP = 0."""
        self.assertTrue(self.stats_zero_hp.is_dead())

    def test_is_dead_zero_hp_not_dead(self):
        """Test is_dead() returns False when HP > 0."""
        stats = Stats(100, 1, 50, 50, 10, 5, 8, 7, 5)
        self.assertFalse(stats.is_dead())

    def test_apply_damage_at_zero_hp_stays_at_zero(self):
        """Test damage application when already at 0 HP stays at 0."""
        self.stats_zero_hp.apply_damage(50)
        # HP should remain at 0, never go negative
        self.assertEqual(self.stats_zero_hp.hp, 0)

    def test_heal_from_zero_hp(self):
        """Test healing from 0 HP."""
        self.stats_zero_hp.heal(30)
        self.assertEqual(self.stats_zero_hp.hp, 30)

    def test_heal_from_zero_hp_to_max(self):
        """Test healing from 0 HP caps at max."""
        self.stats_zero_hp.heal(200)  # More than max
        self.assertEqual(self.stats_zero_hp.hp, self.stats_zero_hp.max_hp)

    def test_status_effect_poison_at_zero_hp(self):
        """Test poison status effect ticking at 0 HP stays at 0."""
        self.stats_zero_hp.add_status_effect("poison", duration=3, stacks=1)
        self.stats_zero_hp.tick_status_effects()
        # HP should remain at 0 (not go negative)
        self.assertEqual(self.stats_zero_hp.hp, 0)

    def test_status_effect_bleed_at_zero_hp(self):
        """Test bleed status effect ticking at 0 HP stays at 0."""
        self.stats_zero_hp.add_status_effect("bleed", duration=2, stacks=1)
        self.stats_zero_hp.tick_status_effects()
        # HP should remain at 0
        self.assertEqual(self.stats_zero_hp.hp, 0)

    def test_status_effect_terror_at_zero_sp(self):
        """Test terror status effect at 0 SP stays at 0."""
        self.stats_zero_sp.add_status_effect("terror", duration=2, stacks=1)
        self.stats_zero_sp.tick_status_effects()
        # SP should remain at 0 (not go negative)
        self.assertEqual(self.stats_zero_sp.sp, 0)

    def test_restore_sp_from_zero(self):
        """Test SP restoration from 0."""
        self.stats_zero_sp.restore_sp(20)
        self.assertEqual(self.stats_zero_sp.sp, 20)

    def test_restore_sp_from_zero_to_max(self):
        """Test SP restoration from 0 caps at max."""
        self.stats_zero_sp.restore_sp(100)  # More than max
        self.assertEqual(self.stats_zero_sp.sp, self.stats_zero_sp.max_sp)

    def test_both_zero_hp_and_sp(self):
        """Test entity with both HP and SP at 0."""
        self.assertTrue(self.stats_both_zero.is_dead())
        self.assertEqual(self.stats_both_zero.hp, 0)
        self.assertEqual(self.stats_both_zero.sp, 0)

    def test_both_zero_heal_hp(self):
        """Test healing HP when both are zero."""
        self.stats_both_zero.heal(30)
        self.assertEqual(self.stats_both_zero.hp, 30)
        self.assertEqual(self.stats_both_zero.sp, 0)  # SP unchanged

    def test_both_zero_restore_sp(self):
        """Test restoring SP when both are zero."""
        self.stats_both_zero.restore_sp(20)
        self.assertEqual(self.stats_both_zero.hp, 0)  # HP unchanged
        self.assertEqual(self.stats_both_zero.sp, 20)

    def test_status_effect_multiple_at_zero(self):
        """Test multiple status effects ticking at zero HP/SP stay at 0."""
        self.stats_both_zero.add_status_effect("poison", duration=2, stacks=1)
        self.stats_both_zero.add_status_effect("terror", duration=2, stacks=1)
        self.stats_both_zero.tick_status_effects()
        # Both should remain at 0
        self.assertEqual(self.stats_both_zero.hp, 0)
        self.assertEqual(self.stats_both_zero.sp, 0)

    def test_level_up_at_zero_hp_restores_to_max(self):
        """Test level-up at 0 HP restores HP to max."""
        self.stats_zero_hp.level = 1
        self.stats_zero_hp.exp = 0
        # Trigger level up via add_exp
        level_ups = self.stats_zero_hp.add_exp(100)
        # Level up should have occurred and HP should be restored to max
        self.assertGreater(len(level_ups), 0, "Should have leveled up")
        self.assertEqual(self.stats_zero_hp.hp, self.stats_zero_hp.max_hp)

    def test_apply_damage_large_at_zero_hp(self):
        """Test applying very large damage at 0 HP stays at 0."""
        self.stats_zero_hp.apply_damage(999999)
        # HP should remain at 0
        self.assertEqual(self.stats_zero_hp.hp, 0)


if __name__ == "__main__":
    unittest.main()

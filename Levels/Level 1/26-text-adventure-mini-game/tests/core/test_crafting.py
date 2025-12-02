"""Unit tests for core/crafting.py - CraftingSystem, CraftingProgress, Recipe."""

import json
import os
import tempfile
import unittest

from core.crafting import (
    Recipe,
    CraftingProgress,
    CraftingSystem,
    load_crafting_system,
)
from core.items import Inventory


class TestRecipe(unittest.TestCase):
    def test_recipe_basic(self):
        recipe = Recipe(
            id="health_potion",
            name="Health Potion",
            description="A healing potion",
            category="alchemy",
            ingredients={"herb": 2, "water": 1},
            result_item_id="health_potion",
            result_quantity=1,
            required_level=1,
        )
        self.assertEqual(recipe.id, "health_potion")
        self.assertEqual(recipe.name, "Health Potion")
        self.assertEqual(recipe.category, "alchemy")
        self.assertEqual(recipe.ingredients, {"herb": 2, "water": 1})
        self.assertEqual(recipe.result_quantity, 1)

    def test_recipe_defaults(self):
        recipe = Recipe(
            id="test",
            name="Test",
            description="",
            category="basic",
            ingredients={},
            result_item_id="test",
        )
        self.assertEqual(recipe.result_quantity, 1)
        self.assertEqual(recipe.required_level, 1)


class TestCraftingProgress(unittest.TestCase):
    def setUp(self):
        self.progress = CraftingProgress()

    def test_progress_defaults(self):
        self.assertEqual(self.progress.crafting_level, 1)
        self.assertEqual(self.progress.crafting_xp, 0)
        self.assertEqual(self.progress.xp_to_next_level, 100)
        self.assertEqual(self.progress.discovered_recipes, [])
        self.assertEqual(self.progress.crafted_counts, {})

    def test_add_xp_no_level_up(self):
        leveled_up = self.progress.add_xp(50)
        self.assertFalse(leveled_up)
        self.assertEqual(self.progress.crafting_xp, 50)
        self.assertEqual(self.progress.crafting_level, 1)

    def test_add_xp_level_up(self):
        leveled_up = self.progress.add_xp(100)
        self.assertTrue(leveled_up)
        self.assertEqual(self.progress.crafting_level, 2)
        self.assertEqual(self.progress.crafting_xp, 0)

    def test_add_xp_multiple_level_ups(self):
        leveled_up = self.progress.add_xp(500)
        self.assertTrue(leveled_up)
        self.assertGreater(self.progress.crafting_level, 2)

    def test_xp_to_next_level_increases(self):
        initial_xp_required = self.progress.xp_to_next_level
        self.progress.add_xp(100)  # Level up
        self.assertGreater(self.progress.xp_to_next_level, initial_xp_required)

    def test_discover_recipe_new(self):
        result = self.progress.discover_recipe("health_potion")
        self.assertTrue(result)
        self.assertIn("health_potion", self.progress.discovered_recipes)

    def test_discover_recipe_already_discovered(self):
        self.progress.discover_recipe("health_potion")
        result = self.progress.discover_recipe("health_potion")
        self.assertFalse(result)
        self.assertEqual(self.progress.discovered_recipes.count("health_potion"), 1)

    def test_record_craft(self):
        self.progress.record_craft("health_potion")
        self.assertEqual(self.progress.crafted_counts["health_potion"], 1)

    def test_record_craft_multiple(self):
        self.progress.record_craft("health_potion")
        self.progress.record_craft("health_potion")
        self.progress.record_craft("health_potion")
        self.assertEqual(self.progress.crafted_counts["health_potion"], 3)

    def test_to_dict(self):
        self.progress.crafting_level = 3
        self.progress.crafting_xp = 75
        self.progress.discover_recipe("potion")
        self.progress.record_craft("potion")

        data = self.progress.to_dict()

        self.assertEqual(data["crafting_level"], 3)
        self.assertEqual(data["crafting_xp"], 75)
        self.assertIn("potion", data["discovered_recipes"])
        self.assertEqual(data["crafted_counts"]["potion"], 1)

    def test_from_dict(self):
        data = {
            "crafting_level": 5,
            "crafting_xp": 200,
            "xp_to_next_level": 500,
            "discovered_recipes": ["recipe1", "recipe2"],
            "crafted_counts": {"recipe1": 10},
        }
        progress = CraftingProgress.from_dict(data)

        self.assertEqual(progress.crafting_level, 5)
        self.assertEqual(progress.crafting_xp, 200)
        self.assertEqual(progress.xp_to_next_level, 500)
        self.assertEqual(len(progress.discovered_recipes), 2)
        self.assertEqual(progress.crafted_counts["recipe1"], 10)

    def test_from_dict_defaults(self):
        progress = CraftingProgress.from_dict({})
        self.assertEqual(progress.crafting_level, 1)
        self.assertEqual(progress.crafting_xp, 0)


class TestCraftingSystem(unittest.TestCase):
    def setUp(self):
        self.recipes_data = {
            "categories": {
                "basic": {"name": "Basic"},
                "alchemy": {"name": "Alchemy"},
            },
            "recipes": [
                {
                    "id": "health_potion",
                    "name": "Health Potion",
                    "description": "Restores HP",
                    "category": "alchemy",
                    "ingredients": {"herb": 2, "water": 1},
                    "result": {"item_id": "health_potion", "quantity": 1},
                    "required_level": 1,
                },
                {
                    "id": "iron_sword",
                    "name": "Iron Sword",
                    "description": "A basic sword",
                    "category": "smithing",
                    "ingredients": {"iron_ore": 3, "coal": 1},
                    "result": {"item_id": "iron_sword", "quantity": 1},
                    "required_level": 3,
                },
            ],
        }
        # Create temp file with recipes
        self.temp_file = tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        )
        json.dump(self.recipes_data, self.temp_file)
        self.temp_file.close()

        self.system = CraftingSystem(self.temp_file.name)
        self.inventory = Inventory()

    def tearDown(self):
        os.unlink(self.temp_file.name)

    def test_load_recipes(self):
        self.assertEqual(len(self.system.recipes), 2)
        self.assertIn("health_potion", self.system.recipes)
        self.assertIn("iron_sword", self.system.recipes)

    def test_get_recipe(self):
        recipe = self.system.get_recipe("health_potion")
        self.assertIsNotNone(recipe)
        self.assertEqual(recipe.name, "Health Potion")

    def test_get_recipe_not_found(self):
        recipe = self.system.get_recipe("nonexistent")
        self.assertIsNone(recipe)

    def test_get_all_recipes(self):
        recipes = self.system.get_all_recipes()
        self.assertEqual(len(recipes), 2)
        # Verify it's a copy
        recipes["test"] = None
        self.assertEqual(len(self.system.recipes), 2)

    def test_get_recipes_by_category(self):
        alchemy_recipes = self.system.get_recipes_by_category("alchemy")
        self.assertEqual(len(alchemy_recipes), 1)
        self.assertEqual(alchemy_recipes[0].id, "health_potion")

    def test_get_recipes_by_category_empty(self):
        recipes = self.system.get_recipes_by_category("enchanting")
        self.assertEqual(len(recipes), 0)

    def test_can_craft_true(self):
        self.inventory.add("herb", 2)
        self.inventory.add("water", 1)
        recipe = self.system.get_recipe("health_potion")
        self.assertTrue(self.system.can_craft(recipe, self.inventory))

    def test_can_craft_false_missing_ingredients(self):
        self.inventory.add("herb", 1)  # Only 1, need 2
        self.inventory.add("water", 1)
        recipe = self.system.get_recipe("health_potion")
        self.assertFalse(self.system.can_craft(recipe, self.inventory))

    def test_can_craft_false_no_ingredients(self):
        recipe = self.system.get_recipe("health_potion")
        self.assertFalse(self.system.can_craft(recipe, self.inventory))

    def test_get_missing_ingredients(self):
        self.inventory.add("herb", 1)  # Have 1, need 2
        # Missing water entirely
        recipe = self.system.get_recipe("health_potion")
        missing = self.system.get_missing_ingredients(recipe, self.inventory, {})

        self.assertIn("herb", missing)
        self.assertEqual(missing["herb"], (1, 2))  # (have, need)
        self.assertIn("water", missing)
        self.assertEqual(missing["water"], (0, 1))

    def test_get_missing_ingredients_none_missing(self):
        self.inventory.add("herb", 5)
        self.inventory.add("water", 3)
        recipe = self.system.get_recipe("health_potion")
        missing = self.system.get_missing_ingredients(recipe, self.inventory, {})
        self.assertEqual(len(missing), 0)

    def test_craft_success(self):
        self.inventory.add("herb", 2)
        self.inventory.add("water", 1)
        recipe = self.system.get_recipe("health_potion")

        success, message = self.system.craft(recipe, self.inventory)

        self.assertTrue(success)
        self.assertIn("Crafted", message)
        # Ingredients consumed
        self.assertEqual(self.inventory.get_quantity("herb"), 0)
        self.assertEqual(self.inventory.get_quantity("water"), 0)
        # Result added
        self.assertEqual(self.inventory.get_quantity("health_potion"), 1)

    def test_craft_failure_missing_ingredients(self):
        recipe = self.system.get_recipe("health_potion")
        success, message = self.system.craft(recipe, self.inventory)

        self.assertFalse(success)
        self.assertIn("Missing", message)

    def test_craft_failure_insufficient_level(self):
        self.inventory.add("iron_ore", 3)
        self.inventory.add("coal", 1)
        recipe = self.system.get_recipe("iron_sword")
        progress = CraftingProgress()  # Level 1

        success, message = self.system.craft(recipe, self.inventory, progress)

        self.assertFalse(success)
        self.assertIn("level", message.lower())

    def test_craft_with_progress_grants_xp(self):
        self.inventory.add("herb", 2)
        self.inventory.add("water", 1)
        recipe = self.system.get_recipe("health_potion")
        progress = CraftingProgress()
        initial_xp = progress.crafting_xp

        self.system.craft(recipe, self.inventory, progress)

        self.assertGreater(progress.crafting_xp, initial_xp)

    def test_craft_records_in_progress(self):
        self.inventory.add("herb", 2)
        self.inventory.add("water", 1)
        recipe = self.system.get_recipe("health_potion")
        progress = CraftingProgress()

        self.system.craft(recipe, self.inventory, progress)

        self.assertEqual(progress.crafted_counts["health_potion"], 1)

    def test_get_available_recipes_discovered_only(self):
        progress = CraftingProgress()
        progress.discover_recipe("health_potion")

        available = self.system.get_available_recipes(
            self.inventory, {}, progress, show_all=False
        )

        self.assertEqual(len(available), 1)
        self.assertEqual(available[0][0].id, "health_potion")

    def test_get_available_recipes_show_all(self):
        progress = CraftingProgress()

        available = self.system.get_available_recipes(
            self.inventory, {}, progress, show_all=True
        )

        self.assertEqual(len(available), 2)

    def test_get_available_recipes_level_filter(self):
        progress = CraftingProgress()  # Level 1

        available = self.system.get_available_recipes(
            self.inventory, {}, progress, show_all=True
        )

        # Find iron_sword (requires level 3)
        iron_sword_entry = next(
            (r, can) for r, can in available if r.id == "iron_sword"
        )
        self.assertFalse(iron_sword_entry[1])  # Cannot craft due to level

    def test_discover_recipes_from_items_basic(self):
        progress = CraftingProgress()
        # Add an ingredient from health_potion recipe
        self.inventory.add("herb", 1)

        newly_discovered = self.system.discover_recipes_from_items(
            self.inventory, progress
        )

        self.assertIn("health_potion", newly_discovered)

    def test_discover_recipes_already_discovered(self):
        progress = CraftingProgress()
        progress.discover_recipe("health_potion")
        self.inventory.add("herb", 1)

        newly_discovered = self.system.discover_recipes_from_items(
            self.inventory, progress
        )

        self.assertNotIn("health_potion", newly_discovered)


class TestLoadCraftingSystem(unittest.TestCase):
    def test_load_nonexistent_file(self):
        system = load_crafting_system("/nonexistent/path.json")
        self.assertEqual(len(system.recipes), 0)

    def test_load_valid_file(self):
        data = {
            "recipes": [
                {
                    "id": "test_recipe",
                    "name": "Test",
                    "category": "basic",
                    "ingredients": {},
                    "result": {"item_id": "test", "quantity": 1},
                }
            ]
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            temp_path = f.name

        try:
            system = load_crafting_system(temp_path)
            self.assertIn("test_recipe", system.recipes)
        finally:
            os.unlink(temp_path)


class TestDiscoverRecipesForPlayer(unittest.TestCase):
    """Test cases for the discover_recipes_for_player helper function."""

    def setUp(self):
        """Create a mock player-like object for testing."""
        # Simple class that mimics Player for crafting progress
        class MockPlayer:
            def __init__(self):
                self.crafting_progress = None

        self.player = MockPlayer()

    def test_discover_creates_progress_if_missing(self):
        """Test that crafting progress is created if player lacks it."""
        from core.crafting import discover_recipes_for_player

        self.assertIsNone(self.player.crafting_progress)

        newly_discovered = discover_recipes_for_player(self.player, ["health_potion"])

        self.assertIsNotNone(self.player.crafting_progress)
        self.assertIn("health_potion", self.player.crafting_progress.discovered_recipes)
        self.assertEqual(newly_discovered, ["health_potion"])

    def test_discover_empty_list_returns_empty(self):
        """Test that empty recipe list returns empty result."""
        from core.crafting import discover_recipes_for_player

        result = discover_recipes_for_player(self.player, [])

        self.assertEqual(result, [])
        # crafting_progress should not be created for empty list
        self.assertIsNone(self.player.crafting_progress)

    def test_discover_already_known_not_returned(self):
        """Test that already-discovered recipes are not in return list."""
        from core.crafting import discover_recipes_for_player, CraftingProgress

        self.player.crafting_progress = CraftingProgress()
        self.player.crafting_progress.discover_recipe("health_potion")

        newly_discovered = discover_recipes_for_player(self.player, ["health_potion"])

        self.assertEqual(newly_discovered, [])
        # Should still only have one entry
        self.assertEqual(
            self.player.crafting_progress.discovered_recipes.count("health_potion"),
            1
        )

    def test_discover_multiple_recipes(self):
        """Test discovering multiple recipes at once."""
        from core.crafting import discover_recipes_for_player

        newly_discovered = discover_recipes_for_player(
            self.player,
            ["health_potion", "mana_potion", "antidote"]
        )

        self.assertEqual(len(newly_discovered), 3)
        self.assertIn("health_potion", newly_discovered)
        self.assertIn("mana_potion", newly_discovered)
        self.assertIn("antidote", newly_discovered)

        # All should be in progress
        self.assertEqual(len(self.player.crafting_progress.discovered_recipes), 3)

    def test_discover_partial_new_recipes(self):
        """Test discovering mix of new and already-known recipes."""
        from core.crafting import discover_recipes_for_player, CraftingProgress

        self.player.crafting_progress = CraftingProgress()
        self.player.crafting_progress.discover_recipe("health_potion")

        newly_discovered = discover_recipes_for_player(
            self.player,
            ["health_potion", "mana_potion", "antidote"]
        )

        # Only new ones returned
        self.assertEqual(len(newly_discovered), 2)
        self.assertNotIn("health_potion", newly_discovered)
        self.assertIn("mana_potion", newly_discovered)
        self.assertIn("antidote", newly_discovered)

    def test_discover_preserves_existing_progress(self):
        """Test that existing progress data is preserved."""
        from core.crafting import discover_recipes_for_player, CraftingProgress

        self.player.crafting_progress = CraftingProgress()
        self.player.crafting_progress.crafting_level = 5
        self.player.crafting_progress.crafting_xp = 250
        self.player.crafting_progress.record_craft("old_recipe")

        discover_recipes_for_player(self.player, ["new_recipe"])

        # Original progress should be preserved
        self.assertEqual(self.player.crafting_progress.crafting_level, 5)
        self.assertEqual(self.player.crafting_progress.crafting_xp, 250)
        self.assertEqual(self.player.crafting_progress.crafted_counts["old_recipe"], 1)
        # New recipe should be added
        self.assertIn("new_recipe", self.player.crafting_progress.discovered_recipes)

    def test_discover_with_no_crafting_progress_attr(self):
        """Test with player object that has no crafting_progress attribute."""
        from core.crafting import discover_recipes_for_player

        # Create player without crafting_progress attribute
        class MinimalPlayer:
            pass

        player = MinimalPlayer()

        newly_discovered = discover_recipes_for_player(player, ["recipe_1"])

        self.assertEqual(newly_discovered, ["recipe_1"])
        self.assertIsNotNone(player.crafting_progress)
        self.assertIn("recipe_1", player.crafting_progress.discovered_recipes)


if __name__ == "__main__":
    unittest.main()

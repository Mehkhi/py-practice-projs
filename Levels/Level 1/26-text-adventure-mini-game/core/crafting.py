"""Crafting system for combining materials into items."""

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, TYPE_CHECKING

from .data_loader import load_json_file
from .items import Inventory, Item

if TYPE_CHECKING:
    from .entities import Player


@dataclass
class Recipe:
    """Represents a crafting recipe."""
    id: str
    name: str
    description: str
    category: str  # "basic", "alchemy", "smithing", "enchanting"
    ingredients: Dict[str, int]  # item_id -> quantity required
    result_item_id: str
    result_quantity: int = 1
    required_level: int = 1  # Crafting level required


@dataclass
class CraftingProgress:
    """Tracks player's crafting progress and unlocks."""
    crafting_level: int = 1
    crafting_xp: int = 0
    xp_to_next_level: int = 100
    discovered_recipes: List[str] = field(default_factory=list)
    crafted_counts: Dict[str, int] = field(default_factory=dict)  # recipe_id -> times crafted

    def add_xp(self, amount: int) -> bool:
        """Add crafting XP. Returns True if leveled up."""
        self.crafting_xp += amount
        leveled_up = False
        while self.crafting_xp >= self.xp_to_next_level:
            self.crafting_xp -= self.xp_to_next_level
            self.crafting_level += 1
            self.xp_to_next_level = self._calculate_xp_for_level(self.crafting_level)
            leveled_up = True
        return leveled_up

    def _calculate_xp_for_level(self, level: int) -> int:
        """Calculate XP needed for next level."""
        return int(100 * (1.5 ** (level - 1)))

    def discover_recipe(self, recipe_id: str) -> bool:
        """Mark a recipe as discovered. Returns True if newly discovered."""
        if recipe_id not in self.discovered_recipes:
            self.discovered_recipes.append(recipe_id)
            return True
        return False

    def record_craft(self, recipe_id: str) -> None:
        """Record that a recipe was crafted."""
        self.crafted_counts[recipe_id] = self.crafted_counts.get(recipe_id, 0) + 1

    def to_dict(self) -> Dict:
        """Serialize to dictionary for saving."""
        return {
            "crafting_level": self.crafting_level,
            "crafting_xp": self.crafting_xp,
            "xp_to_next_level": self.xp_to_next_level,
            "discovered_recipes": self.discovered_recipes,
            "crafted_counts": self.crafted_counts,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "CraftingProgress":
        """Deserialize from dictionary."""
        progress = cls()
        progress.crafting_level = data.get("crafting_level", 1)
        progress.crafting_xp = data.get("crafting_xp", 0)
        progress.xp_to_next_level = data.get("xp_to_next_level", 100)
        progress.discovered_recipes = list(data.get("discovered_recipes", []))
        progress.crafted_counts = dict(data.get("crafted_counts", {}))
        return progress


class CraftingSystem:
    """Manages crafting recipes and crafting operations."""

    def __init__(self, recipes_path: str = os.path.join("data", "recipes.json")):
        self.recipes: Dict[str, Recipe] = {}
        self.categories: Dict[str, Dict] = {}
        self._load_recipes(recipes_path)

    def _load_recipes(self, path: str) -> None:
        """Load recipes from JSON file."""
        data = load_json_file(path, default={}, context="Loading recipes")

        # Load categories
        self.categories = data.get("categories", {})

        # Load recipes
        for recipe_data in data.get("recipes", []):
            result = recipe_data.get("result", {})
            recipe = Recipe(
                id=recipe_data["id"],
                name=recipe_data.get("name", recipe_data["id"]),
                description=recipe_data.get("description", ""),
                category=recipe_data.get("category", "basic"),
                ingredients=recipe_data.get("ingredients", {}),
                result_item_id=result.get("item_id", recipe_data["id"]),
                result_quantity=result.get("quantity", 1),
                required_level=recipe_data.get("required_level", 1),
            )
            self.recipes[recipe.id] = recipe

    def get_recipe(self, recipe_id: str) -> Optional[Recipe]:
        """Get a recipe by ID."""
        return self.recipes.get(recipe_id)

    def get_all_recipes(self) -> Dict[str, Recipe]:
        """Get all recipes."""
        return self.recipes.copy()

    def get_recipes_by_category(self, category: str) -> List[Recipe]:
        """Get all recipes in a category."""
        return [r for r in self.recipes.values() if r.category == category]

    def get_available_recipes(
        self,
        inventory: Inventory,
        items_db: Dict[str, Item],
        progress: Optional[CraftingProgress] = None,
        show_all: bool = False,
    ) -> List[Tuple[Recipe, bool]]:
        """
        Get recipes with availability status.

        Args:
            inventory: Player's inventory
            items_db: Item database
            progress: Player's crafting progress (for level checks)
            show_all: If True, show all recipes; if False, only discovered ones

        Returns:
            List of (recipe, can_craft) tuples
        """
        result = []
        crafting_level = progress.crafting_level if progress else 1
        discovered = progress.discovered_recipes if progress else []

        for recipe in self.recipes.values():
            # Check if recipe should be shown
            if not show_all and recipe.id not in discovered:
                continue

            # Check level requirement
            if recipe.required_level > crafting_level:
                result.append((recipe, False))
                continue

            # Check if player has all ingredients
            can_craft = self.can_craft(recipe, inventory)
            result.append((recipe, can_craft))

        return result

    def can_craft(self, recipe: Recipe, inventory: Inventory) -> bool:
        """Check if a recipe can be crafted with current inventory."""
        for item_id, required_qty in recipe.ingredients.items():
            if not inventory.has(item_id, required_qty):
                return False
        return True

    def get_missing_ingredients(
        self,
        recipe: Recipe,
        inventory: Inventory,
        items_db: Dict[str, Item],
    ) -> Dict[str, Tuple[int, int]]:
        """
        Get missing ingredients for a recipe.

        Returns:
            Dict of item_id -> (have, need) tuples
        """
        missing = {}
        for item_id, required_qty in recipe.ingredients.items():
            have = inventory.get_quantity(item_id)
            if have < required_qty:
                missing[item_id] = (have, required_qty)
        return missing

    def craft(
        self,
        recipe: Recipe,
        inventory: Inventory,
        progress: Optional[CraftingProgress] = None,
    ) -> Tuple[bool, str]:
        """
        Attempt to craft a recipe.

        Args:
            recipe: The recipe to craft
            inventory: Player's inventory
            progress: Player's crafting progress

        Returns:
            Tuple of (success, message)
        """
        # Check level requirement
        if progress and recipe.required_level > progress.crafting_level:
            return False, f"Requires crafting level {recipe.required_level}"

        # Check ingredients
        if not self.can_craft(recipe, inventory):
            return False, "Missing ingredients"

        # Remove ingredients
        for item_id, qty in recipe.ingredients.items():
            if not inventory.remove(item_id, qty):
                # Rollback shouldn't be needed if can_craft passed, but safety first
                return False, "Failed to consume ingredients"

        # Add result
        inventory.add(recipe.result_item_id, recipe.result_quantity)

        # Update progress
        if progress:
            progress.record_craft(recipe.id)
            # Grant XP based on recipe level
            xp_gained = recipe.required_level * 25
            leveled_up = progress.add_xp(xp_gained)

            if leveled_up:
                return True, f"Crafted {recipe.name}! Level up! Now level {progress.crafting_level}"

        return True, f"Crafted {recipe.name}!"

    def discover_recipes_from_items(
        self,
        inventory: Inventory,
        progress: CraftingProgress,
    ) -> List[str]:
        """
        Auto-discover recipes based on items in inventory.

        Returns list of newly discovered recipe IDs.
        """
        newly_discovered = []

        for recipe in self.recipes.values():
            if recipe.id in progress.discovered_recipes:
                continue

            # Check if player has at least one of each ingredient type
            has_any_ingredient = False
            for item_id in recipe.ingredients.keys():
                if inventory.has(item_id, 1):
                    has_any_ingredient = True
                    break

            # Discover basic recipes automatically, others need ingredients
            if recipe.category == "basic" or has_any_ingredient:
                if progress.discover_recipe(recipe.id):
                    newly_discovered.append(recipe.id)

        return newly_discovered


def discover_recipes_for_player(player: "Player", recipe_ids: List[str]) -> List[str]:
    """
    Discover recipes for a player.

    Args:
        player: The player entity
        recipe_ids: List of recipe IDs to discover

    Returns:
        List of newly discovered recipe IDs (recipes that weren't already discovered)
    """
    if not recipe_ids:
        return []

    # Get or create crafting progress
    if not hasattr(player, "crafting_progress") or player.crafting_progress is None:
        player.crafting_progress = CraftingProgress()

    newly_discovered = []
    for recipe_id in recipe_ids:
        if player.crafting_progress.discover_recipe(recipe_id):
            newly_discovered.append(recipe_id)

    return newly_discovered


def load_crafting_system(path: str = os.path.join("data", "recipes.json")) -> CraftingSystem:
    """Factory function to create a CraftingSystem."""
    return CraftingSystem(path)

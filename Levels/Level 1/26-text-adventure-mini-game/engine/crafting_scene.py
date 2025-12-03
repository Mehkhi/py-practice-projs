"""Crafting scene for creating items from materials."""

from typing import Dict, List, Optional, Tuple, TYPE_CHECKING

import pygame

from .base_menu_scene import BaseMenuScene
from .assets import AssetManager
from .ui import Menu, MessageBox, NineSlicePanel, draw_contextual_help
from .theme import Colors, Fonts, Layout
from core.world import World
from core.entities import Player
from core.items import Item
from core.crafting import CraftingSystem, CraftingProgress, Recipe
from core.tutorial_system import TipTrigger

if TYPE_CHECKING:
    from .scene import SceneManager


class CraftingScene(BaseMenuScene):
    """Scene for crafting items from materials."""

    # Scene modes
    MODE_CATEGORY = "category"
    MODE_RECIPE_LIST = "recipe_list"
    MODE_RECIPE_DETAIL = "recipe_detail"

    def __init__(
        self,
        manager: Optional["SceneManager"],
        world: World,
        player: Player,
        items_db: Dict[str, Item],
        crafting_system: Optional[CraftingSystem] = None,
        assets: Optional[AssetManager] = None,
        scale: int = 2,
    ):
        super().__init__(manager, assets, scale)
        self.world = world
        self.player = player
        self.items_db = items_db

        # Initialize crafting system
        self.crafting_system = crafting_system or CraftingSystem()

        # Get or create crafting progress from player
        if hasattr(player, "crafting_progress") and player.crafting_progress:
            self.progress = player.crafting_progress
        else:
            self.progress = CraftingProgress()
            # Discover basic recipes automatically
            for recipe in self.crafting_system.recipes.values():
                if recipe.category == "basic":
                    self.progress.discover_recipe(recipe.id)

        # Auto-discover recipes based on inventory
        self.crafting_system.discover_recipes_from_items(
            player.inventory, self.progress
        )

        # UI state
        self.mode = self.MODE_CATEGORY
        self.menu: Optional[Menu] = None
        self.message_box = MessageBox(position=(20, 380), width=600, height=80)

        # Category/recipe tracking
        self.categories = list(self.crafting_system.categories.keys())
        self.current_category: Optional[str] = None
        self.current_recipes: List[Tuple[Recipe, bool]] = []
        self.recipe_mapping: Dict[int, str] = {}
        self.selected_recipe: Optional[Recipe] = None

        # Result message
        self.result_message: Optional[str] = None
        self.result_timer = 0.0
        self.result_duration = 2.0

        self._refresh_category_menu()

    def _refresh_category_menu(self) -> None:
        """Show the category selection menu."""
        self.mode = self.MODE_CATEGORY
        self.current_category = None
        self.selected_recipe = None

        options = []
        for cat_id in self.categories:
            cat_info = self.crafting_system.categories.get(cat_id, {})
            cat_name = cat_info.get("name", cat_id.title())
            # Count available recipes in category
            recipes = self.crafting_system.get_recipes_by_category(cat_id)
            discovered = [r for r in recipes if r.id in self.progress.discovered_recipes]
            options.append(f"{cat_name} ({len(discovered)})")

        options.append("Back")
        self.menu = Menu(options, position=(50, 120))
        self.message_box.set_text(
            f"Crafting Level {self.progress.crafting_level} | "
            f"XP: {self.progress.crafting_xp}/{self.progress.xp_to_next_level}"
        )

    def _refresh_recipe_menu(self) -> None:
        """Show recipes in the current category."""
        self.mode = self.MODE_RECIPE_LIST
        self.selected_recipe = None
        self.recipe_mapping.clear()

        if not self.current_category:
            self._refresh_category_menu()
            return

        # Get recipes for category
        all_recipes = self.crafting_system.get_recipes_by_category(self.current_category)
        discovered = [r for r in all_recipes if r.id in self.progress.discovered_recipes]

        # Check which can be crafted
        self.current_recipes = []
        options = []
        idx = 0

        for recipe in discovered:
            can_craft = self.crafting_system.can_craft(recipe, self.player.inventory)
            self.current_recipes.append((recipe, can_craft))

            # Format: [*] Recipe Name (craftable) or [ ] Recipe Name (missing materials)
            status = "[+]" if can_craft else "[-]"
            level_indicator = ""
            if recipe.required_level > self.progress.crafting_level:
                status = "[X]"
                level_indicator = f" (Lv{recipe.required_level})"

            options.append(f"{status} {recipe.name}{level_indicator}")
            self.recipe_mapping[idx] = recipe.id
            idx += 1

        options.append("Back")
        self.menu = Menu(options, position=(50, 120))

        cat_info = self.crafting_system.categories.get(self.current_category, {})
        cat_desc = cat_info.get("description", "")
        self.message_box.set_text(cat_desc if cat_desc else "Select a recipe to view details.")

    def _show_recipe_detail(self, recipe: Recipe) -> None:
        """Show details for a specific recipe."""
        self.mode = self.MODE_RECIPE_DETAIL
        self.selected_recipe = recipe

        can_craft = self.crafting_system.can_craft(recipe, self.player.inventory)

        options = []
        if can_craft and recipe.required_level <= self.progress.crafting_level:
            options.append("Craft")
        options.append("Back")

        self.menu = Menu(options, position=(50, 300))
        self._update_recipe_message()

    def _update_recipe_message(self) -> None:
        """Update message box with recipe info."""
        if not self.selected_recipe:
            return

        recipe = self.selected_recipe
        result_item = self.items_db.get(recipe.result_item_id)
        result_name = result_item.name if result_item else recipe.result_item_id

        msg = f"Creates: {result_name}"
        if recipe.result_quantity > 1:
            msg += f" x{recipe.result_quantity}"

        self.message_box.set_text(msg)

    def _handle_craft(self) -> None:
        """Attempt to craft the selected recipe."""
        if not self.selected_recipe:
            return

        crafted_total_before = sum(self.progress.crafted_counts.values())

        success, message = self.crafting_system.craft(
            self.selected_recipe,
            self.player.inventory,
            self.progress,
        )

        self.result_message = message
        self.result_timer = 0.0

        if success:
            # Update player's crafting progress
            if hasattr(self.player, "crafting_progress"):
                self.player.crafting_progress = self.progress

            if crafted_total_before == 0:
                tutorial_manager = self.get_manager_attr(
                    "tutorial_manager", "_craft_selected_recipe"
                )
                if tutorial_manager:
                    tutorial_manager.trigger_tip(TipTrigger.FIRST_CRAFTING)

            # Refresh to show updated state
            self._show_recipe_detail(self.selected_recipe)

    def _handle_selection(self) -> None:
        """Handle menu selection based on current mode."""
        if not self.menu:
            return

        selected_idx = self.menu.selected_index
        selected_option = self.menu.get_selected()

        if self.mode == self.MODE_CATEGORY:
            if selected_option == "Back":
                self.manager.pop()
            elif selected_idx < len(self.categories):
                self.current_category = self.categories[selected_idx]
                self._refresh_recipe_menu()

        elif self.mode == self.MODE_RECIPE_LIST:
            if selected_option == "Back":
                self._refresh_category_menu()
            elif selected_idx in self.recipe_mapping:
                recipe_id = self.recipe_mapping[selected_idx]
                recipe = self.crafting_system.get_recipe(recipe_id)
                if recipe:
                    self._show_recipe_detail(recipe)

        elif self.mode == self.MODE_RECIPE_DETAIL:
            if selected_option == "Back":
                self._refresh_recipe_menu()
            elif selected_option == "Craft":
                self._handle_craft()

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle input events."""
        if event.type != pygame.KEYDOWN or not self.menu:
            return

        if event.key == pygame.K_UP:
            self.menu.move_selection(-1)
        elif event.key == pygame.K_DOWN:
            self.menu.move_selection(1)
        elif event.key == pygame.K_ESCAPE:
            if self.mode == self.MODE_CATEGORY:
                self.manager.pop()
            elif self.mode == self.MODE_RECIPE_LIST:
                self._refresh_category_menu()
            elif self.mode == self.MODE_RECIPE_DETAIL:
                self._refresh_recipe_menu()
        elif event.key == pygame.K_RETURN:
            self._handle_selection()
        # Allow ESCAPE to dismiss result message
        elif self.result_message and event.key == pygame.K_ESCAPE:
            self.result_message = None
            self.result_timer = 0.0

    def update(self, dt: float) -> None:
        """Update scene state."""
        if self.result_message:
            self.result_timer += dt
            if self.result_timer >= self.result_duration:
                self.result_message = None

    def draw(self, surface: pygame.Surface) -> None:
        """Render the crafting scene."""
        surface.fill((20, 25, 35))

        font = self.assets.get_font("default")
        small_font = self.assets.get_font("small") or font
        large_font = self.assets.get_font("large", 24) or font

        # Title
        title_text = "Crafting"
        if self.mode == self.MODE_RECIPE_LIST and self.current_category:
            cat_info = self.crafting_system.categories.get(self.current_category, {})
            title_text = cat_info.get("name", self.current_category.title())
        elif self.mode == self.MODE_RECIPE_DETAIL and self.selected_recipe:
            title_text = self.selected_recipe.name

        title_surface = large_font.render(title_text, True, Colors.TEXT_PRIMARY)
        surface.blit(title_surface, (20, 20))

        # Crafting level display
        level_text = f"Crafting Lv.{self.progress.crafting_level}"
        level_surface = small_font.render(level_text, True, Colors.TEXT_INFO)
        surface.blit(level_surface, (20, 55))

        # XP bar
        xp_bar_width = 150
        xp_bar_height = 8
        xp_bar_x = 20
        xp_bar_y = 75
        xp_ratio = self.progress.crafting_xp / max(1, self.progress.xp_to_next_level)

        pygame.draw.rect(surface, (60, 60, 80), (xp_bar_x, xp_bar_y, xp_bar_width, xp_bar_height))
        pygame.draw.rect(surface, (100, 180, 255), (xp_bar_x, xp_bar_y, int(xp_bar_width * xp_ratio), xp_bar_height))
        pygame.draw.rect(surface, (255, 255, 255), (xp_bar_x, xp_bar_y, xp_bar_width, xp_bar_height), 1)

        xp_text = f"{self.progress.crafting_xp}/{self.progress.xp_to_next_level} XP"
        xp_surface = small_font.render(xp_text, True, (200, 200, 200))
        surface.blit(xp_surface, (xp_bar_x + xp_bar_width + 10, xp_bar_y - 2))

        # Draw recipe details if in detail mode
        if self.mode == self.MODE_RECIPE_DETAIL and self.selected_recipe:
            self._draw_recipe_details(surface, font, small_font)

        # Draw menu
        if self.menu:
            self.menu.draw(
                surface,
                font,
                theme={
                    "active": Colors.TEXT_HIGHLIGHT,
                    "inactive": Colors.TEXT_SECONDARY,
                    "disabled": Colors.TEXT_DISABLED
                }
            )

        # Draw message box
        self.message_box.draw(surface, small_font, panel=self.panel)

        # Draw result message overlay
        if self.result_message:
            self._draw_result_message(surface, font)

        # Draw help text at bottom
        self._draw_help_text(surface, small_font)

    def _draw_recipe_details(
        self,
        surface: pygame.Surface,
        font: pygame.font.Font,
        small_font: pygame.font.Font,
    ) -> None:
        """Draw detailed recipe information."""
        if not self.selected_recipe:
            return

        recipe = self.selected_recipe
        x_start = 50
        y_start = 120
        line_height = 22

        # Description
        desc_surface = small_font.render(recipe.description, True, Colors.TEXT_SECONDARY)
        surface.blit(desc_surface, (x_start, y_start))
        y_start += line_height + 10

        # Required level
        level_color = Colors.TEXT_SUCCESS if recipe.required_level <= self.progress.crafting_level else Colors.TEXT_ERROR
        level_text = f"Required Level: {recipe.required_level}"
        level_surface = small_font.render(level_text, True, level_color)
        surface.blit(level_surface, (x_start, y_start))
        y_start += line_height + 10

        # Ingredients header
        ing_header = small_font.render("Ingredients:", True, Colors.ACCENT)
        surface.blit(ing_header, (x_start, y_start))
        y_start += line_height

        # List ingredients
        for item_id, required_qty in recipe.ingredients.items():
            item = self.items_db.get(item_id)
            item_name = item.name if item else item_id
            have_qty = self.player.inventory.get_quantity(item_id)

            # Color based on availability
            if have_qty >= required_qty:
                color = Colors.TEXT_SUCCESS  # Green - have enough
            elif have_qty > 0:
                color = Colors.HP_MID  # Yellow - have some
            else:
                color = Colors.TEXT_ERROR  # Red - have none

            ing_text = f"  {item_name}: {have_qty}/{required_qty}"
            ing_surface = small_font.render(ing_text, True, color)
            surface.blit(ing_surface, (x_start, y_start))
            y_start += line_height

        # Result
        y_start += 10
        result_item = self.items_db.get(recipe.result_item_id)
        result_name = result_item.name if result_item else recipe.result_item_id
        result_text = f"Creates: {result_name}"
        if recipe.result_quantity > 1:
            result_text += f" x{recipe.result_quantity}"
        result_surface = small_font.render(result_text, True, Colors.TEXT_INFO)
        surface.blit(result_surface, (x_start, y_start))

    def _draw_result_message(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        """Draw the crafting result message overlay."""
        if not self.result_message:
            return

        x = (surface.get_width() - 400) // 2
        y = 200
        box_width = 400
        box_height = 60

        # Use the shared gold-bordered message box style for the result text
        from .ui import MessageBox  # Local import to avoid circular dependencies

        temp_box = MessageBox(position=(x, y), width=box_width, height=box_height)
        # Pass font so wrapping is calculated correctly up front
        temp_box.set_text(self.result_message, font)
        temp_box.draw(surface, font, panel=self.panel)

    def _draw_help_text(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        """Draw standardized help text at the bottom of the screen."""
        mode_labels = {
            self.MODE_CATEGORY: "Up/Down: Select Category  |  Enter: Confirm  |  ESC: Close",
            self.MODE_RECIPE_LIST: "Up/Down: Select Recipe  |  Enter: View Details  |  ESC: Back",
            self.MODE_RECIPE_DETAIL: "Up/Down: Select Action  |  Enter: Craft  |  ESC: Back"
        }
        help_text = mode_labels.get(self.mode, "Up/Down: Navigate  |  Enter: Confirm  |  ESC: Back")

        draw_contextual_help(surface, help_text, font, margin_bottom=Layout.SCREEN_MARGIN)

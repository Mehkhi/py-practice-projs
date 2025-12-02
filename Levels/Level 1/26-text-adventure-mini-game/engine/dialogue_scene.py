"""Dialogue scene for narrative choices."""

import os
from typing import Optional, Dict, List, Set, TYPE_CHECKING

import pygame

from .base_menu_scene import BaseMenuScene
from .assets import AssetManager
from .ui import Menu, MessageBox
from .theme import Colors, Fonts, Layout
from core.dialogue import DialogueChoice, DialogueNode, DialogueTree, load_dialogue_from_json
from core.world import World
from core.logging_utils import log_warning, log_info
from core.tutorial_system import TipTrigger

if TYPE_CHECKING:
    from .scene import SceneManager
    from core.entities import Player, PartyMember


class DialogueScene(BaseMenuScene):
    """Presents a dialogue node with choices and optional flag setting."""

    def __init__(
        self,
        manager: Optional["SceneManager"],
        dialogue_id: str,
        world: Optional[World] = None,
        scale: int = 2,
        tree: Optional[DialogueTree] = None,
        assets: Optional[AssetManager] = None,
        player: Optional["Player"] = None,
    ):
        super().__init__(manager, assets, scale)
        self.world = world
        self.dialogue_id = dialogue_id
        self.player = player

        self.tree = tree or self._load_tree()
        self.current_node: Optional[DialogueNode] = self.tree.get_node(dialogue_id) if self.tree else None
        self._visited_nodes: Set[str] = set()
        self._previous_npc_interaction_state = self.world.npc_interaction_active if self.world else False
        if self.world:
            self.world.npc_interaction_active = True

        # Position message box at bottom
        self.message_box = MessageBox(
            position=(Layout.PADDING_LARGE, 320),
            width=Layout.SCREEN_WIDTH - Layout.PADDING_LARGE * 2,
            height=140
        )
        self.choice_menu: Optional[Menu] = None

        # Queued notifications to show after dialogue closes
        self._pending_notifications: List[str] = []

        self._apply_node_effects(self.current_node)
        self._refresh_ui()

    def _load_tree(self) -> Optional[DialogueTree]:
        """Load dialogue tree from data file."""
        path = os.path.join("data", "dialogue.json")
        if not os.path.exists(path):
            return None
        try:
            return load_dialogue_from_json(path)
        except Exception as e:
            log_warning(f"Failed to load dialogue from {path}: {e}")
            return None

    def _refresh_ui(self) -> None:
        """Update message box and choices based on current node."""
        if not self.current_node:
            return

        # Pass font to ensure proper wrapping
        font = self.assets.get_font(Fonts.DEFAULT, Fonts.SIZE_BODY)
        self.message_box.set_text(self.current_node.text, font)

        portrait_surface = None
        portrait_width = 0
        if self.current_node.portrait_id:
            portrait_surface = self.assets.get_image(self.current_node.portrait_id, (32, 32))
            if portrait_surface:
                portrait_width = portrait_surface.get_width()
        self.message_box.set_portrait(portrait_surface)

        choice_texts = [c.text for c in self.current_node.choices]
        if choice_texts:
            # Position menu ABOVE the message box to avoid any overlap with text
            # Calculate required height for the menu
            menu_line_height = Layout.MENU_ITEM_HEIGHT
            menu_height = len(choice_texts) * menu_line_height + Layout.PADDING_MD * 2

            # Align with the text start position (accounting for portrait)
            menu_x = self.message_box.position[0] + Layout.PADDING_LARGE
            if portrait_width > 0:
                menu_x += portrait_width + Layout.MESSAGE_BOX_PORTRAIT_GAP

            # Position bottom of menu 10px above message box
            menu_y = self.message_box.position[1] - menu_height - 10

            # Ensure it doesn't go off screen top
            menu_y = max(Layout.PADDING_LARGE, menu_y)

            self.choice_menu = Menu(
                choice_texts,
                position=(menu_x, menu_y)
            )
        else:
            self.choice_menu = None

    def _apply_node_effects(self, node: Optional[DialogueNode]) -> None:
        """Apply one-time effects when entering a node (recipes, etc.)."""
        if not node or node.id in self._visited_nodes:
            return
        self._visited_nodes.add(node.id)

        if node.discover_recipes and self.player:
            try:
                from core.crafting import CraftingSystem, discover_recipes_for_player

                crafting_system = getattr(self, "crafting_system", None)
                if not crafting_system:
                    crafting_system = CraftingSystem()
                    self.crafting_system = crafting_system
                newly_discovered = discover_recipes_for_player(self.player, node.discover_recipes)
                if newly_discovered:
                    recipe_names: List[str] = []
                    for recipe_id in newly_discovered:
                        recipe = crafting_system.get_recipe(recipe_id)
                        recipe_names.append(recipe.name if recipe else recipe_id)

                    if len(recipe_names) == 1:
                        self._pending_notifications.append(f"Recipe discovered: {recipe_names[0]}")
                    else:
                        recipes_text = ", ".join(recipe_names[:-1]) + f", and {recipe_names[-1]}"
                        self._pending_notifications.append(f"Recipes discovered: {recipes_text}")
            except Exception as exc:
                log_warning(f"Failed to grant recipes for dialogue node '{node.id}': {exc}")
        elif node.discover_recipes:
            log_warning("discover_recipes provided but no player available to learn them")

    def _apply_choice_effects(self, choice: DialogueChoice) -> None:
        """Apply effects tied to a chosen option."""
        if self.world and choice.set_flag:
            self.world.set_flag(choice.set_flag, True)

            if choice.set_flag.endswith("_recruited"):
                tutorial_manager = self.get_manager_attr("tutorial_manager", "_apply_choice_effects")
                if tutorial_manager:
                    tutorial_manager.trigger_tip(TipTrigger.FIRST_PARTY_MEMBER)

        if self.world and self.current_node and self.current_node.set_flags_after_choice:
            for flag in self.current_node.set_flags_after_choice:
                self.world.set_flag(flag, True)

    def _select_choice(self) -> None:
        """Handle confirming the current menu choice."""
        if not self.choice_menu or not self.current_node or not self.current_node.choices:
            self._close_dialogue()
            return

        index = max(0, min(self.choice_menu.selected_index, len(self.current_node.choices) - 1))
        choice = self.current_node.choices[index]
        self._apply_choice_effects(choice)

        next_id = choice.next_id
        if next_id and self.tree:
            next_node = self.tree.get_node(next_id)
            if next_node:
                self.current_node = next_node
                self._apply_node_effects(self.current_node)
                self._refresh_ui()
                return
            log_warning(f"Dialogue node '{next_id}' not found for dialogue '{self.dialogue_id}'")

        self._close_dialogue()

    def _close_dialogue(self) -> None:
        """Clean up state and return to the previous scene."""
        if self.world:
            self.world.npc_interaction_active = self._previous_npc_interaction_state

        if self._pending_notifications:
            for note in self._pending_notifications:
                log_info(note)
            self._pending_notifications.clear()

        if self.manager:
            self.manager.pop()

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return

        if not self.current_node:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
                self._close_dialogue()
            return

        if self.choice_menu:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.choice_menu.move_selection(-1)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.choice_menu.move_selection(1)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._select_choice()
            elif event.key == pygame.K_ESCAPE:
                self._close_dialogue()
        else:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
                self._close_dialogue()

    def update(self, dt: float) -> None:
        """Update dialogue state (currently no timers needed)."""
        # Placeholder for future animations or typing effects
        return

    def draw(self, surface: pygame.Surface) -> None:
        # Draw semi-transparent dark background
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill(Colors.BG_OVERLAY)
        surface.blit(overlay, (0, 0))

        if self.current_node and self.current_node.speaker:
            name_font = self.assets.get_font(Fonts.DEFAULT, Fonts.SIZE_SUBHEADING)
            if name_font:
                name_text = self.current_node.speaker
                name_surface = name_font.render(name_text, True, Colors.ACCENT)

                name_x = self.message_box.position[0]
                name_y = self.message_box.position[1] - 36

                # Draw name tag background
                name_padding_x = 12
                name_padding_y = 6
                name_bg_rect = pygame.Rect(
                    name_x,
                    name_y,
                    name_surface.get_width() + name_padding_x * 2,
                    name_surface.get_height() + name_padding_y * 2
                )

                # Background
                pygame.draw.rect(surface, Colors.BG_PANEL, name_bg_rect, border_radius=Layout.CORNER_RADIUS_SMALL)
                # Border
                pygame.draw.rect(surface, Colors.ACCENT, name_bg_rect, 1, border_radius=Layout.CORNER_RADIUS_SMALL)

                # Text centered in tag
                surface.blit(name_surface, (name_x + name_padding_x, name_y + name_padding_y))

        self.message_box.draw(surface, self.assets.get_font(Fonts.DEFAULT, Fonts.SIZE_BODY), panel=self.panel)

        if self.choice_menu:
            # Draw a background panel for the menu
            # We need to calculate the rect for the menu background
            menu_rect = pygame.Rect(
                self.choice_menu.position[0] - Layout.PADDING_MD,
                self.choice_menu.position[1] - Layout.PADDING_SM,
                400, # Arbitrary max width or calculate based on longest text
                len(self.choice_menu.options) * Layout.MENU_ITEM_HEIGHT + Layout.PADDING_SM * 2
            )

            # Adjust width based on longest option
            font = self.assets.get_font(Fonts.DEFAULT, Fonts.SIZE_SUBHEADING)
            if font:
                max_w = 0
                for opt in self.choice_menu.options:
                    max_w = max(max_w, font.size(opt)[0])
                menu_rect.width = max_w + Layout.PADDING_MD * 2 + 40 # Extra for cursor

            # Draw menu background
            pygame.draw.rect(surface, Colors.BG_PANEL, menu_rect, border_radius=Layout.CORNER_RADIUS)
            pygame.draw.rect(surface, Colors.BORDER, menu_rect, Layout.BORDER_WIDTH, border_radius=Layout.CORNER_RADIUS)

            self.choice_menu.draw(
                surface,
                self.assets.get_font(Fonts.DEFAULT, Fonts.SIZE_BODY),
                theme={
                    "active": Colors.TEXT_HIGHLIGHT,
                    "inactive": Colors.TEXT_SECONDARY,
                    "disabled": Colors.TEXT_DISABLED
                }
            )

        # Draw help text at bottom
        self._draw_help_text(surface, self.assets.get_font(Fonts.SMALL, Fonts.SIZE_SMALL))

    def _draw_help_text(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        """Draw standardized help text at the bottom of the screen."""
        if not font:
            return

        width, height = surface.get_size()

        if self.choice_menu:
            help_text = "↑/↓: Select Choice  •  Enter/Space: Confirm"
        else:
            help_text = "Enter/Space/ESC: Continue"

        # Draw subtle background for help text
        help_surface = font.render(help_text, True, Colors.TEXT_SECONDARY)
        help_rect = help_surface.get_rect(center=(width // 2, height - Layout.SCREEN_MARGIN))

        bg_rect = help_rect.inflate(Layout.PADDING_MD * 2, Layout.PADDING_SM)
        pygame.draw.rect(surface, Colors.BG_DARK, bg_rect, border_radius=Layout.CORNER_RADIUS_SMALL)

        surface.blit(help_surface, help_rect)

"""Dialogue scene for narrative choices."""

import copy
import os
from typing import Optional, Dict, List, TYPE_CHECKING

import pygame

from .base_menu_scene import BaseMenuScene
from .assets import AssetManager
from .ui import Menu, MessageBox, NineSlicePanel
from .theme import Colors, Fonts, Layout
from core.dialogue import load_dialogue_from_json, DialogueNode, DialogueTree
from core.world import World
from core.logging_utils import log_warning, log_info
from core.gambling import GamblingGameType
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

        # Position message box at bottom
        self.message_box = MessageBox(
            position=(Layout.PADDING_LARGE, 320),
            width=Layout.SCREEN_WIDTH - Layout.PADDING_LARGE * 2,
            height=140
        )
        self.choice_menu: Optional[Menu] = None

        # Queued notifications to show after dialogue closes
        self._pending_notifications: List[str] = []

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

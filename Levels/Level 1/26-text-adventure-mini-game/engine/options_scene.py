"""Options menu scene for game settings."""

import math
import pygame
from typing import Optional, Dict, Any, TYPE_CHECKING

from .base_menu_scene import BaseMenuScene
from .assets import AssetManager
from .ui import Menu, NineSlicePanel, draw_contextual_help
from .input_manager import get_input_manager, get_key_name, BINDABLE_KEYS
from .accessibility import get_accessibility_manager
from .theme import Colors, Layout
from .options import (
    OptionsAudioVideoMixin,
    OptionsControlsMixin,
    OptionsAccessibilityMixin,
)

if TYPE_CHECKING:
    from .scene import SceneManager


class OptionsScene(
    OptionsAudioVideoMixin,
    OptionsControlsMixin,
    OptionsAccessibilityMixin,
    BaseMenuScene,
):
    """Options menu for adjusting game settings."""

    def __init__(
        self,
        manager: Optional["SceneManager"],
        scale: int = 2,
        assets: Optional[AssetManager] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(manager, assets, scale)
        self.config = config or {}

        # Options state (with defaults from config or sensible defaults)
        # Get tips_enabled from tutorial_manager if available, otherwise from config
        tutorial_manager = getattr(manager, "tutorial_manager", None) if manager else None
        tips_enabled_default = (
            tutorial_manager.tips_enabled
            if tutorial_manager
            else self.config.get("tips_enabled", True)
        )
        self.options_state = {
            "master_volume": self.config.get("master_volume", 80),
            "music_volume": self.config.get("music_volume", 70),
            "sfx_volume": self.config.get("sfx_volume", 80),
            "display_scale": self.config.get("scale", 2),
            "minimap_enabled": self.config.get("minimap_enabled", True),
            "debug_ai": self.config.get("debug_ai", False),
            "tips_enabled": tips_enabled_default,
        }

        # Input manager for control remapping
        self.input_manager = get_input_manager()

        # Accessibility manager
        self.accessibility_manager = get_accessibility_manager()

        # Menu options
        self.menu_options = [
            "Master Volume",
            "Music Volume",
            "SFX Volume",
            "Display Scale",
            "Minimap",
            "Debug AI",
            "Show Tips",
            "Controls",
            "Accessibility",
            "Back",
        ]

        self.menu = Menu(
            self.menu_options,
            position=(0, 0),  # Will be positioned dynamically
        )

        # Animation state
        self.title_timer = 0.0
        self.fade_in = 0.0

        # Editing state
        self.editing_value = False

        # Control remapping state
        self.in_controls_submenu = False
        self.controls_menu_index = 0
        self.waiting_for_key = False
        self.rebinding_action: Optional[str] = None
        self.rebind_flash_timer = 0.0

        # Accessibility submenu state
        self.in_accessibility_submenu = False
        self.accessibility_menu_index = 0

        # Pre-render surfaces
        self._gradient_surface: Optional[pygame.Surface] = None

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle input events."""
        if event.type != pygame.KEYDOWN:
            return

        # Handle key rebinding mode
        if self.waiting_for_key:
            self._handle_rebind_key(event)
            return

        # Handle controls submenu
        if self.in_controls_submenu:
            self._handle_controls_menu_event(event)
            return

        # Handle accessibility submenu
        if self.in_accessibility_submenu:
            self._handle_accessibility_menu_event(event)
            return

        # Main options menu
        selected = self.menu.get_selected()

        if event.key == pygame.K_ESCAPE:
            self._go_back()
        elif event.key == pygame.K_UP:
            self.menu.move_selection(-1)
        elif event.key == pygame.K_DOWN:
            self.menu.move_selection(1)
        elif event.key == pygame.K_RETURN:
            if selected == "Back":
                self._go_back()
            elif selected == "Controls":
                self._enter_controls_submenu()
            elif selected == "Accessibility":
                self._enter_accessibility_submenu()
            elif selected in ("Minimap", "Debug AI", "Show Tips"):
                self._toggle_option(selected)
        elif event.key in (pygame.K_LEFT, pygame.K_RIGHT):
            self._adjust_value(selected, event.key == pygame.K_RIGHT)

    def _enter_controls_submenu(self) -> None:
        """Enter the controls remapping submenu."""
        self.in_controls_submenu = True
        self.controls_menu_index = 0

    def _enter_accessibility_submenu(self) -> None:
        """Enter the accessibility settings submenu."""
        self.in_accessibility_submenu = True
        self.accessibility_menu_index = 0

    def _handle_accessibility_menu_event(self, event: pygame.event.Event) -> None:
        """Handle events in the accessibility submenu."""
        # Menu items: Text Size, Colorblind Mode, Back
        num_items = 3

        if event.key == pygame.K_ESCAPE:
            self.in_accessibility_submenu = False
            self.accessibility_manager.save_settings()
        elif event.key == pygame.K_UP:
            self.accessibility_menu_index = (self.accessibility_menu_index - 1) % num_items
        elif event.key == pygame.K_DOWN:
            self.accessibility_menu_index = (self.accessibility_menu_index + 1) % num_items
        elif event.key in (pygame.K_LEFT, pygame.K_RIGHT):
            forward = event.key == pygame.K_RIGHT
            if self.accessibility_menu_index == 0:
                # Text Size
                self.accessibility_manager.cycle_text_size(forward)
            elif self.accessibility_menu_index == 1:
                # Colorblind Mode
                self.accessibility_manager.cycle_colorblind_mode(forward)
        elif event.key == pygame.K_RETURN:
            if self.accessibility_menu_index == 2:
                # Back
                self.in_accessibility_submenu = False
                self.accessibility_manager.save_settings()

    def _handle_controls_menu_event(self, event: pygame.event.Event) -> None:
        """Handle events in the controls submenu."""
        actions = self.input_manager.get_all_actions()
        num_items = len(actions) + 2  # actions + Reset Defaults + Back

        if event.key == pygame.K_ESCAPE:
            self.in_controls_submenu = False
            self.input_manager.save_bindings()
        elif event.key == pygame.K_UP:
            self.controls_menu_index = (self.controls_menu_index - 1) % num_items
        elif event.key == pygame.K_DOWN:
            self.controls_menu_index = (self.controls_menu_index + 1) % num_items
        elif event.key == pygame.K_RETURN:
            if self.controls_menu_index < len(actions):
                # Start rebinding this action
                self.rebinding_action = actions[self.controls_menu_index]
                self.waiting_for_key = True
                self.rebind_flash_timer = 0.0
            elif self.controls_menu_index == len(actions):
                # Reset Defaults
                self.input_manager.reset_to_defaults()
            else:
                # Back
                self.in_controls_submenu = False
                self.input_manager.save_bindings()

    def _handle_rebind_key(self, event: pygame.event.Event) -> None:
        """Handle key press while waiting for rebind."""
        if event.key == pygame.K_ESCAPE:
            # Cancel rebinding
            self.waiting_for_key = False
            self.rebinding_action = None
            return

        if event.key in BINDABLE_KEYS and self.rebinding_action:
            # Rebind the action
            self.input_manager.rebind_action(self.rebinding_action, event.key)
            self.waiting_for_key = False
            self.rebinding_action = None

    def _toggle_option(self, option: str) -> None:
        """Toggle a boolean option."""
        if option == "Minimap":
            self.options_state["minimap_enabled"] = not self.options_state["minimap_enabled"]
        elif option == "Debug AI":
            self.options_state["debug_ai"] = not self.options_state["debug_ai"]
        elif option == "Show Tips":
            self.options_state["tips_enabled"] = not self.options_state["tips_enabled"]
            # Update tutorial_manager if available
            if self.manager and self.manager.tutorial_manager:
                self.manager.tutorial_manager.tips_enabled = self.options_state["tips_enabled"]

    def _go_back(self) -> None:
        """Return to previous scene, applying settings."""
        # Update config with new values
        self.config.update({
            "master_volume": self.options_state["master_volume"],
            "music_volume": self.options_state["music_volume"],
            "sfx_volume": self.options_state["sfx_volume"],
            "scale": self.options_state["display_scale"],
            "minimap_enabled": self.options_state["minimap_enabled"],
            "debug_ai": self.options_state["debug_ai"],
            "tips_enabled": self.options_state["tips_enabled"],
        })
        # Update tutorial_manager if available
        if self.manager and self.manager.tutorial_manager:
            self.manager.tutorial_manager.tips_enabled = self.options_state["tips_enabled"]
        self.manager.pop()

    def update(self, dt: float) -> None:
        """Update scene state."""
        self.title_timer += dt
        if self.fade_in < 1.0:
            self.fade_in = min(1.0, self.fade_in + dt * 2.0)

        # Update rebind flash timer
        if self.waiting_for_key:
            self.rebind_flash_timer += dt

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the options menu."""
        width, height = surface.get_size()
        center_x = width // 2

        # Draw gradient background
        self._draw_gradient_background(surface)

        if self.in_controls_submenu:
            # Draw controls submenu
            self._draw_title(surface, center_x, 40, "CONTROLS")
            self._draw_controls_panel(surface, center_x, 80)
            self._draw_help_text(surface, center_x, height - 40, "controls")
        elif self.in_accessibility_submenu:
            # Draw accessibility submenu
            self._draw_title(surface, center_x, 40, "ACCESSIBILITY")
            self._draw_accessibility_panel(surface, center_x, 80)
            self._draw_help_text(surface, center_x, height - 40, "accessibility")
        else:
            # Draw main options menu
            self._draw_title(surface, center_x, 60)
            self._draw_options_panel(surface, center_x, 120)
            self._draw_help_text(surface, center_x, height - 40, "main")

    def _draw_gradient_background(self, surface: pygame.Surface) -> None:
        """Draw a smooth vertical gradient background."""
        width, height = surface.get_size()

        if self._gradient_surface is None or self._gradient_surface.get_size() != (width, height):
            self._gradient_surface = pygame.Surface((width, height))
            top = Colors.BG_DARK
            bottom = Colors.BG_PANEL
            for y in range(height):
                ratio = y / height
                ratio = ratio * ratio * (3 - 2 * ratio)  # Smoothstep
                r = int(top[0] + (bottom[0] - top[0]) * ratio)
                g = int(top[1] + (bottom[1] - top[1]) * ratio)
                b = int(top[2] + (bottom[2] - top[2]) * ratio)
                pygame.draw.line(self._gradient_surface, (r, g, b), (0, y), (width, y))

        surface.blit(self._gradient_surface, (0, 0))

    def _draw_title(self, surface: pygame.Surface, center_x: int, y: int, title_text: str = "OPTIONS") -> None:
        """Draw the options title."""
        font_large = self.assets.get_font("large", 36) or pygame.font.Font(None, 36)

        # Title with shadow
        shadow = font_large.render(title_text, True, Colors.BG_DARK)
        shadow_rect = shadow.get_rect(center=(center_x + 2, y + 2))
        surface.blit(shadow, shadow_rect)

        title = font_large.render(title_text, True, Colors.ACCENT_BRIGHT)
        title_rect = title.get_rect(center=(center_x, y))
        surface.blit(title, title_rect)

        # Decorative line
        line_y = y + 25
        half_width = 80
        for i in range(half_width):
            alpha_ratio = 1.0 - (i / half_width)
            color = (
                int(Colors.ACCENT[0] * alpha_ratio * 0.5),
                int(Colors.ACCENT[1] * alpha_ratio * 0.5),
                int(Colors.ACCENT[2] * alpha_ratio * 0.5),
            )
            pygame.draw.line(surface, color, (center_x - i, line_y), (center_x - i - 1, line_y))
            pygame.draw.line(surface, color, (center_x + i, line_y), (center_x + i + 1, line_y))

    def _draw_options_panel(self, surface: pygame.Surface, center_x: int, start_y: int) -> None:
        """Draw the options list with values."""
        font = self.assets.get_font("default", 22) or pygame.font.Font(None, 22)
        font_small = self.assets.get_font("small", 18) or pygame.font.Font(None, 18)

        panel_width = 400
        panel_height = 280
        panel_x = center_x - panel_width // 2
        panel_y = start_y

        # Draw panel background
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        bg_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(bg_surface, (*Colors.BG_PANEL, int(Layout.OVERLAY_ALPHA * self.fade_in)),
                        (0, 0, panel_width, panel_height), border_radius=Layout.CORNER_RADIUS)
        pygame.draw.rect(bg_surface, (*Colors.BORDER_FOCUS, int(150 * self.fade_in)),
                        (0, 0, panel_width, panel_height), width=Layout.BORDER_WIDTH, border_radius=Layout.CORNER_RADIUS)
        surface.blit(bg_surface, panel_rect.topleft)

        # Draw each option
        line_height = 36
        option_x = panel_x + 30
        value_x = panel_x + panel_width - 150

        for i, option in enumerate(self.menu_options):
            is_selected = i == self.menu.selected_index
            option_y = panel_y + 20 + i * line_height

            # Highlight for selected item
            if is_selected:
                highlight_rect = pygame.Rect(panel_x + 10, option_y - 4, panel_width - 20, line_height - 4)
                highlight_surf = pygame.Surface((highlight_rect.width, highlight_rect.height), pygame.SRCALPHA)
                pygame.draw.rect(highlight_surf, (*Colors.BORDER, int(180 * self.fade_in)),
                               (0, 0, highlight_rect.width, highlight_rect.height), border_radius=Layout.CORNER_RADIUS_SMALL)
                surface.blit(highlight_surf, highlight_rect.topleft)

                # Cursor
                cursor_offset = 3 * math.sin(self.title_timer * 5)
                cursor_x = option_x - 15 + cursor_offset
                arrow_points = [
                    (cursor_x, option_y + 4),
                    (cursor_x + 8, option_y + 10),
                    (cursor_x, option_y + 16),
                ]
                pygame.draw.polygon(surface, Colors.ACCENT, arrow_points)

            # Option label
            color = Colors.TEXT_PRIMARY if is_selected else Colors.TEXT_SECONDARY
            label = font.render(option, True, color)
            surface.blit(label, (option_x, option_y))

            # Option value
            if option == "Back":
                continue

            value_str = self._get_value_display(option)
            if option in ("Master Volume", "Music Volume", "SFX Volume"):
                # Draw slider
                self._draw_slider(surface, value_x, option_y + 2, 100, 16,
                                 self._get_volume_value(option), is_selected)
            elif option == "Display Scale":
                value_text = font.render(value_str, True, color)
                surface.blit(value_text, (value_x + 30, option_y))
            else:
                # Boolean toggle
                value_text = font.render(value_str, True,
                                        Colors.TEXT_SUCCESS if "ON" in value_str else Colors.TEXT_ERROR)
                surface.blit(value_text, (value_x + 30, option_y))

        # Draw hint for adjusting values
        hint_y = panel_y + panel_height - 30
        hint = font_small.render("← → to adjust values", True, Colors.TEXT_SECONDARY)
        hint_rect = hint.get_rect(center=(center_x, hint_y))
        surface.blit(hint, hint_rect)

    def _draw_help_text(self, surface: pygame.Surface, center_x: int, y: int, mode: str = "main") -> None:
        """Draw footer with controls hint using consistent styling."""
        font_small = self.assets.get_font("small", 16) or pygame.font.Font(None, 16)

        if mode == "controls":
            if self.waiting_for_key:
                hint = "Press any key to bind  |  Esc to cancel"
                text_color = Colors.ACCENT
            else:
                hint = "Up/Down Navigate  |  Enter to rebind  |  Esc Back"
                text_color = Colors.TEXT_SECONDARY
        elif mode == "accessibility":
            hint = "Up/Down Navigate  |  Left/Right Adjust  |  Esc Back"
            text_color = Colors.TEXT_SECONDARY
        else:  # main
            hint = "Up/Down Navigate  |  Left/Right Adjust  |  Enter Toggle  |  Esc Back"
            text_color = Colors.TEXT_SECONDARY

        draw_contextual_help(surface, hint, font_small, margin_bottom=y, text_color=text_color)

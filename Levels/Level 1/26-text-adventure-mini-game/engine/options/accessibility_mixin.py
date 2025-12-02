"""Accessibility submenu mixin for the options scene."""

import math
import pygame

from ..theme import Colors, Layout


class OptionsAccessibilityMixin:
    """Mixin providing accessibility options logic and UI rendering."""

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

    def _draw_accessibility_panel(
        self, surface: pygame.Surface, center_x: int, start_y: int
    ) -> None:
        """Draw the accessibility settings panel."""
        font = self.assets.get_font("default", 22) or pygame.font.Font(None, 22)
        font_small = self.assets.get_font("small", 18) or pygame.font.Font(None, 18)

        panel_width = 420
        panel_height = 200
        panel_x = center_x - panel_width // 2
        panel_y = start_y

        # Draw panel background
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        bg_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(
            bg_surface,
            (*Colors.BG_PANEL, int(Layout.OVERLAY_ALPHA * self.fade_in)),
            (0, 0, panel_width, panel_height),
            border_radius=Layout.CORNER_RADIUS,
        )
        pygame.draw.rect(
            bg_surface,
            (*Colors.BORDER_FOCUS, int(150 * self.fade_in)),
            (0, 0, panel_width, panel_height),
            width=Layout.BORDER_WIDTH,
            border_radius=Layout.CORNER_RADIUS,
        )
        surface.blit(bg_surface, panel_rect.topleft)

        # Menu items
        menu_items = [
            ("Text Size", self.accessibility_manager.get_text_size_name()),
            ("Color Mode", self.accessibility_manager.get_colorblind_mode_name()),
            ("Back", ""),
        ]

        line_height = 40
        option_x = panel_x + 30
        value_x = panel_x + panel_width - 180

        for i, (label, value) in enumerate(menu_items):
            is_selected = i == self.accessibility_menu_index
            option_y = panel_y + 25 + i * line_height

            # Highlight for selected item
            if is_selected:
                highlight_rect = pygame.Rect(
                    panel_x + 10, option_y - 4, panel_width - 20, line_height - 8
                )
                highlight_surf = pygame.Surface(
                    (highlight_rect.width, highlight_rect.height), pygame.SRCALPHA
                )
                pygame.draw.rect(
                    highlight_surf,
                    (*Colors.BORDER, int(180 * self.fade_in)),
                    (0, 0, highlight_rect.width, highlight_rect.height),
                    border_radius=Layout.CORNER_RADIUS_SMALL,
                )
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
            label_surface = font.render(label, True, color)
            surface.blit(label_surface, (option_x, option_y))

            # Option value (if not Back)
            if value:
                # Draw value in a styled box
                value_color = Colors.ACCENT if is_selected else Colors.TEXT_SECONDARY
                value_surface = font.render(value, True, value_color)
                value_rect = value_surface.get_rect(midleft=(value_x, option_y + 10))

                # Draw box around value
                box_rect = pygame.Rect(
                    value_rect.left - 10,
                    value_rect.top - 4,
                    value_rect.width + 20,
                    value_rect.height + 8,
                )
                pygame.draw.rect(
                    surface,
                    Colors.BAR_BG,
                    box_rect,
                    border_radius=Layout.CORNER_RADIUS_SMALL,
                )
                pygame.draw.rect(
                    surface,
                    Colors.BORDER,
                    box_rect,
                    width=Layout.BORDER_WIDTH_THIN,
                    border_radius=Layout.CORNER_RADIUS_SMALL,
                )
                surface.blit(value_surface, value_rect)

                # Draw arrows for adjustable values
                if is_selected:
                    arrow_color = Colors.ACCENT
                    # Left arrow
                    left_arrow = font_small.render("<", True, arrow_color)
                    surface.blit(left_arrow, (box_rect.left - 18, option_y + 2))
                    # Right arrow
                    right_arrow = font_small.render(">", True, arrow_color)
                    surface.blit(right_arrow, (box_rect.right + 6, option_y + 2))

        # Draw preview section
        preview_y = panel_y + panel_height - 50
        preview_label = font_small.render("Preview:", True, Colors.TEXT_SECONDARY)
        surface.blit(preview_label, (panel_x + 20, preview_y))

        # Show sample text at current size
        sample_size = self.accessibility_manager.scale_font_size(18)
        sample_font = self.assets.get_font("default", sample_size) or pygame.font.Font(
            None, sample_size
        )
        sample_text = sample_font.render(
            "Sample Text - The quick brown fox", True, Colors.TEXT_PRIMARY
        )
        surface.blit(sample_text, (panel_x + 90, preview_y))

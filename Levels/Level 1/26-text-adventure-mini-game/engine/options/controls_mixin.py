"""Controls remapping mixin for the options scene."""

import math
import pygame

from ..theme import Colors, Layout


class OptionsControlsMixin:
    """Mixin providing control remapping logic and UI rendering."""

    def _enter_controls_submenu(self) -> None:
        """Enter the controls remapping submenu."""
        self.in_controls_submenu = True
        self.controls_menu_index = 0

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
        from ..input_manager import BINDABLE_KEYS

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

    def _draw_controls_panel(self, surface: pygame.Surface, center_x: int, start_y: int) -> None:
        """Draw the controls remapping panel."""
        font = self.assets.get_font("default", 20) or pygame.font.Font(None, 20)
        font_small = self.assets.get_font("small", 16) or pygame.font.Font(None, 16)

        panel_width = 420
        panel_height = 340
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

        # Get all actions
        actions = self.input_manager.get_all_actions()
        line_height = 28
        option_x = panel_x + 30
        key_x = panel_x + panel_width - 120

        # Draw each action binding
        for i, action in enumerate(actions):
            is_selected = i == self.controls_menu_index
            option_y = panel_y + 15 + i * line_height

            # Highlight for selected item
            if is_selected:
                highlight_rect = pygame.Rect(
                    panel_x + 10, option_y - 2, panel_width - 20, line_height - 4
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
                    (cursor_x, option_y + 2),
                    (cursor_x + 8, option_y + 8),
                    (cursor_x, option_y + 14),
                ]
                pygame.draw.polygon(surface, Colors.ACCENT, arrow_points)

            # Action name
            color = Colors.TEXT_PRIMARY if is_selected else Colors.TEXT_SECONDARY
            action_name = self.input_manager.get_action_name(action)
            label = font.render(action_name, True, color)
            surface.blit(label, (option_x, option_y))

            # Key binding
            if self.waiting_for_key and self.rebinding_action == action:
                # Flashing "Press a key..." text
                flash = int((math.sin(self.rebind_flash_timer * 8) + 1) * 127)
                key_color = (255, flash, flash)
                key_text = font.render("Press a key...", True, key_color)
            else:
                key_display = self.input_manager.get_binding_display(action)
                key_color = Colors.ACCENT if is_selected else Colors.TEXT_SECONDARY
                key_text = font.render(key_display, True, key_color)

            # Draw key in a box
            key_rect = key_text.get_rect(midleft=(key_x, option_y + 10))
            box_rect = pygame.Rect(
                key_rect.left - 8,
                key_rect.top - 4,
                key_rect.width + 16,
                key_rect.height + 8,
            )
            pygame.draw.rect(surface, Colors.BAR_BG, box_rect, border_radius=Layout.CORNER_RADIUS_SMALL)
            pygame.draw.rect(
                surface,
                Colors.BORDER,
                box_rect,
                width=Layout.BORDER_WIDTH_THIN,
                border_radius=Layout.CORNER_RADIUS_SMALL,
            )
            surface.blit(key_text, key_rect)

        # Draw Reset Defaults option
        reset_idx = len(actions)
        is_reset_selected = self.controls_menu_index == reset_idx
        reset_y = panel_y + 15 + reset_idx * line_height + 10

        if is_reset_selected:
            highlight_rect = pygame.Rect(
                panel_x + 10, reset_y - 2, panel_width - 20, line_height - 4
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

            cursor_offset = 3 * math.sin(self.title_timer * 5)
            cursor_x = option_x - 15 + cursor_offset
            arrow_points = [
                (cursor_x, reset_y + 2),
                (cursor_x + 8, reset_y + 8),
                (cursor_x, reset_y + 14),
            ]
            pygame.draw.polygon(surface, Colors.ACCENT, arrow_points)

        reset_color = Colors.HP_MID if is_reset_selected else Colors.ACCENT_DIM
        reset_text = font.render("Reset to Defaults", True, reset_color)
        surface.blit(reset_text, (option_x, reset_y))

        # Draw Back option
        back_idx = len(actions) + 1
        is_back_selected = self.controls_menu_index == back_idx
        back_y = panel_y + 15 + back_idx * line_height + 10

        if is_back_selected:
            highlight_rect = pygame.Rect(
                panel_x + 10, back_y - 2, panel_width - 20, line_height - 4
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

            cursor_offset = 3 * math.sin(self.title_timer * 5)
            cursor_x = option_x - 15 + cursor_offset
            arrow_points = [
                (cursor_x, back_y + 2),
                (cursor_x + 8, back_y + 8),
                (cursor_x, back_y + 14),
            ]
            pygame.draw.polygon(surface, Colors.ACCENT, arrow_points)

        back_color = Colors.TEXT_PRIMARY if is_back_selected else Colors.TEXT_SECONDARY
        back_text = font.render("Back", True, back_color)
        surface.blit(back_text, (option_x, back_y))

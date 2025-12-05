"""Confirmation dialog component."""

from typing import Callable, Optional

import pygame

from ..theme import Colors, Fonts, Layout, PANEL_OVERLAY, PanelStyle
from .nine_slice import NineSlicePanel
from .utils import draw_themed_panel


class ConfirmationDialog:
    """Modal confirmation dialog for important actions."""

    def __init__(
        self,
        message: str,
        on_confirm: Optional[Callable[[], None]] = None,
        on_cancel: Optional[Callable[[], None]] = None,
        title: str = "Confirm",
        confirm_text: str = "Yes",
        cancel_text: str = "No",
        width: int = 320,
        height: int = 160,
        panel: Optional[NineSlicePanel] = None,
        style: Optional[PanelStyle] = None,
    ):
        self.message = message
        self.on_confirm = on_confirm
        self.on_cancel = on_cancel
        self.title = title
        self.confirm_text = confirm_text
        self.cancel_text = cancel_text
        self.width = width
        self.height = height

        # State
        self.visible = False
        self.selected_index = 1  # Default to "No"
        self.result: Optional[bool] = None
        self.overlay_alpha = 180
        # Optional gold-bordered panel for the dialog background
        self.panel = panel
        self.style = style or PANEL_OVERLAY

    def show(self) -> None:
        self.visible = True
        self.result = None
        self.selected_index = 1

    def hide(self) -> None:
        self.visible = False

    def handle_event(self, event: pygame.event.Event) -> Optional[bool]:
        if not self.visible:
            return None

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                self.selected_index = 1 - self.selected_index
            elif event.key == pygame.K_RETURN:
                self.result = self.selected_index == 0
                self.visible = False
                if self.result and self.on_confirm:
                    self.on_confirm()
                elif not self.result and self.on_cancel:
                    self.on_cancel()
                return self.result
            elif event.key == pygame.K_ESCAPE:
                self.result = False
                self.visible = False
                if self.on_cancel:
                    self.on_cancel()
                return False

        return None

    def draw(self, surface: pygame.Surface, font: Optional[pygame.font.Font] = None) -> None:
        if not self.visible:
            return

        if font is None:
            font = pygame.font.Font(None, Fonts.SIZE_BODY)

        screen_w, screen_h = surface.get_size()
        padding = Layout.DIALOG_PADDING

        # Draw overlay
        overlay = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
        overlay.fill(Colors.BG_OVERLAY)
        surface.blit(overlay, (0, 0))

        # Calculate dialog position (centered)
        dialog_x = (screen_w - self.width) // 2
        dialog_y = (screen_h - self.height) // 2

        # Draw dialog background with shadow
        shadow_offset = 4
        shadow_rect = pygame.Rect(dialog_x + shadow_offset, dialog_y + shadow_offset, self.width, self.height)
        pygame.draw.rect(surface, (0, 0, 0, 100), shadow_rect, border_radius=Layout.CORNER_RADIUS)

        dialog_rect = pygame.Rect(dialog_x, dialog_y, self.width, self.height)
        draw_themed_panel(surface, dialog_rect, self.style, self.panel)

        # Draw title
        title_surface = font.render(self.title, True, Colors.ACCENT)
        title_x = dialog_x + (self.width - title_surface.get_width()) // 2
        surface.blit(title_surface, (title_x, dialog_y + padding))

        # Draw message with proper word wrapping and centering
        message_y = dialog_y + padding + font.get_linesize() + Layout.ELEMENT_GAP_LARGE
        lines = self.message.split('\n')
        for line in lines:
            line_surf = font.render(line, True, Colors.TEXT_PRIMARY)
            line_x = dialog_x + (self.width - line_surf.get_width()) // 2
            surface.blit(line_surf, (line_x, message_y))
            message_y += font.get_linesize() + Layout.ELEMENT_GAP_SMALL

        # Draw buttons with improved styling
        btn_y = dialog_y + self.height - padding - Layout.DIALOG_BUTTON_HEIGHT
        btn_width = Layout.DIALOG_BUTTON_MIN_WIDTH
        btn_spacing = Layout.DIALOG_BUTTON_GAP
        total_btn_width = btn_width * 2 + btn_spacing
        start_x = dialog_x + (self.width - total_btn_width) // 2

        # Yes button
        yes_rect = pygame.Rect(start_x, btn_y, btn_width, Layout.DIALOG_BUTTON_HEIGHT)
        yes_selected = self.selected_index == 0
        yes_bg_color = Colors.ACCENT if yes_selected else Colors.BG_DARK
        yes_text_color = Colors.BG_DARK if yes_selected else Colors.TEXT_PRIMARY
        pygame.draw.rect(surface, yes_bg_color, yes_rect, border_radius=Layout.CORNER_RADIUS_SMALL)
        pygame.draw.rect(surface, Colors.ACCENT if yes_selected else Colors.BORDER, yes_rect,
                        Layout.BORDER_WIDTH, border_radius=Layout.CORNER_RADIUS_SMALL)
        yes_surf = font.render(self.confirm_text, True, yes_text_color)
        surface.blit(yes_surf, (yes_rect.centerx - yes_surf.get_width()//2,
                                yes_rect.centery - yes_surf.get_height()//2))

        # No button
        no_rect = pygame.Rect(start_x + btn_width + btn_spacing, btn_y, btn_width, Layout.DIALOG_BUTTON_HEIGHT)
        no_selected = self.selected_index == 1
        no_bg_color = Colors.ACCENT if no_selected else Colors.BG_DARK
        no_text_color = Colors.BG_DARK if no_selected else Colors.TEXT_PRIMARY
        pygame.draw.rect(surface, no_bg_color, no_rect, border_radius=Layout.CORNER_RADIUS_SMALL)
        pygame.draw.rect(surface, Colors.ACCENT if no_selected else Colors.BORDER, no_rect,
                        Layout.BORDER_WIDTH, border_radius=Layout.CORNER_RADIUS_SMALL)
        no_surf = font.render(self.cancel_text, True, no_text_color)
        surface.blit(no_surf, (no_rect.centerx - no_surf.get_width()//2,
                               no_rect.centery - no_surf.get_height()//2))

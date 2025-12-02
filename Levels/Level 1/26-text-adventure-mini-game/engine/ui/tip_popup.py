"""Tip popup UI component for displaying contextual tutorial tips."""

from typing import Optional, Tuple, TYPE_CHECKING

import pygame

from ..theme import Colors, Fonts, Layout

if TYPE_CHECKING:
    from core.tutorial_system import TutorialTip


class TipPopup:
    """
    Non-blocking popup for contextual tips.
    Appears at top or bottom of screen, doesn't pause game.
    """

    def __init__(self, theme: Optional[dict] = None) -> None:
        """
        Initialize the tip popup.

        Args:
            theme: Optional theme dict (for future extensibility)
        """
        self.theme = theme
        self.current_tip: Optional["TutorialTip"] = None
        self.visible = False
        self.show_timer = 0.0
        self.fade_alpha = 0
        self.show_duration = 8.0  # Seconds before auto-hide
        self.fade_duration = 0.3  # Seconds for fade in/out
        self.position = "top"  # "top" or "bottom"
        self._fade_state = "in"  # "in", "out", or "none"

    def show_tip(self, tip: "TutorialTip", position: Optional[str] = None) -> None:
        """
        Display a tip popup.

        Args:
            tip: TutorialTip to display
            position: Optional position override ("top" or "bottom")
        """
        self.current_tip = tip
        self.visible = True
        self.show_timer = 0.0
        self.fade_alpha = 0
        self._fade_state = "in"
        if position:
            self.position = position
        else:
            # Default positioning based on context
            # This can be set via set_context() if needed
            self.position = "top"

    def set_position(self, position: str) -> None:
        """
        Set the popup position.

        Args:
            position: "top" or "bottom"
        """
        if position in ("top", "bottom"):
            self.position = position

    def hide(self) -> None:
        """Hide the current tip with fade-out."""
        if self.visible:
            self._fade_state = "out"
            # Don't set visible=False yet, wait for fade-out to complete

    def handle_event(self, event: pygame.event.Event) -> Tuple[bool, bool]:
        """
        Handle input. Returns (consumed, permanently_dismissed).

        - ENTER/SPACE: Dismiss tip
        - D: Dismiss permanently (don't show again)
        - ESC: Dismiss

        Returns:
            Tuple of (event_consumed, permanently_dismissed)
        """
        if not self.visible:
            return False, False

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.hide()
                return True, False
            elif event.key == pygame.K_d:
                self.hide()
                return True, True
            elif event.key == pygame.K_ESCAPE:
                self.hide()
                return True, False

        return False, False

    def update(self, dt: float) -> None:
        """Update timer and fade animations."""
        if not self.visible:
            return

        # Update auto-hide timer first so a long dt still hides the tip
        if self._fade_state != "out":
            self.show_timer += dt
            if self.show_timer >= self.show_duration:
                self.hide()

        # Update fade animation
        if self._fade_state == "in":
            self.fade_alpha += (255.0 / self.fade_duration) * dt
            if self.fade_alpha >= 255:
                self.fade_alpha = 255
                self._fade_state = "none"
        elif self._fade_state == "out":
            self.fade_alpha -= (255.0 / self.fade_duration) * dt
            if self.fade_alpha <= 0:
                self.fade_alpha = 0
                self.visible = False
                self.current_tip = None
                self._fade_state = "none"

    def _wrap_text(self, text: str, font: pygame.font.Font, max_width: int) -> list:
        """Wrap text to fit within max_width."""
        if not text:
            return []

        words = text.split()
        lines = []
        current_line = []

        for word in words:
            test_line = " ".join(current_line + [word])
            if font.size(test_line)[0] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]

        if current_line:
            lines.append(" ".join(current_line))

        return lines

    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw the tip popup:
        1. Rounded rectangle background
        2. Title in bold
        3. Content text (word-wrapped)
        4. "[ENTER] OK  [D] Don't show again" footer
        """
        if not self.visible or not self.current_tip:
            return

        screen_width = surface.get_width()
        screen_height = surface.get_height()

        # Load fonts
        title_font = pygame.font.Font(None, Fonts.SIZE_SUBHEADING)
        content_font = pygame.font.Font(None, Fonts.SIZE_BODY)
        footer_font = pygame.font.Font(None, Fonts.SIZE_SMALL)

        # Calculate popup dimensions
        popup_width = min(Layout.TOOLTIP_MAX_WIDTH * 2, screen_width - (Layout.SCREEN_MARGIN * 2))
        popup_padding = Layout.PADDING_LG
        content_width = popup_width - (popup_padding * 2)

        # Wrap content text
        wrapped_content = self._wrap_text(self.current_tip.content, content_font, content_width)

        # Calculate popup height
        title_height = title_font.get_height()
        content_height = sum(content_font.get_linesize() for _ in wrapped_content) + (Layout.ELEMENT_GAP_SMALL * (len(wrapped_content) - 1))
        footer_height = footer_font.get_height()
        popup_height = (
            popup_padding * 2 +
            title_height +
            Layout.SECTION_GAP_SMALL +
            content_height +
            Layout.SECTION_GAP_SMALL +
            footer_height
        )

        # Position popup
        popup_x = (screen_width - popup_width) // 2
        if self.position == "top":
            popup_y = Layout.SCREEN_MARGIN
        else:
            popup_y = screen_height - popup_height - Layout.SCREEN_MARGIN

        # Create popup surface with alpha
        popup_surface = pygame.Surface((popup_width, popup_height), pygame.SRCALPHA)

        # Draw background with border
        popup_rect = pygame.Rect(0, 0, popup_width, popup_height)
        bg_color = (*Colors.BG_PANEL, int(self.fade_alpha))
        border_color = (*Colors.BORDER_HIGHLIGHT, int(self.fade_alpha))
        pygame.draw.rect(popup_surface, bg_color, popup_rect, border_radius=Layout.CORNER_RADIUS)
        pygame.draw.rect(popup_surface, border_color, popup_rect, Layout.BORDER_WIDTH, border_radius=Layout.CORNER_RADIUS)

        # Draw title
        title_surface = title_font.render(self.current_tip.title, True, Colors.TEXT_HIGHLIGHT)
        title_surface.set_alpha(int(self.fade_alpha))
        title_x = popup_padding
        title_y = popup_padding
        popup_surface.blit(title_surface, (title_x, title_y))

        # Draw content
        content_y = title_y + title_height + Layout.SECTION_GAP_SMALL
        line_height = content_font.get_linesize()
        for i, line in enumerate(wrapped_content):
            line_surface = content_font.render(line, True, Colors.TEXT_PRIMARY)
            line_surface.set_alpha(int(self.fade_alpha))
            popup_surface.blit(line_surface, (popup_padding, content_y + (i * (line_height + Layout.ELEMENT_GAP_SMALL))))

        # Draw footer
        footer_text = "[ENTER] OK  [D] Don't show again"
        footer_surface = footer_font.render(footer_text, True, Colors.TEXT_SECONDARY)
        footer_surface.set_alpha(int(self.fade_alpha))
        footer_x = (popup_width - footer_surface.get_width()) // 2
        footer_y = popup_height - footer_height - popup_padding
        popup_surface.blit(footer_surface, (footer_x, footer_y))

        # Blit to main surface
        surface.blit(popup_surface, (popup_x, popup_y))

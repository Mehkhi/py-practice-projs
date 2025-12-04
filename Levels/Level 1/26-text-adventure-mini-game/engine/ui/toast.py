"""Toast notification component."""

from typing import Optional

import pygame

from ..theme import Colors, Fonts, Layout


class ToastNotification:
    """A temporary notification message that fades out."""

    def __init__(
        self,
        message: str,
        duration: float = 2.0,
        position: str = "top-center",  # "top-center", "bottom-right", "center"
    ):
        self.message = message
        self.duration = duration
        self.position = position
        self.timer = duration
        self.active = True
        self.alpha = 255

    def update(self, dt: float) -> None:
        """Update the toast timer and fade effect."""
        if not self.active:
            return

        self.timer -= dt

        # Start fading in the last 0.5 seconds
        if self.timer < 0.5:
            self.alpha = max(0, int(255 * (self.timer / 0.5)))

        if self.timer <= 0:
            self.active = False

    def draw(self, surface: pygame.Surface, font: Optional[pygame.font.Font] = None) -> None:
        """Draw the toast notification."""
        if not self.active or self.alpha <= 0:
            return

        if font is None:
            font = pygame.font.Font(None, Fonts.SIZE_BODY)

        screen_w, screen_h = surface.get_size()
        padding_h = 12
        padding_v = 8

        # Render text
        text_surface = font.render(self.message, True, Colors.TEXT_PRIMARY)
        text_w, text_h = text_surface.get_size()

        # Calculate toast dimensions
        toast_w = text_w + padding_h * 2
        toast_h = text_h + padding_v * 2

        # Calculate position
        if self.position == "top-center":
            x = (screen_w - toast_w) // 2
            y = 20
        elif self.position == "bottom-right":
            x = screen_w - toast_w - 20
            y = screen_h - toast_h - 20
        else:  # center
            x = (screen_w - toast_w) // 2
            y = (screen_h - toast_h) // 2

        # Create semi-transparent surface for the toast
        toast_surface = pygame.Surface((toast_w, toast_h), pygame.SRCALPHA)

        # Background
        bg_color = (*Colors.BG_PANEL[:3], int(self.alpha * 0.9))
        pygame.draw.rect(toast_surface, bg_color, (0, 0, toast_w, toast_h),
                        border_radius=Layout.CORNER_RADIUS_SMALL)

        # Border
        border_color = (*Colors.ACCENT[:3], self.alpha)
        pygame.draw.rect(toast_surface, border_color, (0, 0, toast_w, toast_h),
                        2, border_radius=Layout.CORNER_RADIUS_SMALL)

        # Text with alpha
        text_with_alpha = text_surface.copy()
        text_with_alpha.set_alpha(self.alpha)
        toast_surface.blit(text_with_alpha, (padding_h, padding_v))

        surface.blit(toast_surface, (x, y))

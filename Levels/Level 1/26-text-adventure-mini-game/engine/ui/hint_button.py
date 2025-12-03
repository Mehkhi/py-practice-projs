"""Hint button UI component for context-sensitive help access."""

import math
from typing import Optional, Tuple, Any, TYPE_CHECKING

import pygame

from ..theme import Colors, Fonts, Layout
from .animation_utils import sine_wave, sine_wave_01

if TYPE_CHECKING:
    from core.tutorial_system import TutorialManager


class HintButton:
    """
    Persistent hint button in corner of screen.
    When clicked, shows context-relevant help or opens help overlay.
    """

    def __init__(
        self,
        tutorial_manager: "TutorialManager",
        theme: Optional[dict] = None,
        assets: Optional[Any] = None,
    ) -> None:
        """
        Initialize the hint button.

        Args:
            tutorial_manager: TutorialManager instance
            theme: Optional theme dict (for future extensibility)
            assets: Optional AssetManager for loading sprite
        """
        self.tutorial_manager = tutorial_manager
        self.theme = theme
        self.assets = assets
        self.position = (10, 10)  # Top-left by default
        self.size = (32, 32)
        self.hovered = False
        self.pulse_timer = 0.0  # Subtle pulse animation
        self.context = "world"  # Current context for context-sensitive help
        self._icon_surface: Optional[pygame.Surface] = None
        self._load_icon()

    def _load_icon(self) -> None:
        """Load the hint button icon (sprite or fallback to text)."""
        # Try to load sprite from assets
        if self.assets:
            try:
                # Try common sprite names
                for sprite_name in ["hint_button", "help_icon", "question_mark"]:
                    try:
                        sprite = self.assets.get_image(sprite_name, self.size)
                        if sprite:
                            self._icon_surface = sprite
                            return
                    except (AttributeError, KeyError, Exception):
                        continue
            except Exception:
                pass

        # Fallback: Create text-based icon
        font = pygame.font.Font(None, Fonts.SIZE_HEADING)
        self._icon_surface = font.render("?", True, Colors.TEXT_HIGHLIGHT)

    def set_context(self, context: str) -> None:
        """
        Set current context for context-sensitive help.

        Contexts: "world", "battle", "shop", "inventory", "dialogue"
        """
        self.context = context

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle mouse input.

        - Click: Show context help or open overlay

        Returns:
            True if event was consumed
        """
        if event.type == pygame.MOUSEMOTION:
            # Check if mouse is over button
            mx, my = event.pos
            bx, by = self.position
            bw, bh = self.size
            self.hovered = (bx <= mx <= bx + bw and by <= my <= by + bh)
            return False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mx, my = event.pos
                bx, by = self.position
                bw, bh = self.size
                if bx <= mx <= bx + bw and by <= my <= by + bh:
                    # Button clicked - this will be handled by the scene
                    # Return True to indicate click was on button
                    return True
        return False

    def update(self, dt: float) -> None:
        """Update hover state and pulse animation."""
        # Update pulse animation (only when tips are available)
        has_pending_tips = bool(self.tutorial_manager.pending_tips)
        if has_pending_tips:
            # Advance timer using shared helper to keep behavior consistent
            self.pulse_timer = self.pulse_timer + dt * 2.0
        else:
            self.pulse_timer = 0.0

    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw the hint button:
        1. Circular button with icon
        2. Subtle pulse when new tips available
        3. Tooltip on hover: "Press H for Help"
        """
        bx, by = self.position
        bw, bh = self.size

        # Calculate pulse effect
        has_pending_tips = bool(self.tutorial_manager.pending_tips)
        pulse_scale = 1.0
        pulse_alpha = 255
        if has_pending_tips:
            # 10% size variation and alpha pulse using shared sine helpers
            wave = sine_wave(self.pulse_timer)
            wave_01 = sine_wave_01(self.pulse_timer)
            pulse_scale = 1.0 + (wave * 0.1)
            pulse_alpha = 200 + int(55 * wave_01)

        # Draw button background (circular) with gradient-like look
        center_x = bx + bw // 2
        center_y = by + bh // 2
        radius = int((min(bw, bh) // 2) * pulse_scale)

        # Button background - slightly darker/richer
        button_color = Colors.BG_PANEL if not self.hovered else Colors.BG_MAIN
        pygame.draw.circle(surface, button_color, (center_x, center_y), radius)

        # Inner glow/highlight
        pygame.draw.circle(surface, Colors.BG_DARK, (center_x, center_y), radius - 2, 1)

        # Outer border - thicker and accent colored
        border_color = Colors.BORDER_HIGHLIGHT if self.hovered else Colors.BORDER
        pygame.draw.circle(surface, border_color, (center_x, center_y), radius, 2)
        pygame.draw.circle(surface, border_color, (center_x, center_y), radius - 1, 1)

        # Draw icon
        if self._icon_surface:
            icon_w = int(self._icon_surface.get_width() * pulse_scale)
            icon_h = int(self._icon_surface.get_height() * pulse_scale)
            icon_scaled = pygame.transform.scale(self._icon_surface, (icon_w, icon_h))
            icon_scaled.set_alpha(pulse_alpha)
            icon_x = center_x - icon_w // 2
            icon_y = center_y - icon_h // 2
            surface.blit(icon_scaled, (icon_x, icon_y))

        # Draw tooltip on hover
        if self.hovered:
            tooltip_text = "Press H for Help"
            tooltip_font = pygame.font.Font(None, Fonts.SIZE_SMALL)
            tooltip_surface = tooltip_font.render(tooltip_text, True, Colors.TEXT_PRIMARY)
            tooltip_width = tooltip_surface.get_width() + (Layout.TOOLTIP_PADDING * 2)
            tooltip_height = tooltip_surface.get_height() + (Layout.TOOLTIP_PADDING * 2)

            # Position tooltip relative to button, keeping it on screen
            # Default: Above button, centered horizontally
            tooltip_x = center_x - tooltip_width // 2
            tooltip_y = by - tooltip_height - Layout.TOOLTIP_OFFSET

            # Check right edge - ensure it doesn't go off screen
            screen_w = surface.get_width()
            if tooltip_x + tooltip_width > screen_w - Layout.SCREEN_MARGIN:
                tooltip_x = screen_w - tooltip_width - Layout.SCREEN_MARGIN

            # Check left edge
            if tooltip_x < Layout.SCREEN_MARGIN:
                tooltip_x = Layout.SCREEN_MARGIN

            # Draw tooltip background with shadow
            tooltip_rect = pygame.Rect(tooltip_x, tooltip_y, tooltip_width, tooltip_height)

            # Shadow
            shadow_rect = tooltip_rect.copy()
            shadow_rect.move_ip(2, 2)
            pygame.draw.rect(surface, (0, 0, 0, 100), shadow_rect, border_radius=Layout.CORNER_RADIUS_SMALL)

            # Main body
            pygame.draw.rect(surface, Colors.BG_TOOLTIP, tooltip_rect, border_radius=Layout.CORNER_RADIUS_SMALL)
            pygame.draw.rect(surface, Colors.BORDER, tooltip_rect, Layout.BORDER_WIDTH_THIN, border_radius=Layout.CORNER_RADIUS_SMALL)

            # Draw tooltip text
            text_x = tooltip_x + Layout.TOOLTIP_PADDING
            text_y = tooltip_y + Layout.TOOLTIP_PADDING
            surface.blit(tooltip_surface, (text_x, text_y))

    def get_click_handler(self) -> Optional[str]:
        """
        Get the action to perform when button is clicked.

        Returns:
            "overlay" to open help overlay, or None if no action
        """
        # For now, always open overlay
        # Future: Could check for context-specific tips
        return "overlay"

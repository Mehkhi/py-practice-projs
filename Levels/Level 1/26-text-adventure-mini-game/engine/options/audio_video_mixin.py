"""Audio and video (display) options mixin for the options scene."""

import pygame

from ..theme import Colors, Layout


class OptionsAudioVideoMixin:
    """Mixin providing volume and display scale adjustment helpers."""

    def _adjust_value(self, option: str, increase: bool) -> None:
        """Adjust a numeric value."""
        delta = 5 if increase else -5

        if option == "Master Volume":
            self.options_state["master_volume"] = max(
                0, min(100, self.options_state["master_volume"] + delta)
            )
        elif option == "Music Volume":
            self.options_state["music_volume"] = max(
                0, min(100, self.options_state["music_volume"] + delta)
            )
        elif option == "SFX Volume":
            self.options_state["sfx_volume"] = max(
                0, min(100, self.options_state["sfx_volume"] + delta)
            )
        elif option == "Display Scale":
            scale_delta = 1 if increase else -1
            self.options_state["display_scale"] = max(
                1, min(4, self.options_state["display_scale"] + scale_delta)
            )

    def _get_value_display(self, option: str) -> str:
        """Get display string for an option value."""
        if option == "Master Volume":
            return f"{self.options_state['master_volume']}%"
        if option == "Music Volume":
            return f"{self.options_state['music_volume']}%"
        if option == "SFX Volume":
            return f"{self.options_state['sfx_volume']}%"
        if option == "Display Scale":
            return f"{self.options_state['display_scale']}x"
        if option == "Minimap":
            return "ON" if self.options_state["minimap_enabled"] else "OFF"
        if option == "Debug AI":
            return "ON" if self.options_state["debug_ai"] else "OFF"
        if option == "Show Tips":
            return "ON" if self.options_state.get("tips_enabled", True) else "OFF"
        return ""

    def _get_volume_value(self, option: str) -> int:
        """Get volume value for slider."""
        if option == "Master Volume":
            return self.options_state["master_volume"]
        if option == "Music Volume":
            return self.options_state["music_volume"]
        if option == "SFX Volume":
            return self.options_state["sfx_volume"]
        return 0

    def _draw_slider(
        self,
        surface: pygame.Surface,
        x: int,
        y: int,
        width: int,
        height: int,
        value: int,
        is_selected: bool,
    ) -> None:
        """Draw a volume slider."""
        # Background
        bg_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(surface, Colors.BAR_BG, bg_rect, border_radius=Layout.CORNER_RADIUS_SMALL)

        # Fill
        fill_width = int(width * value / 100)
        if fill_width > 0:
            fill_rect = pygame.Rect(x, y, fill_width, height)
            pygame.draw.rect(
                surface, Colors.SP_FILL, fill_rect, border_radius=Layout.CORNER_RADIUS_SMALL
            )

        # Handle
        handle_x = x + fill_width - 4
        handle_rect = pygame.Rect(max(x, handle_x), y - 2, 8, height + 4)
        handle_color = Colors.ACCENT if is_selected else Colors.TEXT_SECONDARY
        pygame.draw.rect(surface, handle_color, handle_rect, border_radius=2)

        # Border
        pygame.draw.rect(
            surface,
            Colors.BORDER_FOCUS,
            bg_rect,
            width=Layout.BORDER_WIDTH_THIN,
            border_radius=Layout.CORNER_RADIUS_SMALL,
        )

        # Value text
        font_small = self.assets.get_font("small", 14) or pygame.font.Font(None, 14)
        value_text = font_small.render(f"{value}%", True, Colors.TEXT_SECONDARY)
        surface.blit(value_text, (x + width + 8, y + 1))

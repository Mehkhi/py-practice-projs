"""Menu and tooltip UI components."""

import math
from typing import Dict, List, Optional, Sequence, Tuple

import pygame

from ..theme import Colors, Fonts, Layout


class Menu:
    """A menu with selectable options and polished visual styling."""

    def __init__(
        self,
        options: Sequence[str],
        position: Tuple[int, int] = (10, 10),
        disabled: Optional[Sequence[str]] = None,
        icons: Optional[Dict[str, pygame.Surface]] = None,
        compact: bool = False,
    ):
        self.options = list(options)
        self.selected_index = 0
        self.position = position
        self.disabled = set(disabled or [])
        self.icons = icons or {}
        self.compact = compact

        # Animation state
        self._anim_timer = 0.0
        self._selection_lerp = 0.0  # Smooth highlight transition

    def move_selection(self, delta: int) -> None:
        """Move selection up (negative) or down (positive)."""
        if not self.options:
            return
        self.selected_index = (self.selected_index + delta) % len(self.options)

    def get_selected(self) -> Optional[str]:
        """Get the currently selected option."""
        if not self.options:
            return None
        return self.options[self.selected_index]

    def draw(
        self,
        surface: pygame.Surface,
        font: Optional[pygame.font.Font] = None,
        cursor_surface: Optional[pygame.Surface] = None,
        theme: Optional[Dict[str, Tuple[int, int, int]]] = None,
        line_height: Optional[int] = None,
    ) -> None:
        """Draw the menu with improved spacing and visual hierarchy."""
        if font is None:
            font = pygame.font.Font(None, Fonts.SIZE_SUBHEADING)

        # Use appropriate line height based on compact mode
        if line_height is None:
            line_height = Layout.MENU_ITEM_HEIGHT_COMPACT if self.compact else Layout.MENU_ITEM_HEIGHT

        # Update animation
        self._anim_timer += 0.08

        colors = theme or {}
        color_active = colors.get("active", Colors.TEXT_HIGHLIGHT)
        color_inactive = colors.get("inactive", Colors.TEXT_SECONDARY)
        color_disabled = colors.get("disabled", Colors.TEXT_DISABLED)

        x, y = self.position
        cursor_width = Layout.MENU_CURSOR_WIDTH
        highlight_padding = Layout.MENU_HIGHLIGHT_PADDING

        for i, option in enumerate(self.options):
            is_selected = (i == self.selected_index)
            is_disabled = option in self.disabled

            color = color_disabled if is_disabled else (color_active if is_selected else color_inactive)

            # Calculate row position with proper vertical centering
            row_y = y + i * line_height

            # Draw selection highlight background
            if is_selected and not is_disabled:
                # Calculate text width for highlight
                text_width = font.size(option)[0]

                # Add padding for icon if present
                icon_padding = 0
                if option in self.icons:
                    icon_padding = self.icons[option].get_width() + Layout.ELEMENT_GAP

                # Create highlight rectangle with better padding
                highlight_x = x - cursor_width - highlight_padding
                highlight_width = text_width + cursor_width + icon_padding + (highlight_padding * 2)
                highlight_rect = pygame.Rect(
                    highlight_x,
                    row_y,
                    highlight_width,
                    line_height
                )

                # Draw rounded highlight background
                highlight_surface = pygame.Surface(
                    (highlight_rect.width, highlight_rect.height),
                    pygame.SRCALPHA
                )
                pygame.draw.rect(
                    highlight_surface,
                    (*Colors.ACCENT, 35),  # Subtle gold tint
                    (0, 0, highlight_rect.width, highlight_rect.height),
                    border_radius=Layout.CORNER_RADIUS_SMALL
                )
                # Add subtle border to highlight
                pygame.draw.rect(
                    highlight_surface,
                    (*Colors.ACCENT, 60),
                    (0, 0, highlight_rect.width, highlight_rect.height),
                    width=1,
                    border_radius=Layout.CORNER_RADIUS_SMALL
                )
                surface.blit(highlight_surface, highlight_rect)

                # Draw animated cursor with smooth motion
                cursor_bounce = math.sin(self._anim_timer * 2.5) * 3
                cursor_x = x - cursor_width + 4 + cursor_bounce
                cursor_center_y = row_y + line_height // 2

                if cursor_surface:
                    cursor_y = cursor_center_y - cursor_surface.get_height() // 2
                    surface.blit(cursor_surface, (int(cursor_x), cursor_y))
                else:
                    # Draw polished triangle cursor
                    cursor_size = 8
                    points = [
                        (cursor_x, cursor_center_y - cursor_size // 2),
                        (cursor_x + cursor_size, cursor_center_y),
                        (cursor_x, cursor_center_y + cursor_size // 2)
                    ]
                    pygame.draw.polygon(surface, Colors.ACCENT, points)
                    # Add subtle glow effect
                    glow_points = [
                        (cursor_x - 1, cursor_center_y - cursor_size // 2 - 1),
                        (cursor_x + cursor_size + 1, cursor_center_y),
                        (cursor_x - 1, cursor_center_y + cursor_size // 2 + 1)
                    ]
                    pygame.draw.polygon(surface, Colors.ACCENT_DIM, glow_points, width=1)

            # Render text with shadow for better readability
            text = font.render(option, True, color)
            text_height = text.get_height()
            text_y = row_y + (line_height - text_height) // 2

            # Calculate text x position
            text_x = x
            if option in self.icons:
                icon = self.icons[option]
                # Center icon vertically in row
                icon_y = row_y + (line_height - icon.get_height()) // 2
                surface.blit(icon, (x, icon_y))
                text_x += icon.get_width() + Layout.ELEMENT_GAP

            # Draw subtle text shadow for depth
            if is_selected and not is_disabled:
                shadow = font.render(option, True, Colors.BG_DARK)
                surface.blit(shadow, (text_x + 1, text_y + 1))

            surface.blit(text, (text_x, text_y))


class Tooltip:
    """Hover tooltip component for displaying item/skill information."""

    def __init__(
        self,
        max_width: int = Layout.TOOLTIP_MAX_WIDTH,
        padding: int = Layout.TOOLTIP_PADDING,
        bg_color: Tuple[int, int, int, int] = Colors.BG_TOOLTIP,
        border_color: Tuple[int, int, int] = Colors.BORDER,
        title_color: Tuple[int, int, int] = Colors.ACCENT,
        text_color: Tuple[int, int, int] = Colors.TEXT_PRIMARY,
        stat_positive_color: Optional[Tuple[int, int, int]] = None,
        stat_negative_color: Optional[Tuple[int, int, int]] = None,
    ):
        self.max_width = max_width
        self.padding = padding
        self.bg_color = bg_color
        self.border_color = border_color
        self.title_color = title_color
        self.text_color = text_color
        # Store explicit overrides; use None to indicate lazy evaluation
        self._stat_positive_color_override = stat_positive_color
        self._stat_negative_color_override = stat_negative_color

        # Current tooltip state
        self.visible = False
        self.title = ""
        self.description = ""
        self.stats: Dict[str, int] = {}
        self.extra_lines: List[Tuple[str, Tuple[int, int, int]]] = []
        self.position: Tuple[int, int] = (0, 0)

        # Hover delay
        self.hover_time = 0.0
        self.hover_delay = 0.3  # seconds before showing tooltip
        self._pending_show = False

    # Lazy color properties that re-evaluate accessibility colors on each access
    @property
    def stat_positive_color(self) -> Tuple[int, int, int]:
        """Get positive stat color, respecting current accessibility settings."""
        return self._stat_positive_color_override or Colors.get_accessibility_color("positive")

    @property
    def stat_negative_color(self) -> Tuple[int, int, int]:
        """Get negative stat color, respecting current accessibility settings."""
        return self._stat_negative_color_override or Colors.get_accessibility_color("negative")

    def show(
        self,
        title: str,
        description: str = "",
        stats: Optional[Dict[str, int]] = None,
        extra_lines: Optional[List[Tuple[str, Tuple[int, int, int]]]] = None,
        position: Optional[Tuple[int, int]] = None,
    ) -> None:
        self.title = title
        self.description = description
        self.stats = stats or {}
        self.extra_lines = extra_lines or []
        if position:
            self.position = position
        self._pending_show = True
        self.hover_time = 0.0

    def hide(self) -> None:
        self.visible = False
        self._pending_show = False
        self.hover_time = 0.0

    def update(self, dt: float, mouse_pos: Optional[Tuple[int, int]] = None) -> None:
        if self._pending_show:
            self.hover_time += dt
            if self.hover_time >= self.hover_delay:
                self.visible = True
                self._pending_show = False

        if mouse_pos and self.visible:
            self.position = mouse_pos

    def draw(self, surface: pygame.Surface, font: Optional[pygame.font.Font] = None) -> None:
        if not self.visible:
            return

        if font is None:
            font = pygame.font.Font(None, Fonts.SIZE_SMALL)

        # Calculate content dimensions
        line_height = font.get_linesize() + 2
        content_width = self.max_width - 2 * self.padding

        # Wrap description text
        wrapped_desc = self._wrap_text(self.description, font, content_width)

        # Calculate total height
        total_height = self.padding * 2
        total_height += line_height  # Title
        if wrapped_desc:
            total_height += len(wrapped_desc) * line_height + 4
        if self.stats:
            total_height += len(self.stats) * line_height + 4
        if self.extra_lines:
            total_height += len(self.extra_lines) * line_height + 4

        # Adjust position to stay on screen
        screen_w, screen_h = surface.get_size()
        x, y = self.position
        x = min(x + 15, screen_w - self.max_width - 5)
        y = min(y + 15, screen_h - total_height - 5)
        x = max(5, x)
        y = max(5, y)

        # Create tooltip surface
        tooltip_surface = pygame.Surface((self.max_width, total_height), pygame.SRCALPHA)
        tooltip_surface.fill(self.bg_color)
        pygame.draw.rect(tooltip_surface, self.border_color,
                        (0, 0, self.max_width, total_height), 2)

        # Draw content
        current_y = self.padding

        # Title
        title_surface = font.render(self.title, True, self.title_color)
        tooltip_surface.blit(title_surface, (self.padding, current_y))
        current_y += line_height + 4

        # Description
        if wrapped_desc:
            for line in wrapped_desc:
                line_surface = font.render(line, True, self.text_color)
                tooltip_surface.blit(line_surface, (self.padding, current_y))
                current_y += line_height
            current_y += 4

        # Stats
        if self.stats:
            for stat_name, value in self.stats.items():
                sign = "+" if value >= 0 else ""
                color = self.stat_positive_color if value >= 0 else self.stat_negative_color
                stat_text = f"{stat_name.title()}: {sign}{value}"
                stat_surface = font.render(stat_text, True, color)
                tooltip_surface.blit(stat_surface, (self.padding, current_y))
                current_y += line_height
            current_y += 4

        # Extra lines
        for text, color in self.extra_lines:
            extra_surface = font.render(text, True, color)
            tooltip_surface.blit(extra_surface, (self.padding, current_y))
            current_y += line_height

        # Blit to main surface
        surface.blit(tooltip_surface, (x, y))

    def _wrap_text(self, text: str, font: pygame.font.Font, max_width: int) -> List[str]:
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

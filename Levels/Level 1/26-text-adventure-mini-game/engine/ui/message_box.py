"""Message box component with text pagination and portrait support."""

from typing import List, Optional, Tuple

import pygame

from ..theme import Colors, Fonts, Layout
from .animation_utils import advance_timer
from .nine_slice import NineSlicePanel
from .utils import draw_rounded_panel


class MessageBox:
    """A text message box with optional portrait and improved styling."""

    def __init__(
        self,
        position: Tuple[int, int] = (10, 400),
        width: int = 620,
        height: int = 80,
        portrait_surface: Optional[pygame.Surface] = None,
    ):
        self.position = position
        self.width = width
        self.height = max(height, Layout.MESSAGE_BOX_MIN_HEIGHT)
        self.lines: List[str] = []
        self.text = ""
        self.portrait_surface = portrait_surface

        # Pagination state
        self.current_page = 0
        self.lines_per_page = 1  # Will be calculated in draw/set_text
        self.animation_timer = 0.0  # For blinking cursor
        self._last_font: Optional[pygame.font.Font] = None  # Track font for pagination calculations

        # Track wrapping parameters so we can re-wrap when font or layout changes
        self._wrap_font_id: Optional[int] = None
        self._wrap_width: Optional[int] = None

        # Animation update source tracking: when True, the timer has been
        # advanced via ``update(dt)`` instead of within ``draw``.
        self._animation_updated_externally: bool = False

    def set_text(self, text: str, font: Optional[pygame.font.Font] = None) -> None:
        """Set the message text with automatic wrapping.

        If a font is provided, text is wrapped immediately. Otherwise, wrapping
        will be performed the next time ``draw`` is called with a concrete
        font.
        """
        self.text = text
        self.current_page = 0
        self.lines = []
        self._wrap_font_id = None
        self._wrap_width = None

        if font is not None:
            # Store font for pagination calculations and wrap immediately
            self._last_font = font
            self._ensure_wrapped_lines(font)
            self.lines_per_page = self._calculate_lines_per_page(font)

    def advance(self) -> bool:
        """Advance to the next page of text.

        Returns True if advanced, False if already at the final page.
        """
        # Ensure we have a font to base pagination on
        if self._last_font is None:
            self._last_font = pygame.font.Font(None, Fonts.SIZE_BODY)

        # Ensure wrapping and pagination are up to date
        self._ensure_wrapped_lines(self._last_font)
        self.lines_per_page = self._calculate_lines_per_page(self._last_font)

        total_pages = max(1, (len(self.lines) + self.lines_per_page - 1) // self.lines_per_page)
        if self.current_page < total_pages - 1:
            self.current_page += 1
            return True
        return False

    def is_finished(self) -> bool:
        """Return True if the last page of text is currently being displayed."""
        if self._last_font is None:
            self._last_font = pygame.font.Font(None, Fonts.SIZE_BODY)

        # Ensure wrapping and pagination are up to date before checking
        self._ensure_wrapped_lines(self._last_font)
        self.lines_per_page = self._calculate_lines_per_page(self._last_font)

        total_pages = max(1, (len(self.lines) + self.lines_per_page - 1) // self.lines_per_page)
        return self.current_page >= total_pages - 1

    def update(self, dt: float) -> None:
        """Advance the message box animations using frame time ``dt``.

        This currently drives the "more" indicator blink. When this method
        is used, ``draw`` will not apply its own fixed-step timer.
        """
        self.animation_timer = advance_timer(self.animation_timer, dt, speed=2.0)
        self._animation_updated_externally = True

    def _wrap_text(self, text: str, font: pygame.font.Font, max_width: int) -> List[str]:
        """Wrap text to fit within max_width."""
        words = text.split()
        lines = []
        current_line = []

        for word in words:
            # Handle explicit newlines in the source text
            if '\n' in word:
                parts = word.split('\n')
                for i, part in enumerate(parts):
                    if i > 0:
                        lines.append(" ".join(current_line))
                        current_line = []
                    if part:
                        test_line = " ".join(current_line + [part])
                        if font.size(test_line)[0] <= max_width:
                            current_line.append(part)
                        else:
                            if current_line:
                                lines.append(" ".join(current_line))
                            current_line = [part]
                continue

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

    def _get_available_width(self, font: pygame.font.Font) -> int:
        """Calculate available text width based on current layout and portrait."""
        padding = Layout.MESSAGE_BOX_PADDING
        portrait_width = 0
        if self.portrait_surface:
            portrait_width = self.portrait_surface.get_width() + Layout.MESSAGE_BOX_PORTRAIT_GAP
        return self.width - (padding * 2) - portrait_width

    def _ensure_wrapped_lines(self, font: pygame.font.Font) -> None:
        """Ensure ``self.lines`` is wrapped for the given font and width.

        Re-wraps text when the font object or available width changes.
        """
        available_width = self._get_available_width(font)
        wrap_font_id = id(font)

        if self.lines and self._wrap_font_id == wrap_font_id and self._wrap_width == available_width:
            return

        if self.text:
            self.lines = self._wrap_text(self.text, font, available_width)
        else:
            self.lines = []

        self._wrap_font_id = wrap_font_id
        self._wrap_width = available_width

    def _calculate_lines_per_page(self, font: pygame.font.Font) -> int:
        """Calculate how many lines fit per page based on font metrics and available height.

        Args:
            font: The font to use for line height calculations

        Returns:
            Number of lines that fit on a page (at least 1)
        """
        padding = Layout.MESSAGE_BOX_PADDING
        line_height = font.get_linesize() + Layout.MESSAGE_BOX_LINE_GAP
        available_height = self.height - (padding * 2)
        return max(1, available_height // line_height)

    def set_portrait(self, surface: Optional[pygame.Surface]) -> None:
        """Assign a portrait surface to render alongside text."""
        self.portrait_surface = surface

    def draw(
        self,
        surface: pygame.Surface,
        font: Optional[pygame.font.Font] = None,
        panel: Optional[NineSlicePanel] = None,
    ) -> None:
        """Draw the message box with improved spacing and visuals."""
        if font is None:
            font = pygame.font.Font(None, Fonts.SIZE_BODY)

        # Store font for pagination and wrapping calculations
        self._last_font = font
        self._ensure_wrapped_lines(font)

        x, y = self.position
        padding = Layout.MESSAGE_BOX_PADDING
        bg_rect = pygame.Rect(x, y, self.width, self.height)

        # Draw shadow
        shadow_rect = bg_rect.copy()
        shadow_rect.move_ip(4, 4)
        pygame.draw.rect(surface, (0, 0, 0, 120), shadow_rect, border_radius=Layout.CORNER_RADIUS)

        if panel:
            panel.draw(surface, bg_rect)
        else:
            # Fallback style matching weather/time panel styling
            PANEL_BG = (20, 25, 40, 180)
            draw_rounded_panel(
                surface,
                bg_rect,
                PANEL_BG,
                Colors.BORDER,
                border_width=Layout.BORDER_WIDTH_THIN,
                radius=Layout.CORNER_RADIUS_SMALL
            )

        # Calculate text starting position
        text_x = x + padding
        content_top = y + padding

        if self.portrait_surface:
            # Draw portrait with fancy frame
            p_w = self.portrait_surface.get_width()
            p_h = self.portrait_surface.get_height()
            portrait_x = x + padding
            portrait_y = y + (self.height - p_h) // 2  # Vertically center portrait

            # Portrait frame background
            frame_rect = pygame.Rect(portrait_x - 3, portrait_y - 3, p_w + 6, p_h + 6)
            pygame.draw.rect(surface, Colors.BG_DARK, frame_rect, border_radius=4)

            # Portrait frame border
            pygame.draw.rect(surface, Colors.ACCENT, frame_rect, 1, border_radius=4)

            surface.blit(self.portrait_surface, (portrait_x, portrait_y))
            text_x = portrait_x + p_w + Layout.MESSAGE_BOX_PORTRAIT_GAP

        # Calculate available text area
        line_height = font.get_linesize() + Layout.MESSAGE_BOX_LINE_GAP

        # Calculate pagination using helper method
        self.lines_per_page = self._calculate_lines_per_page(font)

        start_idx = self.current_page * self.lines_per_page
        end_idx = min(start_idx + self.lines_per_page, len(self.lines))

        lines_to_draw = self.lines[start_idx:end_idx]

        # Vertically center text block if it's less than a full page
        total_text_height = len(lines_to_draw) * line_height - Layout.MESSAGE_BOX_LINE_GAP
        # Only center if we have fewer lines than fit on a page, to look nice
        if len(lines_to_draw) < self.lines_per_page:
            text_y = y + (self.height - total_text_height) // 2
        else:
            text_y = content_top

        # Ensure we don't start above the top padding
        text_y = max(text_y, content_top)

        for line in lines_to_draw:
            # Draw text shadow for depth
            shadow_surface = font.render(line, True, Colors.BLACK)
            surface.blit(shadow_surface, (text_x + Layout.TEXT_SHADOW_OFFSET, text_y + Layout.TEXT_SHADOW_OFFSET))

            # Draw main text
            text_surface = font.render(line, True, Colors.TEXT_PRIMARY)
            surface.blit(text_surface, (text_x, text_y))
            text_y += line_height

        # Draw "more" indicator if there are more pages
        if not self.is_finished():
            import math

            # When not driven externally, advance using a small fixed step
            # so existing scenes continue to animate without needing update(dt).
            if not self._animation_updated_externally:
                self.animation_timer += 0.1
            else:
                self._animation_updated_externally = False

            # Blinking effect
            if math.sin(self.animation_timer) > -0.5:
                indicator_x = x + self.width - padding - 12
                indicator_y = y + self.height - padding - 8

                # Draw a small down arrow/triangle
                pygame.draw.polygon(surface, Colors.ACCENT, [
                    (indicator_x, indicator_y),
                    (indicator_x + 10, indicator_y),
                    (indicator_x + 5, indicator_y + 6)
                ])

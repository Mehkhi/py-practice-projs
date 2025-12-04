"""Combat log component for battle action history."""

from typing import List, Optional, Tuple

import pygame

from ..theme import Colors, Fonts, Layout
from .nine_slice import NineSlicePanel
from .utils import draw_rounded_panel


class CombatLog:
    """
    Scrollable battle action history log.

    Features:
    - Maintains full battle message history (up to max_messages)
    - Toggle between collapsed (mini) and expanded view
    - Scroll through history with UP/DOWN when expanded
    - Auto-scrolls to newest message unless user has scrolled up
    """

    MAX_MESSAGES = 50  # Maximum messages to retain

    def __init__(
        self,
        position: Tuple[int, int] = (10, 400),
        width: int = 620,
        collapsed_height: int = 110,
        expanded_height: int = 280,
        max_visible_collapsed: int = 2,
        max_visible_expanded: int = 12,
    ):
        self.position = position
        self.width = width
        self.collapsed_height = collapsed_height
        self.expanded_height = expanded_height
        self.max_visible_collapsed = max_visible_collapsed
        self.max_visible_expanded = max_visible_expanded

        # Message history
        self.messages: List[str] = []

        # View state
        self.expanded = False
        self.scroll_offset = 0
        self.auto_scroll = True  # Auto-scroll to bottom when new messages arrive

    def add_message(self, message: str) -> None:
        """Add a message to the log. Strips special prefixes for display."""
        # Strip effect prefixes but keep the content
        display_msg = message
        for prefix in ["COMBO:", "TACTIC:", "PHASE:"]:
            if display_msg.startswith(prefix):
                display_msg = display_msg[len(prefix):].strip()
                break

        self.messages.append(display_msg)

        # Trim old messages
        if len(self.messages) > self.MAX_MESSAGES:
            self.messages = self.messages[-self.MAX_MESSAGES:]

        # Auto-scroll to bottom if enabled
        if self.auto_scroll:
            self._scroll_to_bottom()

    def add_messages(self, messages: List[str]) -> None:
        """Add multiple messages to the log."""
        for msg in messages:
            self.add_message(msg)

    def clear(self) -> None:
        """Clear all messages from the log."""
        self.messages.clear()
        self.scroll_offset = 0
        self.auto_scroll = True

    def toggle_expanded(self) -> None:
        """Toggle between expanded and collapsed view."""
        self.expanded = not self.expanded
        if self.expanded:
            # When expanding, scroll to show most recent messages
            self._scroll_to_bottom()

    def scroll_up(self) -> None:
        """Scroll up through message history."""
        if self.scroll_offset > 0:
            self.scroll_offset -= 1
            self.auto_scroll = False

    def scroll_down(self) -> None:
        """Scroll down through message history."""
        max_visible = self.max_visible_expanded if self.expanded else self.max_visible_collapsed
        max_scroll = max(0, len(self.messages) - max_visible)

        if self.scroll_offset < max_scroll:
            self.scroll_offset += 1
            # User-initiated scrolling disables auto-scroll until we reach
            # the bottom again.
            if self.scroll_offset < max_scroll:
                self.auto_scroll = False
            else:
                self.auto_scroll = True
        else:
            # Already at bottom; keep auto-scroll enabled so new messages are
            # followed automatically.
            self.auto_scroll = True

    def _scroll_to_bottom(self) -> None:
        """Scroll to show the most recent messages."""
        max_visible = self.max_visible_expanded if self.expanded else self.max_visible_collapsed
        self.scroll_offset = max(0, len(self.messages) - max_visible)

    def handle_event(self, event: "pygame.event.Event") -> bool:
        """
        Handle input events for the combat log.

        Returns True if the event was consumed.
        """
        if event.type != pygame.KEYDOWN:
            return False

        if event.key == pygame.K_TAB:
            self.toggle_expanded()
            return True

        if self.expanded:
            if event.key == pygame.K_UP:
                self.scroll_up()
                return True
            elif event.key == pygame.K_DOWN:
                self.scroll_down()
                return True

        return False

    def draw(
        self,
        surface: pygame.Surface,
        font: Optional[pygame.font.Font] = None,
        panel: Optional[NineSlicePanel] = None,
    ) -> None:
        """Draw the combat log."""
        if font is None:
            font = pygame.font.Font(None, Fonts.SIZE_BODY)

        x, y = self.position
        padding = Layout.MESSAGE_BOX_PADDING
        height = self.expanded_height if self.expanded else self.collapsed_height
        max_visible = self.max_visible_expanded if self.expanded else self.max_visible_collapsed

        # Background
        bg_rect = pygame.Rect(x, y, self.width, height)

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

        # Header (when expanded)
        text_x = x + padding
        text_y = y + padding
        line_height = font.get_linesize() + Layout.MESSAGE_BOX_LINE_GAP

        indicator_pos = None
        if self.expanded:
            # Draw header with scroll hints
            header_text = "Battle Log"
            header_surface = font.render(header_text, True, Colors.ACCENT)
            surface.blit(header_surface, (text_x, text_y))

            indicator_pos = (x + self.width - padding - 20, text_y)

            text_y += line_height + 4

            # Divider line
            pygame.draw.line(
                surface, Colors.BORDER,
                (text_x, text_y - 2), (x + self.width - padding, text_y - 2)
            )

        # Determine hint and reserve space so it never overlaps entries
        show_hint = self.expanded or len(self.messages) > max_visible
        hint_surface = None
        hint_height = 0
        hint_gap = Layout.ELEMENT_GAP_SMALL
        if show_hint:
            hint_text = "[TAB] Collapse | [UP/DOWN] Scroll" if self.expanded else f"[TAB] View full log ({len(self.messages)} messages)"
            hint_surface = font.render(hint_text, True, Colors.TEXT_DISABLED)
            hint_height = hint_surface.get_height()

        content_bottom = y + height - padding
        if show_hint:
            content_bottom -= hint_height + hint_gap

        available_height = content_bottom - text_y
        max_lines_fit = max(1, available_height // line_height)
        max_visible_for_draw = max(1, min(max_visible, max_lines_fit))
        max_scroll = max(0, len(self.messages) - max_visible_for_draw)
        if self.scroll_offset > max_scroll:
            self.scroll_offset = max_scroll

        if self.expanded and indicator_pos:
            indicator_x, indicator_y = indicator_pos
            can_scroll_up = self.scroll_offset > 0
            can_scroll_down = self.scroll_offset < max_scroll
            if can_scroll_up:
                up_arrow = font.render("^", True, Colors.TEXT_HIGHLIGHT)
                surface.blit(up_arrow, (indicator_x, indicator_y))
            if can_scroll_down:
                down_arrow = font.render("v", True, Colors.TEXT_HIGHLIGHT)
                surface.blit(down_arrow, (indicator_x + 10, indicator_y))

        # Get visible messages
        visible_messages = self.messages[self.scroll_offset:self.scroll_offset + max_visible_for_draw]

        # Draw messages
        for i, msg in enumerate(visible_messages):
            if text_y > content_bottom - font.get_linesize():
                break

            # Truncate long messages
            max_chars = int((self.width - padding * 2) / (font.size("M")[0] * 0.6))
            display_text = msg[:max_chars] + "..." if len(msg) > max_chars else msg

            # Shadow
            shadow_surface = font.render(display_text, True, Colors.BLACK)
            surface.blit(shadow_surface, (text_x + 1, text_y + 1))

            # Text (alternating slight color for readability)
            text_color = Colors.TEXT_PRIMARY if i % 2 == 0 else Colors.TEXT_SECONDARY
            text_surface = font.render(display_text, True, text_color)
            surface.blit(text_surface, (text_x, text_y))

            text_y += line_height

        # Toggle hint at bottom without colliding with messages
        if show_hint and hint_surface:
            hint_x = x + self.width - padding - hint_surface.get_width()
            hint_y = content_bottom + hint_gap
            surface.blit(hint_surface, (hint_x, hint_y))

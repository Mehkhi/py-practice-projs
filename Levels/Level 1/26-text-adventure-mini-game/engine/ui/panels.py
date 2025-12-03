"""Panel and dialog UI components."""

from typing import Callable, List, Optional, Tuple

import pygame

from ..theme import Colors, Fonts, Layout
from .animation_utils import advance_timer, sine_wave


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


class NineSlicePanel:
    """
    9-slice panel renderer for pixel-art UI framing.
    Can use a source image or fallback to procedural drawing.
    """

    def __init__(self, source: Optional[pygame.Surface] = None):
        self.source = source
        if source:
            w, h = source.get_size()
            self.cell_w = w // 3
            self.cell_h = h // 3
        else:
            self.cell_w = 8
            self.cell_h = 8

    def draw(self, surface: pygame.Surface, dest_rect: pygame.Rect) -> None:
        if not self.source:
            # Fallback procedural drawing with semi-transparent style
            panel_surface = pygame.Surface((dest_rect.width, dest_rect.height), pygame.SRCALPHA)
            bg_color = (*Colors.BG_PANEL[:3], 220)
            pygame.draw.rect(panel_surface, bg_color, (0, 0, dest_rect.width, dest_rect.height), border_radius=Layout.CORNER_RADIUS)

            # Inner bevel (darker)
            inner_rect = pygame.Rect(2, 2, dest_rect.width - 4, dest_rect.height - 4)
            inner_color = (*Colors.BG_DARK[:3], 200)
            pygame.draw.rect(panel_surface, inner_color, inner_rect, 1, border_radius=Layout.CORNER_RADIUS)

            # Outer border
            border_color = (*Colors.BORDER[:3], 220)
            pygame.draw.rect(panel_surface, border_color, (0, 0, dest_rect.width, dest_rect.height), Layout.BORDER_WIDTH, border_radius=Layout.CORNER_RADIUS)
            surface.blit(panel_surface, dest_rect.topleft)
            return

        sw, sh = self.cell_w, self.cell_h
        sx = [0, sw, sw * 2]
        sy = [0, sh, sh * 2]

        dx = [dest_rect.left, dest_rect.left + sw, dest_rect.right - sw]
        dy = [dest_rect.top, dest_rect.top + sh, dest_rect.bottom - sh]

        for j in range(3):
            for i in range(3):
                src = pygame.Rect(sx[i], sy[j], sw, sh)
                if i == 1:
                    dw = max(0, dest_rect.width - 2 * sw)
                else:
                    dw = sw
                if j == 1:
                    dh = max(0, dest_rect.height - 2 * sh)
                else:
                    dh = sh

                dst = pygame.Rect(dx[i], dy[j], dw, dh)
                if dw <= 0 or dh <= 0:
                    continue

                tile = pygame.transform.scale(self.source.subsurface(src), (int(dw), int(dh)))
                surface.blit(tile, dst)


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
            from engine.world.overworld_renderer import draw_rounded_panel
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
        if self.panel:
            # Use gold-bordered, textured panel if available
            self.panel.draw(surface, dialog_rect)
        else:
            # Fallback semi-transparent style
            dialog_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            bg_color = (*Colors.BG_PANEL[:3], 230)
            pygame.draw.rect(
                dialog_surface,
                bg_color,
                (0, 0, self.width, self.height),
                border_radius=Layout.CORNER_RADIUS,
            )
            border_color = (*Colors.BORDER_FOCUS[:3], 230)
            pygame.draw.rect(
                dialog_surface,
                border_color,
                (0, 0, self.width, self.height),
                Layout.BORDER_WIDTH,
                border_radius=Layout.CORNER_RADIUS,
            )
            surface.blit(dialog_surface, dialog_rect.topleft)

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
        panel: Optional["NineSlicePanel"] = None,
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
            from engine.world.overworld_renderer import draw_rounded_panel
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

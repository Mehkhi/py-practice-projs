"""Help overlay UI component for displaying help entries organized by category."""

from typing import Dict, List, Optional, Tuple, TYPE_CHECKING

import pygame

from ..theme import Colors, Fonts, Layout
from .text_utils import wrap_text

if TYPE_CHECKING:
    from core.tutorial_system import TutorialManager, HelpEntry


class HelpOverlay:
    """
    Full-screen help overlay showing all help entries organized by category.
    Toggleable via H key or menu option.
    """

    def __init__(self, tutorial_manager: "TutorialManager", theme: Optional[Dict] = None) -> None:
        """
        Initialize the help overlay.

        Args:
            tutorial_manager: TutorialManager instance for accessing help entries
            theme: Optional theme dict (for future extensibility)
        """
        self.tutorial_manager = tutorial_manager
        self.visible = False
        self.current_category_index = 0
        self.scroll_offset = 0
        self._categories: List[str] = []
        self._entries_by_category: Dict[str, List["HelpEntry"]] = {}
        self._refresh_categories()

    def _refresh_categories(self) -> None:
        """Refresh the list of categories from tutorial manager."""
        self._entries_by_category = self.tutorial_manager.get_help_entries_by_category()
        self._categories = sorted(self._entries_by_category.keys())
        # Reset to first category if current is invalid
        if self.current_category_index >= len(self._categories):
            self.current_category_index = 0
        # Reset scroll when category changes
        self.scroll_offset = 0

    def toggle(self) -> None:
        """Show/hide the overlay."""
        self.visible = not self.visible
        if self.visible:
            self._refresh_categories()
            self.scroll_offset = 0

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle input. Returns True if event was consumed.

        - ESC/H: Close overlay
        - LEFT/RIGHT: Switch category tabs
        - UP/DOWN: Scroll content
        - Mouse wheel: Scroll content
        """
        if not self.visible:
            return False

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_h):
                self.visible = False
                return True
            elif event.key == pygame.K_LEFT:
                if self._categories:
                    self.current_category_index = (self.current_category_index - 1) % len(self._categories)
                    self.scroll_offset = 0
                return True
            elif event.key == pygame.K_RIGHT:
                if self._categories:
                    self.current_category_index = (self.current_category_index + 1) % len(self._categories)
                    self.scroll_offset = 0
                return True
            elif event.key == pygame.K_UP:
                self.scroll_offset = max(0, self.scroll_offset - 1)
                return True
            elif event.key == pygame.K_DOWN:
                # Scroll limit will be enforced in draw()
                self.scroll_offset += 1
                return True
        elif event.type == pygame.MOUSEWHEEL:
            # Scroll with mouse wheel; positive y scrolls down for consistency with tests
            # Clamp to 0 here; max scroll is enforced in draw().
            self.scroll_offset = max(0, self.scroll_offset + event.y)
            return True

        return False

    def update(self, dt: float) -> None:
        """Update animations if any."""
        # No animations currently, but method exists for future use
        pass

    def _wrap_text(self, text: str, font: pygame.font.Font, max_width: int) -> List[str]:
        """Wrap text to fit within max_width using shared helper."""
        return wrap_text(text, font, max_width)

    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw the help overlay:
        1. Semi-transparent dark background
        2. Category tabs at top
        3. Scrollable content area
        4. "Press H or ESC to close" footer
        """
        if not self.visible:
            return

        screen_width = surface.get_width()
        screen_height = surface.get_height()

        # Draw semi-transparent background overlay
        overlay_surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay_color = Colors.BG_OVERLAY
        if len(overlay_color) == 4:
            # RGBA color
            overlay_surface.fill(overlay_color)
        else:
            # RGB color, add alpha
            overlay_surface.fill((*overlay_color, Layout.OVERLAY_ALPHA))
        surface.blit(overlay_surface, (0, 0))

        # Main panel dimensions
        panel_margin = Layout.SCREEN_MARGIN_LARGE
        panel_x = panel_margin
        panel_y = panel_margin
        panel_width = screen_width - (panel_margin * 2)
        panel_height = screen_height - (panel_margin * 2)

        # Draw main panel background
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(surface, Colors.BG_PANEL, panel_rect, border_radius=Layout.CORNER_RADIUS_LARGE)
        pygame.draw.rect(surface, Colors.BORDER, panel_rect, Layout.BORDER_WIDTH, border_radius=Layout.CORNER_RADIUS_LARGE)

        # Load fonts
        title_font = pygame.font.Font(None, Fonts.SIZE_HEADING)
        tab_font = pygame.font.Font(None, Fonts.SIZE_SUBHEADING)
        content_font = pygame.font.Font(None, Fonts.SIZE_BODY)
        footer_font = pygame.font.Font(None, Fonts.SIZE_SMALL)

        # Draw title
        title_text = "Help"
        title_surface = title_font.render(title_text, True, Colors.TEXT_HIGHLIGHT)
        title_x = panel_x + Layout.PADDING_XL
        title_y = panel_y + Layout.PADDING_LG
        surface.blit(title_surface, (title_x, title_y))

        # Tab area
        tab_area_y = title_y + title_surface.get_height() + Layout.SECTION_GAP
        tab_height = Layout.MENU_ITEM_HEIGHT
        tab_area_height = tab_height + Layout.PADDING_SM

        # Draw category tabs
        if self._categories:
            tab_padding = Layout.PADDING_MD
            tab_x = panel_x + Layout.PADDING_XL
            tab_y = tab_area_y

            for i, category in enumerate(self._categories):
                is_selected = (i == self.current_category_index)
                tab_text = category.replace("_", " ").title()
                tab_surface = tab_font.render(tab_text, True, Colors.TEXT_PRIMARY if is_selected else Colors.TEXT_SECONDARY)
                tab_width = tab_surface.get_width() + (tab_padding * 2)
                tab_rect = pygame.Rect(tab_x, tab_y, tab_width, tab_height)

                # Draw tab background
                if is_selected:
                    pygame.draw.rect(surface, Colors.BG_DARK, tab_rect, border_radius=Layout.CORNER_RADIUS_SMALL)
                    pygame.draw.rect(surface, Colors.BORDER_HIGHLIGHT, tab_rect, Layout.BORDER_WIDTH, border_radius=Layout.CORNER_RADIUS_SMALL)
                else:
                    pygame.draw.rect(surface, Colors.BG_MAIN, tab_rect, border_radius=Layout.CORNER_RADIUS_SMALL)
                    pygame.draw.rect(surface, Colors.BORDER, tab_rect, Layout.BORDER_WIDTH, border_radius=Layout.CORNER_RADIUS_SMALL)

                # Draw tab text
                text_x = tab_x + tab_padding
                text_y = tab_y + (tab_height - tab_surface.get_height()) // 2
                surface.blit(tab_surface, (text_x, text_y))

                tab_x += tab_width + Layout.ELEMENT_GAP

        # Content area
        content_x = panel_x + Layout.PADDING_XL
        content_y = tab_area_y + tab_area_height + Layout.SECTION_GAP
        content_width = panel_width - (Layout.PADDING_XL * 2)
        content_height = panel_height - (content_y - panel_y) - Layout.PADDING_XL - footer_font.get_height() - Layout.PADDING_MD

        # Draw content background
        content_rect = pygame.Rect(content_x, content_y, content_width, content_height)
        pygame.draw.rect(surface, Colors.BG_DARK, content_rect, border_radius=Layout.CORNER_RADIUS)

        # Draw scrollable content
        if self._categories and self.current_category_index < len(self._categories):
            current_category = self._categories[self.current_category_index]
            entries = self._entries_by_category.get(current_category, [])

            line_height = content_font.get_linesize() + Layout.ELEMENT_GAP_SMALL
            entry_spacing = Layout.SECTION_GAP_SMALL
            y_offset = content_y + Layout.PADDING_LG - (self.scroll_offset * line_height)

            for entry in entries:
                # Draw entry title
                title_surface = content_font.render(entry.title, True, Colors.TEXT_HIGHLIGHT)
                if y_offset + title_surface.get_height() > content_y and y_offset < content_y + content_height:
                    surface.blit(title_surface, (content_x + Layout.PADDING_LG, y_offset))
                y_offset += title_surface.get_height() + Layout.ELEMENT_GAP_SMALL

                # Draw entry content (word-wrapped)
                wrapped_lines = self._wrap_text(entry.content, content_font, content_width - (Layout.PADDING_LG * 2))
                for line in wrapped_lines:
                    if y_offset + line_height > content_y and y_offset < content_y + content_height:
                        line_surface = content_font.render(line, True, Colors.TEXT_PRIMARY)
                        surface.blit(line_surface, (content_x + Layout.PADDING_LG, y_offset))
                    y_offset += line_height

                y_offset += entry_spacing

            # Calculate max scroll offset
            total_content_height = y_offset - (content_y + Layout.PADDING_LG)
            max_scroll = max(0, int((total_content_height - content_height) / line_height) + 1)
            self.scroll_offset = min(self.scroll_offset, max_scroll)
        else:
            # No categories or entries
            no_content_text = "No help entries available."
            no_content_surface = content_font.render(no_content_text, True, Colors.TEXT_SECONDARY)
            text_x = content_x + (content_width - no_content_surface.get_width()) // 2
            text_y = content_y + (content_height - no_content_surface.get_height()) // 2
            surface.blit(no_content_surface, (text_x, text_y))

        # Draw footer
        footer_text = "Press H or ESC to close"
        footer_surface = footer_font.render(footer_text, True, Colors.TEXT_SECONDARY)
        footer_x = panel_x + (panel_width - footer_surface.get_width()) // 2
        footer_y = panel_y + panel_height - footer_font.get_height() - Layout.PADDING_MD
        surface.blit(footer_surface, (footer_x, footer_y))

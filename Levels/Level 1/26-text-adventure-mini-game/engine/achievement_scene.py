"""Achievement list scene for viewing all achievements with detail panel."""

import pygame
from typing import Any, Dict, List, Optional, Tuple, TYPE_CHECKING

from .base_menu_scene import BaseMenuScene
from .assets import AssetManager
from .theme import Colors, Fonts, Layout
from .achievement_popup import AchievementListUI
from .config_loader import load_config
from core.constants import DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT
from core.achievements import Achievement, AchievementManager

if TYPE_CHECKING:
    from .scene import SceneManager


class AchievementScene(BaseMenuScene):
    """Scene for browsing all achievements alongside a detailed inspector."""

    DETAIL_SCROLL_STEP = 24

    def __init__(
        self,
        manager: Optional["SceneManager"],
        achievement_manager: AchievementManager,
        assets: Optional[AssetManager] = None,
        scale: int = 2,
    ):
        super().__init__(manager, assets, scale)
        self.achievement_manager = achievement_manager

        self.config = load_config()
        self.screen_width = self.config.get("window_width", DEFAULT_WINDOW_WIDTH)
        self.screen_height = self.config.get("window_height", DEFAULT_WINDOW_HEIGHT)

        self.achievement_list = AchievementListUI(
            achievements=list(self.achievement_manager.achievements.values()),
            screen_width=self.screen_width,
            screen_height=self.screen_height,
            achievement_manager=self.achievement_manager,
        )

        self.anim_time = 0.0
        self.focus_on_list = True
        self.detail_scroll = 0
        self._max_detail_scroll = 0

    # ------------------------------------------------------------------
    # Event handling
    # ------------------------------------------------------------------

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle keyboard navigation for list/detail focus."""
        if event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_ESCAPE:
            self.manager.pop()
            return

        if event.key in (pygame.K_RETURN, pygame.K_SPACE):
            self.focus_on_list = not self.focus_on_list
            if self.focus_on_list:
                self.detail_scroll = 0
            return

        if self.focus_on_list:
            self._handle_list_event(event)
        else:
            self._handle_detail_event(event)

    def _handle_list_event(self, event: pygame.event.Event) -> None:
        """Handle input while focus is on the list."""
        if event.key == pygame.K_UP:
            self.achievement_list.move_selection(-1)
            self.detail_scroll = 0
        elif event.key == pygame.K_DOWN:
            self.achievement_list.move_selection(1)
            self.detail_scroll = 0
        elif event.key == pygame.K_LEFT:
            self._shift_category(-1)
        elif event.key == pygame.K_RIGHT:
            self._shift_category(1)

    def _handle_detail_event(self, event: pygame.event.Event) -> None:
        """Handle scrolling while focus is on the detail panel."""
        if event.key == pygame.K_UP:
            self.detail_scroll = max(0, self.detail_scroll - self.DETAIL_SCROLL_STEP)
        elif event.key == pygame.K_DOWN:
            self.detail_scroll = min(
                self._max_detail_scroll, self.detail_scroll + self.DETAIL_SCROLL_STEP
            )
        elif event.key in (pygame.K_PAGEUP, pygame.K_HOME):
            self.detail_scroll = 0
        elif event.key in (pygame.K_PAGEDOWN, pygame.K_END):
            self.detail_scroll = self._max_detail_scroll

    def _shift_category(self, delta: int) -> None:
        """Change the active category tab."""
        categories = self.achievement_list.categories
        current = self.achievement_list.current_category
        if not categories:
            return

        if current is None:
            next_index = -1 if delta < 0 else 0
        else:
            try:
                idx = categories.index(current)
            except ValueError:
                idx = 0
            next_index = idx + delta

        if next_index < 0:
            self.achievement_list.set_category(None)
        elif next_index >= len(categories):
            self.achievement_list.set_category(None)
        else:
            self.achievement_list.set_category(categories[next_index])

        self.detail_scroll = 0

    # ------------------------------------------------------------------
    # Update + draw lifecycle
    # ------------------------------------------------------------------

    def update(self, dt: float) -> None:
        """Update animation timer and clamp scroll."""
        self.anim_time += dt
        if hasattr(self.achievement_list, "anim_time"):
            self.achievement_list.anim_time = self.anim_time

        self.detail_scroll = max(0, min(self.detail_scroll, self._max_detail_scroll))

    def draw(self, surface: pygame.Surface) -> None:
        """Render the list + detail layout."""
        width, height = surface.get_size()
        if width != self.screen_width or height != self.screen_height:
            self._rebuild_list(width, height)

        self.draw_overlay(surface)

        panel_rect = pygame.Rect(
            Layout.SCREEN_MARGIN,
            Layout.SCREEN_MARGIN,
            width - Layout.SCREEN_MARGIN * 2,
            height - Layout.SCREEN_MARGIN * 2,
        )
        self._draw_panel_background(surface, panel_rect)

        title_font = self.assets.get_font(Fonts.DEFAULT, Fonts.SIZE_HEADING)
        font = self.assets.get_font(Fonts.DEFAULT, Fonts.SIZE_BODY)
        small_font = self.assets.get_font(Fonts.SMALL, Fonts.SIZE_SMALL)

        list_rect, detail_rect = self._compute_content_rects(panel_rect)
        self._draw_list_background(surface, list_rect)

        layout = {
            "header_pos": (panel_rect.left + Layout.PADDING_LG, panel_rect.top + Layout.PADDING_LG - 8),
            "stats_pos": (panel_rect.left + Layout.PADDING_LG, panel_rect.top + Layout.PADDING_LG + 18),
            "tab_origin": (panel_rect.left + Layout.PADDING_LG, panel_rect.top + 70),
            "tab_width": 110,
            "tab_height": 30,
            "tab_spacing": Layout.ELEMENT_GAP,
            "list_rect": list_rect,
        }
        self.achievement_list.draw(surface, font, small_font, layout)

        self._draw_detail_panel(surface, detail_rect, title_font, font, small_font)
        self._draw_help_text(surface, small_font)

    def _rebuild_list(self, width: int, height: int) -> None:
        """Recreate the list UI when the screen size changes."""
        self.screen_width = width
        self.screen_height = height
        current_cat = self.achievement_list.current_category
        self.achievement_list = AchievementListUI(
            achievements=list(self.achievement_manager.achievements.values()),
            screen_width=self.screen_width,
            screen_height=self.screen_height,
            achievement_manager=self.achievement_manager,
        )
        if current_cat is not None:
            self.achievement_list.set_category(current_cat)

    # ------------------------------------------------------------------
    # Drawing helpers
    # ------------------------------------------------------------------

    def _draw_panel_background(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        """Draw the main container panel."""
        if self.panel:
            self.panel.draw(surface, rect)
        else:
            pygame.draw.rect(surface, Colors.BG_PANEL, rect, border_radius=Layout.CORNER_RADIUS)
            pygame.draw.rect(
                surface,
                Colors.BORDER,
                rect,
                Layout.BORDER_WIDTH,
                border_radius=Layout.CORNER_RADIUS,
            )

    def _compute_content_rects(self, panel_rect: pygame.Rect) -> Tuple[pygame.Rect, pygame.Rect]:
        """Split the panel into list and detail areas."""
        list_width = int(panel_rect.width * 0.45)
        list_rect = pygame.Rect(
            panel_rect.left + Layout.PADDING_LG,
            panel_rect.top + 120,
            max(260, list_width - Layout.PADDING_LG),
            panel_rect.height - 160,
        )
        detail_rect = pygame.Rect(
            list_rect.right + Layout.PADDING_LG,
            list_rect.top,
            panel_rect.right - Layout.PADDING_LG - (list_rect.right + Layout.PADDING_LG),
            list_rect.height,
        )
        if detail_rect.width < 260:
            # Fallback to equal split if available width is too small
            half_width = (panel_rect.width - Layout.PADDING_LG * 3) // 2
            list_rect.width = half_width
            detail_rect.x = list_rect.right + Layout.PADDING_LG
            detail_rect.width = half_width
        return list_rect, detail_rect

    def _draw_list_background(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        """Render a subtle background under the list."""
        pygame.draw.rect(
            surface,
            Colors.BG_DARK,
            rect,
            border_radius=Layout.CORNER_RADIUS_SMALL,
        )
        border_color = Colors.BORDER_HIGHLIGHT if self.focus_on_list else Colors.BORDER
        pygame.draw.rect(
            surface,
            border_color,
            rect,
            Layout.BORDER_WIDTH,
            border_radius=Layout.CORNER_RADIUS_SMALL,
        )

    def _draw_detail_panel(
        self,
        surface: pygame.Surface,
        rect: pygame.Rect,
        title_font: pygame.font.Font,
        font: pygame.font.Font,
        small_font: pygame.font.Font,
    ) -> None:
        """Render the detail inspector for the selected achievement."""
        pygame.draw.rect(surface, Colors.BG_DARK, rect, border_radius=Layout.CORNER_RADIUS_SMALL)
        border_color = Colors.BORDER if self.focus_on_list else Colors.BORDER_HIGHLIGHT
        pygame.draw.rect(
            surface,
            border_color,
            rect,
            Layout.BORDER_WIDTH,
            border_radius=Layout.CORNER_RADIUS_SMALL,
        )

        achievement = self.achievement_list.get_selected()
        padding = Layout.PADDING_LG
        inner_rect = rect.inflate(-padding * 2, -padding * 2)
        if inner_rect.width <= 0 or inner_rect.height <= 0:
            self._max_detail_scroll = 0
            self.detail_scroll = 0
            return

        if not achievement:
            message = small_font.render("No achievements available.", True, Colors.TEXT_DISABLED)
            surface.blit(
                message,
                message.get_rect(center=rect.center),
            )
            self._max_detail_scroll = 0
            self.detail_scroll = 0
            return

        content_surface, max_scroll = self._build_detail_surface(
            achievement, inner_rect.width, inner_rect.height, title_font, font, small_font
        )
        self._max_detail_scroll = max_scroll
        self.detail_scroll = max(0, min(self.detail_scroll, max_scroll))

        clip_rect = pygame.Rect(
            0,
            self.detail_scroll,
            inner_rect.width,
            inner_rect.height,
        )
        surface.blit(
            content_surface,
            (inner_rect.left, inner_rect.top),
            area=clip_rect,
        )

    def _build_detail_surface(
        self,
        achievement: Achievement,
        width: int,
        visible_height: int,
        title_font: pygame.font.Font,
        font: pygame.font.Font,
        small_font: pygame.font.Font,
    ) -> Tuple[pygame.Surface, int]:
        """Create a surface containing all detail content, returning surface + max scroll."""
        entries: List[Tuple[str, Dict[str, Any]]] = []

        entries.append(
            (
                "text",
                {
                    "text": achievement.get_display_name(),
                    "font": title_font,
                    "color": Colors.TEXT_PRIMARY,
                },
            )
        )
        meta = f"{achievement.category.value.title()} • {achievement.rarity.value.title()} • {achievement.points} pts"
        entries.append(
            ("text", {"text": meta, "font": font, "color": Colors.TEXT_SECONDARY})
        )
        entries.append(("spacer", {"size": Layout.ELEMENT_GAP_LARGE}))

        description = achievement.get_display_description() or "No description provided."
        for line in self._wrap_text(description, small_font, width):
            entries.append(
                ("text", {"text": line, "font": small_font, "color": Colors.TEXT_SECONDARY})
            )

        entries.append(("spacer", {"size": Layout.SECTION_GAP_SMALL}))
        progress_label = achievement.get_progress_text()
        entries.append(
            (
                "progress",
                {
                    "percent": achievement.get_progress_percent(),
                    "label": progress_label,
                    "font": small_font,
                },
            )
        )

        entries.append(("section", {"label": "Rewards", "font": font}))
        for reward in achievement.get_reward_lines():
            entries.append(
                (
                    "text",
                    {
                        "text": f"• {reward}",
                        "font": small_font,
                        "color": Colors.TEXT_PRIMARY,
                    },
                )
            )

        unlock_color = Colors.TEXT_INFO if achievement.unlocked else Colors.TEXT_DISABLED
        entries.append(("spacer", {"size": Layout.SECTION_GAP_SMALL}))
        entries.append(
            (
                "text",
                {
                    "text": f"Unlock Status: {achievement.get_unlock_display()}",
                    "font": small_font,
                    "color": unlock_color,
                },
            )
        )
        if achievement.hidden and not achievement.unlocked:
            entries.append(
                (
                    "text",
                    {
                        "text": "Hidden achievement — progress to reveal more details.",
                        "font": small_font,
                        "color": Colors.TEXT_DISABLED,
                    },
                )
            )

        content_height = self._measure_entries(entries)
        content_surface = pygame.Surface((width, max(10, content_height)), pygame.SRCALPHA)

        y = 0
        for entry_type, data in entries:
            if entry_type == "text":
                text_surface = data["font"].render(data["text"], True, data.get("color", Colors.TEXT_PRIMARY))
                content_surface.blit(text_surface, (0, y))
                y += text_surface.get_height() + Layout.ELEMENT_GAP_SMALL
            elif entry_type == "section":
                label_surface = data["font"].render(data["label"], True, Colors.TEXT_INFO)
                content_surface.blit(label_surface, (0, y))
                y += label_surface.get_height() + Layout.ELEMENT_GAP_SMALL
                pygame.draw.line(
                    content_surface,
                    Colors.BORDER,
                    (0, y),
                    (width, y),
                    1,
                )
                y += Layout.ELEMENT_GAP_SMALL
            elif entry_type == "progress":
                bar_height = Layout.BAR_HEIGHT
                bar_rect = pygame.Rect(0, y, width, bar_height)
                pygame.draw.rect(content_surface, Colors.BAR_BG, bar_rect, border_radius=Layout.BAR_BORDER_RADIUS)
                fill_width = int(width * data["percent"])
                if fill_width > 0:
                    fill_rect = pygame.Rect(0, y, fill_width, bar_height)
                    pygame.draw.rect(
                        content_surface,
                        Colors.ACCENT,
                        fill_rect,
                        border_radius=Layout.BAR_BORDER_RADIUS,
                    )
                y += bar_height + Layout.ELEMENT_GAP_SMALL
                label_surface = data["font"].render(data["label"], True, Colors.TEXT_SECONDARY)
                content_surface.blit(label_surface, (0, y))
                y += label_surface.get_height() + Layout.ELEMENT_GAP_SMALL
            elif entry_type == "spacer":
                y += data["size"]

        max_scroll = max(0, content_surface.get_height() - visible_height)
        return content_surface, max_scroll

    def _measure_entries(self, entries: List[Tuple[str, Dict[str, Any]]]) -> int:
        """Estimate the total content height for the detail surface."""
        height = 0
        for entry_type, data in entries:
            if entry_type == "text":
                height += data["font"].size(data["text"])[1] + Layout.ELEMENT_GAP_SMALL
            elif entry_type == "section":
                height += data["font"].size(data["label"])[1] + Layout.ELEMENT_GAP_SMALL * 2
            elif entry_type == "progress":
                height += Layout.BAR_HEIGHT + data["font"].get_height() + Layout.ELEMENT_GAP
            elif entry_type == "spacer":
                height += data["size"]
        return height

    def _draw_help_text(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        """Display control helper text near the bottom of the screen."""
        width, height = surface.get_size()
        focus_label = "List" if self.focus_on_list else "Detail"
        help_text = (
            f"↑/↓: {'Navigate' if self.focus_on_list else 'Scroll Detail'}  •  "
            "←/→: Categories  •  "
            f"ENTER/SPACE: Toggle Focus ({focus_label})  •  ESC: Close"
        )
        help_surface = font.render(help_text, True, Colors.TEXT_SECONDARY)
        help_rect = help_surface.get_rect(
            center=(width // 2, height - Layout.SCREEN_MARGIN)
        )
        surface.blit(help_surface, help_rect)

    # ------------------------------------------------------------------
    # Utility helpers
    # ------------------------------------------------------------------

    def _wrap_text(self, text: str, font: pygame.font.Font, max_width: int) -> List[str]:
        """Word-wrap text to the given width using the supplied font."""
        words = text.split()
        if not words:
            return [""]

        lines: List[str] = []
        current_line = words[0]

        for word in words[1:]:
            test_line = f"{current_line} {word}"
            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word

        lines.append(current_line)
        return lines

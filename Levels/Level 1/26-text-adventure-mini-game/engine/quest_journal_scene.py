"""Quest journal scene for viewing and tracking quests."""

import pygame
from typing import Dict, List, Optional, Tuple, TYPE_CHECKING

from .base_menu_scene import BaseMenuScene
from .assets import AssetManager
from .ui import Menu, NineSlicePanel, draw_contextual_help
from .ui.utils import draw_themed_panel
from .theme import (
    Colors, Fonts, Layout,
    PANEL_TAB, PANEL_TAB_SELECTED, PANEL_ITEM_SELECTED, PANEL_SUBPANEL,
)
from core.quests import Quest, QuestManager, QuestStatus

if TYPE_CHECKING:
    from .scene import SceneManager


class QuestJournalScene(BaseMenuScene):
    """Scene for viewing quest journal with tabs for active/completed quests."""

    # Tab constants
    TAB_ACTIVE = 0
    TAB_COMPLETED = 1
    TAB_AVAILABLE = 2
    TAB_NAMES = ["Active", "Completed", "Available"]

    def __init__(
        self,
        manager: Optional["SceneManager"],
        quest_manager: QuestManager,
        assets: Optional[AssetManager] = None,
        scale: int = 2,
    ):
        super().__init__(manager, assets, scale)
        self.quest_manager = quest_manager

        # UI state
        self.current_tab = self.TAB_ACTIVE
        self.selected_quest_index = 0
        self.scroll_offset = 0
        self.max_visible_quests = 6
        self.max_visible_objectives = 5
        self.sort_modes = ["Name", "Difficulty", "Reward"]
        self.sort_index = 0
        self.filters = self._build_filters()
        self.filter_index = 0

        # Feedback message
        self.feedback_message: str = ""
        self.feedback_timer: float = 0.0
        self.feedback_color: tuple = (255, 255, 255)

        # Cached quest lists per tab
        self._refresh_quest_lists()

    def _build_filters(self) -> List[str]:
        """Build the filter options based on quest categories/tags."""
        if not self.quest_manager:
            return ["all"]

        categories = {quest.category for quest in self.quest_manager.quests.values()}
        tags = set()
        for quest in self.quest_manager.quests.values():
            tags.update(quest.tags or [])

        filters = ["all"]
        filters.extend(sorted(cat for cat in categories if cat))
        filters.extend(sorted(tag for tag in tags if tag))
        return filters

    def _refresh_quest_lists(self) -> None:
        """Refresh cached quest lists for each tab."""
        self.quest_lists = {
            self.TAB_ACTIVE: self.quest_manager.get_active_quests(),
            self.TAB_COMPLETED: self.quest_manager.get_completed_quests(),
            self.TAB_AVAILABLE: self.quest_manager.get_available_quests(),
        }
        self._clamp_selection()

    def _get_current_quests(self) -> List[Quest]:
        """Get quests for current tab."""
        return self._get_filtered_quests(self.current_tab)

    def _get_filtered_quests(self, tab: Optional[int] = None) -> List[Quest]:
        """Filter and sort quests for a specific tab."""
        base = self.quest_lists.get(self.current_tab if tab is None else tab, [])
        filtered = [quest for quest in base if self._filter_accepts(quest)]
        return sorted(filtered, key=self._sort_key)

    def _get_selected_quest(self) -> Optional[Quest]:
        """Get currently selected quest."""
        quests = self._get_current_quests()
        if 0 <= self.selected_quest_index < len(quests):
            return quests[self.selected_quest_index]
        return None

    def _filter_accepts(self, quest: Quest) -> bool:
        """Return True if the quest passes the active filter."""
        if not self.filters:
            return True
        active_filter = self.filters[self.filter_index]
        if active_filter == "all":
            return True
        if active_filter == quest.category:
            return True
        return active_filter in (quest.tags or [])

    def _sort_key(self, quest: Quest) -> Tuple:
        """Key used for sorting quests based on current mode."""
        mode = self.sort_modes[self.sort_index]
        if mode == "Difficulty":
            return (self._difficulty_rank(quest.difficulty), quest.name.lower())
        if mode == "Reward":
            reward_score = quest.reward_gold + quest.reward_exp + sum(quest.reward_items.values()) * 5
            return (-reward_score, quest.name.lower())
        return (quest.name.lower(),)

    def _difficulty_rank(self, difficulty: Optional[str]) -> int:
        """Map textual difficulty to a sortable rank."""
        order = {
            "story": 0,
            "tutorial": 0,
            "easy": 1,
            "normal": 2,
            "challenging": 3,
            "hard": 4,
            "epic": 5,
        }
        label = (difficulty or "normal").lower()
        return order.get(label, 2)

    def _cycle_filter(self, delta: int) -> None:
        """Cycle through available filters."""
        if not self.filters:
            return
        self.filter_index = (self.filter_index + delta) % len(self.filters)
        self.selected_quest_index = 0
        self.scroll_offset = 0
        self._clamp_selection()

    def _cycle_sort(self, delta: int) -> None:
        """Cycle through available sort orders."""
        self.sort_index = (self.sort_index + delta) % len(self.sort_modes)
        self.selected_quest_index = 0
        self.scroll_offset = 0
        self._clamp_selection()

    def _clamp_selection(self) -> None:
        """Ensure the current selection is valid after filters change."""
        quests = self._get_current_quests()
        if not quests:
            self.selected_quest_index = 0
            self.scroll_offset = 0
            return
        if self.selected_quest_index >= len(quests):
            self.selected_quest_index = len(quests) - 1
        self._adjust_scroll()

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle input events."""
        if event.type != pygame.KEYDOWN:
            return

        quests = self._get_current_quests()

        if event.key == pygame.K_ESCAPE:
            self.manager.pop()

        elif event.key == pygame.K_q:
            self._cycle_filter(-1)
        elif event.key == pygame.K_w:
            self._cycle_filter(1)
        elif event.key == pygame.K_a:
            self._cycle_sort(-1)
        elif event.key == pygame.K_s:
            self._cycle_sort(1)

        elif event.key == pygame.K_LEFT:
            # Switch to previous tab
            self.current_tab = (self.current_tab - 1) % len(self.TAB_NAMES)
            self.selected_quest_index = 0
            self.scroll_offset = 0
            self._clamp_selection()

        elif event.key == pygame.K_RIGHT:
            # Switch to next tab
            self.current_tab = (self.current_tab + 1) % len(self.TAB_NAMES)
            self.selected_quest_index = 0
            self.scroll_offset = 0
            self._clamp_selection()

        elif event.key == pygame.K_UP:
            if quests:
                self.selected_quest_index = (self.selected_quest_index - 1) % len(quests)
                self._adjust_scroll()

        elif event.key == pygame.K_DOWN:
            if quests:
                self.selected_quest_index = (self.selected_quest_index + 1) % len(quests)
                self._adjust_scroll()

        elif event.key == pygame.K_RETURN:
            self._handle_select_action()

    def _adjust_scroll(self) -> None:
        """Adjust scroll offset to keep selected quest visible."""
        if self.selected_quest_index < self.scroll_offset:
            self.scroll_offset = self.selected_quest_index
        elif self.selected_quest_index >= self.scroll_offset + self.max_visible_quests:
            self.scroll_offset = self.selected_quest_index - self.max_visible_quests + 1

    def _handle_select_action(self) -> None:
        """Handle Enter key - toggle tracking or start quest based on tab."""
        quest = self._get_selected_quest()
        if not quest:
            return

        if self.current_tab == self.TAB_ACTIVE:
            # Toggle tracking for active quests
            quest.tracked = not quest.tracked
            if quest.tracked:
                # Untrack other quests (only one tracked at a time)
                for other in self.quest_manager.get_active_quests():
                    if other.id != quest.id:
                        other.tracked = False
                self._show_feedback(f"Now tracking: {quest.name}", (100, 255, 100))
            else:
                self._show_feedback(f"Stopped tracking: {quest.name}", (200, 200, 200))

        elif self.current_tab == self.TAB_AVAILABLE:
            # Start available quests
            if self.quest_manager.start_quest(quest.id):
                quest.tracked = True
                # Untrack other quests
                for other in self.quest_manager.get_active_quests():
                    if other.id != quest.id:
                        other.tracked = False
                self._show_feedback(f"Quest started: {quest.name}", (100, 255, 100))
                self._refresh_quest_lists()
                # Switch to Active tab to show the quest
                self.current_tab = self.TAB_ACTIVE
                self.selected_quest_index = 0
                self.scroll_offset = 0
            else:
                self._show_feedback("Cannot start this quest", (255, 100, 100))

        elif self.current_tab == self.TAB_COMPLETED:
            # Completed quests - just show info
            self._show_feedback("Quest already completed", (200, 200, 150))

    def _show_feedback(self, message: str, color: tuple) -> None:
        """Show a temporary feedback message."""
        self.feedback_message = message
        self.feedback_color = color
        self.feedback_timer = 2.0  # Show for 2 seconds

    def update(self, dt: float) -> None:
        """Update scene state."""
        # Update feedback timer
        if self.feedback_timer > 0:
            self.feedback_timer -= dt
            if self.feedback_timer <= 0:
                self.feedback_message = ""

        # Refresh quest lists in case they changed
        self._refresh_quest_lists()

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the quest journal."""
        # Draw semi-transparent background
        overlay = pygame.Surface(surface.get_size())
        overlay.set_alpha(200)
        overlay.fill(Colors.BG_MAIN)
        surface.blit(overlay, (0, 0))

        # Get fonts
        font = self.assets.get_font("default")
        small_font = self.assets.get_font("small")
        title_font = self.assets.get_font("large", 28) or font

        # Draw main panel background
        panel_rect = pygame.Rect(40, 40, 560, 400)
        draw_themed_panel(surface, panel_rect, panel=self.panel)

        # Draw title with shadow
        title_shadow = title_font.render("Quest Journal", True, Colors.BLACK)
        title = title_font.render("Quest Journal", True, Colors.ACCENT)
        title_x = panel_rect.centerx - title.get_width() // 2
        surface.blit(title_shadow, (title_x + 1, 51))
        surface.blit(title, (title_x, 50))

        # Draw tabs
        self._draw_tabs(surface, font, panel_rect)
        self._draw_sort_filter_badges(surface, small_font, panel_rect)

        # Draw quest list (left side)
        self._draw_quest_list(surface, font, small_font, panel_rect)

        # Draw quest details (right side)
        self._draw_quest_details(surface, font, small_font, panel_rect)

        # Draw feedback message if active
        if self.feedback_message and self.feedback_timer > 0:
            # Fade out effect
            alpha = min(255, int(self.feedback_timer * 255))
            feedback_surface = font.render(self.feedback_message, True, self.feedback_color)
            feedback_surface.set_alpha(alpha)
            surface.blit(feedback_surface, (panel_rect.centerx - feedback_surface.get_width() // 2, panel_rect.bottom - 50))

        # Draw controls hint with context-sensitive action
        if self.current_tab == self.TAB_ACTIVE:
            action_hint = "ENTER: Toggle Track"
        elif self.current_tab == self.TAB_AVAILABLE:
            action_hint = "ENTER: Start Quest"
        else:
            action_hint = "ENTER: View"
        help_text = (
            f"Left/Right: Tab  |  Up/Down: Select  |  {action_hint}  |  "
            "Q/W: Filter  |  A/S: Sort  |  ESC: Close"
        )

        font_small = self.assets.get_font("small")
        draw_contextual_help(surface, help_text, font_small, margin_bottom=panel_rect.bottom - 25)

    def _draw_tabs(self, surface: pygame.Surface, font: pygame.font.Font, panel_rect: pygame.Rect) -> None:
        """Draw tab buttons."""
        tab_y = 85
        tab_width = 100
        tab_spacing = Layout.ELEMENT_GAP_LARGE
        total_width = len(self.TAB_NAMES) * tab_width + (len(self.TAB_NAMES) - 1) * tab_spacing
        start_x = panel_rect.centerx - total_width // 2

        for i, tab_name in enumerate(self.TAB_NAMES):
            tab_x = start_x + i * (tab_width + tab_spacing)
            tab_rect = pygame.Rect(tab_x, tab_y, tab_width, 28)

            # Draw tab background with rounded corners
            if i == self.current_tab:
                draw_themed_panel(surface, tab_rect, PANEL_TAB_SELECTED)
                color = Colors.TEXT_PRIMARY
            else:
                draw_themed_panel(surface, tab_rect, PANEL_TAB)
                color = Colors.TEXT_SECONDARY

            # Draw tab text with count
            quests = self.quest_lists.get(i, [])
            text = f"{tab_name} ({len(quests)})"
            tab_text = font.render(text, True, color)
            text_x = tab_rect.centerx - tab_text.get_width() // 2
            text_y = tab_rect.centery - tab_text.get_height() // 2
            surface.blit(tab_text, (text_x, text_y))

    def _draw_sort_filter_badges(
        self,
        surface: pygame.Surface,
        font: pygame.font.Font,
        panel_rect: pygame.Rect,
    ) -> None:
        """Render current filter/sort selections near the top-right."""
        filter_label = self._format_filter_label(self.filters[self.filter_index]) if self.filters else "All"
        sort_label = self.sort_modes[self.sort_index]

        filter_text = font.render(f"Filter: {filter_label}", True, Colors.TEXT_SECONDARY)
        sort_text = font.render(f"Sort: {sort_label}", True, Colors.TEXT_SECONDARY)

        filter_pos = (
            panel_rect.right - filter_text.get_width() - Layout.PADDING_LG,
            panel_rect.top + Layout.PADDING_LG,
        )
        sort_pos = (
            panel_rect.right - sort_text.get_width() - Layout.PADDING_LG,
            filter_pos[1] + filter_text.get_height() + Layout.ELEMENT_GAP_SMALL,
        )

        surface.blit(filter_text, filter_pos)
        surface.blit(sort_text, sort_pos)

    def _draw_quest_list(
        self,
        surface: pygame.Surface,
        font: pygame.font.Font,
        small_font: pygame.font.Font,
        panel_rect: pygame.Rect
    ) -> None:
        """Draw the list of quests on the left side."""
        list_rect = pygame.Rect(panel_rect.left + Layout.PADDING_LG, 125, 200, 280)

        # Draw list background with rounded corners
        draw_themed_panel(surface, list_rect, PANEL_SUBPANEL)

        quests = self._get_current_quests()

        if not quests:
            no_quests = small_font.render("No quests", True, Colors.TEXT_DISABLED)
            surface.blit(no_quests, (list_rect.centerx - no_quests.get_width() // 2, list_rect.top + Layout.PADDING_LG))
            return

        # Draw visible quests
        y = list_rect.top + Layout.PADDING_SM
        visible_quests = quests[self.scroll_offset:self.scroll_offset + self.max_visible_quests]

        for i, quest in enumerate(visible_quests):
            actual_index = self.scroll_offset + i
            is_selected = actual_index == self.selected_quest_index

            # Draw selection highlight with rounded corners
            item_rect = pygame.Rect(list_rect.left + 4, y - 2, list_rect.width - 8, 42)
            if is_selected:
                draw_themed_panel(surface, item_rect, PANEL_ITEM_SELECTED)

            # Draw quest name with tracking indicator
            color = Colors.TEXT_PRIMARY if is_selected else Colors.TEXT_SECONDARY
            prefix = "★ " if quest.tracked else ""
            name_display = prefix + quest.name[:18 if quest.tracked else 20]
            name_text = font.render(name_display, True, color)
            surface.blit(name_text, (list_rect.left + Layout.PADDING_MD, y))

            diff_label = (quest.difficulty or "Normal").upper()
            diff_surface = small_font.render(
                diff_label,
                True,
                self._get_difficulty_color(quest.difficulty),
            )
            surface.blit(
                diff_surface,
                (list_rect.right - diff_surface.get_width() - Layout.PADDING_MD, y),
            )

            # Draw category badge
            category_colors = {
                "main": Colors.ACCENT,
                "side": Colors.TEXT_INFO,
                "bounty": Colors.TEXT_ERROR,
            }
            badge_color = category_colors.get(quest.category, Colors.TEXT_SECONDARY)
            badge_text = small_font.render(quest.category.upper(), True, badge_color)
            surface.blit(badge_text, (list_rect.left + Layout.PADDING_MD, y + 22))

            y += 46

        # Draw scroll indicators
        if self.scroll_offset > 0:
            up_arrow = font.render("▲", True, Colors.TEXT_SECONDARY)
            surface.blit(up_arrow, (list_rect.right - 20, list_rect.top + 5))

        if self.scroll_offset + self.max_visible_quests < len(quests):
            down_arrow = font.render("▼", True, Colors.TEXT_SECONDARY)
            surface.blit(down_arrow, (list_rect.right - 20, list_rect.bottom - 20))

    def _draw_quest_details(
        self,
        surface: pygame.Surface,
        font: pygame.font.Font,
        small_font: pygame.font.Font,
        panel_rect: pygame.Rect
    ) -> None:
        """Draw quest details on the right side."""
        details_rect = pygame.Rect(panel_rect.left + 225, 125, 320, 280)

        # Draw details background with rounded corners
        draw_themed_panel(surface, details_rect, PANEL_SUBPANEL)

        quest = self._get_selected_quest()
        if not quest:
            hint = small_font.render("Select a quest to view details", True, Colors.TEXT_DISABLED)
            surface.blit(hint, (details_rect.centerx - hint.get_width() // 2, details_rect.top + 50))
            return

        y = details_rect.top + Layout.PADDING_MD
        padding = Layout.PADDING_MD

        # Quest name with tracking status - add shadow
        name_shadow = font.render(quest.name, True, Colors.BLACK)
        name_text = font.render(quest.name, True, Colors.ACCENT)
        surface.blit(name_shadow, (details_rect.left + padding + 1, y + 1))
        surface.blit(name_text, (details_rect.left + padding, y))

        # Draw tracking badge if tracked
        if quest.tracked:
            track_badge = small_font.render("★ TRACKING", True, Colors.TEXT_SUCCESS)
            surface.blit(track_badge, (details_rect.right - padding - track_badge.get_width(), y + 2))
        y += 28

        # Description (word wrap)
        desc_lines = self._wrap_text(quest.description, small_font, details_rect.width - 2 * padding)
        meta_parts = []
        if quest.difficulty:
            meta_parts.append(quest.difficulty.title())
        if quest.recommended_level:
            meta_parts.append(f"Lv {quest.recommended_level}+")
        if quest.tags:
            meta_parts.append(", ".join(tag.title() for tag in quest.tags))
        if meta_parts:
            meta_text = small_font.render(" • ".join(meta_parts), True, Colors.TEXT_SECONDARY)
            surface.blit(meta_text, (details_rect.left + padding, y))
            y += Layout.LINE_HEIGHT_COMPACT

        desc_lines = self._wrap_text(quest.description, small_font, details_rect.width - 2 * padding)
        for line in desc_lines[:5]:
            desc_text = small_font.render(line, True, Colors.TEXT_SECONDARY)
            surface.blit(desc_text, (details_rect.left + padding, y))
            y += Layout.LINE_HEIGHT_COMPACT
        y += Layout.ELEMENT_GAP

        # Objectives header
        obj_header = font.render("Objectives:", True, Colors.TEXT_INFO)
        surface.blit(obj_header, (details_rect.left + padding, y))
        y += Layout.LINE_HEIGHT

        # Draw objectives
        for i, obj in enumerate(quest.objectives[:self.max_visible_objectives]):
            # Progress indicator
            if obj.completed:
                status_color = Colors.TEXT_SUCCESS
                status_text = "[✓]"
            else:
                status_color = Colors.ACCENT
                status_text = obj.get_progress_text()

            status = small_font.render(status_text, True, status_color)
            surface.blit(status, (details_rect.left + padding, y))

            # Objective description
            obj_color = Colors.TEXT_DISABLED if obj.completed else Colors.TEXT_PRIMARY
            if obj.optional:
                obj_desc = f"(Optional) {obj.description}"
            else:
                obj_desc = obj.description
            obj_text = small_font.render(obj_desc[:35], True, obj_color)
            surface.blit(obj_text, (details_rect.left + padding + 45, y))
            y += Layout.LINE_HEIGHT_COMPACT

        # Show if more objectives exist
        if len(quest.objectives) > self.max_visible_objectives:
            more = small_font.render(f"... and {len(quest.objectives) - self.max_visible_objectives} more", True, Colors.TEXT_DISABLED)
            surface.blit(more, (details_rect.left + padding, y))
            y += Layout.LINE_HEIGHT_COMPACT

        y += Layout.ELEMENT_GAP

        # Rewards section (only for active/available quests)
        rewards: List[str] = []
        if quest.status in (QuestStatus.ACTIVE, QuestStatus.AVAILABLE):
            if quest.reward_gold > 0 or quest.reward_exp > 0 or quest.reward_items:
                rewards_header = font.render("Rewards:", True, Colors.ACCENT)
                surface.blit(rewards_header, (details_rect.left + padding, y))
                y += Layout.LINE_HEIGHT_COMPACT + 4

                if quest.reward_gold > 0:
                    rewards.append(f"{quest.reward_gold} Gold")
                if quest.reward_exp > 0:
                    rewards.append(f"{quest.reward_exp} EXP")
                for item_id, qty in quest.reward_items.items():
                    item_name = item_id.replace("_", " ").title()
                    rewards.append(f"{item_name} x{qty}")

        if rewards:
            reward_text = ", ".join(rewards)
            reward_surface = small_font.render(reward_text[:40], True, Colors.TEXT_HIGHLIGHT)
            surface.blit(reward_surface, (details_rect.left + padding, y))

    def _wrap_text(self, text: str, font: pygame.font.Font, max_width: int) -> List[str]:
        """Wrap text to fit within max_width."""
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

    def _format_filter_label(self, key: str) -> str:
        """Convert filter keys to readable labels."""
        if key == "all":
            return "All"
        return key.replace("_", " ").title()

    def _get_difficulty_color(self, difficulty: Optional[str]) -> Tuple[int, int, int]:
        """Return themed color for difficulty text."""
        mapping = {
            "easy": Colors.TEXT_SUCCESS,
            "normal": Colors.TEXT_PRIMARY,
            "challenging": Colors.TEXT_INFO,
            "hard": Colors.TEXT_ERROR,
            "epic": Colors.TEXT_HIGHLIGHT,
            "story": Colors.TEXT_SECONDARY,
            "tutorial": Colors.TEXT_SECONDARY,
        }
        return mapping.get((difficulty or "normal").lower(), Colors.TEXT_PRIMARY)

"""Achievement popup notification system."""

import math
import pygame
from typing import Any, Dict, List, Optional, Tuple

from core.achievements import Achievement, AchievementRarity


# Rarity colors for achievement popups
RARITY_COLORS: Dict[AchievementRarity, Tuple[int, int, int]] = {
    AchievementRarity.COMMON: (200, 200, 200),      # Silver/Gray
    AchievementRarity.UNCOMMON: (100, 200, 100),    # Green
    AchievementRarity.RARE: (100, 150, 255),        # Blue
    AchievementRarity.EPIC: (200, 100, 255),        # Purple
    AchievementRarity.LEGENDARY: (255, 200, 50),    # Gold
}

# Rarity border colors (brighter)
RARITY_BORDER_COLORS: Dict[AchievementRarity, Tuple[int, int, int]] = {
    AchievementRarity.COMMON: (255, 255, 255),
    AchievementRarity.UNCOMMON: (150, 255, 150),
    AchievementRarity.RARE: (150, 200, 255),
    AchievementRarity.EPIC: (255, 150, 255),
    AchievementRarity.LEGENDARY: (255, 255, 100),
}


class AchievementPopup:
    """A single achievement popup notification."""

    def __init__(
        self,
        achievement: Achievement,
        screen_width: int,
        duration: float = 4.0,
        slide_duration: float = 0.3,
    ):
        self.achievement = achievement
        self.screen_width = screen_width
        self.duration = duration
        self.slide_duration = slide_duration

        # Animation state
        self.timer: float = 0.0
        self.finished: bool = False

        # Popup dimensions
        self.width = 300
        self.height = 70
        self.padding = 10

        # Position (starts off-screen to the right)
        self.target_x = screen_width - self.width - 20
        self.current_x = screen_width + 10
        self.y = 20

    def update(self, dt: float) -> None:
        """Update popup animation."""
        self.timer += dt

        if self.timer >= self.duration:
            self.finished = True
            return

        # Slide in phase
        if self.timer < self.slide_duration:
            progress = self.timer / self.slide_duration
            # Ease out
            progress = 1 - (1 - progress) ** 2
            self.current_x = self.screen_width + 10 - (self.screen_width + 10 - self.target_x) * progress

        # Slide out phase
        elif self.timer > self.duration - self.slide_duration:
            remaining = self.duration - self.timer
            progress = remaining / self.slide_duration
            # Ease in
            progress = progress ** 2
            self.current_x = self.target_x + (self.screen_width + 10 - self.target_x) * (1 - progress)

        else:
            self.current_x = self.target_x

    def draw(self, surface: pygame.Surface, font: pygame.font.Font, small_font: Optional[pygame.font.Font] = None) -> None:
        """Draw the popup."""
        if self.finished:
            return

        if small_font is None:
            small_font = font

        x = int(self.current_x)
        y = self.y

        rarity = self.achievement.rarity
        bg_color = (30, 30, 40)
        border_color = RARITY_BORDER_COLORS.get(rarity, (255, 255, 255))
        text_color = RARITY_COLORS.get(rarity, (255, 255, 255))

        # Draw background with border
        rect = pygame.Rect(x, y, self.width, self.height)

        # Shadow
        shadow_rect = rect.move(3, 3)
        pygame.draw.rect(surface, (0, 0, 0, 100), shadow_rect, border_radius=8)

        # Background
        pygame.draw.rect(surface, bg_color, rect, border_radius=8)

        # Border (animated glow for legendary)
        border_width = 2
        if rarity == AchievementRarity.LEGENDARY:
            # Pulsing glow effect
            import math
            glow_intensity = int(128 + 127 * math.sin(self.timer * 4))
            glow_color = (
                min(255, border_color[0] + glow_intensity // 4),
                min(255, border_color[1] + glow_intensity // 4),
                min(255, border_color[2]),
            )
            pygame.draw.rect(surface, glow_color, rect, border_width, border_radius=8)
        else:
            pygame.draw.rect(surface, border_color, rect, border_width, border_radius=8)

        # Achievement icon placeholder (trophy symbol)
        icon_size = 40
        icon_x = x + self.padding
        icon_y = y + (self.height - icon_size) // 2
        icon_rect = pygame.Rect(icon_x, icon_y, icon_size, icon_size)
        pygame.draw.rect(surface, border_color, icon_rect, border_radius=4)

        # Draw a simple trophy shape
        trophy_color = (255, 215, 0) if rarity == AchievementRarity.LEGENDARY else (200, 200, 200)
        cx, cy = icon_x + icon_size // 2, icon_y + icon_size // 2
        # Trophy cup
        pygame.draw.polygon(surface, trophy_color, [
            (cx - 12, cy - 10),
            (cx + 12, cy - 10),
            (cx + 8, cy + 2),
            (cx - 8, cy + 2),
        ])
        # Trophy base
        pygame.draw.rect(surface, trophy_color, (cx - 6, cy + 2, 12, 4))
        pygame.draw.rect(surface, trophy_color, (cx - 8, cy + 6, 16, 4))

        # Text area
        text_x = icon_x + icon_size + self.padding
        text_y = y + 8

        # "Achievement Unlocked!" header
        header_text = "Achievement Unlocked!"
        header_surface = small_font.render(header_text, True, (180, 180, 180))
        surface.blit(header_surface, (text_x, text_y))

        # Achievement name
        name_y = text_y + 18
        name_surface = font.render(self.achievement.name, True, text_color)
        # Truncate if too long
        max_width = self.width - icon_size - self.padding * 3
        if name_surface.get_width() > max_width:
            # Truncate with ellipsis
            truncated_name = self.achievement.name
            while name_surface.get_width() > max_width and len(truncated_name) > 3:
                truncated_name = truncated_name[:-4] + "..."
                name_surface = font.render(truncated_name, True, text_color)
        surface.blit(name_surface, (text_x, name_y))

        # Rarity text
        rarity_y = name_y + 20
        rarity_text = rarity.value.capitalize()
        rarity_surface = small_font.render(rarity_text, True, border_color)
        surface.blit(rarity_surface, (text_x, rarity_y))


class AchievementPopupManager:
    """Manages multiple achievement popup notifications."""

    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.popups: List[AchievementPopup] = []
        self.popup_spacing = 80  # Vertical spacing between popups
        self.max_visible = 3  # Maximum popups visible at once

    def add_popup(self, achievement: Achievement) -> None:
        """Add a new achievement popup."""
        popup = AchievementPopup(achievement, self.screen_width)

        # Offset Y position based on existing popups
        popup.y = 20 + len(self.popups) * self.popup_spacing

        # Limit visible popups
        if len(self.popups) >= self.max_visible:
            # Remove oldest popup
            self.popups.pop(0)
            # Adjust Y positions
            for i, p in enumerate(self.popups):
                p.y = 20 + i * self.popup_spacing

        self.popups.append(popup)

    def update(self, dt: float) -> None:
        """Update all popups."""
        # Update each popup
        for popup in self.popups:
            popup.update(dt)

        # Remove finished popups and adjust positions
        finished_indices = [i for i, p in enumerate(self.popups) if p.finished]
        for i in reversed(finished_indices):
            self.popups.pop(i)

        # Smoothly adjust Y positions
        for i, popup in enumerate(self.popups):
            target_y = 20 + i * self.popup_spacing
            if popup.y != target_y:
                diff = target_y - popup.y
                popup.y += diff * min(1.0, dt * 5)

    def draw(self, surface: pygame.Surface, font: pygame.font.Font, small_font: Optional[pygame.font.Font] = None) -> None:
        """Draw all popups."""
        for popup in self.popups:
            popup.draw(surface, font, small_font)

    def has_popups(self) -> bool:
        """Check if there are any active popups."""
        return len(self.popups) > 0


class AchievementListUI:
    """UI for displaying the full achievement list."""

    def __init__(
        self,
        achievements: List[Achievement],
        screen_width: int,
        screen_height: int,
        achievement_manager: Optional[Any] = None,
    ):
        from core.achievements import AchievementCategory
        self.achievements = achievements
        self.all_achievements = achievements  # Keep all for filtering
        self.achievement_manager = achievement_manager
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.scroll_offset = 0
        self.selected_index = 0
        self.item_height = 60
        self.visible_items = (screen_height - 200) // self.item_height  # Reserve space for header/tabs
        self.anim_time = 0.0  # Animation timer for selection effects

        # Category filtering
        self.categories = [
            AchievementCategory.STORY,
            AchievementCategory.COMBAT,
            AchievementCategory.EXPLORATION,
            AchievementCategory.ACTIVITIES,
            AchievementCategory.CHALLENGE,
            AchievementCategory.SECRET,
        ]
        self.current_category: Optional[AchievementCategory] = None  # None = all
        self.category_tab_height = 40

    def set_category(self, category: Optional[Any]) -> None:
        """Filter achievements by category."""
        from core.achievements import AchievementCategory
        self.current_category = category
        if category is None:
            self.achievements = self.all_achievements
        else:
            self.achievements = [a for a in self.all_achievements if a.category == category]
        self.selected_index = 0
        self.scroll_offset = 0

    def move_selection(self, delta: int) -> None:
        """Move selection up or down."""
        if not self.achievements:
            return

        self.selected_index = max(0, min(len(self.achievements) - 1, self.selected_index + delta))

        # Adjust scroll to keep selection visible
        if self.selected_index < self.scroll_offset:
            self.scroll_offset = self.selected_index
        elif self.selected_index >= self.scroll_offset + self.visible_items:
            self.scroll_offset = self.selected_index - self.visible_items + 1

    def get_selected(self) -> Optional[Achievement]:
        """Get the currently selected achievement."""
        if not self.achievements or self.selected_index >= len(self.achievements):
            return None
        return self.achievements[self.selected_index]

    def draw(
        self,
        surface: pygame.Surface,
        font: pygame.font.Font,
        small_font: Optional[pygame.font.Font] = None,
        layout: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Draw the achievement list with optional layout overrides."""
        from core.achievements import AchievementCategory

        if small_font is None:
            small_font = font
        layout = layout or {}

        header_pos = layout.get("header_pos", (50, 50))
        stats_pos = layout.get("stats_pos", (50, 75))
        tab_origin = layout.get("tab_origin", (50, 100))
        tab_width = layout.get("tab_width", 120)
        tab_height = layout.get("tab_height", 30)
        tab_spacing = layout.get("tab_spacing", 5)
        list_rect = layout.get(
            "list_rect",
            pygame.Rect(20, 150, self.screen_width - 40, self.screen_height - 200),
        )

        self._update_visible_items(list_rect.height)

        unlocked_count = sum(1 for a in self.achievements if a.unlocked)
        header_text = f"Achievements ({unlocked_count}/{len(self.achievements)})"
        header_surface = font.render(header_text, True, (255, 255, 255))
        surface.blit(header_surface, header_pos)

        if self.achievement_manager:
            total_points = self.achievement_manager.get_total_points()
            max_points = self.achievement_manager.get_max_points()
            points_text = f"Points: {total_points} / {max_points}"
            points_surface = small_font.render(points_text, True, (200, 200, 100))
            surface.blit(points_surface, stats_pos)

        tab_x = tab_origin[0]
        tab_y = tab_origin[1]
        for category in self.categories:
            is_active = self.current_category == category
            tab_rect = pygame.Rect(tab_x, tab_y, tab_width, tab_height)
            bg_color = (80, 80, 100) if is_active else (50, 50, 60)
            border_color = (150, 150, 200) if is_active else (70, 70, 80)
            pygame.draw.rect(surface, bg_color, tab_rect, border_radius=4)
            pygame.draw.rect(surface, border_color, tab_rect, 2, border_radius=4)

            category_name = category.value.capitalize()
            tab_text_surface = small_font.render(category_name, True, (255, 255, 255))
            text_x = tab_x + (tab_width - tab_text_surface.get_width()) // 2
            text_y = tab_y + (tab_height - tab_text_surface.get_height()) // 2
            surface.blit(tab_text_surface, (text_x, text_y))

            tab_x += tab_width + tab_spacing

        is_all_active = self.current_category is None
        all_tab_rect = pygame.Rect(tab_x, tab_y, tab_width, tab_height)
        pygame.draw.rect(
            surface,
            (80, 80, 100) if is_all_active else (50, 50, 60),
            all_tab_rect,
            border_radius=4,
        )
        pygame.draw.rect(
            surface,
            (150, 150, 200) if is_all_active else (70, 70, 80),
            all_tab_rect,
            2,
            border_radius=4,
        )
        all_text_surface = small_font.render("All", True, (255, 255, 255))
        surface.blit(
            all_text_surface,
            (
                all_tab_rect.x + (tab_width - all_text_surface.get_width()) // 2,
                all_tab_rect.y + (tab_height - all_text_surface.get_height()) // 2,
            ),
        )

        if self.achievement_manager:
            completion_by_cat = self.achievement_manager.get_completion_by_category()
            progress_y = tab_y + tab_height + 8
            tab_x = tab_origin[0]
            for category in self.categories:
                cat_key = category.value
                if cat_key in completion_by_cat:
                    unlocked, total = completion_by_cat[cat_key]
                    if total > 0:
                        progress = unlocked / total
                        bar_width = tab_width - 10
                        bar_height = 4
                        bar_rect = pygame.Rect(tab_x + 5, progress_y, bar_width, bar_height)
                        pygame.draw.rect(surface, (40, 40, 50), bar_rect, border_radius=2)
                        fill_width = int(bar_width * progress)
                        if fill_width > 0:
                            fill_color = (100, 200, 100) if progress == 1.0 else (100, 150, 255)
                            fill_rect = pygame.Rect(
                                bar_rect.x,
                                bar_rect.y,
                                fill_width,
                                bar_height,
                            )
                            pygame.draw.rect(surface, fill_color, fill_rect, border_radius=2)
                tab_x += tab_width + tab_spacing

        start_y = list_rect.top + 8
        item_x = list_rect.left + 10
        for i in range(
            self.scroll_offset,
            min(self.scroll_offset + self.visible_items, len(self.achievements)),
        ):
            achievement = self.achievements[i]
            y = start_y + (i - self.scroll_offset) * self.item_height
            is_selected = i == self.selected_index
            self._draw_achievement_item(
                surface,
                achievement,
                item_x,
                y,
                is_selected,
                font,
                small_font,
                width_override=max(80, list_rect.width - 20),
            )

        arrow_x = list_rect.right - 30
        if self.scroll_offset > 0:
            arrow_up = font.render("▲", True, (200, 200, 200))
            surface.blit(arrow_up, (arrow_x, list_rect.top - 20))

        if self.scroll_offset + self.visible_items < len(self.achievements):
            arrow_down = font.render("▼", True, (200, 200, 200))
            surface.blit(arrow_down, (arrow_x, list_rect.bottom - 10))

    def _update_visible_items(self, list_height: int) -> None:
        """Recalculate the number of visible rows based on layout."""
        available_height = max(1, list_height - 20)
        new_visible = max(1, available_height // self.item_height)
        if new_visible != self.visible_items:
            self.visible_items = new_visible
            max_offset = max(0, len(self.achievements) - self.visible_items)
            self.scroll_offset = min(self.scroll_offset, max_offset)

    def _draw_achievement_item(
        self,
        surface: pygame.Surface,
        achievement: Achievement,
        x: int,
        y: int,
        selected: bool,
        font: pygame.font.Font,
        small_font: pygame.font.Font,
        width_override: Optional[int] = None,
    ) -> None:
        """Draw a single achievement item."""
        width = width_override if width_override is not None else self.screen_width - 60
        height = self.item_height - 5

        rarity = achievement.rarity
        border_color = RARITY_BORDER_COLORS.get(rarity, (255, 255, 255))

        # Background
        bg_color = (50, 50, 60) if selected else (30, 30, 40)
        if not achievement.unlocked:
            bg_color = (20, 20, 25)

        rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(surface, bg_color, rect, border_radius=6)

        # Border for selected (with pulse effect)
        if selected:
            pulse = 0.5 + 0.5 * math.sin(self.anim_time * 4)  # Gentle pulse
            pulse_color = tuple(int(c * (0.7 + 0.3 * pulse)) for c in border_color)
            pygame.draw.rect(surface, pulse_color, rect, 2, border_radius=6)

        # Icon area
        icon_size = 40
        icon_x = x + 10
        icon_y = y + (height - icon_size) // 2

        if achievement.unlocked:
            # Colored icon background
            icon_rect = pygame.Rect(icon_x, icon_y, icon_size, icon_size)
            pygame.draw.rect(surface, border_color, icon_rect, border_radius=4)
            # Trophy
            cx, cy = icon_x + icon_size // 2, icon_y + icon_size // 2
            trophy_color = (255, 215, 0) if rarity == AchievementRarity.LEGENDARY else (40, 40, 50)
            pygame.draw.polygon(surface, trophy_color, [
                (cx - 10, cy - 8),
                (cx + 10, cy - 8),
                (cx + 6, cy + 2),
                (cx - 6, cy + 2),
            ])
            pygame.draw.rect(surface, trophy_color, (cx - 5, cy + 2, 10, 3))
            pygame.draw.rect(surface, trophy_color, (cx - 7, cy + 5, 14, 3))
        else:
            # Locked icon
            icon_rect = pygame.Rect(icon_x, icon_y, icon_size, icon_size)
            pygame.draw.rect(surface, (60, 60, 70), icon_rect, border_radius=4)
            # Lock symbol
            lock_color = (100, 100, 110)
            cx, cy = icon_x + icon_size // 2, icon_y + icon_size // 2
            pygame.draw.rect(surface, lock_color, (cx - 8, cy - 2, 16, 12), border_radius=2)
            pygame.draw.arc(surface, lock_color, (cx - 6, cy - 12, 12, 12), 0, 3.14, 2)

        # Text
        text_x = icon_x + icon_size + 15

        # Name
        name_color = RARITY_COLORS.get(rarity, (200, 200, 200)) if achievement.unlocked else (100, 100, 100)
        name_text = achievement.get_display_name()
        name_surface = font.render(name_text, True, name_color)
        surface.blit(name_surface, (text_x, y + 8))

        # Description
        desc_color = (180, 180, 180) if achievement.unlocked else (80, 80, 80)
        desc_text = achievement.get_display_description()
        # Truncate if too long
        max_desc_width = width - icon_size - 40
        desc_surface = small_font.render(desc_text, True, desc_color)
        if desc_surface.get_width() > max_desc_width:
            while desc_surface.get_width() > max_desc_width and len(desc_text) > 3:
                desc_text = desc_text[:-4] + "..."
                desc_surface = small_font.render(desc_text, True, desc_color)
        surface.blit(desc_surface, (text_x, y + 28))

        # Points display
        if achievement.unlocked:
            points_text = f"+{achievement.points} pts"
            points_surface = small_font.render(points_text, True, (200, 200, 100))
            points_x = width - 80
            surface.blit(points_surface, (x + points_x, y + 8))

        # Progress bar for incomplete achievements
        if not achievement.unlocked and achievement.target_count > 1:
            progress = achievement.get_progress_percent()
            bar_width = 100
            bar_height = 6
            bar_x = width - bar_width - 20
            bar_y = y + height // 2 - bar_height // 2

            # Background
            pygame.draw.rect(surface, (40, 40, 50), (x + bar_x, bar_y, bar_width, bar_height), border_radius=3)
            # Fill
            fill_width = int(bar_width * progress)
            if fill_width > 0:
                pygame.draw.rect(surface, border_color, (x + bar_x, bar_y, fill_width, bar_height), border_radius=3)

            # Progress text
            progress_text = f"{achievement.current_count}/{achievement.target_count}"
            progress_surface = small_font.render(progress_text, True, (150, 150, 150))
            surface.blit(progress_surface, (x + bar_x + bar_width + 5, bar_y - 2))

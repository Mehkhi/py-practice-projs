"""Completion tracking scene showing overall game progress."""

from typing import Dict, Optional, TYPE_CHECKING

import pygame

from .base_menu_scene import BaseMenuScene
from .assets import AssetManager
from .theme import Colors, Fonts, Layout
from core.tutorial_system import TipTrigger

if TYPE_CHECKING:
    from .scene import SceneManager


class CompletionScene(BaseMenuScene):
    """Shows overall game completion progress across all systems."""

    def __init__(
        self,
        manager: Optional["SceneManager"],
        assets: Optional[AssetManager] = None,
        scale: int = 2,
    ):
        super().__init__(manager, assets, scale)
        self.completion_data: Dict[str, Dict] = {}
        self.overall_percent = 0.0
        self.celebration_active = False
        self.celebration_timer = 0.0
        self._near_completion_triggered = False

    def calculate_completion(self) -> Dict[str, Dict]:
        """Calculate completion for each system."""
        if not self.manager:
            return {}

        data: Dict[str, Dict] = {}

        # Main story
        post_game_manager = self.get_manager_attr(
            "post_game_manager", "calculate_completion_main_story"
        )
        if post_game_manager:
            data["main_story"] = {
                "label": "Main Story",
                "current": 1 if post_game_manager.state.final_boss_defeated else 0,
                "total": 1,
            }
        else:
            data["main_story"] = {"label": "Main Story", "current": 0, "total": 1}

        # Achievements
        achievement_manager = self.get_manager_attr(
            "achievement_manager", "calculate_completion_achievements"
        )
        if achievement_manager:
            unlocked = achievement_manager.get_unlocked_count()
            total = len(achievement_manager.achievements)
            data["achievements"] = {
                "label": "Achievements",
                "current": unlocked,
                "total": total,
            }
        else:
            data["achievements"] = {"label": "Achievements", "current": 0, "total": 1}

        # Secret bosses
        secret_boss_manager = self.get_manager_attr(
            "secret_boss_manager", "calculate_completion_secret_bosses"
        )
        if secret_boss_manager:
            defeated = len(secret_boss_manager.defeated)
            total = len(secret_boss_manager.bosses)
            data["secret_bosses"] = {
                "label": "Secret Bosses",
                "current": defeated,
                "total": total,
            }
        else:
            data["secret_bosses"] = {"label": "Secret Bosses", "current": 0, "total": 1}

        # Challenge dungeons
        challenge_manager = self.get_manager_attr(
            "challenge_dungeon_manager", "calculate_completion_challenges"
        )
        if challenge_manager:
            cleared = sum(1 for p in challenge_manager.progress.values() if p.cleared)
            total = len(challenge_manager.dungeons)
            data["challenge_dungeons"] = {
                "label": "Challenge Dungeons",
                "current": cleared,
                "total": total,
            }
        else:
            data["challenge_dungeons"] = {"label": "Challenge Dungeons", "current": 0, "total": 1}

        # Fish species
        fishing_system = self.get_manager_attr(
            "fishing_system", "calculate_completion_fishing"
        )
        if fishing_system:
            caught = len(fishing_system.player_records)
            total = len(fishing_system.fish_db)
            data["fish_species"] = {
                "label": "Fish Caught",
                "current": caught,
                "total": total,
            }
        else:
            data["fish_species"] = {"label": "Fish Caught", "current": 0, "total": 1}

        # Puzzles
        puzzle_manager = self.get_manager_attr(
            "puzzle_manager", "calculate_completion_puzzles"
        )
        if puzzle_manager:
            solved = sum(1 for p in puzzle_manager.puzzles.values() if p.solved)
            total = len(puzzle_manager.puzzles)
            data["puzzles"] = {
                "label": "Puzzles Solved",
                "current": solved,
                "total": total,
            }
        else:
            data["puzzles"] = {"label": "Puzzles Solved", "current": 0, "total": 1}

        # Brain teasers
        brain_teaser_manager = self.get_manager_attr(
            "brain_teaser_manager", "calculate_completion_brain_teasers"
        )
        if brain_teaser_manager:
            solved = len(brain_teaser_manager.solved_teasers)
            total = len(brain_teaser_manager.teasers)
            data["brain_teasers"] = {
                "label": "Brain Teasers",
                "current": solved,
                "total": total,
            }
        else:
            data["brain_teasers"] = {"label": "Brain Teasers", "current": 0, "total": 1}

        return data

    def update(self, dt: float) -> None:
        """Update scene state."""
        self.completion_data = self.calculate_completion()

        # Calculate overall completion percentage
        if self.completion_data:
            total_current = sum(d["current"] for d in self.completion_data.values())
            total_max = sum(d["total"] for d in self.completion_data.values())
            self.overall_percent = (total_current / total_max * 100) if total_max > 0 else 0.0
        else:
            self.overall_percent = 0.0

        if self.overall_percent >= 90.0 and not self._near_completion_triggered:
            tutorial_manager = self.get_manager_attr(
                "tutorial_manager", "calculate_completion_near_complete"
            )
            if tutorial_manager:
                tutorial_manager.trigger_tip(TipTrigger.NEAR_COMPLETION)
            self._near_completion_triggered = True

        # Check for 100% completion
        if self.overall_percent >= 100.0 and not self.celebration_active:
            self.celebration_active = True
            self.celebration_timer = 0.0

        if self.celebration_active:
            self.celebration_timer += dt

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle input events."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.manager.pop()

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the completion scene."""
        width, height = surface.get_size()

        # Draw semi-transparent overlay
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        overlay.fill((15, 15, 25, 200))
        surface.blit(overlay, (0, 0))

        # Get fonts
        font = self.assets.get_font(Fonts.DEFAULT, Fonts.SIZE_BODY)
        title_font = self.assets.get_font(Fonts.LARGE, Fonts.SIZE_TITLE) or font
        small_font = self.assets.get_font(Fonts.SMALL, Fonts.SIZE_SMALL)

        # Draw title
        title_text = "Game Completion"
        title_surface = title_font.render(title_text, True, Colors.TEXT_PRIMARY)
        title_rect = title_surface.get_rect(center=(width // 2, 50))
        surface.blit(title_surface, title_rect)

        # Draw overall completion percentage
        percent_text = f"Overall: {self.overall_percent:.1f}%"
        percent_surface = font.render(percent_text, True, Colors.TEXT_HIGHLIGHT)
        percent_rect = percent_surface.get_rect(center=(width // 2, 90))
        surface.blit(percent_surface, percent_rect)

        # Draw 100% celebration
        if self.celebration_active:
            import math
            pulse = 0.5 + 0.5 * math.sin(self.celebration_timer * 3)
            celebration_color = (
                int(255 * pulse),
                int(255 * pulse),
                int(100 * pulse),
            )
            celebration_text = "100% COMPLETE!"
            celebration_font = self.assets.get_font(Fonts.LARGE, Fonts.SIZE_TITLE + 10) or title_font
            celebration_surface = celebration_font.render(celebration_text, True, celebration_color)
            celebration_rect = celebration_surface.get_rect(center=(width // 2, 130))
            surface.blit(celebration_surface, celebration_rect)

        # Draw main panel
        panel_rect = pygame.Rect(50, 160, width - 100, height - 220)
        if self.panel:
            self.panel.draw(surface, panel_rect)
        else:
            pygame.draw.rect(surface, Colors.BG_PANEL, panel_rect, border_radius=Layout.CORNER_RADIUS)
            pygame.draw.rect(surface, Colors.BORDER, panel_rect, Layout.BORDER_WIDTH, border_radius=Layout.CORNER_RADIUS)

        # Draw completion items
        y_offset = 180
        item_height = 50
        item_spacing = 10

        for key, data in self.completion_data.items():
            label = data["label"]
            current = data["current"]
            total = data["total"]
            percent = (current / total * 100) if total > 0 else 0.0

            # Draw label
            label_surface = font.render(label, True, Colors.TEXT_PRIMARY)
            surface.blit(label_surface, (70, y_offset))

            # Draw count
            count_text = f"{current} / {total}"
            count_surface = small_font.render(count_text, True, Colors.TEXT_SECONDARY)
            count_x = width - 200
            surface.blit(count_surface, (count_x, y_offset + 5))

            # Draw progress bar
            bar_x = 70
            bar_y = y_offset + 25
            bar_width = width - 280
            bar_height = 20

            # Background
            pygame.draw.rect(surface, (40, 40, 50), (bar_x, bar_y, bar_width, bar_height), border_radius=4)

            # Fill
            fill_width = int(bar_width * (current / total)) if total > 0 else 0
            if fill_width > 0:
                fill_color = (100, 200, 100) if percent == 100.0 else (100, 150, 255)
                pygame.draw.rect(surface, fill_color, (bar_x, bar_y, fill_width, bar_height), border_radius=4)

            # Percentage text on bar
            percent_text = f"{percent:.1f}%"
            percent_surface = small_font.render(percent_text, True, Colors.TEXT_PRIMARY)
            percent_x = bar_x + (bar_width - percent_surface.get_width()) // 2
            percent_y = bar_y + (bar_height - percent_surface.get_height()) // 2
            surface.blit(percent_surface, (percent_x, percent_y))

            y_offset += item_height + item_spacing

        # Draw help text
        help_text = "ESC: Close"
        help_surface = small_font.render(help_text, True, Colors.TEXT_SECONDARY)
        help_rect = help_surface.get_rect(center=(width // 2, height - 30))
        surface.blit(help_surface, help_rect)

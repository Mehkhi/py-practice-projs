"""Statistics scene for displaying mini-game and activity statistics."""

import pygame
from typing import Optional, Dict, List, TYPE_CHECKING

from .base_menu_scene import BaseMenuScene
from .assets import AssetManager
from .ui import Menu, draw_contextual_help
from .theme import Colors, Fonts, Layout

if TYPE_CHECKING:
    from .scene import SceneManager
    from core.fishing import FishingSystem
    from core.gambling import GamblingManager
    from core.arena import ArenaManager
    from core.puzzles import PuzzleManager
    from core.brain_teasers import BrainTeaserManager


class StatisticsScene(BaseMenuScene):
    """Displays player statistics for all activities."""

    def __init__(
        self,
        manager: Optional["SceneManager"],
        fishing_system: Optional["FishingSystem"] = None,
        gambling_manager: Optional["GamblingManager"] = None,
        arena_manager: Optional["ArenaManager"] = None,
        puzzle_manager: Optional["PuzzleManager"] = None,
        brain_teaser_manager: Optional["BrainTeaserManager"] = None,
        assets: Optional[AssetManager] = None,
        scale: int = 2,
    ):
        super().__init__(manager, assets, scale)
        self.fishing_system = fishing_system
        self.gambling_manager = gambling_manager
        self.arena_manager = arena_manager
        self.puzzle_manager = puzzle_manager
        self.brain_teaser_manager = brain_teaser_manager

        # Get managers from scene manager if not provided
        if not self.fishing_system:
            self.fishing_system = self.get_manager_attr(
                "fishing_system", "statistics_scene_init"
            )
        if not self.gambling_manager:
            self.gambling_manager = self.get_manager_attr(
                "gambling_manager", "statistics_scene_init"
            )
        if not self.arena_manager:
            self.arena_manager = self.get_manager_attr(
                "arena_manager", "statistics_scene_init"
            )
        if not self.brain_teaser_manager:
            self.brain_teaser_manager = self.get_manager_attr(
                "brain_teaser_manager", "statistics_scene_init"
            )
        # Puzzle manager is on world_scene, try to get it
        if not self.puzzle_manager and self.manager:
            current_scene = self.manager.current()
            self.puzzle_manager = getattr(current_scene, 'puzzle_manager', None)

        # Build statistics data
        self.stats_data = self._build_statistics()
        self.categories = list(self.stats_data.keys())
        self.current_category_index = 0
        self.scroll_offset = 0
        self.max_items_per_page = 12

    def _build_statistics(self) -> Dict[str, List[tuple]]:
        """Build statistics data from all managers."""
        stats: Dict[str, List[tuple]] = {}

        # FISHING STATISTICS
        fishing_stats: List[tuple] = []
        if self.fishing_system:
            records = self.fishing_system.player_records
            total_caught = getattr(self.fishing_system, "total_catches", len(records))
            unique_species = len(set(caught.fish.fish_id for caught in records.values()))

            fishing_stats.append(("Total Fish Caught", str(total_caught)))
            fishing_stats.append(("Unique Species", str(unique_species)))

            if records:
                # Biggest catch
                biggest = max(records.values(), key=lambda c: c.size)
                fishing_stats.append(("Biggest Catch", f"{biggest.fish.name} ({biggest.size:.1f})"))

                # Rarest catch
                rarest = None
                for caught in records.values():
                    if caught.fish.rarity.value == "legendary":
                        if rarest is None or caught.size > rarest.size:
                            rarest = caught
                if rarest:
                    fishing_stats.append(("Rarest Catch", f"{rarest.fish.name} (Legendary)"))
                else:
                    fishing_stats.append(("Rarest Catch", "None"))

                # Favorite spot if tracked
                catches_per_spot = getattr(self.fishing_system, "catches_per_spot", {})
                if catches_per_spot:
                    favorite_spot = max(catches_per_spot.items(), key=lambda item: item[1])[0]
                    fishing_stats.append(("Favorite Spot", favorite_spot))
                else:
                    fishing_stats.append(("Favorite Spot", "N/A"))
            else:
                fishing_stats.append(("Biggest Catch", "None"))
                fishing_stats.append(("Rarest Catch", "None"))
                fishing_stats.append(("Favorite Spot", "N/A"))
        else:
            fishing_stats.append(("Fishing System", "Not Available"))
        stats["FISHING"] = fishing_stats

        # GAMBLING STATISTICS
        gambling_stats: List[tuple] = []
        if self.gambling_manager:
            s = self.gambling_manager.stats
            gambling_stats.append(("Total Wagered", f"{s.total_wagered} gold"))
            gambling_stats.append(("Total Won", f"{s.total_won} gold"))
            gambling_stats.append(("Total Lost", f"{s.total_lost} gold"))
            net = s.total_won - s.total_wagered
            net_str = f"{net:+d} gold" if net != 0 else "0 gold"
            gambling_stats.append(("Net Profit/Loss", net_str))
            gambling_stats.append(("Games Played", str(s.games_played)))
            gambling_stats.append(("Biggest Win", f"{s.biggest_win} gold"))
            gambling_stats.append(("Biggest Loss", f"{s.biggest_loss} gold"))
            gambling_stats.append(("Best Streak", f"{s.best_streak} wins"))
            gambling_stats.append(("Worst Streak", f"{abs(s.worst_streak)} losses"))
        else:
            gambling_stats.append(("Gambling System", "Not Available"))
        stats["GAMBLING"] = gambling_stats

        # ARENA STATISTICS
        arena_stats: List[tuple] = []
        if self.arena_manager:
            history = self.arena_manager.match_history
            matches_watched = len(history)
            resolved_bets = [bet for entry in history for bet in entry.get("bets", [])]
            active_bets = list(self.arena_manager.active_bets)
            bets_placed = len(resolved_bets) + len(active_bets)
            bets_won = sum(1 for bet in resolved_bets if bet.get("winnings", 0) > 0)
            bets_lost = len(resolved_bets) - bets_won
            total_wagered = sum(bet.get("amount", 0) for bet in resolved_bets) + sum(b.amount for b in active_bets)
            net_profit = sum(bet.get("winnings", 0) - bet.get("amount", 0) for bet in resolved_bets)
            arena_stats.append(("Matches Watched", str(matches_watched)))
            arena_stats.append(("Bets Placed", str(bets_placed)))
            arena_stats.append(("Bets Won", str(bets_won)))
            arena_stats.append(("Bets Lost", str(max(bets_lost, 0))))
            arena_stats.append(("Net Profit/Loss", f"{net_profit:+d} gold"))
        else:
            arena_stats.append(("Arena System", "Not Available"))
        stats["ARENA"] = arena_stats

        # PUZZLES STATISTICS
        puzzle_stats: List[tuple] = []
        if self.puzzle_manager:
            puzzles_solved = sum(1 for p in self.puzzle_manager.puzzles.values() if p.solved)
            total_puzzles = len(self.puzzle_manager.puzzles)
            puzzle_stats.append(("Dungeon Puzzles Solved", f"{puzzles_solved}/{total_puzzles}"))
            # Perfect clears would need reset tracking
            puzzle_stats.append(("Perfect Clears", "N/A"))
        else:
            puzzle_stats.append(("Puzzle System", "Not Available"))
        stats["PUZZLES"] = puzzle_stats

        # BRAIN TEASERS STATISTICS
        brain_teaser_stats: List[tuple] = []
        if self.brain_teaser_manager:
            solved = len(self.brain_teaser_manager.solved_teasers)
            total = len(self.brain_teaser_manager.teasers)
            brain_teaser_stats.append(("Brain Teasers Completed", f"{solved}/{total}"))
        else:
            brain_teaser_stats.append(("Brain Teaser System", "Not Available"))
        stats["BRAIN TEASERS"] = brain_teaser_stats

        return stats

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle input events."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.manager.pop()
            elif event.key == pygame.K_UP:
                if self.current_category_index > 0:
                    self.current_category_index -= 1
                    self.scroll_offset = 0
            elif event.key == pygame.K_DOWN:
                if self.current_category_index < len(self.categories) - 1:
                    self.current_category_index += 1
                    self.scroll_offset = 0

    def update(self, dt: float) -> None:
        """Update scene state."""
        pass

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the statistics scene."""
        width, height = surface.get_size()

        # Draw overlay
        self.draw_overlay(surface)

        # Draw title
        title_font = self.assets.get_font(Fonts.LARGE, Fonts.SIZE_TITLE)
        title_text = title_font.render("STATISTICS", True, Colors.TEXT_PRIMARY)
        title_rect = title_text.get_rect(center=(width // 2, 40))
        surface.blit(title_text, title_rect)

        # Draw category panel
        panel_x = 40
        panel_y = 80
        panel_width = width - 80
        panel_height = height - 160

        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        if self.panel:
            self.panel.draw(surface, panel_rect)
        else:
            pygame.draw.rect(surface, Colors.BG_PANEL, panel_rect, border_radius=Layout.CORNER_RADIUS)
            pygame.draw.rect(surface, Colors.BORDER, panel_rect, Layout.BORDER_WIDTH, border_radius=Layout.CORNER_RADIUS)

        # Draw category name
        body_font = self.assets.get_font(Fonts.DEFAULT, Fonts.SIZE_BODY)
        small_font = self.assets.get_font(Fonts.SMALL, Fonts.SIZE_SMALL)

        current_category = self.categories[self.current_category_index]
        category_text = body_font.render(current_category, True, Colors.TEXT_HIGHLIGHT)
        surface.blit(category_text, (panel_x + 20, panel_y + 20))

        # Draw statistics for current category
        stats = self.stats_data[current_category]
        start_y = panel_y + 60
        line_height = 25

        for i, (label, value) in enumerate(stats):
            y = start_y + (i * line_height)
            if y + line_height > panel_y + panel_height - 20:
                break

            # Draw label
            label_text = small_font.render(f"{label}:", True, Colors.TEXT_SECONDARY)
            surface.blit(label_text, (panel_x + 30, y))

            # Draw value
            value_text = small_font.render(str(value), True, Colors.TEXT_PRIMARY)
            value_x = panel_x + panel_width - 30 - value_text.get_width()
            surface.blit(value_text, (value_x, y))

        # Draw category navigation
        if len(self.categories) > 1:
            nav_text = f"Category: {self.current_category_index + 1}/{len(self.categories)}"
            nav_surface = small_font.render(nav_text, True, Colors.TEXT_SECONDARY)
            nav_rect = nav_surface.get_rect(center=(width // 2, height - 40))
            surface.blit(nav_surface, nav_rect)

        # Draw help text
        help_text = "↑/↓: Change Category  •  ESC: Close"
        draw_contextual_help(surface, help_text, small_font, margin_bottom=Layout.SCREEN_MARGIN)

"""Arena scene for spectating and betting on monster battles."""

from enum import Enum, auto
from typing import Optional, List, Dict, Tuple, TYPE_CHECKING

import pygame

from .base_menu_scene import BaseMenuScene
from .assets import AssetManager
from .ui import MessageBox, draw_contextual_help
from .theme import Colors, Fonts, Layout
from core.arena import ArenaManager, ArenaMatch, ArenaFighter
from core.world import World
from core.logging_utils import log_warning
from core.tutorial_system import TipTrigger

if TYPE_CHECKING:
    from .scene import SceneManager
    from core.achievements import AchievementManager
    from core.time_system import TimeOfDay


class ArenaPhase(Enum):
    """Phases of the arena scene."""
    LOBBY = auto()       # View matches, place bets
    PRE_MATCH = auto()   # About to start, final bets
    BATTLE = auto()      # Watching the fight
    RESULT = auto()      # Match ended, payouts


class ArenaScene(BaseMenuScene):
    """
    Monster arena scene for spectating and betting.
    """

    def __init__(
        self,
        manager: Optional["SceneManager"],
        arena_manager: ArenaManager,
        world: World,
        assets: Optional[AssetManager] = None,
        scale: int = 2,
    ):
        super().__init__(manager, assets, scale)
        self.arena = arena_manager
        self.world = world

        self.phase = ArenaPhase.LOBBY
        self.selected_match_index = 0
        self.selected_fighter_index = 0  # 0 = fighter A, 1 = fighter B
        self.bet_amount = 50
        self.current_match: Optional[ArenaMatch] = None
        self.battle_log: List[Dict] = []
        self.log_index = 0
        self.log_timer = 0.0
        self.log_speed = 1.5  # Seconds per log entry
        self.winner_id: Optional[str] = None
        self.bet_results: List[Tuple] = []

        # UI components
        self.message_box = MessageBox(
            position=(Layout.PADDING_LARGE, 320),
            width=Layout.SCREEN_WIDTH - Layout.PADDING_LARGE * 2,
            height=140
        )

        # Generate matches if none exist
        if not self.arena.current_matches:
            self.arena.generate_matches(3)

        self._update_message()
        self._trigger_first_visit_tip()

    def _get_gold(self) -> int:
        """Get current gold from world flags."""
        gold = self.world.get_flag("gold", 0)
        if not isinstance(gold, (int, float)):
            return 0
        return int(gold)

    def _trigger_first_visit_tip(self) -> None:
        """Trigger tutorial tip when entering the arena."""
        tutorial_manager = self.get_manager_attr(
            "tutorial_manager", "_trigger_first_visit_tip"
        )
        if tutorial_manager and not self.world.get_flag("_tutorial_first_arena_visit", False):
            self.world.set_flag("_tutorial_first_arena_visit", True)
            tutorial_manager.trigger_tip(TipTrigger.FIRST_ARENA_VISIT)

    def _trigger_first_bet_tip(self) -> None:
        """Trigger tutorial tip when placing the first arena bet."""
        tutorial_manager = self.get_manager_attr(
            "tutorial_manager", "_trigger_first_bet_tip"
        )
        if tutorial_manager and not self.world.get_flag("_tutorial_first_arena_bet", False):
            self.world.set_flag("_tutorial_first_arena_bet", True)
            tutorial_manager.trigger_tip(TipTrigger.FIRST_ARENA_BET)

    def _update_message(self) -> None:
        """Update message box based on current phase."""
        if self.phase == ArenaPhase.LOBBY:
            gold = self._get_gold()
            if self.arena.current_matches:
                match = self.arena.current_matches[self.selected_match_index]
                fighter = match.fighter_a if self.selected_fighter_index == 0 else match.fighter_b
                self.message_box.set_text(
                    f"Gold: {gold}g | Bet: {self.bet_amount}g\n"
                    f"Selected: {fighter.name} (Odds: {fighter.odds:.1f}:1)\n"
                    f"Record: {fighter.wins}W-{fighter.losses}L"
                )
            else:
                self.message_box.set_text("No matches available today.")
        elif self.phase == ArenaPhase.BATTLE:
            if self.log_index < len(self.battle_log):
                entry = self.battle_log[self.log_index]
                self.message_box.set_text(
                    f"Turn {entry['turn']}: {entry['attacker']} attacks {entry['defender']} "
                    f"for {entry['damage']} damage!\n"
                    f"{entry['defender']} HP: {entry['defender_hp']}"
                )
            else:
                self.message_box.set_text("Battle complete!")
        elif self.phase == ArenaPhase.RESULT:
            if self.current_match and self.winner_id:
                winner = self.current_match.fighter_a if self.winner_id == self.current_match.fighter_a.fighter_id else self.current_match.fighter_b
                result_text = f"Winner: {winner.name}!\n\n"
                if self.bet_results:
                    total_winnings = sum(winnings for _, winnings in self.bet_results)
                    if total_winnings > 0:
                        result_text += f"Total Winnings: +{total_winnings}g\n"
                    else:
                        result_text += "No winning bets.\n"
                else:
                    result_text += "No bets placed.\n"
                self.message_box.set_text(result_text)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.phase == ArenaPhase.LOBBY:
                    self._exit()
                elif self.phase == ArenaPhase.RESULT:
                    self.phase = ArenaPhase.LOBBY
                    self._update_message()

            if self.phase == ArenaPhase.LOBBY:
                self._handle_lobby_input(event)
            elif self.phase == ArenaPhase.BATTLE:
                # Space to speed up battle playback
                if event.key == pygame.K_SPACE:
                    self.log_speed = max(0.3, self.log_speed - 0.3)

    def _handle_lobby_input(self, event: pygame.event.Event) -> None:
        """Handle match selection and betting."""
        if not self.arena.current_matches:
            return

        if event.key == pygame.K_UP:
            self.selected_match_index = max(0, self.selected_match_index - 1)
            self._update_message()
        elif event.key == pygame.K_DOWN:
            self.selected_match_index = min(
                len(self.arena.current_matches) - 1,
                self.selected_match_index + 1
            )
            self._update_message()
        elif event.key == pygame.K_LEFT:
            self.selected_fighter_index = 0
            self._update_message()
        elif event.key == pygame.K_RIGHT:
            self.selected_fighter_index = 1
            self._update_message()
        elif event.key == pygame.K_PAGEUP:
            gold = self._get_gold()
            self.bet_amount = min(gold, self.bet_amount + 50)
            self._update_message()
        elif event.key == pygame.K_PAGEDOWN:
            self.bet_amount = max(10, self.bet_amount - 50)
            self._update_message()
        elif event.key == pygame.K_b:
            self._place_bet()
        elif event.key == pygame.K_w:
            self._watch_match()

    def _place_bet(self) -> None:
        """Place bet on selected fighter."""
        if not self.arena.current_matches:
            return

        match = self.arena.current_matches[self.selected_match_index]
        fighter = match.fighter_a if self.selected_fighter_index == 0 else match.fighter_b

        bet = self.arena.place_bet(match, fighter.fighter_id, self.bet_amount, self.world)
        if bet:
            # Show confirmation
            self.message_box.set_text(f"Bet placed: {self.bet_amount}g on {fighter.name}!")
            self._trigger_first_bet_tip()
        else:
            # Show error (not enough gold)
            self.message_box.set_text("Not enough gold!")

    def _watch_match(self) -> None:
        """Start watching selected match."""
        if not self.arena.current_matches:
            return

        self.current_match = self.arena.current_matches[self.selected_match_index]
        self.winner_id, self.battle_log = self.arena.simulate_match(self.current_match)
        self.log_index = 0
        self.log_timer = 0.0
        self.phase = ArenaPhase.BATTLE
        self._update_message()

    def update(self, dt: float) -> None:
        if self.phase == ArenaPhase.BATTLE:
            self.log_timer += dt
            if self.log_timer >= self.log_speed:
                self.log_timer = 0.0
                self.log_index += 1
                self._update_message()

                if self.log_index >= len(self.battle_log):
                    # Battle ended
                    self._end_battle()

    def _end_battle(self) -> None:
        """Handle battle end, resolve bets."""
        if self.current_match and self.winner_id:
            self.bet_results = self.arena.resolve_bets(
                self.current_match, self.winner_id, self.world
            )
            self._check_achievements()
            self.phase = ArenaPhase.RESULT
            self._update_message()

    def _check_achievements(self) -> None:
        """Check and update arena-related achievements."""
        achievement_manager = self.get_manager_attr(
            "achievement_manager", "_check_achievements"
        )
        if not achievement_manager:
            return

        # Track matches watched
        matches_watched = self.world.get_flag("arena_matches_watched", 0)
        if not isinstance(matches_watched, (int, float)):
            matches_watched = 0
        self.world.set_flag("arena_matches_watched", int(matches_watched) + 1)

        # Track gold won from bets
        total_winnings = sum(winnings for _, winnings in self.bet_results)
        if total_winnings > 0:
            gold_won = self.world.get_flag("arena_gold_won", 0)
            if not isinstance(gold_won, (int, float)):
                gold_won = 0
            self.world.set_flag("arena_gold_won", int(gold_won) + total_winnings)

            # Check for underdog win (odds >= 5.0)
            for bet, winnings in self.bet_results:
                if winnings > 0 and bet.odds_at_bet >= 5.0:
                    self.world.set_flag("arena_underdog_win", True)
                    bus = getattr(self.manager, "event_bus", None) if self.manager else None
                    if bus:
                        bus.publish(
                            "flag_set",
                            flag_name="arena_underdog_win",
                            flag_value=True,
                        )
                    break

        # Track prediction streak
        if self.bet_results:
            # Check if player had a winning bet
            has_win = any(winnings > 0 for _, winnings in self.bet_results)
            streak = self.world.get_flag("arena_streak", 0)
            if not isinstance(streak, (int, float)):
                streak = 0
            if has_win:
                self.world.set_flag("arena_streak", int(streak) + 1)
            else:
                self.world.set_flag("arena_streak", 0)

        # Check stat-based achievements
        stats = {
            "arena_matches_watched": int(self.world.get_flag("arena_matches_watched", 0)),
            "arena_gold_won": int(self.world.get_flag("arena_gold_won", 0)),
            "arena_streak": int(self.world.get_flag("arena_streak", 0)),
        }
        achievement_manager.check_stat_achievements(stats)

    def _exit(self) -> None:
        """Exit arena scene."""
        if self.manager:
            self.manager.pop()

    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw arena UI:

        LOBBY:
        - List of upcoming matches
        - Fighter stats comparison
        - Current odds
        - Win/loss records
        - Bet amount selector
        - Active bets list
        - Gold display

        BATTLE:
        - Two fighters facing each other
        - HP bars for each
        - Battle log (scrolling text)
        - Current action animation
        - "Press SPACE to speed up"

        RESULT:
        - Winner announcement
        - Bet results (win/loss for each bet)
        - Gold gained/lost
        - Updated odds for fighters
        """
        surface.fill(Colors.BG_MAIN)

        # Draw header
        header_rect = pygame.Rect(0, 0, surface.get_width(), 100)
        pygame.draw.rect(surface, Colors.BG_DARK, header_rect)
        pygame.draw.line(surface, Colors.BORDER, (0, 100), (surface.get_width(), 100), 2)

        font = self.assets.get_font(Fonts.DEFAULT, Fonts.SIZE_HEADING)
        small_font = self.assets.get_font(Fonts.DEFAULT, Fonts.SIZE_BODY) or font

        if font:
            # Title
            title_surface = font.render("Monster Arena", True, Colors.TEXT_PRIMARY)
            surface.blit(title_surface, (20, 20))

            # Gold display
            gold = self._get_gold()
            gold_surface = font.render(f"Gold: {gold}g", True, Colors.ACCENT)
            surface.blit(gold_surface, (20, 60))

        if self.phase == ArenaPhase.LOBBY:
            self._draw_lobby(surface, small_font or font)
        elif self.phase == ArenaPhase.BATTLE:
            self._draw_battle(surface, small_font or font)
        elif self.phase == ArenaPhase.RESULT:
            self._draw_result(surface, small_font or font)

        # Draw message box
        if small_font:
            self.message_box.draw(surface, small_font, panel=self.panel)

        # Draw help text
        self._draw_help_text(surface, small_font or font)

    def _draw_lobby(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        """Draw lobby UI with match list and betting interface."""
        y = 120
        x = 20

        if not self.arena.current_matches:
            text = font.render("No matches scheduled today.", True, Colors.TEXT_SECONDARY)
            surface.blit(text, (x, y))
            return

        # Draw match list
        for i, match in enumerate(self.arena.current_matches):
            is_selected = i == self.selected_match_index
            color = Colors.TEXT_HIGHLIGHT if is_selected else Colors.TEXT_PRIMARY

            match_text = font.render(
                f"{match.fighter_a.name} vs {match.fighter_b.name}",
                True, color
            )
            surface.blit(match_text, (x, y + i * 30))

        # Draw selected match details
        if self.selected_match_index < len(self.arena.current_matches):
            match = self.arena.current_matches[self.selected_match_index]
            y_detail = 220

            # Fighter A
            fighter_a_color = Colors.TEXT_HIGHLIGHT if self.selected_fighter_index == 0 else Colors.TEXT_PRIMARY
            fighter_a_text = font.render(
                f"{match.fighter_a.name} (Odds: {match.fighter_a.odds:.1f}:1) "
                f"[{match.fighter_a.wins}W-{match.fighter_a.losses}L]",
                True, fighter_a_color
            )
            surface.blit(fighter_a_text, (x, y_detail))

            # Fighter B
            fighter_b_color = Colors.TEXT_HIGHLIGHT if self.selected_fighter_index == 1 else Colors.TEXT_PRIMARY
            fighter_b_text = font.render(
                f"{match.fighter_b.name} (Odds: {match.fighter_b.odds:.1f}:1) "
                f"[{match.fighter_b.wins}W-{match.fighter_b.losses}L]",
                True, fighter_b_color
            )
            surface.blit(fighter_b_text, (x, y_detail + 30))

    def _draw_battle(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        """Draw battle UI with fighters and HP bars."""
        if not self.current_match:
            return

        y = 120
        x = 20

        # Fighter A (left side)
        fighter_a_text = font.render(self.current_match.fighter_a.name, True, Colors.TEXT_PRIMARY)
        surface.blit(fighter_a_text, (x, y))

        # Fighter B (right side)
        fighter_b_text = font.render(self.current_match.fighter_b.name, True, Colors.TEXT_PRIMARY)
        surface.blit(fighter_b_text, (surface.get_width() - 200, y))

        # Draw HP bars (simplified - would need actual HP tracking for full implementation)
        bar_width = 150
        bar_height = 20
        bar_y = y + 40

        # Fighter A HP bar
        hp_rect = pygame.Rect(x, bar_y, bar_width, bar_height)
        pygame.draw.rect(surface, Colors.BAR_BG, hp_rect)
        pygame.draw.rect(surface, Colors.HP_HIGH, (x, bar_y, bar_width, bar_height))
        pygame.draw.rect(surface, Colors.BORDER, hp_rect, 2)

        # Fighter B HP bar
        hp_rect_b = pygame.Rect(surface.get_width() - 200, bar_y, bar_width, bar_height)
        pygame.draw.rect(surface, Colors.BAR_BG, hp_rect_b)
        pygame.draw.rect(surface, Colors.HP_HIGH, (surface.get_width() - 200, bar_y, bar_width, bar_height))
        pygame.draw.rect(surface, Colors.BORDER, hp_rect_b, 2)

        # Speed up hint
        if self.log_index < len(self.battle_log):
            hint_text = font.render("Press SPACE to speed up", True, Colors.TEXT_SECONDARY)
            surface.blit(hint_text, (x, bar_y + 40))

    def _draw_result(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        """Draw result screen with winner and bet payouts."""
        if not self.current_match or not self.winner_id:
            return

        y = 120
        x = 20

        winner = self.current_match.fighter_a if self.winner_id == self.current_match.fighter_a.fighter_id else self.current_match.fighter_b
        winner_text = font.render(f"Winner: {winner.name}!", True, Colors.TEXT_SUCCESS)
        surface.blit(winner_text, (x, y))

        # Draw bet results
        y += 50
        if self.bet_results:
            for bet, winnings in self.bet_results:
                if winnings > 0:
                    result_text = font.render(
                        f"Bet on {bet.fighter_id}: +{winnings}g",
                        True, Colors.TEXT_SUCCESS
                    )
                else:
                    result_text = font.render(
                        f"Bet on {bet.fighter_id}: Lost",
                        True, Colors.TEXT_ERROR
                    )
                surface.blit(result_text, (x, y))
                y += 30

    def _draw_help_text(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        """Draw standardized help text at the bottom of the screen."""
        if not font:
            return

        width, height = surface.get_size()

        if self.phase == ArenaPhase.LOBBY:
            help_text = "↑/↓: Select Match  •  ←/→: Select Fighter  •  PgUp/PgDn: Bet Amount  •  B: Bet  •  W: Watch  •  ESC: Exit"
        elif self.phase == ArenaPhase.BATTLE:
            help_text = "Space: Speed Up Battle"
        else:
            help_text = "ESC: Return to Lobby"

        draw_contextual_help(surface, help_text, font, margin_bottom=Layout.SCREEN_MARGIN)

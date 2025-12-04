"""Gambling scene for tavern mini-games."""

from typing import Optional, TYPE_CHECKING

import pygame

from .base_menu_scene import BaseMenuScene
from .assets import AssetManager
from .ui import Menu, MessageBox, draw_contextual_help
from .theme import Colors, Fonts, Layout
from core.gambling import (
    GamblingGameType,
    GamblingManager,
    DiceGame,
    BlackjackGame,
    SlotsGame,
    CoinFlipGame,
    CupsGame,
)
from core.world import World
from core.logging_utils import log_warning
from core.tutorial_system import TipTrigger

if TYPE_CHECKING:
    from .scene import SceneManager
    from core.achievements import AchievementManager


class GamblingScene(BaseMenuScene):
    """
    Scene for tavern gambling games.

    Supports multiple game types with shared betting UI.
    """

    def __init__(
        self,
        manager: Optional["SceneManager"],
        game_type: GamblingGameType,
        gambling_manager: GamblingManager,
        world: World,
        min_bet: int = 10,
        max_bet: int = 1000,
        assets: Optional[AssetManager] = None,
        scale: int = 2,
    ):
        super().__init__(manager, assets, scale)
        self.game_type = game_type
        self.gm = gambling_manager
        self.world = world
        self.min_bet = min_bet
        self.max_bet = max_bet

        self.phase = "betting"  # "betting", "playing", "result"
        self.bet_amount = min_bet
        self.game_instance = self._create_game()
        self.result_message = ""
        self.result_type = ""  # "win", "lose", "push"

        # Game-specific state
        self.dice_guess: Optional[str] = None  # "high" or "low"
        self.blackjack_action: Optional[str] = None  # "hit" or "stand"
        self.cups_guess: Optional[int] = None
        self.slots_spun = False
        self.coin_guess: Optional[str] = None  # "heads" or "tails"
        self.coin_result: Optional[str] = None
        self._entered_tip_triggered = False
        self._win_tip_triggered = False
        self._loss_tip_triggered = False

        # UI components
        self.message_box = MessageBox(
            position=(Layout.PADDING_LARGE, 320),
            width=Layout.SCREEN_WIDTH - Layout.PADDING_LARGE * 2,
            height=140
        )
        self.menu: Optional[Menu] = None

        self._update_message()
        self._trigger_gambling_entry_tip()

    def _create_game(self):
        """Create game instance based on type."""
        if self.game_type == GamblingGameType.BLACKJACK:
            return BlackjackGame()
        elif self.game_type == GamblingGameType.DICE_ROLL:
            return DiceGame()
        elif self.game_type == GamblingGameType.SLOTS:
            return SlotsGame()
        elif self.game_type == GamblingGameType.CUPS_GAME:
            return CupsGame()
        elif self.game_type == GamblingGameType.COIN_FLIP:
            return CoinFlipGame()
        return None

    def _get_gold(self) -> int:
        """Get current gold from world flags."""
        gold = self.world.get_flag("gold", 0)
        if not isinstance(gold, (int, float)):
            return 0
        return int(gold)

    def _trigger_gambling_entry_tip(self) -> None:
        """Trigger tutorial tip when entering gambling for the first time."""
        if self._entered_tip_triggered:
            return

        tutorial_manager = self.get_manager_attr(
            "tutorial_manager", "_trigger_gambling_entry_tip"
        )
        if tutorial_manager:
            already_shown = self.world.get_flag("_tutorial_first_gambling_shown", False)
            if not already_shown:
                tutorial_manager.trigger_tip(TipTrigger.FIRST_GAMBLING)
                self.world.set_flag("_tutorial_first_gambling_shown", True)
            self._entered_tip_triggered = True

    def _trigger_result_tip(self, result: str) -> None:
        """Trigger win/loss gambling tutorial tips."""
        tutorial_manager = self.get_manager_attr(
            "tutorial_manager", "_trigger_result_tip"
        )
        if not tutorial_manager:
            return

        if result == "win":
            if not self.world.get_flag("_tutorial_first_gambling_win_shown", False) and not self._win_tip_triggered:
                self.world.set_flag("_tutorial_first_gambling_win_shown", True)
                tutorial_manager.trigger_tip(TipTrigger.FIRST_GAMBLING_WIN)
                self._win_tip_triggered = True
        elif result == "lose":
            if not self.world.get_flag("_tutorial_first_gambling_loss_shown", False) and not self._loss_tip_triggered:
                self.world.set_flag("_tutorial_first_gambling_loss_shown", True)
                tutorial_manager.trigger_tip(TipTrigger.FIRST_GAMBLING_LOSS)
                self._loss_tip_triggered = True

    def _update_message(self) -> None:
        """Update message box based on current phase."""
        if self.phase == "betting":
            gold = self._get_gold()
            self.message_box.set_text(
                f"Current Gold: {gold}g\n"
                f"Bet Amount: {self.bet_amount}g\n"
                f"Press UP/DOWN to adjust, ENTER to place bet"
            )
        elif self.phase == "playing":
            if self.game_type == GamblingGameType.DICE_ROLL and not self.dice_guess:
                self.message_box.set_text("Choose High or Low (UP/DOWN, ENTER to confirm)")
            elif self.game_type == GamblingGameType.BLACKJACK:
                if isinstance(self.game_instance, BlackjackGame):
                    player_val = self.game_instance.get_hand_value(self.game_instance.player_hand)
                    if player_val > 21:
                        self.message_box.set_text("BUST! Press SPACE to continue")
                    elif self.game_instance.player_standing:
                        self.message_box.set_text("Dealer's turn... Press SPACE to continue")
                    else:
                        self.message_box.set_text("Hit or Stand? (UP/DOWN, ENTER)")
            elif self.game_type == GamblingGameType.SLOTS and not self.slots_spun:
                self.message_box.set_text("Press SPACE to spin the reels!")
            elif self.game_type == GamblingGameType.CUPS_GAME and self.cups_guess is None:
                if isinstance(self.game_instance, CupsGame):
                    self.message_box.set_text(f"Which cup? (1-{self.game_instance.num_cups}, ENTER to guess)")
            elif self.game_type == GamblingGameType.COIN_FLIP and not self.coin_guess:
                self.message_box.set_text("Heads or Tails? (UP/DOWN, ENTER to confirm)")
        elif self.phase == "result":
            self.message_box.set_text(self.result_message)

    def _start_game(self) -> None:
        """Start the game after bet is placed."""
        if self.game_type == GamblingGameType.BLACKJACK:
            if isinstance(self.game_instance, BlackjackGame):
                self.game_instance.deal_initial()
        elif self.game_type == GamblingGameType.CUPS_GAME:
            if isinstance(self.game_instance, CupsGame):
                self.game_instance.start_game()
                self.game_instance.generate_shuffles()
        self.phase = "playing"
        self._update_message()

    def _handle_betting_input(self, event: pygame.event.Event) -> None:
        """Handle bet amount selection."""
        if event.key == pygame.K_UP:
            self.bet_amount = min(self.max_bet, self.bet_amount + 10)
            self._update_message()
        elif event.key == pygame.K_DOWN:
            self.bet_amount = max(self.min_bet, self.bet_amount - 10)
            self._update_message()
        elif event.key == pygame.K_RETURN:
            if self.gm.place_bet(self.bet_amount, self.world):
                self._start_game()
            else:
                self.message_box.set_text("Not enough gold!")

    def _handle_game_input(self, event: pygame.event.Event) -> None:
        """Handle game-specific input."""
        if self.game_type == GamblingGameType.DICE_ROLL:
            if not self.dice_guess:
                if event.key == pygame.K_UP:
                    self.dice_guess = "high"
                    self._update_message()
                elif event.key == pygame.K_DOWN:
                    self.dice_guess = "low"
                    self._update_message()
                elif event.key == pygame.K_RETURN and self.dice_guess:
                    self._play_dice()
            elif event.key in (pygame.K_SPACE, pygame.K_RETURN):
                self._show_result()
        elif self.game_type == GamblingGameType.BLACKJACK:
            if isinstance(self.game_instance, BlackjackGame):
                if self.game_instance.player_standing or self.game_instance.is_bust(self.game_instance.player_hand):
                    if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                        if not self.game_instance.player_standing and not self.game_instance.is_bust(self.game_instance.player_hand):
                            self.game_instance.dealer_play()
                        self._finish_blackjack()
                else:
                    if event.key == pygame.K_UP:
                        self.blackjack_action = "hit"
                        self._update_message()
                    elif event.key == pygame.K_DOWN:
                        self.blackjack_action = "stand"
                        self._update_message()
                    elif event.key == pygame.K_RETURN and self.blackjack_action:
                        if self.blackjack_action == "hit":
                            self.game_instance.hit()
                            if self.game_instance.is_bust(self.game_instance.player_hand):
                                self._finish_blackjack()
                            else:
                                self._update_message()
                        else:
                            self.game_instance.player_standing = True
                            self.game_instance.dealer_play()
                            self._finish_blackjack()

        elif self.game_type == GamblingGameType.SLOTS:
            if not self.slots_spun:
                if event.key == pygame.K_SPACE:
                    self._play_slots()
            elif event.key in (pygame.K_SPACE, pygame.K_RETURN):
                self._show_result()
        elif self.game_type == GamblingGameType.CUPS_GAME:
            if self.cups_guess is None:
                if isinstance(self.game_instance, CupsGame):
                    if pygame.K_1 <= event.key <= pygame.K_9:
                        cup_num = event.key - pygame.K_1
                        if cup_num < self.game_instance.num_cups:
                            self.cups_guess = cup_num
                            self._play_cups()
            elif event.key in (pygame.K_SPACE, pygame.K_RETURN):
                self._show_result()
        elif self.game_type == GamblingGameType.COIN_FLIP:
            if not self.coin_guess:
                if event.key == pygame.K_UP:
                    self.coin_guess = "heads"
                    self._update_message()
                elif event.key == pygame.K_DOWN:
                    self.coin_guess = "tails"
                    self._update_message()
                elif event.key == pygame.K_RETURN and self.coin_guess:
                    self._play_coin()
            elif event.key in (pygame.K_SPACE, pygame.K_RETURN):
                self._show_result()

    def _play_dice(self) -> None:
        """Play dice game."""
        if isinstance(self.game_instance, DiceGame) and self.dice_guess:
            self.game_instance.roll()
            result = self.game_instance.check_high_low(self.dice_guess)
            if result is None:
                self.gm.push(self.world)
                self.result_type = "push"
                self.result_message = f"Rolled {self.game_instance.get_total()} (Push - bet returned)"
            elif result:
                winnings = self.gm.win(1.9, self.world)  # Slight house edge
                self.result_type = "win"
                self.result_message = f"Rolled {self.game_instance.get_total()} - You win! +{winnings}g"
                self.gm.track_game_win(self.game_type)
            else:
                self.gm.lose()
                self.result_type = "lose"
                self.result_message = f"Rolled {self.game_instance.get_total()} - You lose!"
            self.phase = "result"
            self._update_message()
            self._check_achievements()
            self._trigger_result_tip(self.result_type)

    def _finish_blackjack(self) -> None:
        """Finish blackjack game."""
        if isinstance(self.game_instance, BlackjackGame):
            winner = self.game_instance.determine_winner()
            if winner == "player":
                winnings = self.gm.win(2.0, self.world)  # 2x payout
                self.result_type = "win"
                self.result_message = f"You win! +{winnings}g"
                self.gm.track_game_win(self.game_type)
            elif winner == "dealer":
                self.gm.lose()
                self.result_type = "lose"
                self.result_message = "Dealer wins!"
            else:
                self.gm.push(self.world)
                self.result_type = "push"
                self.result_message = "Push - bet returned"
            self.phase = "result"
            self._update_message()
            self._check_achievements()
            self._trigger_result_tip(self.result_type)

    def _play_slots(self) -> None:
        """Play slots game."""
        if isinstance(self.game_instance, SlotsGame):
            self.game_instance.spin()
            self.slots_spun = True
            multiplier = self.game_instance.get_payout_multiplier()

            if self.game_instance.is_jackpot():
                # Set flag for jackpot achievement and publish event
                self.world.set_flag("slots_jackpot", True)
                if self.manager and getattr(self.manager, "event_bus", None):
                    self.manager.event_bus.publish(
                        "flag_set",
                        flag_name="slots_jackpot",
                        flag_value=True,
                    )

            if multiplier > 0:
                winnings = self.gm.win(multiplier, self.world)
                self.result_type = "win"
                symbols = " ".join(self.game_instance.reels)
                self.result_message = f"{symbols} - You win {multiplier}x! +{winnings}g"
                self.gm.track_game_win(self.game_type)
            else:
                self.gm.lose()
                self.result_type = "lose"
                symbols = " ".join(self.game_instance.reels)
                self.result_message = f"{symbols} - No win"
            self.phase = "result"
            self._update_message()
            self._check_achievements()
            self._trigger_result_tip(self.result_type)

    def _play_cups(self) -> None:
        """Play cups game."""
        if isinstance(self.game_instance, CupsGame) and self.cups_guess is not None:
            won = self.game_instance.guess(self.cups_guess)
            if won:
                winnings = self.gm.win(2.5, self.world)  # Adjusted for house edge
                self.result_type = "win"
                self.result_message = f"Correct! You win! +{winnings}g"
                self.gm.track_game_win(self.game_type)
            else:
                self.gm.lose()
                self.result_type = "lose"
                self.result_message = f"Wrong cup! The ball was under cup {self.game_instance.ball_position + 1}"
            self.phase = "result"
            self._update_message()
            self._check_achievements()
            self._trigger_result_tip(self.result_type)

    def _play_coin(self) -> None:
        """Play coin flip game."""
        if isinstance(self.game_instance, CoinFlipGame) and self.coin_guess:
            result = self.game_instance.flip()
            self.coin_result = result
            if result == self.coin_guess:
                winnings = self.gm.win(2.0, self.world)
                self.result_type = "win"
                self.result_message = f"The coin lands on {result.title()}! You win +{winnings}g"
                self.gm.track_game_win(self.game_type)
            else:
                self.gm.lose()
                self.result_type = "lose"
                self.result_message = f"The coin lands on {result.title()}. You lose!"
            self.phase = "result"
            self._update_message()
            self._check_achievements()
            self._trigger_result_tip(self.result_type)

    def _show_result(self) -> None:
        """Show result and return to betting."""
        self.phase = "betting"
        self.bet_amount = self.min_bet
        self.dice_guess = None
        self.blackjack_action = None
        self.cups_guess = None
        self.slots_spun = False
        self.coin_guess = None
        self.coin_result = None
        self.game_instance = self._create_game()
        self._update_message()

    def _check_achievements(self) -> None:
        """Check and update gambling-related achievements."""
        achievement_manager = self.get_manager_attr(
            "achievement_manager", "_check_achievements"
        )
        if not achievement_manager:
            return

        # Update world flags for stat-based achievements
        self.world.set_flag("gambling_total_won", self.gm.stats.total_won)
        self.world.set_flag("gambling_best_streak", self.gm.stats.best_streak)
        self.world.set_flag("blackjack_wins", self.gm.stats.blackjack_wins)

        # Check stat-based achievements
        stats = {
            "gambling_total_won": self.gm.stats.total_won,
            "gambling_best_streak": self.gm.stats.best_streak,
            "blackjack_wins": self.gm.stats.blackjack_wins,
        }
        achievement_manager.check_stat_achievements(stats)

    def _exit(self) -> None:
        """Exit gambling scene."""
        if self.manager:
            self.manager.pop()

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.phase == "betting":
                    self._exit()
                elif self.phase == "result":
                    self._show_result()

            if self.phase == "betting":
                self._handle_betting_input(event)
            elif self.phase == "playing":
                self._handle_game_input(event)
            elif self.phase == "result":
                if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    self._show_result()

    def update(self, dt: float) -> None:
        """Update scene state."""
        # Keep message box cursor animation active
        if self.message_box:
            self.message_box.update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        """Draw gambling UI."""
        surface.fill(Colors.BG_MAIN)

        # Draw header
        header_rect = pygame.Rect(0, 0, surface.get_width(), 100)
        pygame.draw.rect(surface, Colors.BG_DARK, header_rect)
        pygame.draw.line(surface, Colors.BORDER, (0, 100), (surface.get_width(), 100), 2)

        font = self.assets.get_font(Fonts.DEFAULT, Fonts.SIZE_HEADING)
        small_font = self.assets.get_font(Fonts.DEFAULT, Fonts.SIZE_BODY) or font

        if font:
            # Title
            game_name = self.game_type.value.replace("_", " ").title()
            title_surface = font.render(f"{game_name}", True, Colors.TEXT_PRIMARY)
            surface.blit(title_surface, (20, 20))

            # Gold display
            gold = self._get_gold()
            gold_surface = font.render(f"Gold: {gold}g", True, Colors.ACCENT)
            surface.blit(gold_surface, (20, 60))

        # Draw game-specific UI
        if self.phase == "playing":
            if self.game_type == GamblingGameType.BLACKJACK:
                self._draw_blackjack(surface, small_font)
            elif self.game_type == GamblingGameType.DICE_ROLL:
                self._draw_dice(surface, small_font)
            elif self.game_type == GamblingGameType.SLOTS:
                self._draw_slots(surface, small_font)
            elif self.game_type == GamblingGameType.CUPS_GAME:
                self._draw_cups(surface, small_font)
            elif self.game_type == GamblingGameType.COIN_FLIP:
                self._draw_coin(surface, small_font)

        # Draw message box
        self.message_box.draw(surface, small_font or self.assets.get_font(Fonts.DEFAULT), panel=self.panel)

        # Draw help text
        self._draw_help_text(surface, small_font or self.assets.get_font(Fonts.DEFAULT))

    def _draw_blackjack(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        """Draw blackjack game UI."""
        if not isinstance(self.game_instance, BlackjackGame):
            return

        y = 120
        # Dealer hand
        dealer_val = self.game_instance.get_hand_value(self.game_instance.dealer_hand)
        if self.game_instance.player_standing or self.game_instance.is_bust(self.game_instance.player_hand):
            dealer_text = font.render(f"Dealer: {dealer_val}", True, Colors.TEXT_PRIMARY)
        else:
            # Hide one card
            hidden_val = self.game_instance.get_hand_value([self.game_instance.dealer_hand[0]])
            dealer_text = font.render(f"Dealer: {hidden_val} + ?", True, Colors.TEXT_PRIMARY)
        surface.blit(dealer_text, (20, y))

        y += 40
        # Player hand
        player_val = self.game_instance.get_hand_value(self.game_instance.player_hand)
        player_text = font.render(f"Player: {player_val}", True, Colors.TEXT_PRIMARY)
        surface.blit(player_text, (20, y))

        if not self.game_instance.player_standing and not self.game_instance.is_bust(self.game_instance.player_hand):
            y += 30
            if self.blackjack_action:
                action_text = font.render(f"Selected: {self.blackjack_action.upper()}", True, Colors.TEXT_HIGHLIGHT)
                surface.blit(action_text, (20, y))

    def _draw_dice(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        """Draw dice game UI."""
        if not isinstance(self.game_instance, DiceGame):
            return

        y = 120
        if self.dice_guess:
            guess_text = font.render(f"Your guess: {self.dice_guess.upper()}", True, Colors.TEXT_HIGHLIGHT)
            surface.blit(guess_text, (20, y))

            if self.phase == "result":
                y += 40
                dice_text = font.render(f"Dice: {self.game_instance.last_roll} = {self.game_instance.get_total()}", True, Colors.TEXT_PRIMARY)
                surface.blit(dice_text, (20, y))

    def _draw_slots(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        """Draw slots game UI."""
        if not isinstance(self.game_instance, SlotsGame):
            return

        y = 120
        if self.slots_spun:
            reels_text = font.render(" ".join(self.game_instance.reels), True, Colors.TEXT_PRIMARY)
            surface.blit(reels_text, (20, y))

    def _draw_cups(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        """Draw cups game UI."""
        if not isinstance(self.game_instance, CupsGame):
            return

        y = 120
        if self.cups_guess is not None:
            guess_text = font.render(f"You chose cup {self.cups_guess + 1}", True, Colors.TEXT_HIGHLIGHT)
            surface.blit(guess_text, (20, y))

    def _draw_coin(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        """Draw coin flip UI."""
        if not isinstance(self.game_instance, CoinFlipGame):
            return

        y = 120
        if self.coin_guess:
            guess_text = font.render(f"Your guess: {self.coin_guess.title()}", True, Colors.TEXT_HIGHLIGHT)
            surface.blit(guess_text, (20, y))

        if self.phase == "result" and self.coin_result:
            y += 40
            result_text = font.render(f"Result: {self.coin_result.title()}", True, Colors.TEXT_PRIMARY)
            surface.blit(result_text, (20, y))

    def _draw_help_text(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        """Draw standardized help text at the bottom of the screen."""
        if not font:
            return

        width, height = surface.get_size()

        if self.phase == "betting":
            help_text = "↑/↓: Adjust Bet  •  Enter: Place Bet  •  ESC: Leave"
        elif self.phase == "playing":
            if self.game_type == GamblingGameType.DICE_ROLL:
                help_text = "↑: High  •  ↓: Low  •  Enter: Confirm"
            elif self.game_type == GamblingGameType.BLACKJACK:
                help_text = "↑: Hit  •  ↓: Stand  •  Enter: Confirm"
            elif self.game_type == GamblingGameType.SLOTS:
                help_text = "Space: Spin"
            elif self.game_type == GamblingGameType.CUPS_GAME:
                help_text = "1-3: Choose Cup  •  Enter: Confirm"
            elif self.game_type == GamblingGameType.COIN_FLIP:
                help_text = "↑: Heads  •  ↓: Tails  •  Enter: Flip"
            else:
                help_text = "Follow on-screen prompts"
        else:
            help_text = "Space/Enter: Play Again  •  ESC: Leave"

        draw_contextual_help(surface, help_text, font, margin_bottom=Layout.SCREEN_MARGIN)

"""Gambling mini-games system for tavern games."""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional, Tuple, Any, TYPE_CHECKING
import random

if TYPE_CHECKING:
    from .world import World


class GamblingGameType(Enum):
    """Types of gambling games available."""
    BLACKJACK = "blackjack"
    DICE_ROLL = "dice_roll"  # High-low dice
    SLOTS = "slots"
    COIN_FLIP = "coin_flip"
    CUPS_GAME = "cups_game"  # Shell game / cups and ball


@dataclass
class GamblingStats:
    """Player's gambling statistics."""
    total_wagered: int = 0
    total_won: int = 0
    total_lost: int = 0
    games_played: int = 0
    biggest_win: int = 0
    biggest_loss: int = 0
    current_streak: int = 0  # Positive = wins, negative = losses
    best_streak: int = 0
    worst_streak: int = 0
    blackjack_wins: int = 0
    dice_wins: int = 0
    slots_wins: int = 0
    cups_wins: int = 0


class DiceGame:
    """Simple high-low dice game."""

    def __init__(self):
        self.num_dice = 2
        self.last_roll: List[int] = []

    def roll(self) -> List[int]:
        """Roll the dice."""
        self.last_roll = [random.randint(1, 6) for _ in range(self.num_dice)]
        return self.last_roll

    def get_total(self) -> int:
        """Get total of last roll."""
        return sum(self.last_roll)

    def check_high_low(self, guess: str) -> Optional[bool]:
        """Check if high/low guess is correct. High = 8+, Low = 6-, 7 = push.

        Args:
            guess: "high" or "low"

        Returns:
            True if correct, False if wrong, None if push (7)
        """
        total = self.get_total()
        if total == 7:
            return None  # Push - bet returned
        if guess == "high":
            return total >= 8
        else:
            return total <= 6


class BlackjackGame:
    """Simplified blackjack."""

    def __init__(self):
        self.deck: List[Tuple[str, str]] = []  # (rank, suit)
        self.player_hand: List[Tuple[str, str]] = []
        self.dealer_hand: List[Tuple[str, str]] = []
        self.player_standing = False
        self._init_deck()

    def _init_deck(self) -> None:
        """Initialize and shuffle deck."""
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        suits = ['hearts', 'diamonds', 'clubs', 'spades']
        self.deck = [(r, s) for r in ranks for s in suits]
        random.shuffle(self.deck)

    def deal_initial(self) -> None:
        """Deal initial hands."""
        self.player_hand = [self.deck.pop(), self.deck.pop()]
        self.dealer_hand = [self.deck.pop(), self.deck.pop()]

    def hit(self, is_player: bool = True) -> Tuple[str, str]:
        """Draw a card."""
        card = self.deck.pop()
        if is_player:
            self.player_hand.append(card)
        else:
            self.dealer_hand.append(card)
        return card

    def get_hand_value(self, hand: List[Tuple[str, str]]) -> int:
        """Calculate hand value, handling aces optimally."""
        value = 0
        aces = 0
        for rank, _ in hand:
            if rank in ['J', 'Q', 'K']:
                value += 10
            elif rank == 'A':
                aces += 1
                value += 11
            else:
                value += int(rank)

        while value > 21 and aces > 0:
            value -= 10
            aces -= 1

        return value

    def is_bust(self, hand: List[Tuple[str, str]]) -> bool:
        """Check if hand is over 21."""
        return self.get_hand_value(hand) > 21

    def dealer_play(self) -> None:
        """Dealer draws until 17+."""
        while self.get_hand_value(self.dealer_hand) < 17:
            self.hit(is_player=False)

    def determine_winner(self) -> str:
        """Returns 'player', 'dealer', or 'push'."""
        player_val = self.get_hand_value(self.player_hand)
        dealer_val = self.get_hand_value(self.dealer_hand)

        if player_val > 21:
            return "dealer"
        if dealer_val > 21:
            return "player"
        if player_val > dealer_val:
            return "player"
        if dealer_val > player_val:
            return "dealer"
        return "push"


class SlotsGame:
    """Simple slot machine."""

    SYMBOLS = ["cherry", "lemon", "orange", "plum", "bell", "bar", "seven"]
    PAYOUTS = {
        ("seven", "seven", "seven"): 100,  # Jackpot
        ("bar", "bar", "bar"): 50,
        ("bell", "bell", "bell"): 25,
        ("cherry", "cherry", "cherry"): 10,
        ("cherry", "cherry", None): 5,  # Two cherries
        ("cherry", None, None): 2,  # One cherry
    }

    def __init__(self):
        self.reels: List[str] = ["", "", ""]

    def spin(self) -> List[str]:
        """Spin the reels."""
        # Weighted random - sevens are rare
        weights = [10, 10, 10, 10, 8, 5, 2]  # cherry most common, seven rarest
        self.reels = random.choices(self.SYMBOLS, weights=weights, k=3)
        return self.reels

    def get_payout_multiplier(self) -> int:
        """Get payout multiplier for current reels."""
        r = tuple(self.reels)

        # Check exact matches first
        if r in self.PAYOUTS:
            return self.PAYOUTS[r]

        # Check partial cherry matches
        if r[0] == "cherry" and r[1] == "cherry":
            return 5
        if r[0] == "cherry":
            return 2

        return 0

    def is_jackpot(self) -> bool:
        """Check if current reels are jackpot (triple sevens)."""
        return tuple(self.reels) == ("seven", "seven", "seven")


class CupsGame:
    """Shell game - find the ball under cups."""

    def __init__(self, num_cups: int = 3, num_shuffles: int = 5):
        self.num_cups = num_cups
        self.num_shuffles = num_shuffles
        self.ball_position = 0
        self.shuffle_sequence: List[Tuple[int, int]] = []

    def start_game(self) -> int:
        """Place ball and return starting position."""
        self.ball_position = random.randint(0, self.num_cups - 1)
        return self.ball_position

    def generate_shuffles(self) -> List[Tuple[int, int]]:
        """Generate shuffle sequence. Returns list of (cup_a, cup_b) swaps."""
        self.shuffle_sequence = []
        for _ in range(self.num_shuffles):
            a = random.randint(0, self.num_cups - 1)
            b = random.randint(0, self.num_cups - 1)
            while b == a:
                b = random.randint(0, self.num_cups - 1)
            self.shuffle_sequence.append((a, b))

            # Track ball position
            if self.ball_position == a:
                self.ball_position = b
            elif self.ball_position == b:
                self.ball_position = a

        return self.shuffle_sequence

    def guess(self, cup_index: int) -> bool:
        """Check if guess is correct."""
        return cup_index == self.ball_position


class GamblingManager:
    """Manages all gambling activities.

    Implements the Saveable protocol for automatic save/load via SaveContext.
    """

    save_key: str = "gambling"

    def __init__(self):
        self.stats = GamblingStats()
        self.current_game: Optional[Any] = None
        self.current_bet: int = 0

    def can_afford(self, amount: int, world: "World") -> bool:
        """Check if player can afford bet."""
        try:
            amount = int(amount)
        except (TypeError, ValueError):
            return False
        if amount <= 0:
            return False

        gold = world.get_flag("gold", 0)
        if not isinstance(gold, (int, float)):
            gold = 0
        return int(gold) >= amount

    def place_bet(self, amount: int, world: "World") -> bool:
        """Place a bet. Returns False if can't afford."""
        self.current_bet = 0  # reset bet in case validation fails
        try:
            amount = int(amount)
        except (TypeError, ValueError):
            return False

        if amount <= 0:
            return False

        if not self.can_afford(amount, world):
            return False
        gold = world.get_flag("gold", 0)
        if not isinstance(gold, (int, float)):
            gold = 0
        world.set_flag("gold", int(gold) - amount)
        self.current_bet = amount
        self.stats.total_wagered += amount
        return True

    def win(self, multiplier: float, world: "World") -> int:
        """Player wins. Returns winnings."""
        winnings = int(self.current_bet * multiplier)
        gold = world.get_flag("gold", 0)
        if not isinstance(gold, (int, float)):
            gold = 0
        world.set_flag("gold", int(gold) + winnings)
        self.stats.total_won += winnings
        self.stats.games_played += 1

        profit = winnings - self.current_bet
        if profit > self.stats.biggest_win:
            self.stats.biggest_win = profit

        # Update streak
        if self.stats.current_streak >= 0:
            self.stats.current_streak += 1
        else:
            self.stats.current_streak = 1
        self.stats.best_streak = max(self.stats.best_streak, self.stats.current_streak)

        self.current_bet = 0
        return winnings

    def lose(self) -> None:
        """Player loses."""
        self.stats.total_lost += self.current_bet
        self.stats.games_played += 1

        if self.current_bet > self.stats.biggest_loss:
            self.stats.biggest_loss = self.current_bet

        # Update streak
        if self.stats.current_streak <= 0:
            self.stats.current_streak -= 1
        else:
            self.stats.current_streak = -1
        self.stats.worst_streak = min(self.stats.worst_streak, self.stats.current_streak)

        self.current_bet = 0

    def push(self, world: "World") -> None:
        """Tie - return bet."""
        gold = world.get_flag("gold", 0)
        if not isinstance(gold, (int, float)):
            gold = 0
        world.set_flag("gold", int(gold) + self.current_bet)
        self.stats.games_played += 1
        self.current_bet = 0

    def track_game_win(self, game_type: GamblingGameType) -> None:
        """Track a win for a specific game type."""
        if game_type == GamblingGameType.BLACKJACK:
            self.stats.blackjack_wins += 1
        elif game_type == GamblingGameType.DICE_ROLL:
            self.stats.dice_wins += 1
        elif game_type == GamblingGameType.SLOTS:
            self.stats.slots_wins += 1
        elif game_type == GamblingGameType.CUPS_GAME:
            self.stats.cups_wins += 1

    def serialize(self) -> Dict[str, Any]:
        """Serialize gambling stats."""
        return {
            "total_wagered": self.stats.total_wagered,
            "total_won": self.stats.total_won,
            "total_lost": self.stats.total_lost,
            "games_played": self.stats.games_played,
            "biggest_win": self.stats.biggest_win,
            "biggest_loss": self.stats.biggest_loss,
            "current_streak": self.stats.current_streak,
            "best_streak": self.stats.best_streak,
            "worst_streak": self.stats.worst_streak,
            "blackjack_wins": self.stats.blackjack_wins,
            "dice_wins": self.stats.dice_wins,
            "slots_wins": self.stats.slots_wins,
            "cups_wins": self.stats.cups_wins,
        }

    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> "GamblingManager":
        """Deserialize gambling stats."""
        manager = cls()
        if data:
            manager.stats.total_wagered = data.get("total_wagered", 0)
            manager.stats.total_won = data.get("total_won", 0)
            manager.stats.total_lost = data.get("total_lost", 0)
            manager.stats.games_played = data.get("games_played", 0)
            manager.stats.biggest_win = data.get("biggest_win", 0)
            manager.stats.biggest_loss = data.get("biggest_loss", 0)
            manager.stats.current_streak = data.get("current_streak", 0)
            manager.stats.best_streak = data.get("best_streak", 0)
            manager.stats.worst_streak = data.get("worst_streak", 0)
            manager.stats.blackjack_wins = data.get("blackjack_wins", 0)
            manager.stats.dice_wins = data.get("dice_wins", 0)
            manager.stats.slots_wins = data.get("slots_wins", 0)
            manager.stats.cups_wins = data.get("cups_wins", 0)
        return manager

    def deserialize_into(self, data: Dict[str, Any]) -> None:
        """Restore state from saved data (Saveable protocol)."""
        if data:
            self.stats.total_wagered = data.get("total_wagered", 0)
            self.stats.total_won = data.get("total_won", 0)
            self.stats.total_lost = data.get("total_lost", 0)
            self.stats.games_played = data.get("games_played", 0)
            self.stats.biggest_win = data.get("biggest_win", 0)
            self.stats.biggest_loss = data.get("biggest_loss", 0)
            self.stats.current_streak = data.get("current_streak", 0)
            self.stats.best_streak = data.get("best_streak", 0)
            self.stats.worst_streak = data.get("worst_streak", 0)
            self.stats.blackjack_wins = data.get("blackjack_wins", 0)
            self.stats.dice_wins = data.get("dice_wins", 0)
            self.stats.slots_wins = data.get("slots_wins", 0)
            self.stats.cups_wins = data.get("cups_wins", 0)

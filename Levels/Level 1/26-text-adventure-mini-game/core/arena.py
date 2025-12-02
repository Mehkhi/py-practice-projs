"""Monster arena betting system for spectating and betting on monster battles."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, TYPE_CHECKING
import random

if TYPE_CHECKING:
    from .world import World
    from .time_system import TimeOfDay


@dataclass
class ArenaFighter:
    """A monster that can fight in the arena."""

    fighter_id: str
    name: str
    sprite_id: str
    stats: Dict[str, int]  # hp, attack, defense, speed
    skills: List[str]
    odds: float  # Betting odds (2.0 = 2:1)
    wins: int = 0
    losses: int = 0

    @property
    def win_rate(self) -> float:
        """Calculate win rate based on wins and losses."""
        total = self.wins + self.losses
        return self.wins / total if total > 0 else 0.5


@dataclass
class ArenaMatch:
    """A single arena match."""

    match_id: str
    fighter_a: ArenaFighter
    fighter_b: ArenaFighter
    scheduled_time: Optional[str] = None  # TimeOfDay or None for anytime


@dataclass
class ArenaBet:
    """A bet placed on a match."""

    match_id: str
    fighter_id: str  # Who player bet on
    amount: int
    odds_at_bet: float  # Odds when bet was placed


class ArenaManager:
    """Manages the monster arena.

    Implements the Saveable protocol for automatic save/load via SaveContext.
    """

    save_key: str = "arena"

    def __init__(self, fighters: Dict[str, ArenaFighter], arena_schedule: Optional[Dict[str, Any]] = None):
        self.fighters = fighters
        self.arena_schedule = arena_schedule or {}
        self.current_matches: List[ArenaMatch] = []
        self.active_bets: List[ArenaBet] = []
        self.match_history: List[Dict] = []

    def generate_matches(self, count: int = 3) -> List[ArenaMatch]:
        """Generate random matchups for the day."""
        available = list(self.fighters.values())
        if len(available) < 2:
            return []

        random.shuffle(available)
        match_times = self.arena_schedule.get("match_times", [])

        matches: List[ArenaMatch] = []
        for i in range(count):
            a_index = (2 * i) % len(available)
            b_index = (2 * i + 1) % len(available)
            if a_index == b_index:
                b_index = (b_index + 1) % len(available)
            time_slot = match_times[i] if i < len(match_times) else None
            match = ArenaMatch(
                match_id=f"match_{len(self.match_history) + len(matches)}",
                fighter_a=available[a_index],
                fighter_b=available[b_index],
                scheduled_time=time_slot
            )
            matches.append(match)

        self.current_matches = matches
        return matches

    def place_bet(self, match: ArenaMatch, fighter_id: str,
                  amount: int, world: "World") -> Optional[ArenaBet]:
        """Place a bet on a fighter. Returns bet or None if failed."""
        gold = world.get_flag("gold", 0)
        if not isinstance(gold, (int, float)):
            gold = 0
        if int(gold) < amount:
            return None

        fighter = self.fighters.get(fighter_id)
        if not fighter or fighter_id not in [match.fighter_a.fighter_id,
                                              match.fighter_b.fighter_id]:
            return None

        world.set_flag("gold", int(gold) - amount)

        bet = ArenaBet(
            match_id=match.match_id,
            fighter_id=fighter_id,
            amount=amount,
            odds_at_bet=fighter.odds
        )
        self.active_bets.append(bet)
        return bet

    def simulate_match(self, match: ArenaMatch) -> Tuple[str, List[Dict]]:
        """
        Simulate a match between two fighters.

        Returns (winner_id, battle_log).

        Uses simplified combat - no player input.
        """
        # Create temporary stats for simulation
        a_hp = match.fighter_a.stats["hp"]
        b_hp = match.fighter_b.stats["hp"]

        log = []
        turn = 0

        while a_hp > 0 and b_hp > 0:
            turn += 1

            # Fighter A attacks
            damage = self._calculate_damage(match.fighter_a, match.fighter_b)
            b_hp -= damage
            log.append({
                "turn": turn,
                "attacker": match.fighter_a.name,
                "defender": match.fighter_b.name,
                "damage": damage,
                "defender_hp": max(0, b_hp)
            })

            if b_hp <= 0:
                break

            # Fighter B attacks
            damage = self._calculate_damage(match.fighter_b, match.fighter_a)
            a_hp -= damage
            log.append({
                "turn": turn,
                "attacker": match.fighter_b.name,
                "defender": match.fighter_a.name,
                "damage": damage,
                "defender_hp": max(0, a_hp)
            })

        winner_id = match.fighter_a.fighter_id if a_hp > 0 else match.fighter_b.fighter_id

        # Update records
        if winner_id == match.fighter_a.fighter_id:
            match.fighter_a.wins += 1
            match.fighter_b.losses += 1
        else:
            match.fighter_b.wins += 1
            match.fighter_a.losses += 1

        # Update odds based on win rates
        self._update_odds(match.fighter_a)
        self._update_odds(match.fighter_b)

        return winner_id, log

    def _calculate_damage(self, attacker: ArenaFighter,
                          defender: ArenaFighter) -> int:
        """Calculate damage with some randomness."""
        base = attacker.stats["attack"] - defender.stats["defense"] // 2
        variance = random.randint(-3, 3)
        return max(1, base + variance)

    def _update_odds(self, fighter: ArenaFighter) -> None:
        """Update odds based on win rate. Better fighters = lower payout."""
        win_rate = fighter.win_rate
        # Win rate 0.5 = 2.0 odds, 0.8 = 1.25 odds, 0.2 = 5.0 odds
        if win_rate > 0:
            fighter.odds = max(1.1, min(10.0, 1.0 / win_rate))
        else:
            fighter.odds = 5.0

    def resolve_bets(self, match: ArenaMatch, winner_id: str,
                     world: "World") -> List[Tuple[ArenaBet, int]]:
        """
        Resolve all bets for a match.

        Returns list of (bet, winnings) tuples.
        """
        results = []
        remaining_bets = []

        for bet in self.active_bets:
            if bet.match_id == match.match_id:
                if bet.fighter_id == winner_id:
                    winnings = int(bet.amount * bet.odds_at_bet)
                    gold = world.get_flag("gold", 0)
                    if not isinstance(gold, (int, float)):
                        gold = 0
                    world.set_flag("gold", int(gold) + winnings)
                    results.append((bet, winnings))
                else:
                    results.append((bet, 0))
            else:
                remaining_bets.append(bet)

        self.active_bets = remaining_bets
        self.match_history.append({
            "match_id": match.match_id,
            "fighter_a": match.fighter_a.fighter_id,
            "fighter_b": match.fighter_b.fighter_id,
            "winner": winner_id,
            "bets": [
                {
                    "fighter_id": bet.fighter_id,
                    "amount": bet.amount,
                    "winnings": winnings
                }
                for bet, winnings in results
            ]
        })
        return results

    def get_current_match(self, time_of_day: "TimeOfDay") -> Optional[ArenaMatch]:
        """Get match happening at current time, if any."""
        time_str = time_of_day.value.upper()
        schedule = self.arena_schedule.get("match_times", [])

        if time_str in schedule:
            index = schedule.index(time_str)
            if index < len(self.current_matches):
                return self.current_matches[index]
        return None

    def serialize(self) -> Dict[str, Any]:
        """Serialize arena state."""
        return {
            "fighters": {
                fighter_id: {
                    "wins": fighter.wins,
                    "losses": fighter.losses,
                    "odds": fighter.odds
                }
                for fighter_id, fighter in self.fighters.items()
            },
            "current_matches": [
                {
                    "match_id": match.match_id,
                    "fighter_a_id": match.fighter_a.fighter_id,
                    "fighter_b_id": match.fighter_b.fighter_id,
                    "scheduled_time": match.scheduled_time
                }
                for match in self.current_matches
            ],
            "active_bets": [
                {
                    "match_id": bet.match_id,
                    "fighter_id": bet.fighter_id,
                    "amount": bet.amount,
                    "odds_at_bet": bet.odds_at_bet
                }
                for bet in self.active_bets
            ],
            "match_history": self.match_history
        }

    @classmethod
    def deserialize(cls, data: Dict[str, Any], fighter_defs: Dict[str, ArenaFighter]) -> "ArenaManager":
        """Deserialize arena state."""
        # Restore fighter records
        fighters = {}
        fighter_data = data.get("fighters", {})
        for fighter_id, fighter_def in fighter_defs.items():
            fighter = ArenaFighter(
                fighter_id=fighter_def.fighter_id,
                name=fighter_def.name,
                sprite_id=fighter_def.sprite_id,
                stats=fighter_def.stats.copy(),
                skills=fighter_def.skills.copy(),
                odds=fighter_def.odds,
                wins=0,
                losses=0
            )
            if fighter_id in fighter_data:
                fighter.wins = fighter_data[fighter_id].get("wins", 0)
                fighter.losses = fighter_data[fighter_id].get("losses", 0)
                fighter.odds = fighter_data[fighter_id].get("odds", fighter.odds)
            fighters[fighter_id] = fighter

        # Restore matches
        manager = cls(fighters, data.get("arena_schedule"))
        matches_data = data.get("current_matches", [])
        current_matches = []
        for match_data in matches_data:
            fighter_a_id = match_data.get("fighter_a_id")
            fighter_b_id = match_data.get("fighter_b_id")
            if fighter_a_id in fighters and fighter_b_id in fighters:
                match = ArenaMatch(
                    match_id=match_data.get("match_id", ""),
                    fighter_a=fighters[fighter_a_id],
                    fighter_b=fighters[fighter_b_id],
                    scheduled_time=match_data.get("scheduled_time")
                )
                current_matches.append(match)
        manager.current_matches = current_matches

        # Restore active bets
        bets_data = data.get("active_bets", [])
        manager.active_bets = [
            ArenaBet(
                match_id=bet_data.get("match_id", ""),
                fighter_id=bet_data.get("fighter_id", ""),
                amount=bet_data.get("amount", 0),
                odds_at_bet=bet_data.get("odds_at_bet", 1.0)
            )
            for bet_data in bets_data
        ]

        manager.match_history = data.get("match_history", [])
        return manager

    def deserialize_into(self, data: Dict[str, Any]) -> None:
        """Restore state from saved data (Saveable protocol)."""
        # Restore fighter records
        fighter_data = data.get("fighters", {})
        for fighter_id, fighter in self.fighters.items():
            if fighter_id in fighter_data:
                fighter.wins = fighter_data[fighter_id].get("wins", 0)
                fighter.losses = fighter_data[fighter_id].get("losses", 0)
                fighter.odds = fighter_data[fighter_id].get("odds", fighter.odds)

        # Restore matches
        matches_data = data.get("current_matches", [])
        self.current_matches = []
        for match_data in matches_data:
            fighter_a_id = match_data.get("fighter_a_id")
            fighter_b_id = match_data.get("fighter_b_id")
            if fighter_a_id in self.fighters and fighter_b_id in self.fighters:
                match = ArenaMatch(
                    match_id=match_data.get("match_id", ""),
                    fighter_a=self.fighters[fighter_a_id],
                    fighter_b=self.fighters[fighter_b_id],
                    scheduled_time=match_data.get("scheduled_time")
                )
                self.current_matches.append(match)

        # Restore active bets
        bets_data = data.get("active_bets", [])
        self.active_bets = [
            ArenaBet(
                match_id=bet_data.get("match_id", ""),
                fighter_id=bet_data.get("fighter_id", ""),
                amount=bet_data.get("amount", 0),
                odds_at_bet=bet_data.get("odds_at_bet", 1.0)
            )
            for bet_data in bets_data
        ]

        self.match_history = data.get("match_history", [])

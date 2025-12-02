"""Unit tests for core/arena.py - Monster arena betting system."""

import unittest
from unittest.mock import Mock

from core.arena import (
    ArenaFighter,
    ArenaMatch,
    ArenaBet,
    ArenaManager,
)
from core.world import World
from core.time_system import TimeOfDay


class TestArenaFighter(unittest.TestCase):
    def test_win_rate_calculation(self):
        fighter = ArenaFighter(
            fighter_id="test",
            name="Test Fighter",
            sprite_id="test_sprite",
            stats={"hp": 100, "attack": 20, "defense": 10, "speed": 15},
            skills=[],
            odds=2.0,
            wins=5,
            losses=5
        )
        self.assertEqual(fighter.win_rate, 0.5)

    def test_win_rate_no_matches(self):
        fighter = ArenaFighter(
            fighter_id="test",
            name="Test Fighter",
            sprite_id="test_sprite",
            stats={"hp": 100, "attack": 20, "defense": 10, "speed": 15},
            skills=[],
            odds=2.0
        )
        self.assertEqual(fighter.win_rate, 0.5)  # Default when no matches

    def test_win_rate_all_wins(self):
        fighter = ArenaFighter(
            fighter_id="test",
            name="Test Fighter",
            sprite_id="test_sprite",
            stats={"hp": 100, "attack": 20, "defense": 10, "speed": 15},
            skills=[],
            odds=2.0,
            wins=10,
            losses=0
        )
        self.assertEqual(fighter.win_rate, 1.0)


class TestArenaManager(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        self.fighter_a = ArenaFighter(
            fighter_id="fighter_a",
            name="Fighter A",
            sprite_id="sprite_a",
            stats={"hp": 100, "attack": 20, "defense": 10, "speed": 15},
            skills=["skill1"],
            odds=2.0
        )
        self.fighter_b = ArenaFighter(
            fighter_id="fighter_b",
            name="Fighter B",
            sprite_id="sprite_b",
            stats={"hp": 80, "attack": 25, "defense": 8, "speed": 20},
            skills=["skill2"],
            odds=1.8
        )
        self.fighters = {
            "fighter_a": self.fighter_a,
            "fighter_b": self.fighter_b
        }
        self.manager = ArenaManager(self.fighters)

    def test_match_generation(self):
        """Test that matches are generated with valid pairings."""
        matches = self.manager.generate_matches(1)
        self.assertEqual(len(matches), 1)
        match = matches[0]
        self.assertIn(match.fighter_a.fighter_id, ["fighter_a", "fighter_b"])
        self.assertIn(match.fighter_b.fighter_id, ["fighter_a", "fighter_b"])
        self.assertNotEqual(match.fighter_a.fighter_id, match.fighter_b.fighter_id)

    def test_match_generation_multiple(self):
        """Test generating multiple matches."""
        # Add more fighters for multiple matches
        fighter_c = ArenaFighter(
            fighter_id="fighter_c",
            name="Fighter C",
            sprite_id="sprite_c",
            stats={"hp": 90, "attack": 22, "defense": 12, "speed": 18},
            skills=[],
            odds=2.2
        )
        fighter_d = ArenaFighter(
            fighter_id="fighter_d",
            name="Fighter D",
            sprite_id="sprite_d",
            stats={"hp": 110, "attack": 18, "defense": 15, "speed": 12},
            skills=[],
            odds=1.9
        )
        self.manager.fighters["fighter_c"] = fighter_c
        self.manager.fighters["fighter_d"] = fighter_d

        matches = self.manager.generate_matches(2)
        self.assertEqual(len(matches), 2)

    def test_bet_placement(self):
        """Test that bets correctly deduct gold."""
        world = World()
        world.set_flag("gold", 1000)

        match = ArenaMatch(
            match_id="test_match",
            fighter_a=self.fighter_a,
            fighter_b=self.fighter_b
        )
        self.manager.current_matches = [match]

        bet = self.manager.place_bet(match, "fighter_a", 100, world)
        self.assertIsNotNone(bet)
        self.assertEqual(world.get_flag("gold"), 900)
        self.assertEqual(bet.amount, 100)
        self.assertEqual(bet.fighter_id, "fighter_a")

    def test_bet_on_invalid_fighter(self):
        """Test that betting on non-participant fails."""
        world = World()
        world.set_flag("gold", 1000)

        match = ArenaMatch(
            match_id="test_match",
            fighter_a=self.fighter_a,
            fighter_b=self.fighter_b
        )

        bet = self.manager.place_bet(match, "invalid_fighter", 100, world)
        self.assertIsNone(bet)
        self.assertEqual(world.get_flag("gold"), 1000)  # Gold not deducted

    def test_bet_insufficient_gold(self):
        """Test that betting with insufficient gold fails."""
        world = World()
        world.set_flag("gold", 50)

        match = ArenaMatch(
            match_id="test_match",
            fighter_a=self.fighter_a,
            fighter_b=self.fighter_b
        )

        bet = self.manager.place_bet(match, "fighter_a", 100, world)
        self.assertIsNone(bet)
        self.assertEqual(world.get_flag("gold"), 50)  # Gold unchanged

    def test_match_simulation(self):
        """Test that simulation produces valid winner."""
        match = ArenaMatch(
            match_id="test_match",
            fighter_a=self.fighter_a,
            fighter_b=self.fighter_b
        )

        winner_id, battle_log = self.manager.simulate_match(match)

        self.assertIn(winner_id, ["fighter_a", "fighter_b"])
        self.assertGreater(len(battle_log), 0)
        # Check that log entries have required fields
        for entry in battle_log:
            self.assertIn("turn", entry)
            self.assertIn("attacker", entry)
            self.assertIn("defender", entry)
            self.assertIn("damage", entry)
            self.assertIn("defender_hp", entry)

    def test_bet_resolution_win(self):
        """Test that winning bets pay out correctly."""
        world = World()
        world.set_flag("gold", 1000)

        match = ArenaMatch(
            match_id="test_match",
            fighter_a=self.fighter_a,
            fighter_b=self.fighter_b
        )

        # Place bet
        bet = self.manager.place_bet(match, "fighter_a", 100, world)
        self.assertIsNotNone(bet)

        # Simulate match (set winner manually for test)
        winner_id = "fighter_a"

        # Resolve bets
        results = self.manager.resolve_bets(match, winner_id, world)

        self.assertEqual(len(results), 1)
        bet_result, winnings = results[0]
        self.assertEqual(bet_result.fighter_id, "fighter_a")
        self.assertEqual(winnings, int(100 * 2.0))  # 100 * odds
        self.assertEqual(world.get_flag("gold"), 1000 - 100 + 200)  # Original - bet + winnings

    def test_bet_resolution_loss(self):
        """Test that losing bets return nothing."""
        world = World()
        world.set_flag("gold", 1000)

        match = ArenaMatch(
            match_id="test_match",
            fighter_a=self.fighter_a,
            fighter_b=self.fighter_b
        )

        # Place bet
        bet = self.manager.place_bet(match, "fighter_a", 100, world)
        self.assertIsNotNone(bet)

        # Simulate match (winner is fighter_b)
        winner_id = "fighter_b"

        # Resolve bets
        results = self.manager.resolve_bets(match, winner_id, world)

        self.assertEqual(len(results), 1)
        bet_result, winnings = results[0]
        self.assertEqual(bet_result.fighter_id, "fighter_a")
        self.assertEqual(winnings, 0)
        self.assertEqual(world.get_flag("gold"), 1000 - 100)  # Only bet deducted

    def test_odds_update(self):
        """Test that odds adjust based on win rate."""
        fighter = ArenaFighter(
            fighter_id="test",
            name="Test",
            sprite_id="test",
            stats={"hp": 100, "attack": 20, "defense": 10, "speed": 15},
            skills=[],
            odds=2.0
        )

        # Win 8 out of 10 matches
        fighter.wins = 8
        fighter.losses = 2

        self.manager._update_odds(fighter)
        # Win rate = 0.8, so odds should be around 1.25 (1.0 / 0.8)
        self.assertLess(fighter.odds, 2.0)
        self.assertGreaterEqual(fighter.odds, 1.1)

    def test_fighter_records(self):
        """Test that win/loss records update after matches."""
        match = ArenaMatch(
            match_id="test_match",
            fighter_a=self.fighter_a,
            fighter_b=self.fighter_b
        )

        initial_wins_a = self.fighter_a.wins
        initial_losses_b = self.fighter_b.losses

        winner_id, _ = self.manager.simulate_match(match)

        if winner_id == "fighter_a":
            self.assertEqual(self.fighter_a.wins, initial_wins_a + 1)
            self.assertEqual(self.fighter_b.losses, initial_losses_b + 1)
        else:
            self.assertEqual(self.fighter_b.wins, initial_losses_b + 1)
            self.assertEqual(self.fighter_a.losses, initial_wins_a + 1)

    def test_scheduled_matches(self):
        """Test that matches appear at correct times."""
        schedule = {
            "match_times": ["MORNING", "AFTERNOON", "EVENING"],
            "matches_per_day": 3
        }
        manager = ArenaManager(self.fighters, schedule)
        manager.generate_matches(3)

        # Check morning match
        morning_match = manager.get_current_match(TimeOfDay.MORNING)
        self.assertIsNotNone(morning_match)

        # Check afternoon match
        afternoon_match = manager.get_current_match(TimeOfDay.AFTERNOON)
        self.assertIsNotNone(afternoon_match)

        # Check evening match
        evening_match = manager.get_current_match(TimeOfDay.EVENING)
        self.assertIsNotNone(evening_match)

        # Check that non-scheduled time returns None
        midnight_match = manager.get_current_match(TimeOfDay.MIDNIGHT)
        self.assertIsNone(midnight_match)

    def test_serialize_deserialize(self):
        """Test that arena state persists through serialization."""
        # Set up some state
        match = ArenaMatch(
            match_id="test_match",
            fighter_a=self.fighter_a,
            fighter_b=self.fighter_b
        )
        self.manager.current_matches = [match]
        self.fighter_a.wins = 5
        self.fighter_a.losses = 3
        self.fighter_a.odds = 1.5

        # Serialize
        data = self.manager.serialize()

        # Deserialize
        restored = ArenaManager.deserialize(data, self.fighters)

        # Check fighter records
        self.assertEqual(restored.fighters["fighter_a"].wins, 5)
        self.assertEqual(restored.fighters["fighter_a"].losses, 3)
        self.assertEqual(restored.fighters["fighter_a"].odds, 1.5)

        # Check matches
        self.assertEqual(len(restored.current_matches), 1)
        self.assertEqual(restored.current_matches[0].match_id, "test_match")

    def test_calculate_damage(self):
        """Test damage calculation."""
        attacker = ArenaFighter(
            fighter_id="attacker",
            name="Attacker",
            sprite_id="attacker",
            stats={"hp": 100, "attack": 30, "defense": 10, "speed": 15},
            skills=[],
            odds=2.0
        )
        defender = ArenaFighter(
            fighter_id="defender",
            name="Defender",
            sprite_id="defender",
            stats={"hp": 100, "attack": 20, "defense": 20, "speed": 15},
            skills=[],
            odds=2.0
        )

        damage = self.manager._calculate_damage(attacker, defender)
        # Base = 30 - (20 // 2) = 20, plus variance -3 to +3
        # So damage should be between 17 and 23, but minimum 1
        self.assertGreaterEqual(damage, 1)
        self.assertLessEqual(damage, 30)  # Reasonable upper bound


if __name__ == "__main__":
    unittest.main()

"""Unit tests for core/gambling.py - Gambling games and statistics."""

import unittest
from unittest.mock import Mock

from core.gambling import (
    GamblingGameType,
    GamblingStats,
    GamblingManager,
    DiceGame,
    BlackjackGame,
    SlotsGame,
    CupsGame,
)
from core.world import World


class TestDiceGame(unittest.TestCase):
    def test_roll_generates_two_dice(self):
        game = DiceGame()
        roll = game.roll()
        self.assertEqual(len(roll), 2)
        self.assertTrue(all(1 <= die <= 6 for die in roll))

    def test_get_total_sums_dice(self):
        game = DiceGame()
        game.last_roll = [3, 4]
        self.assertEqual(game.get_total(), 7)

    def test_check_high_low_high_wins(self):
        game = DiceGame()
        game.last_roll = [4, 5]  # Total = 9
        result = game.check_high_low("high")
        self.assertTrue(result)

    def test_check_high_low_low_wins(self):
        game = DiceGame()
        game.last_roll = [1, 2]  # Total = 3
        result = game.check_high_low("low")
        self.assertTrue(result)

    def test_check_high_low_seven_is_push(self):
        game = DiceGame()
        game.last_roll = [3, 4]  # Total = 7
        result = game.check_high_low("high")
        self.assertIsNone(result)

    def test_check_high_low_wrong_guess_loses(self):
        game = DiceGame()
        game.last_roll = [1, 2]  # Total = 3 (low)
        result = game.check_high_low("high")
        self.assertFalse(result)


class TestBlackjackGame(unittest.TestCase):
    def test_deal_initial_deals_four_cards(self):
        game = BlackjackGame()
        game.deal_initial()
        self.assertEqual(len(game.player_hand), 2)
        self.assertEqual(len(game.dealer_hand), 2)
        self.assertEqual(len(game.deck), 52 - 4)

    def test_get_hand_value_number_cards(self):
        game = BlackjackGame()
        hand = [("5", "hearts"), ("7", "diamonds")]
        self.assertEqual(game.get_hand_value(hand), 12)

    def test_get_hand_value_face_cards(self):
        game = BlackjackGame()
        hand = [("J", "hearts"), ("Q", "diamonds")]
        self.assertEqual(game.get_hand_value(hand), 20)

    def test_get_hand_value_ace_as_eleven(self):
        game = BlackjackGame()
        hand = [("A", "hearts"), ("5", "diamonds")]
        self.assertEqual(game.get_hand_value(hand), 16)

    def test_get_hand_value_ace_adjusts_to_one(self):
        game = BlackjackGame()
        hand = [("A", "hearts"), ("K", "diamonds"), ("Q", "clubs")]
        # A(11) + K(10) + Q(10) = 31, should adjust A to 1 = 21
        self.assertEqual(game.get_hand_value(hand), 21)

    def test_get_hand_value_multiple_aces(self):
        game = BlackjackGame()
        hand = [("A", "hearts"), ("A", "diamonds"), ("9", "clubs")]
        # A(11) + A(11) + 9 = 31, adjust both Aces = 21
        self.assertEqual(game.get_hand_value(hand), 21)

    def test_is_bust_detects_over_21(self):
        game = BlackjackGame()
        hand = [("K", "hearts"), ("Q", "diamonds"), ("J", "clubs")]
        self.assertTrue(game.is_bust(hand))

    def test_is_bust_not_bust_at_21(self):
        game = BlackjackGame()
        hand = [("A", "hearts"), ("K", "diamonds")]
        self.assertFalse(game.is_bust(hand))

    def test_hit_adds_card(self):
        game = BlackjackGame()
        initial_deck_size = len(game.deck)
        game.deal_initial()
        game.hit()
        self.assertEqual(len(game.player_hand), 3)
        self.assertEqual(len(game.deck), initial_deck_size - 5)

    def test_dealer_play_draws_until_17_plus(self):
        game = BlackjackGame()
        game.deal_initial()
        # Manually set dealer hand to low value
        game.dealer_hand = [("6", "hearts"), ("5", "diamonds")]  # 11
        game.dealer_play()
        dealer_val = game.get_hand_value(game.dealer_hand)
        self.assertGreaterEqual(dealer_val, 17)

    def test_determine_winner_player_wins(self):
        game = BlackjackGame()
        game.player_hand = [("K", "hearts"), ("Q", "diamonds")]
        game.dealer_hand = [("9", "hearts"), ("8", "diamonds")]
        self.assertEqual(game.determine_winner(), "player")

    def test_determine_winner_dealer_wins(self):
        game = BlackjackGame()
        game.player_hand = [("9", "hearts"), ("8", "diamonds")]
        game.dealer_hand = [("K", "hearts"), ("Q", "diamonds")]
        self.assertEqual(game.determine_winner(), "dealer")

    def test_determine_winner_push(self):
        game = BlackjackGame()
        game.player_hand = [("K", "hearts"), ("Q", "diamonds")]
        game.dealer_hand = [("K", "diamonds"), ("Q", "clubs")]
        self.assertEqual(game.determine_winner(), "push")

    def test_determine_winner_player_bust(self):
        game = BlackjackGame()
        game.player_hand = [("K", "hearts"), ("Q", "diamonds"), ("J", "clubs")]
        game.dealer_hand = [("9", "hearts"), ("8", "diamonds")]
        self.assertEqual(game.determine_winner(), "dealer")


class TestSlotsGame(unittest.TestCase):
    def test_spin_generates_three_reels(self):
        game = SlotsGame()
        reels = game.spin()
        self.assertEqual(len(reels), 3)
        self.assertTrue(all(symbol in game.SYMBOLS for symbol in reels))

    def test_get_payout_multiplier_jackpot(self):
        game = SlotsGame()
        game.reels = ["seven", "seven", "seven"]
        self.assertEqual(game.get_payout_multiplier(), 100)

    def test_get_payout_multiplier_triple_bar(self):
        game = SlotsGame()
        game.reels = ["bar", "bar", "bar"]
        self.assertEqual(game.get_payout_multiplier(), 50)

    def test_get_payout_multiplier_triple_cherry(self):
        game = SlotsGame()
        game.reels = ["cherry", "cherry", "cherry"]
        self.assertEqual(game.get_payout_multiplier(), 10)

    def test_get_payout_multiplier_two_cherries(self):
        game = SlotsGame()
        game.reels = ["cherry", "cherry", "lemon"]
        self.assertEqual(game.get_payout_multiplier(), 5)

    def test_get_payout_multiplier_one_cherry(self):
        game = SlotsGame()
        game.reels = ["cherry", "lemon", "orange"]
        self.assertEqual(game.get_payout_multiplier(), 2)

    def test_get_payout_multiplier_no_win(self):
        game = SlotsGame()
        game.reels = ["lemon", "orange", "plum"]
        self.assertEqual(game.get_payout_multiplier(), 0)

    def test_is_jackpot_detects_triple_sevens(self):
        game = SlotsGame()
        game.reels = ["seven", "seven", "seven"]
        self.assertTrue(game.is_jackpot())

    def test_is_jackpot_false_for_other_combos(self):
        game = SlotsGame()
        game.reels = ["seven", "seven", "bar"]
        self.assertFalse(game.is_jackpot())


class TestCupsGame(unittest.TestCase):
    def test_start_game_places_ball(self):
        game = CupsGame()
        pos = game.start_game()
        self.assertGreaterEqual(pos, 0)
        self.assertLess(pos, game.num_cups)

    def test_generate_shuffles_creates_sequence(self):
        game = CupsGame()
        game.ball_position = 0
        shuffles = game.generate_shuffles()
        self.assertEqual(len(shuffles), game.num_shuffles)
        self.assertTrue(all(0 <= a < game.num_cups and 0 <= b < game.num_cups for a, b in shuffles))

    def test_generate_shuffles_tracks_ball(self):
        game = CupsGame(num_cups=3, num_shuffles=1)
        game.ball_position = 0
        shuffles = game.generate_shuffles()
        # Ball should have moved if shuffle swapped its position
        final_pos = game.ball_position
        self.assertGreaterEqual(final_pos, 0)
        self.assertLess(final_pos, game.num_cups)

    def test_guess_correct(self):
        game = CupsGame()
        game.ball_position = 1
        self.assertTrue(game.guess(1))

    def test_guess_incorrect(self):
        game = CupsGame()
        game.ball_position = 1
        self.assertFalse(game.guess(0))


class TestGamblingManager(unittest.TestCase):
    def setUp(self):
        self.world = World()
        self.world.set_flag("gold", 1000)
        self.manager = GamblingManager()

    def test_can_afford_sufficient_gold(self):
        self.assertTrue(self.manager.can_afford(500, self.world))

    def test_can_afford_insufficient_gold(self):
        self.assertFalse(self.manager.can_afford(2000, self.world))

    def test_place_bet_deducts_gold(self):
        initial_gold = self.world.get_flag("gold", 0)
        self.manager.place_bet(100, self.world)
        new_gold = self.world.get_flag("gold", 0)
        self.assertEqual(new_gold, initial_gold - 100)
        self.assertEqual(self.manager.current_bet, 100)

    def test_place_bet_updates_wagered(self):
        self.manager.place_bet(100, self.world)
        self.assertEqual(self.manager.stats.total_wagered, 100)

    def test_place_bet_fails_insufficient_funds(self):
        self.world.set_flag("gold", 50)
        result = self.manager.place_bet(100, self.world)
        self.assertFalse(result)
        self.assertEqual(self.world.get_flag("gold", 0), 50)

    def test_win_adds_gold(self):
        self.manager.current_bet = 100
        initial_gold = self.world.get_flag("gold", 0)
        winnings = self.manager.win(2.0, self.world)
        new_gold = self.world.get_flag("gold", 0)
        self.assertEqual(winnings, 200)
        self.assertEqual(new_gold, initial_gold + 200)
        self.assertEqual(self.manager.stats.total_won, 200)

    def test_win_updates_biggest_win(self):
        self.manager.current_bet = 100
        self.manager.win(2.0, self.world)
        self.assertEqual(self.manager.stats.biggest_win, 100)  # Profit = 200 - 100

    def test_win_updates_streak_positive(self):
        self.manager.stats.current_streak = 2
        self.manager.current_bet = 100
        self.manager.win(2.0, self.world)
        self.assertEqual(self.manager.stats.current_streak, 3)
        self.assertEqual(self.manager.stats.best_streak, 3)

    def test_win_resets_negative_streak(self):
        self.manager.stats.current_streak = -2
        self.manager.current_bet = 100
        self.manager.win(2.0, self.world)
        self.assertEqual(self.manager.stats.current_streak, 1)

    def test_lose_updates_total_lost(self):
        self.manager.current_bet = 100
        self.manager.lose()
        self.assertEqual(self.manager.stats.total_lost, 100)

    def test_lose_updates_biggest_loss(self):
        self.manager.current_bet = 200
        self.manager.lose()
        self.assertEqual(self.manager.stats.biggest_loss, 200)

    def test_lose_updates_streak_negative(self):
        self.manager.stats.current_streak = -2
        self.manager.current_bet = 100
        self.manager.lose()
        self.assertEqual(self.manager.stats.current_streak, -3)
        self.assertEqual(self.manager.stats.worst_streak, -3)

    def test_lose_resets_positive_streak(self):
        self.manager.stats.current_streak = 3
        self.manager.current_bet = 100
        self.manager.lose()
        self.assertEqual(self.manager.stats.current_streak, -1)

    def test_push_returns_bet(self):
        self.manager.current_bet = 100
        initial_gold = self.world.get_flag("gold", 0)
        self.manager.push(self.world)
        new_gold = self.world.get_flag("gold", 0)
        self.assertEqual(new_gold, initial_gold + 100)

    def test_track_game_win_blackjack(self):
        self.manager.track_game_win(GamblingGameType.BLACKJACK)
        self.assertEqual(self.manager.stats.blackjack_wins, 1)

    def test_track_game_win_dice(self):
        self.manager.track_game_win(GamblingGameType.DICE_ROLL)
        self.assertEqual(self.manager.stats.dice_wins, 1)

    def test_track_game_win_slots(self):
        self.manager.track_game_win(GamblingGameType.SLOTS)
        self.assertEqual(self.manager.stats.slots_wins, 1)

    def test_track_game_win_cups(self):
        self.manager.track_game_win(GamblingGameType.CUPS_GAME)
        self.assertEqual(self.manager.stats.cups_wins, 1)

    def test_serialize_contains_all_stats(self):
        self.manager.stats.total_wagered = 500
        self.manager.stats.total_won = 600
        self.manager.stats.best_streak = 5
        data = self.manager.serialize()
        self.assertEqual(data["total_wagered"], 500)
        self.assertEqual(data["total_won"], 600)
        self.assertEqual(data["best_streak"], 5)
        self.assertIn("blackjack_wins", data)
        self.assertIn("dice_wins", data)
        self.assertIn("slots_wins", data)
        self.assertIn("cups_wins", data)

    def test_deserialize_restores_stats(self):
        data = {
            "total_wagered": 500,
            "total_won": 600,
            "total_lost": 400,
            "games_played": 10,
            "biggest_win": 200,
            "biggest_loss": 150,
            "current_streak": 3,
            "best_streak": 5,
            "worst_streak": -2,
            "blackjack_wins": 2,
            "dice_wins": 3,
            "slots_wins": 1,
            "cups_wins": 1,
        }
        manager = GamblingManager.deserialize(data)
        self.assertEqual(manager.stats.total_wagered, 500)
        self.assertEqual(manager.stats.total_won, 600)
        self.assertEqual(manager.stats.blackjack_wins, 2)

    def test_deserialize_empty_data(self):
        manager = GamblingManager.deserialize({})
        self.assertEqual(manager.stats.total_wagered, 0)
        self.assertEqual(manager.stats.total_won, 0)

    def test_deserialize_none_data(self):
        manager = GamblingManager.deserialize(None)
        self.assertEqual(manager.stats.total_wagered, 0)


if __name__ == "__main__":
    unittest.main()

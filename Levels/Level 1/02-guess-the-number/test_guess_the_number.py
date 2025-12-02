#!/usr/bin/env python3
"""
Unit tests for the Guess the Number Game
"""

import unittest
import tempfile
import os
from guess_the_number import GuessTheNumberGame


class TestGuessTheNumberGame(unittest.TestCase):
    """Test cases for GuessTheNumberGame class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create temporary files for testing
        self.temp_scores_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_leaderboard_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_scores_file.close()
        self.temp_leaderboard_file.close()

        # Create game instance with temporary files
        self.game = GuessTheNumberGame()
        self.game.scores_file = self.temp_scores_file.name
        self.game.leaderboard_file = self.temp_leaderboard_file.name

    def tearDown(self):
        """Clean up test fixtures."""
        # Remove temporary files
        for temp_file in [self.temp_scores_file.name, self.temp_leaderboard_file.name]:
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    def test_difficulty_levels(self):
        """Test difficulty level configurations."""
        expected_levels = ['easy', 'medium', 'hard', 'expert']
        self.assertEqual(list(self.game.difficulty_levels.keys()), expected_levels)

        # Test easy level
        easy = self.game.difficulty_levels['easy']
        self.assertEqual(easy['min'], 1)
        self.assertEqual(easy['max'], 10)
        self.assertEqual(easy['attempts'], 5)

        # Test expert level
        expert = self.game.difficulty_levels['expert']
        self.assertEqual(expert['min'], 1)
        self.assertEqual(expert['max'], 1000)
        self.assertEqual(expert['attempts'], 15)

    def test_generate_secret_number(self):
        """Test secret number generation."""
        # Test easy difficulty
        self.game.current_difficulty = 'easy'
        secret = self.game.generate_secret_number()

        self.assertGreaterEqual(secret, 1)
        self.assertLessEqual(secret, 10)
        self.assertEqual(self.game.attempts_left, 5)
        self.assertEqual(self.game.total_attempts, 0)

        # Test expert difficulty
        self.game.current_difficulty = 'expert'
        secret = self.game.generate_secret_number()

        self.assertGreaterEqual(secret, 1)
        self.assertLessEqual(secret, 1000)
        self.assertEqual(self.game.attempts_left, 15)

    def test_validate_guess(self):
        """Test guess validation."""
        self.game.current_difficulty = 'medium'  # Range 1-50

        # Valid guesses
        self.assertEqual(self.game.validate_guess("25"), 25)
        self.assertEqual(self.game.validate_guess("1"), 1)
        self.assertEqual(self.game.validate_guess("50"), 50)

        # Invalid guesses
        self.assertIsNone(self.game.validate_guess("0"))  # Below range
        self.assertIsNone(self.game.validate_guess("51"))  # Above range
        self.assertIsNone(self.game.validate_guess("abc"))  # Non-numeric
        self.assertIsNone(self.game.validate_guess(""))  # Empty
        self.assertIsNone(self.game.validate_guess("25.5"))  # Float

    def test_get_hint(self):
        """Test hint generation."""
        self.game.secret_number = 25

        # Test hints
        self.assertEqual(self.game.get_hint(20), "Too low! Try a higher number.")
        self.assertEqual(self.game.get_hint(30), "Too high! Try a lower number.")
        self.assertEqual(self.game.get_hint(25), "Congratulations! You guessed it!")

    def test_calculate_score(self):
        """Test score calculation."""
        self.game.current_difficulty = 'medium'  # Range 1-50, multiplier 2

        # Test with different attempts
        self.game.attempts_left = 3  # Used 4 attempts out of 7
        score1 = self.game.calculate_score()

        self.game.attempts_left = 6  # Used 1 attempt out of 7
        score2 = self.game.calculate_score()

        # More attempts should result in lower score
        self.assertGreater(score2, score1)

        # Score should be positive
        self.assertGreater(score1, 0)
        self.assertGreater(score2, 0)

    def test_set_difficulty(self):
        """Test difficulty setting."""
        # Valid difficulties
        self.assertTrue(self.game.set_difficulty('easy'))
        self.assertEqual(self.game.current_difficulty, 'easy')

        self.assertTrue(self.game.set_difficulty('EXPERT'))
        self.assertEqual(self.game.current_difficulty, 'expert')

        # Invalid difficulty
        self.assertFalse(self.game.set_difficulty('invalid'))
        self.assertEqual(self.game.current_difficulty, 'expert')  # Should remain unchanged

    def test_update_leaderboard(self):
        """Test leaderboard updates."""
        # Add first player
        self.game.update_leaderboard("Alice", 100)
        self.assertEqual(len(self.game.leaderboard), 1)
        self.assertEqual(self.game.leaderboard[0]['name'], "Alice")
        self.assertEqual(self.game.leaderboard[0]['score'], 100)

        # Add second player
        self.game.update_leaderboard("Bob", 150)
        self.assertEqual(len(self.game.leaderboard), 2)

        # Leaderboard should be sorted by score
        self.assertEqual(self.game.leaderboard[0]['name'], "Bob")  # Higher score first
        self.assertEqual(self.game.leaderboard[1]['name'], "Alice")

        # Update existing player with higher score
        self.game.update_leaderboard("Alice", 200)
        self.assertEqual(len(self.game.leaderboard), 2)  # Still 2 players
        self.assertEqual(self.game.leaderboard[0]['name'], "Alice")  # Alice now first
        self.assertEqual(self.game.leaderboard[0]['score'], 200)

        # Update existing player with lower score (should not change)
        original_score = self.game.leaderboard[0]['score']
        self.game.update_leaderboard("Alice", 50)
        self.assertEqual(self.game.leaderboard[0]['score'], original_score)  # Should remain unchanged

    def test_add_to_history(self):
        """Test game history tracking."""
        initial_count = len(self.game.game_history)

        # Add winning game
        self.game.add_to_history(True, 100)
        self.assertEqual(len(self.game.game_history), initial_count + 1)

        # Add losing game
        self.game.add_to_history(False, 0)
        self.assertEqual(len(self.game.game_history), initial_count + 2)

        # Check game data
        last_game = self.game.game_history[-1]
        self.assertFalse(last_game['won'])
        self.assertEqual(last_game['score'], 0)
        self.assertIn('timestamp', last_game)

    def test_file_operations(self):
        """Test file save and load operations."""
        # Add some test data
        self.game.game_history = [{'test': 'data'}]
        self.game.leaderboard = [{'name': 'Test', 'score': 100}]

        # Save data
        self.game.save_data()

        # Create new game instance to test loading
        new_game = GuessTheNumberGame()
        new_game.scores_file = self.temp_scores_file.name
        new_game.leaderboard_file = self.temp_leaderboard_file.name
        new_game.load_data()

        # Verify data was loaded
        self.assertEqual(len(new_game.game_history), 1)
        self.assertEqual(len(new_game.leaderboard), 1)
        self.assertEqual(new_game.leaderboard[0]['name'], 'Test')


def run_tests():
    """Run all tests."""
    unittest.main(verbosity=2)


if __name__ == "__main__":
    run_tests()

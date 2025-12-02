#!/usr/bin/env python3
"""
Unit tests for Hangman Game

Tests all functionality of the HangmanGame class including:
- Word selection and categories
- Game logic and state management
- Guess processing and validation
- Win/lose conditions
- Difficulty levels
- ASCII art display
"""

import unittest
from hangman import HangmanGame


class TestHangmanGame(unittest.TestCase):
    """Test cases for HangmanGame class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.game = HangmanGame()

    def test_initialization(self):
        """Test game initialization with default values."""
        self.assertEqual(self.game.current_word, "")
        self.assertEqual(self.game.current_category, "")
        self.assertEqual(len(self.game.guessed_letters), 0)
        self.assertEqual(self.game.wrong_guesses, 0)
        self.assertEqual(self.game.max_attempts, 6)
        self.assertFalse(self.game.game_over)
        self.assertFalse(self.game.won)

    def test_word_categories_exist(self):
        """Test that word categories are properly initialized."""
        categories = self.game.get_available_categories()
        expected_categories = ["animals", "countries", "fruits", "sports"]
        self.assertEqual(sorted(categories), sorted(expected_categories))

        # Check that each category has words
        for category in expected_categories:
            self.assertGreater(len(self.game.word_categories[category]), 0)

    def test_difficulty_levels(self):
        """Test difficulty level configuration."""
        levels = self.game.get_difficulty_levels()

        self.assertIn("easy", levels)
        self.assertIn("medium", levels)
        self.assertIn("hard", levels)

        self.assertEqual(self.game.difficulty_levels["easy"]["max_attempts"], 8)
        self.assertEqual(self.game.difficulty_levels["medium"]["max_attempts"], 6)
        self.assertEqual(self.game.difficulty_levels["hard"]["max_attempts"], 4)

    def test_select_random_word_specific_category(self):
        """Test selecting a random word from a specific category."""
        word = self.game.select_random_word("animals")

        self.assertEqual(self.game.current_category, "animals")
        self.assertIn(word.lower(), self.game.word_categories["animals"])
        self.assertTrue(word.isupper())

    def test_select_random_word_random_category(self):
        """Test selecting a random word from random category."""
        word = self.game.select_random_word()

        self.assertIn(self.game.current_category, self.game.word_categories.keys())
        self.assertIn(
            word.lower(), self.game.word_categories[self.game.current_category]
        )
        self.assertTrue(word.isupper())

    def test_select_random_word_invalid_category(self):
        """Test selecting word with invalid category falls back to random."""
        word = self.game.select_random_word("invalid_category")

        self.assertIn(self.game.current_category, self.game.word_categories.keys())
        self.assertTrue(word.isupper())

    def test_get_word_progress_empty(self):
        """Test word progress display with no guesses."""
        self.game.current_word = "TEST"
        progress = self.game.get_word_progress()

        self.assertEqual(progress, "_ _ _ _")

    def test_get_word_progress_partial(self):
        """Test word progress display with some guesses."""
        self.game.current_word = "TEST"
        self.game.guessed_letters = {"T", "S"}
        progress = self.game.get_word_progress()

        self.assertEqual(progress, "T _ S T")

    def test_get_word_progress_complete(self):
        """Test word progress display with all letters guessed."""
        self.game.current_word = "TEST"
        self.game.guessed_letters = {"T", "E", "S"}
        progress = self.game.get_word_progress()

        self.assertEqual(progress, "T E S T")

    def test_make_guess_valid_correct(self):
        """Test making a valid correct guess."""
        self.game.current_word = "TEST"
        is_valid, message = self.game.make_guess("T")

        self.assertTrue(is_valid)
        self.assertIn("Good guess", message)
        self.assertIn("T", self.game.guessed_letters)
        self.assertEqual(self.game.wrong_guesses, 0)

    def test_make_guess_valid_incorrect(self):
        """Test making a valid incorrect guess."""
        self.game.current_word = "TEST"
        is_valid, message = self.game.make_guess("A")

        self.assertFalse(is_valid)
        self.assertIn("not in the word", message)
        self.assertIn("A", self.game.guessed_letters)
        self.assertEqual(self.game.wrong_guesses, 1)

    def test_make_guess_empty_input(self):
        """Test making guess with empty input."""
        is_valid, message = self.game.make_guess("")

        self.assertFalse(is_valid)
        self.assertEqual(message, "Please enter a single letter")

    def test_make_guess_multiple_characters(self):
        """Test making guess with multiple characters."""
        is_valid, message = self.game.make_guess("AB")

        self.assertFalse(is_valid)
        self.assertEqual(message, "Please enter a single letter")

    def test_make_guess_non_alpha(self):
        """Test making guess with non-alphabetic character."""
        is_valid, message = self.game.make_guess("1")

        self.assertFalse(is_valid)
        self.assertEqual(message, "Please enter a letter (A-Z)")

    def test_make_guess_already_guessed(self):
        """Test making guess with already guessed letter."""
        self.game.current_word = "TEST"
        self.game.guessed_letters.add("T")

        is_valid, message = self.game.make_guess("T")

        self.assertFalse(is_valid)
        self.assertEqual(message, "You already guessed 'T'")

    def test_make_guess_case_insensitive(self):
        """Test that guesses are case insensitive."""
        self.game.current_word = "TEST"

        # Test lowercase
        is_valid, message = self.game.make_guess("t")
        self.assertTrue(is_valid)
        self.assertIn("T", self.game.guessed_letters)

        # Test uppercase
        is_valid, message = self.game.make_guess("E")
        self.assertTrue(is_valid)
        self.assertIn("E", self.game.guessed_letters)

    def test_check_win_condition_true(self):
        """Test win condition when all letters are guessed."""
        self.game.current_word = "TEST"
        self.game.guessed_letters = {"T", "E", "S"}

        self.assertTrue(self.game.check_win_condition())

    def test_check_win_condition_false(self):
        """Test win condition when not all letters are guessed."""
        self.game.current_word = "TEST"
        self.game.guessed_letters = {"T", "E"}

        self.assertFalse(self.game.check_win_condition())

    def test_check_lose_condition_true(self):
        """Test lose condition when max attempts reached."""
        self.game.max_attempts = 6
        self.game.wrong_guesses = 6

        self.assertTrue(self.game.check_lose_condition())

    def test_check_lose_condition_false(self):
        """Test lose condition when attempts remaining."""
        self.game.max_attempts = 6
        self.game.wrong_guesses = 3

        self.assertFalse(self.game.check_lose_condition())

    def test_get_game_status(self):
        """Test getting complete game status."""
        self.game.current_word = "TEST"
        self.game.current_category = "animals"
        self.game.guessed_letters = {"T"}
        self.game.wrong_guesses = 2
        self.game.max_attempts = 6
        self.game.game_over = False
        self.game.won = False

        status = self.game.get_game_status()

        self.assertEqual(status["word"], "TEST")
        self.assertEqual(status["category"], "animals")
        self.assertEqual(status["progress"], "T _ _ T")
        self.assertEqual(status["guessed_letters"], ["T"])
        self.assertEqual(status["wrong_guesses"], 2)
        self.assertEqual(status["max_attempts"], 6)
        self.assertEqual(status["remaining_attempts"], 4)
        self.assertFalse(status["game_over"])
        self.assertFalse(status["won"])

    def test_get_hangman_display_stages(self):
        """Test hangman ASCII art at different stages."""
        # Test stage 0 (no wrong guesses)
        self.game.wrong_guesses = 0
        display = self.game.get_hangman_display()
        self.assertIn("-----", display)
        self.assertNotIn("O", display)

        # Test stage 1 (1 wrong guess)
        self.game.wrong_guesses = 1
        display = self.game.get_hangman_display()
        self.assertIn("O", display)

        # Test final stage (max wrong guesses)
        self.game.wrong_guesses = 10  # More than available stages
        display = self.game.get_hangman_display()
        self.assertIn("GAME", display)

    def test_start_new_game_with_category_and_difficulty(self):
        """Test starting new game with specific category and difficulty."""
        self.game.start_new_game("animals", "easy")

        self.assertEqual(self.game.current_category, "animals")
        self.assertEqual(self.game.max_attempts, 8)
        self.assertTrue(self.game.current_word.isupper())
        self.assertEqual(len(self.game.guessed_letters), 0)
        self.assertEqual(self.game.wrong_guesses, 0)
        self.assertFalse(self.game.game_over)
        self.assertFalse(self.game.won)

    def test_start_new_game_invalid_difficulty(self):
        """Test starting new game with invalid difficulty uses default."""
        self.game.start_new_game("animals", "invalid")

        self.assertEqual(self.game.current_category, "animals")
        self.assertEqual(self.game.max_attempts, 6)  # Default medium

    def test_reset_game(self):
        """Test resetting game state."""
        # Set up game with some state
        self.game.current_word = "TEST"
        self.game.current_category = "animals"
        self.game.guessed_letters = {"T", "E"}
        self.game.wrong_guesses = 3
        self.game.max_attempts = 8
        self.game.game_over = True
        self.game.won = True

        # Reset game
        self.game.reset_game()

        # Check all values are reset
        self.assertEqual(self.game.current_word, "")
        self.assertEqual(self.game.current_category, "")
        self.assertEqual(len(self.game.guessed_letters), 0)
        self.assertEqual(self.game.wrong_guesses, 0)
        self.assertEqual(self.game.max_attempts, 6)  # Default
        self.assertFalse(self.game.game_over)
        self.assertFalse(self.game.won)

    def test_complete_game_win_scenario(self):
        """Test a complete game scenario where player wins."""
        self.game.start_new_game("animals", "easy")
        self.game.current_word = "CAT"  # Override for predictable test

        # Make correct guesses
        self.game.make_guess("C")
        self.game.make_guess("A")
        self.game.make_guess("T")

        # Check win condition
        self.assertTrue(self.game.check_win_condition())
        self.assertFalse(self.game.check_lose_condition())
        self.assertEqual(self.game.get_word_progress(), "C A T")

    def test_complete_game_lose_scenario(self):
        """Test a complete game scenario where player loses."""
        self.game.start_new_game("animals", "easy")
        self.game.current_word = "CAT"  # Override for predictable test
        self.game.max_attempts = 3

        # Make incorrect guesses
        self.game.make_guess("X")
        self.game.make_guess("Y")
        self.game.make_guess("Z")

        # Check lose condition
        self.assertFalse(self.game.check_win_condition())
        self.assertTrue(self.game.check_lose_condition())
        self.assertEqual(self.game.wrong_guesses, 3)

    def test_word_with_repeated_letters(self):
        """Test game behavior with words containing repeated letters."""
        self.game.current_word = "BALLOON"

        # Guess repeated letter
        is_valid, message = self.game.make_guess("L")
        self.assertTrue(is_valid)
        self.assertIn("L", self.game.guessed_letters)

        # Check progress shows both L's
        progress = self.game.get_word_progress()
        self.assertEqual(progress, "_ _ L L _ _ _")

    def test_max_guesses_boundary(self):
        """Test behavior at max guesses boundary."""
        self.game.max_attempts = 1
        self.game.current_word = "TEST"

        # Make one wrong guess
        self.game.make_guess("A")

        # Should be at lose condition
        self.assertTrue(self.game.check_lose_condition())
        self.assertEqual(self.game.wrong_guesses, 1)

    def test_hangman_stages_count(self):
        """Test that hangman stages array has expected length."""
        self.assertEqual(len(self.game.hangman_stages), 8)

        # Check that each stage contains expected elements
        for i, stage in enumerate(self.game.hangman_stages):
            self.assertIn("-----", stage)
            self.assertIn("========", stage)

            # Later stages should have more body parts
            if i >= 1:
                self.assertIn("O", stage)
            if i >= 2:
                self.assertIn("|", stage)
            if i >= 4:
                self.assertIn("\\", stage)
            if i >= 5:
                self.assertIn("/", stage)
            if i >= 7:
                self.assertIn("GAME", stage)


class TestHangmanGameIntegration(unittest.TestCase):
    """Integration tests for HangmanGame class."""

    def setUp(self):
        """Set up test fixtures."""
        self.game = HangmanGame()

    def test_full_game_workflow(self):
        """Test complete game workflow from start to finish."""
        # Start new game
        self.game.start_new_game("fruits", "medium")

        # Verify initial state
        self.assertEqual(self.game.current_category, "fruits")
        self.assertEqual(self.game.max_attempts, 6)
        self.assertFalse(self.game.game_over)

        # Simulate game play
        word = self.game.current_word
        unique_letters = set(word)

        # Make all correct guesses
        for letter in unique_letters:
            if not self.game.game_over:
                self.game.make_guess(letter)

        # Should have won
        self.assertTrue(self.game.check_win_condition())
        status = self.game.get_game_status()
        self.assertEqual(status["progress"].replace(" ", ""), word)

    def test_difficulty_impact_on_gameplay(self):
        """Test that difficulty levels affect gameplay correctly."""
        # Test easy difficulty
        self.game.start_new_game("sports", "easy")
        easy_attempts = self.game.max_attempts

        # Test hard difficulty
        self.game.start_new_game("sports", "hard")
        hard_attempts = self.game.max_attempts

        # Easy should have more attempts than hard
        self.assertGreater(easy_attempts, hard_attempts)
        self.assertEqual(easy_attempts, 8)
        self.assertEqual(hard_attempts, 4)


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
"""
Hangman Game

A command-line implementation of the classic Hangman word guessing game
with categories, difficulty levels, and ASCII art.
"""

import random
from typing import List, Dict, Tuple, Optional


class HangmanGame:
    """Main class for the Hangman game with all game logic."""

    def __init__(self):
        self.word_categories = {
            "animals": [
                "elephant",
                "giraffe",
                "penguin",
                "dolphin",
                "butterfly",
                "crocodile",
                "kangaroo",
                "octopus",
                "peacock",
                "rhinoceros",
                "squirrel",
                "tortoise",
                "cheetah",
                "gorilla",
                "hamster",
            ],
            "countries": [
                "australia",
                "brazil",
                "canada",
                "denmark",
                "ethiopia",
                "france",
                "germany",
                "hungary",
                "india",
                "jamaica",
                "kenya",
                "luxembourg",
                "mexico",
                "norway",
                "portugal",
            ],
            "fruits": [
                "apple",
                "banana",
                "cherry",
                "dragonfruit",
                "elderberry",
                "fig",
                "grape",
                "honeydew",
                "kiwi",
                "lemon",
                "mango",
                "orange",
                "papaya",
                "quince",
                "raspberry",
            ],
            "sports": [
                "basketball",
                "cricket",
                "football",
                "golf",
                "hockey",
                "tennis",
                "volleyball",
                "baseball",
                "swimming",
                "cycling",
                "boxing",
                "skiing",
                "surfing",
                "climbing",
                "fencing",
            ],
        }

        self.difficulty_levels = {
            "easy": {"max_attempts": 8, "description": "Easy (8 attempts)"},
            "medium": {"max_attempts": 6, "description": "Medium (6 attempts)"},
            "hard": {"max_attempts": 4, "description": "Hard (4 attempts)"},
        }

        self.hangman_stages = [
            """
               -----
               |   |
                   |
                   |
                   |
                   |
            =========
            """,
            """
               -----
               |   |
               O   |
                   |
                   |
                   |
            =========
            """,
            """
               -----
               |   |
               O   |
               |   |
                   |
                   |
            =========
            """,
            """
               -----
               |   |
               O   |
              /|   |
                   |
                   |
            =========
            """,
            """
               -----
               |   |
               O   |
              /|\\  |
                   |
                   |
            =========
            """,
            """
               -----
               |   |
               O   |
              /|\\  |
              /    |
                   |
            =========
            """,
            """
               -----
               |   |
               O   |
              /|\\  |
              / \\  |
                   |
            =========
            """,
            """
               -----
               |   |
               O   |
              /|\\  |
              / \\  |
             GAME  |
            =========
            """,
        ]

        self.reset_game()

    def reset_game(self):
        """Reset the game state for a new game."""
        self.current_word = ""
        self.current_category = ""
        self.guessed_letters = set()
        self.wrong_guesses = 0
        self.max_attempts = 6
        self.game_over = False
        self.won = False

    def select_random_word(self, category: Optional[str] = None) -> str:
        """
        Select a random word from the specified category or any category.

        Args:
            category: Specific category to choose from, or None for random

        Returns:
            Selected word
        """
        if category and category in self.word_categories:
            words = self.word_categories[category]
        else:
            # Random category
            category = random.choice(list(self.word_categories.keys()))
            words = self.word_categories[category]

        self.current_category = category
        self.current_word = random.choice(words).upper()
        return self.current_word

    def get_word_progress(self) -> str:
        """
        Get the current progress of the word with underscores for unguessed letters.

        Returns:
            String showing guessed letters and underscores
        """
        progress = []
        for letter in self.current_word:
            if letter in self.guessed_letters:
                progress.append(letter)
            else:
                progress.append("_")
        return " ".join(progress)

    def make_guess(self, guess: str) -> Tuple[bool, str]:
        """
        Process a letter guess.

        Args:
            guess: The letter being guessed

        Returns:
            Tuple of (is_valid_guess, message)
        """
        if not guess or len(guess) != 1:
            return False, "Please enter a single letter"

        guess = guess.upper()

        if not guess.isalpha():
            return False, "Please enter a letter (A-Z)"

        if guess in self.guessed_letters:
            return False, f"You already guessed '{guess}'"

        self.guessed_letters.add(guess)

        if guess in self.current_word:
            return True, f"Good guess! '{guess}' is in the word"
        else:
            self.wrong_guesses += 1
            return False, f"Sorry, '{guess}' is not in the word"

    def check_win_condition(self) -> bool:
        """
        Check if the player has won the game.

        Returns:
            True if player has won, False otherwise
        """
        for letter in self.current_word:
            if letter not in self.guessed_letters:
                return False
        return True

    def check_lose_condition(self) -> bool:
        """
        Check if the player has lost the game.

        Returns:
            True if player has lost, False otherwise
        """
        return self.wrong_guesses >= self.max_attempts

    def get_game_status(self) -> Dict:
        """
        Get the current game status.

        Returns:
            Dictionary with game status information
        """
        return {
            "word": self.current_word,
            "category": self.current_category,
            "progress": self.get_word_progress(),
            "guessed_letters": sorted(list(self.guessed_letters)),
            "wrong_guesses": self.wrong_guesses,
            "max_attempts": self.max_attempts,
            "remaining_attempts": self.max_attempts - self.wrong_guesses,
            "game_over": self.game_over,
            "won": self.won,
        }

    def get_hangman_display(self) -> str:
        """
        Get the appropriate hangman ASCII art based on wrong guesses.

        Returns:
            ASCII art string
        """
        stage_index = min(self.wrong_guesses, len(self.hangman_stages) - 1)
        return self.hangman_stages[stage_index]

    def start_new_game(
        self, category: Optional[str] = None, difficulty: str = "medium"
    ):
        """
        Start a new game with specified category and difficulty.

        Args:
            category: Word category or None for random
            difficulty: Game difficulty level
        """
        self.reset_game()

        if difficulty in self.difficulty_levels:
            self.max_attempts = self.difficulty_levels[difficulty]["max_attempts"]

        self.select_random_word(category)

    def get_available_categories(self) -> List[str]:
        """Get list of available word categories."""
        return list(self.word_categories.keys())

    def get_difficulty_levels(self) -> Dict[str, str]:
        """Get available difficulty levels."""
        return {k: v["description"] for k, v in self.difficulty_levels.items()}


def display_welcome():
    """Display welcome message and instructions."""
    print("\n" + "=" * 60)
    print("[TARGET] HANGMAN GAME [TARGET]")
    print("=" * 60)
    print("Welcome to Hangman! Try to guess the word letter by letter.")
    print("You have limited attempts before the hangman is complete!")
    print("=" * 60)


def display_game_status(game: HangmanGame):
    """Display the current game status."""
    status = game.get_game_status()

    print(f"\nCategory: {status['category'].title()}")
    print(f"Word: {status['progress']}")
    print(
        f"Guessed letters: {', '.join(status['guessed_letters']) if status['guessed_letters'] else 'None'}"
    )
    print(
        f"Attempts remaining: {status['remaining_attempts']}/{status['max_attempts']}"
    )
    print("\n" + game.get_hangman_display())


def get_player_guess() -> str:
    """Get and validate player's guess."""
    while True:
        guess = input("\nEnter your guess (A-Z): ").strip()
        if guess:
            return guess
        print("Please enter a letter.")


def handle_game_end(game: HangmanGame):
    """Handle the end of game display and options."""
    status = game.get_game_status()

    print("\n" + "=" * 50)
    if status["won"]:
        print("[CELEBRATION] CONGRATULATIONS! YOU WON! [CELEBRATION]")
        print(f"You successfully guessed the word: {status['word']}")
    else:
        print("[SAD] GAME OVER! YOU LOST! [SAD]")
        print(f"The word was: {status['word']}")
    print("=" * 50)


def select_category(game: HangmanGame) -> Optional[str]:
    """Let player select a word category."""
    categories = game.get_available_categories()

    print("\nAvailable categories:")
    for i, category in enumerate(categories, 1):
        print(f"{i}. {category.title()}")
    print(f"{len(categories) + 1}. Random category")

    while True:
        try:
            choice = input(f"\nSelect category (1-{len(categories) + 1}): ").strip()
            choice_num = int(choice)

            if 1 <= choice_num <= len(categories):
                return categories[choice_num - 1]
            elif choice_num == len(categories) + 1:
                return None
            else:
                print(f"Please enter a number between 1 and {len(categories) + 1}")
        except ValueError:
            print("Please enter a valid number")


def select_difficulty(game: HangmanGame) -> str:
    """Let player select difficulty level."""
    levels = game.get_difficulty_levels()

    print("\nDifficulty levels:")
    for i, (level, description) in enumerate(levels.items(), 1):
        print(f"{i}. {description}")

    while True:
        try:
            choice = input(f"\nSelect difficulty (1-{len(levels)}): ").strip()
            choice_num = int(choice)

            if 1 <= choice_num <= len(levels):
                return list(levels.keys())[choice_num - 1]
            else:
                print(f"Please enter a number between 1 and {len(levels)}")
        except ValueError:
            print("Please enter a valid number")


def play_game(game: HangmanGame):
    """Play a single game of Hangman."""
    # Game setup
    category = select_category(game)
    difficulty = select_difficulty(game)

    game.start_new_game(category, difficulty)

    print("\nStarting new game...")
    print(f"Category: {game.current_category.title()}")
    print(f"Difficulty: {difficulty.title()} ({game.max_attempts} attempts)")
    print(f"Word has {len(game.current_word)} letters")

    # Main game loop
    while not game.game_over:
        display_game_status(game)

        # Check win condition
        if game.check_win_condition():
            game.won = True
            game.game_over = True
            break

        # Check lose condition
        if game.check_lose_condition():
            game.won = False
            game.game_over = True
            break

        # Get player guess
        guess = get_player_guess()
        is_valid, message = game.make_guess(guess)

        print(f"\n{message}")

    # Display final game state
    display_game_status(game)
    handle_game_end(game)


def main():
    """Main program loop."""
    game = HangmanGame()

    display_welcome()

    while True:
        play_game(game)

        # Ask to play again
        while True:
            play_again = (
                input("\nWould you like to play again? (y/n): ").strip().lower()
            )
            if play_again in ["y", "yes"]:
                break
            elif play_again in ["n", "no"]:
                print("\nThanks for playing Hangman!")
                print("[TARGET] Goodbye! [TARGET]")
                return
            else:
                print("Please enter 'y' or 'n'")


if __name__ == "__main__":
    main()

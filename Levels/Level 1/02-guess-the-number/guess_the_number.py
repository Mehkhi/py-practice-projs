#!/usr/bin/env python3
"""
Guess the Number Game
A command-line number guessing game with difficulty levels, scoring, and leaderboard.
"""

import random
import json
import os
from typing import Dict, List, Optional
from datetime import datetime


class GuessTheNumberGame:
    """A number guessing game with multiple difficulty levels and scoring."""

    def __init__(self):
        self.difficulty_levels = {
            'easy': {'min': 1, 'max': 10, 'attempts': 5},
            'medium': {'min': 1, 'max': 50, 'attempts': 7},
            'hard': {'min': 1, 'max': 100, 'attempts': 10},
            'expert': {'min': 1, 'max': 1000, 'attempts': 15}
        }
        self.current_difficulty = 'medium'
        self.secret_number = 0
        self.attempts_left = 0
        self.total_attempts = 0
        self.game_history: List[Dict] = []
        self.leaderboard: List[Dict] = []
        self.scores_file = "guess_the_number_scores.json"
        self.leaderboard_file = "guess_the_number_leaderboard.json"
        self.load_data()

    def load_data(self) -> None:
        """Load game data from files."""
        # Load scores
        try:
            if os.path.exists(self.scores_file):
                with open(self.scores_file, 'r') as f:
                    data = json.load(f)
                    self.game_history = data.get('history', [])
        except (json.JSONDecodeError, FileNotFoundError):
            self.game_history = []

        # Load leaderboard
        try:
            if os.path.exists(self.leaderboard_file):
                with open(self.leaderboard_file, 'r') as f:
                    self.leaderboard = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            self.leaderboard = []

    def save_data(self) -> None:
        """Save game data to files."""
        try:
            # Save scores
            with open(self.scores_file, 'w') as f:
                json.dump({'history': self.game_history}, f, indent=2)

            # Save leaderboard
            with open(self.leaderboard_file, 'w') as f:
                json.dump(self.leaderboard, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save data: {e}")

    def generate_secret_number(self) -> int:
        """Generate a random number based on current difficulty."""
        level = self.difficulty_levels[self.current_difficulty]
        self.secret_number = random.randint(level['min'], level['max'])
        self.attempts_left = level['attempts']
        self.total_attempts = 0
        return self.secret_number

    def validate_guess(self, guess_str: str) -> Optional[int]:
        """Validate user input and return integer guess."""
        try:
            guess = int(guess_str.strip())
            level = self.difficulty_levels[self.current_difficulty]

            if guess < level['min'] or guess > level['max']:
                print(f"Please enter a number between {level['min']} and {level['max']}")
                return None

            return guess
        except ValueError:
            print("Please enter a valid number!")
            return None

    def get_hint(self, guess: int) -> str:
        """Provide hint based on guess."""
        if guess < self.secret_number:
            return "Too low! Try a higher number."
        elif guess > self.secret_number:
            return "Too high! Try a lower number."
        else:
            return "Congratulations! You guessed it!"

    def calculate_score(self) -> int:
        """Calculate score based on attempts and difficulty."""
        level = self.difficulty_levels[self.current_difficulty]
        max_attempts = level['attempts']
        attempts_used = max_attempts - self.attempts_left

        # Base score calculation
        base_score = level['max'] - level['min'] + 1
        difficulty_multiplier = {
            'easy': 1,
            'medium': 2,
            'hard': 3,
            'expert': 5
        }

        # Score decreases with more attempts
        score = int((base_score * difficulty_multiplier[self.current_difficulty]) /
                   (attempts_used + 1))

        return max(score, 1)  # Minimum score of 1

    def add_to_history(self, won: bool, score: int) -> None:
        """Add game result to history."""
        self.game_history.append({
            'difficulty': self.current_difficulty,
            'won': won,
            'score': score,
            'attempts_used': self.total_attempts,
            'secret_number': self.secret_number,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

    def update_leaderboard(self, player_name: str, score: int) -> None:
        """Update leaderboard with new score."""
        # Check if player already exists
        player_exists = False
        for entry in self.leaderboard:
            if entry['name'].lower() == player_name.lower():
                if score > entry['score']:
                    entry['score'] = score
                    entry['date'] = datetime.now().strftime("%Y-%m-%d")
                player_exists = True
                break

        # Add new player if doesn't exist
        if not player_exists:
            self.leaderboard.append({
                'name': player_name,
                'score': score,
                'difficulty': self.current_difficulty,
                'date': datetime.now().strftime("%Y-%m-%d")
            })

        # Sort leaderboard by score (descending)
        self.leaderboard.sort(key=lambda x: x['score'], reverse=True)

        # Keep only top 10
        self.leaderboard = self.leaderboard[:10]

    def show_leaderboard(self) -> None:
        """Display the leaderboard."""
        if not self.leaderboard:
            print("No scores yet! Be the first to play!")
            return

        print("\n=== LEADERBOARD ===")
        print(f"{'Rank':<4} {'Name':<15} {'Score':<8} {'Difficulty':<10} {'Date':<12}")
        print("-" * 55)

        for i, entry in enumerate(self.leaderboard, 1):
            print(f"{i:<4} {entry['name']:<15} {entry['score']:<8} "
                  f"{entry['difficulty']:<10} {entry['date']:<12}")
        print("=" * 55)

    def show_difficulty_menu(self) -> None:
        """Display difficulty selection menu."""
        print("\n=== DIFFICULTY LEVELS ===")
        for level, config in self.difficulty_levels.items():
            print(f"{level.capitalize():<8}: {config['min']}-{config['max']} "
                  f"(max {config['attempts']} attempts)")
        print("=" * 35)

    def set_difficulty(self, difficulty: str) -> bool:
        """Set game difficulty."""
        if difficulty.lower() in self.difficulty_levels:
            self.current_difficulty = difficulty.lower()
            return True
        return False

    def show_game_stats(self) -> None:
        """Display game statistics."""
        if not self.game_history:
            print("No games played yet!")
            return

        total_games = len(self.game_history)
        games_won = sum(1 for game in self.game_history if game['won'])
        win_rate = (games_won / total_games) * 100 if total_games > 0 else 0
        best_score = max(game['score'] for game in self.game_history)
        avg_score = sum(game['score'] for game in self.game_history) / total_games

        print("\n=== GAME STATISTICS ===")
        print(f"Total games played: {total_games}")
        print(f"Games won: {games_won}")
        print(f"Win rate: {win_rate:.1f}%")
        print(f"Best score: {best_score}")
        print(f"Average score: {avg_score:.1f}")
        print("=" * 22)

    def play_game(self) -> None:
        """Main game loop."""
        print("\n=== GUESS THE NUMBER ===")
        print(f"Difficulty: {self.current_difficulty.capitalize()}")

        level = self.difficulty_levels[self.current_difficulty]
        print(f"Range: {level['min']} to {level['max']}")
        print(f"Attempts: {level['attempts']}")
        print("=" * 25)

        self.generate_secret_number()

        while self.attempts_left > 0:
            print(f"\nAttempts left: {self.attempts_left}")
            guess_str = input(f"Enter your guess ({level['min']}-{level['max']}): ")

            guess = self.validate_guess(guess_str)
            if guess is None:
                continue

            self.total_attempts += 1
            self.attempts_left -= 1

            hint = self.get_hint(guess)
            print(hint)

            if guess == self.secret_number:
                score = self.calculate_score()
                print("\nCongratulations! You won!")
                print(f"Score: {score} points")
                print(f"Attempts used: {self.total_attempts}")

                self.add_to_history(True, score)

                # Ask for leaderboard entry
                if score > 0:
                    player_name = input("Enter your name for the leaderboard (or press Enter to skip): ").strip()
                    if player_name:
                        self.update_leaderboard(player_name, score)
                        print(f"Added {player_name} to leaderboard!")

                self.save_data()
                return

        # Game over - didn't guess correctly
        print("\nGame Over!")
        print(f"The secret number was: {self.secret_number}")
        print("Better luck next time!")

        self.add_to_history(False, 0)
        self.save_data()

    def show_menu(self) -> None:
        """Display main menu."""
        print("\n=== GUESS THE NUMBER GAME ===")
        print("1. Play Game")
        print("2. Change Difficulty")
        print("3. View Leaderboard")
        print("4. View Statistics")
        print("5. Show Difficulty Levels")
        print("6. Quit")
        print("=" * 30)

    def run(self) -> None:
        """Main program loop."""
        print("Welcome to Guess the Number!")
        print("Try to guess the secret number within the given attempts!")

        while True:
            self.show_menu()
            choice = input("Enter your choice (1-6): ").strip()

            if choice == '1':
                self.play_game()
            elif choice == '2':
                self.show_difficulty_menu()
                difficulty = input("Enter difficulty level: ").strip()
                if self.set_difficulty(difficulty):
                    print(f"Difficulty set to: {self.current_difficulty.capitalize()}")
                else:
                    print("Invalid difficulty level!")
            elif choice == '3':
                self.show_leaderboard()
            elif choice == '4':
                self.show_game_stats()
            elif choice == '5':
                self.show_difficulty_menu()
            elif choice == '6':
                print("Thanks for playing! Goodbye!")
                self.save_data()
                break
            else:
                print("Invalid choice! Please enter 1-6.")


def main():
    """Main entry point."""
    game = GuessTheNumberGame()
    game.run()


if __name__ == "__main__":
    main()

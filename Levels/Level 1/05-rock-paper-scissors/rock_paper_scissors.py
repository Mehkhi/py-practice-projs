"""Command-line Rock-Paper-Scissors game with running score."""

from __future__ import annotations

import random
from typing import Dict, Tuple


VALID_CHOICES = ("rock", "paper", "scissors")
QUIT_COMMANDS = ("quit", "q", "exit")


def normalize_choice(raw_choice: str) -> str | None:
    """Return a normalized choice or None if input is invalid."""
    cleaned = raw_choice.strip().lower()
    if cleaned in QUIT_COMMANDS:
        return "quit"
    if cleaned in VALID_CHOICES:
        return cleaned
    # allow single-letter shortcuts
    shortcuts = {"r": "rock", "p": "paper", "s": "scissors"}
    return shortcuts.get(cleaned)


def determine_outcome(player: str, computer: str) -> str:
    """Decide win/lose/tie for the player."""
    if player == computer:
        return "tie"
    wins_against = {"rock": "scissors", "paper": "rock", "scissors": "paper"}
    if wins_against[player] == computer:
        return "win"
    return "lose"


def format_scoreboard(score: Dict[str, int]) -> str:
    return f"Player: {score['player']} | Computer: {score['computer']} | Ties: {score['ties']}"


def play_round() -> Tuple[str, str, str]:
    """Handle a single round; returns (player_choice, computer_choice, outcome)."""
    computer_choice = random.choice(VALID_CHOICES)
    while True:
        user_input = input("Choose rock, paper, or scissors (or type 'quit' to exit): ")
        normalized = normalize_choice(user_input)
        if normalized == "quit":
            return "quit", computer_choice, "quit"
        if normalized in VALID_CHOICES:
            outcome = determine_outcome(normalized, computer_choice)
            return normalized, computer_choice, outcome
        print("Invalid choice. Please try again.")


def main() -> None:
    print("Welcome to Rock-Paper-Scissors!")
    score = {"player": 0, "computer": 0, "ties": 0}

    while True:
        player_choice, computer_choice, outcome = play_round()
        if outcome == "quit":
            break

        if outcome == "win":
            score["player"] += 1
            result_message = "You win this round!"
        elif outcome == "lose":
            score["computer"] += 1
            result_message = "Computer wins this round."
        else:
            score["ties"] += 1
            result_message = "It's a tie."

        print(f"You chose {player_choice}, computer chose {computer_choice}.")
        print(result_message)
        print(format_scoreboard(score))
        print("-")

    print("Thanks for playing!")
    print("Final score:")
    print(format_scoreboard(score))


if __name__ == "__main__":
    main()

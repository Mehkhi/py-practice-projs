#!/usr/bin/env python3
"""
Flashcards Study App

A simple command-line flashcards application for studying.
Loads flashcards from a JSON file and tracks your score.
"""

import json
import random
import os
from typing import List, Dict


def load_flashcards(filename: str) -> List[Dict[str, str]]:
    """
    Load flashcards from a JSON file.

    Args:
        filename: Path to the JSON file containing flashcards

    Returns:
        List of flashcard dictionaries with 'question' and 'answer' keys

    Raises:
        FileNotFoundError: If the file doesn't exist
        json.JSONDecodeError: If the file contains invalid JSON
    """
    try:
        with open(filename, "r", encoding="utf-8") as file:
            flashcards = json.load(file)

        # Validate flashcard format
        for i, card in enumerate(flashcards):
            if not isinstance(card, dict):
                raise ValueError(f"Flashcard {i} is not a dictionary")
            if "question" not in card or "answer" not in card:
                raise ValueError(f"Flashcard {i} missing 'question' or 'answer' key")

        return flashcards

    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return []
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in file '{filename}': {e}")
        return []
    except ValueError as e:
        print(f"Error: {e}")
        return []


def check_answer(user_answer: str, correct_answer: str) -> bool:
    """
    Check if the user's answer is correct (case-insensitive).

    Args:
        user_answer: The answer provided by the user
        correct_answer: The correct answer

    Returns:
        True if the answer is correct, False otherwise
    """
    return user_answer.strip().lower() == correct_answer.strip().lower()


def display_score(correct: int, total: int) -> None:
    """
    Display the final score.

    Args:
        correct: Number of correct answers
        total: Total number of questions
    """
    percentage = (correct / total * 100) if total > 0 else 0
    print(f"\n{'='*50}")
    print("Quiz Complete!")
    print(f"Score: {correct}/{total} ({percentage:.1f}%)")

    if percentage >= 90:
        print("Excellent work! [STAR]")
    elif percentage >= 70:
        print("Good job! [THUMBS UP]")
    elif percentage >= 50:
        print("Not bad, keep studying! [BOOKS]")
    else:
        print("Keep practicing! [FLEX]")
    print(f"{'='*50}")


def study_session(flashcards: List[Dict[str, str]]) -> None:
    """
    Run a study session with the provided flashcards.

    Args:
        flashcards: List of flashcard dictionaries
    """
    if not flashcards:
        print("No flashcards available to study.")
        return

    # Shuffle flashcards for variety
    shuffled_cards = flashcards.copy()
    random.shuffle(shuffled_cards)

    correct_count = 0
    total_questions = len(shuffled_cards)

    print(f"\nStarting study session with {total_questions} flashcards...")
    print("Type 'quit' at any time to exit.\n")

    for i, card in enumerate(shuffled_cards, 1):
        question = card["question"]
        correct_answer = card["answer"]

        print(f"Question {i}/{total_questions}:")
        print(f"Q: {question}")

        while True:
            try:
                user_answer = input("A: ").strip()

                if user_answer.lower() == "quit":
                    print("\nStudy session ended early.")
                    display_score(correct_count, i - 1)
                    return

                if not user_answer:
                    print("Please enter an answer or 'quit' to exit.")
                    continue

                break

            except KeyboardInterrupt:
                print("\n\nStudy session interrupted.")
                display_score(correct_count, i - 1)
                return

        if check_answer(user_answer, correct_answer):
            print("[OK] Correct!")
            correct_count += 1
        else:
            print(f"[X] Incorrect. The correct answer is: {correct_answer}")

        print("-" * 50)

    display_score(correct_count, total_questions)


def main():
    """Main function to run the flashcards application."""
    print("[GRADUATION] Flashcards Study App")
    print("=" * 30)

    # Default flashcards file
    flashcards_file = "flashcards.json"

    # Check if custom file is provided
    if len(os.sys.argv) > 1:
        flashcards_file = os.sys.argv[1]

    # Load flashcards
    flashcards = load_flashcards(flashcards_file)

    if not flashcards:
        print(f"Could not load flashcards from '{flashcards_file}'.")
        print("Make sure the file exists and contains valid flashcards.")
        return

    print(f"Loaded {len(flashcards)} flashcards from '{flashcards_file}'.")

    # Start study session
    study_session(flashcards)


if __name__ == "__main__":
    main()

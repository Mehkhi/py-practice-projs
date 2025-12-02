#!/usr/bin/env python3
"""
Quiz App from JSON

A command-line quiz application that loads questions from JSON files,
presents them to users, and calculates scores with optional time limits
and result history tracking.
"""

import json
import time
import os
from typing import List, Dict, Any, Optional
from datetime import datetime


class QuizApp:
    """Main class for the quiz application."""

    def __init__(self):
        self.questions = []
        self.current_question_index = 0
        self.score = 0
        self.total_questions = 0
        self.answers = []
        self.start_time = None
        self.end_time = None
        self.time_limit_per_question = 30  # seconds
        self.results_file = "quiz_results.json"

    def load_questions_from_json(self, filename: str) -> bool:
        """
        Load quiz questions from a JSON file.

        Args:
            filename: Path to the JSON file containing questions

        Returns:
            True if successful, False otherwise
        """
        try:
            with open(filename, "r", encoding="utf-8") as file:
                data = json.load(file)

            # Handle different JSON structures
            if isinstance(data, list):
                self.questions = data
            elif isinstance(data, dict) and "questions" in data:
                self.questions = data["questions"]
            else:
                print(
                    "Error: Invalid JSON structure. Expected list or dict with 'questions' key."
                )
                return False

            self.total_questions = len(self.questions)
            return True

        except FileNotFoundError:
            print(f"Error: File '{filename}' not found.")
            return False
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON format - {e}")
            return False
        except Exception as e:
            print(f"Error loading questions: {e}")
            return False

    def create_sample_questions_file(self, filename: str = "sample_questions.json"):
        """Create a sample questions JSON file for testing."""
        sample_questions = {
            "questions": [
                {
                    "question": "What is the capital of France?",
                    "options": ["London", "Berlin", "Paris", "Madrid"],
                    "correct_answer": "Paris",
                    "category": "Geography",
                },
                {
                    "question": "What is 2 + 2?",
                    "options": ["3", "4", "5", "6"],
                    "correct_answer": "4",
                    "category": "Mathematics",
                },
                {
                    "question": "Which planet is known as the Red Planet?",
                    "options": ["Venus", "Mars", "Jupiter", "Saturn"],
                    "correct_answer": "Mars",
                    "category": "Science",
                },
                {
                    "question": "Who painted the Mona Lisa?",
                    "options": ["Van Gogh", "Picasso", "Da Vinci", "Rembrandt"],
                    "correct_answer": "Da Vinci",
                    "category": "Art",
                },
                {
                    "question": "What is the largest ocean on Earth?",
                    "options": ["Atlantic", "Indian", "Arctic", "Pacific"],
                    "correct_answer": "Pacific",
                    "category": "Geography",
                },
            ]
        }

        try:
            with open(filename, "w", encoding="utf-8") as file:
                json.dump(sample_questions, file, indent=2, ensure_ascii=False)
            print(f"Sample questions file '{filename}' created successfully.")
            return True
        except Exception as e:
            print(f"Error creating sample file: {e}")
            return False

    def display_question(self, question: Dict[str, Any]) -> Optional[str]:
        """
        Display a question and get user answer.

        Args:
            question: Question dictionary

        Returns:
            User's answer or None if time expired
        """
        print(f"\n{'='*60}")
        print(f"Question {self.current_question_index + 1} of {self.total_questions}")
        print(f"Category: {question.get('category', 'General')}")
        print(f"{'='*60}")
        print(f"\n{question['question']}\n")

        # Display options if available
        if "options" in question and question["options"]:
            for i, option in enumerate(question["options"], 1):
                print(f"{i}. {option}")
            print()

            # Get user input with time limit
            return self.get_timed_input(
                "Your answer (enter number or text): ", self.time_limit_per_question
            )
        else:
            # Free text answer
            return self.get_timed_input("Your answer: ", self.time_limit_per_question)

    def get_timed_input(self, prompt: str, time_limit: int) -> Optional[str]:
        """
        Get user input with a time limit.

        Args:
            prompt: Input prompt message
            time_limit: Time limit in seconds

        Returns:
            User input or None if time expired
        """
        print(f"Time limit: {time_limit} seconds")

        # Simple implementation without threading for compatibility
        start_time = time.time()
        user_input = input(prompt).strip()
        elapsed_time = time.time() - start_time

        if elapsed_time > time_limit:
            print(f"\nTime expired! (Limit: {time_limit} seconds)")
            return None

        return user_input

    def check_answer(self, question: Dict[str, Any], user_answer: str) -> bool:
        """
        Check if the user's answer is correct.

        Args:
            question: Question dictionary
            user_answer: User's answer

        Returns:
            True if correct, False otherwise
        """
        if not user_answer:
            return False

        correct_answer = question["correct_answer"].lower().strip()

        # Handle numeric input for multiple choice
        if "options" in question and question["options"]:
            try:
                option_index = int(user_answer) - 1
                if 0 <= option_index < len(question["options"]):
                    user_answer = question["options"][option_index]
                else:
                    return False
            except ValueError:
                # User entered text instead of number
                pass

        user_answer = user_answer.lower().strip()
        return user_answer == correct_answer

    def run_quiz(self) -> Dict[str, Any]:
        """
        Run the complete quiz.

        Returns:
            Dictionary with quiz results
        """
        if not self.questions:
            print("No questions loaded. Please load questions first.")
            return {}

        self.reset_quiz()
        self.start_time = datetime.now()

        print("\n[TARGET] QUIZ STARTED [TARGET]")
        print(f"Total questions: {self.total_questions}")
        print(f"Time limit per question: {self.time_limit_per_question} seconds")
        print("Good luck!\n")

        for question in self.questions:
            self.current_question_index += 1

            user_answer = self.display_question(question)

            is_correct = self.check_answer(question, user_answer)

            # Record answer
            answer_record = {
                "question": question["question"],
                "user_answer": user_answer,
                "correct_answer": question["correct_answer"],
                "is_correct": is_correct,
                "question_number": self.current_question_index,
            }
            self.answers.append(answer_record)

            if is_correct:
                self.score += 1
                print("[OK] Correct!")
            else:
                print(
                    f"[X] Incorrect! The correct answer was: {question['correct_answer']}"
                )

            # Brief pause before next question
            if self.current_question_index < self.total_questions:
                input("\nPress Enter to continue...")

        self.end_time = datetime.now()
        return self.get_quiz_results()

    def get_quiz_results(self) -> Dict[str, Any]:
        """
        Get the quiz results.

        Returns:
            Dictionary with quiz results
        """
        if not self.start_time or not self.end_time:
            return {}

        duration = (self.end_time - self.start_time).total_seconds()
        percentage = (
            (self.score / self.total_questions) * 100 if self.total_questions > 0 else 0
        )

        return {
            "score": self.score,
            "total_questions": self.total_questions,
            "percentage": round(percentage, 2),
            "duration_seconds": round(duration, 2),
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "answers": self.answers,
        }

    def display_results(self, results: Dict[str, Any]):
        """Display quiz results to the user."""
        if not results:
            print("No results to display.")
            return

        print(f"\n{'='*60}")
        print("[TARGET] QUIZ RESULTS [TARGET]")
        print(f"{'='*60}")
        print(f"Score: {results['score']}/{results['total_questions']}")
        print(f"Percentage: {results['percentage']}%")
        print(f"Duration: {results['duration_seconds']:.1f} seconds")
        print(f"Completed: {results['end_time']}")

        # Performance message
        if results["percentage"] >= 90:
            print("[TROPHY] Outstanding performance!")
        elif results["percentage"] >= 80:
            print("[STAR] Excellent work!")
        elif results["percentage"] >= 70:
            print("[THUMBS UP] Good job!")
        elif results["percentage"] >= 60:
            print("[BOOKS] Not bad, keep studying!")
        else:
            print("[FLEX] Keep practicing!")

        # Show answer breakdown
        print(f"\n{'='*60}")
        print("ANSWER BREAKDOWN")
        print(f"{'='*60}")

        for answer in results["answers"]:
            status = "[OK]" if answer["is_correct"] else "[X]"
            print(
                f"{status} Q{answer['question_number']}: {answer['question'][:50]}..."
            )
            if not answer["is_correct"]:
                print(f"   Your answer: {answer['user_answer']}")
                print(f"   Correct answer: {answer['correct_answer']}")

    def save_results(self, results: Dict[str, Any]) -> bool:
        """
        Save quiz results to a JSON file.

        Args:
            results: Quiz results dictionary

        Returns:
            True if successful, False otherwise
        """
        try:
            # Load existing results
            existing_results = []
            if os.path.exists(self.results_file):
                with open(self.results_file, "r", encoding="utf-8") as file:
                    existing_results = json.load(file)

            # Add new results
            existing_results.append(results)

            # Save back to file
            with open(self.results_file, "w", encoding="utf-8") as file:
                json.dump(existing_results, file, indent=2, ensure_ascii=False)

            print(f"\nResults saved to '{self.results_file}'")
            return True

        except Exception as e:
            print(f"Error saving results: {e}")
            return False

    def load_results_history(self) -> List[Dict[str, Any]]:
        """
        Load quiz results history.

        Returns:
            List of previous quiz results
        """
        try:
            if os.path.exists(self.results_file):
                with open(self.results_file, "r", encoding="utf-8") as file:
                    return json.load(file)
            return []
        except Exception as e:
            print(f"Error loading results history: {e}")
            return []

    def display_results_history(self):
        """Display the quiz results history."""
        history = self.load_results_history()

        if not history:
            print("\nNo quiz history found.")
            return

        print(f"\n{'='*60}")
        print("[BAR CHART] QUIZ HISTORY [BAR CHART]")
        print(f"{'='*60}")

        for i, result in enumerate(history, 1):
            print(f"\nQuiz #{i}:")
            print(
                f"  Score: {result['score']}/{result['total_questions']} ({result['percentage']}%)"
            )
            print(f"  Duration: {result['duration_seconds']:.1f} seconds")
            print(f"  Date: {result['end_time']}")

    def reset_quiz(self):
        """Reset quiz state for a new quiz."""
        self.current_question_index = 0
        self.score = 0
        self.answers = []
        self.start_time = None
        self.end_time = None

    def set_time_limit(self, seconds: int):
        """Set time limit per question."""
        self.time_limit_per_question = max(5, seconds)  # Minimum 5 seconds

    def get_available_question_files(self) -> List[str]:
        """Get list of available JSON question files in current directory."""
        json_files = []
        for file in os.listdir("."):
            if file.endswith(".json") and file != self.results_file:
                json_files.append(file)
        return json_files


def display_welcome():
    """Display welcome message and instructions."""
    print("\n" + "=" * 60)
    print("[TARGET] QUIZ APP FROM JSON [TARGET]")
    print("=" * 60)
    print("Welcome to the Quiz App! Test your knowledge with questions")
    print("loaded from JSON files. Track your progress and improve!")
    print("=" * 60)


def get_menu_choice() -> str:
    """Get user's menu choice."""
    print("\n[CLIPBOARD] MAIN MENU [CLIPBOARD]")
    print("1. Load questions from file")
    print("2. Create sample questions file")
    print("3. Start quiz")
    print("4. View quiz history")
    print("5. Set time limit per question")
    print("6. Exit")

    while True:
        choice = input("\nEnter your choice (1-6): ").strip()
        if choice in ["1", "2", "3", "4", "5", "6"]:
            return choice
        print("Please enter a number between 1 and 6.")


def select_question_file(quiz_app: QuizApp) -> Optional[str]:
    """Let user select a question file."""
    available_files = quiz_app.get_available_question_files()

    if not available_files:
        print("\nNo JSON question files found in current directory.")
        print("Option 2: Create a sample questions file.")
        return None

    print("\nAvailable question files:")
    for i, file in enumerate(available_files, 1):
        print(f"{i}. {file}")

    while True:
        try:
            choice = input(f"\nSelect file (1-{len(available_files)}): ").strip()
            choice_num = int(choice)

            if 1 <= choice_num <= len(available_files):
                return available_files[choice_num - 1]
            else:
                print(f"Please enter a number between 1 and {len(available_files)}")
        except ValueError:
            print("Please enter a valid number")


def main():
    """Main program loop."""
    quiz_app = QuizApp()

    display_welcome()

    while True:
        choice = get_menu_choice()

        if choice == "1":
            # Load questions from file
            filename = select_question_file(quiz_app)
            if filename:
                if quiz_app.load_questions_from_json(filename):
                    print(
                        f"\n[OK] Successfully loaded {quiz_app.total_questions} questions from '{filename}'"
                    )
                else:
                    print(f"\n[X] Failed to load questions from '{filename}'")

        elif choice == "2":
            # Create sample questions file
            filename = input(
                "Enter filename (default: sample_questions.json): "
            ).strip()
            if not filename:
                filename = "sample_questions.json"
            if not filename.endswith(".json"):
                filename += ".json"

            quiz_app.create_sample_questions_file(filename)

        elif choice == "3":
            # Start quiz
            if not quiz_app.questions:
                print(
                    "\n[X] No questions loaded. Please load questions first (Option 1)."
                )
                continue

            results = quiz_app.run_quiz()
            quiz_app.display_results(results)

            # Ask to save results
            save_choice = input("\nSave results to file? (y/n): ").strip().lower()
            if save_choice in ["y", "yes"]:
                quiz_app.save_results(results)

        elif choice == "4":
            # View quiz history
            quiz_app.display_results_history()

        elif choice == "5":
            # Set time limit
            try:
                time_limit = int(
                    input("Enter time limit per question (seconds): ").strip()
                )
                quiz_app.set_time_limit(time_limit)
                print(
                    f"Time limit set to {quiz_app.time_limit_per_question} seconds per question."
                )
            except ValueError:
                print("Please enter a valid number.")

        elif choice == "6":
            # Exit
            print("\nThanks for using the Quiz App!")
            print("[TARGET] Goodbye! [TARGET]")
            break


if __name__ == "__main__":
    main()

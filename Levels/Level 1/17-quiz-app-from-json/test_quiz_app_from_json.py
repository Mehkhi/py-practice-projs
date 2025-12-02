#!/usr/bin/env python3
"""
Unit tests for Quiz App from JSON

Tests all functionality of the QuizApp class including:
- Loading questions from JSON files
- Answer checking and validation
- Quiz results calculation
- Time limit handling
- Results saving and loading
"""

import unittest
import json
import os
import tempfile
from datetime import datetime
from quiz_app_from_json import QuizApp


class TestQuizApp(unittest.TestCase):
    """Test cases for QuizApp class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.quiz_app = QuizApp()
        self.temp_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        os.chdir(self.temp_dir)

    def tearDown(self):
        """Clean up after each test method."""
        os.chdir(self.original_dir)
        # Clean up temp files
        for file in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file))
        os.rmdir(self.temp_dir)

    def create_test_questions_file(self, filename: str, questions: list):
        """Helper method to create a test questions JSON file."""
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(questions, file, indent=2)

    def test_initialization(self):
        """Test quiz app initialization with default values."""
        self.assertEqual(len(self.quiz_app.questions), 0)
        self.assertEqual(self.quiz_app.current_question_index, 0)
        self.assertEqual(self.quiz_app.score, 0)
        self.assertEqual(self.quiz_app.total_questions, 0)
        self.assertEqual(len(self.quiz_app.answers), 0)
        self.assertIsNone(self.quiz_app.start_time)
        self.assertIsNone(self.quiz_app.end_time)
        self.assertEqual(self.quiz_app.time_limit_per_question, 30)

    def test_load_questions_from_json_list(self):
        """Test loading questions from JSON file with list structure."""
        questions = [
            {
                "question": "What is 2+2?",
                "options": ["3", "4", "5"],
                "correct_answer": "4",
                "category": "Math",
            },
            {
                "question": "Capital of France?",
                "options": ["London", "Paris", "Berlin"],
                "correct_answer": "Paris",
                "category": "Geography",
            },
        ]

        self.create_test_questions_file("test_questions.json", questions)
        result = self.quiz_app.load_questions_from_json("test_questions.json")

        self.assertTrue(result)
        self.assertEqual(len(self.quiz_app.questions), 2)
        self.assertEqual(self.quiz_app.total_questions, 2)
        self.assertEqual(self.quiz_app.questions[0]["question"], "What is 2+2?")
        self.assertEqual(self.quiz_app.questions[1]["correct_answer"], "Paris")

    def test_load_questions_from_json_dict(self):
        """Test loading questions from JSON file with dict structure."""
        questions_data = {
            "questions": [
                {
                    "question": "Test question",
                    "options": ["A", "B", "C"],
                    "correct_answer": "A",
                    "category": "Test",
                }
            ]
        }

        self.create_test_questions_file("test_questions.json", questions_data)
        result = self.quiz_app.load_questions_from_json("test_questions.json")

        self.assertTrue(result)
        self.assertEqual(len(self.quiz_app.questions), 1)
        self.assertEqual(self.quiz_app.questions[0]["question"], "Test question")

    def test_load_questions_file_not_found(self):
        """Test loading questions from non-existent file."""
        result = self.quiz_app.load_questions_from_json("nonexistent.json")
        self.assertFalse(result)

    def test_load_questions_invalid_json(self):
        """Test loading questions from invalid JSON file."""
        with open("invalid.json", "w") as file:
            file.write("{ invalid json }")

        result = self.quiz_app.load_questions_from_json("invalid.json")
        self.assertFalse(result)

    def test_load_questions_invalid_structure(self):
        """Test loading questions from JSON with invalid structure."""
        invalid_data = {"not_questions": "test"}
        self.create_test_questions_file("invalid_structure.json", invalid_data)

        result = self.quiz_app.load_questions_from_json("invalid_structure.json")
        self.assertFalse(result)

    def test_create_sample_questions_file(self):
        """Test creating sample questions file."""
        result = self.quiz_app.create_sample_questions_file("sample.json")
        self.assertTrue(result)
        self.assertTrue(os.path.exists("sample.json"))

        # Verify file contents
        with open("sample.json", "r") as file:
            data = json.load(file)

        self.assertIn("questions", data)
        self.assertGreater(len(data["questions"]), 0)

    def test_check_answer_multiple_choice_correct_number(self):
        """Test checking answer with correct numeric input."""
        question = {
            "question": "Test question",
            "options": ["A", "B", "C"],
            "correct_answer": "B",
        }

        result = self.quiz_app.check_answer(question, "2")
        self.assertTrue(result)

    def test_check_answer_multiple_choice_correct_text(self):
        """Test checking answer with correct text input."""
        question = {
            "question": "Test question",
            "options": ["A", "B", "C"],
            "correct_answer": "B",
        }

        result = self.quiz_app.check_answer(question, "B")
        self.assertTrue(result)

    def test_check_answer_multiple_choice_incorrect(self):
        """Test checking answer with incorrect input."""
        question = {
            "question": "Test question",
            "options": ["A", "B", "C"],
            "correct_answer": "B",
        }

        result = self.quiz_app.check_answer(question, "A")
        self.assertFalse(result)

    def test_check_answer_multiple_choice_invalid_number(self):
        """Test checking answer with invalid numeric input."""
        question = {
            "question": "Test question",
            "options": ["A", "B", "C"],
            "correct_answer": "B",
        }

        result = self.quiz_app.check_answer(question, "5")
        self.assertFalse(result)

    def test_check_answer_text_input_correct(self):
        """Test checking answer with text input (no options)."""
        question = {"question": "What is 2+2?", "correct_answer": "4"}

        result = self.quiz_app.check_answer(question, "4")
        self.assertTrue(result)

    def test_check_answer_text_input_incorrect(self):
        """Test checking answer with incorrect text input."""
        question = {"question": "What is 2+2?", "correct_answer": "4"}

        result = self.quiz_app.check_answer(question, "5")
        self.assertFalse(result)

    def test_check_answer_case_insensitive(self):
        """Test that answer checking is case insensitive."""
        question = {"question": "Test question", "correct_answer": "Answer"}

        result = self.quiz_app.check_answer(question, "answer")
        self.assertTrue(result)

        result = self.quiz_app.check_answer(question, "ANSWER")
        self.assertTrue(result)

    def test_check_answer_whitespace_handling(self):
        """Test that answer checking handles whitespace correctly."""
        question = {"question": "Test question", "correct_answer": "Answer"}

        result = self.quiz_app.check_answer(question, "  answer  ")
        self.assertTrue(result)

    def test_check_answer_empty_input(self):
        """Test checking answer with empty input."""
        question = {"question": "Test question", "correct_answer": "Answer"}

        result = self.quiz_app.check_answer(question, "")
        self.assertFalse(result)

        result = self.quiz_app.check_answer(question, None)
        self.assertFalse(result)

    def test_get_quiz_results_empty(self):
        """Test getting quiz results when no quiz has been taken."""
        results = self.quiz_app.get_quiz_results()
        self.assertEqual(results, {})

    def test_get_quiz_results_with_data(self):
        """Test getting quiz results with quiz data."""
        # Set up quiz data
        self.quiz_app.score = 3
        self.quiz_app.total_questions = 5
        self.quiz_app.answers = [
            {"question": "Q1", "is_correct": True},
            {"question": "Q2", "is_correct": False},
        ]
        self.quiz_app.start_time = datetime(2023, 1, 1, 10, 0, 0)
        self.quiz_app.end_time = datetime(2023, 1, 1, 10, 2, 30)

        results = self.quiz_app.get_quiz_results()

        self.assertEqual(results["score"], 3)
        self.assertEqual(results["total_questions"], 5)
        self.assertEqual(results["percentage"], 60.0)
        self.assertEqual(results["duration_seconds"], 150.0)
        self.assertEqual(len(results["answers"]), 2)

    def test_reset_quiz(self):
        """Test resetting quiz state."""
        # Set up some state
        self.quiz_app.current_question_index = 3
        self.quiz_app.score = 2
        self.quiz_app.answers = [{"test": "data"}]
        self.quiz_app.start_time = datetime.now()
        self.quiz_app.end_time = datetime.now()

        # Reset
        self.quiz_app.reset_quiz()

        # Check all values are reset
        self.assertEqual(self.quiz_app.current_question_index, 0)
        self.assertEqual(self.quiz_app.score, 0)
        self.assertEqual(len(self.quiz_app.answers), 0)
        self.assertIsNone(self.quiz_app.start_time)
        self.assertIsNone(self.quiz_app.end_time)

    def test_set_time_limit(self):
        """Test setting time limit per question."""
        self.quiz_app.set_time_limit(45)
        self.assertEqual(self.quiz_app.time_limit_per_question, 45)

        # Test minimum limit
        self.quiz_app.set_time_limit(2)
        self.assertEqual(self.quiz_app.time_limit_per_question, 5)  # Minimum 5 seconds

    def test_save_results(self):
        """Test saving quiz results to file."""
        results = {
            "score": 4,
            "total_questions": 5,
            "percentage": 80.0,
            "duration_seconds": 120.0,
            "start_time": "2023-01-01T10:00:00",
            "end_time": "2023-01-01T10:02:00",
            "answers": [],
        }

        result = self.quiz_app.save_results(results)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(self.quiz_app.results_file))

        # Verify file contents
        with open(self.quiz_app.results_file, "r") as file:
            saved_data = json.load(file)

        self.assertEqual(len(saved_data), 1)
        self.assertEqual(saved_data[0]["score"], 4)

    def test_save_results_append(self):
        """Test that saving results appends to existing file."""
        # Save first result
        results1 = {"score": 3, "total_questions": 5, "percentage": 60.0}
        self.quiz_app.save_results(results1)

        # Save second result
        results2 = {"score": 4, "total_questions": 5, "percentage": 80.0}
        self.quiz_app.save_results(results2)

        # Verify both results are saved
        with open(self.quiz_app.results_file, "r") as file:
            saved_data = json.load(file)

        self.assertEqual(len(saved_data), 2)
        self.assertEqual(saved_data[0]["score"], 3)
        self.assertEqual(saved_data[1]["score"], 4)

    def test_load_results_history(self):
        """Test loading quiz results history."""
        # Create test results file
        test_results = [
            {"score": 3, "total_questions": 5, "percentage": 60.0},
            {"score": 4, "total_questions": 5, "percentage": 80.0},
        ]

        with open(self.quiz_app.results_file, "w") as file:
            json.dump(test_results, file)

        history = self.quiz_app.load_results_history()
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["score"], 3)
        self.assertEqual(history[1]["score"], 4)

    def test_load_results_history_no_file(self):
        """Test loading results history when no file exists."""
        history = self.quiz_app.load_results_history()
        self.assertEqual(history, [])

    def test_get_available_question_files(self):
        """Test getting list of available question files."""
        # Create test files
        self.create_test_questions_file("questions1.json", [])
        self.create_test_questions_file("questions2.json", [])

        # Create results file (should be excluded)
        with open(self.quiz_app.results_file, "w") as file:
            json.dump([], file)

        available_files = self.quiz_app.get_available_question_files()

        self.assertEqual(len(available_files), 2)
        self.assertIn("questions1.json", available_files)
        self.assertIn("questions2.json", available_files)
        self.assertNotIn(self.quiz_app.results_file, available_files)


class TestQuizAppIntegration(unittest.TestCase):
    """Integration tests for QuizApp class."""

    def setUp(self):
        """Set up test fixtures."""
        self.quiz_app = QuizApp()
        self.temp_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        os.chdir(self.temp_dir)

    def tearDown(self):
        """Clean up after each test method."""
        os.chdir(self.original_dir)
        # Clean up temp files
        for file in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file))
        os.rmdir(self.temp_dir)

    def test_complete_quiz_workflow(self):
        """Test complete quiz workflow from loading to results."""
        # Create test questions
        questions = {
            "questions": [
                {
                    "question": "What is 1+1?",
                    "options": ["1", "2", "3"],
                    "correct_answer": "2",
                },
                {
                    "question": "Capital of France?",
                    "options": ["London", "Paris", "Berlin"],
                    "correct_answer": "Paris",
                },
            ]
        }

        with open("test_questions.json", "w") as file:
            json.dump(questions, file)

        # Load questions
        self.assertTrue(self.quiz_app.load_questions_from_json("test_questions.json"))
        self.assertEqual(self.quiz_app.total_questions, 2)

        # Simulate quiz answers
        self.quiz_app.reset_quiz()
        self.quiz_app.start_time = datetime.now()

        # Question 1 - correct answer
        self.quiz_app.current_question_index = 1
        q1 = self.quiz_app.questions[0]
        is_correct = self.quiz_app.check_answer(q1, "2")
        self.quiz_app.answers.append(
            {
                "question": q1["question"],
                "user_answer": "2",
                "correct_answer": q1["correct_answer"],
                "is_correct": is_correct,
                "question_number": 1,
            }
        )
        if is_correct:
            self.quiz_app.score += 1

        # Question 2 - incorrect answer
        self.quiz_app.current_question_index = 2
        q2 = self.quiz_app.questions[1]
        is_correct = self.quiz_app.check_answer(q2, "London")
        self.quiz_app.answers.append(
            {
                "question": q2["question"],
                "user_answer": "London",
                "correct_answer": q2["correct_answer"],
                "is_correct": is_correct,
                "question_number": 2,
            }
        )
        if is_correct:
            self.quiz_app.score += 1

        self.quiz_app.end_time = datetime.now()

        # Check results
        results = self.quiz_app.get_quiz_results()
        self.assertEqual(results["score"], 1)
        self.assertEqual(results["total_questions"], 2)
        self.assertEqual(results["percentage"], 50.0)
        self.assertEqual(len(results["answers"]), 2)
        self.assertTrue(results["answers"][0]["is_correct"])
        self.assertFalse(results["answers"][1]["is_correct"])

    def test_quiz_with_all_correct_answers(self):
        """Test quiz scenario with all correct answers."""
        questions = {
            "questions": [
                {"question": "Test 1", "correct_answer": "A"},
                {"question": "Test 2", "correct_answer": "B"},
            ]
        }

        with open("perfect_quiz.json", "w") as file:
            json.dump(questions, file)

        self.quiz_app.load_questions_from_json("perfect_quiz.json")

        # Simulate perfect score
        for i, question in enumerate(self.quiz_app.questions):
            is_correct = self.quiz_app.check_answer(
                question, question["correct_answer"]
            )
            self.assertTrue(is_correct)
            if is_correct:
                self.quiz_app.score += 1

        self.assertEqual(self.quiz_app.score, 2)
        self.assertEqual(self.quiz_app.total_questions, 2)

    def test_quiz_with_all_incorrect_answers(self):
        """Test quiz scenario with all incorrect answers."""
        questions = {
            "questions": [
                {"question": "Test 1", "correct_answer": "A"},
                {"question": "Test 2", "correct_answer": "B"},
            ]
        }

        with open("failed_quiz.json", "w") as file:
            json.dump(questions, file)

        self.quiz_app.load_questions_from_json("failed_quiz.json")

        # Simulate all wrong answers
        for question in self.quiz_app.questions:
            is_correct = self.quiz_app.check_answer(question, "Wrong")
            self.assertFalse(is_correct)
            if is_correct:
                self.quiz_app.score += 1

        self.assertEqual(self.quiz_app.score, 0)
        self.assertEqual(self.quiz_app.total_questions, 2)


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
"""
Unit tests for the Flashcards Study App.
"""

import json
import tempfile
import os
from flashcards import load_flashcards, check_answer


def test_load_flashcards_valid_file():
    """Test loading flashcards from a valid JSON file."""
    # Create a temporary file with valid flashcards
    test_data = [
        {"question": "What is 1+1?", "answer": "2"},
        {"question": "What is the capital of Japan?", "answer": "Tokyo"},
    ]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(test_data, f)
        temp_filename = f.name

    try:
        flashcards = load_flashcards(temp_filename)
        assert len(flashcards) == 2
        assert flashcards[0]["question"] == "What is 1+1?"
        assert flashcards[0]["answer"] == "2"
        assert flashcards[1]["question"] == "What is the capital of Japan?"
        assert flashcards[1]["answer"] == "Tokyo"
        print("[OK] test_load_flashcards_valid_file passed")
    finally:
        os.unlink(temp_filename)


def test_load_flashcards_invalid_file():
    """Test loading flashcards from a non-existent file."""
    flashcards = load_flashcards("nonexistent_file.json")
    assert flashcards == []
    print("[OK] test_load_flashcards_invalid_file passed")


def test_load_flashcards_invalid_json():
    """Test loading flashcards from a file with invalid JSON."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write("invalid json content")
        temp_filename = f.name

    try:
        flashcards = load_flashcards(temp_filename)
        assert flashcards == []
        print("[OK] test_load_flashcards_invalid_json passed")
    finally:
        os.unlink(temp_filename)


def test_check_answer_case_insensitive():
    """Test that answer checking is case-insensitive."""
    assert check_answer("PARIS", "Paris")
    assert check_answer("paris", "Paris")
    assert check_answer("Paris", "paris")
    assert check_answer("PARIS", "paris")
    assert not check_answer("London", "Paris")
    print("[OK] test_check_answer_case_insensitive passed")


def test_check_answer_with_whitespace():
    """Test that answer checking handles whitespace correctly."""
    assert check_answer("  Paris  ", "Paris")
    assert check_answer("Paris", "  Paris  ")
    assert check_answer("  Paris  ", "  Paris  ")
    print("[OK] test_check_answer_with_whitespace passed")


def run_tests():
    """Run all tests."""
    print("Running flashcards tests...\n")

    test_load_flashcards_valid_file()
    test_load_flashcards_invalid_file()
    test_load_flashcards_invalid_json()
    test_check_answer_case_insensitive()
    test_check_answer_with_whitespace()

    print("\n[CELEBRATION] All tests passed!")


if __name__ == "__main__":
    run_tests()

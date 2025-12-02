"""Tests for the brain teaser puzzle system."""

import unittest
from unittest.mock import Mock

from core.brain_teasers import (
    BrainTeaser,
    BrainTeaserManager,
    BrainTeaserType,
    Riddle,
    WordScramble,
    NumberSequence,
    PatternMatch,
    SimonSays,
    LockCombination,
)


class TestBrainTeasers(unittest.TestCase):
    """Test cases for brain teaser system."""

    def setUp(self):
        """Set up test fixtures."""
        # Create test riddles
        self.riddle = Riddle(
            riddle_id="test_riddle",
            question="What has keys but no locks?",
            answer="piano",
            alternatives=["a piano", "keyboard"],
            hint="It makes music.",
            difficulty=1,
        )

        self.riddle_teaser = BrainTeaser(
            teaser_id="test_riddle",
            teaser_type=BrainTeaserType.RIDDLE,
            name="Test Riddle",
            data=self.riddle,
            rewards={"gold": 50},
            attempts_allowed=3,
        )

        # Create test lock combination
        self.lock = LockCombination(
            puzzle_id="test_lock",
            combination=[4, 7, 2],
            num_dials=3,
            max_value=9,
            clues=["First is half of eight", "Second is luckiest", "Third is only even prime"],
        )

        self.lock_teaser = BrainTeaser(
            teaser_id="test_lock",
            teaser_type=BrainTeaserType.LOCK_COMBINATION,
            name="Test Lock",
            data=self.lock,
            rewards={"items": {"key": 1}},
            attempts_allowed=0,  # Unlimited
        )

        # Create test Simon Says
        self.simon = SimonSays(
            puzzle_id="test_simon",
            sequence_length=3,
            colors=["red", "blue", "green", "yellow"],
        )

        self.simon_teaser = BrainTeaser(
            teaser_id="test_simon",
            teaser_type=BrainTeaserType.SIMON_SAYS,
            name="Test Simon Says",
            data=self.simon,
            rewards={"flags": ["simon_complete"]},
            attempts_allowed=3,
        )

        # Create manager with test teasers
        self.manager = BrainTeaserManager({
            "test_riddle": self.riddle_teaser,
            "test_lock": self.lock_teaser,
            "test_simon": self.simon_teaser,
        })

    def test_riddle_correct_answer(self):
        """Test that correct answer solves riddle."""
        correct, feedback = self.manager.check_answer("test_riddle", "piano")
        self.assertTrue(correct)
        self.assertIn("Correct", feedback)

    def test_riddle_alternative_accepted(self):
        """Test that alternative answers are accepted."""
        correct, feedback = self.manager.check_answer("test_riddle", "a piano")
        self.assertTrue(correct)
        self.assertIn("Correct", feedback)

    def test_riddle_case_insensitive(self):
        """Test that answer matching ignores case."""
        correct, feedback = self.manager.check_answer("test_riddle", "PIANO")
        self.assertTrue(correct)
        self.assertIn("Correct", feedback)

    def test_riddle_incorrect_answer(self):
        """Test that incorrect answer fails."""
        correct, feedback = self.manager.check_answer("test_riddle", "wrong")
        self.assertFalse(correct)
        self.assertIn("Incorrect", feedback)

    def test_combination_correct(self):
        """Test that correct combination solves lock."""
        correct, feedback = self.manager.check_answer("test_lock", [4, 7, 2])
        self.assertTrue(correct)
        self.assertIn("Correct", feedback)

    def test_combination_incorrect(self):
        """Test that incorrect combination fails."""
        correct, feedback = self.manager.check_answer("test_lock", [1, 2, 3])
        self.assertFalse(correct)
        self.assertIn("Incorrect", feedback)

    def test_attempts_tracking(self):
        """Test that attempts decrease on wrong answers."""
        initial_remaining = self.manager.get_remaining_attempts("test_riddle")
        self.assertEqual(initial_remaining, 3)

        # Wrong answer
        self.manager.check_answer("test_riddle", "wrong")
        remaining = self.manager.get_remaining_attempts("test_riddle")
        self.assertEqual(remaining, 2)

        # Another wrong answer
        self.manager.check_answer("test_riddle", "wrong again")
        remaining = self.manager.get_remaining_attempts("test_riddle")
        self.assertEqual(remaining, 1)

    def test_attempts_exhausted(self):
        """Test failure when attempts exhausted."""
        # Use up all attempts
        for _ in range(3):
            self.manager.check_answer("test_riddle", "wrong")

        # Next attempt should fail
        correct, feedback = self.manager.check_answer("test_riddle", "piano")
        self.assertFalse(correct)
        self.assertIn("No attempts remaining", feedback)

    def test_unlimited_attempts(self):
        """Test that zero attempts_allowed means unlimited."""
        remaining = self.manager.get_remaining_attempts("test_lock")
        self.assertEqual(remaining, -1)  # -1 means unlimited

        # Should be able to try many times
        for _ in range(10):
            self.manager.check_answer("test_lock", [1, 1, 1])
            remaining = self.manager.get_remaining_attempts("test_lock")
            self.assertEqual(remaining, -1)

    def test_rewards_granted(self):
        """Test that rewards are given on solve."""
        # Mark as solved
        self.manager.mark_solved("test_riddle")
        self.assertTrue(self.riddle_teaser.solved)
        self.assertIn("test_riddle", self.manager.solved_teasers)

    def test_simon_sequence_validation(self):
        """Test Simon Says sequence validation."""
        self.simon.generated_sequence = ["red", "blue", "green"]
        correct, feedback = self.manager.check_answer("test_simon", ["red", "blue", "green"])
        self.assertTrue(correct)

    def test_simon_wrong_length(self):
        """Test that wrong length sequence fails."""
        self.simon.generated_sequence = ["red", "blue", "green"]
        correct, feedback = self.manager.check_answer("test_simon", ["red", "blue"])
        self.assertFalse(correct)
        self.assertIn("Incorrect", feedback)

    def test_get_teaser(self):
        """Test retrieving teaser by ID."""
        teaser = self.manager.get_teaser("test_riddle")
        self.assertIsNotNone(teaser)
        self.assertEqual(teaser.teaser_id, "test_riddle")

    def test_get_teaser_not_found(self):
        """Test retrieving non-existent teaser."""
        teaser = self.manager.get_teaser("nonexistent")
        self.assertIsNone(teaser)

    def test_mark_solved(self):
        """Test marking teaser as solved."""
        self.assertFalse(self.riddle_teaser.solved)
        self.manager.mark_solved("test_riddle")
        self.assertTrue(self.riddle_teaser.solved)
        self.assertIn("test_riddle", self.manager.solved_teasers)

    def test_already_solved(self):
        """Test that already solved teaser returns correct."""
        self.manager.mark_solved("test_riddle")
        correct, feedback = self.manager.check_answer("test_riddle", "anything")
        self.assertTrue(correct)
        self.assertIn("already solved", feedback)

    def test_serialize_deserialize(self):
        """Test serialization and deserialization."""
        # Mark some as solved and use some attempts
        self.manager.mark_solved("test_riddle")
        self.manager.check_answer("test_lock", [1, 1, 1])  # Wrong answer

        # Serialize
        data = self.manager.serialize()
        self.assertIn("solved_teasers", data)
        self.assertIn("attempts", data)
        self.assertIn("test_riddle", data["solved_teasers"])
        self.assertIn("test_lock", data["attempts"])

        # Deserialize
        teaser_definitions = {
            "test_riddle": self.riddle_teaser,
            "test_lock": self.lock_teaser,
            "test_simon": self.simon_teaser,
        }
        restored = BrainTeaserManager.deserialize(data, teaser_definitions)

        # Check state restored
        self.assertIn("test_riddle", restored.solved_teasers)
        self.assertEqual(restored.attempts["test_lock"], 1)
        self.assertTrue(restored.teasers["test_riddle"].solved)

    def test_word_scramble(self):
        """Test word scramble puzzle type."""
        scramble = WordScramble(
            puzzle_id="test_scramble",
            word="puzzle",
            scrambled="lzepuz",
            hint="It's a type of game.",
        )

        scramble_teaser = BrainTeaser(
            teaser_id="test_scramble",
            teaser_type=BrainTeaserType.WORD_SCRAMBLE,
            name="Test Scramble",
            data=scramble,
            attempts_allowed=3,
        )

        manager = BrainTeaserManager({"test_scramble": scramble_teaser})

        # Correct answer
        correct, feedback = manager.check_answer("test_scramble", "puzzle")
        self.assertTrue(correct)

        # Incorrect answer
        correct, feedback = manager.check_answer("test_scramble", "wrong")
        self.assertFalse(correct)

    def test_number_sequence(self):
        """Test number sequence puzzle type."""
        sequence = NumberSequence(
            puzzle_id="test_sequence",
            sequence=[2, 4, 6, 8],
            answer=10,
            pattern_description="Even numbers",
        )

        sequence_teaser = BrainTeaser(
            teaser_id="test_sequence",
            teaser_type=BrainTeaserType.NUMBER_SEQUENCE,
            name="Test Sequence",
            data=sequence,
            attempts_allowed=3,
        )

        manager = BrainTeaserManager({"test_sequence": sequence_teaser})

        # Correct answer
        correct, feedback = manager.check_answer("test_sequence", 10)
        self.assertTrue(correct)

        # Incorrect answer
        correct, feedback = manager.check_answer("test_sequence", 12)
        self.assertFalse(correct)

    def test_pattern_match(self):
        """Test pattern match puzzle type."""
        pattern = PatternMatch(
            puzzle_id="test_pattern",
            grid=[["A", "B"], ["C", "D"]],
            answer_position=(1, 0),
            puzzle_type="odd_one_out",
        )

        pattern_teaser = BrainTeaser(
            teaser_id="test_pattern",
            teaser_type=BrainTeaserType.PATTERN_MATCH,
            name="Test Pattern",
            data=pattern,
            attempts_allowed=3,
        )

        manager = BrainTeaserManager({"test_pattern": pattern_teaser})

        # Correct answer
        correct, feedback = manager.check_answer("test_pattern", (1, 0))
        self.assertTrue(correct)

        # Incorrect answer
        correct, feedback = manager.check_answer("test_pattern", (0, 0))
        self.assertFalse(correct)


if __name__ == "__main__":
    unittest.main()

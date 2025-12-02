#!/usr/bin/env python3
"""
Unit tests for Dice Roller Simulator

Tests the core functionality of dice parsing, rolling, and statistics.
"""

import unittest
from unittest.mock import patch
from dice_roller_simulator import DiceRoller


class TestDiceRoller(unittest.TestCase):
    """Test cases for the DiceRoller class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.dice_roller = DiceRoller()

    def test_parse_dice_notation_basic(self):
        """Test parsing basic dice notation."""
        # Test 3d6
        num_dice, num_sides, modifier = self.dice_roller.parse_dice_notation("3d6")
        self.assertEqual(num_dice, 3)
        self.assertEqual(num_sides, 6)
        self.assertEqual(modifier, 0)

        # Test 1d20
        num_dice, num_sides, modifier = self.dice_roller.parse_dice_notation("1d20")
        self.assertEqual(num_dice, 1)
        self.assertEqual(num_sides, 20)
        self.assertEqual(modifier, 0)

    def test_parse_dice_notation_with_modifier(self):
        """Test parsing dice notation with modifiers."""
        # Test 2d6+3
        num_dice, num_sides, modifier = self.dice_roller.parse_dice_notation("2d6+3")
        self.assertEqual(num_dice, 2)
        self.assertEqual(num_sides, 6)
        self.assertEqual(modifier, 3)

        # Test 1d8-2
        num_dice, num_sides, modifier = self.dice_roller.parse_dice_notation("1d8-2")
        self.assertEqual(num_dice, 1)
        self.assertEqual(num_sides, 8)
        self.assertEqual(modifier, -2)

    def test_parse_dice_notation_implicit_one_die(self):
        """Test parsing notation with implicit single die."""
        num_dice, num_sides, modifier = self.dice_roller.parse_dice_notation("d6")
        self.assertEqual(num_dice, 1)
        self.assertEqual(num_sides, 6)
        self.assertEqual(modifier, 0)

    def test_parse_dice_notation_case_insensitive(self):
        """Test that parsing is case insensitive."""
        num_dice, num_sides, modifier = self.dice_roller.parse_dice_notation("3D6+2")
        self.assertEqual(num_dice, 3)
        self.assertEqual(num_sides, 6)
        self.assertEqual(modifier, 2)

    def test_parse_dice_notation_whitespace(self):
        """Test parsing with whitespace."""
        num_dice, num_sides, modifier = self.dice_roller.parse_dice_notation(
            "  3d6+2  "
        )
        self.assertEqual(num_dice, 3)
        self.assertEqual(num_sides, 6)
        self.assertEqual(modifier, 2)

    def test_parse_dice_notation_invalid(self):
        """Test parsing invalid notation raises ValueError."""
        with self.assertRaises(ValueError):
            self.dice_roller.parse_dice_notation("")

        with self.assertRaises(ValueError):
            self.dice_roller.parse_dice_notation("invalid")

        with self.assertRaises(ValueError):
            self.dice_roller.parse_dice_notation("3d")  # Missing sides

        with self.assertRaises(ValueError):
            self.dice_roller.parse_dice_notation("d6+")  # Incomplete modifier

        with self.assertRaises(ValueError):
            self.dice_roller.parse_dice_notation("0d6")  # Zero dice

        with self.assertRaises(ValueError):
            self.dice_roller.parse_dice_notation("3d1")  # One side

        with self.assertRaises(ValueError):
            self.dice_roller.parse_dice_notation("101d6")  # Too many dice

    def test_roll_dice(self):
        """Test dice rolling functionality."""
        # Test rolling multiple dice
        rolls = self.dice_roller.roll_dice(3, 6)
        self.assertEqual(len(rolls), 3)
        for roll in rolls:
            self.assertGreaterEqual(roll, 1)
            self.assertLessEqual(roll, 6)

        # Test rolling single die
        rolls = self.dice_roller.roll_dice(1, 20)
        self.assertEqual(len(rolls), 1)
        self.assertGreaterEqual(rolls[0], 1)
        self.assertLessEqual(rolls[0], 20)

    @patch("random.randint")
    def test_roll_dice_deterministic(self, mock_randint):
        """Test dice rolling with mocked random values."""
        mock_randint.side_effect = [4, 2, 6]

        rolls = self.dice_roller.roll_dice(3, 6)
        self.assertEqual(rolls, [4, 2, 6])

        # Verify randint was called correctly
        self.assertEqual(mock_randint.call_count, 3)
        mock_randint.assert_any_call(1, 6)

    @patch("random.randint")
    def test_roll_with_notation_basic(self, mock_randint):
        """Test rolling with basic notation."""
        mock_randint.side_effect = [3, 5, 2]  # Three rolls of 6-sided die

        result = self.dice_roller.roll_with_notation("3d6")

        self.assertEqual(result["num_dice"], 3)
        self.assertEqual(result["num_sides"], 6)
        self.assertEqual(result["modifier"], 0)
        self.assertEqual(result["individual_rolls"], [3, 5, 2])
        self.assertEqual(result["subtotal"], 10)
        self.assertEqual(result["total"], 10)
        self.assertIn("display", result)

    @patch("random.randint")
    def test_roll_with_notation_modifier(self, mock_randint):
        """Test rolling with notation including modifier."""
        mock_randint.side_effect = [4, 3]  # Two rolls of 6-sided die

        result = self.dice_roller.roll_with_notation("2d6+2")

        self.assertEqual(result["num_dice"], 2)
        self.assertEqual(result["num_sides"], 6)
        self.assertEqual(result["modifier"], 2)
        self.assertEqual(result["individual_rolls"], [4, 3])
        self.assertEqual(result["subtotal"], 7)
        self.assertEqual(result["total"], 9)

    def test_roll_with_notation_invalid(self):
        """Test rolling with invalid notation."""
        result = self.dice_roller.roll_with_notation("invalid")
        self.assertIn("error", result)

    def test_roll_history(self):
        """Test roll history tracking."""
        # Initially empty
        self.assertEqual(len(self.dice_roller.get_roll_history()), 0)

        # Add a roll
        self.dice_roller.roll_with_notation("1d6")
        self.assertEqual(len(self.dice_roller.get_roll_history()), 1)

        # Add another roll
        self.dice_roller.roll_with_notation("2d8+1")
        self.assertEqual(len(self.dice_roller.get_roll_history()), 2)

        # Clear history
        self.dice_roller.clear_history()
        self.assertEqual(len(self.dice_roller.get_roll_history()), 0)

    def test_statistics_empty(self):
        """Test statistics with no rolls."""
        stats = self.dice_roller.get_statistics()
        self.assertIn("message", stats)

    @patch("random.randint")
    def test_statistics_with_data(self, mock_randint):
        """Test statistics with roll data."""
        # Mock predictable rolls
        mock_randint.side_effect = [3, 5, 2, 4, 6]

        # Add some rolls
        self.dice_roller.roll_with_notation("2d6")  # 3 + 5 = 8
        self.dice_roller.roll_with_notation("1d6+1")  # 2 + 1 = 3
        self.dice_roller.roll_with_notation("2d6-1")  # 4 + 6 - 1 = 9

        stats = self.dice_roller.get_statistics()

        self.assertEqual(stats["total_rolls"], 3)
        self.assertEqual(stats["sum"], 20)  # 8 + 3 + 9
        self.assertEqual(stats["min"], 3)
        self.assertEqual(stats["max"], 9)
        self.assertAlmostEqual(stats["average"], 20 / 3, places=2)

    def test_format_roll_display(self):
        """Test roll result formatting."""
        # Test without modifier
        display = self.dice_roller._format_roll_display("3d6", [3, 5, 2], 0, 10)
        self.assertEqual(display, "3d6: 3 + 5 + 2 = 10")

        # Test with positive modifier
        display = self.dice_roller._format_roll_display("2d6+2", [4, 3], 2, 9)
        self.assertEqual(display, "2d6+2: 4 + 3 + 2 = 9")

        # Test with negative modifier
        display = self.dice_roller._format_roll_display("1d8-2", [5], -2, 3)
        self.assertEqual(display, "1d8-2: 5 - 2 = 3")


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete dice rolling workflow."""

    def setUp(self):
        """Set up test fixtures."""
        self.dice_roller = DiceRoller()

    def test_complete_workflow(self):
        """Test a complete workflow from parsing to statistics."""
        # Perform several rolls
        self.dice_roller.roll_with_notation("1d6")
        self.dice_roller.roll_with_notation("2d8+1")
        self.dice_roller.roll_with_notation("d20-5")

        # Check history
        history = self.dice_roller.get_roll_history()
        self.assertEqual(len(history), 3)

        # Check statistics
        stats = self.dice_roller.get_statistics()
        self.assertEqual(stats["total_rolls"], 3)
        self.assertIn("average", stats)
        self.assertIn("min", stats)
        self.assertIn("max", stats)


if __name__ == "__main__":
    unittest.main()

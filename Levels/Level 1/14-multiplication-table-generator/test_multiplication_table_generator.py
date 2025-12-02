#!/usr/bin/env python3
"""
Unit tests for Multiplication Table Generator

Tests the core functionality of table generation, formatting, and export.
"""

import unittest
import os
import tempfile
from unittest.mock import patch, mock_open
from multiplication_table_generator import MultiplicationTableGenerator


class TestMultiplicationTableGenerator(unittest.TestCase):
    """Test cases for the MultiplicationTableGenerator class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.generator = MultiplicationTableGenerator()

    def test_initial_state(self):
        """Test generator initial state."""
        self.assertEqual(len(self.generator.table), 0)
        self.assertEqual(self.generator.start_range, 1)
        self.assertEqual(self.generator.end_range, 10)
        self.assertFalse(self.generator.use_color)

    def test_validate_input_positive_int_valid(self):
        """Test valid positive integer input."""
        is_valid, value, error = self.generator.validate_input("5", "positive_int")

        self.assertTrue(is_valid)
        self.assertEqual(value, 5)
        self.assertEqual(error, "")

    def test_validate_input_positive_int_invalid(self):
        """Test invalid positive integer input."""
        # Empty input
        is_valid, value, error = self.generator.validate_input("", "positive_int")
        self.assertFalse(is_valid)
        self.assertIsNone(value)
        self.assertIn("cannot be empty", error)

        # Non-integer
        is_valid, value, error = self.generator.validate_input("abc", "positive_int")
        self.assertFalse(is_valid)
        self.assertIsNone(value)
        self.assertIn("valid integer", error)

        # Zero
        is_valid, value, error = self.generator.validate_input("0", "positive_int")
        self.assertFalse(is_valid)
        self.assertIsNone(value)
        self.assertIn("greater than 0", error)

        # Negative
        is_valid, value, error = self.generator.validate_input("-5", "positive_int")
        self.assertFalse(is_valid)
        self.assertIsNone(value)
        self.assertIn("greater than 0", error)

        # Too large
        is_valid, value, error = self.generator.validate_input("101", "positive_int")
        self.assertFalse(is_valid)
        self.assertIsNone(value)
        self.assertIn("less than or equal to 100", error)

    def test_validate_input_range_valid(self):
        """Test valid range input."""
        is_valid, value, error = self.generator.validate_input("50", "range")

        self.assertTrue(is_valid)
        self.assertEqual(value, 50)
        self.assertEqual(error, "")

    def test_validate_input_range_invalid(self):
        """Test invalid range input."""
        # Too small
        is_valid, value, error = self.generator.validate_input("0", "range")
        self.assertFalse(is_valid)
        self.assertIsNone(value)
        self.assertIn("at least 1", error)

        # Too large
        is_valid, value, error = self.generator.validate_input("1001", "range")
        self.assertFalse(is_valid)
        self.assertIsNone(value)
        self.assertIn("less than or equal to 1000", error)

    def test_generate_table_standard(self):
        """Test generating standard 1-10 table."""
        table = self.generator.generate_table(1, 10)

        # Check table dimensions (11x11 including headers)
        self.assertEqual(len(table), 11)
        self.assertEqual(len(table[0]), 11)

        # Check header row
        self.assertEqual(table[0][1], 1)
        self.assertEqual(table[0][10], 10)

        # Check header column
        self.assertEqual(table[1][0], 1)
        self.assertEqual(table[10][0], 10)

        # Check multiplication result
        self.assertEqual(table[3][4], 12)  # 3 * 4
        self.assertEqual(table[7][8], 56)  # 7 * 8

        # Check generator state
        self.assertEqual(self.generator.start_range, 1)
        self.assertEqual(self.generator.end_range, 10)

    def test_generate_table_custom_range(self):
        """Test generating custom range table."""
        table = self.generator.generate_table(5, 8)

        # Check table dimensions (5x5 including headers: 5,6,7,8 + header)
        self.assertEqual(len(table), 5)
        self.assertEqual(len(table[0]), 5)

        # Check header row
        self.assertEqual(table[0][1], 5)
        self.assertEqual(table[0][4], 8)

        # Check header column
        self.assertEqual(table[1][0], 5)
        self.assertEqual(table[4][0], 8)

        # Check multiplication result
        self.assertEqual(table[1][1], 25)  # 5 * 5
        self.assertEqual(table[2][4], 48)  # 6 * 8

    def test_generate_table_reversed_range(self):
        """Test generating table with start > end."""
        table = self.generator.generate_table(10, 5)

        # Should swap the range
        self.assertEqual(self.generator.start_range, 5)
        self.assertEqual(self.generator.end_range, 10)

        # Check table dimensions (6x6 including headers: 5,6,7,8,9,10 + header)
        self.assertEqual(len(table), 7)
        self.assertEqual(len(table[0]), 7)

    def test_generate_table_single_value(self):
        """Test generating table with single value."""
        table = self.generator.generate_table(7, 7)

        # Check table dimensions (2x2 including headers)
        self.assertEqual(len(table), 2)
        self.assertEqual(len(table[0]), 2)

        # Check multiplication result
        self.assertEqual(table[1][1], 49)  # 7 * 7

    def test_get_column_width(self):
        """Test column width calculation."""
        # No table
        width = self.generator.get_column_width()
        self.assertEqual(width, 4)

        # Small table
        self.generator.generate_table(1, 3)
        width = self.generator.get_column_width()
        self.assertEqual(width, 4)  # Max value is 9, so width is 4

        # Larger table
        self.generator.generate_table(1, 12)
        width = self.generator.get_column_width()
        self.assertEqual(width, 4)  # Max value is 144, so width is 4

        # Very large table
        self.generator.generate_table(10, 20)
        width = self.generator.get_column_width()
        self.assertEqual(width, 4)  # Max value is 400, so width is 4

    def test_format_table_no_color(self):
        """Test table formatting without color."""
        self.generator.generate_table(1, 3)
        formatted = self.generator.format_table(use_color=False)

        # Check that table contains expected elements
        self.assertIn("Multiplication Table (1 to 3)", formatted)
        self.assertIn("1", formatted)
        self.assertIn("2", formatted)
        self.assertIn("3", formatted)
        self.assertIn("4", formatted)  # 2*2
        self.assertIn("6", formatted)  # 2*3
        self.assertIn("9", formatted)  # 3*3

        # Check that no color codes are present
        self.assertNotIn("\033[", formatted)

    def test_format_table_with_color(self):
        """Test table formatting with color."""
        self.generator.generate_table(1, 3)
        formatted = self.generator.format_table(use_color=True)

        # Check that color codes are present
        self.assertIn("\033[", formatted)
        self.assertIn("\033[94m", formatted)  # Blue for headers
        self.assertIn("\033[92m", formatted)  # Green for even numbers
        self.assertIn("\033[91m", formatted)  # Red for odd numbers

    def test_format_table_no_table(self):
        """Test formatting when no table exists."""
        formatted = self.generator.format_table()
        self.assertIn("No table generated", formatted)

    @patch("builtins.open", new_callable=mock_open)
    def test_export_to_csv_success(self, mock_file):
        """Test successful CSV export."""
        self.generator.generate_table(1, 3)

        result = self.generator.export_to_csv("test.csv")

        self.assertTrue(result)
        mock_file.assert_called_once_with("test.csv", "w", newline="")

        # Check that CSV writer was used correctly
        handle = mock_file()
        written_calls = handle.write.call_args_list
        self.assertGreater(len(written_calls), 0)

    def test_export_to_csv_no_table(self):
        """Test CSV export when no table exists."""
        result = self.generator.export_to_csv("test.csv")
        self.assertFalse(result)

    @patch("builtins.open", side_effect=IOError("Permission denied"))
    def test_export_to_csv_error(self, mock_file):
        """Test CSV export with file error."""
        self.generator.generate_table(1, 3)

        result = self.generator.export_to_csv("test.csv")
        self.assertFalse(result)

    def test_get_table_info_no_table(self):
        """Test getting table info when no table exists."""
        info = self.generator.get_table_info()

        self.assertFalse(info["has_table"])
        self.assertEqual(len(info), 1)

    def test_get_table_info_with_table(self):
        """Test getting table info when table exists."""
        self.generator.generate_table(5, 8)
        info = self.generator.get_table_info()

        self.assertTrue(info["has_table"])
        self.assertEqual(info["start_range"], 5)
        self.assertEqual(info["end_range"], 8)
        self.assertEqual(info["size"], 4)
        self.assertEqual(info["total_cells"], 16)
        self.assertEqual(info["max_value"], 64)  # 8*8
        self.assertIsInstance(info["column_width"], int)


class TestMultiplicationTableIntegration(unittest.TestCase):
    """Integration tests for complete workflows."""

    def setUp(self):
        """Set up test fixtures."""
        self.generator = MultiplicationTableGenerator()

    def test_complete_workflow_standard_table(self):
        """Test complete workflow with standard table."""
        # Generate table
        table = self.generator.generate_table(1, 5)
        self.assertEqual(len(table), 6)

        # Format table
        formatted = self.generator.format_table()
        self.assertIn("Multiplication Table (1 to 5)", formatted)

        # Get info
        info = self.generator.get_table_info()
        self.assertTrue(info["has_table"])
        self.assertEqual(info["size"], 5)

        # Export to CSV
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".csv") as f:
            filename = f.name

        try:
            result = self.generator.export_to_csv(filename)
            self.assertTrue(result)

            # Check file exists and has content
            self.assertTrue(os.path.exists(filename))
            with open(filename, "r") as f:
                content = f.read()
                self.assertIn("1,2,3,4,5", content)
        finally:
            if os.path.exists(filename):
                os.unlink(filename)

    def test_workflow_with_color_toggle(self):
        """Test workflow with color toggle functionality."""
        # Generate table
        self.generator.generate_table(1, 3)

        # Format without color
        formatted_no_color = self.generator.format_table(use_color=False)
        self.assertNotIn("\033[", formatted_no_color)

        # Format with color
        formatted_with_color = self.generator.format_table(use_color=True)
        self.assertIn("\033[", formatted_with_color)

        # Toggle generator color setting
        formatted_toggle = self.generator.format_table(use_color=True)
        self.assertIn("\033[", formatted_toggle)

    def test_multiple_table_generation(self):
        """Test generating multiple different tables."""
        # First table
        self.generator.generate_table(1, 3)
        info1 = self.generator.get_table_info()
        self.assertEqual(info1["size"], 3)

        # Second table
        self.generator.generate_table(5, 7)
        info2 = self.generator.get_table_info()
        self.assertEqual(info2["size"], 3)
        self.assertEqual(info2["start_range"], 5)
        self.assertEqual(info2["end_range"], 7)

        # Third table (N×N)
        self.generator.generate_table(1, 8)
        info3 = self.generator.get_table_info()
        self.assertEqual(info3["size"], 8)

        # Verify tables are different
        self.assertNotEqual(info1["max_value"], info2["max_value"])
        self.assertNotEqual(info2["max_value"], info3["max_value"])


if __name__ == "__main__":
    unittest.main()

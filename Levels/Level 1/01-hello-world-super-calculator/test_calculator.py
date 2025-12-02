#!/usr/bin/env python3
"""
Unit tests for the Super Calculator
"""

import unittest
import tempfile
import os
from hello_world_super_calculator import SuperCalculator


class TestSuperCalculator(unittest.TestCase):
    """Test cases for SuperCalculator class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_file.close()

        # Create calculator with temporary history file
        self.calc = SuperCalculator()
        self.calc.history_file = self.temp_file.name

    def tearDown(self):
        """Clean up test fixtures."""
        # Remove temporary file
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)

    def test_basic_operations(self):
        """Test basic arithmetic operations."""
        # Test addition
        result = self.calc.basic_operation(5, '+', 3)
        self.assertEqual(result, 8)

        # Test subtraction
        result = self.calc.basic_operation(10, '-', 4)
        self.assertEqual(result, 6)

        # Test multiplication
        result = self.calc.basic_operation(3, '*', 4)
        self.assertEqual(result, 12)

        # Test division
        result = self.calc.basic_operation(15, '/', 3)
        self.assertEqual(result, 5)

    def test_division_by_zero(self):
        """Test division by zero handling."""
        result = self.calc.basic_operation(10, '/', 0)
        self.assertIsNone(result)

    def test_validate_number(self):
        """Test number validation."""
        # Valid numbers
        self.assertEqual(self.calc.validate_number("5"), 5.0)
        self.assertEqual(self.calc.validate_number("3.14"), 3.14)
        self.assertEqual(self.calc.validate_number("-10"), -10.0)

        # Invalid numbers
        self.assertIsNone(self.calc.validate_number("abc"))
        self.assertIsNone(self.calc.validate_number(""))
        self.assertIsNone(self.calc.validate_number("5.5.5"))

    def test_memory_operations(self):
        """Test memory operations."""
        # Test memory add
        self.calc.memory_add(10)
        self.assertEqual(self.calc.memory, 10.0)

        # Test memory subtract
        self.calc.memory_subtract(3)
        self.assertEqual(self.calc.memory, 7.0)

        # Test memory clear
        self.calc.memory_clear()
        self.assertEqual(self.calc.memory, 0.0)

    def test_expression_parsing(self):
        """Test expression parsing."""
        # Simple expressions
        self.assertEqual(self.calc.parse_expression("2 + 3"), 5.0)
        self.assertEqual(self.calc.parse_expression("10 - 4"), 6.0)
        self.assertEqual(self.calc.parse_expression("3 * 4"), 12.0)
        self.assertEqual(self.calc.parse_expression("15 / 3"), 5.0)

        # Complex expressions with precedence
        self.assertEqual(self.calc.parse_expression("2 + 3 * 4"), 14.0)
        self.assertEqual(self.calc.parse_expression("(2 + 3) * 4"), 20.0)

        # Division by zero in expression
        self.assertIsNone(self.calc.parse_expression("10 / 0"))

        # Invalid expressions
        self.assertIsNone(self.calc.parse_expression("2 + abc"))
        self.assertIsNone(self.calc.parse_expression(""))

    def test_command_normalization(self):
        """Test command normalization and aliases."""
        # Test aliases
        self.assertEqual(self.calc.normalize_command("add"), "+")
        self.assertEqual(self.calc.normalize_command("subtract"), "-")
        self.assertEqual(self.calc.normalize_command("multiply"), "*")
        self.assertEqual(self.calc.normalize_command("divide"), "/")
        self.assertEqual(self.calc.normalize_command("quit"), "q")
        self.assertEqual(self.calc.normalize_command("help"), "?")

        # Test case insensitivity
        self.assertEqual(self.calc.normalize_command("ADD"), "+")
        self.assertEqual(self.calc.normalize_command("Quit"), "q")

        # Test unknown commands
        self.assertEqual(self.calc.normalize_command("unknown"), "unknown")


def run_tests():
    """Run all tests."""
    unittest.main(verbosity=2)


if __name__ == "__main__":
    run_tests()

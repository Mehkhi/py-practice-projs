#!/usr/bin/env python3
"""
Unit tests for the Unit Converter application.
Tests core functionality including conversions, validation, and error handling.
"""

import unittest
import os
from unit_converter import UnitConverter, validate_number_input


class TestUnitConverter(unittest.TestCase):
    """Test cases for the UnitConverter class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.converter = UnitConverter()
        # Clean up any existing history file
        if os.path.exists(self.converter.history_file):
            os.remove(self.converter.history_file)

    def tearDown(self):
        """Clean up after each test method."""
        # Remove history file if it exists
        if os.path.exists(self.converter.history_file):
            os.remove(self.converter.history_file)

    def test_length_conversion(self):
        """Test length unit conversions."""
        # Test meter to centimeter
        result = self.converter.convert(1, "m", "cm", "length")
        self.assertAlmostEqual(result, 100.0, places=6)

        # Test inch to foot
        result = self.converter.convert(12, "in", "ft", "length")
        self.assertAlmostEqual(result, 1.0, places=6)

        # Test kilometer to mile
        result = self.converter.convert(1, "km", "mi", "length")
        self.assertAlmostEqual(result, 0.621371, places=6)

    def test_weight_conversion(self):
        """Test weight unit conversions."""
        # Test kilogram to gram
        result = self.converter.convert(1, "kg", "g", "weight")
        self.assertAlmostEqual(result, 1000.0, places=6)

        # Test pound to ounce
        result = self.converter.convert(1, "lb", "oz", "weight")
        self.assertAlmostEqual(result, 16.0, places=6)

        # Test gram to milligram
        result = self.converter.convert(1, "g", "mg", "weight")
        self.assertAlmostEqual(result, 1000.0, places=6)

    def test_volume_conversion(self):
        """Test volume unit conversions."""
        # Test liter to milliliter
        result = self.converter.convert(1, "l", "ml", "volume")
        self.assertAlmostEqual(result, 1000.0, places=6)

        # Test gallon to quart
        result = self.converter.convert(1, "gal", "qt", "volume")
        self.assertAlmostEqual(result, 4.0, places=5)

        # Test cup to fluid ounce
        result = self.converter.convert(1, "cup", "fl_oz", "volume")
        self.assertAlmostEqual(result, 8.0, places=6)

    def test_invalid_conversion(self):
        """Test invalid conversion scenarios."""
        # Test invalid category
        result = self.converter.convert(1, "m", "cm", "invalid_category")
        self.assertIsNone(result)

        # Test invalid source unit
        result = self.converter.convert(1, "invalid_unit", "cm", "length")
        self.assertIsNone(result)

        # Test invalid target unit
        result = self.converter.convert(1, "m", "invalid_unit", "length")
        self.assertIsNone(result)

    def test_conversion_history(self):
        """Test conversion history functionality."""
        # Initially no history
        history = self.converter.get_conversion_history()
        self.assertEqual(len(history), 0)

        # Perform a conversion
        self.converter.convert(10, "m", "cm", "length")

        # Check history
        history = self.converter.get_conversion_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["value"], 10)
        self.assertEqual(history[0]["from_unit"], "m")
        self.assertEqual(history[0]["to_unit"], "cm")
        self.assertEqual(history[0]["category"], "length")
        self.assertAlmostEqual(history[0]["result"], 1000.0, places=6)

        # Clear history
        self.converter.clear_history()
        history = self.converter.get_conversion_history()
        self.assertEqual(len(history), 0)

    def test_get_categories(self):
        """Test getting available categories."""
        categories = self.converter.get_categories()
        expected_categories = ["length", "weight", "volume"]
        self.assertEqual(set(categories), set(expected_categories))

    def test_get_units(self):
        """Test getting available units for categories."""
        # Test length units
        length_units = self.converter.get_units("length")
        expected_length_units = ["mm", "cm", "m", "km", "in", "ft", "yd", "mi"]
        self.assertEqual(set(length_units), set(expected_length_units))

        # Test weight units
        weight_units = self.converter.get_units("weight")
        expected_weight_units = ["mg", "g", "kg", "oz", "lb", "ton"]
        self.assertEqual(set(weight_units), set(expected_weight_units))

        # Test volume units
        volume_units = self.converter.get_units("volume")
        expected_volume_units = ["ml", "l", "fl_oz", "cup", "pt", "qt", "gal"]
        self.assertEqual(set(volume_units), set(expected_volume_units))

        # Test invalid category
        invalid_units = self.converter.get_units("invalid_category")
        self.assertEqual(invalid_units, [])


class TestValidationFunctions(unittest.TestCase):
    """Test cases for validation functions."""

    def test_validate_number_input_valid(self):
        """Test valid number input validation."""
        # Test positive integers
        result = validate_number_input("10")
        self.assertEqual(result, 10.0)

        # Test positive floats
        result = validate_number_input("3.14")
        self.assertEqual(result, 3.14)

        # Test with whitespace
        result = validate_number_input("  5.5  ")
        self.assertEqual(result, 5.5)

    def test_validate_number_input_invalid(self):
        """Test invalid number input validation."""
        # Test negative numbers
        result = validate_number_input("-5")
        self.assertIsNone(result)

        # Test non-numeric input
        result = validate_number_input("abc")
        self.assertIsNone(result)

        # Test empty input
        result = validate_number_input("")
        self.assertIsNone(result)

        # Test mixed input
        result = validate_number_input("5abc")
        self.assertIsNone(result)


def run_tests():
    """Run all unit tests."""
    print("[TEST TUBE] Running Unit Converter Tests...")
    print("=" * 50)

    # Create test suite
    loader = unittest.TestLoader()
    test_suite = unittest.TestSuite()

    # Add test cases
    test_suite.addTests(loader.loadTestsFromTestCase(TestUnitConverter))
    test_suite.addTests(loader.loadTestsFromTestCase(TestValidationFunctions))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    # Print summary
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("[OK] All tests passed!")
    else:
        print(
            f"[X] {len(result.failures)} test(s) failed, {len(result.errors)} error(s)"
        )

    return result.wasSuccessful()


if __name__ == "__main__":
    run_tests()

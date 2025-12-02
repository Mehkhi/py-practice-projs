#!/usr/bin/env python3
"""
Unit tests for Simple & Compound Interest Calculator

Tests the core calculation functions and input validation.
"""

import unittest
from simple_interest_compound_calculator import (
    calculate_simple_interest,
    calculate_compound_interest,
    get_year_by_year_growth,
    validate_input
)


class TestInterestCalculations(unittest.TestCase):
    """Test cases for interest calculation functions."""

    def test_simple_interest_basic(self):
        """Test basic simple interest calculation."""
        # Test case: $1000 at 5% for 2 years
        result = calculate_simple_interest(1000, 5, 2)
        expected = 1000 * 0.05 * 2  # $100
        self.assertAlmostEqual(result, expected, places=2)

    def test_simple_interest_zero_rate(self):
        """Test simple interest with zero rate."""
        result = calculate_simple_interest(1000, 0, 2)
        self.assertEqual(result, 0)

    def test_simple_interest_zero_time(self):
        """Test simple interest with zero time."""
        result = calculate_simple_interest(1000, 5, 0)
        self.assertEqual(result, 0)

    def test_compound_interest_basic(self):
        """Test basic compound interest calculation."""
        # Test case: $1000 at 5% for 2 years, compounded annually
        result = calculate_compound_interest(1000, 5, 2, 1)
        expected = 1000 * (1.05 ** 2) - 1000  # $102.50
        self.assertAlmostEqual(result, expected, places=2)

    def test_compound_interest_monthly(self):
        """Test compound interest with monthly compounding."""
        # Test case: $1000 at 5% for 1 year, compounded monthly
        result = calculate_compound_interest(1000, 5, 1, 12)
        expected = 1000 * (1 + 0.05/12) ** 12 - 1000
        self.assertAlmostEqual(result, expected, places=2)

    def test_compound_vs_simple_comparison(self):
        """Test that compound interest is greater than simple interest for same parameters."""
        principal, rate, time = 1000, 5, 2
        simple = calculate_simple_interest(principal, rate, time)
        compound = calculate_compound_interest(principal, rate, time, 1)

        self.assertGreater(compound, simple)

    def test_year_by_year_growth_structure(self):
        """Test year-by-year growth data structure."""
        growth_data = get_year_by_year_growth(1000, 5, 3, 1)

        # Check that we get the right number of years
        self.assertEqual(len(growth_data), 3)

        # Check that each year has the required keys
        for year_data in growth_data:
            self.assertIn('year', year_data)
            self.assertIn('compound_amount', year_data)
            self.assertIn('simple_amount', year_data)
            self.assertIn('year_interest', year_data)
            self.assertIn('total_interest', year_data)

    def test_year_by_year_growth_values(self):
        """Test year-by-year growth calculation values."""
        growth_data = get_year_by_year_growth(1000, 10, 2, 1)

        # First year: $1000 * 1.1 = $1100, interest = $100
        self.assertAlmostEqual(growth_data[0]['compound_amount'], 1100, places=2)
        self.assertAlmostEqual(growth_data[0]['year_interest'], 100, places=2)

        # Second year: $1100 * 1.1 = $1210, interest = $110
        self.assertAlmostEqual(growth_data[1]['compound_amount'], 1210, places=2)
        self.assertAlmostEqual(growth_data[1]['year_interest'], 110, places=2)


class TestInputValidation(unittest.TestCase):
    """Test cases for input validation function."""

    def test_valid_positive_number(self):
        """Test validation with valid positive number."""
        result = validate_input("100.50", "test")
        self.assertEqual(result, 100.50)

    def test_valid_integer(self):
        """Test validation with valid integer."""
        result = validate_input("100", "test")
        self.assertEqual(result, 100.0)

    def test_empty_input(self):
        """Test validation with empty input."""
        with self.assertRaises(ValueError) as context:
            validate_input("", "test")
        self.assertIn("cannot be empty", str(context.exception))

    def test_whitespace_input(self):
        """Test validation with whitespace-only input."""
        with self.assertRaises(ValueError) as context:
            validate_input("   ", "test")
        self.assertIn("cannot be empty", str(context.exception))

    def test_negative_number(self):
        """Test validation with negative number."""
        with self.assertRaises(ValueError) as context:
            validate_input("-100", "test")
        self.assertIn("cannot be negative", str(context.exception))

    def test_non_numeric_input(self):
        """Test validation with non-numeric input."""
        with self.assertRaises(ValueError) as context:
            validate_input("abc", "test")
        self.assertIn("must be a valid number", str(context.exception))

    def test_mixed_input(self):
        """Test validation with mixed numeric and non-numeric input."""
        with self.assertRaises(ValueError) as context:
            validate_input("100abc", "test")
        self.assertIn("must be a valid number", str(context.exception))


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions."""

    def test_very_small_amounts(self):
        """Test with very small principal amounts."""
        result = calculate_simple_interest(0.01, 1, 1)
        self.assertAlmostEqual(result, 0.0001, places=4)

    def test_very_high_rate(self):
        """Test with very high interest rate."""
        result = calculate_simple_interest(1000, 100, 1)
        self.assertEqual(result, 1000)

    def test_very_long_time(self):
        """Test with very long time period."""
        result = calculate_compound_interest(1000, 5, 100, 1)
        # Should be a very large number (1000 * 1.05^100 - 1000 ≈ 130,501)
        self.assertGreater(result, 100000)

    def test_fractional_time(self):
        """Test with fractional time periods."""
        result = calculate_simple_interest(1000, 10, 0.5)
        self.assertEqual(result, 50)  # Half year at 10% = 5%


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)

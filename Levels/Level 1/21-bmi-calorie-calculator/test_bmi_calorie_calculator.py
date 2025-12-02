#!/usr/bin/env python3
"""
Unit tests for BMI & Calorie Calculator

Tests core functionality including BMI calculation, calorie estimation,
and weight goal calculations.
"""

import unittest
import os
import tempfile
from bmi_calorie_calculator import BMICalculator


class TestBMICalculator(unittest.TestCase):
    """Test cases for BMICalculator class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary file for testing history
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_file.close()

        # Create calculator instance with temporary history file
        self.calculator = BMICalculator()
        self.calculator.history_file = self.temp_file.name
        self.calculator.history = []

    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)

    def test_bmi_calculation_metric(self):
        """Test BMI calculation with metric units."""
        # Test case: 70kg, 1.75m = BMI ~22.86
        bmi = self.calculator.calculate_bmi(70, 1.75, "metric")
        self.assertAlmostEqual(bmi, 22.86, places=1)

    def test_bmi_calculation_imperial(self):
        """Test BMI calculation with imperial units."""
        # Test case: 154lbs, 69in = BMI ~22.7
        bmi = self.calculator.calculate_bmi(154, 69, "imperial")
        self.assertAlmostEqual(bmi, 22.7, places=1)

    def test_bmi_categories(self):
        """Test BMI category classification."""
        # Test underweight
        self.assertEqual(self.calculator.get_bmi_category(17.0), "Underweight")

        # Test normal weight
        self.assertEqual(self.calculator.get_bmi_category(22.0), "Normal weight")

        # Test overweight
        self.assertEqual(self.calculator.get_bmi_category(27.0), "Overweight")

        # Test obese
        self.assertEqual(self.calculator.get_bmi_category(32.0), "Obese")

    def test_bmr_calculation_male_metric(self):
        """Test BMR calculation for male with metric units."""
        # Test case: 70kg, 175cm, 30 years, male
        bmr = self.calculator.calculate_bmr(70, 1.75, 30, "male", "metric")
        self.assertAlmostEqual(bmr, 1696, places=0)

    def test_bmr_calculation_female_imperial(self):
        """Test BMR calculation for female with imperial units."""
        # Test case: 130lbs, 65in, 25 years, female
        bmr = self.calculator.calculate_bmr(130, 65, 25, "female", "imperial")
        self.assertAlmostEqual(bmr, 1396, places=0)

    def test_tdee_calculation(self):
        """Test TDEE calculation with different activity levels."""
        bmr = 1500  # Base BMR

        # Test sedentary
        tdee_sedentary = self.calculator.calculate_tdee(bmr, "sedentary")
        self.assertEqual(tdee_sedentary, 1800)

        # Test moderate
        tdee_moderate = self.calculator.calculate_tdee(bmr, "moderate")
        self.assertEqual(tdee_moderate, 2325)

        # Test very active
        tdee_very_active = self.calculator.calculate_tdee(bmr, "very_active")
        self.assertEqual(tdee_very_active, 2850)

    def test_weight_goal_calculation_loss(self):
        """Test weight goal calculation for weight loss."""
        # Test case: 80kg -> 70kg, TDEE 2000
        goal_info = self.calculator.calculate_weight_goal(80, 70, 2000, "metric")

        self.assertEqual(goal_info["goal_type"], "loss")
        self.assertGreater(goal_info["weeks_needed"], 0)
        self.assertGreater(goal_info["daily_adjustment"], 0)
        self.assertLess(goal_info["target_calories"], 2000)

    def test_weight_goal_calculation_gain(self):
        """Test weight goal calculation for weight gain."""
        # Test case: 60kg -> 70kg, TDEE 2000
        goal_info = self.calculator.calculate_weight_goal(60, 70, 2000, "metric")

        self.assertEqual(goal_info["goal_type"], "gain")
        self.assertGreater(goal_info["weeks_needed"], 0)
        self.assertGreater(goal_info["daily_adjustment"], 0)  # Should be positive for gain
        self.assertGreater(goal_info["target_calories"], 2000)

    def test_history_save_and_load(self):
        """Test saving and loading calculation history."""
        # Save test data
        test_data = {
            "type": "bmi",
            "weight": 70,
            "height": 1.75,
            "bmi": 22.86,
            "category": "Normal weight"
        }

        self.calculator.save_to_history(test_data)

        # Check if data was saved
        history = self.calculator.get_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["data"], test_data)

    def test_invalid_height_bmi(self):
        """Test BMI calculation with invalid height."""
        with self.assertRaises(ValueError):
            self.calculator.calculate_bmi(70, 0, "metric")

        with self.assertRaises(ValueError):
            self.calculator.calculate_bmi(70, -1, "metric")


class TestInputValidation(unittest.TestCase):
    """Test input validation functions."""

    def test_bmi_calculator_initialization(self):
        """Test BMI calculator initialization."""
        calculator = BMICalculator()
        self.assertIsNotNone(calculator)
        self.assertEqual(calculator.history_file, "bmi_history.json")
        self.assertIsInstance(calculator.history, list)


def run_tests():
    """Run all tests."""
    print("Running BMI & Calorie Calculator Tests...")
    print("=" * 50)

    # Create test suite
    test_suite = unittest.TestSuite()

    # Add test cases
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestBMICalculator))
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestInputValidation))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    # Print summary
    print("\n" + "=" * 50)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")

    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")

    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)

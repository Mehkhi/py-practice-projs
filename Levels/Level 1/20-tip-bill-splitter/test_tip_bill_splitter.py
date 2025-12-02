#!/usr/bin/env python3
"""
Unit tests for Tip & Bill Splitter

Tests all functionality of the TipBillSplitter class including:
- Tip and tax calculations
- Even and uneven splitting
- Rounding strategies
- Receipt export and history
"""

import unittest
import json
import os
import tempfile
from unittest.mock import patch
from tip_bill_splitter import TipBillSplitter, RoundingStrategy


class TestTipBillSplitter(unittest.TestCase):
    """Test cases for TipBillSplitter class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.splitter = TipBillSplitter()
        self.temp_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        os.chdir(self.temp_dir)
        self.splitter.receipt_file = "test_receipts.json"

    def tearDown(self):
        """Clean up after each test method."""
        os.chdir(self.original_dir)
        # Clean up temp files
        for file in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file))
        os.rmdir(self.temp_dir)

    def test_initialization(self):
        """Test splitter initialization with default values."""
        self.assertEqual(self.splitter.subtotal, 0.0)
        self.assertEqual(self.splitter.tax_rate, 0.0)
        self.assertEqual(self.splitter.tip_percentage, 0.0)
        self.assertEqual(self.splitter.num_people, 1)
        self.assertEqual(self.splitter.rounding_strategy, RoundingStrategy.NORMAL)

    def test_calculate_tax(self):
        """Test tax calculation."""
        # Test with 10% tax
        tax = self.splitter.calculate_tax(100.0, 10.0)
        self.assertEqual(tax, 10.0)

        # Test with 8.5% tax
        tax = self.splitter.calculate_tax(50.0, 8.5)
        self.assertEqual(tax, 4.25)

        # Test with zero tax
        tax = self.splitter.calculate_tax(100.0, 0.0)
        self.assertEqual(tax, 0.0)

    def test_calculate_tip(self):
        """Test tip calculation."""
        # Test with 15% tip
        tip = self.splitter.calculate_tip(100.0, 15.0)
        self.assertEqual(tip, 15.0)

        # Test with 20% tip
        tip = self.splitter.calculate_tip(75.50, 20.0)
        self.assertAlmostEqual(tip, 15.1, places=5)

        # Test with zero tip
        tip = self.splitter.calculate_tip(100.0, 0.0)
        self.assertEqual(tip, 0.0)

    def test_apply_rounding_none(self):
        """Test rounding strategy NONE."""
        amount = 12.3456
        result = self.splitter.apply_rounding(amount, RoundingStrategy.NONE)
        self.assertEqual(result, 12.3456)

    def test_apply_rounding_normal(self):
        """Test rounding strategy NORMAL."""
        # Test rounding down
        result = self.splitter.apply_rounding(12.344, RoundingStrategy.NORMAL)
        self.assertEqual(result, 12.34)

        # Test rounding up
        result = self.splitter.apply_rounding(12.345, RoundingStrategy.NORMAL)
        self.assertEqual(result, 12.35)

        # Test exact value
        result = self.splitter.apply_rounding(12.34, RoundingStrategy.NORMAL)
        self.assertEqual(result, 12.34)

    def test_apply_rounding_up(self):
        """Test rounding strategy UP."""
        # Should always round up
        result = self.splitter.apply_rounding(12.341, RoundingStrategy.UP)
        self.assertEqual(result, 12.35)

        result = self.splitter.apply_rounding(12.349, RoundingStrategy.UP)
        self.assertEqual(result, 12.35)

    def test_apply_rounding_down(self):
        """Test rounding strategy DOWN."""
        # Should always round down
        result = self.splitter.apply_rounding(12.349, RoundingStrategy.DOWN)
        self.assertEqual(result, 12.34)

        result = self.splitter.apply_rounding(12.341, RoundingStrategy.DOWN)
        self.assertEqual(result, 12.34)

    def test_calculate_even_split(self):
        """Test even split calculation."""
        # Test normal case
        result = self.splitter.calculate_even_split(100.0, 4)
        self.assertEqual(result, 25.0)

        # Test with remainder
        result = self.splitter.calculate_even_split(100.0, 3)
        self.assertAlmostEqual(result, 33.333333, places=5)

        # Test with single person
        result = self.splitter.calculate_even_split(100.0, 1)
        self.assertEqual(result, 100.0)

        # Test with zero people (edge case)
        result = self.splitter.calculate_even_split(100.0, 0)
        self.assertEqual(result, 0.0)

    def test_calculate_uneven_split(self):
        """Test uneven split calculation."""
        # Test equal percentages
        percentages = [50.0, 50.0]
        amounts = self.splitter.calculate_uneven_split(100.0, percentages)
        self.assertEqual(len(amounts), 2)
        self.assertEqual(amounts[0], 50.0)
        self.assertEqual(amounts[1], 50.0)

        # Test different percentages
        percentages = [75.0, 25.0]
        amounts = self.splitter.calculate_uneven_split(100.0, percentages)
        self.assertEqual(amounts[0], 75.0)
        self.assertEqual(amounts[1], 25.0)

        # Test three people
        percentages = [33.33, 33.33, 33.34]
        amounts = self.splitter.calculate_uneven_split(100.0, percentages)
        self.assertEqual(len(amounts), 3)
        self.assertAlmostEqual(sum(amounts), 100.0, places=2)

    def test_calculate_uneven_split_normalization(self):
        """Test uneven split with percentage normalization."""
        # Test percentages that don't sum to 100
        percentages = [30.0, 20.0]  # Sum = 50
        amounts = self.splitter.calculate_uneven_split(100.0, percentages)

        # Should normalize to 60/40 split
        self.assertEqual(amounts[0], 60.0)
        self.assertEqual(amounts[1], 40.0)

    def test_calculate_uneven_split_empty(self):
        """Test uneven split with empty percentages."""
        amounts = self.splitter.calculate_uneven_split(100.0, [])
        self.assertEqual(amounts, [])

    def test_calculate_bill(self):
        """Test complete bill calculation."""
        self.splitter.subtotal = 100.0
        self.splitter.tax_rate = 10.0
        self.splitter.tip_percentage = 15.0
        self.splitter.num_people = 4

        result = self.splitter.calculate_bill()

        self.assertEqual(result["subtotal"], 100.0)
        self.assertEqual(result["tax_rate"], 10.0)
        self.assertEqual(result["tax_amount"], 10.0)
        self.assertEqual(result["tip_percentage"], 15.0)
        self.assertEqual(result["tip_amount"], 15.0)
        self.assertEqual(result["total"], 125.0)
        self.assertEqual(result["num_people"], 4)
        self.assertEqual(result["per_person"], 31.25)
        self.assertEqual(result["rounding_strategy"], "normal")

    def test_calculate_bill_with_rounding(self):
        """Test bill calculation with different rounding strategies."""
        self.splitter.subtotal = 100.0
        self.splitter.tax_rate = 8.25  # Creates fractional tax
        self.splitter.tip_percentage = 18.5  # Creates fractional tip
        self.splitter.num_people = 3

        # Test with normal rounding
        self.splitter.rounding_strategy = RoundingStrategy.NORMAL
        result = self.splitter.calculate_bill()
        self.assertAlmostEqual(result["tax_amount"], 8.25, places=2)
        self.assertAlmostEqual(result["tip_amount"], 18.5, places=2)
        self.assertAlmostEqual(result["total"], 126.75, places=2)

        # Test with up rounding
        self.splitter.rounding_strategy = RoundingStrategy.UP
        result = self.splitter.calculate_bill()
        self.assertAlmostEqual(result["tax_amount"], 8.26, places=2)  # Rounded up
        self.assertAlmostEqual(
            result["tip_amount"], 18.5, places=2
        )  # Stays the same (18.5 rounds to 18.5)
        self.assertAlmostEqual(
            result["total"], 126.77, places=2
        )  # Total with rounded components

    def test_get_valid_float_input(self):
        """Test getting valid float input."""
        # Test valid input
        with patch("builtins.input", return_value="25.50"):
            result = self.splitter.get_valid_float_input("Enter amount: ")
            self.assertEqual(result, 25.50)

        # Test invalid then valid input
        with patch("builtins.input", side_effect=["invalid", "25.50"]):
            result = self.splitter.get_valid_float_input("Enter amount: ")
            self.assertEqual(result, 25.50)

        # Test below minimum
        with patch("builtins.input", side_effect=["-5", "25.50"]):
            result = self.splitter.get_valid_float_input("Enter amount: ", 0.0)
            self.assertEqual(result, 25.50)

        # Test above maximum
        with patch("builtins.input", side_effect=["150", "25.50"]):
            result = self.splitter.get_valid_float_input("Enter amount: ", 0.0, 100.0)
            self.assertEqual(result, 25.50)

    def test_get_valid_int_input(self):
        """Test getting valid integer input."""
        # Test valid input
        with patch("builtins.input", return_value="4"):
            result = self.splitter.get_valid_int_input("Enter number: ")
            self.assertEqual(result, 4)

        # Test invalid then valid input
        with patch("builtins.input", side_effect=["invalid", "4"]):
            result = self.splitter.get_valid_int_input("Enter number: ")
            self.assertEqual(result, 4)

        # Test below minimum
        with patch("builtins.input", side_effect=["0", "4"]):
            result = self.splitter.get_valid_int_input("Enter number: ", 1)
            self.assertEqual(result, 4)

    def test_get_rounding_strategy(self):
        """Test getting rounding strategy from user."""
        # Test each option
        test_cases = [
            ("1", RoundingStrategy.NONE),
            ("2", RoundingStrategy.NORMAL),
            ("3", RoundingStrategy.UP),
            ("4", RoundingStrategy.DOWN),
        ]

        for input_val, expected_strategy in test_cases:
            with patch("builtins.input", return_value=input_val):
                result = self.splitter.get_rounding_strategy()
                self.assertEqual(result, expected_strategy)

        # Test invalid then valid input
        with patch("builtins.input", side_effect=["invalid", "2"]):
            result = self.splitter.get_rounding_strategy()
            self.assertEqual(result, RoundingStrategy.NORMAL)

    def test_save_receipt(self):
        """Test saving receipt to JSON file."""
        bill_data = {
            "subtotal": 100.0,
            "tax_amount": 10.0,
            "tip_amount": 15.0,
            "total": 125.0,
            "num_people": 4,
            "per_person": 31.25,
        }

        self.splitter.save_receipt(bill_data)

        # Verify file was created
        self.assertTrue(os.path.exists(self.splitter.receipt_file))

        # Verify file contents
        with open(self.splitter.receipt_file, "r") as file:
            receipts = json.load(file)

        self.assertEqual(len(receipts), 1)
        receipt = receipts[0]
        self.assertEqual(receipt["bill_data"]["subtotal"], 100.0)
        self.assertEqual(receipt["bill_data"]["total"], 125.0)
        self.assertIn("timestamp", receipt)
        self.assertIn("date", receipt)
        self.assertIn("time", receipt)

    def test_save_multiple_receipts(self):
        """Test saving multiple receipts."""
        bill_data1 = {"subtotal": 100.0, "total": 125.0}
        bill_data2 = {"subtotal": 50.0, "total": 60.0}

        # Save first receipt
        self.splitter.save_receipt(bill_data1)

        # Save second receipt
        self.splitter.save_receipt(bill_data2)

        # Verify both receipts are saved
        with open(self.splitter.receipt_file, "r") as file:
            receipts = json.load(file)

        self.assertEqual(len(receipts), 2)
        self.assertEqual(receipts[0]["bill_data"]["subtotal"], 100.0)
        self.assertEqual(receipts[1]["bill_data"]["subtotal"], 50.0)

    def test_save_receipt_with_uneven_split(self):
        """Test saving receipt with uneven split data."""
        bill_data = {"subtotal": 100.0, "total": 125.0}
        uneven_split_data = {"percentages": [60.0, 40.0], "amounts": [75.0, 50.0]}

        self.splitter.save_receipt(bill_data, uneven_split_data)

        with open(self.splitter.receipt_file, "r") as file:
            receipts = json.load(file)

        receipt = receipts[0]
        self.assertIn("uneven_split", receipt)
        self.assertEqual(receipt["uneven_split"]["percentages"], [60.0, 40.0])
        self.assertEqual(receipt["uneven_split"]["amounts"], [75.0, 50.0])

    def test_export_receipt_to_text(self):
        """Test exporting receipt to text file."""
        bill_data = {
            "subtotal": 100.0,
            "tax_rate": 10.0,
            "tax_amount": 10.0,
            "tip_percentage": 15.0,
            "tip_amount": 15.0,
            "total": 125.0,
            "num_people": 4,
            "per_person": 31.25,
            "rounding_strategy": "normal",
        }

        filename = "test_receipt.txt"
        self.splitter.export_receipt_to_text(bill_data, filename)

        # Verify file was created
        self.assertTrue(os.path.exists(filename))

        # Verify file contents
        with open(filename, "r") as file:
            content = file.read()

        self.assertIn("RECEIPT", content)
        self.assertIn("Subtotal:           $100.00", content)
        self.assertIn("Total:              $125.00", content)
        self.assertIn("Per Person:         $31.25", content)

    def test_export_receipt_with_uneven_split(self):
        """Test exporting receipt with uneven split to text file."""
        bill_data = {
            "subtotal": 100.0,
            "tax_rate": 10.0,
            "tax_amount": 10.0,
            "tip_percentage": 15.0,
            "tip_amount": 15.0,
            "total": 125.0,
            "num_people": 2,
            "per_person": 62.5,
            "rounding_strategy": "normal",
        }
        uneven_split_data = {"percentages": [60.0, 40.0], "amounts": [75.0, 50.0]}

        filename = "test_uneven_receipt.txt"
        self.splitter.export_receipt_to_text(bill_data, filename, uneven_split_data)

        with open(filename, "r") as file:
            content = file.read()

        self.assertIn("UNEVEN SPLIT BREAKDOWN", content)
        self.assertIn("Person 1:", content)
        self.assertIn("Percentage: 60.0%", content)
        self.assertIn("Amount: $75.00", content)

    def test_view_receipt_history_empty(self):
        """Test viewing receipt history when no file exists."""
        with patch("builtins.print") as mock_print:
            self.splitter.view_receipt_history()
            mock_print.assert_called()
            calls = [str(call) for call in mock_print.call_args_list]
            output = " ".join(calls)
            self.assertIn("No receipt history found", output)

    def test_view_receipt_history_with_data(self):
        """Test viewing receipt history with saved receipts."""
        # Create test receipts
        bill_data1 = {
            "subtotal": 100.0,
            "total": 125.0,
            "num_people": 4,
            "per_person": 31.25,
        }
        bill_data2 = {
            "subtotal": 50.0,
            "total": 60.0,
            "num_people": 2,
            "per_person": 30.0,
        }

        self.splitter.save_receipt(bill_data1)
        self.splitter.save_receipt(bill_data2)

        with patch("builtins.print") as mock_print:
            self.splitter.view_receipt_history()
            mock_print.assert_called()
            calls = [str(call) for call in mock_print.call_args_list]
            output = " ".join(calls)
            self.assertIn("RECEIPT HISTORY", output)
            self.assertIn("Total: $125.00", output)
            self.assertIn("Total: $60.00", output)

    def test_get_menu_choice(self):
        """Test getting menu choice from user."""
        # Test valid choices
        for choice in ["1", "2", "3", "4"]:
            with patch("builtins.input", return_value=choice):
                result = self.splitter.get_menu_choice()
                self.assertEqual(result, choice)

        # Test invalid then valid input
        with patch("builtins.input", side_effect=["invalid", "2"]):
            result = self.splitter.get_menu_choice()
            self.assertEqual(result, "2")


class TestTipBillSplitterIntegration(unittest.TestCase):
    """Integration tests for TipBillSplitter class."""

    def setUp(self):
        """Set up test fixtures."""
        self.splitter = TipBillSplitter()
        self.temp_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        os.chdir(self.temp_dir)
        self.splitter.receipt_file = "test_receipts.json"

    def tearDown(self):
        """Clean up after each test method."""
        os.chdir(self.original_dir)
        # Clean up temp files
        for file in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file))
        os.rmdir(self.temp_dir)

    def test_complete_even_split_workflow(self):
        """Test complete even split workflow."""
        # Set up test data
        self.splitter.subtotal = 100.0
        self.splitter.tax_rate = 10.0
        self.splitter.tip_percentage = 15.0
        self.splitter.num_people = 4
        self.splitter.rounding_strategy = RoundingStrategy.NORMAL

        # Calculate bill
        bill_data = self.splitter.calculate_bill()

        # Verify calculations
        self.assertEqual(bill_data["subtotal"], 100.0)
        self.assertEqual(bill_data["tax_amount"], 10.0)
        self.assertEqual(bill_data["tip_amount"], 15.0)
        self.assertEqual(bill_data["total"], 125.0)
        self.assertEqual(bill_data["per_person"], 31.25)

        # Save receipt
        self.splitter.save_receipt(bill_data)

        # Verify receipt was saved
        self.assertTrue(os.path.exists(self.splitter.receipt_file))

        with open(self.splitter.receipt_file, "r") as file:
            receipts = json.load(file)

        self.assertEqual(len(receipts), 1)
        self.assertEqual(receipts[0]["bill_data"]["total"], 125.0)

    def test_complete_uneven_split_workflow(self):
        """Test complete uneven split workflow."""
        # Set up test data
        self.splitter.subtotal = 100.0
        self.splitter.tax_rate = 10.0
        self.splitter.tip_percentage = 15.0
        self.splitter.num_people = 3
        self.splitter.rounding_strategy = RoundingStrategy.NORMAL

        # Calculate bill
        bill_data = self.splitter.calculate_bill()

        # Calculate uneven split
        percentages = [50.0, 30.0, 20.0]
        amounts = self.splitter.calculate_uneven_split(bill_data["total"], percentages)

        # Verify split
        self.assertEqual(len(amounts), 3)
        self.assertEqual(amounts[0], 62.5)  # 50% of 125
        self.assertEqual(amounts[1], 37.5)  # 30% of 125
        self.assertEqual(amounts[2], 25.0)  # 20% of 125
        self.assertAlmostEqual(sum(amounts), bill_data["total"], places=2)

        # Save receipt with uneven split
        uneven_split_data = {"percentages": percentages, "amounts": amounts}
        self.splitter.save_receipt(bill_data, uneven_split_data)

        # Verify receipt was saved
        with open(self.splitter.receipt_file, "r") as file:
            receipts = json.load(file)

        receipt = receipts[0]
        self.assertIn("uneven_split", receipt)
        self.assertEqual(receipt["uneven_split"]["percentages"], percentages)
        self.assertEqual(receipt["uneven_split"]["amounts"], amounts)

    def test_rounding_strategies_impact(self):
        """Test impact of different rounding strategies."""
        # Set up test data that creates rounding issues
        self.splitter.subtotal = 100.0
        self.splitter.tax_rate = 8.333  # Creates repeating decimal
        self.splitter.tip_percentage = 12.777  # Creates repeating decimal
        self.splitter.num_people = 3

        # Test each rounding strategy
        strategies = [
            RoundingStrategy.NONE,
            RoundingStrategy.NORMAL,
            RoundingStrategy.UP,
            RoundingStrategy.DOWN,
        ]
        results = []

        for strategy in strategies:
            self.splitter.rounding_strategy = strategy
            result = self.splitter.calculate_bill()
            results.append(result)

        # Check that rounding strategies are applied correctly
        # The tax_amount and tip_amount should be different due to rounding
        self.assertNotEqual(
            results[0]["tax_amount"], results[2]["tax_amount"]
        )  # NONE vs UP
        self.assertNotEqual(
            results[1]["tax_amount"], results[2]["tax_amount"]
        )  # NORMAL vs UP
        self.assertNotEqual(
            results[2]["tax_amount"], results[3]["tax_amount"]
        )  # UP vs DOWN

    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        # Test zero values
        self.splitter.subtotal = 0.0
        self.splitter.tax_rate = 0.0
        self.splitter.tip_percentage = 0.0
        self.splitter.num_people = 1

        result = self.splitter.calculate_bill()
        self.assertEqual(result["total"], 0.0)
        self.assertEqual(result["per_person"], 0.0)

        # Test very large values
        self.splitter.subtotal = 999999.99
        self.splitter.tax_rate = 100.0
        self.splitter.tip_percentage = 100.0
        self.splitter.num_people = 100

        result = self.splitter.calculate_bill()
        self.assertAlmostEqual(
            result["total"], 2999999.97, places=2
        )  # subtotal + tax + tip
        self.assertAlmostEqual(result["per_person"], 30000.0, places=2)

    def test_receipt_history_persistence(self):
        """Test that receipt history persists across multiple sessions."""
        # Create multiple receipts
        for i in range(5):
            self.splitter.subtotal = 100.0 + i * 10
            self.splitter.tax_rate = 10.0
            self.splitter.tip_percentage = 15.0
            self.splitter.num_people = 2

            bill_data = self.splitter.calculate_bill()
            self.splitter.save_receipt(bill_data)

        # Verify all receipts are saved
        with open(self.splitter.receipt_file, "r") as file:
            receipts = json.load(file)

        self.assertEqual(len(receipts), 5)

        # Verify receipt data
        for i, receipt in enumerate(receipts):
            expected_total = (100.0 + i * 10) * 1.25  # subtotal + tax + tip
            self.assertAlmostEqual(
                receipt["bill_data"]["total"], expected_total, places=2
            )


if __name__ == "__main__":
    unittest.main()

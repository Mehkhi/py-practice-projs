#!/usr/bin/env python3
"""
Tip & Bill Splitter

A command-line application for calculating tips, adding tax, and splitting bills
among multiple people with support for uneven splits and receipt export.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum


class RoundingStrategy(Enum):
    """Enumeration of different rounding strategies."""

    NONE = "none"
    NORMAL = "normal"
    UP = "up"
    DOWN = "down"


class TipBillSplitter:
    """Main class for tip and bill splitting calculations."""

    def __init__(self):
        self.subtotal = 0.0
        self.tax_rate = 0.0
        self.tip_percentage = 0.0
        self.num_people = 1
        self.rounding_strategy = RoundingStrategy.NORMAL
        self.receipt_file = "receipts.json"
        self.receipt_history = []

    def get_valid_float_input(
        self, prompt: str, min_value: float = 0.0, max_value: float = None
    ) -> float:
        """
        Get valid float input from user with validation.

        Args:
            prompt: Input prompt message
            min_value: Minimum allowed value
            max_value: Maximum allowed value

        Returns:
            Validated float value
        """
        while True:
            try:
                value = float(input(prompt).strip())

                if value < min_value:
                    print(f"Value must be at least {min_value}")
                    continue

                if max_value is not None and value > max_value:
                    print(f"Value must be at most {max_value}")
                    continue

                return value

            except ValueError:
                print("Please enter a valid number.")

    def get_valid_int_input(
        self, prompt: str, min_value: int = 1, max_value: int = None
    ) -> int:
        """
        Get valid integer input from user with validation.

        Args:
            prompt: Input prompt message
            min_value: Minimum allowed value
            max_value: Maximum allowed value

        Returns:
            Validated integer value
        """
        while True:
            try:
                value = int(input(prompt).strip())

                if value < min_value:
                    print(f"Value must be at least {min_value}")
                    continue

                if max_value is not None and value > max_value:
                    print(f"Value must be at most {max_value}")
                    continue

                return value

            except ValueError:
                print("Please enter a valid integer.")

    def calculate_tax(self, subtotal: float, tax_rate: float) -> float:
        """
        Calculate tax amount.

        Args:
            subtotal: Subtotal amount
            tax_rate: Tax rate as percentage

        Returns:
            Tax amount
        """
        return subtotal * (tax_rate / 100)

    def calculate_tip(self, subtotal: float, tip_percentage: float) -> float:
        """
        Calculate tip amount.

        Args:
            subtotal: Subtotal amount
            tip_percentage: Tip percentage

        Returns:
            Tip amount
        """
        return subtotal * (tip_percentage / 100)

    def apply_rounding(self, amount: float, strategy: RoundingStrategy) -> float:
        """
        Apply rounding strategy to amount.

        Args:
            amount: Amount to round
            strategy: Rounding strategy to apply

        Returns:
            Rounded amount
        """
        if strategy == RoundingStrategy.NONE:
            return amount
        elif strategy == RoundingStrategy.NORMAL:
            return round(amount, 2)
        elif strategy == RoundingStrategy.UP:
            return round(amount + 0.005, 2)  # Always round up
        elif strategy == RoundingStrategy.DOWN:
            return round(amount - 0.005, 2)  # Always round down
        else:
            return round(amount, 2)

    def calculate_even_split(self, total: float, num_people: int) -> float:
        """
        Calculate even split among people.

        Args:
            total: Total amount to split
            num_people: Number of people

        Returns:
            Amount per person
        """
        if num_people <= 0:
            return 0.0
        return total / num_people

    def calculate_uneven_split(
        self, total: float, percentages: List[float]
    ) -> List[float]:
        """
        Calculate uneven split based on percentages.

        Args:
            total: Total amount to split
            percentages: List of percentages for each person

        Returns:
            List of amounts for each person
        """
        if not percentages:
            return []

        # Normalize percentages to ensure they sum to 100
        total_percentage = sum(percentages)
        if total_percentage == 0:
            return [0.0] * len(percentages)

        normalized_percentages = [p / total_percentage * 100 for p in percentages]

        # Calculate amounts
        amounts = []
        for percentage in normalized_percentages:
            amount = total * (percentage / 100)
            amounts.append(self.apply_rounding(amount, self.rounding_strategy))

        # Adjust for rounding errors
        calculated_total = sum(amounts)
        difference = total - calculated_total

        if abs(difference) > 0.01:  # If there's a significant difference
            # Add the difference to the first person's amount
            amounts[0] += difference
            amounts[0] = self.apply_rounding(amounts[0], self.rounding_strategy)

        return amounts

    def calculate_bill(self) -> Dict:
        """
        Calculate complete bill breakdown.

        Returns:
            Dictionary with all calculation results
        """
        tax_amount = self.calculate_tax(self.subtotal, self.tax_rate)
        tip_amount = self.calculate_tip(self.subtotal, self.tip_percentage)

        # Apply rounding to individual components
        tax_amount = self.apply_rounding(tax_amount, self.rounding_strategy)
        tip_amount = self.apply_rounding(tip_amount, self.rounding_strategy)

        total = self.subtotal + tax_amount + tip_amount
        total = self.apply_rounding(total, self.rounding_strategy)

        per_person = self.calculate_even_split(total, self.num_people)
        per_person = self.apply_rounding(per_person, self.rounding_strategy)

        return {
            "subtotal": self.subtotal,
            "tax_rate": self.tax_rate,
            "tax_amount": tax_amount,
            "tip_percentage": self.tip_percentage,
            "tip_amount": tip_amount,
            "total": total,
            "num_people": self.num_people,
            "per_person": per_person,
            "rounding_strategy": self.rounding_strategy.value,
        }

    def display_bill_breakdown(self, bill_data: Dict):
        """Display formatted bill breakdown."""
        print("\n" + "=" * 60)
        print("[MONEY BAG] BILL BREAKDOWN")
        print("=" * 60)

        print(f"\n[CLIPBOARD] SUBTOTAL:           ${bill_data['subtotal']:.2f}")
        print(f"[CHART UP] TAX RATE:           {bill_data['tax_rate']:.1f}%")
        print(f"[DOLLAR BILL] TAX AMOUNT:         ${bill_data['tax_amount']:.2f}")
        print(f"[TARGET] TIP PERCENTAGE:     {bill_data['tip_percentage']:.1f}%")
        print(f"[GIFT HEART] TIP AMOUNT:         ${bill_data['tip_amount']:.2f}")
        print("-" * 40)
        print(f"[MONEY BAG] TOTAL:              ${bill_data['total']:.2f}")
        print(f"[PROFILES] SPLIT BETWEEN:      {bill_data['num_people']} people")
        print(f"[RECEIPT] PER PERSON:         ${bill_data['per_person']:.2f}")
        print(f"[REFRESH] ROUNDING:           {bill_data['rounding_strategy'].upper()}")

        print("\n" + "=" * 60)

    def get_uneven_split_percentages(self, num_people: int) -> List[float]:
        """
        Get percentages for uneven split from user.

        Args:
            num_people: Number of people

        Returns:
            List of percentages
        """
        print(f"\n[BAR CHART] Enter percentage split for {num_people} people:")
        percentages = []

        for i in range(num_people):
            while True:
                try:
                    percentage = float(input(f"Person {i+1} percentage: ").strip())
                    if percentage < 0:
                        print("Percentage cannot be negative.")
                        continue
                    percentages.append(percentage)
                    break
                except ValueError:
                    print("Please enter a valid number.")

        # Show total and confirm
        total_percentage = sum(percentages)
        print(f"\nTotal percentage entered: {total_percentage:.1f}%")

        if abs(total_percentage - 100) > 0.1:
            print("Note: Percentages don't sum to 100%. They will be normalized.")

        confirm = input("Continue with these percentages? (y/n): ").strip().lower()
        if confirm not in ["y", "yes"]:
            return []

        return percentages

    def display_uneven_split(self, amounts: List[float], percentages: List[float]):
        """Display uneven split breakdown."""
        print("\n" + "=" * 60)
        print("[BAR CHART] UNEVEN SPLIT BREAKDOWN")
        print("=" * 60)

        total = sum(amounts)

        for i, (amount, percentage) in enumerate(zip(amounts, percentages)):
            print(f"\n[PROFILE] Person {i+1}:")
            print(f"   Percentage: {percentage:.1f}%")
            print(f"   Amount: ${amount:.2f}")

        print(f"\n[MONEY BAG] Total: ${total:.2f}")
        print("=" * 60)

    def save_receipt(self, bill_data: Dict, uneven_split_data: Optional[Dict] = None):
        """
        Save receipt data to JSON file.

        Args:
            bill_data: Bill calculation data
            uneven_split_data: Optional uneven split data
        """
        receipt = {
            "timestamp": datetime.now().isoformat(),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "time": datetime.now().strftime("%H:%M:%S"),
            "bill_data": bill_data,
        }

        if uneven_split_data:
            receipt["uneven_split"] = uneven_split_data

        try:
            # Load existing receipts
            receipts = []
            if os.path.exists(self.receipt_file):
                with open(self.receipt_file, "r", encoding="utf-8") as file:
                    receipts = json.load(file)

            # Add new receipt
            receipts.append(receipt)

            # Save back to file
            with open(self.receipt_file, "w", encoding="utf-8") as file:
                json.dump(receipts, file, indent=2, ensure_ascii=False)

            print(f"\n[PAGE] Receipt saved to '{self.receipt_file}'")

        except Exception as e:
            print(f"\n[X] Error saving receipt: {e}")

    def export_receipt_to_text(
        self,
        bill_data: Dict,
        filename: Optional[str] = None,
        uneven_split_data: Optional[Dict] = None,
    ):
        """
        Export receipt to text file.

        Args:
            bill_data: Bill calculation data
            filename: Optional custom filename
            uneven_split_data: Optional uneven split data
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"receipt_{timestamp}.txt"

        try:
            with open(filename, "w", encoding="utf-8") as file:
                file.write("=" * 60 + "\n")
                file.write("[MONEY BAG] RECEIPT\n")
                file.write("=" * 60 + "\n")
                file.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                file.write(
                    f"Rounding Strategy: {bill_data['rounding_strategy'].upper()}\n\n"
                )

                file.write("BILL BREAKDOWN:\n")
                file.write("-" * 40 + "\n")
                file.write(f"Subtotal:           ${bill_data['subtotal']:.2f}\n")
                file.write(f"Tax Rate:           {bill_data['tax_rate']:.1f}%\n")
                file.write(f"Tax Amount:         ${bill_data['tax_amount']:.2f}\n")
                file.write(f"Tip Percentage:     {bill_data['tip_percentage']:.1f}%\n")
                file.write(f"Tip Amount:         ${bill_data['tip_amount']:.2f}\n")
                file.write("-" * 40 + "\n")
                file.write(f"Total:              ${bill_data['total']:.2f}\n")
                file.write(f"Split Between:      {bill_data['num_people']} people\n")
                file.write(f"Per Person:         ${bill_data['per_person']:.2f}\n")

                if uneven_split_data:
                    file.write("\n" + "=" * 60 + "\n")
                    file.write("[BAR CHART] UNEVEN SPLIT BREAKDOWN\n")
                    file.write("=" * 60 + "\n")

                    for i, (amount, percentage) in enumerate(
                        zip(
                            uneven_split_data["amounts"],
                            uneven_split_data["percentages"],
                        )
                    ):
                        file.write(f"\nPerson {i+1}:\n")
                        file.write(f"  Percentage: {percentage:.1f}%\n")
                        file.write(f"  Amount: ${amount:.2f}\n")

                file.write("\n" + "=" * 60 + "\n")
                file.write("Thank you for using Tip & Bill Splitter!\n")
                file.write("=" * 60 + "\n")

            print(f"\n[PAGE] Receipt exported to '{filename}'")

        except Exception as e:
            print(f"\n[X] Error exporting receipt: {e}")

    def get_rounding_strategy(self) -> RoundingStrategy:
        """Get rounding strategy choice from user."""
        print("\n[REFRESH] ROUNDING STRATEGIES:")
        print("1. None (no rounding)")
        print("2. Normal (standard rounding)")
        print("3. Always round up")
        print("4. Always round down")

        while True:
            choice = input("Select rounding strategy (1-4): ").strip()

            if choice == "1":
                return RoundingStrategy.NONE
            elif choice == "2":
                return RoundingStrategy.NORMAL
            elif choice == "3":
                return RoundingStrategy.UP
            elif choice == "4":
                return RoundingStrategy.DOWN
            else:
                print("Please enter a number between 1 and 4.")

    def run_even_split_calculation(self):
        """Run even split calculation."""
        print("\n[ABACUS] EVEN SPLIT CALCULATION")
        print("=" * 40)

        # Get inputs
        self.subtotal = self.get_valid_float_input("Enter subtotal amount: $", 0.01)
        self.tax_rate = self.get_valid_float_input("Enter tax rate (%): ", 0.0, 100.0)
        self.tip_percentage = self.get_valid_float_input(
            "Enter tip percentage (%): ", 0.0, 100.0
        )
        self.num_people = self.get_valid_int_input("Enter number of people: ", 1)

        # Get rounding strategy
        self.rounding_strategy = self.get_rounding_strategy()

        # Calculate and display
        bill_data = self.calculate_bill()
        self.display_bill_breakdown(bill_data)

        # Save options
        save_choice = input("\nSave receipt? (y/n): ").strip().lower()
        if save_choice in ["y", "yes"]:
            self.save_receipt(bill_data)

        export_choice = input("Export receipt to text file? (y/n): ").strip().lower()
        if export_choice in ["y", "yes"]:
            filename = input("Enter filename (press Enter for default): ").strip()
            if not filename:
                filename = None
            self.export_receipt_to_text(bill_data, filename)

    def run_uneven_split_calculation(self):
        """Run uneven split calculation."""
        print("\n[BAR CHART] UNEVEN SPLIT CALCULATION")
        print("=" * 40)

        # Get inputs
        self.subtotal = self.get_valid_float_input("Enter subtotal amount: $", 0.01)
        self.tax_rate = self.get_valid_float_input("Enter tax rate (%): ", 0.0, 100.0)
        self.tip_percentage = self.get_valid_float_input(
            "Enter tip percentage (%): ", 0.0, 100.0
        )
        self.num_people = self.get_valid_int_input("Enter number of people: ", 1)

        # Get percentages
        percentages = self.get_uneven_split_percentages(self.num_people)
        if not percentages:
            print("Uneven split cancelled.")
            return

        # Get rounding strategy
        self.rounding_strategy = self.get_rounding_strategy()

        # Calculate bill
        bill_data = self.calculate_bill()

        # Calculate uneven split
        amounts = self.calculate_uneven_split(bill_data["total"], percentages)

        # Display results
        self.display_bill_breakdown(bill_data)
        self.display_uneven_split(amounts, percentages)

        # Prepare uneven split data for saving
        uneven_split_data = {"percentages": percentages, "amounts": amounts}

        # Save options
        save_choice = input("\nSave receipt? (y/n): ").strip().lower()
        if save_choice in ["y", "yes"]:
            self.save_receipt(bill_data, uneven_split_data)

        export_choice = input("Export receipt to text file? (y/n): ").strip().lower()
        if export_choice in ["y", "yes"]:
            filename = input("Enter filename (press Enter for default): ").strip()
            if not filename:
                filename = None
            self.export_receipt_to_text(bill_data, filename, uneven_split_data)

    def view_receipt_history(self):
        """View saved receipt history."""
        try:
            if not os.path.exists(self.receipt_file):
                print("\n[PAGE] No receipt history found.")
                return

            with open(self.receipt_file, "r", encoding="utf-8") as file:
                receipts = json.load(file)

            if not receipts:
                print("\n[PAGE] No receipts in history.")
                return

            print(f"\n[PAGE] RECEIPT HISTORY ({len(receipts)} receipts)")
            print("=" * 60)

            for i, receipt in enumerate(receipts[-10:], 1):  # Show last 10
                bill_data = receipt["bill_data"]
                print(f"\n[RECEIPT] Receipt #{len(receipts) - 10 + i}:")
                print(f"   Date: {receipt['date']} {receipt['time']}")
                print(f"   Total: ${bill_data['total']:.2f}")
                print(f"   People: {bill_data['num_people']}")
                print(f"   Per Person: ${bill_data['per_person']:.2f}")

                if "uneven_split" in receipt:
                    print("   Split Type: Uneven")
                else:
                    print("   Split Type: Even")

        except Exception as e:
            print(f"\n[X] Error loading receipt history: {e}")

    def get_menu_choice(self) -> str:
        """Get user's menu choice."""
        print("\n[MONEY BAG] TIP & BILL SPLITTER MENU")
        print("=" * 35)
        print("1. Even split calculation")
        print("2. Uneven split calculation")
        print("3. View receipt history")
        print("4. Exit")

        while True:
            choice = input("\nEnter your choice (1-4): ").strip()
            if choice in ["1", "2", "3", "4"]:
                return choice
            print("Please enter a number between 1 and 4.")


def display_welcome():
    """Display welcome message and instructions."""
    print("\n" + "=" * 60)
    print("[MONEY BAG] TIP & BILL SPLITTER [MONEY BAG]")
    print("=" * 60)
    print("Welcome to the Tip & Bill Splitter!")
    print("Calculate tips, add tax, and split bills easily.")
    print("\nFeatures:")
    print("• Even and uneven bill splitting")
    print("• Multiple rounding strategies")
    print("• Receipt export and history")
    print("• Tax and tip calculations")
    print("=" * 60)


def main():
    """Main program loop."""
    splitter = TipBillSplitter()

    display_welcome()

    while True:
        choice = splitter.get_menu_choice()

        if choice == "1":
            # Even split calculation
            splitter.run_even_split_calculation()

        elif choice == "2":
            # Uneven split calculation
            splitter.run_uneven_split_calculation()

        elif choice == "3":
            # View receipt history
            splitter.view_receipt_history()

        elif choice == "4":
            # Exit
            print("\nThanks for using Tip & Bill Splitter!")
            print("[MONEY BAG] Have a great day! [MONEY BAG]")
            break


if __name__ == "__main__":
    main()

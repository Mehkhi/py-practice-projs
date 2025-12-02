#!/usr/bin/env python3
"""
Multiplication Table Generator

A command-line program that generates formatted multiplication tables
with customizable ranges, alignment, and export capabilities.
"""

import csv
from typing import List, Tuple, Optional


class MultiplicationTableGenerator:
    """Main class for generating and formatting multiplication tables."""

    def __init__(self):
        self.table: List[List[int]] = []
        self.start_range: int = 1
        self.end_range: int = 10
        self.use_color: bool = False

    def validate_input(
        self, value: str, input_type: str = "positive_int"
    ) -> Tuple[bool, Optional[int], str]:
        """
        Validate user input for table parameters.

        Args:
            value: String input to validate
            input_type: Type of validation ("positive_int", "range")

        Returns:
            Tuple of (is_valid, parsed_value, error_message)
        """
        if not value or not value.strip():
            return False, None, "Input cannot be empty"

        value = value.strip()

        try:
            num = int(value)

            if input_type == "positive_int":
                if num <= 0:
                    return False, None, "Please enter a positive integer greater than 0"
                if num > 100:
                    return (
                        False,
                        None,
                        "Please enter a number less than or equal to 100",
                    )
                return True, num, ""

            elif input_type == "range":
                if num < 1:
                    return False, None, "Range start must be at least 1"
                if num > 1000:
                    return False, None, "Range end must be less than or equal to 1000"
                return True, num, ""

            return False, None, "Invalid input type"

        except ValueError:
            return False, None, "Please enter a valid integer"

    def generate_table(self, start: int = 1, end: int = 10) -> List[List[int]]:
        """
        Generate multiplication table for given range.

        Args:
            start: Starting number for the table
            end: Ending number for the table

        Returns:
            2D list representing the multiplication table
        """
        if start > end:
            start, end = end, start  # Swap if start > end

        self.start_range = start
        self.end_range = end

        # Create table with header row and column
        size = end - start + 1
        self.table = [[0] * (size + 1) for _ in range(size + 1)]

        # Fill header row (top row)
        for i in range(size):
            self.table[0][i + 1] = start + i

        # Fill header column (leftmost column)
        for i in range(size):
            self.table[i + 1][0] = start + i

        # Fill multiplication results
        for i in range(size):
            for j in range(size):
                row_num = start + i
                col_num = start + j
                self.table[i + 1][j + 1] = row_num * col_num

        return self.table

    def get_column_width(self) -> int:
        """
        Calculate the required column width for proper alignment.

        Returns:
            Width needed for the widest column
        """
        if not self.table:
            return 4

        max_value = max(max(row) for row in self.table)
        return max(len(str(max_value)), 4)

    def format_table(self, use_color: bool = False) -> str:
        """
        Format the multiplication table for display.

        Args:
            use_color: Whether to use color coding

        Returns:
            Formatted table string
        """
        if not self.table:
            return "No table generated. Please generate a table first."

        col_width = self.get_column_width()
        lines = []

        # Add title
        lines.append(f"Multiplication Table ({self.start_range} to {self.end_range})")
        lines.append(
            "=" * (col_width * len(self.table[0]) + len(self.table[0]) * 3 + 1)
        )

        # Format each row
        for i, row in enumerate(self.table):
            formatted_row = []

            for j, value in enumerate(row):
                if i == 0 and j == 0:
                    # Top-left corner (empty)
                    formatted_cell = " " * col_width
                elif i == 0 or j == 0:
                    # Header row or column
                    if use_color:
                        formatted_cell = f"\033[94m{value:^{col_width}}\033[0m"  # Blue
                    else:
                        formatted_cell = f"{value:^{col_width}}"
                else:
                    # Multiplication results
                    if use_color:
                        # Color code based on value
                        if value % 2 == 0:
                            color_code = "\033[92m"  # Green for even
                        else:
                            color_code = "\033[91m"  # Red for odd
                        formatted_cell = f"{color_code}{value:^{col_width}}\033[0m"
                    else:
                        formatted_cell = f"{value:^{col_width}}"

                formatted_row.append(formatted_cell)

            lines.append(" | ".join(formatted_row))

            # Add separator after header row
            if i == 0:
                separator = "-+-".join(["-" * col_width] * len(row))
                lines.append(separator)

        return "\n".join(lines)

    def export_to_csv(self, filename: str = "multiplication_table.csv") -> bool:
        """
        Export the multiplication table to a CSV file.

        Args:
            filename: Name of the CSV file

        Returns:
            True if successful, False otherwise
        """
        if not self.table:
            return False

        try:
            with open(filename, "w", newline="") as csvfile:
                writer = csv.writer(csvfile)

                # Write header row
                header = [""] + [
                    str(self.start_range + i) for i in range(len(self.table) - 1)
                ]
                writer.writerow(header)

                # Write data rows
                for i in range(1, len(self.table)):
                    row = [self.table[i][0]] + self.table[i][1:]
                    writer.writerow(row)

            return True
        except Exception:
            return False

    def get_table_info(self) -> dict:
        """
        Get information about the current table.

        Returns:
            Dictionary with table information
        """
        if not self.table:
            return {"has_table": False}

        size = len(self.table) - 1
        return {
            "has_table": True,
            "start_range": self.start_range,
            "end_range": self.end_range,
            "size": size,
            "total_cells": size * size,
            "max_value": max(max(row) for row in self.table[1:]),
            "column_width": self.get_column_width(),
        }


def display_menu():
    """Display the main menu options."""
    print("\n" + "=" * 60)
    print("[NUMBERS] MULTIPLICATION TABLE GENERATOR [NUMBERS]")
    print("=" * 60)
    print("1. Generate standard table (1-10)")
    print("2. Generate custom range table")
    print("3. Generate N×N table")
    print("4. Display current table")
    print("5. Export table to CSV")
    print("6. Toggle color output")
    print("7. Exit")
    print("=" * 60)


def get_user_choice() -> str:
    """Get and validate user menu choice."""
    while True:
        choice = input("\nEnter your choice (1-7): ").strip()
        if choice in ["1", "2", "3", "4", "5", "6", "7"]:
            return choice
        print("Invalid choice. Please enter 1, 2, 3, 4, 5, 6, or 7.")


def handle_standard_table(generator: MultiplicationTableGenerator):
    """Handle generating a standard 1-10 table."""
    generator.generate_table(1, 10)
    print("\n[OK] Standard multiplication table (1-10) generated!")
    print(generator.format_table(generator.use_color))


def handle_custom_range(generator: MultiplicationTableGenerator):
    """Handle generating a custom range table."""
    print("\nEnter custom range for multiplication table")

    while True:
        start_input = input("Start number: ").strip()
        is_valid, start_value, error = generator.validate_input(start_input, "range")
        if is_valid:
            break
        print(f"[X] {error}")

    while True:
        end_input = input("End number: ").strip()
        is_valid, end_value, error = generator.validate_input(end_input, "range")
        if is_valid:
            break
        print(f"[X] {error}")

    generator.generate_table(start_value, end_value)
    print(f"\n[OK] Custom multiplication table ({start_value}-{end_value}) generated!")
    print(generator.format_table(generator.use_color))


def handle_nxn_table(generator: MultiplicationTableGenerator):
    """Handle generating an N×N table."""
    print("\nEnter size for N×N multiplication table")

    while True:
        n_input = input("Enter N (table size): ").strip()
        is_valid, n_value, error = generator.validate_input(n_input, "positive_int")
        if is_valid:
            break
        print(f"[X] {error}")

    generator.generate_table(1, n_value)
    print(f"\n[OK] {n_value}×{n_value} multiplication table generated!")
    print(generator.format_table(generator.use_color))


def handle_display_table(generator: MultiplicationTableGenerator):
    """Handle displaying the current table."""
    info = generator.get_table_info()

    if not info["has_table"]:
        print("\n[X] No table generated yet. Please generate a table first.")
        return

    print("\n[BAR CHART] Current Table Information:")
    print(f"   Range: {info['start_range']} to {info['end_range']}")
    print(f"   Size: {info['size']}×{info['size']}")
    print(f"   Total cells: {info['total_cells']}")
    print(f"   Maximum value: {info['max_value']}")

    print("\n" + generator.format_table(generator.use_color))


def handle_export_csv(generator: MultiplicationTableGenerator):
    """Handle exporting table to CSV."""
    info = generator.get_table_info()

    if not info["has_table"]:
        print("\n[X] No table generated yet. Please generate a table first.")
        return

    filename = input("Enter filename (or press Enter for default): ").strip()
    if not filename:
        filename = (
            f"multiplication_table_{info['start_range']}_to_{info['end_range']}.csv"
        )

    if not filename.endswith(".csv"):
        filename += ".csv"

    if generator.export_to_csv(filename):
        print(f"\n[OK] Table exported to '{filename}'")
    else:
        print(f"\n[X] Failed to export table to '{filename}'")


def handle_toggle_color(generator: MultiplicationTableGenerator):
    """Handle toggling color output."""
    generator.use_color = not generator.use_color
    status = "enabled" if generator.use_color else "disabled"
    print(f"\n[PALETTE] Color output {status}")


def main():
    """Main program loop."""
    generator = MultiplicationTableGenerator()

    print("Welcome to the Multiplication Table Generator!")
    print("Create beautiful, formatted multiplication tables with ease.")

    while True:
        display_menu()
        choice = get_user_choice()

        if choice == "1":
            handle_standard_table(generator)
        elif choice == "2":
            handle_custom_range(generator)
        elif choice == "3":
            handle_nxn_table(generator)
        elif choice == "4":
            handle_display_table(generator)
        elif choice == "5":
            handle_export_csv(generator)
        elif choice == "6":
            handle_toggle_color(generator)
        elif choice == "7":
            print("\nThanks for using the Multiplication Table Generator!")
            print("[NUMBERS] Happy multiplying! [NUMBERS]")
            break

        # Pause before showing menu again
        if choice != "7":
            input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()

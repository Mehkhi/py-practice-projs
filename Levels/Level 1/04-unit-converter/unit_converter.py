#!/usr/bin/env python3
"""
Unit Converter - A command-line tool for converting between different units
Supports length, weight, and volume conversions with bidirectional conversion logic.
"""

import json
import os
from typing import Dict, List, Optional


class UnitConverter:
    """A unit converter that supports multiple categories of measurements."""

    def __init__(self):
        """Initialize the converter with conversion factors."""
        self.conversion_factors = {
            'length': {
                'mm': 1,           # millimeter (base unit)
                'cm': 10,          # centimeter
                'm': 1000,         # meter
                'km': 1000000,     # kilometer
                'in': 25.4,        # inch
                'ft': 304.8,       # foot
                'yd': 914.4,       # yard
                'mi': 1609344      # mile
            },
            'weight': {
                'mg': 1,           # milligram (base unit)
                'g': 1000,         # gram
                'kg': 1000000,     # kilogram
                'oz': 28349.5,     # ounce
                'lb': 453592,      # pound
                'ton': 1000000000  # metric ton
            },
            'volume': {
                'ml': 1,           # milliliter (base unit)
                'l': 1000,         # liter
                'fl_oz': 29.5735,  # fluid ounce
                'cup': 236.588,    # cup
                'pt': 473.176,      # pint
                'qt': 946.353,     # quart
                'gal': 3785.41     # gallon
            }
        }

        self.history_file = 'conversion_history.json'
        self.history = self._load_history()

    def _load_history(self) -> List[Dict]:
        """Load conversion history from file."""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return []
        return []

    def _save_history(self) -> None:
        """Save conversion history to file."""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.history, f, indent=2)
        except IOError:
            pass  # Silently fail if can't save history

    def get_categories(self) -> List[str]:
        """Return list of available conversion categories."""
        return list(self.conversion_factors.keys())

    def get_units(self, category: str) -> List[str]:
        """Return list of available units for a category."""
        return list(self.conversion_factors.get(category, {}).keys())

    def convert(self, value: float, from_unit: str, to_unit: str, category: str) -> Optional[float]:
        """
        Convert a value from one unit to another within the same category.

        Args:
            value: The numeric value to convert
            from_unit: The source unit
            to_unit: The target unit
            category: The category of units (length, weight, volume)

        Returns:
            The converted value, or None if conversion is not possible
        """
        if category not in self.conversion_factors:
            return None

        units = self.conversion_factors[category]
        if from_unit not in units or to_unit not in units:
            return None

        # Convert to base unit first, then to target unit
        base_value = value * units[from_unit]
        converted_value = base_value / units[to_unit]

        # Save to history
        self.history.append({
            'value': value,
            'from_unit': from_unit,
            'to_unit': to_unit,
            'category': category,
            'result': converted_value
        })
        self._save_history()

        return converted_value

    def get_conversion_history(self) -> List[Dict]:
        """Return the conversion history."""
        return self.history.copy()

    def clear_history(self) -> None:
        """Clear the conversion history."""
        self.history = []
        self._save_history()


def validate_number_input(value_str: str) -> Optional[float]:
    """Validate and convert string input to float."""
    try:
        value = float(value_str.strip())
        if value < 0:
            print("[X] Error: Please enter a positive number.")
            return None
        return value
    except ValueError:
        print("[X] Error: Please enter a valid number.")
        return None


def display_menu() -> None:
    """Display the main menu."""
    print("\n" + "="*50)
    print("[WRENCH] UNIT CONVERTER")
    print("="*50)
    print("1. Convert units")
    print("2. View conversion history")
    print("3. Clear history")
    print("4. Exit")
    print("="*50)


def display_categories(converter: UnitConverter) -> None:
    """Display available categories."""
    print("\n[CLIPBOARD] Available Categories:")
    categories = converter.get_categories()
    for i, category in enumerate(categories, 1):
        print(f"  {i}. {category.title()}")


def display_units(converter: UnitConverter, category: str) -> None:
    """Display available units for a category."""
    print(f"\n[RULER] Available {category.title()} Units:")
    units = converter.get_units(category)
    for i, unit in enumerate(units, 1):
        print(f"  {i}. {unit}")


def get_category_choice(converter: UnitConverter) -> Optional[str]:
    """Get category choice from user."""
    categories = converter.get_categories()

    while True:
        try:
            choice = input(f"\nSelect category (1-{len(categories)}): ").strip()
            if choice.lower() in ['q', 'quit', 'exit']:
                return None

            choice_num = int(choice)
            if 1 <= choice_num <= len(categories):
                return categories[choice_num - 1]
            else:
                print(f"[X] Please enter a number between 1 and {len(categories)}")
        except ValueError:
            print("[X] Please enter a valid number or 'q' to quit")


def get_unit_choice(converter: UnitConverter, category: str, prompt: str) -> Optional[str]:
    """Get unit choice from user."""
    units = converter.get_units(category)

    while True:
        try:
            choice = input(f"{prompt} (1-{len(units)}): ").strip()
            if choice.lower() in ['q', 'quit', 'exit']:
                return None

            choice_num = int(choice)
            if 1 <= choice_num <= len(units):
                return units[choice_num - 1]
            else:
                print(f"[X] Please enter a number between 1 and {len(units)}")
        except ValueError:
            print("[X] Please enter a valid number or 'q' to quit")


def perform_conversion(converter: UnitConverter) -> None:
    """Perform a unit conversion."""
    display_categories(converter)
    category = get_category_choice(converter)
    if not category:
        return

    display_units(converter, category)
    from_unit = get_unit_choice(converter, category, "Select source unit")
    if not from_unit:
        return

    to_unit = get_unit_choice(converter, category, "Select target unit")
    if not to_unit:
        return

    if from_unit == to_unit:
        print("[X] Source and target units are the same!")
        return

    # Get value to convert
    while True:
        value_str = input(f"\nEnter value to convert from {from_unit} to {to_unit}: ").strip()
        if value_str.lower() in ['q', 'quit', 'exit']:
            return

        value = validate_number_input(value_str)
        if value is not None:
            break

    # Perform conversion
    result = converter.convert(value, from_unit, to_unit, category)
    if result is not None:
        print("\n[OK] Conversion Result:")
        print(f"   {value} {from_unit} = {result:.6f} {to_unit}")
    else:
        print("[X] Conversion failed!")


def view_history(converter: UnitConverter) -> None:
    """View conversion history."""
    history = converter.get_conversion_history()

    if not history:
        print("\n[MEMO] No conversion history found.")
        return

    print(f"\n[MEMO] Conversion History ({len(history)} entries):")
    print("-" * 60)

    # Show last 10 entries
    recent_history = history[-10:]
    for i, entry in enumerate(reversed(recent_history), 1):
        print(f"{i:2d}. {entry['value']} {entry['from_unit']} → "
              f"{entry['result']:.6f} {entry['to_unit']} ({entry['category']})")

    if len(history) > 10:
        print(f"... and {len(history) - 10} more entries")


def clear_history(converter: UnitConverter) -> None:
    """Clear conversion history."""
    confirm = input("\nWARNING  Are you sure you want to clear all history? (y/N): ").strip().lower()
    if confirm in ['y', 'yes']:
        converter.clear_history()
        print("[OK] History cleared successfully!")
    else:
        print("[X] History not cleared.")


def main():
    """Main program loop."""
    converter = UnitConverter()

    print("[WRENCH] Welcome to Unit Converter!")
    print("Convert between different units of length, weight, and volume.")

    while True:
        display_menu()

        try:
            choice = input("\nEnter your choice (1-4): ").strip()

            if choice == '1':
                perform_conversion(converter)
            elif choice == '2':
                view_history(converter)
            elif choice == '3':
                clear_history(converter)
            elif choice == '4':
                print("\n[WAVE] Thank you for using Unit Converter!")
                break
            else:
                print("[X] Please enter a valid choice (1-4)")

        except KeyboardInterrupt:
            print("\n\n[WAVE] Goodbye!")
            break
        except Exception as e:
            print(f"[X] An error occurred: {e}")


if __name__ == "__main__":
    main()

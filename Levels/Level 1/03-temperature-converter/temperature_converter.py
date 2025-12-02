#!/usr/bin/env python3
"""
Temperature Converter
A command-line program for converting between Celsius, Fahrenheit, and Kelvin.
"""

import sys


def celsius_to_fahrenheit(celsius: float) -> float:
    """Convert Celsius to Fahrenheit."""
    return (celsius * 9 / 5) + 32


def fahrenheit_to_celsius(fahrenheit: float) -> float:
    """Convert Fahrenheit to Celsius."""
    return (fahrenheit - 32) * 5 / 9


def celsius_to_kelvin(celsius: float) -> float:
    """Convert Celsius to Kelvin."""
    return celsius + 273.15


def kelvin_to_celsius(kelvin: float) -> float:
    """Convert Kelvin to Celsius."""
    return kelvin - 273.15


def fahrenheit_to_kelvin(fahrenheit: float) -> float:
    """Convert Fahrenheit to Kelvin."""
    celsius = fahrenheit_to_celsius(fahrenheit)
    return celsius_to_kelvin(celsius)


def kelvin_to_fahrenheit(kelvin: float) -> float:
    """Convert Kelvin to Fahrenheit."""
    celsius = kelvin_to_celsius(kelvin)
    return celsius_to_fahrenheit(celsius)


def get_valid_temperature(prompt: str) -> float:
    """Get a valid temperature value from user input."""
    while True:
        try:
            value = input(prompt)
            if not value.strip():
                print("Please enter a temperature value.")
                continue

            temperature = float(value)
            return temperature
        except ValueError:
            print("Invalid input. Please enter a valid number.")


def display_menu():
    """Display the conversion menu."""
    print("\n" + "=" * 50)
    print("TEMPERATURE CONVERTER")
    print("=" * 50)
    print("1. Celsius to Fahrenheit")
    print("2. Fahrenheit to Celsius")
    print("3. Celsius to Kelvin")
    print("4. Kelvin to Celsius")
    print("5. Fahrenheit to Kelvin")
    print("6. Kelvin to Fahrenheit")
    print("7. Exit")
    print("=" * 50)


def get_menu_choice() -> int:
    """Get a valid menu choice from the user."""
    while True:
        try:
            choice = input("Enter your choice (1-7): ").strip()
            if not choice:
                print("Please enter a choice.")
                continue

            choice_num = int(choice)
            if 1 <= choice_num <= 7:
                return choice_num
            else:
                print("Please enter a number between 1 and 7.")
        except ValueError:
            print("Invalid input. Please enter a number between 1 and 7.")


def format_temperature(temp: float, unit: str) -> str:
    """Format temperature with proper rounding and unit."""
    return f"{temp:.2f}°{unit}"


def perform_conversion(choice: int) -> None:
    """Perform the selected temperature conversion."""
    conversions = {
        1: ("Celsius", "Fahrenheit", celsius_to_fahrenheit),
        2: ("Fahrenheit", "Celsius", fahrenheit_to_celsius),
        3: ("Celsius", "Kelvin", celsius_to_kelvin),
        4: ("Kelvin", "Celsius", kelvin_to_celsius),
        5: ("Fahrenheit", "Kelvin", fahrenheit_to_kelvin),
        6: ("Kelvin", "Fahrenheit", kelvin_to_fahrenheit),
    }

    from_unit, to_unit, conversion_func = conversions[choice]

    temperature = get_valid_temperature(f"Enter temperature in {from_unit}: ")
    converted_temp = conversion_func(temperature)

    print("\nConversion Result:")
    print(
        f"{format_temperature(temperature, from_unit[0])} = {format_temperature(converted_temp, to_unit[0])}"
    )


def main():
    """Main program loop."""
    print("Welcome to the Temperature Converter!")

    while True:
        display_menu()
        choice = get_menu_choice()

        if choice == 7:
            print("Thank you for using the Temperature Converter. Goodbye!")
            break

        perform_conversion(choice)

        # Ask if user wants to continue
        while True:
            continue_choice = (
                input("\nWould you like to perform another conversion? (y/n): ")
                .strip()
                .lower()
            )
            if continue_choice in ["y", "yes"]:
                break
            elif continue_choice in ["n", "no"]:
                print("Thank you for using the Temperature Converter. Goodbye!")
                sys.exit(0)
            else:
                print("Please enter 'y' for yes or 'n' for no.")


if __name__ == "__main__":
    main()

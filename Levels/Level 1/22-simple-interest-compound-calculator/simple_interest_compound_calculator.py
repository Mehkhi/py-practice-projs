#!/usr/bin/env python3
"""
Simple & Compound Interest Calculator

A command-line program that calculates simple and compound interest
for given principal amount, interest rate, and time period.
"""

import csv
from typing import List, Dict, Any


def calculate_simple_interest(principal: float, rate: float, time: float) -> float:
    """
    Calculate simple interest.

    Formula: I = P * R * T
    Where:
    - P = Principal amount
    - R = Annual interest rate (as decimal)
    - T = Time in years

    Args:
        principal: The initial amount of money
        rate: Annual interest rate as a percentage
        time: Time period in years

    Returns:
        Simple interest amount
    """
    return principal * (rate / 100) * time


def calculate_compound_interest(principal: float, rate: float, time: float,
                               compounding_frequency: int = 1) -> float:
    """
    Calculate compound interest.

    Formula: A = P(1 + r/n)^(nt)
    Where:
    - P = Principal amount
    - r = Annual interest rate (as decimal)
    - n = Number of times interest is compounded per year
    - t = Time in years

    Args:
        principal: The initial amount of money
        rate: Annual interest rate as a percentage
        time: Time period in years
        compounding_frequency: Number of times interest is compounded per year

    Returns:
        Compound interest amount (total amount - principal)
    """
    r = rate / 100
    n = compounding_frequency
    t = time

    total_amount = principal * (1 + r / n) ** (n * t)
    return total_amount - principal


def get_year_by_year_growth(principal: float, rate: float, time: int,
                           compounding_frequency: int = 1) -> List[Dict[str, Any]]:
    """
    Generate year-by-year growth table.

    Args:
        principal: The initial amount of money
        rate: Annual interest rate as a percentage
        time: Time period in years
        compounding_frequency: Number of times interest is compounded per year

    Returns:
        List of dictionaries containing year-by-year data
    """
    growth_data = []
    current_amount = principal

    for year in range(1, time + 1):
        # Calculate compound interest for this year
        year_interest = calculate_compound_interest(current_amount, rate, 1, compounding_frequency)
        current_amount += year_interest

        # Calculate simple interest for comparison
        simple_total = principal + calculate_simple_interest(principal, rate, year)

        growth_data.append({
            'year': year,
            'compound_amount': round(current_amount, 2),
            'simple_amount': round(simple_total, 2),
            'year_interest': round(year_interest, 2),
            'total_interest': round(current_amount - principal, 2)
        })

    return growth_data


def validate_input(value: str, input_type: str) -> float:
    """
    Validate user input for numeric values.

    Args:
        value: User input string
        input_type: Type of input for error messages

    Returns:
        Validated float value

    Raises:
        ValueError: If input is invalid
    """
    if not value.strip():
        raise ValueError(f"{input_type} cannot be empty")

    try:
        num_value = float(value)
        if num_value < 0:
            raise ValueError(f"{input_type} cannot be negative")
        return num_value
    except ValueError as e:
        if "could not convert" in str(e):
            raise ValueError(f"{input_type} must be a valid number")
        raise


def display_results(principal: float, rate: float, time: float,
                   compounding_frequency: int = 1) -> None:
    """
    Display calculation results in a formatted table.

    Args:
        principal: The initial amount of money
        rate: Annual interest rate as a percentage
        time: Time period in years
        compounding_frequency: Number of times interest is compounded per year
    """
    simple_interest = calculate_simple_interest(principal, rate, time)
    compound_interest = calculate_compound_interest(principal, rate, time, compounding_frequency)

    simple_total = principal + simple_interest
    compound_total = principal + compound_interest

    print("\n" + "="*60)
    print("INTEREST CALCULATION RESULTS")
    print("="*60)
    print(f"Principal Amount:     ${principal:,.2f}")
    print(f"Annual Interest Rate: {rate:.2f}%")
    print(f"Time Period:          {time:.1f} years")
    print(f"Compounding Frequency: {compounding_frequency} times per year")
    print("-"*60)
    print(f"Simple Interest:      ${simple_interest:,.2f}")
    print(f"Simple Total:         ${simple_total:,.2f}")
    print(f"Compound Interest:    ${compound_interest:,.2f}")
    print(f"Compound Total:       ${compound_total:,.2f}")
    print("-"*60)
    print(f"Difference:           ${compound_total - simple_total:,.2f}")
    print(f"Extra Earnings:       {((compound_total - simple_total) / simple_total * 100):.2f}%")
    print("="*60)


def display_year_by_year_table(growth_data: List[Dict[str, Any]]) -> None:
    """
    Display year-by-year growth table.

    Args:
        growth_data: List of year-by-year data
    """
    print("\n" + "="*80)
    print("YEAR-BY-YEAR GROWTH COMPARISON")
    print("="*80)
    print(f"{'Year':<6} {'Compound Amount':<16} {'Simple Amount':<16} {'Year Interest':<14} {'Total Interest':<16}")
    print("-"*80)

    for data in growth_data:
        print(f"{data['year']:<6} ${data['compound_amount']:<15,.2f} ${data['simple_amount']:<15,.2f} "
              f"${data['year_interest']:<13,.2f} ${data['total_interest']:<15,.2f}")

    print("="*80)


def export_to_csv(growth_data: List[Dict[str, Any]], filename: str = "interest_calculation.csv") -> None:
    """
    Export growth data to CSV file.

    Args:
        growth_data: List of year-by-year data
        filename: Output CSV filename
    """
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['year', 'compound_amount', 'simple_amount', 'year_interest', 'total_interest']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            writer.writerows(growth_data)

        print(f"\nData exported successfully to '{filename}'")
    except Exception as e:
        print(f"Error exporting to CSV: {e}")


def compare_scenarios(scenarios: List[Dict[str, float]]) -> None:
    """
    Compare multiple interest calculation scenarios.

    Args:
        scenarios: List of scenario dictionaries with principal, rate, time keys
    """
    print("\n" + "="*90)
    print("SCENARIO COMPARISON")
    print("="*90)
    print(f"{'Scenario':<12} {'Principal':<12} {'Rate':<8} {'Time':<8} {'Simple Total':<14} {'Compound Total':<16} {'Difference':<12}")
    print("-"*90)

    for i, scenario in enumerate(scenarios, 1):
        principal = scenario['principal']
        rate = scenario['rate']
        time = scenario['time']

        simple_total = principal + calculate_simple_interest(principal, rate, time)
        compound_total = principal + calculate_compound_interest(principal, rate, time)
        difference = compound_total - simple_total

        print(f"Scenario {i:<6} ${principal:<11,.0f} {rate:<7.1f}% {time:<7.1f} ${simple_total:<13,.2f} "
              f"${compound_total:<15,.2f} ${difference:<11,.2f}")

    print("="*90)


def main():
    """Main program function."""
    print("Simple & Compound Interest Calculator")
    print("="*40)

    while True:
        try:
            # Get user input
            print("\nEnter the following details:")
            principal_input = input("Principal amount ($): ").strip()
            rate_input = input("Annual interest rate (%): ").strip()
            time_input = input("Time period (years): ").strip()

            # Validate inputs
            principal = validate_input(principal_input, "Principal amount")
            rate = validate_input(rate_input, "Interest rate")
            time = validate_input(time_input, "Time period")

            # Get compounding frequency (optional)
            compounding_input = input("Compounding frequency per year (default: 1): ").strip()
            compounding_frequency = 1
            if compounding_input:
                compounding_frequency = int(validate_input(compounding_input, "Compounding frequency"))
                if compounding_frequency <= 0:
                    raise ValueError("Compounding frequency must be positive")

            # Display results
            display_results(principal, rate, time, compounding_frequency)

            # Ask for additional features
            if time >= 1:
                show_table = input("\nShow year-by-year growth table? (y/n): ").strip().lower()
                if show_table in ['y', 'yes']:
                    growth_data = get_year_by_year_growth(principal, rate, int(time), compounding_frequency)
                    display_year_by_year_table(growth_data)

                    export_csv = input("\nExport data to CSV? (y/n): ").strip().lower()
                    if export_csv in ['y', 'yes']:
                        filename = input("Enter filename (default: interest_calculation.csv): ").strip()
                        if not filename:
                            filename = "interest_calculation.csv"
                        export_to_csv(growth_data, filename)

            # Ask for scenario comparison
            compare_more = input("\nCompare with another scenario? (y/n): ").strip().lower()
            if compare_more in ['y', 'yes']:
                scenarios = [{'principal': principal, 'rate': rate, 'time': time}]

                while True:
                    try:
                        print(f"\nScenario {len(scenarios) + 1}:")
                        new_principal = validate_input(input("Principal amount ($): ").strip(), "Principal amount")
                        new_rate = validate_input(input("Annual interest rate (%): ").strip(), "Interest rate")
                        new_time = validate_input(input("Time period (years): ").strip(), "Time period")

                        scenarios.append({'principal': new_principal, 'rate': new_rate, 'time': new_time})

                        add_more = input("Add another scenario? (y/n): ").strip().lower()
                        if add_more not in ['y', 'yes']:
                            break
                    except ValueError as e:
                        print(f"Error: {e}")
                        continue

                compare_scenarios(scenarios)

            # Ask if user wants to calculate again
            again = input("\nCalculate again? (y/n): ").strip().lower()
            if again not in ['y', 'yes']:
                break

        except ValueError as e:
            print(f"Error: {e}")
            print("Please try again with valid input.")
        except KeyboardInterrupt:
            print("\n\nProgram interrupted by user. Goodbye!")
            break
        except Exception as e:
            print(f"Unexpected error: {e}")
            print("Please try again.")

    print("\nThank you for using the Interest Calculator!")


if __name__ == "__main__":
    main()

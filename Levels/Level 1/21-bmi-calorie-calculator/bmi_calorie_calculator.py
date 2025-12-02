#!/usr/bin/env python3
"""
BMI & Calorie Calculator

A command-line program that calculates BMI and estimates daily calorie needs
using the Harris-Benedict equation. Supports both metric and imperial units.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional


class BMICalculator:
    """BMI and calorie calculation functionality."""

    def __init__(self):
        self.history_file = "bmi_history.json"
        self.history = self._load_history()

    def calculate_bmi(self, weight: float, height: float, unit_system: str = "metric") -> float:
        """
        Calculate BMI from weight and height.

        Args:
            weight: Weight in kg (metric) or lbs (imperial)
            height: Height in meters (metric) or inches (imperial)
            unit_system: "metric" or "imperial"

        Returns:
            BMI value
        """
        if unit_system == "imperial":
            # Convert pounds to kg and inches to meters
            weight_kg = weight * 0.453592
            height_m = height * 0.0254
        else:
            weight_kg = weight
            height_m = height

        if height_m <= 0:
            raise ValueError("Height must be greater than 0")

        return weight_kg / (height_m ** 2)

    def get_bmi_category(self, bmi: float) -> str:
        """
        Get BMI category based on BMI value.

        Args:
            bmi: BMI value

        Returns:
            BMI category string
        """
        if bmi < 18.5:
            return "Underweight"
        elif bmi < 25:
            return "Normal weight"
        elif bmi < 30:
            return "Overweight"
        else:
            return "Obese"

    def calculate_bmr(self, weight: float, height: float, age: int, gender: str, unit_system: str = "metric") -> float:
        """
        Calculate Basal Metabolic Rate using Harris-Benedict equation.

        Args:
            weight: Weight in kg (metric) or lbs (imperial)
            height: Height in meters (metric) or inches (imperial)
            age: Age in years
            gender: "male" or "female"
            unit_system: "metric" or "imperial"

        Returns:
            BMR in calories per day
        """
        if unit_system == "imperial":
            # Convert to metric for calculation
            weight_kg = weight * 0.453592
            height_cm = height * 2.54
        else:
            weight_kg = weight
            height_cm = height * 100

        if gender.lower() == "male":
            bmr = 88.362 + (13.397 * weight_kg) + (4.799 * height_cm) - (5.677 * age)
        else:
            bmr = 447.593 + (9.247 * weight_kg) + (3.098 * height_cm) - (4.330 * age)

        return bmr

    def calculate_tdee(self, bmr: float, activity_level: str) -> float:
        """
        Calculate Total Daily Energy Expenditure based on activity level.

        Args:
            bmr: Basal Metabolic Rate
            activity_level: Activity level description

        Returns:
            TDEE in calories per day
        """
        activity_multipliers = {
            "sedentary": 1.2,      # Little to no exercise
            "light": 1.375,        # Light exercise 1-3 days/week
            "moderate": 1.55,      # Moderate exercise 3-5 days/week
            "active": 1.725,       # Heavy exercise 6-7 days/week
            "very_active": 1.9     # Very heavy exercise, physical job
        }

        multiplier = activity_multipliers.get(activity_level.lower(), 1.2)
        return bmr * multiplier

    def calculate_weight_goal(self, current_weight: float, target_weight: float,
                            current_tdee: float, unit_system: str = "metric") -> Dict:
        """
        Calculate timeline and calorie adjustments for weight goal.

        Args:
            current_weight: Current weight
            target_weight: Target weight
            current_tdee: Current TDEE
            unit_system: "metric" or "imperial"

        Returns:
            Dictionary with goal information
        """
        if unit_system == "imperial":
            weight_diff = (current_weight - target_weight) * 0.453592  # Convert to kg
        else:
            weight_diff = current_weight - target_weight

        # Safe weight loss/gain: 0.5-1 kg per week
        weekly_change = 0.75  # kg per week
        weeks_needed = abs(weight_diff) / weekly_change

        # Calorie deficit/surplus needed (1 kg = ~7700 calories)
        daily_adjustment = abs(weight_diff * 7700) / (weeks_needed * 7)

        if weight_diff > 0:  # Weight loss
            target_calories = current_tdee - daily_adjustment
            goal_type = "loss"
        else:  # Weight gain
            target_calories = current_tdee + daily_adjustment
            goal_type = "gain"

        return {
            "weeks_needed": weeks_needed,
            "daily_adjustment": daily_adjustment,
            "target_calories": target_calories,
            "goal_type": goal_type
        }

    def save_to_history(self, data: Dict) -> None:
        """Save calculation data to history."""
        timestamp = datetime.now().isoformat()
        entry = {
            "timestamp": timestamp,
            "data": data
        }
        self.history.append(entry)
        self._save_history()

    def get_history(self) -> List[Dict]:
        """Get calculation history."""
        return self.history

    def _load_history(self) -> List[Dict]:
        """Load history from file."""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return []
        return []

    def _save_history(self) -> None:
        """Save history to file."""
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=2)


def get_user_input(prompt: str, input_type: type = str, min_val: Optional[float] = None,
                  max_val: Optional[float] = None) -> any:
    """
    Get validated user input.

    Args:
        prompt: Input prompt
        input_type: Expected input type
        min_val: Minimum allowed value
        max_val: Maximum allowed value

    Returns:
        Validated user input
    """
    while True:
        try:
            value = input(prompt).strip()
            if not value:
                print("Input cannot be empty. Please try again.")
                continue

            if input_type is float:
                value = float(value)
            elif input_type is int:
                value = int(value)

            if min_val is not None and value < min_val:
                print(f"Value must be at least {min_val}. Please try again.")
                continue

            if max_val is not None and value > max_val:
                print(f"Value must be at most {max_val}. Please try again.")
                continue

            return value
        except ValueError:
            print("Invalid input. Please enter a valid number.")
        except KeyboardInterrupt:
            print("\nGoodbye!")
            exit(0)


def display_menu() -> None:
    """Display the main menu."""
    print("\n" + "="*50)
    print("BMI & CALORIE CALCULATOR")
    print("="*50)
    print("1. Calculate BMI")
    print("2. Calculate Calorie Needs")
    print("3. Calculate Weight Goal")
    print("4. View History")
    print("5. Exit")
    print("="*50)


def main():
    """Main program function."""
    calculator = BMICalculator()

    print("Welcome to the BMI & Calorie Calculator!")
    print("This program helps you calculate BMI and estimate your daily calorie needs.")

    while True:
        display_menu()

        try:
            choice = input("Enter your choice (1-5): ").strip()
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break

        if choice == "1":
            calculate_bmi_menu(calculator)
        elif choice == "2":
            calculate_calorie_menu(calculator)
        elif choice == "3":
            calculate_goal_menu(calculator)
        elif choice == "4":
            view_history_menu(calculator)
        elif choice == "5":
            print("Thank you for using the BMI & Calorie Calculator!")
            break
        else:
            print("Invalid choice. Please enter 1-5.")


def calculate_bmi_menu(calculator: BMICalculator) -> None:
    """BMI calculation menu."""
    print("\n--- BMI CALCULATION ---")

    # Get unit system
    print("Choose unit system:")
    print("1. Metric (kg, meters)")
    print("2. Imperial (lbs, inches)")

    unit_choice = get_user_input("Enter choice (1-2): ", int, 1, 2)
    unit_system = "metric" if unit_choice == 1 else "imperial"

    # Get weight
    weight_unit = "kg" if unit_system == "metric" else "lbs"
    weight = get_user_input(f"Enter your weight in {weight_unit}: ", float, 0.1, 1000)

    # Get height
    height_unit = "meters" if unit_system == "metric" else "inches"
    height = get_user_input(f"Enter your height in {height_unit}: ", float, 0.1, 300)

    try:
        bmi = calculator.calculate_bmi(weight, height, unit_system)
        category = calculator.get_bmi_category(bmi)

        print("\n--- RESULTS ---")
        print(f"Weight: {weight} {weight_unit}")
        print(f"Height: {height} {height_unit}")
        print(f"BMI: {bmi:.2f}")
        print(f"Category: {category}")

        # Save to history
        calculator.save_to_history({
            "type": "bmi",
            "weight": weight,
            "height": height,
            "unit_system": unit_system,
            "bmi": bmi,
            "category": category
        })

    except ValueError as e:
        print(f"Error: {e}")


def calculate_calorie_menu(calculator: BMICalculator) -> None:
    """Calorie calculation menu."""
    print("\n--- CALORIE NEEDS CALCULATION ---")

    # Get unit system
    print("Choose unit system:")
    print("1. Metric (kg, meters)")
    print("2. Imperial (lbs, inches)")

    unit_choice = get_user_input("Enter choice (1-2): ", int, 1, 2)
    unit_system = "metric" if unit_choice == 1 else "imperial"

    # Get basic info
    weight_unit = "kg" if unit_system == "metric" else "lbs"
    weight = get_user_input(f"Enter your weight in {weight_unit}: ", float, 0.1, 1000)

    height_unit = "meters" if unit_system == "metric" else "inches"
    height = get_user_input(f"Enter your height in {height_unit}: ", float, 0.1, 300)

    age = get_user_input("Enter your age: ", int, 1, 150)

    print("Enter your gender:")
    print("1. Male")
    print("2. Female")
    gender_choice = get_user_input("Enter choice (1-2): ", int, 1, 2)
    gender = "male" if gender_choice == 1 else "female"

    # Get activity level
    print("\nSelect your activity level:")
    print("1. Sedentary (little to no exercise)")
    print("2. Light (light exercise 1-3 days/week)")
    print("3. Moderate (moderate exercise 3-5 days/week)")
    print("4. Active (heavy exercise 6-7 days/week)")
    print("5. Very Active (very heavy exercise, physical job)")

    activity_choice = get_user_input("Enter choice (1-5): ", int, 1, 5)
    activity_levels = ["sedentary", "light", "moderate", "active", "very_active"]
    activity_level = activity_levels[activity_choice - 1]

    try:
        bmr = calculator.calculate_bmr(weight, height, age, gender, unit_system)
        tdee = calculator.calculate_tdee(bmr, activity_level)

        print("\n--- RESULTS ---")
        print(f"Weight: {weight} {weight_unit}")
        print(f"Height: {height} {height_unit}")
        print(f"Age: {age} years")
        print(f"Gender: {gender.title()}")
        print(f"Activity Level: {activity_level.replace('_', ' ').title()}")
        print(f"BMR (Basal Metabolic Rate): {bmr:.0f} calories/day")
        print(f"TDEE (Total Daily Energy Expenditure): {tdee:.0f} calories/day")

        # Save to history
        calculator.save_to_history({
            "type": "calorie",
            "weight": weight,
            "height": height,
            "age": age,
            "gender": gender,
            "unit_system": unit_system,
            "activity_level": activity_level,
            "bmr": bmr,
            "tdee": tdee
        })

    except ValueError as e:
        print(f"Error: {e}")


def calculate_goal_menu(calculator: BMICalculator) -> None:
    """Weight goal calculation menu."""
    print("\n--- WEIGHT GOAL CALCULATION ---")

    # Get unit system
    print("Choose unit system:")
    print("1. Metric (kg, meters)")
    print("2. Imperial (lbs, inches)")

    unit_choice = get_user_input("Enter choice (1-2): ", int, 1, 2)
    unit_system = "metric" if unit_choice == 1 else "imperial"

    # Get current weight and target weight
    weight_unit = "kg" if unit_system == "metric" else "lbs"
    current_weight = get_user_input(f"Enter your current weight in {weight_unit}: ", float, 0.1, 1000)
    target_weight = get_user_input(f"Enter your target weight in {weight_unit}: ", float, 0.1, 1000)

    # Get other info for TDEE calculation
    height_unit = "meters" if unit_system == "metric" else "inches"
    height = get_user_input(f"Enter your height in {height_unit}: ", float, 0.1, 300)

    age = get_user_input("Enter your age: ", int, 1, 150)

    print("Enter your gender:")
    print("1. Male")
    print("2. Female")
    gender_choice = get_user_input("Enter choice (1-2): ", int, 1, 2)
    gender = "male" if gender_choice == 1 else "female"

    # Get activity level
    print("\nSelect your activity level:")
    print("1. Sedentary (little to no exercise)")
    print("2. Light (light exercise 1-3 days/week)")
    print("3. Moderate (moderate exercise 3-5 days/week)")
    print("4. Active (heavy exercise 6-7 days/week)")
    print("5. Very Active (very heavy exercise, physical job)")

    activity_choice = get_user_input("Enter choice (1-5): ", int, 1, 5)
    activity_levels = ["sedentary", "light", "moderate", "active", "very_active"]
    activity_level = activity_levels[activity_choice - 1]

    try:
        bmr = calculator.calculate_bmr(current_weight, height, age, gender, unit_system)
        current_tdee = calculator.calculate_tdee(bmr, activity_level)
        goal_info = calculator.calculate_weight_goal(current_weight, target_weight, current_tdee, unit_system)

        print("\n--- RESULTS ---")
        print(f"Current Weight: {current_weight} {weight_unit}")
        print(f"Target Weight: {target_weight} {weight_unit}")
        print(f"Current TDEE: {current_tdee:.0f} calories/day")
        print(f"\nGoal: {goal_info['goal_type'].title()}")
        print(f"Estimated Time: {goal_info['weeks_needed']:.1f} weeks")
        print(f"Daily Calorie Adjustment: {goal_info['daily_adjustment']:.0f} calories")
        print(f"Target Daily Calories: {goal_info['target_calories']:.0f} calories/day")

        # Save to history
        calculator.save_to_history({
            "type": "goal",
            "current_weight": current_weight,
            "target_weight": target_weight,
            "height": height,
            "age": age,
            "gender": gender,
            "unit_system": unit_system,
            "activity_level": activity_level,
            "current_tdee": current_tdee,
            "goal_info": goal_info
        })

    except ValueError as e:
        print(f"Error: {e}")


def view_history_menu(calculator: BMICalculator) -> None:
    """View calculation history menu."""
    history = calculator.get_history()

    if not history:
        print("\nNo calculation history found.")
        return

    print(f"\n--- CALCULATION HISTORY ({len(history)} entries) ---")

    for i, entry in enumerate(reversed(history[-10:]), 1):  # Show last 10 entries
        timestamp = datetime.fromisoformat(entry["timestamp"])
        data = entry["data"]

        print(f"\n{i}. {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")

        if data["type"] == "bmi":
            print(f"   BMI: {data['bmi']:.2f} ({data['category']})")
            print(f"   Weight: {data['weight']} {'kg' if data['unit_system'] == 'metric' else 'lbs'}")
            print(f"   Height: {data['height']} {'meters' if data['unit_system'] == 'metric' else 'inches'}")

        elif data["type"] == "calorie":
            print(f"   TDEE: {data['tdee']:.0f} calories/day")
            print(f"   BMR: {data['bmr']:.0f} calories/day")
            print(f"   Activity: {data['activity_level'].replace('_', ' ').title()}")

        elif data["type"] == "goal":
            print(f"   Goal: {data['goal_info']['goal_type'].title()}")
            print(f"   Current Weight: {data['current_weight']} {'kg' if data['unit_system'] == 'metric' else 'lbs'}")
            print(f"   Target Weight: {data['target_weight']} {'kg' if data['unit_system'] == 'metric' else 'lbs'}")
            print(f"   Timeline: {data['goal_info']['weeks_needed']:.1f} weeks")


if __name__ == "__main__":
    main()

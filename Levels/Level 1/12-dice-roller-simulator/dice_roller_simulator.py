#!/usr/bin/env python3
"""
Dice Roller Simulator

A command-line dice rolling program that supports standard dice notation
like "3d6" (roll 3 six-sided dice) and modifiers like "2d6+3".
"""

import random
import re
from typing import List, Tuple, Dict


class DiceRoller:
    """Main dice rolling class with notation parsing and rolling capabilities."""

    def __init__(self):
        self.roll_history: List[Dict] = []

    def parse_dice_notation(self, notation: str) -> Tuple[int, int, int]:
        """
        Parse dice notation like "3d6+2" into components.

        Args:
            notation: String in format "XdY+Z" where X is number of dice,
                     Y is sides, Z is optional modifier

        Returns:
            Tuple of (num_dice, num_sides, modifier)

        Raises:
            ValueError: If notation is invalid
        """
        if not notation or not isinstance(notation, str):
            raise ValueError("Dice notation must be a non-empty string")

        # Clean and normalize the notation
        notation = notation.strip().lower()

        # Pattern matches: 3d6, 2d6+3, 1d20-2, d6 (implies 1 die)
        pattern = r"^(\d*)d(\d+)([+-]\d+)?$"
        match = re.fullmatch(pattern, notation)

        if not match:
            raise ValueError(f"Invalid dice notation: {notation}")

        num_dice_str, num_sides_str, modifier_str = match.groups()

        # Default to 1 die if not specified (e.g., "d6")
        num_dice = int(num_dice_str) if num_dice_str else 1
        num_sides = int(num_sides_str)
        modifier = int(modifier_str) if modifier_str else 0

        # Validate values
        if num_dice < 1:
            raise ValueError("Number of dice must be at least 1")
        if num_sides < 2:
            raise ValueError("Number of sides must be at least 2")
        if num_dice > 100:
            raise ValueError("Number of dice cannot exceed 100")

        return num_dice, num_sides, modifier

    def roll_dice(self, num_dice: int, num_sides: int) -> List[int]:
        """
        Roll the specified number of dice with the given number of sides.

        Args:
            num_dice: Number of dice to roll
            num_sides: Number of sides on each die

        Returns:
            List of individual roll results
        """
        return [random.randint(1, num_sides) for _ in range(num_dice)]

    def roll_with_notation(self, notation: str) -> Dict:
        """
        Parse notation and perform the roll.

        Args:
            notation: Dice notation string

        Returns:
            Dictionary with roll details
        """
        try:
            num_dice, num_sides, modifier = self.parse_dice_notation(notation)
            individual_rolls = self.roll_dice(num_dice, num_sides)
            total = sum(individual_rolls) + modifier

            result = {
                "notation": notation,
                "num_dice": num_dice,
                "num_sides": num_sides,
                "modifier": modifier,
                "individual_rolls": individual_rolls,
                "subtotal": sum(individual_rolls),
                "total": total,
                "display": self._format_roll_display(
                    notation, individual_rolls, modifier, total
                ),
            }

            # Add to history
            self.roll_history.append(result)

            return result

        except ValueError as e:
            return {"error": str(e)}

    def _format_roll_display(
        self, notation: str, rolls: List[int], modifier: int, total: int
    ) -> str:
        """Format the roll result for display."""
        rolls_str = " + ".join(map(str, rolls))

        if modifier > 0:
            return f"{notation}: {rolls_str} + {modifier} = {total}"
        elif modifier < 0:
            return f"{notation}: {rolls_str} - {abs(modifier)} = {total}"
        else:
            return f"{notation}: {rolls_str} = {total}"

    def get_roll_history(self) -> List[Dict]:
        """Get the history of all rolls."""
        return self.roll_history.copy()

    def clear_history(self):
        """Clear the roll history."""
        self.roll_history.clear()

    def get_statistics(self) -> Dict:
        """Get basic statistics about rolls."""
        if not self.roll_history:
            return {"message": "No rolls yet"}

        totals = [roll["total"] for roll in self.roll_history if "total" in roll]

        if not totals:
            return {"message": "No valid rolls yet"}

        return {
            "total_rolls": len(totals),
            "average": sum(totals) / len(totals),
            "min": min(totals),
            "max": max(totals),
            "sum": sum(totals),
        }


def display_menu():
    """Display the main menu options."""
    print("\n" + "=" * 50)
    print("[DICE] DICE ROLLER SIMULATOR [DICE]")
    print("=" * 50)
    print("1. Roll dice (e.g., 3d6, 2d6+3, d20)")
    print("2. View roll history")
    print("3. View statistics")
    print("4. Clear history")
    print("5. Exit")
    print("=" * 50)


def get_user_choice() -> str:
    """Get and validate user menu choice."""
    while True:
        choice = input("\nEnter your choice (1-5): ").strip()
        if choice in ["1", "2", "3", "4", "5"]:
            return choice
        print("Invalid choice. Please enter 1, 2, 3, 4, or 5.")


def handle_roll(dice_roller: DiceRoller):
    """Handle the roll dice option."""
    print("\nEnter dice notation (e.g., 3d6, 2d6+3, d20)")
    print("Format: [number]d[sides][+/-modifier]")

    while True:
        notation = input("Dice notation: ").strip()
        if not notation:
            print("Please enter a dice notation.")
            continue

        result = dice_roller.roll_with_notation(notation)

        if "error" in result:
            print(f"[X] Error: {result['error']}")
        else:
            print(f"\n[DICE] {result['display']}")
            if len(result["individual_rolls"]) > 1:
                print(f"   Individual rolls: {result['individual_rolls']}")

        break


def handle_history(dice_roller: DiceRoller):
    """Handle viewing roll history."""
    history = dice_roller.get_roll_history()

    if not history:
        print("\nNo rolls yet. Start rolling to see history!")
        return

    print(f"\n[SCROLL] ROLL HISTORY ({len(history)} rolls)")
    print("-" * 50)

    for i, roll in enumerate(history, 1):
        if "error" in roll:
            print(f"{i}. [X] {roll['notation']}: {roll['error']}")
        else:
            print(f"{i}. {roll['display']}")


def handle_statistics(dice_roller: DiceRoller):
    """Handle viewing statistics."""
    stats = dice_roller.get_statistics()

    print("\n[BAR CHART] ROLL STATISTICS")
    print("-" * 30)

    if "message" in stats:
        print(stats["message"])
    else:
        print(f"Total rolls: {stats['total_rolls']}")
        print(f"Average roll: {stats['average']:.2f}")
        print(f"Minimum roll: {stats['min']}")
        print(f"Maximum roll: {stats['max']}")
        print(f"Sum of all rolls: {stats['sum']}")


def main():
    """Main program loop."""
    dice_roller = DiceRoller()

    print("Welcome to the Dice Roller Simulator!")
    print("Roll dice using standard notation like 3d6, 2d6+3, or d20.")

    while True:
        display_menu()
        choice = get_user_choice()

        if choice == "1":
            handle_roll(dice_roller)
        elif choice == "2":
            handle_history(dice_roller)
        elif choice == "3":
            handle_statistics(dice_roller)
        elif choice == "4":
            dice_roller.clear_history()
            print("\n[TRASH]  Roll history cleared!")
        elif choice == "5":
            print("\nThanks for using the Dice Roller Simulator!")
            print("[DICE] Happy rolling! [DICE]")
            break

        # Pause before showing menu again
        if choice != "5":
            input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()

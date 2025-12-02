#!/usr/bin/env python3
"""
Password Generator

A command-line program that generates secure, random passwords with
customizable length, character classes, and advanced features.
"""

import random
import string
import math
from typing import Dict, Tuple, Optional


class PasswordGenerator:
    """Main class for generating secure passwords with various options."""

    def __init__(self):
        self.character_classes = {
            "uppercase": {
                "characters": string.ascii_uppercase,
                "description": "Uppercase letters (A-Z)",
                "enabled": True,
            },
            "lowercase": {
                "characters": string.ascii_lowercase,
                "description": "Lowercase letters (a-z)",
                "enabled": True,
            },
            "digits": {
                "characters": string.digits,
                "description": "Digits (0-9)",
                "enabled": True,
            },
            "symbols": {
                "characters": "!@#$%^&*()_+-=[]{}|;:,.<>?",
                "description": "Special symbols (!@#$%^&*...)",
                "enabled": False,
            },
        }

        self.word_list = [
            "apple",
            "banana",
            "coffee",
            "dragon",
            "elephant",
            "forest",
            "guitar",
            "horizon",
            "island",
            "jungle",
            "kitten",
            "lemon",
            "mountain",
            "nebula",
            "ocean",
            "penguin",
            "quantum",
            "rainbow",
            "sunset",
            "thunder",
            "umbrella",
            "volcano",
            "wizard",
            "xylophone",
            "yellow",
            "zebra",
            "adventure",
            "butterfly",
            "crystal",
            "diamond",
            "emerald",
            "fountain",
            "galaxy",
            "harmony",
            "infinity",
            "journey",
            "kingdom",
            "lighthouse",
            "melody",
            "northern",
            "phoenix",
            "quasar",
            "radiant",
            "serenity",
            "twilight",
            "universe",
            "victory",
            "whisper",
            "xenon",
            "yesterday",
            "zodiac",
        ]

    def validate_length(self, length_str: str) -> Tuple[bool, Optional[int], str]:
        """
        Validate password length input.

        Args:
            length_str: String input for password length

        Returns:
            Tuple of (is_valid, parsed_length, error_message)
        """
        if not length_str or not length_str.strip():
            return False, None, "Password length cannot be empty"

        try:
            length = int(length_str.strip())

            if length < 4:
                return False, None, "Password length must be at least 4 characters"
            if length > 128:
                return False, None, "Password length cannot exceed 128 characters"

            return True, length, ""

        except ValueError:
            return False, None, "Please enter a valid integer"

    def get_enabled_character_classes(self) -> Dict[str, str]:
        """
        Get all enabled character classes.

        Returns:
            Dictionary of enabled character classes
        """
        enabled = {}
        for class_name, class_info in self.character_classes.items():
            if class_info["enabled"]:
                enabled[class_name] = class_info["characters"]
        return enabled

    def validate_character_classes(self) -> Tuple[bool, str]:
        """
        Validate that at least one character class is enabled.

        Returns:
            Tuple of (is_valid, error_message)
        """
        enabled_classes = self.get_enabled_character_classes()
        if not enabled_classes:
            return False, "At least one character class must be selected"
        return True, ""

    def calculate_entropy(self, password: str) -> float:
        """
        Calculate the entropy of a password.

        Args:
            password: The password to calculate entropy for

        Returns:
            Entropy value in bits
        """
        if not password:
            return 0.0

        # Determine character set size
        char_set_size = 0
        if any(c in string.ascii_lowercase for c in password):
            char_set_size += 26
        if any(c in string.ascii_uppercase for c in password):
            char_set_size += 26
        if any(c in string.digits for c in password):
            char_set_size += 10
        if any(c in self.character_classes["symbols"]["characters"] for c in password):
            char_set_size += len(self.character_classes["symbols"]["characters"])

        # Calculate entropy: log2(char_set_size^length)
        if char_set_size == 0:
            return 0.0

        entropy = len(password) * math.log2(char_set_size)
        return round(entropy, 2)

    def assess_password_strength(self, password: str) -> Dict[str, any]:
        """
        Assess the strength of a password.

        Args:
            password: The password to assess

        Returns:
            Dictionary with strength assessment
        """
        entropy = self.calculate_entropy(password)

        if entropy < 40:
            strength = "Very Weak"
            color_code = "\033[91m"  # Red
        elif entropy < 60:
            strength = "Weak"
            color_code = "\033[93m"  # Yellow
        elif entropy < 80:
            strength = "Moderate"
            color_code = "\033[93m"  # Yellow
        elif entropy < 100:
            strength = "Strong"
            color_code = "\033[92m"  # Green
        else:
            strength = "Very Strong"
            color_code = "\033[92m"  # Green

        return {
            "entropy": entropy,
            "strength": strength,
            "color_code": color_code,
            "length": len(password),
            "has_uppercase": any(c in string.ascii_uppercase for c in password),
            "has_lowercase": any(c in string.ascii_lowercase for c in password),
            "has_digits": any(c in string.digits for c in password),
            "has_symbols": any(
                c in self.character_classes["symbols"]["characters"] for c in password
            ),
        }

    def generate_password(self, length: int, ensure_all_classes: bool = True) -> str:
        """
        Generate a random password.

        Args:
            length: Desired password length
            ensure_all_classes: Whether to ensure at least one character from each enabled class

        Returns:
            Generated password string
        """
        enabled_classes = self.get_enabled_character_classes()

        if not enabled_classes:
            raise ValueError("No character classes enabled")

        # Build character pool
        char_pool = ""
        for chars in enabled_classes.values():
            char_pool += chars

        # Generate password
        password = []

        if ensure_all_classes and len(enabled_classes) <= length:
            # Ensure at least one character from each enabled class
            for class_chars in enabled_classes.values():
                password.append(random.choice(class_chars))

            # Fill remaining positions
            remaining_length = length - len(password)
            for _ in range(remaining_length):
                password.append(random.choice(char_pool))
        else:
            # Generate completely random password
            for _ in range(length):
                password.append(random.choice(char_pool))

        # Shuffle to avoid predictable patterns
        random.shuffle(password)

        return "".join(password)

    def generate_passphrase(
        self,
        word_count: int = 4,
        separator: str = "-",
        capitalize: bool = True,
        include_number: bool = True,
    ) -> str:
        """
        Generate a memorable passphrase.

        Args:
            word_count: Number of words in the passphrase
            separator: Separator between words
            capitalize: Whether to capitalize the first letter of each word
            include_number: Whether to include a random number

        Returns:
            Generated passphrase string
        """
        if word_count < 2:
            word_count = 2
        if word_count > 10:
            word_count = 10

        # Select random words
        words = random.sample(self.word_list, min(word_count, len(self.word_list)))

        # Process words
        if capitalize:
            words = [word.capitalize() for word in words]

        # Create passphrase
        passphrase = separator.join(words)

        # Add number if requested
        if include_number:
            passphrase += str(random.randint(0, 999))

        return passphrase

    def copy_to_clipboard(self, text: str) -> bool:
        """
        Copy text to clipboard (platform-dependent).

        Args:
            text: Text to copy to clipboard

        Returns:
            True if successful, False otherwise
        """
        try:
            import subprocess
            import platform

            system = platform.system()

            if system == "Darwin":  # macOS
                subprocess.run(["pbcopy"], input=text, text=True, check=True)
            elif system == "Windows":
                subprocess.run(["clip"], input=text, text=True, check=True)
            elif system == "Linux":
                # Try xclip first, then xsel
                try:
                    subprocess.run(
                        ["xclip", "-selection", "clipboard"],
                        input=text,
                        text=True,
                        check=True,
                    )
                except (subprocess.CalledProcessError, FileNotFoundError):
                    try:
                        subprocess.run(
                            ["xsel", "--clipboard", "--input"],
                            input=text,
                            text=True,
                            check=True,
                        )
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        return False
            else:
                return False

            return True

        except Exception:
            return False


def display_menu():
    """Display the main menu options."""
    print("\n" + "=" * 60)
    print("[LOCK] PASSWORD GENERATOR [LOCK]")
    print("=" * 60)
    print("1. Generate password")
    print("2. Generate passphrase")
    print("3. Configure character classes")
    print("4. Password strength analyzer")
    print("5. Copy to clipboard")
    print("6. Exit")
    print("=" * 60)


def get_user_choice() -> str:
    """Get and validate user menu choice."""
    while True:
        choice = input("\nEnter your choice (1-6): ").strip()
        if choice in ["1", "2", "3", "4", "5", "6"]:
            return choice
        print("Invalid choice. Please enter 1, 2, 3, 4, 5, or 6.")


def handle_generate_password(generator: PasswordGenerator):
    """Handle password generation."""
    print("\n" + "=" * 40)
    print("[KEY] PASSWORD GENERATION")
    print("=" * 40)

    # Get password length
    while True:
        length_input = input("Enter password length (4-128): ").strip()
        is_valid, length, error = generator.validate_length(length_input)
        if is_valid:
            break
        print(f"[X] {error}")

    # Ask about ensuring all character classes
    ensure_classes = (
        input("Ensure at least one character from each class? (y/n): ").strip().lower()
    )
    ensure_classes = ensure_classes.startswith("y")

    try:
        password = generator.generate_password(length, ensure_classes)
        assessment = generator.assess_password_strength(password)

        print("\n[KEY] Generated Password:")
        print(f"   {assessment['color_code']}{password}\033[0m")
        print("\n[BAR CHART] Password Analysis:")
        print(f"   Length: {assessment['length']} characters")
        print(f"   Entropy: {assessment['entropy']} bits")
        print(f"   Strength: {assessment['color_code']}{assessment['strength']}\033[0m")
        print("   Contains:")
        print(f"     Uppercase: {'[OK]' if assessment['has_uppercase'] else '[X]'}")
        print(f"     Lowercase: {'[OK]' if assessment['has_lowercase'] else '[X]'}")
        print(f"     Digits: {'[OK]' if assessment['has_digits'] else '[X]'}")
        print(f"     Symbols: {'[OK]' if assessment['has_symbols'] else '[X]'}")

    except ValueError as e:
        print(f"\n[X] Error: {e}")


def handle_generate_passphrase(generator: PasswordGenerator):
    """Handle passphrase generation."""
    print("\n" + "=" * 40)
    print("[MEMO] PASSPHRASE GENERATION")
    print("=" * 40)

    # Get word count
    while True:
        word_input = input("Enter number of words (2-10): ").strip()
        try:
            word_count = int(word_input)
            if 2 <= word_count <= 10:
                break
            print("[X] Please enter a number between 2 and 10")
        except ValueError:
            print("[X] Please enter a valid integer")

    # Get separator
    separator = input("Enter separator (default: -): ").strip()
    if not separator:
        separator = "-"

    # Get options
    capitalize = input("Capitalize words? (y/n): ").strip().lower().startswith("y")
    include_number = (
        input("Include random number? (y/n): ").strip().lower().startswith("y")
    )

    passphrase = generator.generate_passphrase(
        word_count, separator, capitalize, include_number
    )
    assessment = generator.assess_password_strength(passphrase)

    print("\n[MEMO] Generated Passphrase:")
    print(f"   {assessment['color_code']}{passphrase}\033[0m")
    print("\n[BAR CHART] Passphrase Analysis:")
    print(f"   Length: {assessment['length']} characters")
    print(f"   Entropy: {assessment['entropy']} bits")
    print(f"   Strength: {assessment['color_code']}{assessment['strength']}\033[0m")


def handle_configure_classes(generator: PasswordGenerator):
    """Handle character class configuration."""
    print("\n" + "=" * 40)
    print("[GEAR]  CHARACTER CLASS CONFIGURATION")
    print("=" * 40)

    for class_name, class_info in generator.character_classes.items():
        status = "[OK] Enabled" if class_info["enabled"] else "[X] Disabled"
        print(f"{class_name.title()}: {status}")
        print(f"   {class_info['description']}")
        print()

    print("Toggle character classes (enter class name, or 'done' to finish):")

    while True:
        choice = input("Class to toggle: ").strip().lower()

        if choice == "done":
            break

        if choice in generator.character_classes:
            generator.character_classes[choice]["enabled"] = (
                not generator.character_classes[choice]["enabled"]
            )
            status = (
                "enabled"
                if generator.character_classes[choice]["enabled"]
                else "disabled"
            )
            print(f"[OK] {choice.title()} {status}")
        else:
            print(
                "[X] Invalid class name. Available: uppercase, lowercase, digits, symbols"
            )

    # Validate configuration
    is_valid, error = generator.validate_character_classes()
    if not is_valid:
        print(f"\nWARNING  Warning: {error}")
        # Enable lowercase by default
        generator.character_classes["lowercase"]["enabled"] = True
        print("[OK] Enabled lowercase by default")


def handle_strength_analyzer(generator: PasswordGenerator):
    """Handle password strength analysis."""
    print("\n" + "=" * 40)
    print("[SEARCH] PASSWORD STRENGTH ANALYZER")
    print("=" * 40)

    password = input("Enter password to analyze: ").strip()

    if not password:
        print("[X] Password cannot be empty")
        return

    assessment = generator.assess_password_strength(password)

    print("\n[SEARCH] Password Analysis:")
    print(f"   Password: {password}")
    print(f"   Length: {assessment['length']} characters")
    print(f"   Entropy: {assessment['entropy']} bits")
    print(f"   Strength: {assessment['color_code']}{assessment['strength']}\033[0m")
    print("\n[SEARCH] Character Analysis:")
    print(f"   Uppercase letters: {'[OK]' if assessment['has_uppercase'] else '[X]'}")
    print(f"   Lowercase letters: {'[OK]' if assessment['has_lowercase'] else '[X]'}")
    print(f"   Digits: {'[OK]' if assessment['has_digits'] else '[X]'}")
    print(f"   Special symbols: {'[OK]' if assessment['has_symbols'] else '[X]'}")

    # Recommendations
    print("\n[LIGHTBULB] Recommendations:")
    if assessment["length"] < 12:
        print("   • Use at least 12 characters for better security")
    if not assessment["has_uppercase"]:
        print("   • Add uppercase letters for more complexity")
    if not assessment["has_lowercase"]:
        print("   • Add lowercase letters for more complexity")
    if not assessment["has_digits"]:
        print("   • Add numbers for more complexity")
    if not assessment["has_symbols"]:
        print("   • Add special symbols for maximum security")
    if assessment["entropy"] < 60:
        print("   • Consider using a longer password or passphrase")


def handle_copy_to_clipboard(generator: PasswordGenerator):
    """Handle copying to clipboard."""
    print("\n" + "=" * 40)
    print("[CLIPBOARD] COPY TO CLIPBOARD")
    print("=" * 40)

    text = input(
        "Enter text to copy (or press Enter for last generated password): "
    ).strip()

    if not text:
        print("[X] No text provided")
        return

    if generator.copy_to_clipboard(text):
        print("[OK] Text copied to clipboard successfully")
    else:
        print("[X] Failed to copy to clipboard")
        print("   This feature may not be available on your system")
        print("   You can manually copy the text instead")


def main():
    """Main program loop."""
    generator = PasswordGenerator()

    print("Welcome to the Password Generator!")
    print("Generate secure passwords and passphrases with ease.")

    while True:
        display_menu()
        choice = get_user_choice()

        if choice == "1":
            handle_generate_password(generator)
        elif choice == "2":
            handle_generate_passphrase(generator)
        elif choice == "3":
            handle_configure_classes(generator)
        elif choice == "4":
            handle_strength_analyzer(generator)
        elif choice == "5":
            handle_copy_to_clipboard(generator)
        elif choice == "6":
            print("\nThanks for using the Password Generator!")
            print("[LOCK] Stay secure! [LOCK]")
            break

        # Pause before showing menu again
        if choice != "6":
            input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()

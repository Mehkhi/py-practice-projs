#!/usr/bin/env python3

import re
from collections import Counter


def normalize_string(text):
    """Normalize string by removing spaces, punctuation, and converting to lowercase."""
    if not isinstance(text, str):
        return ""

    # Remove all non-alphanumeric characters and convert to lowercase
    normalized = re.sub(r'[^a-zA-Z0-9]', '', text.lower())
    return normalized


def is_palindrome(text):
    """Check if a string is a palindrome."""
    normalized = normalize_string(text)
    return normalized == normalized[::-1]


def are_anagrams(str1, str2):
    """Check if two strings are anagrams using character counting."""
    norm1 = normalize_string(str1)
    norm2 = normalize_string(str2)

    # If lengths are different, they can't be anagrams
    if len(norm1) != len(norm2):
        return False

    # Compare character counts
    return Counter(norm1) == Counter(norm2)


def get_user_input(prompt):
    """Get and validate user input."""
    while True:
        try:
            user_input = input(prompt).strip()
            if user_input:
                return user_input
            else:
                print("Please enter some text.")
        except KeyboardInterrupt:
            print("\nGoodbye!")
            exit()
        except EOFError:
            print("\nGoodbye!")
            exit()


def palindrome_checker():
    """Interactive palindrome checker."""
    print("\n=== Palindrome Checker ===")
    text = get_user_input("Enter text to check if it's a palindrome: ")

    if is_palindrome(text):
        print(f"[OK] '{text}' is a palindrome!")
    else:
        print(f"[X] '{text}' is not a palindrome.")


def anagram_checker():
    """Interactive anagram checker."""
    print("\n=== Anagram Checker ===")
    str1 = get_user_input("Enter first string: ")
    str2 = get_user_input("Enter second string: ")

    if are_anagrams(str1, str2):
        print(f"[OK] '{str1}' and '{str2}' are anagrams!")
    else:
        print(f"[X] '{str1}' and '{str2}' are not anagrams.")


def batch_file_checker():
    """Check palindromes and anagrams from a file."""
    print("\n=== Batch File Checker ===")
    filename = get_user_input("Enter filename to process: ")

    try:
        with open(filename, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        print(f"\nProcessing {len(lines)} lines from {filename}:")
        print("-" * 50)

        for i, line in enumerate(lines, 1):
            line = line.strip()
            if line:
                if is_palindrome(line):
                    print(f"Line {i}: '{line}' → PALINDROME")
                else:
                    print(f"Line {i}: '{line}' → Not a palindrome")

    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
    except Exception as e:
        print(f"Error reading file: {e}")


def display_menu():
    """Display the main menu."""
    print("\n" + "="*40)
    print("Palindrome & Anagram Checker")
    print("="*40)
    print("1. Check if text is a palindrome")
    print("2. Check if two strings are anagrams")
    print("3. Batch process file for palindromes")
    print("4. Exit")
    print("="*40)


def main():
    """Main function to run the palindrome and anagram checker."""
    while True:
        display_menu()

        try:
            choice = input("Enter your choice (1-4): ").strip()

            if choice == '1':
                palindrome_checker()
            elif choice == '2':
                anagram_checker()
            elif choice == '3':
                batch_file_checker()
            elif choice == '4':
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please enter 1, 2, 3, or 4.")

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except EOFError:
            print("\nGoodbye!")
            break


if __name__ == "__main__":
    main()

#!/usr/bin/env python3

import re
import sys
from collections import Counter
from typing import Dict, List, Tuple


class WordCounter:
    """A text analysis tool for counting words, lines, characters, and more."""

    # Common English stop words
    STOP_WORDS = {
        'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
        'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
        'to', 'was', 'were', 'will', 'with', 'i', 'you', 'your', 'we',
        'they', 'them', 'their', 'this', 'these', 'those', 'have', 'had',
        'but', 'not', 'or', 'if', 'than', 'then', 'now', 'so', 'my', 'me'
    }

    def __init__(self):
        self.text = ""
        self.filename = ""

    def read_file(self, filename: str) -> bool:
        """Read text from a file."""
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                self.text = file.read()
            self.filename = filename
            return True
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found.")
            return False
        except UnicodeDecodeError:
            print(f"Error: Could not decode file '{filename}' as text.")
            return False
        except Exception as e:
            print(f"Error reading file '{filename}': {e}")
            return False

    def set_text(self, text: str):
        """Set text directly."""
        self.text = text
        self.filename = ""

    def count_characters(self) -> int:
        """Count total characters including spaces."""
        return len(self.text)

    def count_characters_no_spaces(self) -> int:
        """Count characters excluding spaces."""
        return len(self.text.replace(' ', ''))

    def count_words(self) -> int:
        """Count words in the text."""
        if not self.text.strip():
            return 0

        # Split by whitespace and filter out empty strings
        words = re.findall(r'\b\w+\b', self.text.lower())
        return len(words)

    def count_lines(self) -> int:
        """Count lines in the text."""
        if not self.text:
            return 0

        # Split by lines and filter out empty strings
        lines = [line for line in self.text.split('\n') if line.strip()]
        return len(lines)

    def count_paragraphs(self) -> int:
        """Count paragraphs (separated by blank lines)."""
        if not self.text.strip():
            return 0

        # Split by double newlines and filter out empty strings
        paragraphs = [p for p in self.text.split('\n\n') if p.strip()]
        return len(paragraphs)

    def get_word_frequency(self, exclude_stop_words: bool = False) -> Counter:
        """Get word frequency dictionary."""
        if not self.text.strip():
            return Counter()

        # Find all words and convert to lowercase
        words = re.findall(r'\b\w+\b', self.text.lower())

        if exclude_stop_words:
            words = [word for word in words if word not in self.STOP_WORDS]

        return Counter(words)

    def get_most_common_words(self, n: int = 10, exclude_stop_words: bool = False) -> List[Tuple[str, int]]:
        """Get the N most common words."""
        word_freq = self.get_word_frequency(exclude_stop_words)
        return word_freq.most_common(n)

    def get_average_word_length(self) -> float:
        """Calculate average word length."""
        words = re.findall(r'\b\w+\b', self.text)
        if not words:
            return 0.0

        total_length = sum(len(word) for word in words)
        return total_length / len(words)

    def get_reading_time(self, wpm: int = 200) -> float:
        """Estimate reading time in minutes."""
        word_count = self.count_words()
        return word_count / wpm

    def get_statistics(self) -> Dict:
        """Get comprehensive text statistics."""
        return {
            'filename': self.filename or 'Direct Input',
            'characters': self.count_characters(),
            'characters_no_spaces': self.count_characters_no_spaces(),
            'words': self.count_words(),
            'lines': self.count_lines(),
            'paragraphs': self.count_paragraphs(),
            'average_word_length': round(self.get_average_word_length(), 2),
            'reading_time_minutes': round(self.get_reading_time(), 2),
            'unique_words': len(self.get_word_frequency()),
        }

    def analyze_text(self, top_words: int = 10, exclude_stop_words: bool = False) -> Dict:
        """Perform complete text analysis."""
        stats = self.get_statistics()
        most_common = self.get_most_common_words(top_words, exclude_stop_words)

        return {
            'statistics': stats,
            'most_common_words': most_common,
            'word_frequency': dict(self.get_word_frequency(exclude_stop_words))
        }


def display_statistics(stats: Dict):
    """Display text statistics in a formatted way."""
    print("\n" + "="*50)
    print("[BAR CHART] TEXT STATISTICS")
    print("="*50)
    print(f"File: {stats['filename']}")
    print(f"Characters:       {stats['characters']:,}")
    print(f"Characters (no spaces): {stats['characters_no_spaces']:,}")
    print(f"Words:            {stats['words']:,}")
    print(f"Lines:            {stats['lines']:,}")
    print(f"Paragraphs:       {stats['paragraphs']:,}")
    print(f"Unique words:     {stats['unique_words']:,}")
    print(f"Avg word length:  {stats['average_word_length']} characters")
    print(f"Reading time:     {stats['reading_time_minutes']} minutes")
    print("="*50)


def display_most_common(words: List[Tuple[str, int]], title: str = "Most Common Words"):
    """Display most common words."""
    if not words:
        print(f"\nNo {title.lower()} found.")
        return

    print(f"\n{title.upper()}")
    print("-" * 30)

    for i, (word, count) in enumerate(words, 1):
        print(f"{i:2d}. {word:<15} {count:>5} occurrences")

    print("-" * 30)


def get_user_input(prompt: str, allow_empty: bool = False) -> str:
    """Get and validate user input."""
    while True:
        try:
            user_input = input(prompt).strip()
            if user_input or allow_empty:
                return user_input
            else:
                print("Please enter some text.")
        except KeyboardInterrupt:
            print("\nGoodbye!")
            exit()
        except EOFError:
            print("\nGoodbye!")
            exit()


def analyze_file_menu(counter: WordCounter):
    """Handle file analysis."""
    print("\n=== Analyze File ===")
    filename = get_user_input("Enter filename: ")

    if counter.read_file(filename):
        analysis = counter.analyze_text()

        # Display statistics
        display_statistics(analysis['statistics'])

        # Display most common words
        display_most_common(analysis['most_common_words'])

        # Ask if user wants to exclude stop words
        choice = input("\nAnalyze without stop words? (y/n): ").strip().lower()
        if choice in ['y', 'yes']:
            most_common_no_stop = counter.get_most_common_words(10, exclude_stop_words=True)
            display_most_common(most_common_no_stop, "Most Common Words (No Stop Words)")
    else:
        print("Failed to analyze file.")


def analyze_text_menu(counter: WordCounter):
    """Handle direct text input analysis."""
    print("\n=== Analyze Text ===")
    print("Enter your text (press Enter twice to finish):")

    lines = []
    while True:
        try:
            line = input()
            if line == "" and len(lines) > 0 and lines[-1] == "":
                break
            lines.append(line)
        except KeyboardInterrupt:
            print("\nGoodbye!")
            exit()
        except EOFError:
            break

    text = "\n".join(lines).strip()
    if text:
        counter.set_text(text)
        analysis = counter.analyze_text()

        # Display statistics
        display_statistics(analysis['statistics'])

        # Display most common words
        display_most_common(analysis['most_common_words'])
    else:
        print("No text provided.")


def compare_files_menu(counter: WordCounter):
    """Handle comparing multiple files."""
    print("\n=== Compare Files ===")

    filenames = []
    while len(filenames) < 2:
        filename = get_user_input(f"Enter filename {len(filenames) + 1} (or 'done' to finish): ")
        if filename.lower() == 'done':
            if len(filenames) >= 2:
                break
            else:
                print("Please enter at least 2 files to compare.")
                continue

        if counter.read_file(filename):
            filenames.append(filename)
            stats = counter.get_statistics()
            print(f"[OK] Added: {stats['words']:,} words, {stats['lines']:,} lines")
        else:
            print("[X] Failed to read file.")

    if len(filenames) >= 2:
        print(f"\n{'File':<20} {'Words':<10} {'Lines':<10} {'Characters':<12}")
        print("-" * 55)

        for filename in filenames:
            if counter.read_file(filename):
                stats = counter.get_statistics()
                print(f"{filename:<20} {stats['words']:<10,} {stats['lines']:<10,} {stats['characters']:<12,}")


def display_menu():
    """Display the main menu."""
    print("\n" + "="*40)
    print("[MEMO] WORD COUNT TOOL")
    print("="*40)
    print("1. Analyze file")
    print("2. Analyze text input")
    print("3. Compare files")
    print("4. Exit")
    print("="*40)


def main():
    """Main function to run the word count tool."""
    counter = WordCounter()

    # Handle command line arguments
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        if counter.read_file(filename):
            analysis = counter.analyze_text()
            display_statistics(analysis['statistics'])
            display_most_common(analysis['most_common_words'])
        return

    print("Welcome to the Word Count Tool!")

    while True:
        display_menu()

        try:
            choice = input("Enter your choice (1-4): ").strip()

            if choice == '1':
                analyze_file_menu(counter)
            elif choice == '2':
                analyze_text_menu(counter)
            elif choice == '3':
                compare_files_menu(counter)
            elif choice == '4':
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please enter 1-4.")

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except EOFError:
            print("\nGoodbye!")
            break


if __name__ == "__main__":
    main()

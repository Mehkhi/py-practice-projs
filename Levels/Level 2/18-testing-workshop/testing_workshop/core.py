"""Core text analysis functionality for the Testing Workshop CLI tool."""

import re
from collections import Counter
from typing import Dict, List, Tuple


def count_words(text: str) -> int:
    """Count the number of words in the given text.

    Args:
        text: The text to analyze.

    Returns:
        The number of words in the text.
    """
    if not text:
        return 0
    words = re.findall(r"\b\w+\b", text)
    return len(words)


def count_characters(text: str, include_spaces: bool = True) -> int:
    """Count the number of characters in the given text.

    Args:
        text: The text to analyze.
        include_spaces: Whether to include spaces in the count.

    Returns:
        The number of characters in the text.
    """
    if not text:
        return 0
    if include_spaces:
        return len(text)
    return len(text.replace(" ", "").replace("\n", "").replace("\t", ""))


def get_most_frequent_words(text: str, n: int = 5) -> List[Tuple[str, int]]:
    """Get the most frequent words in the text.

    Args:
        text: The text to analyze.
        n: Number of top words to return.

    Returns:
        List of tuples containing (word, frequency) pairs.
    """
    if not text:
        return []
    words = re.findall(r"\b\w+\b", text.lower())
    word_counts = Counter(words)
    return word_counts.most_common(n)


def estimate_reading_time(text: str, words_per_minute: int = 200) -> float:
    """Estimate reading time for the text in minutes.

    Args:
        text: The text to analyze.
        words_per_minute: Average reading speed.

    Returns:
        Estimated reading time in minutes.
    """
    word_count = count_words(text)
    if word_count == 0:
        return 0.0
    return word_count / words_per_minute


def analyze_text(text: str) -> Dict[str, any]:
    """Perform comprehensive text analysis.

    Args:
        text: The text to analyze.

    Returns:
        Dictionary containing various text statistics.
    """
    return {
        "word_count": count_words(text),
        "character_count_with_spaces": count_characters(text, include_spaces=True),
        "character_count_no_spaces": count_characters(text, include_spaces=False),
        "most_frequent_words": get_most_frequent_words(text),
        "estimated_reading_time": estimate_reading_time(text),
        "line_count": text.count("\n") + 1 if text else 0,
    }


def read_file_content(file_path: str) -> str:
    """Read content from a file.

    Args:
        file_path: Path to the file to read.

    Returns:
        The content of the file as a string.

    Raises:
        FileNotFoundError: If the file does not exist.
        IOError: If there's an error reading the file.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")
    except IOError as e:
        raise IOError(f"Error reading file {file_path}: {e}")

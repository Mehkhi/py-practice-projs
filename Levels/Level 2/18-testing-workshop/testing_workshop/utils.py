"""Utility functions for the Testing Workshop CLI tool."""

import os
from typing import Any, Dict


def format_analysis_results(results: Dict[str, Any]) -> str:
    """Format text analysis results for display.

    Args:
        results: Dictionary containing analysis results.

    Returns:
        Formatted string representation of the results.
    """
    output = []
    output.append("Text Analysis Results:")
    output.append("-" * 30)
    output.append(f"Word count: {results['word_count']}")
    output.append(f"Characters (with spaces): {results['character_count_with_spaces']}")
    output.append(f"Characters (no spaces): {results['character_count_no_spaces']}")
    output.append(f"Line count: {results['line_count']}")
    reading_time = results.get("estimated_reading_time", 0.0)
    output.append(f"Estimated reading time: {reading_time:.1f} minutes")

    if results["most_frequent_words"]:
        output.append("\nMost frequent words:")
        for word, count in results["most_frequent_words"]:
            output.append(f"  {word}: {count}")

    return "\n".join(output)


def validate_file_path(file_path: str) -> bool:
    """Validate if a file path exists and is readable.

    Args:
        file_path: Path to validate.

    Returns:
        True if file exists and is readable, False otherwise.
    """
    return os.path.isfile(file_path) and os.access(file_path, os.R_OK)


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to a maximum length with ellipsis.

    Args:
        text: Text to truncate.
        max_length: Maximum length of the truncated text.

    Returns:
        Truncated text with ellipsis if needed.
    """
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."


def safe_int_conversion(value: str, default: int = 0) -> int:
    """Safely convert a string to integer with a default value.

    Args:
        value: String value to convert.
        default: Default value if conversion fails.

    Returns:
        Integer value or default.
    """
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

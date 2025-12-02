"""Shared ending evaluation logic for determining game endings based on world flags."""

import os
from typing import Any, Dict, List, Optional, TYPE_CHECKING, Union

from .data_loader import load_json_file
from .logging_utils import log_warning

if TYPE_CHECKING:
    from .world import World


def load_endings_data(data_dir: str = "data") -> Optional[List[Dict[str, Any]]]:
    """
    Load endings data from JSON file.

    Args:
        data_dir: Directory containing the endings.json file (default: "data")

    Returns:
        List of ending dictionaries, or None if loading fails
    """
    path = os.path.join(data_dir, "endings.json")
    if not os.path.exists(path):
        return None
    try:
        data = load_json_file(path, {})
        return data.get("endings", [])
    except Exception as e:
        log_warning(f"Failed to load endings data from {path}: {e}")
        return None


def evaluate_condition(condition: Union[str, Dict[str, Any]], world: "World") -> bool:
    """
    Evaluate a nested condition (AND/OR/NOT) against world flags.

    Args:
        condition: Condition to evaluate. Can be:
            - None - returns True (no condition = always matches)
            - A string (flag name) - checks if flag is truthy
            - A dict with "and" key - all subconditions must be true
            - A dict with "or" key - at least one subcondition must be true
              (returns False if the list is empty)
            - A dict with "not" key - subcondition must be false
        world: World object with get_flag() method

    Returns:
        True if condition is met, False otherwise
    """
    # None means no condition required - always matches
    if condition is None:
        return True

    # Empty string or empty dict means no valid condition - no match
    if not condition:
        return False

    # Simple string condition - check if flag is truthy
    if isinstance(condition, str):
        return bool(world.get_flag(condition))

    # AND condition - all subconditions must be true
    # Returns True if the list is empty (vacuous truth)
    if isinstance(condition, dict) and "and" in condition:
        for subcondition in condition["and"]:
            if not evaluate_condition(subcondition, world):
                return False
        return True

    # OR condition - at least one subcondition must be true
    # Returns False if the list is empty (no conditions to satisfy)
    if isinstance(condition, dict) and "or" in condition:
        for subcondition in condition["or"]:
            if evaluate_condition(subcondition, world):
                return True
        return False

    # NOT condition - subcondition must be false
    if isinstance(condition, dict) and "not" in condition:
        return not evaluate_condition(condition["not"], world)

    return False


def determine_ending(
    world: "World",
    endings_data: Optional[List[Dict[str, Any]]] = None,
    data_dir: str = "data",
) -> str:
    """
    Determine which ending to show based on world flags using data-driven conditions.

    Args:
        world: World object with get_flag() method
        endings_data: Optional pre-loaded endings data. If None, will load from data_dir
        data_dir: Directory containing endings.json (used if endings_data is None)

    Returns:
        Ending ID string (e.g., "good", "bad", "neutral")
    """
    # Load endings data if not provided
    if endings_data is None:
        endings_data = load_endings_data(data_dir)

    if not endings_data:
        return "neutral"  # Fallback if data loading fails

    # Sort a copy to avoid mutating caller's data
    # Lower priority number = higher precedence
    sorted_endings = sorted(endings_data, key=lambda x: x.get("priority", 999))

    # Find the highest priority ending that matches its conditions
    for ending in sorted_endings:
        conditions = ending.get("conditions")
        if evaluate_condition(conditions, world):
            return ending.get("id", "neutral")

    return "neutral"  # Fallback if no conditions match

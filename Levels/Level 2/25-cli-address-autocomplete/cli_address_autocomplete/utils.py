"""Utility functions for address autocomplete."""

import re


def normalize_address(address: str) -> str:
    """Normalize address string for better matching."""
    # Remove extra spaces, lowercase, etc.
    return re.sub(r'\s+', ' ', address.strip().lower())


def validate_query(query: str) -> bool:
    """Validate search query."""
    return len(query.strip()) >= 3

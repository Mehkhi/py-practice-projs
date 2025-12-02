"""Utility functions for password strength checker."""

import re
from typing import List


def normalize_password(password: str) -> str:
    """Normalize password for consistent processing.

    Args:
        password: Raw password string

    Returns:
        Normalized password string
    """
    return password.strip()


def validate_password_input(password: str) -> List[str]:
    """Validate password input for basic requirements.

    Args:
        password: Password to validate

    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []

    if not password:
        errors.append("Password cannot be empty")
        return errors

    if len(password) > 128:
        errors.append("Password is too long (maximum 128 characters)")

    # Check for control characters
    if re.search(r'[\x00-\x1f\x7f-\x9f]', password):
        errors.append("Password contains invalid control characters")

    return errors

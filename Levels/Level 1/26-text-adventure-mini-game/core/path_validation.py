"""Path validation utilities to prevent path traversal attacks and ensure security.

This module provides functions to validate and sanitize file paths before use,
preventing directory traversal attacks and ensuring paths stay within allowed
directories.
"""

import os
from typing import Optional


def validate_path_inside_base(
    path: str,
    base_dir: str,
    allow_absolute: bool = False
) -> tuple[bool, Optional[str]]:
    """
    Validate that a path stays within a base directory (prevents path traversal).

    Args:
        path: The path to validate (can be relative or absolute)
        base_dir: The base directory that the path must stay within
        allow_absolute: If True, allow absolute paths (still validated against base_dir)

    Returns:
        Tuple of (is_valid, resolved_path)
        - is_valid: True if path is safe, False if it escapes base_dir
        - resolved_path: The resolved absolute path if valid, None if invalid

    Examples:
        >>> validate_path_inside_base("save_1.json", "/game/saves", allow_absolute=False)
        (True, "/game/saves/save_1.json")

        >>> validate_path_inside_base("../../../etc/passwd", "/game/saves", allow_absolute=False)
        (False, None)

        >>> validate_path_inside_base("/game/saves/save_1.json", "/game/saves", allow_absolute=True)
        (True, "/game/saves/save_1.json")
    """
    if not path:
        return False, None

    # Resolve base directory to absolute path
    # Use realpath to resolve symlinks, but handle nonexistent directories
    try:
        if os.path.exists(base_dir):
            base_abs = os.path.abspath(os.path.realpath(base_dir))
        else:
            # Base doesn't exist, but we can still validate the path structure
            base_abs = os.path.abspath(base_dir)
    except (OSError, ValueError):
        return False, None

    # Handle relative paths
    if not os.path.isabs(path):
        # Join with base directory and normalize
        try:
            joined = os.path.join(base_abs, path)
            resolved = os.path.abspath(joined)
            # Normalize to remove any '..' sequences
            resolved = os.path.normpath(resolved)
            # Convert back to absolute after normalization
            resolved = os.path.abspath(resolved)
        except (OSError, ValueError):
            return False, None
    else:
        # Absolute path provided
        if not allow_absolute:
            return False, None
        try:
            if os.path.exists(path):
                resolved = os.path.abspath(os.path.realpath(path))
            else:
                resolved = os.path.abspath(os.path.normpath(path))
        except (OSError, ValueError):
            return False, None

    # Ensure resolved path is within base directory
    # Use os.path.commonpath to check if base is a prefix
    try:
        # Normalize both paths for comparison
        base_normalized = os.path.normpath(base_abs)
        resolved_normalized = os.path.normpath(resolved)

        # Check if resolved path starts with base path
        # On Windows, also check case-insensitively
        if os.name == 'nt':
            is_valid = resolved_normalized.lower().startswith(base_normalized.lower())
        else:
            is_valid = resolved_normalized.startswith(base_normalized)

        # Also verify using commonpath (more robust)
        try:
            common_path = os.path.commonpath([base_normalized, resolved_normalized])
            is_valid = is_valid and (os.path.normpath(common_path) == base_normalized)
        except (OSError, ValueError):
            # commonpath can fail on Windows with different drives
            pass
    except (OSError, ValueError):
        # If validation fails, reject the path
        is_valid = False

    if not is_valid:
        return False, None

    return True, resolved


def sanitize_filename(filename: str, max_length: int = 255) -> Optional[str]:
    """
    Sanitize a filename by removing dangerous characters and limiting length.

    Args:
        filename: The filename to sanitize
        max_length: Maximum allowed filename length (default 255, common filesystem limit)

    Returns:
        Sanitized filename or None if filename is invalid

    Examples:
        >>> sanitize_filename("save_1.json")
        'save_1.json'

        >>> sanitize_filename("../../../etc/passwd")
        'etc_passwd'

        >>> sanitize_filename("file" + "x" * 300)
        None  # Too long
    """
    if not filename:
        return None

    # Remove path separators and dangerous characters
    # Replace '..' first to handle path traversal sequences
    sanitized = filename.replace('..', '_')
    sanitized = sanitized.replace('/', '_')
    sanitized = sanitized.replace('\\', '_')
    sanitized = sanitized.replace('\x00', '_')

    # Collapse multiple consecutive underscores
    while '__' in sanitized:
        sanitized = sanitized.replace('__', '_')

    # Remove leading/trailing dots, spaces, and underscores
    sanitized = sanitized.strip('. _')

    if not sanitized:
        return None

    # Limit length
    if len(sanitized) > max_length:
        return None

    # Check for reserved names on Windows
    reserved_names = {
        'CON', 'PRN', 'AUX', 'NUL',
        'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
        'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
    }
    name_upper = sanitized.upper().split('.')[0]  # Check base name without extension
    if name_upper in reserved_names:
        return None

    return sanitized


def validate_save_slot(slot: int) -> tuple[bool, Optional[str]]:
    """
    Validate a save slot number and generate safe filename.

    Args:
        slot: Save slot number (1-based)

    Returns:
        Tuple of (is_valid, filename)
        - is_valid: True if slot is valid
        - filename: Safe filename like "save_1.json" or None if invalid

    Examples:
        >>> validate_save_slot(1)
        (True, 'save_1.json')

        >>> validate_save_slot(0)
        (False, None)

        >>> validate_save_slot(-1)
        (False, None)
    """
    if not isinstance(slot, int) or slot < 1 or slot > 999:
        return False, None

    filename = f"save_{slot}.json"
    sanitized = sanitize_filename(filename)
    if sanitized != filename:  # Sanitization changed the filename
        return False, None

    return True, sanitized


def ensure_directory_exists(path: str, create_if_missing: bool = True) -> tuple[bool, Optional[str]]:
    """
    Ensure a directory exists, optionally creating it if missing.

    Args:
        path: Directory path to check/create
        create_if_missing: If True, create directory if it doesn't exist

    Returns:
        Tuple of (success, resolved_path)
        - success: True if directory exists or was created successfully
        - resolved_path: Absolute path to directory or None on failure
    """
    try:
        resolved = os.path.abspath(path)
        if os.path.exists(resolved):
            if not os.path.isdir(resolved):
                return False, None
            return True, resolved

        if create_if_missing:
            os.makedirs(resolved, mode=0o755, exist_ok=True)
            return True, resolved

        return False, None
    except (OSError, ValueError, PermissionError):
        return False, None

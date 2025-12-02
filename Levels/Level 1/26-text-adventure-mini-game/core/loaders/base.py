"""Shared utilities for loader modules."""

import json
import os
from typing import Any, Optional

from core.logging_utils import log_debug, log_warning


def load_json_file(
    path: str,
    default: Any = None,
    context: Optional[str] = None,
    warn_on_missing: bool = False,
) -> Any:
    """
    Load a JSON file with standardized error handling.

    Args:
        path: Path to JSON file
        default: Default value to return on failure (defaults to {})
        context: Optional context string for more descriptive log messages
            (e.g., "Loading quest data" or "items")
        warn_on_missing: If True, log a warning when file is missing.
            If False, only log at debug level.

    Returns:
        Parsed JSON data, or default value on failure.
        Note: JSON can be any type (dict, list, etc.) depending on file contents.
    """
    if default is None:
        default = {}

    if not os.path.exists(path):
        if warn_on_missing:
            msg = f"File not found at {path}"
            if context:
                msg = f"{context}: {msg}"
            log_warning(msg)
        else:
            log_debug(f"JSON file not found at {path}, using default")
        return default

    try:
        with open(path, "r") as file_handle:
            data = json.load(file_handle)
        return data
    except Exception as exc:  # pylint: disable=broad-except
        msg = f"Failed to load JSON file from {path}: {exc}"
        if context:
            msg = f"{context}: {msg}"
        log_warning(msg)
        return default

"""Shared utilities for loader modules.

Loaders default to a tolerant schema policy: they log and skip malformed data
while still returning usable defaults. Set the environment variable
``STRICT_SCHEMA=1`` to raise ``ValueError`` instead when schema issues are
encountered.
"""

import json
import os
from typing import Any, Dict, Mapping, MutableMapping, Optional, Sequence

from core.logging_utils import (
    format_schema_message,
    log_debug,
    log_schema_warning,
    log_warning,
)

STRICT_SCHEMA = os.environ.get("STRICT_SCHEMA", "").lower() in {"1", "true", "yes", "on"}


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


def _handle_schema_issue(
    context: str,
    section: str,
    identifier: Optional[str],
    message: str,
) -> None:
    """Apply the global schema policy: log and continue, or raise when strict."""
    if STRICT_SCHEMA:
        raise ValueError(format_schema_message(context, message, section, identifier))
    log_schema_warning(context, message, section=section, identifier=identifier)


def ensure_dict(
    data: Any,
    *,
    context: str,
    section: str,
    identifier: Optional[str] = None,
    default: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Ensure the provided data is a dictionary.

    Returns a dictionary (or default) and logs per schema policy when the value
    is not a dict.
    """
    if isinstance(data, MutableMapping):
        return dict(data)

    fallback: Dict[str, Any] = default if default is not None else {}
    _handle_schema_issue(
        context,
        section,
        identifier,
        f"expected object/dict, got {type(data).__name__}",
    )
    return fallback


def ensure_list(
    data: Any,
    *,
    context: str,
    section: str,
    identifier: Optional[str] = None,
    default: Optional[Sequence[Any]] = None,
) -> list:
    """
    Ensure the provided data is a list.

    Returns a list (or default) and logs per schema policy when the value is
    not a list.
    """
    if isinstance(data, list):
        return data

    fallback = list(default) if default is not None else []
    _handle_schema_issue(
        context,
        section,
        identifier,
        f"expected list/array, got {type(data).__name__}",
    )
    return fallback


def validate_required_keys(
    obj: Mapping[str, Any],
    keys: Sequence[str],
    *,
    context: str,
    section: str,
    identifier: Optional[str] = None,
) -> bool:
    """Validate presence of required keys, logging once if any are missing."""
    missing = [key for key in keys if key not in obj]
    if missing:
        _handle_schema_issue(
            context,
            section,
            identifier,
            f"missing required field(s): {', '.join(missing)}",
        )
        return False
    return True

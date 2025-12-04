"""Logging utilities for consistent error handling across the game."""

import logging
import os
from typing import Optional

# Global flag to track if logging has been configured
_logging_configured: bool = False


def get_logger(name: str = "game") -> logging.Logger:
    """
    Get or create a logger instance.

    Args:
        name: Logger name (typically module name)

    Returns:
        Configured logger instance
    """
    global _logging_configured

    if not _logging_configured:
        # Configure root logger once
        log_level_str = os.environ.get("LOG_LEVEL", "INFO").upper()
        log_level = getattr(logging, log_level_str, logging.INFO)

        logging.basicConfig(
            level=log_level,
            format='%(levelname)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        # Mark logging as configured
        _logging_configured = True

    # Always return the logger for the requested name to respect the parameter
    return logging.getLogger(name)


def log_warning(message: str, *args, **kwargs) -> None:
    """Log a warning message."""
    logger = get_logger()
    logger.warning(message, *args, **kwargs)


def log_error(message: str, *args, **kwargs) -> None:
    """Log an error message."""
    logger = get_logger()
    logger.error(message, *args, **kwargs)


def log_info(message: str, *args, **kwargs) -> None:
    """Log an info message."""
    logger = get_logger()
    logger.info(message, *args, **kwargs)


def log_debug(message: str, *args, **kwargs) -> None:
    """Log a debug message."""
    logger = get_logger()
    logger.debug(message, *args, **kwargs)


def format_schema_message(
    context: str,
    message: str,
    section: Optional[str] = None,
    identifier: Optional[str] = None,
) -> str:
    """
    Create a consistently formatted schema validation message.

    Args:
        context: High-level loader context, e.g., "fishing loader"
        message: Human-readable detail about the issue
        section: Optional section name within the payload (e.g., "fish")
        identifier: Optional identifier for the problematic entry

    Returns:
        String formatted with a SCHEMA prefix and contextual fields.
    """
    details = []
    if section:
        details.append(f"section={section}")
    if identifier:
        details.append(f"id={identifier}")
    detail_suffix = f" ({', '.join(details)})" if details else ""
    return f"[SCHEMA] {context}{detail_suffix}: {message}"


def log_schema_warning(
    context: str,
    message: str,
    *,
    section: Optional[str] = None,
    identifier: Optional[str] = None,
) -> None:
    """Log schema issues with a consistent SCHEMA prefix."""
    log_warning(format_schema_message(context, message, section, identifier))


def log_schema_error(
    context: str,
    message: str,
    *,
    section: Optional[str] = None,
    identifier: Optional[str] = None,
) -> None:
    """Log schema issues at error level (reserved for fatal cases)."""
    log_error(format_schema_message(context, message, section, identifier))

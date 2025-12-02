"""Logging utilities for consistent error handling across the game."""

import logging
import os
from typing import Optional

# Global logger instance
_logger: Optional[logging.Logger] = None


def get_logger(name: str = "game") -> logging.Logger:
    """
    Get or create a logger instance.

    Args:
        name: Logger name (typically module name)

    Returns:
        Configured logger instance
    """
    global _logger

    if _logger is None:
        # Configure root logger
        log_level_str = os.environ.get("LOG_LEVEL", "INFO").upper()
        log_level = getattr(logging, log_level_str, logging.INFO)

        logging.basicConfig(
            level=log_level,
            format='%(levelname)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        _logger = logging.getLogger(name)
    else:
        _logger = logging.getLogger(name)

    return _logger


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

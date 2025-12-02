"""Utility functions for image thumbnailer."""

import logging
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)


def validate_image_path(path: Path) -> bool:
    """Validate that a path points to a supported image file.

    Args:
        path: Path to validate

    Returns:
        True if valid image path, False otherwise
    """
    if not path.exists():
        logger.error(f"File does not exist: {path}")
        return False

    if not path.is_file():
        logger.error(f"Path is not a file: {path}")
        return False

    supported_extensions = {".jpg", ".jpeg", ".png", ".webp"}
    if path.suffix.lower() not in supported_extensions:
        logger.error(f"Unsupported file extension: {path.suffix}")
        return False

    return True


def find_image_files(directory: Path) -> List[Path]:
    """Find all supported image files in a directory.

    Args:
        directory: Directory to search

    Returns:
        List of image file paths
    """
    if not directory.exists():
        logger.error(f"Directory does not exist: {directory}")
        return []

    if not directory.is_dir():
        logger.error(f"Path is not a directory: {directory}")
        return []

    supported_extensions = {".jpg", ".jpeg", ".png", ".webp"}
    image_files = []

    for ext in supported_extensions:
        image_files.extend(directory.glob(f"*{ext}"))
        image_files.extend(directory.glob(f"*{ext.upper()}"))

    return sorted(image_files)


def create_output_filename(
    input_path: Path, prefix: str = "thumb_", suffix: str = ""
) -> str:
    """Create an output filename for a thumbnail.

    Args:
        input_path: Original image path
        prefix: Prefix to add to filename
        suffix: Suffix to add before extension

    Returns:
        Output filename
    """
    stem = input_path.stem
    suffix_ext = input_path.suffix
    return f"{prefix}{stem}{suffix}{suffix_ext}"


def setup_logging(level: str = "INFO") -> None:
    """Setup logging configuration.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def parse_size(size_str: str) -> Optional[tuple[int, int]]:
    """Parse size string in format 'WIDTHxHEIGHT'.

    Args:
        size_str: Size string like '200x200' or '300x400'

    Returns:
        Tuple of (width, height) or None if invalid
    """
    try:
        width, height = size_str.split("x", 1)
        return (int(width), int(height))
    except ValueError:
        logger.error(f"Invalid size format: {size_str}. Use WIDTHxHEIGHT format.")
        return None


def validate_directory(path: Path, create_if_missing: bool = False) -> bool:
    """Validate that a path is a directory, optionally creating it.

    Args:
        path: Path to validate
        create_if_missing: Whether to create directory if it doesn't exist

    Returns:
        True if valid directory, False otherwise
    """
    if not path.exists():
        if create_if_missing:
            try:
                path.mkdir(parents=True, exist_ok=True)
                logger.info(f"Created directory: {path}")
                return True
            except Exception as e:
                logger.error(f"Failed to create directory {path}: {e}")
                return False
        else:
            logger.error(f"Directory does not exist: {path}")
            return False

    if not path.is_dir():
        logger.error(f"Path is not a directory: {path}")
        return False

    return True

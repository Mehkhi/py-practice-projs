"""Utility functions for the backup ZIP script."""

from pathlib import Path


def ensure_directory_exists(directory: Path) -> None:
    """
    Ensure a directory exists, creating it if necessary.

    Args:
        directory: Directory path to ensure exists
    """
    directory.mkdir(parents=True, exist_ok=True)


def get_directory_size(directory: Path) -> int:
    """
    Calculate the total size of a directory in bytes.

    Args:
        directory: Directory to calculate size for

    Returns:
        Total size in bytes
    """
    total_size = 0
    for file_path in directory.rglob("*"):
        if file_path.is_file():
            total_size += file_path.stat().st_size
    return total_size


def format_size(size_bytes: int) -> str:
    """
    Format size in bytes to human readable format.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted size string
    """
    size = float(size_bytes)
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        # Return once the value fits within the current unit.
        if size < 1024.0 or unit == "TB":
            return f"{size:.1f} {unit}"
        size /= 1024.0

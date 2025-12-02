"""Core backup functionality for the backup ZIP script."""

import logging
import os
import zipfile
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Set
import fnmatch


logger = logging.getLogger(__name__)


def create_backup_zip(
    source_dir: Path,
    backup_dir: Path,
    exclude_patterns: Optional[List[str]] = None,
    max_backups: int = 10,
) -> Path:
    """
    Create a ZIP backup of the source directory with timestamp.

    Args:
        source_dir: Directory to backup
        backup_dir: Directory to store backup files
        exclude_patterns: List of patterns to exclude (e.g., ['*.pyc', '__pycache__'])
        max_backups: Maximum number of backups to keep

    Returns:
        Path to the created backup file

    Raises:
        ValueError: If source directory doesn't exist
        OSError: If backup creation fails
    """
    if not source_dir.exists():
        raise ValueError(f"Source directory {source_dir} does not exist")

    if not source_dir.is_dir():
        raise ValueError(f"Source path {source_dir} is not a directory")

    # Create backup directory if it doesn't exist
    backup_dir.mkdir(parents=True, exist_ok=True)

    # Generate timestamp for backup filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"backup_{timestamp}.zip"
    backup_path = backup_dir / backup_filename

    logger.info(f"Creating backup: {backup_path}")

    try:
        # Create ZIP file
        with zipfile.ZipFile(backup_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            # Walk through source directory
            for file_path in _get_files_to_backup(source_dir, exclude_patterns or []):
                # Calculate relative path for ZIP
                relative_path = file_path.relative_to(source_dir)
                zipf.write(file_path, relative_path)
                logger.debug(f"Added to backup: {relative_path}")

        # Verify integrity
        if not _verify_zip_integrity(backup_path):
            raise OSError(f"Backup verification failed for {backup_path}")

        logger.info(f"Backup created successfully: {backup_path}")

        # Apply rotation policy
        _rotate_backups(backup_dir, max_backups)

        return backup_path

    except Exception as e:
        # Clean up failed backup
        if backup_path.exists():
            backup_path.unlink()
        logger.error(f"Backup creation failed: {e}")
        raise


def _get_files_to_backup(source_dir: Path, exclude_patterns: List[str]) -> List[Path]:
    """
    Get list of files to include in backup, respecting exclude patterns.

    Args:
        source_dir: Source directory to scan
        exclude_patterns: Patterns to exclude

    Returns:
        List of file paths to backup
    """
    files_to_backup = []

    # Default exclude patterns
    default_excludes = [".git", "__pycache__", "*.pyc", ".DS_Store", "node_modules"]
    all_excludes = set(default_excludes + exclude_patterns)

    for root, dirs, files in os.walk(source_dir):
        root_path = Path(root)

        # Filter directories to exclude
        dirs[:] = [
            d
            for d in dirs
            if not _matches_exclude_patterns(Path(root) / d, all_excludes)
        ]

        # Add files that don't match exclude patterns
        for file in files:
            file_path = root_path / file
            if not _matches_exclude_patterns(file_path, all_excludes):
                files_to_backup.append(file_path)

    return files_to_backup


def _matches_exclude_patterns(path: Path, exclude_patterns: Set[str]) -> bool:
    """
    Check if a path matches any exclude pattern.

    Args:
        path: Path to check
        exclude_patterns: Set of patterns to match against

    Returns:
        True if path matches any pattern
    """
    path_str = str(path)
    path_parts = set(path.parts)

    for pattern in exclude_patterns:
        normalized = pattern.rstrip("/\\")

        if fnmatch.fnmatch(path.name, normalized):
            return True

        if fnmatch.fnmatch(path_str, pattern) or fnmatch.fnmatch(path_str, normalized):
            return True

        if normalized in path_parts:
            return True

    return False


def _verify_zip_integrity(zip_path: Path) -> bool:
    """
    Verify the integrity of a ZIP file.

    Args:
        zip_path: Path to ZIP file

    Returns:
        True if ZIP is valid
    """
    try:
        with zipfile.ZipFile(zip_path, "r") as zipf:
            # Test the ZIP file
            bad_file = zipf.testzip()
            if bad_file:
                logger.error(f"Corrupted file in ZIP: {bad_file}")
                return False
        return True
    except zipfile.BadZipFile:
        logger.error(f"Invalid ZIP file: {zip_path}")
        return False


def _rotate_backups(backup_dir: Path, max_backups: int) -> None:
    """
    Rotate backup files, keeping only the most recent N backups.

    Args:
        backup_dir: Directory containing backup files
        max_backups: Maximum number of backups to keep
    """
    if not backup_dir.exists():
        return

    # Find all backup ZIP files
    backup_files = list(backup_dir.glob("backup_*.zip"))

    if len(backup_files) <= max_backups:
        return

    # Sort by modification time (newest first)
    backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

    # Remove old backups
    files_to_remove = backup_files[max_backups:]
    for old_backup in files_to_remove:
        logger.info(f"Removing old backup: {old_backup}")
        old_backup.unlink()

"""
Utility functions for image organization.
"""

import os
import logging
from pathlib import Path
from typing import List, Optional
from PIL import Image


logger = logging.getLogger(__name__)

FORMAT_BY_SUFFIX = {
    ".jpg": "JPEG",
    ".jpeg": "JPEG",
    ".png": "PNG",
    ".gif": "GIF",
    ".bmp": "BMP",
    ".tiff": "TIFF",
    ".tif": "TIFF",
}


def create_thumbnail(image_path: Path, thumbnail_path: Path, size: tuple = (150, 150)) -> bool:
    """
    Create a thumbnail for an image.

    Args:
        image_path: Path to the source image
        thumbnail_path: Path where thumbnail should be saved
        size: Thumbnail size as (width, height) tuple

    Returns:
        True if successful, False otherwise
    """
    try:
        with Image.open(image_path) as img:
            original_mode = img.mode
            img.thumbnail(size, Image.Resampling.LANCZOS)

            suffix = thumbnail_path.suffix.lower()
            output_format = FORMAT_BY_SUFFIX.get(suffix) or (img.format or "JPEG")

            save_kwargs: dict[str, object] = {}
            if output_format.upper() == "JPEG":
                if img.mode not in {"RGB", "L"}:
                    img = img.convert("RGB")
                save_kwargs["quality"] = 85
            elif output_format.upper() == "PNG" and original_mode == "P":
                # Palette images can produce large files; convert to RGBA for better fidelity
                img = img.convert("RGBA")

            thumbnail_path.parent.mkdir(parents=True, exist_ok=True)
            if output_format.upper() == "PNG":
                save_kwargs.setdefault("optimize", True)

            img.save(thumbnail_path, output_format, **save_kwargs)

        logger.debug(f"Created thumbnail: {thumbnail_path}")
        return True

    except Exception as e:
        logger.error(f"Error creating thumbnail for {image_path}: {e}")
        return False


def get_image_info(image_path: Path) -> dict:
    """
    Get detailed information about an image file.

    Args:
        image_path: Path to the image file

    Returns:
        Dictionary with image information
    """
    info = {
        'path': str(image_path),
        'size_bytes': 0,
        'dimensions': None,
        'format': None,
        'mode': None,
        'has_exif': False
    }

    try:
        # File size
        info['size_bytes'] = image_path.stat().st_size

        # Image properties
        with Image.open(image_path) as img:
            info['dimensions'] = img.size
            info['format'] = img.format
            info['mode'] = img.mode
            info['has_exif'] = hasattr(img, '_getexif') and img._getexif() is not None

    except Exception as e:
        logger.error(f"Error getting info for {image_path}: {e}")

    return info


def validate_image_file(image_path: Path) -> bool:
    """
    Validate that a file is a valid image.

    Args:
        image_path: Path to the file to validate

    Returns:
        True if valid image, False otherwise
    """
    try:
        with Image.open(image_path) as img:
            img.verify()
        return True
    except Exception:
        return False


def get_safe_filename(filename: str) -> str:
    """
    Convert filename to a safe format for filesystem.

    Args:
        filename: Original filename

    Returns:
        Safe filename
    """
    # Replace invalid characters
    safe_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-_"
    safe_filename = "".join(c if c in safe_chars else "_" for c in filename)

    # Remove multiple consecutive underscores
    while "__" in safe_filename:
        safe_filename = safe_filename.replace("__", "_")

    # Remove leading/trailing underscores and dots
    safe_filename = safe_filename.strip("._")

    # Ensure it's not empty
    if not safe_filename:
        safe_filename = "image"

    return safe_filename


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted size string
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

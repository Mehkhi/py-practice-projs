"""Utility functions for the URL shortener."""

import logging
import os
from typing import Optional

try:
    import qrcode
    from qrcode.constants import ERROR_CORRECT_L

    QR_AVAILABLE = True
except ImportError:
    QR_AVAILABLE = False


def setup_logging(level: str = "INFO") -> None:
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def generate_qr_code(url: str, filename: Optional[str] = None) -> str:
    """
    Generate a QR code for the given URL.

    Args:
        url: URL to encode in QR code
        filename: Optional filename for the QR code image

    Returns:
        Path to the generated QR code file

    Raises:
        ImportError: If qrcode library is not available
        RuntimeError: If QR code generation fails
    """
    if not QR_AVAILABLE:
        raise ImportError(
            "qrcode library not installed. Install with: pip install qrcode[pil]"
        )

    if not filename:
        # Generate filename from URL or use default
        safe_chars = "".join(c for c in url if c.isalnum() or c in ("-", "_"))
        filename = f"qr_{safe_chars[:20]}.png"

    try:
        # Create QR code with error correction
        qr = qrcode.QRCode(
            version=1,
            error_correction=ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)

        # Create image
        img = qr.make_image(fill_color="black", back_color="white")

        # Save to file
        img.save(filename)
        logging.info(f"QR code generated: {filename}")

        return filename

    except Exception as e:
        logging.error(f"Failed to generate QR code: {e}")
        raise RuntimeError(f"QR code generation failed: {e}")


def validate_short_code(code: str) -> bool:
    """
    Validate a short code format.

    Args:
        code: Short code to validate

    Returns:
        True if valid, False otherwise
    """
    if not code or not isinstance(code, str):
        return False

    # Check length (3-50 characters)
    if len(code) < 3 or len(code) > 50:
        return False

    # Check allowed characters (alphanumeric and some symbols)
    allowed_chars = set(
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_"
    )
    return all(c in allowed_chars for c in code)


def sanitize_url(url: str) -> str:
    """
    Sanitize and normalize a URL.

    Args:
        url: URL to sanitize

    Returns:
        Sanitized URL
    """
    if not url:
        return ""

    # Remove whitespace
    url = url.strip()

    # Add protocol if missing
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    return url


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted size string
    """
    if size_bytes == 0:
        return "0 B"

    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1

    return f"{size_bytes:.1f} {size_names[i]}"


def get_database_info(db_path: str) -> dict:
    """
    Get information about the SQLite database.

    Args:
        db_path: Path to the database file

    Returns:
        Dictionary with database information
    """
    info = {
        "exists": os.path.exists(db_path),
        "size": 0,
        "readable": False,
        "writable": False,
    }

    if info["exists"]:
        try:
            info["size"] = os.path.getsize(db_path)
            info["readable"] = os.access(db_path, os.R_OK)
            info["writable"] = os.access(db_path, os.W_OK)
        except OSError:
            pass

    return info


def create_backup_filename(original_path: str) -> str:
    """
    Create a backup filename with timestamp.

    Args:
        original_path: Original file path

    Returns:
        Backup filename
    """
    import datetime

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = os.path.splitext(original_path)[0]
    extension = os.path.splitext(original_path)[1] or ".db"

    return f"{base_name}_backup_{timestamp}{extension}"


def is_port_available(port: int) -> bool:
    """
    Check if a port is available for binding.

    Args:
        port: Port number to check

    Returns:
        True if port is available, False otherwise
    """
    import socket

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("localhost", port))
            return True
    except (OSError, socket.error):
        return False


def find_available_port(start_port: int = 5000, max_attempts: int = 100) -> int:
    """
    Find an available port starting from the given port.

    Args:
        start_port: Port to start checking from
        max_attempts: Maximum number of ports to check

    Returns:
        Available port number

    Raises:
        RuntimeError: If no available port found
    """
    for port in range(start_port, start_port + max_attempts):
        if is_port_available(port):
            return port

    raise RuntimeError(
        f"No available port found in range {start_port}-{start_port + max_attempts}"
    )


def truncate_string(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """
    Truncate a string to a maximum length.

    Args:
        text: String to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated

    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text

    return text[: max_length - len(suffix)] + suffix


def parse_expiration_time(expiry_input: str) -> Optional[str]:
    """
    Parse expiration time from various input formats.

    Args:
        expiry_input: Expiration time input (days, date, etc.)

    Returns:
        ISO format expiration datetime or None
    """
    import datetime
    import re

    if not expiry_input:
        return None

    # Try to parse as number of days
    days_match = re.match(r"^(\d+)d?$", expiry_input.strip())
    if days_match:
        days = int(days_match.group(1))
        expiry_date = datetime.datetime.now() + datetime.timedelta(days=days)
        return expiry_date.isoformat()

    # Try to parse as date (YYYY-MM-DD)
    try:
        expiry_date = datetime.datetime.strptime(expiry_input.strip(), "%Y-%m-%d")
        return expiry_date.isoformat()
    except ValueError:
        pass

    # Try to parse as datetime (YYYY-MM-DD HH:MM:SS)
    try:
        expiry_date = datetime.datetime.strptime(
            expiry_input.strip(), "%Y-%m-%d %H:%M:%S"
        )
        return expiry_date.isoformat()
    except ValueError:
        pass

    return None

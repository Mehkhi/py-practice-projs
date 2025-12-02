"""
Utility functions for QR Code Generator

Provides helper functions for validation, data formatting, and batch processing.
"""

import csv
import re
import logging
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


def validate_url(url: str) -> bool:
    """
    Validate if a string is a valid URL.

    Args:
        url: The URL string to validate

    Returns:
        True if valid URL, False otherwise
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception as e:
        logger.debug(f"URL validation error: {e}")
        return False


def validate_email(email: str) -> bool:
    """
    Validate if a string is a valid email address.

    Args:
        email: The email string to validate

    Returns:
        True if valid email, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    """
    Validate if a string is a valid phone number.

    Args:
        phone: The phone number string to validate

    Returns:
        True if valid phone, False otherwise
    """
    # Remove common phone number formatting
    cleaned = re.sub(r'[\s\-\(\)]', '', phone)
    # Check if it's mostly digits (allow + for international)
    return bool(re.match(r'^\+?\d{7,15}$', cleaned))


def create_vcard(name: str, phone: Optional[str] = None, email: Optional[str] = None,
                 org: Optional[str] = None, url: Optional[str] = None) -> str:
    """
    Create a vCard format string from contact information.

    Args:
        name: Full name of the contact
        phone: Phone number (optional)
        email: Email address (optional)
        org: Organization/company (optional)
        url: Website URL (optional)

    Returns:
        vCard formatted string

    Raises:
        ValueError: If name is empty or invalid
    """
    if not name or not name.strip():
        raise ValueError("Name is required for vCard")

    vcard_lines = [
        "BEGIN:VCARD",
        "VERSION:3.0",
        f"FN:{name.strip()}"
    ]

    if phone:
        if not validate_phone(phone):
            logger.warning(f"Potentially invalid phone number: {phone}")
        vcard_lines.append(f"TEL:{phone}")

    if email:
        if not validate_email(email):
            logger.warning(f"Potentially invalid email: {email}")
        vcard_lines.append(f"EMAIL:{email}")

    if org:
        vcard_lines.append(f"ORG:{org}")

    if url:
        if not validate_url(url):
            logger.warning(f"Potentially invalid URL: {url}")
        vcard_lines.append(f"URL:{url}")

    vcard_lines.append("END:VCARD")

    return "\n".join(vcard_lines)


def parse_csv_batch(csv_file_path: str) -> List[Dict[str, Any]]:
    """
    Parse CSV file for batch QR code generation.

    Expected CSV format:
    - Required columns: 'data' (the content to encode)
    - Optional columns: 'filename', 'type', 'size', 'error_correction',
                       'fill_color', 'back_color', 'format'

    Args:
        csv_file_path: Path to the CSV file

    Returns:
        List of dictionaries containing QR code parameters

    Raises:
        FileNotFoundError: If CSV file doesn't exist
        ValueError: If CSV format is invalid or missing required columns
    """
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)

            if not reader.fieldnames or 'data' not in reader.fieldnames:
                raise ValueError("CSV must contain a 'data' column")

            batch_data = []
            for row_num, row in enumerate(reader, start=2):
                if not row.get('data', '').strip():
                    logger.warning(f"Row {row_num}: Empty data field, skipping")
                    continue

                # Convert string values to appropriate types
                qr_params = {
                    'data': row['data'].strip(),
                    'filename': row.get('filename', '').strip() or None,
                    'type': row.get('type', '').strip() or 'text',
                    'size': int(row.get('size', 10)) if row.get('size') else None,
                    'error_correction': row.get('error_correction', '').strip() or None,
                    'fill_color': row.get('fill_color', '').strip() or 'black',
                    'back_color': row.get('back_color', '').strip() or 'white',
                    'format': row.get('format', '').strip() or 'png'
                }

                batch_data.append(qr_params)
                logger.debug(f"Parsed row {row_num}: {qr_params['data'][:50]}...")

            if not batch_data:
                raise ValueError("No valid data found in CSV file")

            logger.info(f"Successfully parsed {len(batch_data)} QR code entries from CSV")
            return batch_data

    except FileNotFoundError:
        raise FileNotFoundError(f"CSV file not found: {csv_file_path}")
    except Exception as e:
        if isinstance(e, (ValueError, FileNotFoundError)):
            raise
        raise ValueError(f"Error parsing CSV file: {e}")


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing invalid characters.

    Args:
        filename: The filename to sanitize

    Returns:
        Sanitized filename
    """
    # Remove or replace invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip('. ')
    # Ensure it's not empty
    return sanitized or 'qr_code'


def get_error_correction_level(level: str) -> int:
    """
    Convert error correction level string to qrcode constant.

    Args:
        level: Error correction level ('L', 'M', 'Q', 'H')

    Returns:
        qrcode error correction constant

    Raises:
        ValueError: If level is invalid
    """
    level = level.upper()
    error_correction_map = {
        'L': 1,  # ~7% correction
        'M': 0,  # ~15% correction (default)
        'Q': 3,  # ~25% correction
        'H': 2   # ~30% correction
    }

    if level not in error_correction_map:
        raise ValueError(f"Invalid error correction level: {level}. Use L, M, Q, or H")

    return error_correction_map[level]

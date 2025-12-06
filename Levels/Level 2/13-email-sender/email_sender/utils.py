"""
Utility functions for email sender.

This module provides helper functions for email validation, CSV processing,
and other utility operations.
"""

import csv
import re
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

try:
    from email_validator import validate_email as _validate_email, EmailNotValidError
    EMAIL_VALIDATOR_AVAILABLE = True
except ImportError:
    EMAIL_VALIDATOR_AVAILABLE = False

logger = logging.getLogger(__name__)


def validate_email(email: str) -> bool:
    """
    Validate an email address.

    Args:
        email: Email address to validate

    Returns:
        True if email is valid, False otherwise
    """
    if not email or not isinstance(email, str):
        return False

    email = email.strip()

    # Basic regex validation
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return False

    # Use email-validator library if available for more thorough validation
    if EMAIL_VALIDATOR_AVAILABLE:
        try:
            _validate_email(email, check_deliverability=False)
            return True
        except EmailNotValidError:
            return False

    return True


def load_recipients_from_csv(file_path: str) -> List[Dict[str, Any]]:
    """
    Load recipient data from a CSV file.

    Expected CSV format:
    email,name,company
    john@example.com,John Doe,Acme Corp
    jane@example.com,Jane Smith,Tech Inc

    Args:
        file_path: Path to the CSV file

    Returns:
        List of dictionaries with recipient data

    Raises:
        FileNotFoundError: If CSV file doesn't exist
        ValueError: If CSV format is invalid
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"CSV file not found: {file_path}")

    recipients = []

    try:
        with open(file_path, 'r', encoding='utf-8') as csvfile:
            # Detect delimiter
            sample = csvfile.read(1024)
            csvfile.seek(0)
            sniffer = csv.Sniffer()
            delimiter = sniffer.sniff(sample).delimiter

            reader = csv.DictReader(csvfile, delimiter=delimiter)

            for row_num, row in enumerate(reader, start=2):  # Start at 2 for header
                # Skip empty rows
                if not any(row.values()):
                    continue

                # Validate required fields
                if 'email' not in row or not row['email']:
                    logger.warning(f"Row {row_num}: Missing email address")
                    continue

                # Validate email format
                if not validate_email(row['email']):
                    logger.warning(f"Row {row_num}: Invalid email address: {row['email']}")
                    continue

                # Clean up the row data
                cleaned_row = {k.strip(): v.strip() for k, v in row.items() if v}
                recipients.append(cleaned_row)

        logger.info(f"Loaded {len(recipients)} valid recipients from {file_path}")
        return recipients

    except Exception as e:
        logger.error(f"Error reading CSV file {file_path}: {e}")
        raise ValueError(f"Invalid CSV file: {e}")


def create_sample_csv(file_path: str) -> None:
    """
    Create a sample CSV file with recipient data.

    Args:
        file_path: Path where to create the sample CSV
    """
    sample_data = [
        {'email': 'john.doe@example.com', 'name': 'John Doe', 'company': 'Acme Corp'},
        {'email': 'jane.smith@example.com', 'name': 'Jane Smith', 'company': 'Tech Inc'},
        {'email': 'bob.wilson@example.com', 'name': 'Bob Wilson', 'company': 'Startup LLC'},
    ]

    file_path = Path(file_path)

    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['email', 'name', 'company']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(sample_data)

    logger.info(f"Created sample CSV file: {file_path}")


def format_email_template(template: str, data: Dict[str, Any], use_jinja: bool = False) -> str:
    """
    Format an email template with provided data.

    Args:
        template: Email template string with placeholders like {name} or Jinja2 syntax
        data: Dictionary with data to substitute
        use_jinja: If True, use Jinja2 rendering; otherwise use simple .format()

    Returns:
        Formatted email content
    """
    try:
        if use_jinja:
            try:
                from jinja2 import Template
                jinja_template = Template(template)
                return jinja_template.render(**data)
            except ImportError:
                logger.warning("Jinja2 not available, falling back to .format()")
                return template.format(**data)
        else:
            return template.format(**data)
    except KeyError as e:
        logger.warning(f"Missing template variable: {e}")
        return template
    except Exception as e:
        logger.error(f"Error formatting template: {e}")
        return template


def load_template_file(file_path: str) -> str:
    """
    Load template content from a file.

    Args:
        file_path: Path to template file

    Returns:
        Template content as string

    Raises:
        FileNotFoundError: If template file doesn't exist
    """
    template_path = Path(file_path)
    if not template_path.exists():
        raise FileNotFoundError(f"Template file not found: {file_path}")

    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()


def get_file_size_mb(file_path: str) -> float:
    """
    Get file size in megabytes.

    Args:
        file_path: Path to the file

    Returns:
        File size in MB
    """
    try:
        size_bytes = Path(file_path).stat().st_size
        return size_bytes / (1024 * 1024)
    except Exception as e:
        logger.error(f"Error getting file size for {file_path}: {e}")
        return 0.0


def is_valid_attachment(file_path: str, max_size_mb: float = 25.0) -> bool:
    """
    Check if a file is a valid email attachment.

    Args:
        file_path: Path to the file
        max_size_mb: Maximum file size in MB

    Returns:
        True if file is valid for attachment
    """
    try:
        file_path = Path(file_path)

        if not file_path.exists():
            return False

        if not file_path.is_file():
            return False

        size_mb = get_file_size_mb(str(file_path))
        if size_mb > max_size_mb:
            logger.warning(f"File {file_path} is too large: {size_mb:.2f}MB > {max_size_mb}MB")
            return False

        return True

    except Exception as e:
        logger.error(f"Error validating attachment {file_path}: {e}")
        return False

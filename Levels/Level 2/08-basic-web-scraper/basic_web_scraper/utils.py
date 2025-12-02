"""Utility functions for the web scraper."""

import re
from typing import Optional
from urllib.parse import urljoin, urlparse


def is_valid_url(url: str) -> bool:
    """Check if a URL is valid.

    Args:
        url: URL to check

    Returns:
        True if URL is valid, False otherwise
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def normalize_url(url: str, base_url: str = "") -> str:
    """Normalize a URL by adding scheme and resolving relative URLs.

    Args:
        url: URL to normalize
        base_url: Base URL for resolving relative URLs

    Returns:
        Normalized absolute URL
    """
    # Resolve relative URLs if base URL provided
    if base_url and not urlparse(url).scheme:
        url = urljoin(base_url, url)
    # Add scheme if missing and no base URL provided
    elif not urlparse(url).scheme:
        url = f"http://{url}"

    return url


def extract_price_from_text(text: str) -> Optional[str]:
    """Extract price information from text.

    Args:
        text: Text to extract price from

    Returns:
        Price string or None if not found
    """
    # Common price patterns
    patterns = [
        r"[\$€£¥]\s*\d+(?:,\d{3})*(?:\.\d{2})?",  # $1,234.56
        r"\d+(?:,\d{3})*(?:\.\d{2})?\s*[\$€£¥]",  # 1,234.56$
        r"\d+(?:,\d{3})*(?:\.\d{2})?",  # Just numbers
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group().strip()

    return None


def clean_text(text: str) -> str:
    """Clean and normalize text.

    Args:
        text: Text to clean

    Returns:
        Cleaned text
    """
    if not text:
        return ""

    # Remove extra whitespace
    text = re.sub(r"\s+", " ", text)

    # Remove leading/trailing whitespace
    text = text.strip()

    return text


def get_domain(url: str) -> str:
    """Extract domain from URL.

    Args:
        url: URL to extract domain from

    Returns:
        Domain string
    """
    try:
        parsed = urlparse(url)
        return parsed.netloc
    except Exception:
        return ""


def is_same_domain(url1: str, url2: str) -> bool:
    """Check if two URLs belong to the same domain.

    Args:
        url1: First URL
        url2: Second URL

    Returns:
        True if same domain, False otherwise
    """
    domain1 = get_domain(url1)
    domain2 = get_domain(url2)

    # If either URL is invalid, return False
    if not domain1 or not domain2:
        return False

    return domain1 == domain2


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file system usage.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename
    """
    # Remove or replace unsafe characters
    filename = re.sub(r'[<>:"/\\|?*]', "_", filename)
    filename = re.sub(r"\s+", "_", filename)

    # Remove leading/trailing underscores and dots
    filename = filename.strip("._")

    # Ensure filename is not empty
    if not filename:
        filename = "output"

    return filename


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format.

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

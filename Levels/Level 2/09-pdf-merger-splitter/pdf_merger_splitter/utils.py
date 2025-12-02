"""Utility functions for PDF operations."""

import logging
from pathlib import Path
from typing import List, Union

logger = logging.getLogger(__name__)


def validate_pdf_path(file_path: Union[str, Path]) -> Path:
    """Validate that a file path exists and is a PDF file.

    Args:
        file_path: Path to validate

    Returns:
        Path object if valid

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file is not a PDF
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if path.suffix.lower() != '.pdf':
        raise ValueError(f"File is not a PDF: {file_path}")

    return path


def parse_page_range(range_str: str, total_pages: int) -> List[int]:
    """Parse page range string into list of page numbers.

    Args:
        range_str: Page range string (e.g., "1-3,5,7-9")
        total_pages: Total number of pages in the PDF

    Returns:
        List of 1-based page numbers

    Raises:
        ValueError: If range format is invalid
    """
    if not range_str.strip():
        return list(range(1, total_pages + 1))

    pages = set()

    for part in range_str.split(','):
        part = part.strip()

        if '-' in part:
            start, end = part.split('-', 1)
            start = int(start.strip())
            end = int(end.strip())

            if start < 1 or end > total_pages or start > end:
                raise ValueError(f"Invalid page range: {part}")

            pages.update(range(start, end + 1))
        else:
            page = int(part)
            if page < 1 or page > total_pages:
                raise ValueError(f"Page number out of range: {page}")
            pages.add(page)

    return sorted(list(pages))


def parse_page_order(order_str: str, total_pages: int) -> List[int]:
    """Parse a page order string preserving order and duplicates.

    Accepts comma or whitespace separated tokens. Each token can be a single
    page number (e.g., "3") or an inclusive range (e.g., "2-5").

    Returns a 1-based list of page numbers in the given order.
    Raises ValueError for out-of-range or malformed tokens.
    """
    tokens = [t for part in order_str.replace(',', ' ').split() if (t := part.strip())]
    if not tokens:
        return []
    ordered_pages: List[int] = []
    for token in tokens:
        if '-' in token:
            try:
                start_str, end_str = token.split('-', 1)
                start = int(start_str.strip())
                end = int(end_str.strip())
            except Exception as exc:
                raise ValueError(f"Invalid range token: {token}") from exc
            if start < 1 or end > total_pages or start > end:
                raise ValueError(f"Invalid page range: {token}")
            ordered_pages.extend(list(range(start, end + 1)))
        else:
            try:
                page = int(token)
            except Exception as exc:
                raise ValueError(f"Invalid page token: {token}") from exc
            if page < 1 or page > total_pages:
                raise ValueError(f"Page number out of range: {page}")
            ordered_pages.append(page)
    return ordered_pages


def ensure_output_dir(output_path: Union[str, Path]) -> Path:
    """Ensure output directory exists.

    Args:
        output_path: Output file path

    Returns:
        Path object with guaranteed existing parent directory
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def get_page_number_text(page_num: int, total_pages: int, format_str: str = "Page {num} of {total}") -> str:
    """Generate page number text.

    Args:
        page_num: Current page number (1-based)
        total_pages: Total number of pages
        format_str: Format string for page number

    Returns:
        Formatted page number text
    """
    return format_str.format(num=page_num, total=total_pages)

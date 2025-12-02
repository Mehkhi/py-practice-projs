"""
Utility functions for the currency converter.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


def validate_currency_code(currency: str) -> bool:
    """
    Validate currency code format.

    Args:
        currency: Currency code to validate

    Returns:
        True if valid, False otherwise
    """
    if not isinstance(currency, str):
        return False

    currency = currency.upper().strip()

    # Basic validation: 3 uppercase letters
    if len(currency) != 3 or not currency.isalpha():
        return False

    return True


def format_currency_amount(amount: float, currency: str, precision: int = 2) -> str:
    """
    Format currency amount with proper formatting.

    Args:
        amount: Amount to format
        currency: Currency code
        precision: Decimal precision

    Returns:
        Formatted currency string
    """
    if amount is None:
        return "N/A"

    # Round to specified precision
    rounded_amount = round(amount, precision)

    # Format with thousands separator
    formatted = f"{rounded_amount:,.{precision}f}"

    return f"{formatted} {currency.upper()}"


def calculate_conversion_rate(from_currency: str, to_currency: str, rates: Dict[str, float]) -> float:
    """
    Calculate conversion rate between two currencies.

    Args:
        from_currency: Source currency
        to_currency: Target currency
        rates: Exchange rates dictionary

    Returns:
        Conversion rate
    """
    if from_currency == to_currency:
        return 1.0

    if from_currency == "USD":
        return rates.get(to_currency, 1.0)
    elif to_currency == "USD":
        return 1.0 / rates.get(from_currency, 1.0)
    else:
        from_rate = rates.get(from_currency, 1.0)
        to_rate = rates.get(to_currency, 1.0)
        return to_rate / from_rate


def get_currency_symbol(currency: str) -> str:
    """
    Get currency symbol for display.

    Args:
        currency: Currency code

    Returns:
        Currency symbol
    """
    symbols = {
        'USD': '$',
        'EUR': '€',
        'GBP': '£',
        'JPY': '¥',
        'CAD': 'C$',
        'AUD': 'A$',
        'CHF': 'CHF',
        'CNY': '¥',
        'INR': '₹',
        'BRL': 'R$',
        'RUB': '₽',
        'KRW': '₩',
        'MXN': '$',
        'SGD': 'S$',
        'HKD': 'HK$',
        'NZD': 'NZ$',
        'SEK': 'kr',
        'NOK': 'kr',
        'DKK': 'kr',
        'PLN': 'zł',
        'CZK': 'Kč',
        'HUF': 'Ft',
        'TRY': '₺',
        'ZAR': 'R',
        'ILS': '₪',
        'AED': 'د.إ',
        'SAR': '﷼',
        'THB': '฿',
        'MYR': 'RM',
        'PHP': '₱',
        'IDR': 'Rp',
        'VND': '₫',
    }

    return symbols.get(currency.upper(), currency.upper())


def format_timestamp(timestamp: str) -> str:
    """
    Format timestamp for display.

    Args:
        timestamp: ISO timestamp string

    Returns:
        Formatted timestamp
    """
    if not timestamp or timestamp == "N/A":
        return "N/A"

    try:
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    except (ValueError, AttributeError):
        return timestamp


def create_conversion_summary(amount: float, from_currency: str, to_currency: str,
                            converted_amount: float, timestamp: str,
                            conversion_rate: Optional[float] = None) -> str:
    """
    Create a formatted conversion summary.

    Args:
        amount: Original amount
        from_currency: Source currency
        to_currency: Target currency
        converted_amount: Converted amount
        timestamp: Conversion timestamp
        conversion_rate: Conversion rate (optional)

    Returns:
        Formatted summary string
    """
    from_symbol = get_currency_symbol(from_currency)
    to_symbol = get_currency_symbol(to_currency)

    summary = f"""
💰 Currency Conversion Summary
{'=' * 40}
Original:     {from_symbol}{amount:,.2f} {from_currency.upper()}
Converted:    {to_symbol}{converted_amount:,.2f} {to_currency.upper()}
Last Updated: {format_timestamp(timestamp)}
"""

    if conversion_rate:
        summary += f"Rate:         1 {from_currency.upper()} = {conversion_rate:.6f} {to_currency.upper()}\n"

    return summary


def validate_csv_columns(df_columns: List[str], required_columns: List[str]) -> List[str]:
    """
    Validate that CSV contains required columns.

    Args:
        df_columns: List of column names in DataFrame
        required_columns: List of required column names

    Returns:
        List of missing columns

    Raises:
        ValueError: If required columns are missing
    """
    missing_columns = [col for col in required_columns if col not in df_columns]

    if missing_columns:
        raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")

    return missing_columns


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe file operations.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename
    """
    import re

    # Remove or replace invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)

    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip(' .')

    # Ensure it's not empty
    if not sanitized:
        sanitized = "conversion_result"

    return sanitized


def estimate_conversion_time(num_conversions: int) -> str:
    """
    Estimate time for batch conversion.

    Args:
        num_conversions: Number of conversions to perform

    Returns:
        Estimated time string
    """
    if num_conversions <= 10:
        return "less than 1 second"
    elif num_conversions <= 100:
        return "1-2 seconds"
    elif num_conversions <= 1000:
        return "2-5 seconds"
    else:
        return f"5-{num_conversions // 200} seconds"


def get_cache_info(cache_file_path: str) -> Dict[str, str]:
    """
    Get information about the cache file.

    Args:
        cache_file_path: Path to cache file

    Returns:
        Dictionary with cache information
    """
    from pathlib import Path
    import json
    from datetime import datetime

    cache_file = Path(cache_file_path)

    if not cache_file.exists():
        return {
            "exists": "No",
            "size": "N/A",
            "last_modified": "N/A",
            "rates_count": "N/A"
        }

    try:
        stat = cache_file.stat()
        size = f"{stat.st_size:,} bytes"
        last_modified = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")

        with open(cache_file, 'r') as f:
            data = json.load(f)
            rates_count = len(data.get('rates', {}))

        return {
            "exists": "Yes",
            "size": size,
            "last_modified": last_modified,
            "rates_count": str(rates_count)
        }
    except Exception as e:
        logger.warning(f"Could not read cache info: {e}")
        return {
            "exists": "Yes",
            "size": "Unknown",
            "last_modified": "Unknown",
            "rates_count": "Unknown"
        }

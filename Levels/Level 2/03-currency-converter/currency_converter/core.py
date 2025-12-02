"""
Core currency conversion logic with API integration and caching.
"""

import json
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import pandas as pd
import requests
from dateutil import parser as date_parser

logger = logging.getLogger(__name__)


class CurrencyConverter:
    """
    A professional currency converter with live exchange rates and caching.

    Features:
    - Live exchange rate fetching from API
    - Fallback to cached rates when API fails
    - Batch conversion from CSV files
    - Historical rate lookups
    - Offline mode with stale data warnings
    """

    def __init__(self, cache_file: str = "exchange_rates.json"):
        """
        Initialize the currency converter.

        Args:
            cache_file: Path to the cache file for storing exchange rates
        """
        self.cache_file = Path(cache_file)
        self.api_url = "https://api.exchangerate-api.com/v4/latest"
        self.rates: Dict[str, float] = {}
        self.last_updated: Optional[datetime] = None
        self.cache_duration = timedelta(hours=1)  # Cache rates for 1 hour

        # Load cached rates on initialization
        self._load_cached_rates()

    def _load_cached_rates(self) -> None:
        """Load exchange rates from cache file."""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r') as f:
                    data = json.load(f)
                    self.rates = data.get('rates', {})
                    last_updated_str = data.get('last_updated')
                    if last_updated_str:
                        self.last_updated = date_parser.parse(last_updated_str)
                    logger.info(f"Loaded {len(self.rates)} cached exchange rates")
        except Exception as e:
            logger.warning(f"Failed to load cached rates: {e}")
            self.rates = {}

    def _save_rates_to_cache(self) -> None:
        """Save current exchange rates to cache file."""
        try:
            data = {
                'rates': self.rates,
                'last_updated': self.last_updated.isoformat() if self.last_updated else None
            }
            with open(self.cache_file, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info("Exchange rates saved to cache")
        except Exception as e:
            logger.error(f"Failed to save rates to cache: {e}")

    def _is_cache_stale(self) -> bool:
        """Check if cached rates are stale."""
        if not self.last_updated:
            return True
        return datetime.now() - self.last_updated > self.cache_duration

    def fetch_live_rates(self, base_currency: str = "USD") -> bool:
        """
        Fetch live exchange rates from API.

        Args:
            base_currency: Base currency for exchange rates (default: USD)

        Returns:
            True if rates were successfully fetched, False otherwise
        """
        try:
            logger.info(f"Fetching live exchange rates for {base_currency}")
            response = requests.get(f"{self.api_url}/{base_currency}", timeout=10)
            response.raise_for_status()

            data = response.json()
            rates = data.get("rates")
            if not isinstance(rates, dict) or not rates:
                logger.error("Live rate response missing usable 'rates' data")
                return False

            timestamp: Optional[datetime] = None
            raw_timestamp = (
                data.get("time_last_update_unix")
                or data.get("time_last_updated")
                or data.get("time_last_update_utc")
            )
            if isinstance(raw_timestamp, (int, float)):
                timestamp = datetime.fromtimestamp(raw_timestamp)
            elif raw_timestamp:
                try:
                    timestamp = date_parser.parse(str(raw_timestamp))
                except (ValueError, TypeError, OverflowError):
                    logger.debug("Unable to parse timestamp from live rates payload")

            self.rates = rates
            self.last_updated = timestamp or datetime.now()

            # Save to cache
            self._save_rates_to_cache()

            logger.info(f"Successfully fetched {len(self.rates)} exchange rates")
            return True

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch live rates: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error fetching rates: {e}")
            return False

    def get_rates(self, force_refresh: bool = False) -> Dict[str, float]:
        """
        Get exchange rates, fetching live data if needed.

        Args:
            force_refresh: Force refresh from API even if cache is fresh

        Returns:
            Dictionary of exchange rates
        """
        if force_refresh or self._is_cache_stale() or not self.rates:
            if not self.fetch_live_rates():
                if not self.rates:
                    raise RuntimeError("No exchange rates available (API failed and no cache)")
                else:
                    logger.warning("Using stale cached rates due to API failure")

        return self.rates.copy()

    def convert(self, amount: float, from_currency: str, to_currency: str) -> Tuple[float, str]:
        """
        Convert amount from one currency to another.

        Args:
            amount: Amount to convert
            from_currency: Source currency code (e.g., 'USD')
            to_currency: Target currency code (e.g., 'EUR')

        Returns:
            Tuple of (converted_amount, timestamp_string)

        Raises:
            ValueError: If currency codes are invalid
            RuntimeError: If no exchange rates are available
        """
        if amount < 0:
            raise ValueError("Amount must be non-negative")

        from_currency = from_currency.upper()
        to_currency = to_currency.upper()

        if from_currency == to_currency:
            return amount, self.last_updated.isoformat() if self.last_updated else "N/A"

        rates = self.get_rates()

        if from_currency not in rates and from_currency != "USD":
            raise ValueError(f"Currency '{from_currency}' not supported")
        if to_currency not in rates and to_currency != "USD":
            raise ValueError(f"Currency '{to_currency}' not supported")

        # Convert to USD first if needed
        if from_currency != "USD":
            usd_amount = amount / rates[from_currency]
        else:
            usd_amount = amount

        # Convert from USD to target currency
        if to_currency != "USD":
            converted_amount = usd_amount * rates[to_currency]
        else:
            converted_amount = usd_amount

        timestamp = self.last_updated.isoformat() if self.last_updated else "N/A"
        return round(converted_amount, 2), timestamp

    def get_historical_rates(self, date: str, base_currency: str = "USD") -> Dict[str, float]:
        """
        Get historical exchange rates for a specific date.

        Args:
            date: Date in YYYY-MM-DD format
            base_currency: Base currency for exchange rates

        Returns:
            Dictionary of historical exchange rates
        """
        try:
            # Parse and validate date
            parsed_date = datetime.strptime(date, "%Y-%m-%d")
            if parsed_date > datetime.now():
                raise ValueError("Date cannot be in the future")

            # Use a different API endpoint for historical data
            historical_url = f"https://api.exchangerate-api.com/v4/history/{base_currency}/{date}"
            logger.info(f"Fetching historical rates for {date}")

            response = requests.get(historical_url, timeout=10)
            response.raise_for_status()

            data = response.json()
            return data.get('rates', {})

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch historical rates: {e}")
            raise RuntimeError(f"Could not fetch historical rates: {e}")
        except ValueError as e:
            logger.error(f"Invalid date format: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching historical rates: {e}")
            raise RuntimeError(f"Unexpected error: {e}")

    def convert_historical(self, amount: float, from_currency: str, to_currency: str, date: str) -> Tuple[float, str]:
        """
        Convert amount using historical exchange rates.

        Args:
            amount: Amount to convert
            from_currency: Source currency code
            to_currency: Target currency code
            date: Date in YYYY-MM-DD format

        Returns:
            Tuple of (converted_amount, date)
        """
        if amount < 0:
            raise ValueError("Amount must be non-negative")

        from_currency = from_currency.upper()
        to_currency = to_currency.upper()

        if from_currency == to_currency:
            return amount, date

        rates = self.get_historical_rates(date)

        if from_currency not in rates and from_currency != "USD":
            raise ValueError(f"Currency '{from_currency}' not supported for date {date}")
        if to_currency not in rates and to_currency != "USD":
            raise ValueError(f"Currency '{to_currency}' not supported for date {date}")

        # Convert to USD first if needed
        if from_currency != "USD":
            usd_amount = amount / rates[from_currency]
        else:
            usd_amount = amount

        # Convert from USD to target currency
        if to_currency != "USD":
            converted_amount = usd_amount * rates[to_currency]
        else:
            converted_amount = usd_amount

        return round(converted_amount, 2), date

    def batch_convert_csv(self, input_file: str, output_file: str,
                         amount_col: str, from_col: str, to_col: str) -> None:
        """
        Convert currencies in batch from a CSV file.

        Args:
            input_file: Path to input CSV file
            output_file: Path to output CSV file
            amount_col: Name of column containing amounts
            from_col: Name of column containing source currencies
            to_col: Name of column containing target currencies
        """
        try:
            logger.info(f"Starting batch conversion from {input_file}")

            # Read input CSV
            df = pd.read_csv(input_file)

            if amount_col not in df.columns:
                raise ValueError(f"Column '{amount_col}' not found in CSV")
            if from_col not in df.columns:
                raise ValueError(f"Column '{from_col}' not found in CSV")
            if to_col not in df.columns:
                raise ValueError(f"Column '{to_col}' not found in CSV")

            # Add conversion results
            df['converted_amount'] = 0.0
            df['conversion_timestamp'] = ""
            df['conversion_rate'] = 0.0

            for index, row in df.iterrows():
                try:
                    amount = float(row[amount_col])
                    from_curr = str(row[from_col]).upper()
                    to_curr = str(row[to_col]).upper()

                    converted, timestamp = self.convert(amount, from_curr, to_curr)
                    df.at[index, 'converted_amount'] = converted
                    df.at[index, 'conversion_timestamp'] = timestamp

                    # Calculate conversion rate
                    if from_curr == to_curr:
                        rate = 1.0
                    else:
                        rates = self.get_rates()
                        if from_curr == "USD":
                            rate = rates.get(to_curr, 1.0)
                        elif to_curr == "USD":
                            rate = 1.0 / rates.get(from_curr, 1.0)
                        else:
                            rate = rates.get(to_curr, 1.0) / rates.get(from_curr, 1.0)

                    df.at[index, 'conversion_rate'] = round(rate, 6)

                except Exception as e:
                    logger.warning(f"Failed to convert row {index}: {e}")
                    df.at[index, 'converted_amount'] = None
                    df.at[index, 'conversion_timestamp'] = f"Error: {str(e)}"
                    df.at[index, 'conversion_rate'] = None

            # Save output CSV
            df.to_csv(output_file, index=False)
            logger.info(f"Batch conversion completed. Results saved to {output_file}")

        except FileNotFoundError:
            raise FileNotFoundError(f"Input file '{input_file}' not found")
        except pd.errors.EmptyDataError:
            raise ValueError("Input CSV file is empty")
        except Exception as e:
            logger.error(f"Batch conversion failed: {e}")
            raise

    def get_supported_currencies(self) -> List[str]:
        """
        Get list of supported currency codes.

        Returns:
            List of supported currency codes
        """
        rates = self.get_rates()
        currencies = list(rates.keys())
        currencies.append("USD")  # USD is always supported as base
        return sorted(currencies)

    def is_offline_mode(self) -> bool:
        """
        Check if the converter is in offline mode (using stale cache).

        Returns:
            True if using stale cached data, False otherwise
        """
        return bool(self.rates) and self._is_cache_stale()

"""
Comprehensive unit tests for the currency converter.
"""

import json
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

import pandas as pd
import requests

from currency_converter.core import CurrencyConverter
from currency_converter.utils import (
    validate_currency_code,
    format_currency_amount,
    calculate_conversion_rate,
    get_currency_symbol,
    format_timestamp,
    create_conversion_summary,
    validate_csv_columns,
    sanitize_filename,
    estimate_conversion_time,
    get_cache_info
)


class TestCurrencyConverter(unittest.TestCase):
    """Test cases for CurrencyConverter class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.cache_file = self.temp_dir / "test_rates.json"
        self.converter = CurrencyConverter(cache_file=str(self.cache_file))

        # Mock exchange rates
        self.sample_rates = {
            "EUR": 0.85,
            "GBP": 0.73,
            "JPY": 110.0,
            "CAD": 1.25,
            "AUD": 1.35
        }

    def tearDown(self):
        """Clean up test fixtures."""
        if self.cache_file.exists():
            self.cache_file.unlink()

    def test_initialization(self):
        """Test converter initialization."""
        self.assertEqual(self.converter.cache_file, self.cache_file)
        self.assertEqual(self.converter.api_url, "https://api.exchangerate-api.com/v4/latest")
        self.assertEqual(self.converter.cache_duration, timedelta(hours=1))

    def test_load_cached_rates_empty_file(self):
        """Test loading rates from empty cache file."""
        # Create empty cache file
        self.cache_file.write_text("")
        converter = CurrencyConverter(cache_file=str(self.cache_file))
        self.assertEqual(converter.rates, {})
        self.assertIsNone(converter.last_updated)

    def test_load_cached_rates_valid_data(self):
        """Test loading rates from valid cache file."""
        cache_data = {
            "rates": self.sample_rates,
            "last_updated": "2023-01-01T12:00:00"
        }
        self.cache_file.write_text(json.dumps(cache_data))

        converter = CurrencyConverter(cache_file=str(self.cache_file))
        self.assertEqual(converter.rates, self.sample_rates)
        self.assertIsNotNone(converter.last_updated)

    def test_load_cached_rates_invalid_json(self):
        """Test loading rates from invalid JSON cache file."""
        self.cache_file.write_text("invalid json")
        converter = CurrencyConverter(cache_file=str(self.cache_file))
        self.assertEqual(converter.rates, {})

    @patch('requests.get')
    def test_fetch_live_rates_success(self, mock_get):
        """Test successful fetching of live rates."""
        mock_response = Mock()
        mock_response.json.return_value = {"rates": self.sample_rates}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = self.converter.fetch_live_rates()

        self.assertTrue(result)
        self.assertEqual(self.converter.rates, self.sample_rates)
        self.assertIsNotNone(self.converter.last_updated)
        mock_get.assert_called_once()

    @patch('requests.get')
    def test_fetch_live_rates_api_failure(self, mock_get):
        """Test handling of API failure."""
        mock_get.side_effect = requests.exceptions.RequestException("API Error")

        result = self.converter.fetch_live_rates()

        self.assertFalse(result)
        self.assertEqual(self.converter.rates, {})

    @patch('requests.get')
    def test_fetch_live_rates_invalid_payload_does_not_clobber_cache(self, mock_get):
        """Rates response without usable data should not overwrite cached rates."""
        mock_response = Mock()
        mock_response.json.return_value = {"foo": "bar"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        self.converter.rates = self.sample_rates.copy()
        last_updated = datetime.now() - timedelta(minutes=5)
        self.converter.last_updated = last_updated

        result = self.converter.fetch_live_rates()

        self.assertFalse(result)
        self.assertEqual(self.converter.rates, self.sample_rates)
        self.assertEqual(self.converter.last_updated, last_updated)

    def test_is_cache_stale_fresh_cache(self):
        """Test cache staleness with fresh data."""
        self.converter.last_updated = datetime.now() - timedelta(minutes=30)
        self.converter.rates = self.sample_rates

        self.assertFalse(self.converter._is_cache_stale())

    def test_is_cache_stale_old_cache(self):
        """Test cache staleness with old data."""
        self.converter.last_updated = datetime.now() - timedelta(hours=2)
        self.converter.rates = self.sample_rates

        self.assertTrue(self.converter._is_cache_stale())

    def test_is_cache_stale_no_data(self):
        """Test cache staleness with no data."""
        self.converter.last_updated = None
        self.converter.rates = {}

        self.assertTrue(self.converter._is_cache_stale())

    def test_is_offline_mode_returns_boolean(self):
        """Offline mode detection should yield a boolean."""
        self.converter.rates = self.sample_rates
        self.converter.last_updated = datetime.now() - timedelta(hours=2)

        self.assertTrue(self.converter.is_offline_mode())
        self.assertIsInstance(self.converter.is_offline_mode(), bool)

    @patch.object(CurrencyConverter, 'fetch_live_rates')
    def test_get_rates_fresh_cache(self, mock_fetch):
        """Test getting rates with fresh cache."""
        self.converter.rates = self.sample_rates
        self.converter.last_updated = datetime.now()

        rates = self.converter.get_rates()

        self.assertEqual(rates, self.sample_rates)
        mock_fetch.assert_not_called()

    @patch.object(CurrencyConverter, 'fetch_live_rates')
    def test_get_rates_stale_cache_success(self, mock_fetch):
        """Test getting rates with stale cache and successful refresh."""
        self.converter.rates = self.sample_rates
        self.converter.last_updated = datetime.now() - timedelta(hours=2)
        mock_fetch.return_value = True

        rates = self.converter.get_rates()

        self.assertEqual(rates, self.sample_rates)
        mock_fetch.assert_called_once()

    @patch.object(CurrencyConverter, 'fetch_live_rates')
    def test_get_rates_stale_cache_failure(self, mock_fetch):
        """Test getting rates with stale cache and failed refresh."""
        self.converter.rates = self.sample_rates
        self.converter.last_updated = datetime.now() - timedelta(hours=2)
        mock_fetch.return_value = False

        rates = self.converter.get_rates()

        self.assertEqual(rates, self.sample_rates)
        mock_fetch.assert_called_once()

    def test_convert_same_currency(self):
        """Test converting between same currency."""
        self.converter.rates = self.sample_rates
        self.converter.last_updated = datetime.now()

        amount, timestamp = self.converter.convert(100, "USD", "USD")

        self.assertEqual(amount, 100)
        self.assertIsNotNone(timestamp)

    def test_convert_different_currencies(self):
        """Test converting between different currencies."""
        self.converter.rates = self.sample_rates
        self.converter.last_updated = datetime.now()

        amount, timestamp = self.converter.convert(100, "USD", "EUR")

        expected = 100 * self.sample_rates["EUR"]
        self.assertEqual(amount, round(expected, 2))
        self.assertIsNotNone(timestamp)

    def test_convert_invalid_currency(self):
        """Test converting with invalid currency."""
        self.converter.rates = self.sample_rates
        self.converter.last_updated = datetime.now()

        with self.assertRaises(ValueError):
            self.converter.convert(100, "INVALID", "EUR")

    def test_convert_negative_amount(self):
        """Test converting negative amount."""
        with self.assertRaises(ValueError):
            self.converter.convert(-100, "USD", "EUR")

    @patch.object(CurrencyConverter, 'fetch_live_rates')
    def test_convert_no_rates_available(self, mock_fetch):
        """Test converting when no rates are available."""
        # Clear rates to simulate no data available
        self.converter.rates = {}
        self.converter.last_updated = None
        mock_fetch.return_value = False  # API fails

        with self.assertRaises(RuntimeError):
            self.converter.convert(100, "USD", "EUR")

    @patch('requests.get')
    def test_get_historical_rates_success(self, mock_get):
        """Test successful historical rate fetching."""
        mock_response = Mock()
        mock_response.json.return_value = {"rates": self.sample_rates}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        rates = self.converter.get_historical_rates("2023-01-01")

        self.assertEqual(rates, self.sample_rates)
        mock_get.assert_called_once()

    @patch('requests.get')
    def test_get_historical_rates_api_failure(self, mock_get):
        """Test historical rate fetching with API failure."""
        mock_get.side_effect = requests.exceptions.RequestException("API Error")

        with self.assertRaises(RuntimeError):
            self.converter.get_historical_rates("2023-01-01")

    def test_get_historical_rates_invalid_date(self):
        """Test historical rate fetching with invalid date."""
        with self.assertRaises(ValueError):
            self.converter.get_historical_rates("invalid-date")

    def test_get_historical_rates_future_date(self):
        """Test historical rate fetching with future date."""
        future_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

        with self.assertRaises(ValueError):
            self.converter.get_historical_rates(future_date)

    def test_convert_historical_success(self):
        """Test successful historical conversion."""
        with patch.object(self.converter, 'get_historical_rates', return_value=self.sample_rates):
            amount, date = self.converter.convert_historical(100, "USD", "EUR", "2023-01-01")

            expected = 100 * self.sample_rates["EUR"]
            self.assertEqual(amount, round(expected, 2))
            self.assertEqual(date, "2023-01-01")

    def test_convert_historical_negative_amount(self):
        """Test historical conversion with negative amount."""
        with self.assertRaises(ValueError):
            self.converter.convert_historical(-100, "USD", "EUR", "2023-01-01")

    def test_batch_convert_csv_success(self):
        """Test successful batch CSV conversion."""
        # Create test CSV
        test_data = {
            'amount': [100, 200],
            'from_currency': ['USD', 'EUR'],
            'to_currency': ['EUR', 'USD']
        }
        input_file = self.temp_dir / "input.csv"
        output_file = self.temp_dir / "output.csv"

        df = pd.DataFrame(test_data)
        df.to_csv(input_file, index=False)

        # Mock rates
        self.converter.rates = self.sample_rates
        self.converter.last_updated = datetime.now()

        self.converter.batch_convert_csv(str(input_file), str(output_file),
                                       'amount', 'from_currency', 'to_currency')

        # Verify output file exists and has correct columns
        self.assertTrue(output_file.exists())
        result_df = pd.read_csv(output_file)
        self.assertIn('converted_amount', result_df.columns)
        self.assertIn('conversion_timestamp', result_df.columns)
        self.assertIn('conversion_rate', result_df.columns)

    def test_batch_convert_csv_missing_file(self):
        """Test batch conversion with missing input file."""
        with self.assertRaises(FileNotFoundError):
            self.converter.batch_convert_csv("nonexistent.csv", "output.csv",
                                           'amount', 'from_currency', 'to_currency')

    def test_batch_convert_csv_missing_columns(self):
        """Test batch conversion with missing columns."""
        # Create test CSV with missing columns
        test_data = {'amount': [100]}
        input_file = self.temp_dir / "input.csv"
        output_file = self.temp_dir / "output.csv"

        df = pd.DataFrame(test_data)
        df.to_csv(input_file, index=False)

        with self.assertRaises(ValueError):
            self.converter.batch_convert_csv(str(input_file), str(output_file),
                                           'amount', 'from_currency', 'to_currency')

    def test_get_supported_currencies(self):
        """Test getting supported currencies."""
        self.converter.rates = self.sample_rates
        self.converter.last_updated = datetime.now()

        currencies = self.converter.get_supported_currencies()

        self.assertIn("USD", currencies)
        for currency in self.sample_rates.keys():
            self.assertIn(currency, currencies)
        self.assertEqual(len(currencies), len(self.sample_rates) + 1)

    def test_is_offline_mode_true(self):
        """Test offline mode detection when using stale cache."""
        self.converter.rates = self.sample_rates
        self.converter.last_updated = datetime.now() - timedelta(hours=2)

        self.assertTrue(self.converter.is_offline_mode())

    def test_is_offline_mode_false(self):
        """Test offline mode detection with fresh cache."""
        self.converter.rates = self.sample_rates
        self.converter.last_updated = datetime.now()

        self.assertFalse(self.converter.is_offline_mode())


class TestUtils(unittest.TestCase):
    """Test cases for utility functions."""

    def test_validate_currency_code_valid(self):
        """Test currency code validation with valid codes."""
        self.assertTrue(validate_currency_code("USD"))
        self.assertTrue(validate_currency_code("eur"))
        self.assertTrue(validate_currency_code("  GBP  "))

    def test_validate_currency_code_invalid(self):
        """Test currency code validation with invalid codes."""
        self.assertFalse(validate_currency_code("US"))
        self.assertFalse(validate_currency_code("USDD"))
        self.assertFalse(validate_currency_code("123"))
        self.assertFalse(validate_currency_code("US$"))
        self.assertFalse(validate_currency_code(None))
        self.assertFalse(validate_currency_code(123))

    def test_format_currency_amount(self):
        """Test currency amount formatting."""
        self.assertEqual(format_currency_amount(1234.56, "USD"), "1,234.56 USD")
        self.assertEqual(format_currency_amount(0, "EUR"), "0.00 EUR")
        self.assertEqual(format_currency_amount(None, "GBP"), "N/A")
        self.assertEqual(format_currency_amount(100, "JPY", 0), "100 JPY")

    def test_calculate_conversion_rate(self):
        """Test conversion rate calculation."""
        rates = {"EUR": 0.85, "GBP": 0.73}

        # Same currency
        self.assertEqual(calculate_conversion_rate("USD", "USD", rates), 1.0)

        # USD to other
        self.assertEqual(calculate_conversion_rate("USD", "EUR", rates), 0.85)

        # Other to USD
        self.assertEqual(calculate_conversion_rate("EUR", "USD", rates), 1/0.85)

        # Other to other
        expected = 0.73 / 0.85
        self.assertEqual(calculate_conversion_rate("EUR", "GBP", rates), expected)

    def test_get_currency_symbol(self):
        """Test currency symbol retrieval."""
        self.assertEqual(get_currency_symbol("USD"), "$")
        self.assertEqual(get_currency_symbol("EUR"), "€")
        self.assertEqual(get_currency_symbol("GBP"), "£")
        self.assertEqual(get_currency_symbol("INVALID"), "INVALID")

    def test_format_timestamp(self):
        """Test timestamp formatting."""
        self.assertEqual(format_timestamp("N/A"), "N/A")
        self.assertEqual(format_timestamp(""), "N/A")
        self.assertEqual(format_timestamp(None), "N/A")

        # Valid timestamp
        timestamp = "2023-01-01T12:00:00"
        formatted = format_timestamp(timestamp)
        self.assertIn("2023-01-01", formatted)
        self.assertIn("12:00:00", formatted)

    def test_create_conversion_summary(self):
        """Test conversion summary creation."""
        summary = create_conversion_summary(100, "USD", "EUR", 85.0, "2023-01-01T12:00:00", 0.85)

        self.assertIn("100", summary)
        self.assertIn("85.0", summary)
        self.assertIn("USD", summary)
        self.assertIn("EUR", summary)
        self.assertIn("0.85", summary)

    def test_validate_csv_columns_valid(self):
        """Test CSV column validation with valid columns."""
        df_columns = ["amount", "from_currency", "to_currency"]
        required_columns = ["amount", "from_currency"]

        missing = validate_csv_columns(df_columns, required_columns)
        self.assertEqual(missing, [])

    def test_validate_csv_columns_missing(self):
        """Test CSV column validation with missing columns."""
        df_columns = ["amount", "from_currency"]
        required_columns = ["amount", "from_currency", "to_currency"]

        with self.assertRaises(ValueError):
            validate_csv_columns(df_columns, required_columns)

    def test_sanitize_filename(self):
        """Test filename sanitization."""
        self.assertEqual(sanitize_filename("test.csv"), "test.csv")
        self.assertEqual(sanitize_filename("test<file>.csv"), "test_file_.csv")
        self.assertEqual(sanitize_filename("  .csv  "), "csv")
        self.assertEqual(sanitize_filename(""), "conversion_result")

    def test_estimate_conversion_time(self):
        """Test conversion time estimation."""
        self.assertEqual(estimate_conversion_time(5), "less than 1 second")
        self.assertEqual(estimate_conversion_time(50), "1-2 seconds")
        self.assertEqual(estimate_conversion_time(500), "2-5 seconds")
        self.assertIn("seconds", estimate_conversion_time(2000))

    def test_get_cache_info_nonexistent(self):
        """Test cache info for nonexistent file."""
        info = get_cache_info("nonexistent.json")

        self.assertEqual(info["exists"], "No")
        self.assertEqual(info["size"], "N/A")

    def test_get_cache_info_existing(self):
        """Test cache info for existing file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"rates": {"USD": 1.0}}, f)
            cache_file = f.name

        try:
            info = get_cache_info(cache_file)

            self.assertEqual(info["exists"], "Yes")
            self.assertNotEqual(info["size"], "N/A")
            self.assertEqual(info["rates_count"], "1")
        finally:
            Path(cache_file).unlink()


if __name__ == '__main__':
    unittest.main()

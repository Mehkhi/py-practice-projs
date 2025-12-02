# Currency Converter

A professional command-line currency converter with live exchange rates, batch processing, and comprehensive error handling.

## Features

### Core Features
- 💱 **Live Exchange Rates**: Fetch real-time exchange rates from reliable APIs
- 🔄 **Multi-Currency Support**: Convert between 160+ supported currencies
- 📊 **Batch Processing**: Convert currencies in bulk from CSV files
- 📅 **Historical Rates**: Look up exchange rates for specific dates
- 💾 **Intelligent Caching**: Automatic fallback to cached rates when API fails
- ⚡ **Offline Mode**: Continue working with cached data when offline
- 🛡️ **Error Handling**: Comprehensive error handling and validation
- 📝 **Detailed Logging**: Configurable logging for debugging and monitoring

### Bonus Features
- 🚨 **Rate Change Alerts**: Monitor significant currency rate changes
- 📈 **Conversion History**: Track conversion history and trends
- 🎯 **Precision Control**: Configurable decimal precision for results
- 📋 **Sample Data**: Generate sample CSV files for testing

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup

1. **Clone or download the project**:
   ```bash
   git clone <repository-url>
   cd 03-currency-converter
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify installation**:
   ```bash
   python -m currency_converter --help
   ```

## Usage

### Basic Currency Conversion

Convert a single amount between currencies:

```bash
# Convert 100 USD to EUR
python -m currency_converter convert 100 USD EUR

# Convert 250 EUR to GBP
python -m currency_converter convert 250 EUR GBP

# Convert 1000 JPY to USD
python -m currency_converter convert 1000 JPY USD
```

### Historical Conversion

Convert using historical exchange rates:

```bash
# Convert 100 USD to EUR using rates from January 1, 2023
python -m currency_converter historical 100 USD EUR --date 2023-01-01

# Convert 500 GBP to CAD using rates from December 25, 2022
python -m currency_converter historical 500 GBP CAD --date 2022-12-25
```

### Batch Processing

Convert multiple currencies from a CSV file:

```bash
# Basic batch conversion
python -m currency_converter batch input.csv output.csv

# Custom column names
python -m currency_converter batch input.csv output.csv \
    --amount-column "value" \
    --from-column "source_currency" \
    --to-column "target_currency"
```

**CSV Format**:
```csv
amount,from_currency,to_currency
100,USD,EUR
250,EUR,GBP
500,GBP,JPY
```

### List Supported Currencies

View all supported currency codes:

```bash
python -m currency_converter list
```

### Refresh Exchange Rates

Force refresh exchange rates from the API:

```bash
python -m currency_converter refresh
```

### Create Sample Data

Generate a sample CSV file for testing:

```bash
python -m currency_converter sample sample_data.csv
```

## Configuration

### Environment Variables

- `CURRENCY_CONVERTER_CACHE_FILE`: Path to cache file (default: `exchange_rates.json`)
- `CURRENCY_CONVERTER_CACHE_DURATION`: Cache duration in hours (default: 1)

### Cache Management

The converter automatically caches exchange rates to improve performance and enable offline operation:

- **Cache Location**: `exchange_rates.json` in the current directory
- **Cache Duration**: 1 hour (configurable)
- **Fallback Behavior**: Uses cached data when API is unavailable
- **Offline Warning**: Displays warning when using stale cached data

## Examples

### Example 1: Basic Conversion

```bash
$ python -m currency_converter convert 100 USD EUR

💰 Currency Conversion Result:
   100 USD = 85.00 EUR
   Last updated: 2023-12-07T14:30:00
```

### Example 2: Batch Conversion

```bash
$ python -m currency_converter batch conversions.csv results.csv

✅ Batch conversion completed!
   Input: conversions.csv
   Output: results.csv
```

**Input CSV** (`conversions.csv`):
```csv
amount,from_currency,to_currency
100,USD,EUR
250,EUR,GBP
500,GBP,JPY
1000,JPY,USD
```

**Output CSV** (`results.csv`):
```csv
amount,from_currency,to_currency,converted_amount,conversion_timestamp,conversion_rate
100,USD,EUR,85.00,2023-12-07T14:30:00,0.850000
250,EUR,GBP,212.50,2023-12-07T14:30:00,0.850000
500,GBP,JPY,75000.00,2023-12-07T14:30:00,150.000000
1000,JPY,USD,6.67,2023-12-07T14:30:00,0.006667
```

### Example 3: Historical Conversion

```bash
$ python -m currency_converter historical 100 USD EUR --date 2023-01-01

📅 Historical Currency Conversion Result:
   100 USD = 84.50 EUR
   Date: 2023-01-01
```

### Example 4: Offline Mode

```bash
$ python -m currency_converter convert 100 USD EUR

💰 Currency Conversion Result:
   100 USD = 85.00 EUR
   Last updated: 2023-12-07T12:00:00 (OFFLINE MODE - using cached data)
```

## API Integration

The converter uses the [ExchangeRate-API](https://exchangerate-api.com/) for live exchange rates:

- **Free Tier**: 1,500 requests per month
- **Rate Limit**: 1 request per second
- **Coverage**: 160+ currencies
- **Update Frequency**: Real-time

### Fallback Strategy

1. **Primary**: Fetch live rates from API
2. **Fallback**: Use cached rates if API fails
3. **Error**: Raise exception if no data available

## Error Handling

The converter handles various error conditions gracefully:

- **Invalid Currency Codes**: Clear error messages for unsupported currencies
- **API Failures**: Automatic fallback to cached data
- **Network Issues**: Timeout handling and retry logic
- **Invalid Input**: Validation for amounts, dates, and file formats
- **File Errors**: Proper handling of missing or corrupted files

## Logging

Enable verbose logging for debugging:

```bash
python -m currency_converter convert 100 USD EUR --verbose
```

Log levels:
- **INFO**: General operation information
- **WARNING**: Non-critical issues (e.g., using stale cache)
- **ERROR**: Critical errors (e.g., API failures)
- **DEBUG**: Detailed debugging information

## Testing

Run the comprehensive test suite:

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=currency_converter

# Run specific test file
python -m pytest tests/test_currency_converter.py

# Run with verbose output
python -m pytest tests/ -v
```

### Test Coverage

The test suite covers:
- ✅ Core conversion functionality
- ✅ API integration and error handling
- ✅ Caching and offline mode
- ✅ Batch processing
- ✅ Historical rate lookups
- ✅ Input validation
- ✅ Edge cases and error conditions

## Performance

### Typical Performance
- **Single Conversion**: < 100ms (with cache)
- **API Fetch**: 1-3 seconds
- **Batch Processing**: ~10ms per conversion
- **Memory Usage**: < 10MB

### Optimization Tips
- Use cached rates when possible
- Batch multiple conversions together
- Avoid frequent API calls
- Use appropriate precision settings

## Troubleshooting

### Common Issues

**1. API Rate Limiting**
```
Error: API rate limit exceeded
Solution: Wait a moment and try again, or use cached rates
```

**2. Invalid Currency Code**
```
Error: Currency 'INVALID' not supported
Solution: Use 'python -m currency_converter list' to see supported currencies
```

**3. Network Connectivity**
```
Error: Failed to fetch live rates
Solution: Check internet connection or use offline mode
```

**4. Invalid Date Format**
```
Error: Invalid date format
Solution: Use YYYY-MM-DD format (e.g., 2023-01-01)
```

### Debug Mode

Enable debug logging to troubleshoot issues:

```bash
python -m currency_converter convert 100 USD EUR --verbose
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Changelog

### Version 1.0.0
- Initial release
- Live exchange rate fetching
- Batch CSV processing
- Historical rate lookups
- Comprehensive error handling
- Offline mode support
- Full test coverage

## Support

For issues, questions, or contributions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review the test cases for usage examples

## Acknowledgments

- [ExchangeRate-API](https://exchangerate-api.com/) for providing free exchange rate data
- Python community for excellent libraries (requests, pandas, etc.)
- Contributors and testers

---

**Note**: This tool is for educational and personal use. For production financial applications, consider using professional financial data providers and appropriate compliance measures.

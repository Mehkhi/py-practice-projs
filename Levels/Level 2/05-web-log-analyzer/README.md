# Web Log Analyzer

A professional CLI tool for analyzing Apache and Nginx web server access logs. This tool provides comprehensive insights into web traffic patterns, error analysis, performance metrics, and user behavior.

## Features

### Core Features
- **Multi-format Support**: Parse Apache Common, Apache Combined, and Nginx log formats
- **Auto-detection**: Automatically detect log format from sample data
- **Comprehensive Analysis**: Generate detailed statistics including:
  - Request counts and unique visitors
  - Status code distribution
  - Top endpoints and IP addresses
  - Error analysis (404s, 5xx errors)
  - Traffic patterns by hour and day
  - User agent and browser analysis
  - Performance metrics (when response time data is available)

### Output Formats
- **Text Reports**: Human-readable summaries
- **CSV Reports**: Spreadsheet-compatible data
- **JSON Reports**: Machine-readable structured data
- **Console Output**: Quick summaries for terminal use

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup
```bash
# Clone or download the project
cd 05-web-log-analyzer

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Basic Usage
```bash
# Analyze a log file with auto-detected format
python -m web_log_analyzer access.log

# Specify log format explicitly
python -m web_log_analyzer access.log --format nginx

# Generate a text report
python -m web_log_analyzer access.log --output report.txt

# Generate multiple format reports in a directory
python -m web_log_analyzer access.log --output-dir reports/ --format-output all
```

### Advanced Options
```bash
# Show top 20 items instead of default 10
python -m web_log_analyzer access.log --top 20

# Include performance analysis (requires response time data)
python -m web_log_analyzer access.log --include-performance

# Verbose logging for debugging
python -m web_log_analyzer access.log --verbose

# Quiet mode (errors only)
python -m web_log_analyzer access.log --quiet

# Generate sample log entry for testing
python -m web_log_analyzer --sample
```

### Command Line Options

| Option | Description |
|--------|-------------|
| `log_file` | Path to the log file to analyze |
| `--format`, `-f` | Log format: common, combined, nginx, nginx_time, auto (default: auto) |
| `--output`, `-o` | Output file path (default: stdout) |
| `--output-dir` | Output directory for multiple format reports |
| `--format-output` | Output format: text, csv, json, all (default: text) |
| `--top`, `-t` | Number of top items to show (default: 10) |
| `--verbose`, `-v` | Enable verbose logging |
| `--quiet`, `-q` | Suppress non-error output |
| `--sample` | Generate a sample log entry and exit |
| `--include-performance` | Include performance analysis |

## Supported Log Formats

### Apache Combined Log Format
```
127.0.0.1 - - [25/Dec/2023:10:00:00 +0000] "GET /index.html HTTP/1.1" 200 1234 "http://example.com" "Mozilla/5.0"
```

### Apache Common Log Format
```
127.0.0.1 - - [25/Dec/2023:10:00:00 +0000] "GET /index.html HTTP/1.1" 200 1234
```

### Nginx Default Format
```
127.0.0.1 - user [25/Dec/2023:10:00:00 +0000] "GET /index.html HTTP/1.1" 200 1234 "http://example.com" "Mozilla/5.0"
```

### Nginx Format with Response Time
```
127.0.0.1 - - [25/Dec/2023:10:00:00 +0000] "GET /index.html HTTP/1.1" 200 1234 "http://example.com" "Mozilla/5.0" 1234567
```

## Output Examples

### Console Summary
```
Web Log Analysis Summary
========================================
Total Requests: 15,432
Unique IPs: 1,234
Time Range: 2023-12-25T10:00:00 to 2023-12-25T18:00:00
Total Bytes: 1,234,567,890
Errors: 234 (1.5%)

Top Endpoints:
  1. /index.html: 3,456
  2. /api/data: 2,345
  3. /about.html: 1,234

Top IPs:
  1. 192.168.1.100: 234
  2. 10.0.0.50: 189
  3. 172.16.0.25: 156
```

### Text Report Structure
- Basic Statistics (requests, IPs, bytes, time range)
- Status Code Distribution
- Top Endpoints
- Top IP Addresses
- Error Analysis (404s, 5xx errors)
- Traffic Patterns (hourly/daily distribution)
- Performance Analysis (when available)
- User Agent Analysis

## Configuration

### Environment Variables
- `LOG_LEVEL`: Set default logging level (DEBUG, INFO, WARNING, ERROR)

### Log Format Customization
The tool supports the most common log formats out of the box. If you have a custom format, you can:
1. Use the `--format auto` option for best-effort detection
2. Modify the regex patterns in `core.py` for your specific format

## Examples

### Analyze Apache Access Log
```bash
python -m web_log_analyzer /var/log/apache2/access.log --format combined --output apache_analysis.txt
```

### Analyze Nginx Access Log with Performance Data
```bash
python -m web_log_analyzer /var/log/nginx/access.log --format nginx_time --include-performance --output nginx_performance.json --format-output json
```

### Generate All Report Formats
```bash
python -m web_log_analyzer access.log --output-dir reports/ --format-output all --top 20
```

### Quick Analysis in Terminal
```bash
python -m web_log_analyzer access.log --quiet
```

## Development

### Running Tests
```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=web_log_analyzer

# Run specific test file
pytest tests/test_web_log_analyzer.py
```

### Code Quality
```bash
# Format code
black web_log_analyzer/ tests/

# Lint code
ruff check web_log_analyzer/ tests/

# Type checking (if using mypy)
mypy web_log_analyzer/
```

### Project Structure
```
05-web-log-analyzer/
├── web_log_analyzer/          # Main package
│   ├── __init__.py           # Package initialization
│   ├── __main__.py           # Package entry point
│   ├── core.py               # Core parsing and analysis logic
│   ├── main.py               # CLI interface and main logic
│   └── utils.py              # Utility functions
├── tests/                    # Test suite
│   ├── __init__.py
│   └── test_web_log_analyzer.py
├── requirements.txt          # Dependencies
├── README.md                # This file
├── CHECKLIST.md             # Feature checklist
└── SPEC.md                  # Project specification
```

## Performance Considerations

- **Memory Usage**: The tool loads all log entries into memory. For very large files (>1GB), consider splitting the log file.
- **Processing Speed**: Approximately 10,000-50,000 log lines per second depending on format complexity.
- **File I/O**: Uses buffered reading for efficient file processing.

## Limitations

- Requires log files to be in supported formats or close variants
- Response time analysis only works with logs that include timing data
- Geo-IP analysis and HTML dashboard generation are not implemented in the base version
- Large files (>1GB with millions of entries) may require significant memory

## Troubleshooting

### Common Issues

**"No valid log entries found"**
- Check if the log file is empty or corrupted
- Verify the log format with `--format` option
- Use `--verbose` to see parsing details

**"Failed to parse timestamp"**
- Check if timestamps are in expected format
- Try different log format options
- Some custom timestamp formats may not be supported

**Memory errors with large files**
- Process smaller chunks of the log file
- Consider using log splitting tools
- Monitor system memory usage

### Debug Mode
```bash
python -m web_log_analyzer access.log --verbose --format combined
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

This project is part of the Python Practice Projects collection and is provided for educational purposes.

## Changelog

### Version 1.0.0
- Initial release
- Support for Apache and Nginx log formats
- Basic and advanced analysis features
- Multiple output formats
- Comprehensive test suite
- Complete documentation

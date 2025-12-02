# Basic Web Scraper

A professional CLI tool for extracting data from websites with support for pagination, multiple output formats, and robust error handling.

## Features

- **HTML Fetching**: Retrieve web pages using the requests library
- **BeautifulSoup Parsing**: Parse HTML content with lxml backend
- **Element Extraction**: Extract titles, links, and prices from web pages
- **Pagination Support**: Automatically follow "next" links for multi-page content
- **Multiple Output Formats**: Save results to JSON or CSV files
- **Error Handling**: Comprehensive error handling and logging
- **Rate Limiting**: Built-in delays to be respectful to web servers
- **Configurable**: Custom CSS selectors for different website structures

## Installation

1. Clone or download this project
2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage

Scrape a single web page:
```bash
python -m basic_web_scraper https://example.com
```

### Advanced Usage

Scrape multiple pages with pagination:
```bash
python -m basic_web_scraper https://example.com --max-pages 5
```

Save results to JSON:
```bash
python -m basic_web_scraper https://example.com --output results.json
```

Save results to CSV:
```bash
python -m basic_web_scraper https://example.com --output results.csv
```

### Custom Selectors

Use custom CSS selectors for titles:
```bash
python -m basic_web_scraper https://example.com --title-selector "h1.title"
```

Specify custom price patterns:
```bash
python -m basic_web_scraper https://example.com --price-patterns ".price,.cost,[data-price]"
```

Custom next page selectors:
```bash
python -m basic_web_scraper https://example.com --next-selectors ".next,.pagination-next"
```

### Rate Limiting and Timeouts

Set custom delay and timeout:
```bash
python -m basic_web_scraper https://example.com --delay 2 --timeout 15
```

### Verbose Logging

Enable verbose logging for debugging:
```bash
python -m basic_web_scraper https://example.com --verbose
```

## Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `url` | URL to scrape (required) | - |
| `--max-pages` | Maximum number of pages to scrape | 1 |
| `--output`, `-o` | Output file (.json or .csv) | - |
| `--delay` | Delay between requests in seconds | 1.0 |
| `--timeout` | Request timeout in seconds | 10 |
| `--title-selector` | CSS selector for title elements | "h1, h2, h3" |
| `--price-patterns` | Comma-separated CSS selectors for prices | - |
| `--next-selectors` | Comma-separated CSS selectors for next page | - |
| `--verbose`, `-v` | Enable verbose logging | False |
| `--version` | Show version information | - |

## Output Formats

### JSON Output

The JSON format includes all extracted data:
```json
[
  {
    "url": "https://example.com",
    "titles": ["Main Title", "Subtitle"],
    "links": [
      {
        "url": "https://example.com/page1",
        "text": "Link 1",
        "original_href": "/page1"
      }
    ],
    "prices": ["$19.99", "$29.99"],
    "next_page": "/page/2"
  }
]
```

### CSV Output

The CSV format provides a flattened view suitable for spreadsheet applications:
```csv
url,error,titles,prices,link_count,next_page
https://example.com,,Main Title;Subtitle,$19.99;$29.99,1,/page/2
```

## Configuration Examples

### E-commerce Site
```bash
python -m basic_web_scraper https://shop.example.com/products \
  --max-pages 10 \
  --title-selector ".product-title,h1" \
  --price-patterns ".price,.sale-price" \
  --output products.csv \
  --delay 2
```

### News Website
```bash
python -m basic_web_scraper https://news.example.com \
  --max-pages 5 \
  --title-selector "h1.article-title,h2.headline" \
  --next-selectors ".next-page,.more-stories" \
  --output articles.json \
  --verbose
```

### Blog Scraping
```bash
python -m basic_web_scraper https://blog.example.com \
  --max-pages 20 \
  --title-selector ".post-title,h1" \
  --next-selectors ".pagination .next,a[rel='next']" \
  --output blog_posts.csv \
  --delay 1.5
```

## Known Limitations

- **JavaScript-rendered content**: This scraper does not execute JavaScript. For dynamic content, consider using Selenium or Playwright.
- **Anti-bot measures**: Some websites may block automated scraping. Use appropriate delays and user agents.
- **Login-required content**: This tool does not handle authentication.
- **Rate limiting**: Always respect robots.txt and implement reasonable delays.

## Error Handling

The scraper includes comprehensive error handling:

- **Network errors**: Automatic retry with exponential backoff
- **Parsing errors**: Graceful handling of malformed HTML
- **File I/O errors**: Proper error reporting for file operations
- **Invalid URLs**: Validation and error reporting

## Logging

The scraper provides detailed logging for monitoring and debugging:

- **INFO level**: General operation information
- **DEBUG level**: Detailed debugging information (use --verbose)
- **ERROR level**: Error conditions and failures

## Testing

Run the test suite:
```bash
python -m pytest tests/ -v
```

Run with coverage:
```bash
python -m pytest tests/ --cov=basic_web_scraper --cov-report=html
```

## Development

### Project Structure
```
08-basic-web-scraper/
├── basic_web_scraper/          # Package directory
│   ├── __init__.py            # Package initialization
│   ├── __main__.py            # Module entry point
│   ├── main.py                # CLI interface
│   ├── core.py                # Core scraping logic
│   └── utils.py               # Utility functions
├── tests/                     # Test suite
│   ├── __init__.py
│   └── test_basic_web_scraper.py
├── requirements.txt           # Dependencies
├── README.md                  # This file
├── CHECKLIST.md              # Feature checklist
└── SPEC.md                   # Project specification
```

### Code Quality

The project follows Python best practices:

- **Type hints**: All public functions include type hints
- **Docstrings**: Comprehensive documentation for all modules and functions
- **Error handling**: No bare exceptions, specific error handling
- **Logging**: Appropriate logging for debugging and monitoring
- **Testing**: 12+ unit tests with good coverage

### Contributing

1. Follow PEP 8 style guidelines
2. Add type hints to new functions
3. Write tests for new features
4. Update documentation
5. Ensure all tests pass

## License

This project is provided for educational purposes. Please respect website terms of service and robots.txt when scraping.

## Examples

### Real-world Example: Scraping a Book Store
```bash
python -m basic_web_scraper https://books.toscrape.com \
  --max-pages 5 \
  --title-selector "h3 a" \
  --price-patterns ".price_color" \
  --next-selectors ".next a" \
  --output books.csv \
  --delay 1
```

### Real-world Example: Scraping Quotes
```bash
python -m basic_web_scraper https://quotes.toscrape.com \
  --max-pages 10 \
  --title-selector ".quote span.text" \
  --next-selectors ".next a" \
  --output quotes.json \
  --verbose
```

## Troubleshooting

### Common Issues

1. **SSL Certificate Errors**: Some websites may have SSL issues. The scraper uses default SSL settings.
2. **Timeout Errors**: Increase timeout value with `--timeout` option.
3. **Rate Limiting**: Increase delay between requests with `--delay` option.
4. **Empty Results**: Check if the website uses JavaScript or requires authentication.

### Debug Mode

Use verbose logging to troubleshoot issues:
```bash
python -m basic_web_scraper https://example.com --verbose
```

## Performance Tips

1. **Adjust delays**: Balance between politeness and speed
2. **Limit pages**: Use `--max-pages` to avoid excessive requests
3. **Choose appropriate selectors**: Be specific to avoid unnecessary data extraction
4. **Monitor logs**: Watch for errors and warnings

## Security Considerations

- Always validate and sanitize URLs
- Implement rate limiting to avoid overwhelming servers
- Respect robots.txt files
- Don't scrape sensitive or private data
- Use appropriate user agents

## Version History

- **v1.0.0**: Initial release with core functionality
  - HTML fetching and parsing
  - Element extraction (titles, links, prices)
  - Pagination support
  - JSON/CSV output
  - CLI interface
  - Comprehensive testing

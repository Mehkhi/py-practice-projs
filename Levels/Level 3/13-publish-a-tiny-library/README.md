# TextUtils

[![PyPI version](https://badge.fury.io/py/textutils.svg)](https://badge.fury.io/py/textutils)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/yourusername/textutils/workflows/Tests/badge.svg)](https://github.com/yourusername/textutils/actions)
[![codecov](https://codecov.io/gh/yourusername/textutils/branch/main/graph/badge.svg)](https://codecov.io/gh/yourusername/textutils)

A comprehensive string manipulation library for Python, providing utilities for case conversion, text cleaning, validation, and formatting.

## Features

- **Case Conversion**: Convert between camelCase, snake_case, kebab-case, PascalCase, and more
- **Text Cleaning**: Remove extra whitespace, HTML tags, normalize unicode characters
- **String Validation**: Validate emails, URLs, phone numbers, IP addresses, credit cards, and more
- **Text Formatting**: Truncate text, pad strings, format numbers and currency
- **Type Safe**: Full type hints with mypy support
- **Well Tested**: Comprehensive test suite with high coverage

## Installation

```bash
pip install textutils
```

### Development Installation

```bash
git clone https://github.com/yourusername/textutils.git
cd textutils
pip install -e ".[dev]"
```

## Quick Start

```python
from textutils import CaseConverter, TextCleaner, StringValidator, TextFormatter

# Case conversion
camel_case = CaseConverter.to_camel_case("hello_world_test")
# "helloWorldTest"

snake_case = CaseConverter.to_snake_case("helloWorldTest")
# "hello_world_test"

# Text cleaning
clean_text = TextCleaner.remove_extra_whitespace("  Hello    world!  ")
# "Hello world!"

# String validation
is_valid = StringValidator.is_email("user@example.com")
# True

# Text formatting
truncated = TextFormatter.truncate("This is a long text", 10)
# "This is..."
```

## API Reference

### CaseConverter

Convert between different string case formats:

```python
from textutils import CaseConverter

# Convert snake_case to camelCase
CaseConverter.to_camel_case("hello_world")  # "helloWorld"

# Convert camelCase to snake_case
CaseConverter.to_snake_case("helloWorld")   # "hello_world"

# Convert to kebab-case
CaseConverter.to_kebab_case("helloWorld")   # "hello-world"

# Convert to PascalCase
CaseConverter.to_pascal_case("hello_world") # "HelloWorld"

# Convert to SCREAMING_SNAKE_CASE
CaseConverter.to_screaming_snake_case("helloWorld")  # "HELLO_WORLD"
```

### TextCleaner

Clean and normalize text:

```python
from textutils import TextCleaner

# Remove extra whitespace
TextCleaner.remove_extra_whitespace("  Hello    world!  ")
# "Hello world!"

# Remove HTML tags
TextCleaner.remove_html_tags("<p>Hello <strong>world</strong>!</p>")
# "Hello world!"

# Normalize unicode characters
TextCleaner.normalize_unicode("café naïve résumé")
# "cafe naive resume"

# Clean for URL slugs
TextCleaner.clean_for_slug("Hello World! (Test)")
# "hello-world-test"
```

### StringValidator

Validate different types of strings:

```python
from textutils import StringValidator

# Email validation
StringValidator.is_email("user@example.com")  # True

# URL validation
StringValidator.is_url("https://www.example.com")  # True

# Phone number validation
StringValidator.is_phone_number("555-123-4567")  # True

# Strong password check
StringValidator.is_strong_password("MyStr0ng!P@ss")  # True

# Palindrome check
StringValidator.is_palindrome("A man a plan a canal Panama")  # True
```

### TextFormatter

Format text for display:

```python
from textutils import TextFormatter

# Truncate text
TextFormatter.truncate("This is a long text", 15)
# "This is a lo..."

# Format currency
TextFormatter.format_currency(1234.56)
# "$1,234.56"

# Format phone numbers
TextFormatter.format_phone_number("5551234567")
# "(555) 123-4567"

# Format lists
TextFormatter.format_list(["apple", "banana", "cherry"])
# "apple, banana and cherry"
```

## Examples

See the `examples/` directory for runnable examples:

```bash
cd examples
python basic_usage.py
python advanced_formatting.py
```

## Testing

Run the test suite:

```bash
pytest
```

With coverage:

```bash
pytest --cov=textutils --cov-report=html
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Run the tests: `pytest`
4. Commit your changes: `git commit -m 'Add amazing feature'`
5. Push to the branch: `git push origin feature/amazing-feature`
6. Open a Pull Request

### Development Setup

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
flake8 textutils tests

# Type checking
mypy textutils

# Format code
black textutils tests
isort textutils tests
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

## Support

For questions, bug reports, or feature requests, please [open an issue](https://github.com/yourusername/textutils/issues) on GitHub.

# Testing Workshop - Text Analysis CLI Tool

A comprehensive Python CLI tool for text analysis with extensive testing coverage. This project demonstrates professional testing practices including unit tests, fixtures, parametrization, mocking, and CI/CD integration.

## Features

- **Word counting**: Count words in text or files
- **Character analysis**: Count characters with or without spaces
- **Frequency analysis**: Find most frequent words
- **Reading time estimation**: Calculate estimated reading time
- **File processing**: Analyze text files directly
- **Comprehensive testing**: 34+ unit tests with high coverage

## Installation

### Prerequisites

- Python 3.8 or higher
- pip for package management

### Setup

```bash
# Clone the repository
git clone <repository-url>
cd 18-testing-workshop

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Basic Usage

```bash
# Analyze text from command line
python -m testing_workshop "Hello world! This is a sample text for analysis."

# Analyze a text file
python -m testing_workshop --file sample.txt

# Show only word count
python -m testing_workshop --words-only "Hello world!"

# Show only character count
python -m testing_workshop --chars-only "Hello world!"

# Show top N frequent words
python -m testing_workshop --frequent-words 10 --file large_text.txt

# Enable verbose logging
python -m testing_workshop --verbose "Hello world!"
```

### Example Output

```
Text Analysis Results:
----------------------
Word count: 8
Characters (with spaces): 41
Characters (no spaces): 34
Line count: 1
Estimated reading time: 0.04 minutes

Most frequent words:
  hello: 2
  world: 1
  this: 1
  is: 1
  a: 1
```

## Configuration Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--file` | `-f` | Path to text file to analyze | None |
| `--words-only` | `-w` | Show only word count | False |
| `--chars-only` | `-c` | Show only character count | False |
| `--frequent-words` | `-t` | Number of top frequent words to show | 5 |
| `--verbose` | `-v` | Enable verbose logging | False |

## Development

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=testing_workshop --cov-report=html
```

### Code Quality

The project uses:
- **pytest** for testing
- **pytest-cov** for coverage reporting
- **GitHub Actions** for CI/CD
- Type hints throughout the codebase
- Comprehensive docstrings

### Project Structure

```
18-testing-workshop/
├── testing_workshop/          # Main package
│   ├── __init__.py
│   ├── core.py               # Core analysis functions
│   ├── main.py               # CLI entry point
│   └── utils.py              # Utility functions
├── tests/                    # Test suite
│   ├── __init__.py
│   └── test_testing_workshop.py
├── .github/workflows/        # CI/CD configuration
│   └── ci.yml
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── CHECKLIST.md              # Feature checklist
└── SPEC.md                   # Project specifications
```

## Testing

This project demonstrates comprehensive testing practices:

- **34 unit tests** covering all functionality
- **Test fixtures** for reusable test data
- **Parametrization** for testing multiple inputs
- **Mocking** for external dependencies (file I/O)
- **Edge case testing** (empty inputs, error conditions)
- **CI/CD integration** with GitHub Actions

### Test Coverage

The test suite achieves >80% code coverage and includes:

- Core functionality tests
- File operation tests with mocking
- CLI interface tests
- Error handling tests
- Edge case tests

## API Reference

### Core Functions

#### `count_words(text: str) -> int`
Count the number of words in the given text.

#### `count_characters(text: str, include_spaces: bool = True) -> int`
Count characters in text, optionally excluding spaces.

#### `get_most_frequent_words(text: str, n: int = 5) -> List[Tuple[str, int]]`
Get the most frequent words and their counts.

#### `estimate_reading_time(text: str, words_per_minute: int = 200) -> float`
Estimate reading time in minutes.

#### `analyze_text(text: str) -> Dict[str, Any]`
Perform comprehensive text analysis.

### Utility Functions

#### `format_analysis_results(results: Dict[str, Any]) -> str`
Format analysis results for display.

#### `validate_file_path(file_path: str) -> bool`
Validate if a file exists and is readable.

#### `truncate_text(text: str, max_length: int = 100) -> str`
Truncate text with ellipsis if too long.

#### `safe_int_conversion(value: str, default: int = 0) -> int`
Safely convert string to integer with fallback.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Write tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

This project is for educational purposes as part of the Python practice projects series.

## Known Limitations

- Only supports UTF-8 encoded text files
- Word counting uses simple regex pattern (`\b\w+\b`)
- Reading time estimation assumes 200 words per minute
- No support for binary files or non-text content

## Future Enhancements

- Support for multiple file formats (PDF, DOCX)
- Advanced text analysis (sentiment, readability scores)
- Web interface with Flask
- Configuration file support
- Progress bars for large file processing

# Markdown to HTML Converter

A professional command-line tool for converting Markdown files to HTML with syntax highlighting, built with Python.

## Features

- ✅ **Complete Markdown Support**: Headers, bold, italic, lists, links, images, tables, code blocks
- ✅ **Syntax Highlighting**: Code blocks with Pygments-powered syntax highlighting
- ✅ **Standalone HTML**: Generates complete HTML documents with embedded CSS
- ✅ **Multiple Themes**: Support for various syntax highlighting themes
- ✅ **CLI Interface**: Easy-to-use command-line interface
- ✅ **File Validation**: Built-in markdown validation and statistics
- ✅ **Error Handling**: Comprehensive error handling and logging
- ✅ **Extensible**: Easy to extend with custom themes and features

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. **Clone or download the project**:
   ```bash
   cd 07-markdown-html-converter
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

## Usage

### Basic Usage

Convert a markdown file to HTML:
```bash
python -m markdown_html_converter input.md
```

This creates `input.html` in the same directory.

### Advanced Usage

**Specify output file**:
```bash
python -m markdown_html_converter input.md -o output.html
```

**Use a different syntax highlighting theme**:
```bash
python -m markdown_html_converter input.md --theme github
```

**Generate HTML without embedded CSS**:
```bash
python -m markdown_html_converter input.md --no-css
```

**Validate a markdown file**:
```bash
python -m markdown_html_converter --validate input.md
```

**List supported programming languages**:
```bash
python -m markdown_html_converter --languages
```

**Enable verbose logging**:
```bash
python -m markdown_html_converter input.md --verbose
```

### Command Line Options

| Option | Description |
|--------|-------------|
| `input_file` | Input markdown file to convert |
| `-o, --output` | Output HTML file path |
| `-t, --theme` | Syntax highlighting theme (default: default) |
| `--no-css` | Generate HTML without embedded CSS |
| `--validate` | Validate markdown file and show statistics |
| `--languages` | List supported programming languages |
| `-v, --verbose` | Enable verbose logging |
| `--version` | Show version information |

## Supported Markdown Features

### Basic Formatting
- **Headers** (H1-H6): `# Header`, `## Subheader`
- **Bold text**: `**bold**` or `__bold__`
- **Italic text**: `*italic*` or `_italic_`
- **Strikethrough**: `~~strikethrough~~`
- **Inline code**: `` `code` ``

### Lists
- **Unordered lists**: `- Item` or `* Item`
- **Ordered lists**: `1. Item`
- **Nested lists**: Supported with proper indentation

### Code Blocks
- **Fenced code blocks**:
  ```markdown
  ```python
  def hello():
      print("Hello, World!")
  ```
  ```
- **Syntax highlighting**: Automatic detection of 20+ programming languages

### Tables
```markdown
| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Data 1   | Data 2   | Data 3   |
| Data 4   | Data 5   | Data 6   |
```

### Links and Images
- **Links**: `[Link text](https://example.com)`
- **Images**: `![Alt text](image.jpg)`
- **Reference links**: `[Link][ref]` with `[ref]: https://example.com`

### Other Features
- **Blockquotes**: `> Quote text`
- **Horizontal rules**: `---` or `***`
- **Line breaks**: Double space at end of line or `\n\n`

## Supported Programming Languages

The converter supports syntax highlighting for 20+ programming languages including:

- **Web**: HTML, CSS, JavaScript, JSON, XML
- **Python**: Python
- **Java Family**: Java, Kotlin, Scala
- **C Family**: C, C++, C#
- **Scripting**: Bash, Shell, PowerShell, Ruby, PHP
- **Modern**: Go, Rust, Swift
- **Data**: R, SQL, YAML
- **Other**: Dockerfile, Markdown, Text

## Themes

The converter supports various Pygments themes for syntax highlighting:

- `default` (default)
- `github`
- `monokai`
- `vs`
- `xcode`
- And many more...

## Examples

### Example 1: Basic Document

**Input** (`example.md`):
```markdown
# My Project

This is a **sample** document with some *formatting*.

## Code Example

```python
def calculate_sum(a, b):
    """Calculate the sum of two numbers."""
    return a + b

result = calculate_sum(5, 3)
print(f"The result is: {result}")
```

## Features

- [x] Feature 1
- [x] Feature 2
- [ ] Feature 3

## Links

Visit [GitHub](https://github.com) for more information.
```

**Command**:
```bash
python -m markdown_html_converter example.md
```

**Output**: Creates `example.html` with syntax-highlighted code and styled content.

### Example 2: With Custom Theme

```bash
python -m markdown_html_converter example.md --theme github
```

### Example 3: Validation

```bash
python -m markdown_html_converter --validate example.md
```

**Output**:
```
Validation results for: example.md
==================================================
✅ File is valid markdown

Statistics:
  Lines: 25
  Characters: 456
  Words: 78
  Headers: 3
  Code blocks: 1
  Links: 1
  Images: 0
  Tables: 0
```

## Development

### Project Structure

```
07-markdown-html-converter/
├── markdown_html_converter/      # Main package
│   ├── __init__.py
│   ├── main.py                   # CLI interface
│   ├── core.py                   # Core conversion logic
│   └── utils.py                  # Utility functions
├── tests/                        # Test suite
│   ├── __init__.py
│   └── test_markdown_html_converter.py
├── requirements.txt              # Dependencies
├── README.md                     # This file
├── CHECKLIST.md                  # Feature checklist
└── SPEC.md                       # Project specification
```

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=markdown_html_converter
```

### Code Quality

The project follows Python best practices:

- **Type hints** on all public functions
- **Docstrings** for all modules and functions
- **Error handling** with specific exception types
- **Logging** for debugging and monitoring
- **PEP 8** style compliance

## Configuration

### Environment Variables

- `MARKDOWN_CONVERTER_LOG_LEVEL`: Set logging level (DEBUG, INFO, WARNING, ERROR)
- `MARKDOWN_CONVERTER_THEME`: Default theme for syntax highlighting

### Custom Themes

You can create custom themes by extending the `MarkdownConverter` class:

```python
from markdown_html_converter.core import MarkdownConverter

class CustomConverter(MarkdownConverter):
    def _generate_css(self):
        # Your custom CSS here
        return super()._generate_css() + custom_css
```

## Error Handling

The converter handles various error conditions gracefully:

- **File not found**: Clear error message with file path
- **Invalid file format**: Validation for markdown file extensions
- **Encoding issues**: Automatic fallback to latin-1 encoding
- **Syntax errors**: Graceful handling of malformed markdown
- **Permission errors**: Clear error messages for file access issues

## Logging

The converter provides comprehensive logging:

- **INFO**: File conversion progress
- **DEBUG**: Detailed conversion steps
- **WARNING**: Non-critical issues
- **ERROR**: Conversion failures

Enable verbose logging with `--verbose` flag.

## Limitations

- **Large files**: Very large markdown files may take longer to process
- **Complex tables**: Some complex table structures may not render perfectly
- **Custom HTML**: Raw HTML in markdown is not processed
- **Math equations**: LaTeX math is not supported (use HTML entities)

## Troubleshooting

### Common Issues

1. **Import errors**: Make sure all dependencies are installed
   ```bash
   pip install -r requirements.txt
   ```

2. **File encoding issues**: The converter tries UTF-8 first, then falls back to latin-1

3. **Theme not found**: Use `--languages` to see available themes

4. **Permission denied**: Check file permissions and output directory access

### Getting Help

- Check the logs with `--verbose` flag
- Validate your markdown with `--validate` flag
- Ensure input file has `.md` or `.markdown` extension

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is part of the Python Practice Projects collection and is available for educational purposes.

## Changelog

### Version 1.0.0
- Initial release
- Basic markdown to HTML conversion
- Syntax highlighting with Pygments
- CLI interface
- Comprehensive test suite
- Documentation

---

**Happy converting!** 🚀

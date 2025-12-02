# QR Code Generator

A professional command-line tool for generating QR codes with extensive customization options. Supports text, URLs, vCards, batch processing, and multiple output formats.

## Features

### Core Features
- ✅ Generate QR codes from text, URLs, and vCard contact information
- ✅ Support for PNG and SVG output formats
- ✅ Customizable size, error correction levels, and colors
- ✅ Batch generation from CSV files
- ✅ Add logos to QR codes (PNG format)
- ✅ Comprehensive CLI with argparse
- ✅ Extensive error handling and logging

### Customization Options
- **Size**: Adjustable box size in pixels
- **Error Correction**: Four levels (L, M, Q, H) for different data recovery capabilities
- **Colors**: Custom fill and background colors
- **Output Formats**: PNG (raster) and SVG (vector)
- **Batch Processing**: Generate multiple QR codes from CSV data

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup

1. **Clone or download the project**
   ```bash
   cd 22-qr-code-generator
   ```

2. **Create virtual environment (recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify installation**
   ```bash
   python -m qr_code_generator --version
   ```

## Usage

### Basic Usage

#### Generate Text QR Code
```bash
python -m qr_code_generator "Hello World"
```

#### Generate URL QR Code
```bash
python -m qr_code_generator --url "https://example.com"
```

#### Generate vCard QR Code
```bash
python -m qr_code_generator --vcard --name "John Doe" --phone "+1234567890" --email "john@example.com"
```

### Advanced Usage

#### Custom Styling
```bash
python -m qr_code_generator "Custom QR" \
  --size 15 \
  --fill-color blue \
  --back-color white \
  --error-correction H \
  --output custom_qr.png
```

#### Generate SVG Format
```bash
python -m qr_code_generator "Vector QR" --format svg --output vector_qr.svg
```

#### Add Logo to QR Code
```bash
python -m qr_code_generator "Branded QR" --add-logo logo.png
```

### Batch Generation

#### Create CSV File
Create a CSV file with the following structure:

```csv
data,filename,type,size,format,fill_color,back_color
https://google.com,google,url,15,png,black,white
Hello World,hello,text,10,svg,blue,white
Contact Info,contact,text,12,png,red,yellow
```

#### Run Batch Generation
```bash
python -m qr_code_generator --batch data.csv --output-dir ./qr_codes
```

## Command Line Options

### Input Options
- `text` - Plain text to encode (positional argument)
- `--url` - URL to encode
- `--vcard` - Generate vCard QR code
- `--batch` - CSV file for batch generation

### vCard Options
- `--name` - Contact name (required for vCard)
- `--phone` - Phone number
- `--email` - Email address
- `--org` - Organization/company

### Output Options
- `--output, -o` - Output file path
- `--format, -f` - Output format (png, svg)
- `--output-dir` - Directory for batch output

### Customization Options
- `--size, -s` - Box size in pixels (default: 10)
- `--error-correction, -e` - Error correction level (L, M, Q, H)
- `--fill-color` - QR code color (default: black)
- `--back-color` - Background color (default: white)

### Other Options
- `--add-logo` - Path to logo image (PNG only)
- `--verbose, -v` - Enable verbose logging
- `--version` - Show version information

## Error Correction Levels

| Level | Error Correction Capacity | Use Case |
|-------|-------------------------|----------|
| L | ~7% | Clean environments, maximum data capacity |
| M | ~15% | Standard use, good balance |
| Q | ~25% | Industrial environments, moderate damage |
| H | ~30% | Harsh environments, maximum reliability |

## CSV Batch Format

### Required Columns
- `data` - The content to encode in the QR code

### Optional Columns
- `filename` - Custom filename (without extension)
- `type` - Data type (text, url, vcard)
- `size` - Box size in pixels
- `error_correction` - Error correction level (L, M, Q, H)
- `fill_color` - QR code color
- `back_color` - Background color
- `format` - Output format (png, svg)

### Example CSV
```csv
data,filename,type,size,format,fill_color,back_color
https://github.com,github,url,12,png,black,white
Welcome to our event!,event,text,15,svg,blue,white
John Doe - Contact,john_contact,text,10,png,red,white
WiFi:NetworkName,Password123,wifi,text,12,png,green,white
```

## Examples

### Business Card QR Code
```bash
python -m qr_code_generator --vcard \
  --name "Jane Smith" \
  --phone "+1-555-0123" \
  --email "jane@company.com" \
  --org "Tech Corp" \
  --url "https://company.com" \
  --output jane_contact.png
```

### WiFi Access QR Code
```bash
python -m qr_code_generator "WIFI:T:WPA;S:MyNetwork;P:MyPassword;;" \
  --output wifi_access.png \
  --size 12 \
  --fill-color blue
```

### Event Registration QR Code
```bash
python -m qr_code_generator "https://eventbrite.com/e/my-event-123456" \
  --output event_qr.svg \
  --format svg \
  --error-correction H
```

### Batch Generate Multiple QR Codes
```bash
# Create CSV file
cat > qr_data.csv << EOF
data,filename,type
https://twitter.com/username,twitter,url
https://linkedin.com/in/username,linkedin,url
+1234567890,phone,text
EOF

# Generate batch
python -m qr_code_generator --batch qr_data.csv --output-dir ./social_qrs
```

## Testing

Run the comprehensive test suite:

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=qr_code_generator

# Run specific test file
pytest tests/test_qr_code_generator.py

# Run with verbose output
pytest tests/ -v
```

The test suite includes:
- 12+ unit tests covering all major functionality
- Edge case testing
- Error handling validation
- Mock testing for external dependencies

## Logging

The application provides comprehensive logging:

```bash
# Enable verbose logging
python -m qr_code_generator "Test" --verbose

# Check log file
cat qr_generator.log
```

Log levels:
- `INFO`: Normal operation messages
- `DEBUG`: Detailed debugging information (with --verbose)
- `ERROR`: Error messages and exceptions
- `WARNING`: Non-critical issues

## Error Handling

The application handles various error conditions gracefully:

- **Invalid URLs**: Validates URL format before generation
- **Missing Files**: Clear error messages for missing input files
- **Invalid Parameters**: Validates all command-line arguments
- **File Permissions**: Handles file system permission issues
- **Memory Issues**: Manages large batch operations efficiently

## Known Limitations

- Logo addition only supports PNG format
- SVG output doesn't support logo embedding
- Large batch operations may require significant memory
- Some advanced QR code features (like structured append) are not implemented

## Troubleshooting

### Common Issues

#### "ModuleNotFoundError: No module named 'qrcode'"
```bash
pip install -r requirements.txt
```

#### "Permission denied" when saving files
```bash
# Check directory permissions
ls -la /path/to/output/directory

# Use different output directory
python -m qr_code_generator "Test" --output-dir ~/qr_codes
```

#### "Invalid URL" error
Ensure URLs include protocol (http:// or https://):
```bash
# Correct
python -m qr_code_generator --url "https://example.com"

# Incorrect
python -m qr_code_generator --url "example.com"
```

### Performance Tips

- Use SVG format for scalable QR codes
- Choose appropriate error correction level (L for maximum capacity, H for reliability)
- For batch operations, ensure adequate disk space
- Use moderate size values (10-20) for balance between quality and file size

## Development

### Project Structure
```
22-qr-code-generator/
├── qr_code_generator/          # Main package
│   ├── __init__.py            # Package initialization
│   ├── main.py                # CLI interface
│   ├── core.py                # Core QR code functionality
│   └── utils.py               # Utility functions
├── tests/                     # Test suite
│   ├── __init__.py
│   └── test_qr_code_generator.py
├── requirements.txt           # Dependencies
├── README.md                 # This file
├── CHECKLIST.md              # Feature checklist
└── SPEC.md                   # Project specification
```

### Code Quality
- Follows PEP 8 style guidelines
- Type hints on all public functions
- Comprehensive docstrings
- 90%+ test coverage
- Error handling for all edge cases

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Version History

- **v1.0.0** - Initial release with all core features
  - Text, URL, and vCard QR code generation
  - PNG and SVG output formats
  - Batch processing from CSV
  - CLI interface with comprehensive options
  - Full test suite and documentation

---

**QR Code Generator** - A professional tool for all your QR code needs!

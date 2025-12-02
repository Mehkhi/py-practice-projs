# Local URL Shortener

A professional CLI tool and web service for creating and managing short URLs with SQLite storage, click tracking, and QR code generation.

## Features

### Core Features
- ✅ Generate short codes (random or hash-based)
- ✅ Store URL mappings in SQLite database
- ✅ Redirect to original URLs with click tracking
- ✅ CLI and web interface
- ✅ Custom short codes
- ✅ Expiration dates for links
- ✅ QR code generation for short URLs

### Technical Features
- SQLite database for persistence
- RESTful API endpoints
- Click analytics and statistics
- URL validation and sanitization
- Comprehensive error handling
- Logging for debugging and monitoring
- Unit tests with high coverage

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup

1. **Clone or download the project**
   ```bash
   cd 14-local-url-shortener
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
   python -m local_url_shortener --help
   ```

## Usage

### Command Line Interface

#### Basic URL Shortening
```bash
# Create a short URL
python -m local_url_shortener shorten https://example.com

# Output:
# Short URL: http://localhost:5000/abc123
# Short code: abc123
```

#### Custom Short Codes
```bash
# Create a URL with custom code
python -m local_url_shortener shorten https://example.com --custom mylink

# Output:
# Short URL: http://localhost:5000/mylink
# Short code: mylink
```

#### URL Expiration
```bash
# Create URL that expires in 30 days
python -m local_url_shortener shorten https://example.com --expires 30
```

#### Hash-based Codes
```bash
# Use hash-based code generation
python -m local_url_shortener shorten https://example.com --hash
```

#### QR Code Generation
```bash
# Generate QR code along with short URL
python -m local_url_shortener shorten https://example.com --qr

# Output:
# Short URL: http://localhost:5000/abc123
# Short code: abc123
# QR code saved to: qr_abc123.png
```

#### URL Management
```bash
# Expand short URL to get original
python -m local_url_shortener expand abc123

# Get statistics for a short URL
python -m local_url_shortener stats abc123

# List all URLs
python -m local_url_shortener list

# Delete a short URL
python -m local_url_shortener delete abc123

# Clean up expired URLs
python -m local_url_shortener cleanup
```

### Web Interface

#### Start Web Server
```bash
# Start server on default port 5000
python -m local_url_shortener serve

# Start server on custom port
python -m local_url_shortener serve --port 8080

# Start server with debug mode
python -m local_url_shortener serve --debug
```

#### Web Features
- **Home Page**: Form to create short URLs
- **Redirection**: Automatic redirect to original URLs
- **URL List**: View recent URLs with statistics
- **API Endpoints**: RESTful API for programmatic access

#### API Endpoints

**Create Short URL**
```bash
curl -X POST http://localhost:5000/api/shorten \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "custom_code": "mylink"}'
```

**Expand Short URL**
```bash
curl http://localhost:5000/api/mylink
```

**Get URL Statistics**
```bash
curl http://localhost:5000/api/mylink/stats
```

**List All URLs**
```bash
curl http://localhost:5000/api/urls
```

## Configuration

### Database
- Default database file: `urls.db`
- SQLite database with automatic schema creation
- Stores URLs, metadata, and click statistics

### Server Configuration
- Default host: `localhost`
- Default port: `5000`
- Configurable via command-line arguments

### Logging
- Logs to console by default
- Configurable log levels (DEBUG, INFO, WARNING, ERROR)
- Includes operation timestamps and details

## Examples

### Example 1: Basic Workflow
```bash
# Create short URL
python -m local_url_shortener shorten https://github.com/user/repo --custom myrepo

# Start web server
python -m local_url_shortener serve

# Visit http://localhost:5000/myrepo to redirect
```

### Example 2: Batch URL Creation
```bash
# Create multiple URLs
python -m local_url_shortener shorten https://google.com --custom google
python -m local_url_shortener shorten https://github.com --custom github
python -m local_url_shortener shorten https://stackoverflow.com --custom so

# List all URLs
python -m local_url_shortener list
```

### Example 3: Temporary Links
```bash
# Create link that expires in 7 days
python -m local_url_shortener shorten https://event.com/register --expires 7 --custom event2024

# Check statistics
python -m local_url_shortener stats event2024
```

### Example 4: API Usage
```bash
# Start server
python -m local_url_shortener serve &

# Create URL via API
curl -X POST http://localhost:5000/api/shorten \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "expires_days": 30}'

# Get statistics
curl http://localhost:5000/api/abc123/stats
```

## Testing

### Run Unit Tests
```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=local_url_shortener
```

### Test Coverage
The test suite includes:
- URL shortening and expansion
- Custom code handling
- Expiration functionality
- Click tracking
- Database operations
- Utility functions
- Integration workflows

## Development

### Project Structure
```
14-local-url-shortener/
├── local_url_shortener/          # Main package
│   ├── __init__.py              # Package initialization
│   ├── main.py                  # CLI interface
│   ├── core.py                  # Core URL shortening logic
│   ├── utils.py                 # Utility functions
│   └── web.py                   # Web interface
├── tests/                       # Test suite
│   ├── __init__.py
│   └── test_local_url_shortener.py
├── requirements.txt             # Dependencies
├── README.md                    # This file
├── CHECKLIST.md                 # Feature checklist
└── SPEC.md                      # Project specification
```

### Code Quality
- **Type Hints**: All public functions include type hints
- **Docstrings**: Comprehensive documentation for all modules and functions
- **Error Handling**: Proper exception handling with meaningful messages
- **Logging**: Appropriate logging for debugging and monitoring
- **Testing**: High test coverage with unit and integration tests

### Dependencies
- `flask>=2.3.0`: Web framework for HTTP server
- `qrcode[pil]>=7.4.0`: QR code generation
- `pytest>=7.4.0`: Testing framework

## Known Limitations

1. **Single-User Design**: No user authentication or multi-tenancy
2. **Local Storage**: SQLite database limited to single machine
3. **No Analytics**: Basic click tracking only, no detailed analytics
4. **Memory Usage**: All URLs loaded into memory for web interface
5. **No Rate Limiting**: No protection against abuse
6. **Simple UI**: Basic HTML interface without advanced features

## Troubleshooting

### Common Issues

**Port Already in Use**
```bash
# Find available port
python -c "from local_url_shortener.utils import find_available_port; print(find_available_port())"

# Use different port
python -m local_url_shortener serve --port 8080
```

**Database Permission Error**
```bash
# Check database permissions
ls -la urls.db

# Remove database and recreate
rm urls.db
python -m local_url_shortener shorten https://example.com
```

**Missing Dependencies**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

**QR Code Generation Fails**
```bash
# Install PIL separately if needed
pip install Pillow
```

### Debug Mode
Enable debug logging for troubleshooting:
```bash
# Set debug environment variable
export LOG_LEVEL=DEBUG
python -m local_url_shortener serve --debug
```

## Contributing

### Development Setup
```bash
# Clone project
git clone <repository-url>
cd 14-local-url-shortener

# Setup development environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt  # If available

# Run tests
pytest tests/
```

### Code Style
- Follow PEP 8 style guidelines
- Use `black` for code formatting
- Use `ruff` for linting
- Include type hints for all public functions
- Write comprehensive docstrings

## License

This project is part of a Python learning curriculum and is provided for educational purposes.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the test files for usage examples
3. Examine the source code for implementation details
4. Enable debug logging for detailed error information

---

**Version**: 1.0.0
**Python**: 3.8+
**Last Updated**: 2024

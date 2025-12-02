# Image Organizer

A professional CLI tool for organizing images by date using EXIF data. Automatically sorts your photos into a structured folder hierarchy based on when they were taken, with support for duplicate detection, thumbnail generation, and custom naming patterns.

## Features

### Core Features
- **Smart Date Detection**: Extracts dates from EXIF data (DateTime, DateTimeOriginal)
- **Fallback Handling**: Uses file modification time when EXIF data is missing
- **Organized Structure**: Creates YYYY/MM folder hierarchy
- **Duplicate Detection**: Uses perceptual hashing to identify duplicate images
- **Comprehensive Reporting**: Detailed statistics and action summaries

### Bonus Features
- **Thumbnail Generation**: Create thumbnails for organized images
- **Custom Naming**: Flexible naming templates with date variables
- **Dry Run Mode**: Preview changes without actually moving files
- **Multiple Formats**: Supports JPG, PNG, TIFF, BMP, GIF
- **Error Handling**: Graceful handling of corrupted or invalid files

## Installation

### Prerequisites
- Python 3.8 or higher
- pip for package management

### Setup

1. **Clone or download the project**:
   ```bash
   cd 06-image-organizer
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

4. **Install the package** (optional, for development):
   ```bash
   pip install -e .
   ```

## Usage

### Basic Usage

```bash
# Organize images from source to target directory
python -m image_organizer /path/to/source /path/to/target

# Preview what would be done (dry run)
python -m image_organizer /path/to/source /path/to/target --dry-run
```

### Advanced Options

```bash
# Create thumbnails with custom size
python -m image_organizer /path/to/source /path/to/target --thumbnails --thumbnail-size 200x200

# Use custom naming pattern
python -m image_organizer /path/to/source /path/to/target --naming "{date}_{original_name}"

# Enable verbose logging
python -m image_organizer /path/to/source /path/to/target --verbose

# Combine multiple options
python -m image_organizer /path/to/source /path/to/target --thumbnails --naming "{datetime}_{original_name}" --dry-run
```

### Command Line Options

| Option | Description |
|--------|-------------|
| `SOURCE_DIR` | Directory containing images to organize (required) |
| `TARGET_DIR` | Directory where organized images will be placed (required) |
| `--dry-run` | Show what would be done without actually moving files |
| `--verbose`, `-v` | Enable verbose logging for debugging |
| `--thumbnails` | Create thumbnails for organized images |
| `--thumbnail-size` | Thumbnail size in format WIDTHxHEIGHT (default: 150x150) |
| `--naming` | Custom naming template (see below) |
| `--version` | Show version information |

### Custom Naming Templates

The `--naming` option supports template variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `{date}` | Date in YYYYMMDD format | 20230515 |
| `{time}` | Time in HHMMSS format | 143000 |
| `{datetime}` | Combined date and time | 20230515_143000 |
| `{year}` | Year | 2023 |
| `{month}` | Month (zero-padded) | 05 |
| `{day}` | Day (zero-padded) | 15 |
| `{original_name}` | Original filename without extension | IMG_001 |
| `{extension}` | File extension | .jpg |

**Examples**:
- `{date}_{original_name}` → `20230515_IMG_001.jpg`
- `{datetime}_{original_name}` → `20230515_143000_IMG_001.jpg`
- `{year}/{month}/{day}_{original_name}` → `2023/05/15_IMG_001.jpg`

## Examples

### Example 1: Basic Organization
```bash
# Organize photos from Downloads to Pictures
python -m image_organizer ~/Downloads/photos ~/Pictures/organized
```

**Result**: Images are organized into folders like:
```
~/Pictures/organized/
├── 2023/
│   ├── 01/
│   │   ├── IMG_001.jpg
│   │   └── IMG_002.jpg
│   └── 05/
│       └── vacation_photo.jpg
└── 2022/
    └── 12/
        └── christmas.jpg
```

### Example 2: With Thumbnails and Custom Naming
```bash
python -m image_organizer ~/Downloads/photos ~/Pictures/organized \
  --thumbnails \
  --thumbnail-size 200x200 \
  --naming "{date}_{original_name}"
```

**Result**: Creates both full images and thumbnails with custom naming:
```
~/Pictures/organized/2023/05/
├── 20230515_IMG_001.jpg
├── 20230515_IMG_001_thumb.jpg
├── 20230515_vacation.jpg
└── 20230515_vacation_thumb.jpg
```

### Example 3: Preview Changes
```bash
python -m image_organizer ~/Downloads/photos ~/Pictures/organized --dry-run --verbose
```

**Output**:
```
2023-05-15 14:30:00 - image_organizer.core - INFO - Scanning directory: /Users/john/Downloads/photos
2023-05-15 14:30:00 - image_organizer.core - INFO - Found 15 image files
2023-05-15 14:30:00 - image_organizer.core - INFO - Would move: /Users/john/Downloads/photos/IMG_001.jpg -> /Users/john/Pictures/organized/2023/05/IMG_001.jpg
...
==================================================
IMAGE ORGANIZATION REPORT
==================================================
Source Directory: /Users/john/Downloads/photos
Target Directory: /Users/john/Pictures/organized
Dry Run: True
Thumbnails: No
Custom Naming: None

STATISTICS:
  Images Processed: 15
  Images Moved: 14
  Images Skipped: 1
  Errors: 0
  Duplicates Found: 0
  Thumbnails Created: 0
==================================================
```

## Configuration

### Environment Variables
- `IMAGE_ORGANIZER_LOG_LEVEL`: Set logging level (DEBUG, INFO, WARNING, ERROR)
- `IMAGE_ORGANIZER_DEFAULT_THUMBNAIL_SIZE`: Default thumbnail size (e.g., "150x150")

### Logging
The tool provides detailed logging at different levels:
- **INFO**: General progress and operations
- **DEBUG**: Detailed information about file processing
- **WARNING**: Non-critical issues (e.g., missing EXIF data)
- **ERROR**: Critical errors that prevent processing

## Testing

Run the test suite to verify functionality:

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=image_organizer

# Run specific test file
pytest tests/test_image_organizer.py

# Run with verbose output
pytest tests/ -v
```

## Project Structure

```
06-image-organizer/
├── image_organizer/          # Main package
│   ├── __init__.py
│   ├── main.py              # CLI entry point
│   ├── core.py              # Core organization logic
│   └── utils.py             # Utility functions
├── tests/                   # Test suite
│   ├── __init__.py
│   └── test_image_organizer.py
├── requirements.txt         # Dependencies
├── README.md               # This file
├── CHECKLIST.md            # Feature checklist
└── SPEC.md                 # Project specification
```

## Dependencies

- **Pillow (PIL)**: Image processing and EXIF data extraction
- **imagehash**: Perceptual hashing for duplicate detection
- **click**: Command-line interface framework

## Known Limitations

1. **EXIF Data**: Some images may not have EXIF data, requiring fallback to file modification time
2. **File Permissions**: Requires read access to source directory and write access to target directory
3. **Large Files**: Very large images may take longer to process
4. **Corrupted Files**: Corrupted image files are skipped with appropriate logging
5. **Memory Usage**: Processing many large images simultaneously may require significant memory

## Troubleshooting

### Common Issues

**"No images found to organize"**
- Check that the source directory contains supported image formats
- Verify file permissions allow reading the directory

**"Permission denied" errors**
- Ensure write permissions for the target directory
- Check that source files are not locked by other applications

**"Invalid thumbnail size format"**
- Use the format WIDTHxHEIGHT (e.g., "150x150", "200x300")
- Ensure both dimensions are positive integers

**"Error reading EXIF data"**
- This is normal for some image formats or corrupted files
- The tool will fall back to file modification time

### Debug Mode

Enable verbose logging to see detailed processing information:

```bash
python -m image_organizer /path/to/source /path/to/target --verbose
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is part of the Python Practice Projects collection and is intended for educational purposes.

## Changelog

### Version 1.0.0
- Initial release
- Core image organization functionality
- EXIF data extraction with fallback
- Duplicate detection
- Thumbnail generation
- Custom naming templates
- Comprehensive test suite
- CLI interface with multiple options

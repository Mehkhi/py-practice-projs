# Image Thumbnailer

A professional command-line tool for creating image thumbnails with advanced features like watermarking, border addition, and batch processing.

## Features

- **Batch Processing**: Process multiple images at once
- **Aspect Ratio Preservation**: Maintain image proportions or force exact sizes
- **Multiple Formats**: Support for JPG, PNG, and WebP
- **Watermarking**: Add customizable text watermarks
- **Border Addition**: Add borders with custom colors and widths
- **EXIF Orientation**: Automatically correct image rotation from EXIF data
- **Quality Control**: Adjustable compression quality for output images

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. Clone or download this repository
2. Navigate to the project directory:
   ```bash
   cd 24-image-thumbnailer
   ```

3. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage

Create a thumbnail from a single image:
```bash
python -m image_thumbnailer image.jpg -s 200x200 -o thumbnail.jpg
```

Process all images in a directory:
```bash
python -m image_thumbnailer input_directory/ -d output_directory/ -s 300x300
```

### Command Line Options

#### Input Options
- `input_path`: Path to a single image file (mutually exclusive with `-i`)
- `-i, --input-dir`: Directory containing images to process (mutually exclusive with `input_path`)

#### Output Options
- `-o, --output`: Output file path (single image) or output directory (batch)
- `-d, --output-dir`: Output directory for batch processing

#### Size and Quality
- `-s, --size`: Thumbnail size in WIDTHxHEIGHT format (default: 200x200)
- `-q, --quality`: JPEG/WebP quality (1-100, default: 85)
- `--no-aspect`: Force exact size without maintaining aspect ratio

#### Watermarking
- `-w, --watermark`: Add watermark text
- `--watermark-position`: Position for watermark (bottom-right, bottom-left, top-right, top-left)

#### Borders
- `-b, --border`: Add border with specified width in pixels
- `--border-color`: Border color (default: black)

#### Logging
- `-v, --verbose`: Enable verbose logging
- `--log-level`: Set logging level (DEBUG, INFO, WARNING, ERROR)

### Examples

#### Single Image with Watermark
```bash
python -m image_thumbnailer photo.jpg -o thumb.jpg -s 400x400 -w "© 2024"
```

#### Batch Processing with Borders
```bash
python -m image_thumbnailer photos/ -d thumbnails/ -s 250x250 -b 5 --border-color white
```

#### High-Quality Thumbnails
```bash
python -m image_thumbnailer image.png -o thumb.png -s 500x500 -q 95 --no-aspect
```

#### Verbose Batch Processing
```bash
python -m image_thumbnailer images/ -d thumbs/ -s 200x200 -v
```

## Supported Formats

- **Input**: JPG, PNG, WebP
- **Output**: JPG, PNG, WebP (same format as input by default)

## Development

### Running Tests

```bash
pytest tests/
```

### Code Quality

Format code with Black:
```bash
black image_thumbnailer/
```

Lint with Ruff:
```bash
ruff check image_thumbnailer/
```

## Project Structure

```
24-image-thumbnailer/
├── image_thumbnailer/
│   ├── __init__.py
│   ├── core.py          # Core thumbnail generation logic
│   ├── main.py          # Command-line interface
│   └── utils.py         # Utility functions
├── tests/
│   ├── __init__.py
│   └── test_image_thumbnailer.py
├── requirements.txt     # Python dependencies
├── README.md           # This file
├── CHECKLIST.md        # Feature checklist
└── SPEC.md            # Project specification
```

## Error Handling

The tool includes comprehensive error handling for:
- Invalid input files or directories
- Unsupported image formats
- Permission errors
- Corrupted image files
- EXIF data issues

All errors are logged with appropriate severity levels.

## Limitations

- Only supports JPG, PNG, and WebP formats
- Watermark text is limited to basic fonts
- No support for animated images (GIF, WebP animations)
- Large images may require significant memory

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

This project is open source. See the repository for license details.

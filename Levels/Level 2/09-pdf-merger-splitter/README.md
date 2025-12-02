# PDF Merger & Splitter

A powerful command-line tool for manipulating PDF files with support for merging, splitting, extracting pages, adding watermarks, rotating pages, encryption, and page numbering.

## Features

### Core Features
- **Merge PDFs**: Combine multiple PDF files into a single document
- **Split PDFs**: Split PDF files into individual pages or custom page ranges
- **Extract Pages**: Extract specific pages from a PDF to create a new document
- **Metadata Preservation**: Preserve original PDF metadata when merging

### Bonus Features
- **Add Watermarks**: Add text watermarks to PDF pages with customizable opacity
- **Rotate Pages**: Rotate pages by 90°, 180°, or 270°
- **Encrypt PDFs**: Password-protect PDF files
- **Add Page Numbers**: Automatically add page numbers to documents

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup

1. **Clone or download the project**
   ```bash
   cd 09-pdf-merger-splitter
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify installation (CLI)**
   ```bash
   python -m pdf_merger_splitter --help
   ```

### GUI (PySide6) quick start (dev)

```bash
python -m pip install -r requirements.txt
python -m pdf_merger_splitter.gui.app
```

### Packaging

- Windows: build with PyInstaller and create an installer with Inno Setup (unsigned by default).
- macOS: build a .app with PyInstaller and an unsigned .dmg.

Windows build:
```powershell
cd build
./build-win.ps1
```
Then open `build/windows/installer.iss` in Inno Setup and Build.

macOS build:
```bash
cd build
./build-mac.sh
./mac/create_dmg.sh
```

## Usage

### Basic Commands

#### Merge PDFs
Combine multiple PDF files into one:

```bash
python -m pdf_merger_splitter merge -o merged.pdf file1.pdf file2.pdf file3.pdf
```

Options:
- `-o, --output`: Output file path (required)
- `--no-preserve-metadata`: Don't preserve metadata from first PDF

#### Split PDFs
Split a PDF into individual pages:

```bash
python -m pdf_merger_splitter split input.pdf -o output_directory/
```

Split by custom page ranges:

```bash
python -m pdf_merger_splitter split input.pdf -o output_directory/ -r "1-3" "4-6" "7-10"
```

Options:
- `-o, --output`: Output directory (required)
- `-r, --ranges`: Page ranges for splitting (optional)

#### Extract Pages
Extract specific pages from a PDF:

```bash
python -m pdf_merger_splitter extract input.pdf -o extracted.pdf -p "1-3,5,7-9"
```

Options:
- `-o, --output`: Output file path (required)
- `-p, --pages`: Page range to extract (required)

### Advanced Features

#### Add Watermarks
Add a text watermark to all pages:

```bash
python -m pdf_merger_splitter watermark input.pdf -o watermarked.pdf -t "CONFIDENTIAL"
```

With custom opacity:

```bash
python -m pdf_merger_splitter watermark input.pdf -o watermarked.pdf -t "DRAFT" --opacity 0.5
```

Options:
- `-o, --output`: Output file path (required)
- `-t, --text`: Watermark text (required)
- `--opacity`: Watermark opacity (0.0-1.0, default: 0.3)

#### Rotate Pages
Rotate pages in a PDF:

```bash
python -m pdf_merger_splitter rotate input.pdf -o rotated.pdf -r 90
```

Rotate specific pages only:

```bash
python -m pdf_merger_splitter rotate input.pdf -o rotated.pdf -r 180 -p "1-3,5"
```

Options:
- `-o, --output`: Output file path (required)
- `-r, --rotation`: Rotation angle (90, 180, or 270) (required)
- `-p, --pages`: Page range to rotate (optional, defaults to all pages)

#### Encrypt PDFs
Password-protect a PDF:

```bash
python -m pdf_merger_splitter encrypt input.pdf -o encrypted.pdf --password "secret123"
```

Options:
- `-o, --output`: Output file path (required)
- `--password`: Password for encryption (required)

#### Add Page Numbers
Add page numbers to a PDF:

```bash
python -m pdf_merger_splitter pagenumbers input.pdf -o numbered.pdf
```

Custom position and format:

```bash
python -m pdf_merger_splitter pagenumbers input.pdf -o numbered.pdf --position top --format "{num}/{total}"
```

Options:
- `-o, --output`: Output file path (required)
- `--position`: Position of page numbers (top or bottom, default: bottom)
- `--format`: Format string for page numbers (default: "Page {num} of {total}")

### Global Options

- `-v, --verbose`: Enable verbose logging for debugging

## Page Range Syntax

Page ranges use the following syntax:
- Single pages: `5`
- Ranges: `1-3` (pages 1, 2, and 3)
- Multiple ranges: `1-3,5,7-9` (pages 1, 2, 3, 5, 7, 8, and 9)
- All pages: Leave empty (for extract command)

## Examples

### Document Preparation Workflow
```bash
# 1. Merge multiple chapters
python -m pdf_merger_splitter merge -o book.pdf chapter1.pdf chapter2.pdf chapter3.pdf

# 2. Add page numbers
python -m pdf_merger_splitter pagenumbers book.pdf -o book_numbered.pdf

# 3. Add watermark for draft version
python -m pdf_merger_splitter watermark book_numbered.pdf -o book_draft.pdf -t "DRAFT" --opacity 0.2

# 4. Encrypt final version
python -m pdf_merger_splitter encrypt book_numbered.pdf -o book_final.pdf --password "reader123"
```

### Extract Specific Sections
```bash
# Extract table of contents (pages 1-3)
python -m pdf_merger_splitter extract textbook.pdf -o toc.pdf -p "1-3"

# Extract specific chapters (pages 15-25 and 40-55)
python -m pdf_merger_splitter extract textbook.pdf -o chapters.pdf -p "15-25,40-55"
```

### Split Large Documents
```bash
# Split into chunks of 10 pages each
python -m pdf_merger_splitter split large_document.pdf -o chunks/ -r "1-10" "11-20" "21-30"

# Split into individual pages for processing
python -m pdf_merger_splitter split document.pdf -o individual_pages/
```

## Testing

Run the test suite to verify functionality:

```bash
python -m pytest tests/ -v
```

Or run specific test categories:

```bash
# Run core functionality tests
python -m pytest tests/test_pdf_merger_splitter.py::TestPDFProcessor -v

# Run utility function tests
python -m pytest tests/test_pdf_merger_splitter.py::TestUtils -v
```

## Error Handling

The tool includes comprehensive error handling for common issues:

- **File not found**: Clear error messages when input files don't exist
- **Invalid page ranges**: Validation of page range syntax and bounds
- **Permission errors**: Handling of file permission issues
- **Corrupted PDFs**: Graceful handling of damaged PDF files
- **Invalid operations**: Clear error messages for unsupported operations

## Logging

Enable verbose logging to debug issues:

```bash
python -m pdf_merger_splitter -v merge -o output.pdf input1.pdf input2.pdf
```

Log levels:
- `INFO`: Normal operation messages
- `DEBUG`: Detailed debugging information (use `-v` flag)
- `ERROR`: Error messages only

## Configuration

The tool uses sensible defaults but can be customized:

### Default Settings
- Watermark opacity: 0.3
- Page number position: bottom
- Page number format: "Page {num} of {total}"
- Metadata preservation: enabled

### Environment Variables
No environment variables are required, but you can set:
- `PYTHONPATH`: If installing in development mode

## Known Limitations

1. **Text annotations**: Watermarks and page numbers are added as text annotations, not as direct content
2. **Complex PDFs**: May not work correctly with highly complex or encrypted PDFs
3. **Large files**: Performance may degrade with very large PDF files (>100MB)
4. **Image quality**: No image compression or optimization features
5. **Form fields**: Does not preserve interactive form fields during operations

## Dependencies

- **PyPDF2**: Core PDF manipulation library
- **Python standard library**: argparse, logging, pathlib, typing

## Contributing

This project follows standard Python development practices:

1. **Code style**: Follow PEP 8
2. **Testing**: Write tests for new features
3. **Documentation**: Update README and docstrings
4. **Type hints**: Include type hints for public functions

## License

This project is provided as educational code. Please check the project license for usage terms.

## Support

For issues or questions:
1. Check the examples section above
2. Run with `-v` flag for detailed error messages
3. Verify input files are valid PDFs
4. Ensure sufficient disk space for output files

## Version History

- **v1.0.0**: Initial release with core and bonus features
  - PDF merging, splitting, extracting
  - Watermarks, rotation, encryption, page numbering
  - Comprehensive CLI interface
  - Full test coverage

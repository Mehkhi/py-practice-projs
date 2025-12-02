# File Organizer

A command-line Python tool that automatically organizes files by their extensions into category folders. Perfect for cleaning up messy directories!

## What It Does

The File Organizer scans a directory, identifies files by their extensions, and moves them into organized category folders such as:
- **Images** (jpg, png, gif, etc.)
- **Documents** (pdf, doc, txt, etc.)
- **Videos** (mp4, avi, mov, etc.)
- **Audio** (mp3, wav, flac, etc.)
- **Code** (py, js, html, css, etc.)
- **Archives** (zip, rar, 7z, etc.)
- **Spreadsheets** (xlsx, csv, etc.)
- **Presentations** (pptx, ppt, etc.)
- **Executables** (exe, dmg, pkg, etc.)
- **Other** (unknown extensions)

## Features

- [OK] **Smart Categorization**: Automatically categorizes files by extension
- [OK] **Safe Operation**: Dry-run mode to preview actions before moving files
- [OK] **Duplicate Handling**: Automatically handles duplicate filenames
- [OK] **Detailed Reporting**: Shows exactly what actions were taken
- [OK] **Error Handling**: Gracefully handles errors and invalid input
- [OK] **Command-line Interface**: Easy to use from terminal
- [OK] **Cross-platform**: Works on Windows, macOS, and Linux

## Installation

No installation required! Just make sure you have Python 3.7 or higher installed.

## How to Run

### Basic Usage

Organize files in the current directory:
```bash
python file_organizer.py
```

Organize files in a specific directory:
```bash
python file_organizer.py /path/to/directory
```

### Dry Run Mode

Preview what will happen without actually moving files:
```bash
python file_organizer.py --dry-run
python file_organizer.py /path/to/directory --dry-run
```

### Command Line Options

- `directory`: Directory to organize (default: current directory)
- `--dry-run`: Preview actions without moving files

## Example Usage

### Example 1: Organize Current Directory

```bash
$ python file_organizer.py
File Organizer
==================================================
Target directory: /Users/john/Downloads
Mode: NORMAL

Scanning directory: /Users/john/Downloads

Found files to organize:
  Images: 5 files
  Documents: 3 files
  Videos: 2 files
  Audio: 1 files
  Code: 4 files
Total: 15 files

Organize 15 files? (y/N): y
Created folder: /Users/john/Downloads/Images
Created folder: /Users/john/Downloads/Documents
Created folder: /Users/john/Downloads/Videos
Created folder: /Users/john/Downloads/Audio
Created folder: /Users/john/Downloads/Code
Moved: photo1.jpg -> Images/photo1.jpg
Moved: document.pdf -> Documents/document.pdf
Moved: video.mp4 -> Videos/video.mp4
...

==================================================
FILE ORGANIZATION REPORT
==================================================

Files organized by category:
  Images: 5 files
  Documents: 3 files
  Videos: 2 files
  Audio: 1 files
  Code: 4 files

Total files processed: 15

Actions taken:
  - Created folder: /Users/john/Downloads/Images
  - Created folder: /Users/john/Downloads/Documents
  - Moved: photo1.jpg -> Images/photo1.jpg
  - Moved: document.pdf -> Documents/document.pdf
  ...

==================================================
```

### Example 2: Dry Run Preview

```bash
$ python file_organizer.py --dry-run
File Organizer
==================================================
Target directory: /Users/john/Downloads
Mode: DRY RUN (preview only)

Scanning directory: /Users/john/Downloads

Found files to organize:
  Images: 5 files
  Documents: 3 files
Total: 8 files

[DRY RUN MODE] - No files will be moved

[DRY RUN] Would create folder: /Users/john/Downloads/Images
[DRY RUN] Would create folder: /Users/john/Downloads/Documents
[DRY RUN] Would move: photo1.jpg -> Images/photo1.jpg
[DRY RUN] Would move: document.pdf -> Documents/document.pdf
...

==================================================
FILE ORGANIZATION REPORT
==================================================

Files organized by category:
  Images: 5 files
  Documents: 3 files

Total files processed: 8

Actions planned:
  - Would create folder: /Users/john/Downloads/Images
  - Would create folder: /Users/john/Downloads/Documents
  - Would move: photo1.jpg -> Images/photo1.jpg
  - Would move: document.pdf -> Documents/document.pdf
  ...

==================================================
```

## File Categories

The organizer recognizes these file types:

| Category | Extensions |
|----------|------------|
| **Images** | jpg, jpeg, png, gif, bmp, svg, tiff, webp, ico, raw |
| **Documents** | pdf, doc, docx, txt, rtf, odt, pages, md, tex |
| **Spreadsheets** | xls, xlsx, csv, ods, numbers |
| **Presentations** | ppt, pptx, odp, key |
| **Videos** | mp4, avi, mov, wmv, flv, webm, mkv, m4v |
| **Audio** | mp3, wav, flac, aac, ogg, wma, m4a |
| **Archives** | zip, rar, 7z, tar, gz, bz2, xz |
| **Code** | py, js, html, css, java, cpp, c, php, rb, go, rs, ts, json, xml, yaml, yml, sql, sh, bat, ps1 |
| **Executables** | exe, msi, dmg, pkg, deb, rpm, app, bin |
| **Other** | Any unrecognized extensions |

## Safety Features

- **Confirmation Prompt**: Asks for confirmation before moving files (except in dry-run mode)
- **Duplicate Handling**: Automatically renames files if a file with the same name already exists
- **Error Handling**: Continues processing even if some files fail to move
- **Dry Run Mode**: Test the organizer without making any changes

## Testing

Run the test suite to verify everything works correctly:

```bash
# Run all tests
python -m pytest test_file_organizer.py -v

# Run tests with coverage (if pytest-cov is installed)
python -m pytest test_file_organizer.py --cov=file_organizer --cov-report=html
```

## Project Structure

```
25-file-organizer/
├── file_organizer.py      # Main program
├── test_file_organizer.py # Unit tests
├── README.md              # This file
├── CHECKLIST.md           # Feature checklist
└── SPEC.md                # Project specification
```

## Requirements

- Python 3.7 or higher
- No external dependencies (uses only standard library)

## How It Works

1. **Scan**: The program scans the target directory for files
2. **Categorize**: Files are categorized by their extensions using a predefined mapping
3. **Create Folders**: Category folders are created as needed
4. **Move Files**: Files are moved to their respective category folders
5. **Report**: A detailed report shows what actions were taken

## Error Handling

The program handles various error conditions gracefully:
- Non-existent directories
- Permission errors
- File system errors
- Invalid input

## Contributing

This is a learning project, but suggestions for improvements are welcome!

## License

This project is for educational purposes. Feel free to use and modify as needed.

## Troubleshooting

### Common Issues

**Q: The program says "No files found to organize"**
A: Make sure you're running it in a directory that contains files, or specify the correct directory path.

**Q: Permission denied errors**
A: Make sure you have write permissions to the target directory.

**Q: Files aren't being categorized correctly**
A: Check if the file extensions are in the supported list. Unknown extensions go to the "Other" category.

**Q: The program crashes**
A: Run with `--dry-run` first to see what it would do, and check the error message for details.

### Getting Help

If you encounter issues:
1. Try running with `--dry-run` first
2. Check that you have the required permissions
3. Verify the directory path is correct
4. Look at the error messages for specific issues

## Future Enhancements

Potential improvements for future versions:
- Custom category rules from configuration file
- Undo/rollback capability
- GUI interface
- Batch processing of multiple directories
- File filtering by size or date
- Integration with cloud storage services

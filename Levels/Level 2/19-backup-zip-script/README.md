# Backup ZIP Script

A command-line tool for creating compressed backups with automatic rotation, exclusion patterns, and integrity verification.

## Features

- **ZIP Compression**: Create compressed backups with timestamps
- **Exclusion Patterns**: Automatically exclude common directories like `.git`, `__pycache__`, etc.
- **Integrity Verification**: Verify backup integrity after creation
- **Rotation Policy**: Keep only the most recent N backups
- **Logging**: Comprehensive logging for backup operations
- **CLI Interface**: Easy-to-use command-line interface

## Installation

### Prerequisites

- Python 3.8 or higher

### Setup

1. Clone or download this repository
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

Create a backup of the current directory:

```bash
python -m backup_zip_script .
```

### Specify Backup Directory

```bash
python -m backup_zip_script /path/to/source --backup-dir /path/to/backups
```

### Custom Exclusion Patterns

Exclude additional files or directories:

```bash
python -m backup_zip_script . --exclude "*.log" "*.tmp" "temp_*"
```

### Limit Number of Backups

Keep only the 5 most recent backups:

```bash
python -m backup_zip_script . --max-backups 5
```

### Verbose Logging

Enable detailed logging:

```bash
python -m backup_zip_script . --verbose
```

## Command Line Options

```
positional arguments:
  source_dir            Directory to backup

optional arguments:
  -h, --help            Show help message and exit
  --backup-dir BACKUP_DIR
                        Directory to store backup files (default: ./backups)
  --exclude EXCLUDE     Patterns to exclude (can be used multiple times)
  --max-backups MAX_BACKUPS
                        Maximum number of backups to keep (default: 10)
  --verbose, -v         Enable verbose logging
```

## Examples

### Backup a Python Project

```bash
python -m backup_zip_script /home/user/myproject --backup-dir /home/user/backups --max-backups 7
```

### Backup with Custom Exclusions

```bash
python -m backup_zip_script . \
  --exclude "*.log" \
  --exclude "temp/*" \
  --exclude "cache/" \
  --backup-dir ./my-backups \
  --max-backups 3
```

### Automated Backup Script

Create a simple bash script for automated backups:

```bash
#!/bin/bash
# daily-backup.sh
python -m backup_zip_script /important/data --backup-dir /backups/daily --max-backups 30
```

## Default Exclusions

The following patterns are excluded by default:
- `.git` (Git repository data)
- `__pycache__` (Python bytecode cache)
- `*.pyc` (Python compiled files)
- `.DS_Store` (macOS system files)
- `node_modules` (Node.js dependencies)

## Configuration

All configuration is done via command-line arguments. There is no configuration file.

## Logging

The tool provides comprehensive logging:
- **INFO**: Backup creation, completion, and rotation operations
- **DEBUG**: Individual files added to backup (with `--verbose`)
- **ERROR**: Failures and verification errors

Logs are output to stderr and can be redirected to a file:

```bash
python -m backup_zip_script . --verbose 2> backup.log
```

## Error Handling

The tool handles various error conditions:
- Non-existent source directories
- Permission errors
- Disk space issues
- ZIP corruption detection

Failed backups are automatically cleaned up.

## Testing

Run the test suite:

```bash
pytest tests/
```

## Development

### Code Quality

Format code with Black:

```bash
black backup_zip_script/ tests/
```

Lint with Ruff:

```bash
ruff check backup_zip_script/ tests/
```

### Project Structure

```
19-backup-zip-script/
├── backup_zip_script/      # Main package
│   ├── __init__.py
│   ├── main.py            # CLI entry point
│   ├── core.py            # Core backup logic
│   └── utils.py           # Utility functions
├── tests/                 # Test suite
│   ├── __init__.py
│   └── test_backup_zip_script.py
├── requirements.txt       # Dependencies
├── README.md             # This file
├── CHECKLIST.md          # Feature checklist
└── SPEC.md               # Project specification
```

## Limitations

- Only supports ZIP compression (not other formats like TAR)
- Exclusion patterns use simple string matching (not regex)
- No encryption support (consider bonus features)
- No cloud upload support (consider bonus features)
- No incremental backup support (consider bonus features)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Format code with Black and Ruff
6. Submit a pull request

## License

This project is open source. See the repository for license details.

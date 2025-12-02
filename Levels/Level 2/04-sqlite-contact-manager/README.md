# SQLite Contact Manager

A professional command-line tool for managing contacts with SQLite database. This tool provides full CRUD operations, advanced search capabilities, CSV import/export, contact grouping, and custom fields support.

## Features

### Core Features
- ✅ **SQLite Database**: Robust SQLite database with proper schema design
- ✅ **CRUD Operations**: Create, Read, Update, Delete contacts via SQL queries
- ✅ **Advanced Search**: Both LIKE queries and FTS5 full-text search
- ✅ **CSV Import/Export**: Export contacts to CSV and import with duplicate detection
- ✅ **Contact Groups**: Organize contacts into groups/categories
- ✅ **Custom Fields**: Store additional data using JSON columns
- ✅ **Professional CLI**: User-friendly command-line interface with argparse

### Advanced Features
- 🔍 **Full-Text Search**: FTS5 virtual table for powerful search capabilities
- 📊 **Duplicate Detection**: Smart handling of duplicate contacts during import
- 🏷️ **Contact Grouping**: Organize contacts with multiple group assignments
- 📝 **Custom Fields**: Store any additional data as JSON
- 📈 **Timestamps**: Automatic created_at and updated_at tracking
- 🛡️ **Data Validation**: Comprehensive input validation and error handling
- 📋 **Detailed Logging**: Configurable logging for debugging and monitoring

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup

1. **Clone or download the project**
   ```bash
   cd 04-sqlite-contact-manager
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

4. **Install the package in development mode**
   ```bash
   pip install -e .
   ```

## Usage

### Basic Commands

#### Add a Contact
```bash
python -m sqlite_contact_manager add --name "John Doe" --email "john@example.com" --phone "555-1234"
```

#### Get a Contact
```bash
python -m sqlite_contact_manager get --id 1
```

#### List All Contacts
```bash
python -m sqlite_contact_manager list
python -m sqlite_contact_manager list --details  # Show full details
```

#### Search Contacts
```bash
python -m sqlite_contact_manager search "john"  # FTS5 search
python -m sqlite_contact_manager search "john" --no-fts  # LIKE search
python -m sqlite_contact_manager search "john" --details  # Show full details
```

#### Update a Contact
```bash
python -m sqlite_contact_manager update --id 1 --phone "555-5678" --company "Acme Corp"
```

#### Delete a Contact
```bash
python -m sqlite_contact_manager delete --id 1
```

### Advanced Features

#### Contact Groups
```bash
# Add contact with groups
python -m sqlite_contact_manager add --name "Jane Smith" --email "jane@example.com" --groups "work,friends"

# List all groups
python -m sqlite_contact_manager groups

# Get contacts in a specific group
python -m sqlite_contact_manager group-contacts --group "work"
```

#### Custom Fields
```bash
# Add contact with custom fields (requires JSON format)
python -m sqlite_contact_manager add --name "Bob Johnson" --email "bob@example.com" --custom-fields '{"department": "Engineering", "level": "Senior"}'
```

#### CSV Import/Export
```bash
# Export all contacts to CSV
python -m sqlite_contact_manager export --file contacts.csv

# Import contacts from CSV
python -m sqlite_contact_manager import --file contacts.csv

# Import with duplicate overwrite
python -m sqlite_contact_manager import --file contacts.csv --overwrite
```

### Database Management

#### Custom Database Location
```bash
python -m sqlite_contact_manager --db /path/to/custom.db add --name "Test User"
```

#### Verbose Logging
```bash
python -m sqlite_contact_manager --verbose search "test"
```

## Configuration

### Database Schema

The tool creates the following database structure:

```sql
-- Main contacts table
CREATE TABLE contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    address TEXT,
    company TEXT,
    notes TEXT,
    groups TEXT DEFAULT '[]',           -- JSON array of group names
    custom_fields TEXT DEFAULT '{}',    -- JSON object for custom data
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- FTS5 virtual table for full-text search
CREATE VIRTUAL TABLE contacts_fts USING fts5(
    name, email, phone, address, company, notes,
    content='contacts',
    content_rowid='id'
);
```

### CSV Format

The CSV import/export format includes all contact fields:

```csv
id,name,email,phone,address,company,notes,groups,custom_fields
1,John Doe,john@example.com,555-1234,123 Main St,Acme Corp,Notes here,"[""work""]","{""dept"": ""IT""}"
```

## Examples

### Complete Workflow Example

```bash
# 1. Add some contacts
python -m sqlite_contact_manager add --name "Alice Johnson" --email "alice@company.com" --phone "555-0001" --company "Tech Corp" --groups "work,colleagues"

python -m sqlite_contact_manager add --name "Bob Smith" --email "bob@company.com" --phone "555-0002" --company "Tech Corp" --groups "work,managers"

python -m sqlite_contact_manager add --name "Carol Davis" --email "carol@personal.com" --phone "555-0003" --groups "friends,family"

# 2. List all contacts
python -m sqlite_contact_manager list --details

# 3. Search for work contacts
python -m sqlite_contact_manager search "work" --details

# 4. Get contacts in specific group
python -m sqlite_contact_manager group-contacts --group "work"

# 5. Update a contact
python -m sqlite_contact_manager update --id 1 --phone "555-9999" --notes "Updated contact info"

# 6. Export to CSV
python -m sqlite_contact_manager export --file my_contacts.csv

# 7. Search with FTS5
python -m sqlite_contact_manager search "tech corp" --details
```

## Testing

Run the comprehensive test suite:

```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=sqlite_contact_manager

# Run specific test file
pytest tests/test_sqlite_contact_manager.py
```

The test suite includes:
- Database initialization tests
- CRUD operation tests
- Search functionality tests (both LIKE and FTS5)
- CSV import/export tests
- Contact group tests
- Error handling and validation tests
- Edge case testing

## Development

### Project Structure

```
04-sqlite-contact-manager/
├── sqlite_contact_manager/          # Main package
│   ├── __init__.py                 # Package initialization
│   ├── core.py                     # Core database operations
│   └── main.py                     # CLI interface
├── tests/                          # Test suite
│   ├── __init__.py
│   └── test_sqlite_contact_manager.py
├── requirements.txt                # Dependencies
├── README.md                       # This file
├── CHECKLIST.md                    # Feature checklist
└── SPEC.md                         # Project specification
```

### Code Quality

The project follows Python best practices:

- **Type Hints**: All public functions have type annotations
- **Docstrings**: Comprehensive documentation for all functions
- **Error Handling**: Proper exception handling with meaningful messages
- **Logging**: Structured logging for debugging and monitoring
- **Testing**: Comprehensive test coverage
- **Code Style**: Follows PEP 8 guidelines

### Running Tests

```bash
# Install development dependencies
pip install -r requirements.txt

# Run tests
pytest

# Run with coverage
pytest --cov=sqlite_contact_manager --cov-report=html

# Code formatting
black sqlite_contact_manager/ tests/

# Linting
ruff sqlite_contact_manager/ tests/
```

## Known Limitations

1. **Database File**: Uses SQLite file database (not suitable for high-concurrency applications)
2. **Custom Fields**: Limited to JSON storage (no complex data types)
3. **Search**: FTS5 search is limited to text fields only
4. **Import**: CSV import requires exact column names
5. **Groups**: Group names are case-sensitive

## Troubleshooting

### Common Issues

1. **Database Permission Errors**
   - Ensure write permissions in the database directory
   - Check if database file is locked by another process

2. **Import/Export Errors**
   - Verify CSV file format matches expected schema
   - Check file permissions for read/write access

3. **Search Not Working**
   - FTS5 requires SQLite 3.9+ with FTS5 extension
   - Try using `--no-fts` flag for LIKE search

4. **Memory Issues with Large Datasets**
   - Consider using `--no-fts` for large result sets
   - Export to CSV for external processing

### Debug Mode

Enable verbose logging to debug issues:

```bash
python -m sqlite_contact_manager --verbose [command]
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is part of a Python practice series and is available for educational purposes.

## Changelog

### Version 1.0.0
- Initial release
- Full CRUD operations
- FTS5 search support
- CSV import/export
- Contact grouping
- Custom fields support
- Comprehensive test suite
- Professional CLI interface

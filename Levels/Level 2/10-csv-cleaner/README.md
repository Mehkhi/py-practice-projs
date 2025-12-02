# CSV Data Cleaner

A professional command-line tool for cleaning and validating CSV data files. This tool helps you handle common data quality issues like missing values, inconsistent column names, type mismatches, and outliers.

## Features

### Core Functionality
- **CSV Loading**: Robust CSV file loading with error handling
- **Missing Value Handling**: Multiple strategies for dealing with missing data (drop, fill with mean/median/mode, or custom values)
- **Column Normalization**: Standardize column names (lowercase, strip spaces, replace spaces)
- **Type Coercion**: Automatic type detection and conversion, with manual type forcing support
- **Outlier Detection**: Identify outliers using Interquartile Range (IQR) method
- **Export with Summary**: Generate cleaned CSV files with detailed summary reports

### Bonus Features
- **YAML Configuration**: Flexible configuration system for customizing cleaning behavior
- **Error Logging**: Detailed error logs for troubleshooting data issues
- **Comprehensive Reporting**: Summary reports with statistics and data quality metrics

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup

1. **Clone or download the project**
   ```bash
   cd 10-csv-cleaner
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

## Usage

### Basic Usage

```bash
# Clean a CSV file with default settings
python -m csv_cleaner input.csv

# Specify output file
python -m csv_cleaner input.csv -o cleaned_output.csv

# Use custom configuration
python -m csv_cleaner input.csv -c config.yaml

# Enable verbose logging
python -m csv_cleaner input.csv -v
```

### Command Line Options

```
positional arguments:
  input_file            Input CSV file to clean

optional arguments:
  -h, --help            Show help message and exit
  -o OUTPUT, --output OUTPUT
                        Output CSV file path (default: input_cleaned.csv)
  -c CONFIG, --config CONFIG
                        YAML configuration file path
  -v, --verbose         Enable verbose logging
  --version             Show version and exit
```

### Configuration File

Create a `config.yaml` file to customize cleaning behavior:

```yaml
# CSV Cleaner Configuration File
missing_value_strategies:
  drop: false  # Set to true to drop rows with missing values
  fill_numeric: "mean"  # Options: mean, median, mode, or a specific number
  fill_categorical: "mode"  # Options: mode or a specific string
  fill_constant: "Unknown"  # Default value for constant filling

column_normalization:
  lowercase: true  # Convert column names to lowercase
  strip_spaces: true  # Remove leading/trailing spaces
  replace_spaces: "_"  # Replace spaces with this character

type_detection:
  auto_detect: true  # Automatically detect and convert data types
  force_types:  # Force specific types for columns
    "age": "int64"
    "price": "float64"
    "date": "datetime64"

outlier_detection:
  enabled: true  # Enable outlier detection
  method: "iqr"  # Method: iqr (Interquartile Range)
  threshold: 1.5  # Threshold multiplier for outlier detection

export:
  include_summary: true  # Generate summary report
  include_error_log: true  # Export error log if any errors occur
```

## Examples

### Example 1: Basic Cleaning

```bash
# Clean sample data with default settings
python -m csv_cleaner sample_data.csv
```

**Input (`sample_data.csv`):**
```csv
Name,Age,Email,Salary,Department,Start Date
John Doe,25,john.doe@email.com,50000,Engineering,2023-01-15
Jane Smith,30,jane.smith@email.com,60000,Marketing,2023-02-20
Bob Johnson,,bob.johnson@email.com,55000,Engineering,2023-03-10
Alice Brown,28,alice.brown@email.com,,Sales,2023-04-05
```

**Output:**
- `sample_data_cleaned.csv` - Cleaned data
- `sample_data_cleaned_summary.txt` - Summary report

### Example 2: Custom Configuration

```bash
# Use custom configuration for aggressive cleaning
python -m csv_cleaner messy_data.csv -c aggressive_config.yaml
```

**Configuration (`aggressive_config.yaml`):**
```yaml
missing_value_strategies:
  drop: true  # Drop rows with any missing values
column_normalization:
  lowercase: true
  strip_spaces: true
  replace_spaces: "_"
outlier_detection:
  enabled: true
  threshold: 1.0  # More sensitive outlier detection
```

### Example 3: Verbose Output

```bash
# Get detailed logging information
python -m csv_cleaner large_dataset.csv -v -o cleaned_large.csv
```

## Output Files

### Cleaned CSV
The main output file containing the cleaned data with:
- Normalized column names
- Handled missing values
- Converted data types
- Outlier flags (if enabled)

### Summary Report
A text file with detailed cleaning statistics:
```
CSV Cleaning Summary Report
==================================================

Generated: 2023-12-07 14:30:25

Data Overview:
  Original rows: 1000
  Cleaned rows: 950
  Dropped rows: 50
  Columns: 8

Cleaning Operations:
  Columns normalized: 5
  Missing values filled: 120
  Type conversions: 3
  Outliers detected: 15

Column Information:
  name: object (0 nulls)
  age: int64 (0 nulls)
  salary: float64 (0 nulls)
  department: object (0 nulls)
```

### Error Log (if applicable)
A CSV file containing any errors or warnings encountered during cleaning.

## Testing

Run the test suite to verify functionality:

```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=csv_cleaner
```

## Project Structure

```
10-csv-cleaner/
├── csv_cleaner/           # Main package
│   ├── __init__.py
│   ├── core.py           # Core cleaning functionality
│   └── main.py           # CLI interface
├── tests/                 # Test suite
│   ├── __init__.py
│   └── test_csv_cleaner.py
├── requirements.txt       # Dependencies
├── config.yaml           # Default configuration
├── sample_data.csv       # Sample data for testing
├── README.md             # This file
├── CHECKLIST.md          # Feature checklist
└── SPEC.md              # Project specification
```

## Dependencies

- **pandas**: Data manipulation and analysis
- **numpy**: Numerical computing
- **pyyaml**: YAML configuration file parsing

## Error Handling

The tool includes comprehensive error handling for:
- File not found errors
- Empty or corrupted CSV files
- Invalid configuration files
- Type conversion errors
- Memory issues with large files

## Performance

- Optimized for files up to 100MB
- Memory-efficient processing
- Progress logging for large files
- Configurable batch processing

## Limitations

- Currently supports CSV format only
- Large files (>1GB) may require additional memory
- Outlier detection only supports IQR method
- Type conversion may fail with complex data formats

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is part of the Python Practice Projects series and is available for educational use.

## Support

For issues and questions:
1. Check the error logs for detailed error messages
2. Review the configuration file for proper settings
3. Test with the provided sample data
4. Check the test suite for expected behavior

## Changelog

### Version 1.0.0
- Initial release
- Core CSV cleaning functionality
- YAML configuration support
- Comprehensive test suite
- CLI interface with argparse
- Error handling and logging
- Summary report generation

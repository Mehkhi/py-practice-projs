# Excel Report Builder

A professional Python CLI tool for generating formatted Excel reports from CSV data. This tool provides powerful features for data visualization, formatting, and analysis with support for charts, formulas, conditional formatting, and multiple sheets.

## Features

### Core Features
- ✅ **CSV Data Import**: Load data from CSV files with automatic validation
- ✅ **Excel Generation**: Create professional Excel workbooks with openpyxl
- ✅ **Data Formatting**: Apply bold headers, colors, borders, and alignment
- ✅ **Formulas**: Add automatic sum, average, and custom formulas
- ✅ **Charts**: Create bar, line, and pie charts with customizable styling
- ✅ **Multiple Sheets**: Generate reports with multiple worksheets
- ✅ **Conditional Formatting**: Highlight cells based on conditions
- ✅ **Summary Sheets**: Automatic generation of summary statistics

### Bonus Features
- ✅ **Data Analysis**: Built-in data analysis and column type detection
- ✅ **Chart Suggestions**: Intelligent chart type recommendations
- ✅ **Color Schemes**: Multiple color palettes for charts
- ✅ **Sample Data Generation**: Create test data for development
- ✅ **Comprehensive CLI**: Full command-line interface with multiple commands

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup

1. **Clone or download the project**
   ```bash
   cd 23-excel-report-builder
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

4. **Install the package in development mode**
   ```bash
   pip install -e .
   ```

## Quick Start

### 1. Generate Sample Data
```bash
python -m excel_report_builder sample-data --rows 50 --output sample_data.csv
```

### 2. Create a Basic Report
```bash
python -m excel_report_builder generate -i sample_data.csv -o report.xlsx
```

### 3. Create a Report with Charts
```bash
python -m excel_report_builder generate -i sample_data.csv -o report.xlsx \
    --chart-type bar --x-column Product --y-column Sales \
    --chart-title "Sales by Product"
```

### 4. Create a Full-Featured Report
```bash
python -m excel_report_builder generate -i sample_data.csv -o report.xlsx \
    --add-summary --add-formulas --conditional-format \
    --chart-type line --x-column Date --y-column Sales
```

## Usage

### Command Line Interface

The tool provides three main commands:

#### 1. `generate` - Create Excel Reports

Generate Excel reports from CSV data with various formatting and visualization options.

**Basic Usage:**
```bash
python -m excel_report_builder generate -i input.csv -o output.xlsx
```

**Options:**
- `-i, --input`: Input CSV file path (required)
- `-o, --output`: Output Excel file path (required)
- `-s, --sheet-name`: Name for the data sheet (default: "Data")
- `-c, --chart-type`: Type of chart to create (bar, line, pie)
- `--x-column`: Column name for x-axis (required for charts)
- `--y-column`: Column name for y-axis (required for charts)
- `--chart-title`: Title for the chart
- `--add-summary`: Add a summary sheet with statistics
- `--add-formulas`: Add basic formulas (sums, averages)
- `--conditional-format`: Add conditional formatting
- `-v, --verbose`: Enable verbose logging

**Examples:**

```bash
# Basic report
python -m excel_report_builder generate -i sales.csv -o sales_report.xlsx

# Report with bar chart
python -m excel_report_builder generate -i sales.csv -o report.xlsx \
    --chart-type bar --x-column Product --y-column Sales

# Full-featured report
python -m excel_report_builder generate -i data.csv -o report.xlsx \
    --add-summary --add-formulas --conditional-format \
    --chart-type line --x-column Date --y-column Revenue \
    --chart-title "Revenue Trend"
```

#### 2. `sample-data` - Generate Sample Data

Create sample CSV data for testing and development.

**Usage:**
```bash
python -m excel_report_builder sample-data --output sample.csv --rows 100
```

**Options:**
- `-o, --output`: Output CSV file path (default: "sample_data.csv")
- `-r, --rows`: Number of rows to generate (default: 100)

#### 3. `analyze` - Analyze CSV Files

Analyze a CSV file and get suggestions for report configuration.

**Usage:**
```bash
python -m excel_report_builder analyze -i data.csv
```

**Output includes:**
- Data summary (rows, columns, data types)
- Numeric and date column detection
- Chart type suggestions
- Missing value analysis

### Programmatic Usage

You can also use the Excel Report Builder as a Python library:

```python
from excel_report_builder import ExcelReportBuilder
import pandas as pd

# Create a report builder
builder = ExcelReportBuilder("output.xlsx")

# Load data
df = pd.read_csv("data.csv")
builder.create_sheet_from_dataframe(df, "My Data")

# Add formulas
formulas = {
    'B10': '=SUM(B2:B9)',
    'C10': '=AVERAGE(C2:C9)'
}
builder.add_formulas("My Data", formulas)

# Create a chart
builder.create_chart(
    "My Data",
    "bar",
    "B2:B9",
    "A2:A9",
    "Sales Chart"
)

# Add conditional formatting
builder.add_conditional_formatting(
    "My Data",
    "B2:B9",
    "greater_than",
    100,
    "90EE90"
)

# Save the workbook
builder.save_workbook()
```

## Configuration

### Data Format Requirements

The tool works with CSV files that have:
- Headers in the first row
- Consistent data types within columns
- No special characters in column names (for best results)

### Supported Chart Types

- **Bar Charts**: Best for categorical data comparison
- **Line Charts**: Ideal for time series and trends
- **Pie Charts**: Good for showing proportions

### Color Schemes

The tool includes several built-in color schemes:
- `default`: Professional blue theme
- `pastel`: Soft, muted colors
- `dark`: Dark theme for presentations
- `bright`: Vibrant, high-contrast colors

## Examples

### Example 1: Sales Report

```bash
# Generate sample sales data
python -m excel_report_builder sample-data --output sales_data.csv --rows 30

# Create sales report with bar chart
python -m excel_report_builder generate -i sales_data.csv -o sales_report.xlsx \
    --chart-type bar --x-column Product --y-column Sales \
    --add-summary --add-formulas --conditional-format
```

### Example 2: Employee Analysis

```bash
# Analyze employee data
python -m excel_report_builder analyze -i employee_data.csv

# Create employee report with line chart
python -m excel_report_builder generate -i employee_data.csv -o employee_report.xlsx \
    --chart-type line --x-column Department --y-column Salary \
    --chart-title "Salary by Department"
```

### Example 3: Financial Dashboard

```bash
# Create comprehensive financial dashboard
python -m excel_report_builder generate -i financial_data.csv -o dashboard.xlsx \
    --add-summary --add-formulas --conditional-format \
    --chart-type pie --x-column Category --y-column Amount \
    --chart-title "Expense Distribution"
```

## Testing

Run the test suite to ensure everything works correctly:

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all tests
pytest tests/

# Run tests with coverage
pytest tests/ --cov=excel_report_builder --cov-report=html

# Run specific test file
pytest tests/test_excel_report_builder.py -v
```

## Project Structure

```
23-excel-report-builder/
├── excel_report_builder/          # Main package
│   ├── __init__.py               # Package initialization
│   ├── main.py                   # CLI interface
│   ├── core.py                   # Core Excel generation logic
│   └── utils.py                  # Utility functions
├── tests/                        # Test suite
│   ├── __init__.py
│   └── test_excel_report_builder.py
├── sample_sales_data.csv         # Sample sales data
├── sample_employee_data.csv      # Sample employee data
├── requirements.txt              # Dependencies
├── README.md                     # This file
├── CHECKLIST.md                  # Feature checklist
└── SPEC.md                       # Project specification
```

## Dependencies

- **openpyxl**: Excel file generation and manipulation
- **pandas**: Data processing and analysis
- **click**: Command-line interface
- **pytest**: Testing framework
- **black**: Code formatting
- **ruff**: Code linting

## Error Handling

The tool includes comprehensive error handling for:
- Invalid CSV files
- Missing columns
- File permission issues
- Data type mismatches
- Memory limitations

All errors are logged with descriptive messages to help with debugging.

## Performance

- Handles CSV files up to 100,000 rows efficiently
- Memory usage scales linearly with data size
- Chart generation optimized for datasets up to 1,000 points
- Automatic data sampling for large datasets in charts

## Limitations

- Maximum chart data points: 1,000 (larger datasets are automatically sampled)
- Excel file size limit: ~1GB (depends on system memory)
- Chart types: Bar, Line, and Pie charts only
- CSV encoding: UTF-8 recommended

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is part of a Python learning curriculum and is intended for educational purposes.

## Support

For issues and questions:
1. Check the examples in this README
2. Run the `analyze` command on your data
3. Check the test files for usage examples
4. Review the error messages for specific guidance

## Changelog

### Version 1.0.0
- Initial release
- Core Excel generation functionality
- Chart creation (bar, line, pie)
- Conditional formatting
- Multiple sheet support
- CLI interface
- Comprehensive test suite
- Sample data generation
- Data analysis tools

---

**Happy Excel Report Building! 📊✨**

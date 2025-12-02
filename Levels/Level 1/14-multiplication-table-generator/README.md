# Multiplication Table Generator

A command-line program that generates beautifully formatted multiplication tables with customizable ranges, alignment, and export capabilities. Perfect for students, teachers, and anyone who needs quick access to multiplication tables.

## Features

### Core Features
- **Generate N×N Tables**: Create multiplication tables of any size
- **Custom Ranges**: Generate tables for any number range (e.g., 5-12)
- **Perfect Alignment**: Automatic column and row alignment for readability
- **Input Validation**: Robust validation with helpful error messages
- **Formatted Display**: Clean, professional table formatting

### Advanced Features
- **Color-Coded Output**: Visual distinction between headers, even, and odd numbers
- **CSV Export**: Save tables to CSV files for use in spreadsheets
- **Multiple Table Types**: Standard (1-10), custom ranges, and N×N tables
- **Interactive Menu**: User-friendly command-line interface
- **Table Information**: Detailed statistics about generated tables

## Installation

No installation required! This program uses only Python's standard library.

### Requirements
- Python 3.7 or higher

## Usage

### Running the Program
```bash
python multiplication_table_generator.py
```

### Interactive Menu
Once running, you'll see a menu with these options:

1. **Generate standard table (1-10)** - Quick classic multiplication table
2. **Generate custom range table** - Specify your own start and end numbers
3. **Generate N×N table** - Create a square table from 1 to N
4. **Display current table** - Show the last generated table with info
5. **Export table to CSV** - Save the current table to a CSV file
6. **Toggle color output** - Enable/disable color coding
7. **Exit** - Quit the program

### Example Session
```
$ python multiplication_table_generator.py
Welcome to the Multiplication Table Generator!
Create beautiful, formatted multiplication tables with ease.

============================================================
[NUMBERS] MULTIPLICATION TABLE GENERATOR [NUMBERS]
============================================================
1. Generate standard table (1-10)
2. Generate custom range table
3. Generate N×N table
4. Display current table
5. Export table to CSV
6. Toggle color output
7. Exit
============================================================

Enter your choice (1-7): 3

Enter size for N×N multiplication table
Enter N (table size): 5

[OK] 5×5 multiplication table generated!

Multiplication Table (1 to 5)
===============================================================
     |     1  |     2  |     3  |     4  |     5
-----+--------+--------+--------+--------+--------
   1 |     1  |     2  |     3  |     4  |     5
   2 |     2  |     4  |     6  |     8  |    10
   3 |     3  |     6  |     9  |    12  |    15
   4 |     4  |     8  |    12  |    16  |    20
   5 |     5  |    10  |    15  |    20  |    25

Press Enter to continue...
```

## Table Types

### Standard Table (1-10)
The classic multiplication table everyone learns in school:
- Headers from 1 to 10
- All multiplication results from 1×1 to 10×10
- Perfect alignment and formatting

### Custom Range Table
Generate tables for specific number ranges:
- Choose any start and end numbers
- Automatically handles reversed ranges (10-5 becomes 5-10)
- Great for focusing on specific multiplication facts

### N×N Table
Create square tables from 1 to N:
- Perfect for practice sessions
- Common sizes: 5×5, 10×10, 12×12, 20×20
- Automatically adjusts column width for large numbers

## Color Coding

When color output is enabled:
- **Blue headers**: Row and column numbers
- **Green cells**: Even multiplication results
- **Red cells**: Odd multiplication results

This visual distinction helps with pattern recognition and learning.

## CSV Export

Export your multiplication tables to CSV format for:
- Import into spreadsheet applications (Excel, Google Sheets)
- Further analysis and manipulation
- Printing and sharing
- Creating custom worksheets

### CSV Format
- First row: Empty cell followed by column headers
- First column: Row headers
- Interior cells: Multiplication results

Example CSV content:
```csv
,1,2,3,4,5
1,1,2,3,4,5
2,2,4,6,8,10
3,3,6,9,12,15
```

## Testing

Run the unit tests to verify functionality:

```bash
python -m pytest test_multiplication_table_generator.py -v
```

Or run with unittest:

```bash
python -m unittest test_multiplication_table_generator.py
```

### Test Coverage
- Input validation for all parameter types
- Table generation for various ranges and sizes
- Formatting with and without color
- CSV export functionality
- Error handling and edge cases
- Integration workflows

## Project Structure

```
14-multiplication-table-generator/
├── multiplication_table_generator.py  # Main program
├── test_multiplication_table_generator.py  # Unit tests
├── README.md                           # This file
├── CHECKLIST.md                        # Feature checklist
└── SPEC.md                            # Project specification
```

## Code Structure

### Main Classes

#### `MultiplicationTableGenerator`
The core class that handles all table generation functionality:

- `validate_input()` - Validate user input with detailed error messages
- `generate_table()` - Create multiplication tables for any range
- `format_table()` - Format tables with optional color coding
- `export_to_csv()` - Export tables to CSV files
- `get_table_info()` - Get detailed information about current table
- `get_column_width()` - Calculate optimal column width

### Key Functions

- `display_menu()` - Show interactive menu options
- `handle_*()` methods - Process user choices
- `main()` - Main application loop

## Use Cases

### Education
- **Students**: Practice multiplication facts
- **Teachers**: Create worksheets and teaching materials
- **Parents**: Help children with homework
- **Tutors**: Generate practice materials

### Professional
- **Mathematicians**: Quick reference for calculations
- **Engineers**: Verify multiplication results
- **Data analysts**: Create lookup tables
- **Researchers**: Generate mathematical data

### Personal
- **Learning**: Improve mental math skills
- **Teaching**: Help others learn multiplication
- **Reference**: Quick access to multiplication facts
- **Practice**: Create custom drills

## Input Validation

The program validates all user input:

### Positive Integers
- Must be greater than 0
- Maximum value of 100 for table sizes
- Clear error messages for invalid input

### Range Values
- Start and end values between 1 and 1000
- Automatic handling of reversed ranges
- Prevents excessively large tables

### File Names
- Automatic CSV extension addition
- Default naming based on table parameters
- Error handling for file permission issues

## Performance

- Efficient table generation using nested loops
- Minimal memory usage for large tables
- Fast CSV export with Python's csv module
- Responsive user interface

## Limitations

- Maximum table size: 1000×1000 (to prevent memory issues)
- Color output requires terminal support
- CSV export limited to current table only
- No persistent storage of table history

## Learning Objectives

This project demonstrates:
- **Nested loops** for table generation
- **String formatting** for alignment
- **Input validation** with error handling
- **File I/O** for CSV export
- **Color output** using ANSI escape codes
- **Menu-driven interfaces**
- **Data structures** (2D lists)
- **Algorithmic thinking** (multiplication patterns)

## Extension Ideas

After mastering the basics, consider adding:
- GUI interface with tkinter or pygame
- Additional mathematical operations (addition, subtraction)
- Custom formatting options
- Batch table generation
- Interactive quiz mode
- Historical tracking of generated tables
- Integration with educational platforms
- Support for other mathematical tables (division, squares)

## Troubleshooting

### Common Issues

**"Table too large" error**
- Reduce the table size to under 1000×1000
- Consider using custom ranges instead

**Color output not working**
- Check if your terminal supports ANSI color codes
- Toggle color off using menu option 6

**CSV export fails**
- Check file permissions in the current directory
- Ensure the filename is valid
- Try using a different filename

**Table formatting looks wrong**
- Make sure your terminal uses a monospace font
- Adjust terminal width if table is too wide
- Try smaller table sizes for better display

### Performance Tips

- For very large tables, consider using custom ranges
- CSV export is faster than displaying large tables
- Color output has minimal performance impact
- Table generation is optimized for speed

## Contributing

This is a learning project. Feel free to:
- Add new table types
- Improve formatting options
- Enhance error messages
- Add more test cases
- Optimize performance
- Add new export formats

## License

This project is open source and available for educational purposes.

---

**[NUMBERS] Happy Multiplying! [NUMBERS]**

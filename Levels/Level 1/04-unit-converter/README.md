# Unit Converter

A command-line unit converter that supports conversions between different units of length, weight, and volume. Built with Python as a beginner-friendly project to practice fundamental programming concepts.

## What This Project Does

The Unit Converter is a interactive command-line application that allows users to:
- Convert between different units within the same category (length, weight, volume)
- View conversion history
- Clear conversion history
- Handle invalid input gracefully with helpful error messages

## Features

### Core Features
- **Multiple Unit Categories**: Supports length, weight, and volume conversions
- **Conversion Factor Dictionary**: Uses a comprehensive dictionary of conversion factors
- **Bidirectional Conversion Logic**: Convert from any unit to any other unit within the same category
- **Input Validation**: Validates user input and provides clear error messages

### Bonus Features
- **Conversion History Log**: Tracks and displays recent conversions
- **Persistent Storage**: Saves conversion history to a JSON file
- **Comprehensive Unit Support**: Includes metric and imperial units

## Supported Units

### Length Units
- **Metric**: millimeter (mm), centimeter (cm), meter (m), kilometer (km)
- **Imperial**: inch (in), foot (ft), yard (yd), mile (mi)

### Weight Units
- **Metric**: milligram (mg), gram (g), kilogram (kg), metric ton (ton)
- **Imperial**: ounce (oz), pound (lb)

### Volume Units
- **Metric**: milliliter (ml), liter (l)
- **Imperial**: fluid ounce (fl_oz), cup, pint (pt), quart (qt), gallon (gal)

## How to Run

### Prerequisites
- Python 3.7 or higher
- No additional packages required (uses only standard library)

### Running the Application

1. **Clone or download** the project files
2. **Navigate** to the project directory:
   ```bash
   cd 04-unit-converter
   ```
3. **Run** the main program:
   ```bash
   python unit_converter.py
   ```

### Running Tests

To run the unit tests:
```bash
python test_unit_converter.py
```

## Example Usage

### Basic Conversion
```
[WRENCH] UNIT CONVERTER
==================================================
1. Convert units
2. View conversion history
3. Clear history
4. Exit
==================================================

Enter your choice (1-4): 1

[CLIPBOARD] Available Categories:
  1. Length
  2. Weight
  3. Volume

Select category (1-3): 1

[RULER] Available Length Units:
  1. mm
  2. cm
  3. m
  4. km
  5. in
  6. ft
  7. yd
  8. mi

Select source unit (1-8): 3
Select target unit (1-8): 2

Enter value to convert from m to cm: 5

[OK] Conversion Result:
   5 m = 500.000000 cm
```

### Viewing History
```
Enter your choice (1-4): 2

[MEMO] Conversion History (3 entries):
------------------------------------------------------------
 1. 5.0 m → 500.000000 cm (length)
 2. 10.0 kg → 10000.000000 g (weight)
 3. 2.0 l → 2000.000000 ml (volume)
```

## Project Structure

```
04-unit-converter/
├── unit_converter.py      # Main application
├── test_unit_converter.py # Unit tests
├── README.md             # This file
├── CHECKLIST.md          # Feature checklist
├── SPEC.md               # Project specification
└── conversion_history.json # Generated history file
```

## Key Learning Concepts

This project demonstrates:
- **Object-Oriented Programming**: Using classes to organize code
- **Data Structures**: Dictionaries for conversion factors, lists for history
- **Input/Output**: Reading user input and displaying formatted output
- **Error Handling**: Validating input and handling edge cases
- **File I/O**: Saving and loading conversion history
- **Functions**: Breaking code into reusable, testable functions
- **Type Hints**: Using Python type annotations for better code clarity

## Testing

The project includes comprehensive unit tests covering:
- Unit conversions across all categories
- Input validation
- Error handling for invalid inputs
- History management functionality
- Edge cases and boundary conditions

Run tests with:
```bash
python test_unit_converter.py
```

## Code Quality

- **Consistent Formatting**: Code follows PEP 8 style guidelines
- **Type Hints**: Functions include type annotations for better code clarity
- **Error Handling**: Comprehensive input validation and error messages
- **Documentation**: Well-documented code with docstrings
- **Modular Design**: Code organized into logical functions and classes

## Future Enhancements

Potential improvements could include:
- Additional unit categories (temperature, area, speed)
- Custom conversion factors from configuration files
- Chained conversions (e.g., m → ft → in)
- Graphical user interface
- API integration for real-time conversion rates
- Export functionality for conversion history

## Troubleshooting

### Common Issues

1. **"python: command not found"**
   - Make sure Python is installed and in your PATH
   - Try `python3` instead of `python`

2. **Permission errors with history file**
   - The program will continue to work without saving history
   - Check file permissions in the project directory

3. **Invalid input errors**
   - Enter positive numbers only
   - Use the menu numbers (1, 2, 3, etc.) for selections
   - Type 'q' or 'quit' to exit from any input prompt

## Contributing

This is a learning project, but suggestions for improvements are welcome:
- Additional unit categories
- Better error messages
- Enhanced user interface
- Performance optimizations

## License

This project is created for educational purposes as part of a Python learning curriculum.

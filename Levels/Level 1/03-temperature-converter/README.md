# Temperature Converter

A command-line Python program for converting temperatures between Celsius, Fahrenheit, and Kelvin scales.

## What the Project Does

This program provides a user-friendly interface for converting temperatures between three common temperature scales:
- **Celsius** (°C) - Metric system standard
- **Fahrenheit** (°F) - Common in the United States
- **Kelvin** (K) - Scientific standard (absolute temperature)

The program features:
- Menu-driven interface for easy navigation
- Input validation to prevent crashes on invalid input
- Formatted output with proper rounding
- Support for all six possible conversion combinations

## How to Run It

### Prerequisites
- Python 3.7 or higher
- No additional packages required (uses only standard library)

### Running the Program

1. Navigate to the project directory:
   ```bash
   cd 03-temperature-converter
   ```

2. Run the main program:
   ```bash
   python temperature_converter.py
   ```

3. Follow the on-screen prompts to select conversion type and enter temperature values.

### Running Tests

To verify the conversion functions work correctly:

```bash
python test_temperature_converter.py
```

Or if you have pytest installed:
```bash
pytest test_temperature_converter.py
```

## Example Usage

```
$ python temperature_converter.py
Welcome to the Temperature Converter!

==================================================
TEMPERATURE CONVERTER
==================================================
1. Celsius to Fahrenheit
2. Fahrenheit to Celsius
3. Celsius to Kelvin
4. Kelvin to Celsius
5. Fahrenheit to Kelvin
6. Kelvin to Fahrenheit
7. Exit
==================================================
Enter your choice (1-7): 1
Enter temperature in Celsius: 25

Conversion Result:
25.00°C = 77.00°F

Would you like to perform another conversion? (y/n): y

==================================================
TEMPERATURE CONVERTER
==================================================
1. Celsius to Fahrenheit
2. Fahrenheit to Celsius
3. Celsius to Kelvin
4. Kelvin to Celsius
5. Fahrenheit to Kelvin
6. Kelvin to Fahrenheit
7. Exit
==================================================
Enter your choice (1-7): 3
Enter temperature in Celsius: 0

Conversion Result:
0.00°C = 273.15°K

Would you like to perform another conversion? (y/n): n
Thank you for using the Temperature Converter. Goodbye!
```

## Conversion Formulas

The program uses these standard conversion formulas:

- **Celsius to Fahrenheit**: `F = (C * 9/5) + 32`
- **Fahrenheit to Celsius**: `C = (F - 32) * 5/9`
- **Celsius to Kelvin**: `K = C + 273.15`
- **Kelvin to Celsius**: `C = K - 273.15`
- **Fahrenheit to Kelvin**: `K = (F - 32) * 5/9 + 273.15`
- **Kelvin to Fahrenheit**: `F = (K - 273.15) * 9/5 + 32`

## Features

### Required Features (complete)
- [x] Menu-driven unit selection
- [x] Celsius/Fahrenheit/Kelvin conversions
- [x] Input validation
- [x] Formatted output with rounding

### Error Handling
- Validates numeric input and handles non-numeric entries gracefully
- Prevents program crashes on invalid input
- Provides clear error messages to guide users

### Code Quality
- Well-documented functions with type hints
- Clear variable names and consistent formatting
- Modular design with separate functions for each conversion
- Comprehensive test coverage

## File Structure

```
03-temperature-converter/
|-- temperature_converter.py    # Main program
|-- test_temperature_converter.py  # Unit tests
|-- README.md                   # This file
|-- CHECKLIST.md               # Feature checklist
`-- SPEC.md                    # Project specification
```

## Learning Objectives

This project demonstrates:
- Basic Python syntax and data types
- User input/output handling
- Control flow (if/else, loops)
- Function definition and organization
- Error handling with try/except
- Type hints and documentation
- Unit testing basics

## Troubleshooting

**Problem**: Program crashes on invalid input
**Solution**: The program includes input validation. If you encounter issues, ensure you're entering numeric values for temperatures.

**Problem**: Conversion results seem incorrect
**Solution**: Check that you've selected the correct conversion type. The program uses standard scientific formulas.

**Problem**: Tests fail
**Solution**: Ensure you're running the tests from the correct directory and that all files are present.

## Future Enhancements

Potential improvements for advanced users:
- Batch conversion from CSV files
- Conversion table generation
- Save conversion history
- Graphical user interface
- Additional temperature scales (Rankine, etc.)

---

**Note**: This is a beginner-level project focused on learning Python fundamentals. The code prioritizes clarity and educational value over advanced optimization techniques.

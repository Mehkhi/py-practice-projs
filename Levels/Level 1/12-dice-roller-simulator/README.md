# Dice Roller Simulator

A command-line dice rolling program that supports standard dice notation like "3d6" (roll 3 six-sided dice) and modifiers like "2d6+3". Perfect for tabletop RPGs, board games, or probability experiments.

## Features

### Core Features
- **Dice Notation Parsing**: Supports standard format like `3d6`, `2d8+3`, `d20-2`
- **Random Roll Generation**: Uses Python's `random` module for fair dice rolls
- **Modifier Support**: Add or subtract modifiers from your rolls
- **Roll History**: Track all your rolls with detailed results
- **Statistics**: View average, min, max, and total of your rolls
- **Interactive Menu**: User-friendly command-line interface

### Supported Dice Notation
- `3d6` - Roll 3 six-sided dice
- `2d8+3` - Roll 2 eight-sided dice and add 3
- `d20-2` - Roll 1 twenty-sided die and subtract 2
- `1d4` - Roll 1 four-sided die
- `100d6` - Roll up to 100 dice at once

## Installation

No installation required! This program uses only Python's standard library.

### Requirements
- Python 3.7 or higher

## Usage

### Running the Program
```bash
python dice_roller_simulator.py
```

### Interactive Menu
Once running, you'll see a menu with these options:

1. **Roll dice** - Enter dice notation to roll
2. **View roll history** - See all previous rolls
3. **View statistics** - See roll statistics
4. **Clear history** - Reset roll history
5. **Exit** - Quit the program

### Example Session
```
$ python dice_roller_simulator.py
Welcome to the Dice Roller Simulator!
Roll dice using standard notation like 3d6, 2d6+3, or d20.

==================================================
[DICE] DICE ROLLER SIMULATOR [DICE]
==================================================
1. Roll dice (e.g., 3d6, 2d6+3, d20)
2. View roll history
3. View statistics
4. Clear history
5. Exit
==================================================

Enter your choice (1-5): 1

Enter dice notation (e.g., 3d6, 2d6+3, d20)
Format: [number]d[sides][+/-modifier]
Dice notation: 3d6+2

[DICE] 3d6+2: 4 + 2 + 5 + 2 = 13
   Individual rolls: [4, 2, 5]

Press Enter to continue...
```

## Testing

Run the unit tests to verify functionality:

```bash
python -m pytest test_dice_roller_simulator.py -v
```

Or run with unittest:

```bash
python -m unittest test_dice_roller_simulator.py
```

### Test Coverage
- Dice notation parsing (valid and invalid inputs)
- Random roll generation
- Modifier handling
- Roll history tracking
- Statistics calculation
- Error handling

## Project Structure

```
12-dice-roller-simulator/
├── dice_roller_simulator.py    # Main program
├── test_dice_roller_simulator.py  # Unit tests
├── README.md                   # This file
├── CHECKLIST.md                # Feature checklist
└── SPEC.md                     # Project specification
```

## Code Structure

### Main Classes

#### `DiceRoller`
The core class that handles all dice rolling functionality:

- `parse_dice_notation(notation)` - Parse dice strings into components
- `roll_dice(num_dice, num_sides)` - Generate random dice rolls
- `roll_with_notation(notation)` - Complete roll with notation
- `get_roll_history()` - Retrieve roll history
- `get_statistics()` - Calculate roll statistics
- `clear_history()` - Reset roll history

### Key Functions

- `display_menu()` - Show the interactive menu
- `handle_roll(dice_roller)` - Process roll requests
- `handle_history(dice_roller)` - Display roll history
- `handle_statistics(dice_roller)` - Show statistics
- `main()` - Main program loop

## Error Handling

The program gracefully handles:
- Invalid dice notation format
- Invalid numbers (negative dice, zero sides)
- Too many dice (limit: 100)
- Empty input
- Non-numeric values

## Learning Objectives

This project demonstrates:
- **String parsing** with regular expressions
- **Random number generation**
- **Data structures** (lists, dictionaries)
- **Error handling** with try/except
- **Object-oriented programming** with classes
- **User input validation**
- **File I/O** concepts (history tracking)
- **Unit testing** with unittest framework

## Extension Ideas

After mastering the basics, consider adding:
- Advantage/disadvantage mechanics (D&D 5e)
- Custom dice with non-standard sides
- Probability calculations
- Roll result filtering
- Export history to file
- Color output with `colorama`
- GUI interface with tkinter or pygame

## Common Issues & Solutions

### "Invalid dice notation" Error
- Ensure format: `[number]d[sides][+/-modifier]`
- Examples: `3d6`, `2d8+3`, `d20`, `1d4-1`
- No spaces in the notation

### Large Numbers
- Maximum 100 dice per roll to prevent performance issues
- Maximum sides per die: 1000

### Random Results
- Results are truly random using Python's `random.randint()`
- For testing, use the unit tests which mock random values

## Contributing

This is a learning project. Feel free to:
- Add new features
- Improve error messages
- Enhance the user interface
- Add more test cases
- Optimize performance

## License

This project is open source and available for educational purposes.

---

**Happy Rolling! [DICE]**

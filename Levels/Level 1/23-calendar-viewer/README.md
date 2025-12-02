# Calendar Viewer

A simple command-line calendar application built with Python that displays monthly calendars, manages events, and provides intuitive navigation features.

## What This Project Does

The Calendar Viewer is a beginner-friendly Python application that demonstrates core programming concepts including:

- **Calendar Display**: Shows monthly calendars with proper formatting and alignment
- **Date Navigation**: Navigate between months and years easily
- **Today Highlighting**: Clearly marks today's date in the calendar
- **Event Management**: Add, view, and manage events for specific dates
- **Data Persistence**: Save and load events from a JSON file
- **Week Numbers**: Display week numbers for better date reference
- **Interactive Menu**: User-friendly command-line interface

## Features

### Required Features [OK]
- [x] Display current month calendar
- [x] Navigate to previous/next months
- [x] Highlight today's date
- [x] Proper alignment and formatting

### Bonus Features [OK]
- [x] Add and display events
- [x] Save events to JSON
- [x] Show week numbers

## How to Run

### Prerequisites
- Python 3.7 or higher
- No additional packages required (uses only standard library)

### Running the Application

1. **Navigate to the project directory:**
   ```bash
   cd 23-calendar-viewer
   ```

2. **Run the calendar viewer:**
   ```bash
   python calendar_viewer.py
   ```

3. **Follow the on-screen prompts** to navigate and interact with the calendar.

### Running Tests

To run the unit tests:

```bash
python test_calendar_viewer.py
```

## Example Usage

### Basic Calendar Display
```
==================================================
                January 2024
==================================================
Mon Tue Wed Thu Fri Sat Sun
------------------------
 1   2   3   4   5   6   7
 8   9  10  11  12  13  14
15  16  17  18  19  20  21
22  23  24  25  26  27  28
29  30  31

Legend:
[XX] = Today
*XX* = Day with events
 XX  = Regular day
```

### Menu Options
```
Options:
1. Previous month (p)
2. Next month (n)
3. Go to specific month (g)
4. Add event (a)
5. Show week numbers (w)
6. Go to today (t)
7. Quit (q)
```

### Adding Events
```
Add Event
--------------------
Enter year: 2024
Enter month (1-12): 1
Enter day: 15
Enter event description: Doctor Appointment
Event added successfully for 1/15/2024
```

### Week Numbers Display
```
Week numbers for January 2024:
-------------------------
Week  1: 1, 2, 3, 4, 5, 6, 7
Week  2: 8, 9, 10, 11, 12, 13, 14
Week  3: 15, 16, 17, 18, 19, 20, 21
Week  4: 22, 23, 24, 25, 26, 27, 28
Week  5: 29, 30, 31
```

## File Structure

```
23-calendar-viewer/
├── calendar_viewer.py          # Main application
├── test_calendar_viewer.py     # Unit tests
├── calendar_events.json        # Events storage (created automatically)
├── README.md                   # This file
├── CHECKLIST.md                # Feature checklist
└── SPEC.md                     # Project specification
```

## Key Features Explained

### Calendar Display
- Uses Python's built-in `calendar` module for accurate date calculations
- Properly handles months with different numbers of days
- Clear visual formatting with consistent spacing

### Event Management
- Events are stored in JSON format for easy reading and modification
- Multiple events can be added to the same date
- Events persist between application sessions
- Events are displayed below the calendar for easy reference

### Navigation
- Intuitive keyboard shortcuts for common actions
- Handles year boundaries correctly (December ↔ January)
- "Go to today" feature for quick return to current date
- Input validation prevents crashes on invalid dates

### Error Handling
- Graceful handling of invalid user input
- File I/O errors are caught and reported
- Date validation prevents invalid calendar displays

## Learning Objectives

This project demonstrates:

1. **Object-Oriented Programming**: Class-based design with methods and attributes
2. **File I/O**: Reading and writing JSON files for data persistence
3. **Date/Time Handling**: Working with Python's datetime and calendar modules
4. **User Interface Design**: Creating intuitive command-line interfaces
5. **Input Validation**: Ensuring robust handling of user input
6. **Error Handling**: Graceful management of edge cases and errors
7. **Testing**: Writing unit tests to verify functionality

## Technical Implementation

### Core Classes
- `CalendarViewer`: Main application class handling all functionality

### Key Methods
- `display_calendar()`: Renders the monthly calendar view
- `navigate_month()`: Handles month navigation logic
- `add_event()`: Manages event creation and storage
- `load_events()` / `save_events()`: Handle data persistence
- `main_menu()`: Interactive user interface loop

### Data Storage
- Events stored in JSON format: `{"YYYY-MM-DD": ["event1", "event2"]}`
- Automatic file creation and error handling
- Human-readable format for easy debugging

## Testing

The project includes comprehensive unit tests covering:

1. **Date Key Generation**: Verifies correct date formatting
2. **Event Management**: Tests adding, retrieving, and managing events
3. **Month Navigation**: Validates navigation logic including year boundaries
4. **Data Persistence**: Ensures events are saved and loaded correctly
5. **Error Handling**: Tests invalid date handling

Run tests with: `python test_calendar_viewer.py`

## Common Use Cases

- **Personal Scheduling**: Track appointments, meetings, and important dates
- **Event Planning**: Organize events and deadlines
- **Date Reference**: Quick lookup of dates and week numbers
- **Learning Tool**: Study Python programming concepts

## Future Enhancements

Potential improvements for advanced users:

- Color output using `colorama` library
- Recurring event support
- Event categories and priorities
- Export to other calendar formats (ICS, CSV)
- Command-line arguments for non-interactive use
- Integration with external calendar services

## Troubleshooting

### Common Issues

1. **Permission Errors**: Ensure write permissions in the project directory
2. **Invalid Date Input**: Use valid month (1-12) and day ranges
3. **File Corruption**: Delete `calendar_events.json` to reset events

### Getting Help

- Check that Python 3.7+ is installed: `python --version`
- Verify file permissions in the project directory
- Review error messages for specific guidance

## Contributing

This is a learning project, but suggestions for improvements are welcome:

1. Fork the project
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is part of a Python learning curriculum and is available for educational use.

---

**Happy Coding!** [SPIRAL CALENDAR]

This calendar viewer demonstrates fundamental Python concepts while providing a useful, functional application. Perfect for beginners learning Python programming!

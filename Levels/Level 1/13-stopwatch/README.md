# Stopwatch Application

A command-line stopwatch program with start/stop functionality, lap times, and elapsed time display. Perfect for timing activities, workouts, experiments, or any situation where precise timing is needed.

## Features

### Core Features
- **Start/Stop Control**: Start, stop, and resume timing with precision
- **Elapsed Time Display**: Shows current time in multiple formats
- **Lap Recording**: Record unlimited lap times with duration tracking
- **Reset Functionality**: Clear all times and start fresh
- **Interactive Menu**: User-friendly command-line interface

### Advanced Features
- **Multiple Time Formats**: Standard, digital, and compact display options
- **Lap Statistics**: Fastest, slowest, and average lap times
- **Save to File**: Export lap times to text file for analysis
- **Resume Capability**: Stop and resume without losing progress
- **Real-time Status**: Live display of current stopwatch state

## Installation

No installation required! This program uses only Python's standard library.

### Requirements
- Python 3.7 or higher

## Usage

### Running the Program
```bash
python stopwatch.py
```

### Interactive Menu
Once running, you'll see a menu with these options:

1. **Start/Resume** - Begin or continue timing
2. **Stop** - Pause the current timing session
3. **Lap** - Record a lap time
4. **Reset** - Clear all times and start over
5. **View Lap Times** - See all recorded laps with statistics
6. **Save Lap Times** - Export laps to a text file
7. **Exit** - Quit the program

### Example Session
```
$ python stopwatch.py
Welcome to the Stopwatch Application!
Time your activities with precision timing.

==================================================
[STOPWATCH]  STOPWATCH [STOPWATCH]
==================================================
Status: RESET [STOP]  00:00.00
Laps recorded: 0
--------------------------------------------------
1. Start/Resume
2. Stop
3. Lap
4. Reset
5. View Lap Times
6. Save Lap Times
7. Exit
==================================================

Enter your choice (1-7): 1

▶  Stopwatch started!

Press Enter to continue...

==================================================
[STOPWATCH]  STOPWATCH [STOPWATCH]
==================================================
Status: RUNNING [STOPWATCH]  00:05.23
Laps recorded: 0
--------------------------------------------------
1. Start/Resume
2. Stop
3. Lap
4. Reset
5. View Lap Times
6. Save Lap Times
7. Exit
==================================================

Enter your choice (1-7): 3

[CHECKERED FLAG] Lap 1: 05.23 (Total: 05.23)

Press Enter to continue...
```

## Time Formats

The stopwatch supports multiple display formats:

### Standard Format
- `45.50` - Seconds only
- `02:05.75` - Minutes:seconds.milliseconds
- `01:01:01.25` - Hours:minutes:seconds.milliseconds

### Digital Format
- `02:05.75` - Minutes:seconds.milliseconds
- `01:01:01.25` - Hours:minutes:seconds.milliseconds

### Compact Format
- `45.50s` - Seconds only
- `2m 5.8s` - Minutes and seconds
- `1h 1m 1s` - Hours, minutes, and seconds

## Lap Times

### Recording Laps
- Press `3` or select "Lap" from the menu while timing
- Each lap records:
  - Lap number
  - Lap duration (time since last lap)
  - Total elapsed time
  - Timestamp

### Lap Statistics
When viewing lap times, you'll see:
- Individual lap times and total times
- Fastest lap with lap number
- Slowest lap with lap number
- Average lap time across all laps

### Saving Lap Times
Export lap times to a text file with:
- Session summary (date, total time, lap count)
- Detailed lap table
- Individual lap durations
- Human-readable format

## Testing

Run the unit tests to verify functionality:

```bash
python -m pytest test_stopwatch.py -v
```

Or run with unittest:

```bash
python -m unittest test_stopwatch.py
```

### Test Coverage
- Stopwatch start/stop functionality
- Elapsed time calculation
- Lap recording and management
- Time formatting in multiple formats
- File saving operations
- Error handling and edge cases
- Integration workflows

## Project Structure

```
13-stopwatch/
├── stopwatch.py              # Main program
├── test_stopwatch.py         # Unit tests
├── README.md                 # This file
├── CHECKLIST.md              # Feature checklist
└── SPEC.md                   # Project specification
```

## Code Structure

### Main Classes

#### `Stopwatch`
The core timing class that handles all stopwatch functionality:

- `start()` - Start or resume timing
- `stop()` - Pause timing
- `reset()` - Clear all data
- `record_lap()` - Record a lap time
- `get_elapsed_time()` - Get current elapsed time
- `format_time()` - Format time in various styles
- `get_status()` - Get current stopwatch state
- `save_lap_times()` - Export laps to file

#### `StopwatchDisplay`
Handles user interaction and menu display:

- `display_menu()` - Show interactive menu
- `handle_*()` methods - Process user choices
- `run()` - Main application loop

### Key Functions

- `main()` - Entry point for the application
- Time formatting utilities
- File I/O operations
- Thread management for live display

## Use Cases

### Sports and Fitness
- Track lap times while running
- Time workout intervals
- Monitor rest periods

### Productivity
- Time work sessions (Pomodoro technique)
- Track task completion times
- Measure meeting durations

### Education and Science
- Time experiments
- Measure reaction times
- Track study sessions

### Gaming
- Speedrun timing
- Challenge timing
- Competition tracking

## Keyboard Shortcuts

The application uses a menu-driven interface:
- Number keys (1-7) for menu selection
- Enter to confirm selections
- Ctrl+C to exit at any time

## Error Handling

The program gracefully handles:
- Invalid menu choices
- File save errors
- Edge cases (no laps to save, etc.)
- Keyboard interrupts

## Performance

- Precision timing using `time.time()`
- Minimal CPU usage during timing
- Efficient lap time storage
- Thread-safe operations

## Learning Objectives

This project demonstrates:
- **Time handling** with Python's time module
- **Threading** for concurrent operations
- **File I/O** for data persistence
- **State management** in applications
- **User interface design** for CLI applications
- **Data formatting** and display
- **Error handling** and validation
- **Unit testing** with mocking

## Extension Ideas

After mastering the basics, consider adding:
- GUI interface with tkinter or pygame
- Sound notifications for lap times
- Countdown timer functionality
- Multiple stopwatch support
- Data visualization of lap times
- Integration with system notifications
- Export to CSV/JSON formats
- Voice control capabilities

## Troubleshooting

### Common Issues

**"Stopwatch is not running" error**
- Make sure to start the stopwatch before recording laps
- Use option 1 to start timing

**File save fails**
- Check write permissions in current directory
- Ensure you have recorded lap times before saving

**Timing seems inaccurate**
- The stopwatch uses system time, which is generally accurate
- For very precise timing, consider specialized hardware

### Performance Tips

- The stopwatch is designed for accuracy over long periods
- For sub-millisecond precision, specialized timing libraries may be needed
- Large numbers of laps (>10,000) may impact performance

## Contributing

This is a learning project. Feel free to:
- Add new time formats
- Improve the user interface
- Enhance error messages
- Add more test cases
- Optimize performance

## License

This project is open source and available for educational purposes.

---

**[STOPWATCH] Happy Timing! [STOPWATCH]**

# Countdown Pomodoro Timer

A command-line Pomodoro timer application that helps users manage work and break periods with configurable durations, session logging, and productivity statistics.

## Features

### Core Features
- **Work Period Timer**: Default 25-minute focused work sessions
- **Break Period Timer**: Default 5-minute break sessions
- **Cycle Counter**: Track completed work/break cycles
- **Period Notifications**: System notifications when periods end

### Bonus Features
- **Configurable Durations**: Customize work and break period lengths
- **Session Logging**: Save session data to JSON file for tracking
- **Productivity Statistics**: View daily, weekly, and overall statistics
- **Session History**: Track completed and interrupted sessions
- **Cross-Platform Notifications**: System notifications on Windows, macOS, and Linux
- **Interactive Menu**: User-friendly interface for all features

## How to Run

```bash
python countdown_pomodoro.py
```

## How to Use

### 1. Main Menu
When you start the app, you'll see the main menu:

```
[TOMATO] POMODORO TIMER MENU
==============================
1. Start Pomodoro session
2. Configure durations
3. View statistics
4. Exit
```

### 2. Starting a Session

1. Select option 1 to start a Pomodoro session
2. Enter the number of cycles (default is 4)
3. Press Enter to begin
4. The timer will display:
   - Time remaining in MM:SS format
   - Current cycle number
   - Total cycles planned
   - Helpful messages for work/break periods

### 3. During a Session

**Work Period:**
- Focus on your task without distractions
- The timer counts down from your work duration
- When time expires, you'll get a notification

**Break Period:**
- Relax, stretch, or get water
- The timer counts down from your break duration
- When time expires, you'll get a notification to return to work

**Controls:**
- **Ctrl+C**: Skip current period and move to next
- **Close terminal**: Exit the application

### 4. Configuring Durations

1. Select option 2 from the main menu
2. Enter work duration in minutes (default: 25)
3. Enter break duration in minutes (default: 5)
4. Press Enter to save settings

### 5. Viewing Statistics

1. Select option 3 from the main menu
2. View comprehensive productivity statistics:
   - Overall performance metrics
   - Today's activity
   - This week's activity
   - Recent session history

## Example Usage Session

```
============================================================
[TOMATO] COUNTDOWN POMODORO TIMER [TOMATO]
============================================================
Welcome to the Pomodoro Timer!
Boost your productivity with focused work sessions and regular breaks.

The Pomodoro Technique:
• Work for 25 minutes, then take a 5-minute break
• After 4 cycles, take a longer break (15-30 minutes)
• Track your progress and build better focus habits
============================================================

[TOMATO] POMODORO TIMER MENU
==============================
1. Start Pomodoro session
2. Configure durations
3. View statistics
4. Exit

Enter your choice (1-4): 1
Enter number of cycles (default 4): 2

[TARGET] Starting Pomodoro Session
[CLIPBOARD] Planned cycles: 2
[STOPWATCH] Work duration: 25:00
[COFFEE] Break duration: 05:00
[CLOCK 1] Total estimated time: 01:00:00

Press Enter to begin...

============================================================
[REFRESH] CYCLE 1 of 2
============================================================

[TOMATO] Starting work period (25:00)
Get ready to focus!

============================================================
[TOMATO] POMODORO TIMER - WORK PERIOD
============================================================
[ALARM] Time Remaining: 24:59
[REFRESH] Current Cycle: 1
[BAR CHART] Total Cycles: 2
[FLEX] Focus on your work!
[NO ENTRY] Avoid distractions

============================================================
Controls:
  Ctrl+C: Skip to next period
  (Close window to exit)
============================================================

... (timer continues) ...

[OK] Work period completed! Great job!

[COFFEE] Starting break period (05:00)
Time to relax!

... (break timer continues) ...

[OK] Break period completed!

[CELEBRATION] Cycle 1 completed!
Press Enter to continue to next cycle...

... (second cycle) ...

============================================================
[CELEBRATION] POMODORO SESSION COMPLETED! [CELEBRATION]
============================================================
[OK] Total cycles completed: 2
[STOPWATCH] Total session time: 01:00:00
[CHECKERED FLAG] Session ended: 2023-12-07 15:30:45
[STAR] Great work today!

[MEMO] Session logged to 'pomodoro_sessions.json'
```

## Statistics Dashboard

The statistics view provides comprehensive productivity insights:

### Overall Performance
- Total sessions completed
- Completion rate percentage
- Total focus time in hours
- Average session length

### Daily Performance
- Sessions completed today
- Focus time today
- Cycles completed today

### Weekly Performance
- Sessions this week
- Focus time this week
- Cycles completed this week

### Recent Sessions
- Last 5 sessions with dates, cycles, and completion status

## Session Logging

All sessions are automatically logged to `pomodoro_sessions.json`:

```json
[
  {
    "date": "2023-12-07",
    "start_time": "2023-12-07T15:30:00.123456",
    "end_time": "2023-12-07T16:30:00.123456",
    "duration_seconds": 3600,
    "cycles_completed": 2,
    "cycles_planned": 2,
    "work_duration": 1500,
    "break_duration": 300,
    "interrupted": false
  }
]
```

### Session Data Fields
- **date**: Session date
- **start_time/end_time**: Session timestamps
- **duration_seconds**: Total session duration
- **cycles_completed/planned**: Actual vs planned cycles
- **work_duration/break_duration**: Timer settings used
- **interrupted**: Whether session was completed fully

## Configuration Options

### Default Settings
- **Work Duration**: 25 minutes
- **Break Duration**: 5 minutes
- **Session Log**: `pomodoro_sessions.json`

### Customizable Settings
- Work duration: 1-999 minutes
- Break duration: 1-999 minutes
- Number of cycles per session: 1-999

### Recommended Pomodoro Variations

**Standard Pomodoro:**
- Work: 25 minutes
- Break: 5 minutes
- Long break: 15-30 minutes (after 4 cycles)

**Extended Focus:**
- Work: 50 minutes
- Break: 10 minutes

**Quick Sprints:**
- Work: 15 minutes
- Break: 3 minutes

**Deep Work:**
- Work: 90 minutes
- Break: 20 minutes

## System Notifications

The app provides system notifications on all platforms:

### Windows
- System sound notification
- Uses Windows API for native notifications

### macOS
- Native macOS notifications via osascript
- System sound alerts

### Linux
- Uses `notify-send` command for notifications
- Requires `libnotify` package on most distributions

## Productivity Tips

### Best Practices
1. **Eliminate Distractions**: Close unnecessary apps and tabs
2. **Plan Your Work**: Know what you'll work on before starting
3. **Take Real Breaks**: Step away from screens during breaks
4. **Stay Consistent**: Try to use the timer regularly
5. **Track Progress**: Review your statistics weekly

### Break Activities
- Stretch or walk around
- Get water or a healthy snack
- Look out the window (eye rest)
- Quick meditation or breathing exercises
- Listen to one song

### Work Strategies
- One task per Pomodoro
- Break large tasks into smaller chunks
- Use breaks to plan next work session
- Track interruptions and minimize them

## Testing

Run the unit tests to verify functionality:

```bash
python -m pytest test_countdown_pomodoro.py -v
```

The test suite includes:
- **25 test methods** covering all timer functionality
- **Time formatting tests** for display functions
- **Session logging tests** for data persistence
- **Statistics calculation tests** for analytics
- **Configuration tests** for settings management
- **Integration tests** for complete workflows

## Code Structure

### Main Classes
- `PomodoroTimer`: Core timer class containing all functionality

### Key Methods
- `start_pomodoro_session()`: Execute complete Pomodoro cycles
- `countdown()`: Run countdown timer with display
- `log_session()`: Save session data to JSON file
- `calculate_statistics()`: Generate productivity metrics
- `set_durations()`: Configure timer settings
- `display_statistics()`: Show analytics dashboard

### Helper Functions
- `format_time()`: Convert seconds to MM:SS format
- `format_time_with_hours()`: Convert seconds to HH:MM:SS format
- `clear_screen()`: Cross-platform screen clearing
- `show_notification()`: Platform-specific notifications

## Error Handling

The app includes comprehensive error handling for:
- **Invalid Input**: Non-numeric duration inputs
- **File Operations**: Permission issues, corrupted log files
- **Timer Interruption**: Graceful handling of user interruptions
- **Platform Compatibility**: Fallbacks for notification systems
- **Session State**: Proper cleanup on unexpected exits

## Requirements

- Python 3.7 or higher
- No external dependencies required
- Cross-platform compatibility (Windows, macOS, Linux)

### Platform-Specific Requirements

**Linux:**
- `libnotify` package for system notifications
- Install with: `sudo apt-get install libnotify-bin` (Ubuntu/Debian)

**Windows:**
- No additional requirements

**macOS:**
- No additional requirements (uses built-in osascript)

## File Structure

```
19-countdown-pomodoro/
├── countdown_pomodoro.py          # Main application
├── test_countdown_pomodoro.py     # Unit tests
├── README.md                      # This file
├── SPEC.md                        # Project specifications
├── CHECKLIST.md                   # Project checklist
└── pomodoro_sessions.json         # Session log (auto-generated)
```

## Advanced Usage

### Keyboard Shortcuts
- **Ctrl+C**: Skip current period
- **Ctrl+Z**: Pause timer (if supported by terminal)
- **Ctrl+D**: Exit application

### Automation Ideas
- Create shell scripts for quick session starts
- Integrate with task management tools
- Set up automatic break reminders
- Export statistics for external analysis

### Data Analysis
Your session data can be analyzed to:
- Identify peak productivity hours
- Track focus time trends
- Measure goal completion rates
- Optimize work/break ratios

## Troubleshooting

### Common Issues

**Notifications not working:**
- Linux: Install `libnotify-bin` package
- macOS: Grant terminal notification permissions
- Windows: Check system sound settings

**Timer display issues:**
- Ensure terminal supports ANSI codes
- Try resizing terminal window
- Check for conflicting terminal themes

**Session log errors:**
- Check file permissions in current directory
- Ensure sufficient disk space
- Verify JSON file isn't corrupted

**Performance issues:**
- Close other applications during sessions
- Check system resource usage
- Restart terminal if needed

## Productivity Science

The Pomodoro Technique is based on research showing that:
- **Focused work sprints** improve concentration
- **Regular breaks** prevent mental fatigue
- **Time boxing** reduces procrastination
- **Frequent rewards** maintain motivation

## Integration Ideas

- **Task Managers**: Connect with Todoist, Trello, or Asana
- **Time Tracking**: Sync with Toggl or Clockify
- **Calendar Apps**: Block time in Google Calendar
- **Health Apps**: Track focus time alongside wellness metrics
- **Automation Tools**: Use with IFTTT or Zapier workflows

Enjoy boosting your productivity with the Pomodoro Timer! [TOMATO]

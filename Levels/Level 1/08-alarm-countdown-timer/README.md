# Alarm & Countdown Timer

A command-line countdown timer with customizable time input and audio/visual alerts.

## What It Does

This program provides a simple countdown timer that:
- Accepts time input in multiple formats (seconds, minutes, MM:SS)
- Displays a live countdown with remaining time
- Plays an alert sound and shows visual notification when complete
- Includes quick preset timers for common durations
- Supports graceful interruption with Ctrl+C

## How to Run

1. Make sure you have Python 3.7 or higher installed
2. Run the program:
   ```bash
   python alarm_countdown_timer.py
   ```
3. Follow the menu prompts to set a timer

## Example Usage

### Custom Timer
```
[ALARM] Alarm & Countdown Timer
========================================
1. Set custom timer
2. Quick timer (presets)
3. Exit
========================================
Enter your choice (1-3): 1

Enter time (e.g., 30s, 5m, 2m30s, 1:30): 2m30s

[STOPWATCH]  Timer started for 02:30
Press Ctrl+C to stop the timer

[ALARM] Time remaining: 02:25
```

### Quick Timer
```
=== Quick Timer ===
1. 1 minute
2. 5 minutes
3. 10 minutes
4. 25 minutes (Pomodoro)
5. Custom time
6. Back to main menu

Select option (1-6): 4
```

## Time Input Formats

The timer accepts multiple time input formats:

- **Seconds only**: `30`, `30s`
- **Minutes only**: `5m`, `10m`
- **Combined**: `2m30s`, `1m45s`
- **MM:SS format**: `1:30`, `5:00`, `0:45`

## Features

- **Flexible Input**: Multiple time format support with validation
- **Live Countdown**: Real-time display of remaining time
- **Audio Alerts**: System sound notifications on completion
- **Visual Alerts**: Clear completion message
- **Quick Presets**: Common timer durations (1m, 5m, 10m, 25m)
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Graceful Exit**: Clean interruption with Ctrl+C

## Testing

Run the unit tests:
```bash
python -m pytest test_alarm_countdown_timer.py -v
```

Or run with unittest:
```bash
python test_alarm_countdown_timer.py
```

## Platform-Specific Features

### Windows
- Uses `winsound.Beep()` for audio alerts
- System beep fallback

### macOS
- Uses `afplay` with system sounds
- Falls back to text alert if sound unavailable

### Linux
- Uses `paplay` for audio alerts
- Falls back to text alert if sound unavailable

## Examples

### Time Input Examples
```bash
30s      # 30 seconds
5m       # 5 minutes (300 seconds)
2m30s    # 2 minutes 30 seconds (150 seconds)
1:30     # 1 minute 30 seconds (90 seconds)
45       # 45 seconds
```

### Quick Timer Presets
1. **1 minute** - Quick breaks
2. **5 minutes** - Short breaks
3. **10 minutes** - Medium breaks
4. **25 minutes** - Pomodoro technique

## Keyboard Controls

- **Ctrl+C**: Stop the timer and return to menu
- **Ctrl+D**: Exit the program

## Error Handling

The program handles various error conditions gracefully:
- Invalid time formats with helpful error messages
- Negative or zero time values
- Missing audio files (falls back to visual alerts)
- Keyboard interrupts during countdown

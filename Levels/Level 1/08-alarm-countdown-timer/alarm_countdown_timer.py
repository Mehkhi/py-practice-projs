#!/usr/bin/env python3

import time
import sys
import os
import platform


def parse_time_input(time_input):
    """Parse time input in various formats and return total seconds."""
    time_input = time_input.strip().lower()

    try:
        # Try to parse as just seconds (number)
        if time_input.isdigit():
            return int(time_input)

        # Parse format like "5m", "30s", "1m30s"
        total_seconds = 0

        # Handle minutes and seconds
        if 'm' in time_input:
            parts = time_input.split('m')
            if parts[0]:
                total_seconds += int(parts[0]) * 60
            if len(parts) > 1 and parts[1]:
                remaining = parts[1].replace('s', '')
                if remaining:
                    total_seconds += int(remaining)
        elif 's' in time_input:
            # Just seconds
            total_seconds = int(time_input.replace('s', ''))
        else:
            # Try to parse as MM:SS format
            if ':' in time_input:
                parts = time_input.split(':')
                if len(parts) == 2:
                    minutes = int(parts[0])
                    seconds = int(parts[1])
                    total_seconds = minutes * 60 + seconds
            else:
                # Try as plain number
                total_seconds = int(time_input)

        return total_seconds

    except (ValueError, IndexError):
        return None


def format_time(seconds):
    """Format seconds as MM:SS."""
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes:02d}:{seconds:02d}"


def play_alert():
    """Play an alert sound when timer completes."""
    print("\a")  # Bell character

    # Try platform-specific alerts
    system = platform.system()

    if system == "Windows":
        import winsound
        try:
            winsound.Beep(1000, 1000)  # Frequency: 1000Hz, Duration: 1000ms
        except (RuntimeError, OSError):
            pass
    elif system == "Darwin":  # macOS
        os.system('afplay /System/Library/Sounds/Glass.aiff 2>/dev/null || echo "Alert!"')
    elif system == "Linux":
        os.system('paplay /usr/share/sounds/alsa/Front_Left.wav 2>/dev/null || echo "Alert!"')

    # Visual alert
    print("\n" + "="*50)
    print("[ALARM] TIMER COMPLETED! [ALARM]")
    print("="*50)


def countdown_timer(seconds):
    """Run a countdown timer for the specified number of seconds."""
    if seconds <= 0:
        print("Please enter a positive time value.")
        return

    print(f"\n[STOPWATCH]  Timer started for {format_time(seconds)}")
    print("Press Ctrl+C to stop the timer\n")

    try:
        start_time = time.time()
        end_time = start_time + seconds

        while time.time() < end_time:
            remaining = int(end_time - time.time())

            # Clear the line and show remaining time
            sys.stdout.write(f"\r[ALARM] Time remaining: {format_time(remaining)}")
            sys.stdout.flush()

            time.sleep(1)

        # Timer completed
        sys.stdout.write("\r" + " " * 30 + "\r")  # Clear the line
        play_alert()

    except KeyboardInterrupt:
        print("\n\n[STOP]  Timer stopped by user")
    except Exception as e:
        print(f"\n\n[X] Error: {e}")


def get_time_input():
    """Get and validate time input from user."""
    while True:
        try:
            user_input = input("\nEnter time (e.g., 30s, 5m, 2m30s, 1:30): ").strip()
            if not user_input:
                print("Please enter a time value.")
                continue

            seconds = parse_time_input(user_input)
            if seconds is None:
                print("Invalid time format. Try: 30s, 5m, 2m30s, or 1:30")
                continue
            elif seconds <= 0:
                print("Please enter a positive time value.")
                continue

            return seconds

        except KeyboardInterrupt:
            print("\nGoodbye!")
            exit()
        except EOFError:
            print("\nGoodbye!")
            exit()


def quick_timer():
    """Quick timer with common presets."""
    print("\n=== Quick Timer ===")
    print("1. 1 minute")
    print("2. 5 minutes")
    print("3. 10 minutes")
    print("4. 25 minutes (Pomodoro)")
    print("5. Custom time")
    print("6. Back to main menu")

    while True:
        try:
            choice = input("\nSelect option (1-6): ").strip()

            if choice == '1':
                return 60
            elif choice == '2':
                return 300
            elif choice == '3':
                return 600
            elif choice == '4':
                return 1500
            elif choice == '5':
                return get_time_input()
            elif choice == '6':
                return None
            else:
                print("Invalid choice. Please enter 1-6.")

        except KeyboardInterrupt:
            print("\nGoodbye!")
            exit()
        except EOFError:
            print("\nGoodbye!")
            exit()


def display_menu():
    """Display the main menu."""
    print("\n" + "="*40)
    print("[ALARM] Alarm & Countdown Timer")
    print("="*40)
    print("1. Set custom timer")
    print("2. Quick timer (presets)")
    print("3. Exit")
    print("="*40)


def main():
    """Main function to run the alarm and countdown timer."""
    print("Welcome to the Alarm & Countdown Timer!")

    while True:
        display_menu()

        try:
            choice = input("Enter your choice (1-3): ").strip()

            if choice == '1':
                seconds = get_time_input()
                countdown_timer(seconds)
            elif choice == '2':
                seconds = quick_timer()
                if seconds is not None:
                    countdown_timer(seconds)
            elif choice == '3':
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please enter 1, 2, or 3.")

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except EOFError:
            print("\nGoodbye!")
            break


if __name__ == "__main__":
    main()

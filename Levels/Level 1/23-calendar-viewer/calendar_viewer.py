#!/usr/bin/env python3
"""
Calendar Viewer - A simple command-line calendar application

This program displays a monthly calendar with the ability to navigate between months,
highlight today's date, and manage events.
"""

import calendar
import json
import os
from datetime import datetime, date
from typing import Dict, List, Optional


class CalendarViewer:
    """A simple calendar viewer with event management capabilities."""

    def __init__(self):
        """Initialize the calendar viewer."""
        self.current_date = datetime.now()
        self.events_file = "calendar_events.json"
        self.events = self.load_events()

    def load_events(self) -> Dict[str, List[str]]:
        """Load events from JSON file."""
        try:
            if os.path.exists(self.events_file):
                with open(self.events_file, 'r') as f:
                    return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
        return {}

    def save_events(self) -> None:
        """Save events to JSON file."""
        try:
            with open(self.events_file, 'w') as f:
                json.dump(self.events, f, indent=2)
        except IOError:
            print("Error: Could not save events to file.")

    def get_date_key(self, year: int, month: int, day: int) -> str:
        """Get a standardized date key for events."""
        return f"{year}-{month:02d}-{day:02d}"

    def add_event(self, year: int, month: int, day: int, event: str) -> None:
        """Add an event to a specific date."""
        date_key = self.get_date_key(year, month, day)
        if date_key not in self.events:
            self.events[date_key] = []
        self.events[date_key].append(event)
        self.save_events()

    def get_events(self, year: int, month: int, day: int) -> List[str]:
        """Get events for a specific date."""
        date_key = self.get_date_key(year, month, day)
        return self.events.get(date_key, [])

    def display_calendar(self, year: Optional[int] = None, month: Optional[int] = None) -> None:
        """Display the calendar for the specified month and year."""
        if year is None:
            year = self.current_date.year
        if month is None:
            month = self.current_date.month

        # Get today's date
        today = datetime.now()

        # Create calendar object
        cal = calendar.Calendar()

        # Get month calendar data
        month_calendar = cal.monthdayscalendar(year, month)

        # Get month name and year
        month_name = calendar.month_name[month]

        # Display header
        print(f"\n{'=' * 50}")
        print(f"{month_name} {year}".center(50))
        print(f"{'=' * 50}")

        # Display day headers
        day_headers = "Mon Tue Wed Thu Fri Sat Sun"
        print(day_headers)
        print("-" * len(day_headers))

        # Display calendar days
        for week in month_calendar:
            week_line = ""
            for day_num in week:
                if day_num == 0:
                    week_line += "    "  # Empty space for days not in this month
                else:
                    # Check if this is today
                    is_today = (year == today.year and
                              month == today.month and
                              day_num == today.day)

                    # Check if there are events on this day
                    events = self.get_events(year, month, day_num)
                    has_events = len(events) > 0

                    # Format the day
                    if is_today:
                        day_str = f"[{day_num:2d}]"  # Highlight today
                    elif has_events:
                        day_str = f"*{day_num:2d}*"  # Mark days with events
                    else:
                        day_str = f" {day_num:2d} "

                    week_line += day_str
            print(week_line)

        # Display legend
        print("\nLegend:")
        print("[XX] = Today")
        print("*XX* = Day with events")
        print(" XX  = Regular day")

        # Display events for the current month
        self.display_month_events(year, month)

    def display_month_events(self, year: int, month: int) -> None:
        """Display all events for the specified month."""
        month_events = []
        for day in range(1, calendar.monthrange(year, month)[1] + 1):
            events = self.get_events(year, month, day)
            if events:
                month_events.append((day, events))

        if month_events:
            print(f"\nEvents in {calendar.month_name[month]} {year}:")
            print("-" * 30)
            for day, events in month_events:
                print(f"{day:2d}: {', '.join(events)}")
        else:
            print(f"\nNo events scheduled for {calendar.month_name[month]} {year}.")

    def navigate_month(self, direction: str) -> None:
        """Navigate to previous or next month."""
        if direction == "prev":
            if self.current_date.month == 1:
                self.current_date = self.current_date.replace(year=self.current_date.year - 1, month=12)
            else:
                self.current_date = self.current_date.replace(month=self.current_date.month - 1)
        elif direction == "next":
            if self.current_date.month == 12:
                self.current_date = self.current_date.replace(year=self.current_date.year + 1, month=1)
            else:
                self.current_date = self.current_date.replace(month=self.current_date.month + 1)

    def show_week_numbers(self, year: int, month: int) -> None:
        """Display week numbers for the month."""
        cal = calendar.Calendar()
        month_calendar = cal.monthdayscalendar(year, month)

        print(f"\nWeek numbers for {calendar.month_name[month]} {year}:")
        print("-" * 25)

        for i, week in enumerate(month_calendar, 1):
            week_days = [str(day) for day in week if day != 0]
            if week_days:
                print(f"Week {i:2d}: {', '.join(week_days)}")

    def add_event_interactive(self) -> None:
        """Interactive event addition."""
        try:
            print("\nAdd Event")
            print("-" * 20)

            year = int(input("Enter year: "))
            month = int(input("Enter month (1-12): "))
            day = int(input("Enter day: "))
            event = input("Enter event description: ")

            # Validate date
            try:
                event_date = date(year, month, day)
                self.add_event(year, month, day, event)
                print(f"Event added successfully for {event_date:%Y-%m-%d}")
            except ValueError:
                print("Error: Invalid date entered.")

        except ValueError:
            print("Error: Please enter valid numbers.")

    def main_menu(self) -> None:
        """Display the main menu and handle user input."""
        while True:
            print("\n" + "=" * 50)
            print("CALENDAR VIEWER".center(50))
            print("=" * 50)

            self.display_calendar()

            print("\nOptions:")
            print("1. Previous month (p)")
            print("2. Next month (n)")
            print("3. Go to specific month (g)")
            print("4. Add event (a)")
            print("5. Show week numbers (w)")
            print("6. Go to today (t)")
            print("7. Quit (q)")

            choice = input("\nEnter your choice: ").lower().strip()

            if choice in ['p', 'prev', 'previous']:
                self.navigate_month("prev")
            elif choice in ['n', 'next']:
                self.navigate_month("next")
            elif choice in ['g', 'go']:
                self.go_to_month()
            elif choice in ['a', 'add']:
                self.add_event_interactive()
            elif choice in ['w', 'week']:
                self.show_week_numbers(self.current_date.year, self.current_date.month)
                input("\nPress Enter to continue...")
            elif choice in ['t', 'today']:
                self.current_date = datetime.now()
            elif choice in ['q', 'quit', 'exit']:
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")

    def go_to_month(self) -> None:
        """Navigate to a specific month and year."""
        try:
            year = int(input("Enter year: "))
            month = int(input("Enter month (1-12): "))

            # Validate month
            if not 1 <= month <= 12:
                print("Error: Month must be between 1 and 12.")
                return

            # Validate year
            if year < 1:
                print("Error: Year must be positive.")
                return

            self.current_date = self.current_date.replace(year=year, month=month)
            print(f"Navigated to {calendar.month_name[month]} {year}")

        except ValueError:
            print("Error: Please enter valid numbers.")


def main():
    """Main function to run the calendar viewer."""
    try:
        calendar_viewer = CalendarViewer()
        calendar_viewer.main_menu()
    except KeyboardInterrupt:
        print("\n\nProgram interrupted. Goodbye!")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()

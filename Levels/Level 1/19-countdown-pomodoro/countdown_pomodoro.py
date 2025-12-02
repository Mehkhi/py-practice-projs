#!/usr/bin/env python3
"""
Countdown Pomodoro Timer

A command-line Pomodoro timer application that helps users manage work and break periods
with configurable durations, session logging, and productivity statistics.
"""

import time
import os
import json
import platform
from datetime import datetime, timedelta
from typing import Dict, List


class PomodoroTimer:
    """Main class for the Pomodoro timer application."""

    def __init__(self):
        self.work_duration = 25 * 60  # 25 minutes in seconds
        self.break_duration = 5 * 60  # 5 minutes in seconds
        self.current_cycle = 0
        self.total_cycles = 0
        self.session_start_time = None
        self.session_log_file = "pomodoro_sessions.json"
        self.is_running = False
        self.is_paused = False
        self.paused_time = 0
        self.pause_start_time = None

    def format_time(self, seconds: int) -> str:
        """
        Format seconds into MM:SS format.

        Args:
            seconds: Number of seconds to format

        Returns:
            Formatted time string
        """
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"

    def format_time_with_hours(self, seconds: int) -> str:
        """
        Format seconds into HH:MM:SS format for longer durations.

        Args:
            seconds: Number of seconds to format

        Returns:
            Formatted time string with hours
        """
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"

    def clear_screen(self):
        """Clear the terminal screen."""
        if platform.system() == "Windows":
            os.system("cls")
        else:
            os.system("clear")

    def show_notification(self, title: str, message: str):
        """
        Show a system notification (platform-dependent).

        Args:
            title: Notification title
            message: Notification message
        """
        try:
            if platform.system() == "Windows":
                import winsound

                winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
            elif platform.system() == "Darwin":  # macOS
                os.system(
                    f'osascript -e \'display notification "{message}" with title "{title}"\''
                )
            else:  # Linux
                os.system(f'notify-send "{title}" "{message}"')
        except Exception:
            # Fallback to simple bell sound
            print("\a")

    def countdown(self, duration: int, period_type: str) -> bool:
        """
        Run a countdown timer for the specified duration.

        Args:
            duration: Duration in seconds
            period_type: Type of period ("work" or "break")

        Returns:
            True if completed normally, False if interrupted
        """
        self.is_running = True
        start_time = time.time()
        end_time = start_time + duration

        while time.time() < end_time and self.is_running:
            if not self.is_paused:
                remaining = int(end_time - time.time())

                self.clear_screen()
                self.display_timer_status(remaining, period_type)

                # Update every second
                time.sleep(1)
            else:
                # Handle pause
                time.sleep(0.1)

        self.is_running = False

        if not self.is_paused and time.time() >= end_time:
            self.show_notification(
                f"Pomodoro {period_type.title()} Complete!",
                f"Time for a {'break' if period_type == 'work' else 'work session'}!",
            )
            return True

        return False

    def display_timer_status(self, remaining: int, period_type: str):
        """Display the current timer status."""
        print("=" * 60)
        print(f"[TOMATO] POMODORO TIMER - {period_type.upper()} PERIOD")
        print("=" * 60)
        print(f"\n[ALARM] Time Remaining: {self.format_time(remaining)}")
        print(f"[REFRESH] Current Cycle: {self.current_cycle}")
        print(f"[BAR CHART] Total Cycles: {self.total_cycles}")

        if period_type == "work":
            print("[FLEX] Focus on your work!")
            print("[NO ENTRY] Avoid distractions")
        else:
            print("[COFFEE] Take a break!")
            print("[MEDITATE] Stretch, relax, recharge")

        print("\n" + "=" * 60)
        print("Controls:")
        print("  Ctrl+C: Skip to next period")
        print("  (Close window to exit)")
        print("=" * 60)

    def run_work_period(self) -> bool:
        """Run a work period."""
        print(f"\n[TOMATO] Starting work period ({self.format_time(self.work_duration)})")
        print("Get ready to focus!")
        time.sleep(2)

        completed = self.countdown(self.work_duration, "work")

        if completed:
            print("\n[OK] Work period completed! Great job!")
            return True
        else:
            print("\n[SKIP] Work period skipped.")
            return False

    def run_break_period(self) -> bool:
        """Run a break period."""
        print(f"\n[COFFEE] Starting break period ({self.format_time(self.break_duration)})")
        print("Time to relax!")
        time.sleep(2)

        completed = self.countdown(self.break_duration, "break")

        if completed:
            print("\n[OK] Break period completed!")
            return True
        else:
            print("\n[SKIP] Break period skipped.")
            return False

    def start_pomodoro_session(self, num_cycles: int = 4):
        """
        Start a complete Pomodoro session.

        Args:
            num_cycles: Number of work/break cycles to complete
        """
        self.session_start_time = datetime.now()
        self.current_cycle = 1
        self.total_cycles = num_cycles

        print("\n[TARGET] Starting Pomodoro Session")
        print(f"[CLIPBOARD] Planned cycles: {num_cycles}")
        print(f"[STOPWATCH] Work duration: {self.format_time(self.work_duration)}")
        print(f"[COFFEE] Break duration: {self.format_time(self.break_duration)}")
        print(
            f"[CLOCK 1] Total estimated time: {self.format_time_with_hours((self.work_duration + self.break_duration) * num_cycles)}"
        )

        input("\nPress Enter to begin...")

        session_completed = True

        try:
            while self.current_cycle <= num_cycles:
                print(f"\n{'='*60}")
                print(f"[REFRESH] CYCLE {self.current_cycle} of {num_cycles}")
                print(f"{'='*60}")

                # Work period
                if not self.run_work_period():
                    print("\nWARNING  Work period skipped. Ending session early.")
                    session_completed = False
                    break

                if self.current_cycle < num_cycles:
                    # Break period (only if not the last cycle)
                    if not self.run_break_period():
                        print("\nWARNING  Break skipped. Moving to next cycle.")

                self.current_cycle += 1

                if self.current_cycle <= num_cycles:
                    print(f"\n[CELEBRATION] Cycle {self.current_cycle - 1} completed!")
                    input("Press Enter to continue to next cycle...")

            session_end_time = datetime.now()
            session_duration = session_end_time - self.session_start_time

            if session_completed:
                # Session completed
                print(f"\n{'='*60}")
                print("[CELEBRATION] POMODORO SESSION COMPLETED! [CELEBRATION]")
                print(f"{'='*60}")
                print(f"[OK] Total cycles completed: {num_cycles}")
                print(
                    f"[STOPWATCH] Total session time: {self.format_time_with_hours(int(session_duration.total_seconds()))}"
                )
                print(f"[CHECKERED FLAG] Session ended: {session_end_time.strftime('%Y-%m-%d %H:%M:%S')}")
                print("[STAR] Great work today!")

                # Log session
                self.log_session(num_cycles, session_duration, session_end_time)
            else:
                completed_cycles = max(0, self.current_cycle - 1)
                print(f"\nWARNING  Session ended early after {completed_cycles} cycle(s).")
                self.log_session(
                    completed_cycles,
                    session_duration,
                    session_end_time,
                    interrupted=True,
                )

        except KeyboardInterrupt:
            print("\n\n[STOP] Session interrupted by user.")
            print(f"[BAR CHART] Cycles completed: {self.current_cycle - 1} of {num_cycles}")

            # Log partial session
            if self.current_cycle > 1:
                session_end_time = datetime.now()
                session_duration = session_end_time - self.session_start_time
                self.log_session(
                    self.current_cycle - 1,
                    session_duration,
                    session_end_time,
                    interrupted=True,
                )

    def log_session(
        self,
        cycles_completed: int,
        duration: timedelta,
        end_time: datetime,
        interrupted: bool = False,
    ):
        """
        Log the session to a JSON file.

        Args:
            cycles_completed: Number of cycles completed
            duration: Session duration
            end_time: Session end time
            interrupted: Whether the session was interrupted
        """
        session_data = {
            "date": end_time.strftime("%Y-%m-%d"),
            "start_time": self.session_start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_seconds": int(duration.total_seconds()),
            "cycles_completed": cycles_completed,
            "cycles_planned": self.total_cycles,
            "work_duration": self.work_duration,
            "break_duration": self.break_duration,
            "interrupted": interrupted,
        }

        try:
            # Load existing sessions
            sessions = []
            if os.path.exists(self.session_log_file):
                with open(self.session_log_file, "r", encoding="utf-8") as file:
                    sessions = json.load(file)

            # Add new session
            sessions.append(session_data)

            # Save back to file
            with open(self.session_log_file, "w", encoding="utf-8") as file:
                json.dump(sessions, file, indent=2, ensure_ascii=False)

            print(f"\n[MEMO] Session logged to '{self.session_log_file}'")

        except Exception as e:
            print(f"\n[X] Error logging session: {e}")

    def load_session_history(self) -> List[Dict]:
        """
        Load session history from log file.

        Returns:
            List of session dictionaries
        """
        try:
            if os.path.exists(self.session_log_file):
                with open(self.session_log_file, "r", encoding="utf-8") as file:
                    return json.load(file)
            return []
        except Exception as e:
            print(f"Error loading session history: {e}")
            return []

    def calculate_statistics(self, sessions: List[Dict]) -> Dict:
        """
        Calculate statistics from session data.

        Args:
            sessions: List of session dictionaries

        Returns:
            Dictionary with calculated statistics
        """
        if not sessions:
            return {}

        total_sessions = len(sessions)
        total_cycles = sum(s["cycles_completed"] for s in sessions)
        total_time = sum(s["duration_seconds"] for s in sessions)
        completed_sessions = sum(1 for s in sessions if not s.get("interrupted", False))

        # Calculate daily and weekly stats
        today = datetime.now().date()
        this_week_start = today - timedelta(days=today.weekday())

        today_sessions = [
            s for s in sessions if datetime.fromisoformat(s["date"]).date() == today
        ]
        week_sessions = [
            s
            for s in sessions
            if datetime.fromisoformat(s["date"]).date() >= this_week_start
        ]

        today_cycles = sum(s["cycles_completed"] for s in today_sessions)
        week_cycles = sum(s["cycles_completed"] for s in week_sessions)
        today_time = sum(s["duration_seconds"] for s in today_sessions)
        week_time = sum(s["duration_seconds"] for s in week_sessions)

        return {
            "total_sessions": total_sessions,
            "completed_sessions": completed_sessions,
            "completion_rate": (
                round((completed_sessions / total_sessions) * 100, 1)
                if total_sessions > 0
                else 0
            ),
            "total_cycles": total_cycles,
            "total_time_hours": round(total_time / 3600, 1),
            "today_sessions": len(today_sessions),
            "today_cycles": today_cycles,
            "today_time_minutes": round(today_time / 60, 1),
            "week_sessions": len(week_sessions),
            "week_cycles": week_cycles,
            "week_time_hours": round(week_time / 3600, 1),
            "average_session_time": (
                round(total_time / total_sessions / 60, 1) if total_sessions > 0 else 0
            ),
        }

    def display_statistics(self):
        """Display productivity statistics."""
        sessions = self.load_session_history()
        stats = self.calculate_statistics(sessions)

        if not stats:
            print("\n[BAR CHART] No session history found.")
            print("Start a Pomodoro session to build your statistics!")
            return

        print("\n" + "=" * 60)
        print("[BAR CHART] POMODORO STATISTICS")
        print("=" * 60)

        print("\n[CHART UP] OVERALL PERFORMANCE:")
        print(f"  Total sessions: {stats['total_sessions']}")
        print(f"  Completed sessions: {stats['completed_sessions']}")
        print(f"  Completion rate: {stats['completion_rate']}%")
        print(f"  Total cycles: {stats['total_cycles']}")
        print(f"  Total focus time: {stats['total_time_hours']} hours")
        print(f"  Average session: {stats['average_session_time']} minutes")

        print("\n[CALENDAR] TODAY'S PERFORMANCE:")
        print(f"  Sessions: {stats['today_sessions']}")
        print(f"  Cycles: {stats['today_cycles']}")
        print(f"  Focus time: {stats['today_time_minutes']} minutes")

        print("\n[CALENDAR] THIS WEEK'S PERFORMANCE:")
        print(f"  Sessions: {stats['week_sessions']}")
        print(f"  Cycles: {stats['week_cycles']}")
        print(f"  Focus time: {stats['week_time_hours']} hours")

        # Recent sessions
        print("\n[CLOCK 1] RECENT SESSIONS:")
        recent_sessions = sorted(sessions, key=lambda x: x["end_time"], reverse=True)[
            :5
        ]
        for i, session in enumerate(recent_sessions, 1):
            date = datetime.fromisoformat(session["date"]).strftime("%m/%d")
            cycles = session["cycles_completed"]
            time_min = round(session["duration_seconds"] / 60, 1)
            status = "[OK]" if not session.get("interrupted", False) else "[STOP]"
            print(f"  {i}. {date} - {cycles} cycles, {time_min} min {status}")

    def set_durations(self):
        """Allow user to configure work and break durations."""
        print("\n[GEAR] CONFIGURE DURATIONS")
        print("=" * 40)

        # Set work duration
        while True:
            try:
                work_input = input(
                    f"Work duration in minutes (current: {self.work_duration // 60}): "
                ).strip()
                if not work_input:
                    break

                work_minutes = int(work_input)
                if work_minutes < 1:
                    print("Work duration must be at least 1 minute.")
                    continue

                self.work_duration = work_minutes * 60
                print(f"[OK] Work duration set to {work_minutes} minutes")
                break

            except ValueError:
                print("Please enter a valid number.")

        # Set break duration
        while True:
            try:
                break_input = input(
                    f"Break duration in minutes (current: {self.break_duration // 60}): "
                ).strip()
                if not break_input:
                    break

                break_minutes = int(break_input)
                if break_minutes < 1:
                    print("Break duration must be at least 1 minute.")
                    continue

                self.break_duration = break_minutes * 60
                print(f"[OK] Break duration set to {break_minutes} minutes")
                break

            except ValueError:
                print("Please enter a valid number.")

        print("\n[STOPWATCH] New settings:")
        print(f"  Work: {self.format_time(self.work_duration)}")
        print(f"  Break: {self.format_time(self.break_duration)}")

    def get_menu_choice(self) -> str:
        """Get user's menu choice."""
        print("\n[TOMATO] POMODORO TIMER MENU")
        print("=" * 30)
        print("1. Start Pomodoro session")
        print("2. Configure durations")
        print("3. View statistics")
        print("4. Exit")

        while True:
            choice = input("\nEnter your choice (1-4): ").strip()
            if choice in ["1", "2", "3", "4"]:
                return choice
            print("Please enter a number between 1 and 4.")


def display_welcome():
    """Display welcome message and instructions."""
    print("\n" + "=" * 60)
    print("[TOMATO] COUNTDOWN POMODORO TIMER [TOMATO]")
    print("=" * 60)
    print("Welcome to the Pomodoro Timer!")
    print("Boost your productivity with focused work sessions and regular breaks.")
    print("\nThe Pomodoro Technique:")
    print("• Work for 25 minutes, then take a 5-minute break")
    print("• After 4 cycles, take a longer break (15-30 minutes)")
    print("• Track your progress and build better focus habits")
    print("=" * 60)


def main():
    """Main program loop."""
    timer = PomodoroTimer()

    display_welcome()

    while True:
        choice = timer.get_menu_choice()

        if choice == "1":
            # Start Pomodoro session
            while True:
                try:
                    cycles = input("Enter number of cycles (default 4): ").strip()
                    if not cycles:
                        cycles = 4
                    else:
                        cycles = int(cycles)

                    if cycles < 1:
                        print("Please enter at least 1 cycle.")
                        continue

                    timer.start_pomodoro_session(cycles)
                    break

                except ValueError:
                    print("Please enter a valid number.")

        elif choice == "2":
            # Configure durations
            timer.set_durations()

        elif choice == "3":
            # View statistics
            timer.display_statistics()

        elif choice == "4":
            # Exit
            print("\nThanks for using the Pomodoro Timer!")
            print("[TOMATO] Stay productive! [TOMATO]")
            break


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Stopwatch Application

A command-line stopwatch program with start/stop functionality, lap times,
and elapsed time display. Perfect for timing activities, workouts, or experiments.
"""

import time
import threading
from typing import List, Dict, Optional
from datetime import datetime


class Stopwatch:
    """Main stopwatch class with timing and lap functionality."""

    def __init__(self):
        self.start_time: Optional[float] = None
        self.stop_time: Optional[float] = None
        self.elapsed_time: float = 0.0
        self.is_running: bool = False
        self.lap_times: List[Dict] = []
        self.lap_counter: int = 0

    def start(self) -> bool:
        """
        Start the stopwatch.

        Returns:
            True if successfully started, False if already running
        """
        if self.is_running:
            return False

        if self.stop_time is not None:
            # Resume from where we left off
            self.start_time = time.time() - (self.stop_time - self.start_time)
        else:
            # Fresh start
            self.start_time = time.time()

        self.is_running = True
        return True

    def stop(self) -> bool:
        """
        Stop the stopwatch.

        Returns:
            True if successfully stopped, False if not running
        """
        if not self.is_running:
            return False

        self.stop_time = time.time()
        self.elapsed_time = self.stop_time - self.start_time
        self.is_running = False
        return True

    def reset(self) -> None:
        """Reset the stopwatch to initial state."""
        self.start_time = None
        self.stop_time = None
        self.elapsed_time = 0.0
        self.is_running = False
        self.lap_times.clear()
        self.lap_counter = 0

    def get_elapsed_time(self) -> float:
        """
        Get the current elapsed time.

        Returns:
            Elapsed time in seconds
        """
        if self.is_running:
            return time.time() - self.start_time
        elif self.stop_time is not None:
            return self.elapsed_time
        else:
            return 0.0

    def format_time(self, seconds: float, format_type: str = "standard") -> str:
        """
        Format time in various formats.

        Args:
            seconds: Time in seconds
            format_type: "standard", "digital", or "compact"

        Returns:
            Formatted time string
        """
        if format_type == "standard":
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = seconds % 60

            if hours > 0:
                return f"{hours:02d}:{minutes:02d}:{secs:05.2f}"
            else:
                return f"{minutes:02d}:{secs:05.2f}"

        elif format_type == "digital":
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = int(seconds % 60)
            milliseconds = int((seconds % 1) * 100)

            if hours > 0:
                return f"{hours:02d}:{minutes:02d}:{secs:02d}.{milliseconds:02d}"
            else:
                return f"{minutes:02d}:{secs:02d}.{milliseconds:02d}"

        elif format_type == "compact":
            if seconds < 60:
                return f"{seconds:.2f}s"
            elif seconds < 3600:
                minutes = int(seconds // 60)
                secs = seconds % 60
                return f"{minutes}m {secs:.1f}s"
            else:
                hours = int(seconds // 3600)
                minutes = int((seconds % 3600) // 60)
                secs = seconds % 60
                return f"{hours}h {minutes}m {secs:.0f}s"

        else:
            return f"{seconds:.2f}s"

    def record_lap(self) -> Optional[Dict]:
        """
        Record a lap time.

        Returns:
            Lap information dictionary or None if not running
        """
        if not self.is_running:
            return None

        self.lap_counter += 1
        current_time = time.time()
        lap_time = current_time - self.start_time

        # Calculate lap duration (time since last lap)
        if self.lap_times:
            last_lap_time = self.lap_times[-1]["absolute_time"]
            lap_duration = lap_time - last_lap_time
        else:
            lap_duration = lap_time

        lap_info = {
            "lap_number": self.lap_counter,
            "absolute_time": lap_time,
            "lap_duration": lap_duration,
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "formatted_absolute": self.format_time(lap_time),
            "formatted_duration": self.format_time(lap_duration),
        }

        self.lap_times.append(lap_info)
        return lap_info

    def get_lap_times(self) -> List[Dict]:
        """Get all recorded lap times."""
        return self.lap_times.copy()

    def get_status(self) -> Dict:
        """
        Get current stopwatch status.

        Returns:
            Status dictionary with all relevant information
        """
        return {
            "is_running": self.is_running,
            "elapsed_time": self.get_elapsed_time(),
            "formatted_time": self.format_time(self.get_elapsed_time()),
            "lap_count": len(self.lap_times),
            "has_started": self.start_time is not None,
        }

    def save_lap_times(self, filename: str = "lap_times.txt") -> bool:
        """
        Save lap times to a file.

        Args:
            filename: Name of the file to save to

        Returns:
            True if successful, False otherwise
        """
        if not self.lap_times:
            return False

        try:
            with open(filename, "w") as f:
                f.write("Stopwatch Lap Times\n")
                f.write("=" * 50 + "\n")
                f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total Laps: {len(self.lap_times)}\n")
                f.write(f"Total Time: {self.format_time(self.get_elapsed_time())}\n")
                f.write("\n")

                f.write("Lap | Lap Time  | Total Time | Timestamp\n")
                f.write("-" * 45 + "\n")

                for lap in self.lap_times:
                    f.write(
                        f"{lap['lap_number']:3d} | {lap['formatted_duration']:9s} | {lap['formatted_absolute']:10s} | {lap['timestamp']}\n"
                    )

                f.write("\n")
                f.write("Lap Durations:\n")
                for i, lap in enumerate(self.lap_times, 1):
                    f.write(f"Lap {i}: {lap['formatted_duration']}\n")

            return True
        except Exception:
            return False


class StopwatchDisplay:
    """Handles the display and user interaction for the stopwatch."""

    def __init__(self):
        self.stopwatch = Stopwatch()
        self.display_thread: Optional[threading.Thread] = None
        self.should_display: bool = False

    def display_menu(self):
        """Display the main menu options."""
        print("\n" + "=" * 50)
        print("[STOPWATCH]  STOPWATCH [STOPWATCH]")
        print("=" * 50)
        status = self.stopwatch.get_status()

        if status["is_running"]:
            print(f"Status: RUNNING [STOPWATCH]  {status['formatted_time']}")
        elif status["has_started"]:
            print(f"Status: STOPPED [PAUSE]  {status['formatted_time']}")
        else:
            print("Status: RESET [STOP]  00:00.00")

        print(f"Laps recorded: {status['lap_count']}")
        print("-" * 50)
        print("1. Start/Resume")
        print("2. Stop")
        print("3. Lap")
        print("4. Reset")
        print("5. View Lap Times")
        print("6. Save Lap Times")
        print("7. Exit")
        print("=" * 50)

    def get_user_choice(self) -> str:
        """Get and validate user menu choice."""
        while True:
            choice = input("\nEnter your choice (1-7): ").strip()
            if choice in ["1", "2", "3", "4", "5", "6", "7"]:
                return choice
            print("Invalid choice. Please enter 1, 2, 3, 4, 5, 6, or 7.")

    def handle_start_stop(self):
        """Handle start/stop functionality."""
        if self.stopwatch.is_running:
            if self.stopwatch.stop():
                print(
                    f"\n[PAUSE]  Stopwatch stopped at {self.stopwatch.format_time(self.stopwatch.get_elapsed_time())}"
                )
            else:
                print("\n[X] Stopwatch is not running")
        else:
            if self.stopwatch.start():
                print("\n▶  Stopwatch started!")
                self.start_live_display()
            else:
                print("\n[X] Stopwatch is already running")

    def handle_lap(self):
        """Handle lap recording."""
        lap = self.stopwatch.record_lap()
        if lap:
            print(
                f"\n[CHECKERED FLAG] Lap {lap['lap_number']}: {lap['formatted_duration']} (Total: {lap['formatted_absolute']})"
            )
        else:
            print("\n[X] Cannot record lap - stopwatch is not running")

    def handle_reset(self):
        """Handle reset functionality."""
        if self.stopwatch.is_running:
            self.stopwatch.stop()

        self.stopwatch.reset()
        print("\n[REFRESH] Stopwatch reset!")

    def handle_view_laps(self):
        """Handle viewing lap times."""
        laps = self.stopwatch.get_lap_times()

        if not laps:
            print("\n[CLIPBOARD] No lap times recorded yet")
            return

        print(f"\n[CLIPBOARD] LAP TIMES ({len(laps)} laps)")
        print("-" * 60)
        print("Lap | Lap Time  | Total Time | Timestamp")
        print("-" * 60)

        for lap in laps:
            print(
                f"{lap['lap_number']:3d} | {lap['formatted_duration']:9s} | {lap['formatted_absolute']:10s} | {lap['timestamp']}"
            )

        # Show summary
        if len(laps) > 1:
            fastest_lap = min(laps, key=lambda x: x["lap_duration"])
            slowest_lap = max(laps, key=lambda x: x["lap_duration"])
            avg_lap = sum(lap["lap_duration"] for lap in laps) / len(laps)

            print("-" * 60)
            print(
                f"Fastest Lap: {fastest_lap['formatted_duration']} (Lap {fastest_lap['lap_number']})"
            )
            print(
                f"Slowest Lap: {slowest_lap['formatted_duration']} (Lap {slowest_lap['lap_number']})"
            )
            print(f"Average Lap: {self.stopwatch.format_time(avg_lap)}")

    def handle_save_laps(self):
        """Handle saving lap times to file."""
        if self.stopwatch.save_lap_times():
            print("\n[FLOPPY DISK] Lap times saved to 'lap_times.txt'")
        else:
            print("\n[X] No lap times to save or error occurred")

    def start_live_display(self):
        """Start live time display in a separate thread."""
        if self.display_thread and self.display_thread.is_alive():
            return

        self.should_display = True
        self.display_thread = threading.Thread(
            target=self._display_time_loop, daemon=True
        )
        self.display_thread.start()

    def stop_live_display(self):
        """Stop the live time display."""
        self.should_display = False
        if self.display_thread:
            self.display_thread.join(timeout=1)

    def _display_time_loop(self):
        """Display time updates in a loop."""
        while self.should_display and self.stopwatch.is_running:
            # This would normally update a GUI, but for CLI we'll just update
            # the display when user asks for status
            time.sleep(0.1)

    def run(self):
        """Main application loop."""
        print("Welcome to the Stopwatch Application!")
        print("Time your activities with precision timing.")

        try:
            while True:
                self.display_menu()
                choice = self.get_user_choice()

                if choice == "1":
                    self.handle_start_stop()
                elif choice == "2":
                    if self.stopwatch.is_running:
                        self.stopwatch.stop()
                        print(
                            f"\n[PAUSE]  Stopwatch stopped at {self.stopwatch.format_time(self.stopwatch.get_elapsed_time())}"
                        )
                    else:
                        print("\n[X] Stopwatch is not running")
                elif choice == "3":
                    self.handle_lap()
                elif choice == "4":
                    self.handle_reset()
                elif choice == "5":
                    self.handle_view_laps()
                elif choice == "6":
                    self.handle_save_laps()
                elif choice == "7":
                    self.stop_live_display()
                    if self.stopwatch.is_running:
                        self.stopwatch.stop()
                    print("\nThanks for using the Stopwatch!")
                    print("[STOPWATCH]  Happy timing! [STOPWATCH]")
                    break

                # Pause before showing menu again
                if choice != "7":
                    input("\nPress Enter to continue...")

        except KeyboardInterrupt:
            print("\n\n[STOPWATCH]  Stopwatch stopped by user")
            if self.stopwatch.is_running:
                self.stopwatch.stop()
            print("Thanks for using the Stopwatch!")


def main():
    """Main entry point for the stopwatch application."""
    app = StopwatchDisplay()
    app.run()


if __name__ == "__main__":
    main()

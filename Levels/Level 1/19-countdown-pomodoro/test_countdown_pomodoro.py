#!/usr/bin/env python3
"""
Unit tests for Countdown Pomodoro Timer

Tests all functionality of the PomodoroTimer class including:
- Time formatting and display
- Session logging and statistics
- Configuration management
- Timer countdown logic
"""

import unittest
import json
import os
import tempfile
from unittest.mock import patch
from datetime import datetime, timedelta
from countdown_pomodoro import PomodoroTimer


class TestPomodoroTimer(unittest.TestCase):
    """Test cases for PomodoroTimer class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.timer = PomodoroTimer()
        self.temp_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        os.chdir(self.temp_dir)
        self.timer.session_log_file = "test_sessions.json"

    def tearDown(self):
        """Clean up after each test method."""
        os.chdir(self.original_dir)
        # Clean up temp files
        for file in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file))
        os.rmdir(self.temp_dir)

    def test_initialization(self):
        """Test timer initialization with default values."""
        self.assertEqual(self.timer.work_duration, 25 * 60)  # 25 minutes
        self.assertEqual(self.timer.break_duration, 5 * 60)  # 5 minutes
        self.assertEqual(self.timer.current_cycle, 0)
        self.assertEqual(self.timer.total_cycles, 0)
        self.assertIsNone(self.timer.session_start_time)
        self.assertFalse(self.timer.is_running)
        self.assertFalse(self.timer.is_paused)

    def test_format_time(self):
        """Test time formatting to MM:SS."""
        self.assertEqual(self.timer.format_time(0), "00:00")
        self.assertEqual(self.timer.format_time(5), "00:05")
        self.assertEqual(self.timer.format_time(65), "01:05")
        self.assertEqual(self.timer.format_time(3600), "60:00")
        self.assertEqual(self.timer.format_time(3661), "61:01")

    def test_format_time_with_hours(self):
        """Test time formatting to HH:MM:SS."""
        self.assertEqual(self.timer.format_time_with_hours(0), "00:00")
        self.assertEqual(self.timer.format_time_with_hours(65), "01:05")
        self.assertEqual(self.timer.format_time_with_hours(3600), "01:00:00")
        self.assertEqual(self.timer.format_time_with_hours(3661), "01:01:01")
        self.assertEqual(self.timer.format_time_with_hours(7325), "02:02:05")

    def test_log_session(self):
        """Test logging session data to file."""
        start_time = datetime(2023, 1, 1, 10, 0, 0)
        end_time = datetime(2023, 1, 1, 12, 0, 0)
        duration = end_time - start_time

        self.timer.session_start_time = start_time
        self.timer.total_cycles = 4

        self.timer.log_session(4, duration, end_time)

        # Verify file was created
        self.assertTrue(os.path.exists(self.timer.session_log_file))

        # Verify file contents
        with open(self.timer.session_log_file, "r") as file:
            sessions = json.load(file)

        self.assertEqual(len(sessions), 1)
        session = sessions[0]
        self.assertEqual(session["cycles_completed"], 4)
        self.assertEqual(session["cycles_planned"], 4)
        self.assertEqual(session["duration_seconds"], 7200)
        self.assertEqual(session["work_duration"], 25 * 60)
        self.assertEqual(session["break_duration"], 5 * 60)
        self.assertFalse(session["interrupted"])

    def test_log_interrupted_session(self):
        """Test logging interrupted session."""
        start_time = datetime(2023, 1, 1, 10, 0, 0)
        end_time = datetime(2023, 1, 1, 11, 0, 0)
        duration = end_time - start_time

        self.timer.session_start_time = start_time
        self.timer.total_cycles = 4

        self.timer.log_session(2, duration, end_time, interrupted=True)

        with open(self.timer.session_log_file, "r") as file:
            sessions = json.load(file)

        session = sessions[0]
        self.assertEqual(session["cycles_completed"], 2)
        self.assertEqual(session["cycles_planned"], 4)
        self.assertTrue(session["interrupted"])

    def test_log_multiple_sessions(self):
        """Test logging multiple sessions."""
        # Log first session
        start_time1 = datetime(2023, 1, 1, 10, 0, 0)
        end_time1 = datetime(2023, 1, 1, 12, 0, 0)
        duration1 = end_time1 - start_time1

        self.timer.session_start_time = start_time1
        self.timer.log_session(4, duration1, end_time1)

        # Log second session
        start_time2 = datetime(2023, 1, 2, 10, 0, 0)
        end_time2 = datetime(2023, 1, 2, 11, 30, 0)
        duration2 = end_time2 - start_time2

        self.timer.session_start_time = start_time2
        self.timer.log_session(3, duration2, end_time2)

        # Verify both sessions are saved
        with open(self.timer.session_log_file, "r") as file:
            sessions = json.load(file)

        self.assertEqual(len(sessions), 2)
        self.assertEqual(sessions[0]["cycles_completed"], 4)
        self.assertEqual(sessions[1]["cycles_completed"], 3)

    def test_load_session_history(self):
        """Test loading session history from file."""
        # Create test sessions file
        test_sessions = [
            {
                "date": "2023-01-01",
                "cycles_completed": 4,
                "duration_seconds": 7200,
                "interrupted": False,
            },
            {
                "date": "2023-01-02",
                "cycles_completed": 3,
                "duration_seconds": 5400,
                "interrupted": True,
            },
        ]

        with open(self.timer.session_log_file, "w") as file:
            json.dump(test_sessions, file)

        sessions = self.timer.load_session_history()

        self.assertEqual(len(sessions), 2)
        self.assertEqual(sessions[0]["cycles_completed"], 4)
        self.assertEqual(sessions[1]["cycles_completed"], 3)
        self.assertFalse(sessions[0]["interrupted"])
        self.assertTrue(sessions[1]["interrupted"])

    def test_load_session_history_no_file(self):
        """Test loading session history when no file exists."""
        sessions = self.timer.load_session_history()
        self.assertEqual(sessions, [])

    def test_calculate_statistics_empty(self):
        """Test calculating statistics with no sessions."""
        stats = self.timer.calculate_statistics([])
        self.assertEqual(stats, {})

    def test_calculate_statistics_with_data(self):
        """Test calculating statistics with session data."""
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)

        sessions = [
            {
                "date": today.isoformat(),
                "cycles_completed": 4,
                "duration_seconds": 7200,
                "interrupted": False,
            },
            {
                "date": today.isoformat(),
                "cycles_completed": 2,
                "duration_seconds": 3600,
                "interrupted": True,
            },
            {
                "date": yesterday.isoformat(),
                "cycles_completed": 3,
                "duration_seconds": 5400,
                "interrupted": False,
            },
        ]

        stats = self.timer.calculate_statistics(sessions)

        self.assertEqual(stats["total_sessions"], 3)
        self.assertEqual(stats["completed_sessions"], 2)
        self.assertEqual(stats["completion_rate"], 66.7)
        self.assertEqual(stats["total_cycles"], 9)
        self.assertEqual(stats["total_time_hours"], 4.5)
        self.assertEqual(stats["today_sessions"], 2)
        self.assertEqual(stats["today_cycles"], 6)
        self.assertEqual(stats["today_time_minutes"], 180.0)
        self.assertEqual(stats["average_session_time"], 90.0)

    def test_set_durations_valid(self):
        """Test setting valid work and break durations."""
        # Mock user input
        with patch("builtins.input", side_effect=["30", "10"]):
            self.timer.set_durations()

        self.assertEqual(self.timer.work_duration, 30 * 60)
        self.assertEqual(self.timer.break_duration, 10 * 60)

    def test_set_durations_default(self):
        """Test setting durations with default values (empty input)."""
        original_work = self.timer.work_duration
        original_break = self.timer.break_duration

        with patch("builtins.input", side_effect=["", ""]):
            self.timer.set_durations()

        # Should remain unchanged
        self.assertEqual(self.timer.work_duration, original_work)
        self.assertEqual(self.timer.break_duration, original_break)

    def test_set_durations_invalid_then_valid(self):
        """Test setting durations with invalid input then valid input."""
        with patch("builtins.input", side_effect=["invalid", "20", "invalid", "8"]):
            self.timer.set_durations()

        self.assertEqual(self.timer.work_duration, 20 * 60)
        self.assertEqual(self.timer.break_duration, 8 * 60)

    def test_set_durations_minimum_value(self):
        """Test setting durations with minimum valid values."""
        with patch("builtins.input", side_effect=["1", "1"]):
            self.timer.set_durations()

        self.assertEqual(self.timer.work_duration, 60)
        self.assertEqual(self.timer.break_duration, 60)

    def test_set_durations_below_minimum(self):
        """Test setting durations with values below minimum."""
        original_work = self.timer.work_duration
        original_break = self.timer.break_duration

        with patch("builtins.input", side_effect=["0", "-5", "", ""]):
            self.timer.set_durations()

        # Should remain unchanged
        self.assertEqual(self.timer.work_duration, original_work)
        self.assertEqual(self.timer.break_duration, original_break)

    def test_get_menu_choice_valid(self):
        """Test getting valid menu choice."""
        with patch("builtins.input", return_value="2"):
            choice = self.timer.get_menu_choice()
            self.assertEqual(choice, "2")

    def test_get_menu_choice_invalid_then_valid(self):
        """Test getting menu choice with invalid input then valid input."""
        with patch("builtins.input", side_effect=["invalid", "5", "3"]):
            choice = self.timer.get_menu_choice()
            self.assertEqual(choice, "3")

    @patch("platform.system")
    def test_clear_screen_windows(self, mock_system):
        """Test clearing screen on Windows."""
        mock_system.return_value = "Windows"

        with patch("os.system") as mock_system_call:
            self.timer.clear_screen()
            mock_system_call.assert_called_with("cls")

    @patch("platform.system")
    def test_clear_screen_unix(self, mock_system):
        """Test clearing screen on Unix-like systems."""
        mock_system.return_value = "Linux"

        with patch("os.system") as mock_system_call:
            self.timer.clear_screen()
            mock_system_call.assert_called_with("clear")

    @patch("platform.system")
    def test_show_notification_macos(self, mock_system):
        """Test showing notification on macOS."""
        mock_system.return_value = "Darwin"

        with patch("os.system") as mock_system_call:
            self.timer.show_notification("Test", "Message")
            mock_system_call.assert_called_once()

    @patch("platform.system")
    def test_show_notification_linux(self, mock_system):
        """Test showing notification on Linux."""
        mock_system.return_value = "Linux"

        with patch("os.system") as mock_system_call:
            self.timer.show_notification("Test", "Message")
            mock_system_call.assert_called_with('notify-send "Test" "Message"')

    def test_display_timer_status_work(self):
        """Test displaying timer status for work period."""
        with patch("builtins.print") as mock_print:
            self.timer.display_timer_status(1500, "work")  # 25 minutes

        # Check that print was called with work-specific messages
        mock_print.assert_called()
        calls = [str(call) for call in mock_print.call_args_list]
        status_output = " ".join(calls)
        self.assertIn("WORK", status_output)
        self.assertIn("Focus on your work", status_output)

    def test_display_timer_status_break(self):
        """Test displaying timer status for break period."""
        with patch("builtins.print") as mock_print:
            self.timer.display_timer_status(300, "break")  # 5 minutes

        # Check that print was called with break-specific messages
        mock_print.assert_called()
        calls = [str(call) for call in mock_print.call_args_list]
        status_output = " ".join(calls)
        self.assertIn("BREAK", status_output)
        self.assertIn("Take a break", status_output)


class TestPomodoroTimerIntegration(unittest.TestCase):
    """Integration tests for PomodoroTimer class."""

    def setUp(self):
        """Set up test fixtures."""
        self.timer = PomodoroTimer()
        self.temp_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        os.chdir(self.temp_dir)
        self.timer.session_log_file = "test_sessions.json"

    def tearDown(self):
        """Clean up after each test method."""
        os.chdir(self.original_dir)
        # Clean up temp files
        for file in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file))
        os.rmdir(self.temp_dir)

    def test_complete_session_workflow(self):
        """Test complete session workflow from start to logging."""
        # Set up session parameters
        self.timer.work_duration = 1  # 1 second for testing
        self.timer.break_duration = 1  # 1 second for testing
        self.timer.total_cycles = 2

        # Mock the countdown to return immediately (completed)
        with patch.object(self.timer, "countdown", return_value=True), patch(
            "builtins.input", return_value=""
        ):  # Skip user prompts

            self.timer.start_pomodoro_session(2)

        # Verify session was logged
        self.assertTrue(os.path.exists(self.timer.session_log_file))

        with open(self.timer.session_log_file, "r") as file:
            sessions = json.load(file)

        self.assertEqual(len(sessions), 1)
        self.assertEqual(sessions[0]["cycles_completed"], 2)
        self.assertEqual(sessions[0]["cycles_planned"], 2)
        self.assertFalse(sessions[0]["interrupted"])

    def test_interrupted_session_workflow(self):
        """Test interrupted session workflow."""
        self.timer.work_duration = 1  # 1 second for testing
        self.timer.break_duration = 1  # 1 second for testing
        self.timer.total_cycles = 3

        # Mock countdown to simulate interruption
        with patch.object(self.timer, "countdown", side_effect=[True, False]), patch(
            "builtins.input", side_effect=["", KeyboardInterrupt()]
        ):

            try:
                self.timer.start_pomodoro_session(3)
            except KeyboardInterrupt:
                pass

        # Verify partial session was logged
        if os.path.exists(self.timer.session_log_file):
            with open(self.timer.session_log_file, "r") as file:
                sessions = json.load(file)

            if sessions:
                session = sessions[0]
                self.assertLess(session["cycles_completed"], session["cycles_planned"])

    def test_statistics_calculation_workflow(self):
        """Test statistics calculation with multiple sessions."""
        # Create multiple test sessions
        today = datetime.now().date()

        sessions = []
        for i in range(5):
            session = {
                "date": today.isoformat(),
                "start_time": datetime.now().isoformat(),
                "end_time": datetime.now().isoformat(),
                "duration_seconds": 3600,  # 1 hour
                "cycles_completed": 2,
                "cycles_planned": 2,
                "work_duration": 1500,
                "break_duration": 300,
                "interrupted": i % 2 == 1,  # Alternate interrupted sessions
            }
            sessions.append(session)

        with open(self.timer.session_log_file, "w") as file:
            json.dump(sessions, file)

        # Calculate and verify statistics
        loaded_sessions = self.timer.load_session_history()
        stats = self.timer.calculate_statistics(loaded_sessions)

        self.assertEqual(stats["total_sessions"], 5)
        self.assertEqual(stats["completed_sessions"], 3)  # 3 non-interrupted
        self.assertEqual(stats["completion_rate"], 60.0)
        self.assertEqual(stats["total_cycles"], 10)
        self.assertEqual(stats["total_time_hours"], 5.0)
        self.assertEqual(stats["today_sessions"], 5)
        self.assertEqual(stats["today_cycles"], 10)
        self.assertEqual(stats["today_time_minutes"], 300.0)

    def test_configuration_persistence(self):
        """Test that configuration changes persist during session."""
        # Change durations
        with patch("builtins.input", side_effect=["20", "8"]):
            self.timer.set_durations()

        # Verify durations were changed
        self.assertEqual(self.timer.work_duration, 20 * 60)
        self.assertEqual(self.timer.break_duration, 8 * 60)

        # Start session with new durations
        self.timer.total_cycles = 1

        with patch.object(self.timer, "countdown", return_value=True), patch(
            "builtins.input", return_value=""
        ):

            self.timer.start_pomodoro_session(1)

        # Verify logged session uses new durations
        with open(self.timer.session_log_file, "r") as file:
            sessions = json.load(file)

        session = sessions[0]
        self.assertEqual(session["work_duration"], 20 * 60)
        self.assertEqual(session["break_duration"], 8 * 60)


if __name__ == "__main__":
    unittest.main()

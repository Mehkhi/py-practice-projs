#!/usr/bin/env python3
"""
Unit tests for Stopwatch Application

Tests the core functionality of timing, lap recording, and formatting.
"""

import unittest
import time
from unittest.mock import patch, mock_open
from stopwatch import Stopwatch


class TestStopwatch(unittest.TestCase):
    """Test cases for the Stopwatch class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.stopwatch = Stopwatch()

    def test_initial_state(self):
        """Test stopwatch initial state."""
        self.assertFalse(self.stopwatch.is_running)
        self.assertIsNone(self.stopwatch.start_time)
        self.assertIsNone(self.stopwatch.stop_time)
        self.assertEqual(self.stopwatch.elapsed_time, 0.0)
        self.assertEqual(len(self.stopwatch.lap_times), 0)
        self.assertEqual(self.stopwatch.lap_counter, 0)

    def test_start_stopwatch(self):
        """Test starting the stopwatch."""
        result = self.stopwatch.start()

        self.assertTrue(result)
        self.assertTrue(self.stopwatch.is_running)
        self.assertIsNotNone(self.stopwatch.start_time)
        self.assertIsNone(self.stopwatch.stop_time)

    def test_start_already_running(self):
        """Test starting when already running."""
        self.stopwatch.start()
        result = self.stopwatch.start()

        self.assertFalse(result)
        self.assertTrue(self.stopwatch.is_running)

    def test_stop_stopwatch(self):
        """Test stopping the stopwatch."""
        self.stopwatch.start()
        time.sleep(0.1)  # Small delay

        result = self.stopwatch.stop()

        self.assertTrue(result)
        self.assertFalse(self.stopwatch.is_running)
        self.assertIsNotNone(self.stopwatch.stop_time)
        self.assertGreater(self.stopwatch.elapsed_time, 0)

    def test_stop_not_running(self):
        """Test stopping when not running."""
        result = self.stopwatch.stop()

        self.assertFalse(result)
        self.assertFalse(self.stopwatch.is_running)

    def test_reset_stopwatch(self):
        """Test resetting the stopwatch."""
        # Start, record a lap, then reset
        self.stopwatch.start()
        time.sleep(0.1)
        self.stopwatch.record_lap()
        self.stopwatch.stop()

        self.stopwatch.reset()

        self.assertFalse(self.stopwatch.is_running)
        self.assertIsNone(self.stopwatch.start_time)
        self.assertIsNone(self.stopwatch.stop_time)
        self.assertEqual(self.stopwatch.elapsed_time, 0.0)
        self.assertEqual(len(self.stopwatch.lap_times), 0)
        self.assertEqual(self.stopwatch.lap_counter, 0)

    def test_get_elapsed_time_not_started(self):
        """Test getting elapsed time when not started."""
        elapsed = self.stopwatch.get_elapsed_time()
        self.assertEqual(elapsed, 0.0)

    def test_get_elapsed_time_running(self):
        """Test getting elapsed time while running."""
        self.stopwatch.start()
        time.sleep(0.1)

        elapsed = self.stopwatch.get_elapsed_time()
        self.assertGreater(elapsed, 0.09)  # At least 0.1 seconds
        self.assertLess(elapsed, 1.0)  # But less than 1 second

    def test_get_elapsed_time_stopped(self):
        """Test getting elapsed time when stopped."""
        self.stopwatch.start()
        time.sleep(0.1)
        self.stopwatch.stop()

        elapsed = self.stopwatch.get_elapsed_time()
        self.assertEqual(elapsed, self.stopwatch.elapsed_time)
        self.assertGreater(elapsed, 0.09)

    def test_record_lap_running(self):
        """Test recording lap times while running."""
        self.stopwatch.start()
        time.sleep(0.1)

        lap = self.stopwatch.record_lap()

        self.assertIsNotNone(lap)
        self.assertEqual(lap["lap_number"], 1)
        self.assertGreater(lap["absolute_time"], 0.09)
        self.assertGreater(lap["lap_duration"], 0.09)
        self.assertIn("timestamp", lap)
        self.assertIn("formatted_absolute", lap)
        self.assertIn("formatted_duration", lap)

        # Check lap was added to list
        self.assertEqual(len(self.stopwatch.lap_times), 1)
        self.assertEqual(self.stopwatch.lap_counter, 1)

    def test_record_lap_not_running(self):
        """Test recording lap times when not running."""
        lap = self.stopwatch.record_lap()

        self.assertIsNone(lap)
        self.assertEqual(len(self.stopwatch.lap_times), 0)

    def test_multiple_laps(self):
        """Test recording multiple lap times."""
        self.stopwatch.start()

        # Record first lap
        time.sleep(0.1)
        lap1 = self.stopwatch.record_lap()

        # Record second lap
        time.sleep(0.1)
        lap2 = self.stopwatch.record_lap()

        # Verify laps
        self.assertEqual(len(self.stopwatch.lap_times), 2)
        self.assertEqual(lap1["lap_number"], 1)
        self.assertEqual(lap2["lap_number"], 2)

        # Second lap duration should be less than absolute time
        self.assertLess(lap2["lap_duration"], lap2["absolute_time"])

        # Second lap absolute time should be greater than first
        self.assertGreater(lap2["absolute_time"], lap1["absolute_time"])

    def test_format_time_standard(self):
        """Test standard time formatting."""
        # Test seconds only
        result = self.stopwatch.format_time(45.5, "standard")
        self.assertEqual(result, "00:45.50")

        # Test minutes and seconds
        result = self.stopwatch.format_time(125.75, "standard")
        self.assertEqual(result, "02:05.75")

        # Test hours, minutes, seconds
        result = self.stopwatch.format_time(3661.25, "standard")
        self.assertEqual(result, "01:01:01.25")

    def test_format_time_digital(self):
        """Test digital time formatting."""
        result = self.stopwatch.format_time(3661.256, "digital")
        self.assertEqual(result, "01:01:01.25")

        result = self.stopwatch.format_time(125.756, "digital")
        self.assertEqual(result, "02:05.75")

    def test_format_time_compact(self):
        """Test compact time formatting."""
        result = self.stopwatch.format_time(45.5, "compact")
        self.assertEqual(result, "45.50s")

        result = self.stopwatch.format_time(125.75, "compact")
        self.assertEqual(result, "2m 5.8s")

        result = self.stopwatch.format_time(3661.25, "compact")
        self.assertEqual(result, "1h 1m 1s")

    def test_format_time_default(self):
        """Test default time formatting."""
        result = self.stopwatch.format_time(45.5)
        self.assertEqual(result, "00:45.50")

    def test_get_status(self):
        """Test getting stopwatch status."""
        # Initial status
        status = self.stopwatch.get_status()
        self.assertFalse(status["is_running"])
        self.assertEqual(status["elapsed_time"], 0.0)
        self.assertEqual(status["formatted_time"], "00:00.00")
        self.assertEqual(status["lap_count"], 0)
        self.assertFalse(status["has_started"])

        # After starting
        self.stopwatch.start()
        time.sleep(0.01)  # Small delay to ensure elapsed time > 0
        status = self.stopwatch.get_status()
        self.assertTrue(status["is_running"])
        self.assertGreaterEqual(status["elapsed_time"], 0)
        self.assertTrue(status["has_started"])

        # After recording lap
        self.stopwatch.record_lap()
        status = self.stopwatch.get_status()
        self.assertEqual(status["lap_count"], 1)

    def test_get_lap_times(self):
        """Test getting lap times."""
        # Initially empty
        laps = self.stopwatch.get_lap_times()
        self.assertEqual(len(laps), 0)

        # Add laps
        self.stopwatch.start()
        self.stopwatch.record_lap()
        self.stopwatch.record_lap()

        laps = self.stopwatch.get_lap_times()
        self.assertEqual(len(laps), 2)

        # Verify it's a copy (modifying shouldn't affect original)
        laps.clear()
        self.assertEqual(len(self.stopwatch.lap_times), 2)

    @patch("builtins.open", new_callable=mock_open)
    @patch("stopwatch.datetime")
    def test_save_lap_times_success(self, mock_datetime, mock_file):
        """Test successful saving of lap times."""
        # Mock datetime
        mock_datetime.now.return_value.strftime.return_value = "2023-01-01 12:00:00"

        # Add some lap times
        self.stopwatch.start()
        self.stopwatch.record_lap()
        self.stopwatch.record_lap()

        result = self.stopwatch.save_lap_times("test.txt")

        self.assertTrue(result)
        mock_file.assert_called_once_with("test.txt", "w")

        # Check that content was written
        handle = mock_file()
        written_content = "".join(call[0][0] for call in handle.write.call_args_list)
        self.assertIn("Stopwatch Lap Times", written_content)
        self.assertIn("Total Laps: 2", written_content)

    def test_save_lap_times_no_laps(self):
        """Test saving when no lap times exist."""
        result = self.stopwatch.save_lap_times()
        self.assertFalse(result)

    @patch("builtins.open", side_effect=IOError("Permission denied"))
    def test_save_lap_times_error(self, mock_file):
        """Test saving when file error occurs."""
        # Add a lap time
        self.stopwatch.start()
        self.stopwatch.record_lap()

        result = self.stopwatch.save_lap_times()
        self.assertFalse(result)


class TestStopwatchIntegration(unittest.TestCase):
    """Integration tests for complete stopwatch workflows."""

    def setUp(self):
        """Set up test fixtures."""
        self.stopwatch = Stopwatch()

    def test_complete_timing_session(self):
        """Test a complete timing session with multiple laps."""
        # Start timing
        self.assertTrue(self.stopwatch.start())
        self.assertTrue(self.stopwatch.is_running)

        # Record some laps
        time.sleep(0.1)
        lap1 = self.stopwatch.record_lap()
        self.assertIsNotNone(lap1)

        time.sleep(0.1)
        lap2 = self.stopwatch.record_lap()
        self.assertIsNotNone(lap2)

        # Stop timing
        self.assertTrue(self.stopwatch.stop())
        self.assertFalse(self.stopwatch.is_running)

        # Verify results
        self.assertEqual(len(self.stopwatch.lap_times), 2)
        self.assertGreater(self.stopwatch.get_elapsed_time(), 0.19)

        # Check lap order
        self.assertEqual(lap1["lap_number"], 1)
        self.assertEqual(lap2["lap_number"], 2)
        self.assertLess(lap1["absolute_time"], lap2["absolute_time"])

    def test_start_stop_resume_cycle(self):
        """Test start, stop, and resume functionality."""
        # Initial start
        self.stopwatch.start()
        time.sleep(0.1)
        initial_time = self.stopwatch.get_elapsed_time()

        # Stop
        self.stopwatch.stop()
        stopped_time = self.stopwatch.get_elapsed_time()

        # Resume
        self.stopwatch.start()
        time.sleep(0.1)
        resumed_time = self.stopwatch.get_elapsed_time()

        # Verify time accumulation
        self.assertGreaterEqual(stopped_time, initial_time)
        self.assertGreater(resumed_time, stopped_time)

        # The resumed time should be approximately initial + 0.2 seconds
        self.assertGreater(resumed_time, 0.19)

    def test_reset_during_operation(self):
        """Test resetting while stopwatch is running."""
        # Start and record some data
        self.stopwatch.start()
        time.sleep(0.1)
        self.stopwatch.record_lap()

        # Reset while running
        self.stopwatch.reset()

        # Verify everything is reset
        self.assertFalse(self.stopwatch.is_running)
        self.assertIsNone(self.stopwatch.start_time)
        self.assertEqual(len(self.stopwatch.lap_times), 0)
        self.assertEqual(self.stopwatch.get_elapsed_time(), 0.0)


if __name__ == "__main__":
    unittest.main()

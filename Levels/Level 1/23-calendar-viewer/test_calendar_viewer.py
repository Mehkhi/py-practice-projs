#!/usr/bin/env python3
"""
Unit tests for Calendar Viewer

This module contains basic unit tests to verify the core functionality
of the calendar viewer application.
"""

import unittest
import os
import tempfile
from datetime import datetime, date
from calendar_viewer import CalendarViewer


class TestCalendarViewer(unittest.TestCase):
    """Test cases for CalendarViewer class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a temporary file for events
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_file.close()

        # Create calendar viewer with temporary events file
        self.calendar = CalendarViewer()
        self.calendar.events_file = self.temp_file.name
        self.calendar.events = {}

    def tearDown(self):
        """Clean up after each test method."""
        # Remove temporary file
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)

    def test_date_key_generation(self):
        """Test that date keys are generated correctly."""
        # Test basic date key generation
        key1 = self.calendar.get_date_key(2024, 1, 15)
        self.assertEqual(key1, "2024-01-15")

        # Test with single digit month and day
        key2 = self.calendar.get_date_key(2024, 3, 5)
        self.assertEqual(key2, "2024-03-05")

        # Test with December
        key3 = self.calendar.get_date_key(2024, 12, 31)
        self.assertEqual(key3, "2024-12-31")

    def test_add_and_get_events(self):
        """Test adding and retrieving events."""
        # Add an event
        self.calendar.add_event(2024, 1, 15, "Test Event")

        # Retrieve the event
        events = self.calendar.get_events(2024, 1, 15)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0], "Test Event")

        # Add another event to the same date
        self.calendar.add_event(2024, 1, 15, "Another Event")
        events = self.calendar.get_events(2024, 1, 15)
        self.assertEqual(len(events), 2)
        self.assertIn("Test Event", events)
        self.assertIn("Another Event", events)

        # Test getting events for a date with no events
        events = self.calendar.get_events(2024, 1, 16)
        self.assertEqual(len(events), 0)

    def test_month_navigation(self):
        """Test month navigation functionality."""
        # Set initial date to January 2024
        self.calendar.current_date = datetime(2024, 1, 15)

        # Navigate to next month
        self.calendar.navigate_month("next")
        self.assertEqual(self.calendar.current_date.month, 2)
        self.assertEqual(self.calendar.current_date.year, 2024)

        # Navigate to previous month
        self.calendar.navigate_month("prev")
        self.assertEqual(self.calendar.current_date.month, 1)
        self.assertEqual(self.calendar.current_date.year, 2024)

        # Test year boundary - December to January
        self.calendar.current_date = datetime(2024, 12, 15)
        self.calendar.navigate_month("next")
        self.assertEqual(self.calendar.current_date.month, 1)
        self.assertEqual(self.calendar.current_date.year, 2025)

        # Test year boundary - January to December
        self.calendar.current_date = datetime(2024, 1, 15)
        self.calendar.navigate_month("prev")
        self.assertEqual(self.calendar.current_date.month, 12)
        self.assertEqual(self.calendar.current_date.year, 2023)

    def test_events_persistence(self):
        """Test that events are saved and loaded correctly."""
        # Add some events
        self.calendar.add_event(2024, 1, 15, "Persistent Event 1")
        self.calendar.add_event(2024, 2, 20, "Persistent Event 2")

        # Create a new calendar instance to test loading
        new_calendar = CalendarViewer()
        new_calendar.events_file = self.temp_file.name
        new_calendar.events = new_calendar.load_events()

        # Verify events were loaded
        events1 = new_calendar.get_events(2024, 1, 15)
        events2 = new_calendar.get_events(2024, 2, 20)

        self.assertEqual(len(events1), 1)
        self.assertEqual(events1[0], "Persistent Event 1")
        self.assertEqual(len(events2), 1)
        self.assertEqual(events2[0], "Persistent Event 2")

    def test_invalid_date_handling(self):
        """Test handling of invalid dates."""
        # Test with invalid month
        with self.assertRaises(ValueError):
            date(2024, 13, 15)  # Month 13 doesn't exist

        # Test with invalid day
        with self.assertRaises(ValueError):
            date(2024, 2, 30)  # February doesn't have 30 days

        # Test with invalid year
        with self.assertRaises(ValueError):
            date(0, 1, 1)  # Year 0 is invalid


def run_tests():
    """Run all unit tests."""
    print("Running Calendar Viewer Unit Tests")
    print("=" * 40)

    # Create test suite
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestCalendarViewer)

    # Run tests
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)

    # Print summary
    print("\n" + "=" * 40)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")

    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")

    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")

    if result.wasSuccessful():
        print("\n[OK] All tests passed!")
    else:
        print("\n[X] Some tests failed.")

    return result.wasSuccessful()


if __name__ == "__main__":
    run_tests()

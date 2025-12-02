#!/usr/bin/env python3

import unittest
from alarm_countdown_timer import parse_time_input, format_time


class TestAlarmCountdownTimer(unittest.TestCase):

    def test_parse_time_input_seconds(self):
        """Test parsing seconds input."""
        self.assertEqual(parse_time_input("30"), 30)
        self.assertEqual(parse_time_input("30s"), 30)
        self.assertEqual(parse_time_input("120s"), 120)

    def test_parse_time_input_minutes(self):
        """Test parsing minutes input."""
        self.assertEqual(parse_time_input("5m"), 300)
        self.assertEqual(parse_time_input("10m"), 600)
        self.assertEqual(parse_time_input("1m"), 60)

    def test_parse_time_input_combined(self):
        """Test parsing combined minutes and seconds."""
        self.assertEqual(parse_time_input("1m30s"), 90)
        self.assertEqual(parse_time_input("2m45s"), 165)
        self.assertEqual(parse_time_input("5m30s"), 330)

    def test_parse_time_input_colon_format(self):
        """Test parsing MM:SS format."""
        self.assertEqual(parse_time_input("1:30"), 90)
        self.assertEqual(parse_time_input("5:00"), 300)
        self.assertEqual(parse_time_input("0:45"), 45)
        self.assertEqual(parse_time_input("10:15"), 615)

    def test_parse_time_input_invalid(self):
        """Test parsing invalid input."""
        self.assertIsNone(parse_time_input("abc"))
        self.assertIsNone(parse_time_input("1h"))
        self.assertIsNone(parse_time_input(""))
        self.assertIsNone(parse_time_input("invalid"))

    def test_parse_time_input_edge_cases(self):
        """Test edge cases."""
        self.assertEqual(parse_time_input("0"), 0)
        self.assertEqual(parse_time_input("0s"), 0)
        self.assertEqual(parse_time_input("0m"), 0)
        self.assertEqual(parse_time_input("0:0"), 0)

    def test_format_time(self):
        """Test time formatting."""
        self.assertEqual(format_time(30), "00:30")
        self.assertEqual(format_time(60), "01:00")
        self.assertEqual(format_time(90), "01:30")
        self.assertEqual(format_time(125), "02:05")
        self.assertEqual(format_time(3600), "60:00")
        self.assertEqual(format_time(0), "00:00")

    def test_format_time_edge_cases(self):
        """Test time formatting edge cases."""
        self.assertEqual(format_time(1), "00:01")
        self.assertEqual(format_time(59), "00:59")
        self.assertEqual(format_time(61), "01:01")
        self.assertEqual(format_time(3599), "59:59")


if __name__ == "__main__":
    unittest.main()

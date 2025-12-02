"""Unit tests for core/time_system.py - DayNightCycle, TimeOfDay."""

import unittest

from core.time_system import (
    TimeOfDay,
    DayNightCycle,
    TIME_TINTS,
    TIME_AMBIENT,
)


class TestTimeOfDay(unittest.TestCase):
    def test_time_periods_exist(self):
        self.assertEqual(TimeOfDay.DAWN.value, "dawn")
        self.assertEqual(TimeOfDay.MORNING.value, "morning")
        self.assertEqual(TimeOfDay.NOON.value, "noon")
        self.assertEqual(TimeOfDay.AFTERNOON.value, "afternoon")
        self.assertEqual(TimeOfDay.DUSK.value, "dusk")
        self.assertEqual(TimeOfDay.EVENING.value, "evening")
        self.assertEqual(TimeOfDay.NIGHT.value, "night")
        self.assertEqual(TimeOfDay.MIDNIGHT.value, "midnight")

    def test_all_periods_have_tints(self):
        for period in TimeOfDay:
            self.assertIn(period, TIME_TINTS)

    def test_all_periods_have_ambient(self):
        for period in TimeOfDay:
            self.assertIn(period, TIME_AMBIENT)


class TestDayNightCycle(unittest.TestCase):
    def setUp(self):
        self.cycle = DayNightCycle()

    def test_default_state(self):
        self.assertEqual(self.cycle.current_time, 360.0)  # 6:00 AM
        self.assertEqual(self.cycle.day_count, 1)
        self.assertEqual(self.cycle.time_scale, 1.0)
        self.assertFalse(self.cycle.paused)

    def test_get_hour(self):
        self.cycle.current_time = 720.0  # 12:00 PM
        self.assertEqual(self.cycle.get_hour(), 12)

    def test_get_hour_midnight(self):
        self.cycle.current_time = 0.0
        self.assertEqual(self.cycle.get_hour(), 0)

    def test_get_minute(self):
        self.cycle.current_time = 725.0  # 12:05
        self.assertEqual(self.cycle.get_minute(), 5)

    def test_get_formatted_time(self):
        self.cycle.current_time = 725.0
        self.assertEqual(self.cycle.get_formatted_time(), "12:05")

    def test_get_formatted_time_leading_zeros(self):
        self.cycle.current_time = 65.0  # 1:05 AM
        self.assertEqual(self.cycle.get_formatted_time(), "01:05")

    def test_get_12hour_time_am(self):
        self.cycle.current_time = 540.0  # 9:00 AM
        self.assertEqual(self.cycle.get_12hour_time(), "9:00 AM")

    def test_get_12hour_time_pm(self):
        self.cycle.current_time = 840.0  # 2:00 PM
        self.assertEqual(self.cycle.get_12hour_time(), "2:00 PM")

    def test_get_12hour_time_noon(self):
        self.cycle.current_time = 720.0  # 12:00 PM
        self.assertEqual(self.cycle.get_12hour_time(), "12:00 PM")

    def test_get_12hour_time_midnight(self):
        self.cycle.current_time = 0.0
        self.assertEqual(self.cycle.get_12hour_time(), "12:00 AM")

    def test_get_time_of_day_dawn(self):
        self.cycle.current_time = 270.0  # 4:30 AM
        self.assertEqual(self.cycle.get_time_of_day(), TimeOfDay.DAWN)

    def test_get_time_of_day_morning(self):
        self.cycle.current_time = 420.0  # 7:00 AM
        self.assertEqual(self.cycle.get_time_of_day(), TimeOfDay.MORNING)

    def test_get_time_of_day_noon(self):
        self.cycle.current_time = 660.0  # 11:00 AM
        self.assertEqual(self.cycle.get_time_of_day(), TimeOfDay.NOON)

    def test_get_time_of_day_afternoon(self):
        self.cycle.current_time = 900.0  # 3:00 PM
        self.assertEqual(self.cycle.get_time_of_day(), TimeOfDay.AFTERNOON)

    def test_get_time_of_day_dusk(self):
        self.cycle.current_time = 1080.0  # 6:00 PM
        self.assertEqual(self.cycle.get_time_of_day(), TimeOfDay.DUSK)

    def test_get_time_of_day_evening(self):
        self.cycle.current_time = 1200.0  # 8:00 PM
        self.assertEqual(self.cycle.get_time_of_day(), TimeOfDay.EVENING)

    def test_get_time_of_day_night(self):
        self.cycle.current_time = 1380.0  # 11:00 PM
        self.assertEqual(self.cycle.get_time_of_day(), TimeOfDay.NIGHT)

    def test_get_time_of_day_midnight(self):
        self.cycle.current_time = 60.0  # 1:00 AM
        self.assertEqual(self.cycle.get_time_of_day(), TimeOfDay.MIDNIGHT)

    def test_update_advances_time(self):
        initial = self.cycle.current_time
        self.cycle.update(60.0)  # 60 seconds = 60 game minutes
        self.assertEqual(self.cycle.current_time, initial + 60.0)

    def test_update_with_time_scale(self):
        self.cycle.time_scale = 2.0
        initial = self.cycle.current_time
        self.cycle.update(30.0)
        self.assertEqual(self.cycle.current_time, initial + 60.0)

    def test_update_paused(self):
        self.cycle.paused = True
        initial = self.cycle.current_time
        self.cycle.update(100.0)
        self.assertEqual(self.cycle.current_time, initial)

    def test_update_day_rollover(self):
        self.cycle.current_time = 1430.0  # 23:50
        self.cycle.update(20.0)  # +20 minutes
        self.assertEqual(self.cycle.day_count, 2)
        self.assertEqual(self.cycle.current_time, 10.0)

    def test_update_multiple_day_rollover(self):
        self.cycle.current_time = 0.0
        self.cycle.update(2880.0)  # 2 full days
        self.assertEqual(self.cycle.day_count, 3)

    def test_set_time(self):
        self.cycle.set_time(14, 30)
        self.assertEqual(self.cycle.get_hour(), 14)
        self.assertEqual(self.cycle.get_minute(), 30)

    def test_set_time_wraps(self):
        self.cycle.set_time(25, 70)  # Invalid values wrap
        self.assertEqual(self.cycle.get_hour(), 1)  # 25 % 24
        self.assertEqual(self.cycle.get_minute(), 10)  # 70 % 60

    def test_advance_hours(self):
        self.cycle.current_time = 360.0  # 6:00 AM
        self.cycle.advance_hours(3.5)
        self.assertEqual(self.cycle.current_time, 570.0)  # 9:30 AM

    def test_advance_hours_rollover(self):
        self.cycle.current_time = 1380.0  # 11:00 PM
        self.cycle.advance_hours(2)  # +2 hours
        self.assertEqual(self.cycle.day_count, 2)
        self.assertEqual(self.cycle.get_hour(), 1)

    def test_is_daytime(self):
        self.cycle.current_time = 720.0  # Noon
        self.assertTrue(self.cycle.is_daytime())

    def test_is_daytime_boundary_start(self):
        self.cycle.current_time = 360.0  # 6:00 AM
        self.assertTrue(self.cycle.is_daytime())

    def test_is_daytime_boundary_end(self):
        self.cycle.current_time = 1079.0  # 5:59 PM
        self.assertTrue(self.cycle.is_daytime())

    def test_is_nighttime(self):
        self.cycle.current_time = 1200.0  # 8:00 PM
        self.assertTrue(self.cycle.is_nighttime())

    def test_is_nighttime_early_morning(self):
        self.cycle.current_time = 180.0  # 3:00 AM
        self.assertTrue(self.cycle.is_nighttime())

    def test_get_tint_color(self):
        self.cycle.current_time = 720.0  # Noon
        tint = self.cycle.get_tint_color()
        self.assertEqual(len(tint), 4)
        self.assertEqual(tint, TIME_TINTS[TimeOfDay.NOON])

    def test_get_ambient_level(self):
        self.cycle.current_time = 720.0  # Noon
        ambient = self.cycle.get_ambient_level()
        self.assertEqual(ambient, 1.0)

    def test_get_ambient_level_night(self):
        self.cycle.current_time = 60.0  # 1:00 AM
        ambient = self.cycle.get_ambient_level()
        self.assertLess(ambient, 0.5)

    def test_serialize(self):
        self.cycle.current_time = 720.0
        self.cycle.day_count = 5
        self.cycle.time_scale = 2.0
        self.cycle.paused = True

        data = self.cycle.serialize()

        self.assertEqual(data["current_time"], 720.0)
        self.assertEqual(data["day_count"], 5)
        self.assertEqual(data["time_scale"], 2.0)
        self.assertTrue(data["paused"])

    def test_deserialize(self):
        data = {
            "current_time": 900.0,
            "day_count": 10,
            "time_scale": 0.5,
            "paused": True,
        }
        cycle = DayNightCycle.deserialize(data)

        self.assertEqual(cycle.current_time, 900.0)
        self.assertEqual(cycle.day_count, 10)
        self.assertEqual(cycle.time_scale, 0.5)
        self.assertTrue(cycle.paused)

    def test_deserialize_defaults(self):
        cycle = DayNightCycle.deserialize({})
        self.assertEqual(cycle.current_time, 360.0)
        self.assertEqual(cycle.day_count, 1)


class TestTimeConstants(unittest.TestCase):
    def test_tints_are_rgba(self):
        for period, tint in TIME_TINTS.items():
            self.assertEqual(len(tint), 4)
            for value in tint:
                self.assertGreaterEqual(value, 0)
                self.assertLessEqual(value, 255)

    def test_ambient_in_range(self):
        for period, ambient in TIME_AMBIENT.items():
            self.assertGreaterEqual(ambient, 0.0)
            self.assertLessEqual(ambient, 1.0)

    def test_noon_is_brightest(self):
        self.assertEqual(TIME_AMBIENT[TimeOfDay.NOON], 1.0)

    def test_midnight_is_darkest(self):
        self.assertEqual(TIME_AMBIENT[TimeOfDay.MIDNIGHT], min(TIME_AMBIENT.values()))


if __name__ == "__main__":
    unittest.main()

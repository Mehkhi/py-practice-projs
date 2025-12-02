"""Day/night cycle system for the game world."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Tuple, Dict, Any


class TimeOfDay(Enum):
    """Represents different periods of the day."""
    DAWN = "dawn"
    MORNING = "morning"
    NOON = "noon"
    AFTERNOON = "afternoon"
    DUSK = "dusk"
    EVENING = "evening"
    NIGHT = "night"
    MIDNIGHT = "midnight"


# Color tints for each time of day (R, G, B, Alpha)
# Alpha controls overlay opacity (0 = no tint, 255 = full tint)
TIME_TINTS: Dict[TimeOfDay, Tuple[int, int, int, int]] = {
    TimeOfDay.DAWN: (255, 200, 150, 40),       # Warm orange-pink
    TimeOfDay.MORNING: (255, 250, 230, 15),    # Slight warm yellow
    TimeOfDay.NOON: (255, 255, 255, 0),        # No tint (full daylight)
    TimeOfDay.AFTERNOON: (255, 240, 200, 20),  # Warm golden
    TimeOfDay.DUSK: (255, 150, 100, 50),       # Orange-red sunset
    TimeOfDay.EVENING: (100, 80, 150, 60),     # Purple twilight
    TimeOfDay.NIGHT: (30, 30, 80, 100),        # Deep blue night
    TimeOfDay.MIDNIGHT: (10, 10, 50, 120),     # Very dark blue
}

# Ambient light levels for each time of day (0.0 = pitch black, 1.0 = full brightness)
TIME_AMBIENT: Dict[TimeOfDay, float] = {
    TimeOfDay.DAWN: 0.6,
    TimeOfDay.MORNING: 0.85,
    TimeOfDay.NOON: 1.0,
    TimeOfDay.AFTERNOON: 0.95,
    TimeOfDay.DUSK: 0.7,
    TimeOfDay.EVENING: 0.5,
    TimeOfDay.NIGHT: 0.3,
    TimeOfDay.MIDNIGHT: 0.2,
}


@dataclass
class DayNightCycle:
    """
    Manages the day/night cycle for the game world.

    Implements the Saveable protocol for automatic save/load via SaveContext.

    Time is measured in game minutes. A full day is 24 game hours (1440 minutes).
    The cycle progresses based on real time, with a configurable speed multiplier.

    Attributes:
        current_time: Current time in game minutes (0-1439)
        day_count: Number of days that have passed
        time_scale: How many game minutes pass per real second (default: 1.0)
        paused: Whether time progression is paused
        save_key: Key used for this manager in save data ('day_night')
    """
    current_time: float = 360.0  # Start at 6:00 AM (dawn)
    day_count: int = 1
    time_scale: float = 1.0  # 1 game minute per real second by default
    paused: bool = False

    # Class attribute for Saveable protocol
    save_key: str = "day_night"

    # Internal state for smooth transitions
    _transition_progress: float = field(default=0.0, repr=False)

    MINUTES_PER_DAY: int = 1440  # 24 hours * 60 minutes

    # Time ranges for each period (in game minutes from midnight)
    TIME_RANGES: Dict[TimeOfDay, Tuple[int, int]] = field(default_factory=lambda: {
        TimeOfDay.MIDNIGHT: (0, 180),      # 00:00 - 03:00
        TimeOfDay.DAWN: (180, 360),        # 03:00 - 06:00
        TimeOfDay.MORNING: (360, 540),     # 06:00 - 09:00
        TimeOfDay.NOON: (540, 780),        # 09:00 - 13:00
        TimeOfDay.AFTERNOON: (780, 1020),  # 13:00 - 17:00
        TimeOfDay.DUSK: (1020, 1140),      # 17:00 - 19:00
        TimeOfDay.EVENING: (1140, 1320),   # 19:00 - 22:00
        TimeOfDay.NIGHT: (1320, 1440),     # 22:00 - 24:00
    })

    def update(self, dt: float) -> None:
        """
        Update the time cycle.

        Args:
            dt: Delta time in seconds since last update
        """
        if self.paused:
            return

        # Advance time based on time scale
        self.current_time += dt * self.time_scale

        # Handle day rollover
        while self.current_time >= self.MINUTES_PER_DAY:
            self.current_time -= self.MINUTES_PER_DAY
            self.day_count += 1

    def get_time_of_day(self) -> TimeOfDay:
        """Get the current time period."""
        time_int = int(self.current_time) % self.MINUTES_PER_DAY

        for period, (start, end) in self.TIME_RANGES.items():
            if start <= time_int < end:
                return period

        # Fallback (shouldn't happen with proper ranges)
        return TimeOfDay.MIDNIGHT

    def get_hour(self) -> int:
        """Get the current hour (0-23)."""
        return int(self.current_time // 60) % 24

    def get_minute(self) -> int:
        """Get the current minute (0-59)."""
        return int(self.current_time) % 60

    def get_formatted_time(self) -> str:
        """Get the current time as a formatted string (HH:MM)."""
        hour = self.get_hour()
        minute = self.get_minute()
        return f"{hour:02d}:{minute:02d}"

    def get_12hour_time(self) -> str:
        """Get the current time in 12-hour format with AM/PM."""
        hour = self.get_hour()
        minute = self.get_minute()
        period = "AM" if hour < 12 else "PM"
        display_hour = hour % 12
        if display_hour == 0:
            display_hour = 12
        return f"{display_hour}:{minute:02d} {period}"

    def get_tint_color(self) -> Tuple[int, int, int, int]:
        """
        Get the current tint color with smooth interpolation between periods.

        Returns:
            RGBA tuple for the overlay tint
        """
        current_period = self.get_time_of_day()
        current_tint = TIME_TINTS[current_period]

        # Find the next period for interpolation
        time_int = int(self.current_time) % self.MINUTES_PER_DAY
        start, end = self.TIME_RANGES[current_period]

        # Calculate progress through current period (0.0 to 1.0)
        period_duration = end - start
        progress = (time_int - start) / period_duration if period_duration > 0 else 0.0

        # Get next period's tint for smooth transition
        next_period = self._get_next_period(current_period)
        next_tint = TIME_TINTS[next_period]

        # Interpolate colors for smooth transition
        # Only start blending in the last 25% of each period
        if progress > 0.75:
            blend = (progress - 0.75) * 4  # 0.0 to 1.0 over last 25%
            return self._lerp_color(current_tint, next_tint, blend)

        return current_tint

    def get_ambient_level(self) -> float:
        """
        Get the current ambient light level with smooth interpolation.

        Returns:
            Float from 0.0 (dark) to 1.0 (bright)
        """
        current_period = self.get_time_of_day()
        current_ambient = TIME_AMBIENT[current_period]

        time_int = int(self.current_time) % self.MINUTES_PER_DAY
        start, end = self.TIME_RANGES[current_period]

        period_duration = end - start
        progress = (time_int - start) / period_duration if period_duration > 0 else 0.0

        next_period = self._get_next_period(current_period)
        next_ambient = TIME_AMBIENT[next_period]

        # Smooth interpolation throughout the period
        if progress > 0.75:
            blend = (progress - 0.75) * 4
            return current_ambient + (next_ambient - current_ambient) * blend

        return current_ambient

    def _get_next_period(self, current: TimeOfDay) -> TimeOfDay:
        """Get the next time period in the cycle."""
        order = [
            TimeOfDay.MIDNIGHT, TimeOfDay.DAWN, TimeOfDay.MORNING,
            TimeOfDay.NOON, TimeOfDay.AFTERNOON, TimeOfDay.DUSK,
            TimeOfDay.EVENING, TimeOfDay.NIGHT
        ]
        idx = order.index(current)
        return order[(idx + 1) % len(order)]

    def _lerp_color(
        self,
        c1: Tuple[int, int, int, int],
        c2: Tuple[int, int, int, int],
        t: float
    ) -> Tuple[int, int, int, int]:
        """Linearly interpolate between two RGBA colors."""
        return (
            int(c1[0] + (c2[0] - c1[0]) * t),
            int(c1[1] + (c2[1] - c1[1]) * t),
            int(c1[2] + (c2[2] - c1[2]) * t),
            int(c1[3] + (c2[3] - c1[3]) * t),
        )

    def set_time(self, hour: int, minute: int = 0) -> None:
        """
        Set the current time directly.

        Args:
            hour: Hour (0-23)
            minute: Minute (0-59)
        """
        self.current_time = float((hour % 24) * 60 + (minute % 60))

    def advance_hours(self, hours: float) -> None:
        """Advance time by a number of hours (can be fractional)."""
        self.current_time += hours * 60
        while self.current_time >= self.MINUTES_PER_DAY:
            self.current_time -= self.MINUTES_PER_DAY
            self.day_count += 1

    def is_daytime(self) -> bool:
        """Check if it's currently daytime (6 AM to 6 PM)."""
        hour = self.get_hour()
        return 6 <= hour < 18

    def is_nighttime(self) -> bool:
        """Check if it's currently nighttime (6 PM to 6 AM)."""
        return not self.is_daytime()

    def serialize(self) -> Dict[str, Any]:
        """Serialize the time state for saving."""
        return {
            "current_time": self.current_time,
            "day_count": self.day_count,
            "time_scale": self.time_scale,
            "paused": self.paused,
        }

    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> "DayNightCycle":
        """Deserialize time state from saved data."""
        return cls(
            current_time=data.get("current_time", 360.0),
            day_count=data.get("day_count", 1),
            time_scale=data.get("time_scale", 1.0),
            paused=data.get("paused", False),
        )

    def deserialize_into(self, data: Dict[str, Any]) -> None:
        """Restore state from saved data (Saveable protocol)."""
        self.current_time = data.get("current_time", 360.0)
        self.day_count = data.get("day_count", 1)
        self.time_scale = data.get("time_scale", 1.0)
        # Don't restore paused state - let config control that

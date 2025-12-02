"""Utility helpers for the task scheduler."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Set


class CronExpressionError(ValueError):
    """Raised when a cron expression cannot be parsed or produces no run times."""


@dataclass
class CronSchedule:
    """Minimal cron expression evaluator supporting five-field syntax."""

    expression: str
    base_time: datetime | None = None

    def __post_init__(self) -> None:
        fields = self.expression.split()
        if len(fields) != 5:
            raise CronExpressionError("Cron expression must have exactly 5 fields")

        self.minutes = _parse_cron_field(fields[0], 0, 59)
        self.hours = _parse_cron_field(fields[1], 0, 23)
        self.days = _parse_cron_field(fields[2], 1, 31)
        self.months = _parse_cron_field(fields[3], 1, 12)
        self.weekdays = _parse_weekday_field(fields[4])
        self._last_run = self.base_time or datetime.now()

    def get_next(self) -> datetime:
        """Return the next run time strictly after the previous reference."""
        candidate = _increment_minute(self._last_run)

        for _ in range(60 * 24 * 366):  # Search up to one year ahead.
            if self._matches(candidate):
                self._last_run = candidate
                return candidate
            candidate += timedelta(minutes=1)

        raise CronExpressionError("Cron expression did not yield a run time within a year")

    def _matches(self, moment: datetime) -> bool:
        python_weekday = moment.weekday()
        return (
            moment.minute in self.minutes
            and moment.hour in self.hours
            and moment.day in self.days
            and moment.month in self.months
            and python_weekday in self.weekdays
        )


def _increment_minute(reference: datetime) -> datetime:
    """Advance to the next minute boundary strictly after the reference."""
    return reference.replace(second=0, microsecond=0) + timedelta(minutes=1)


def _parse_cron_field(field: str, minimum: int, maximum: int) -> Set[int]:
    """Parse a generic cron field into a set of allowed integers."""
    if field in ("*", "?"):
        return set(range(minimum, maximum + 1))

    values: Set[int] = set()
    for part in field.split(","):
        values.update(_expand_part(part.strip(), minimum, maximum))

    if not values:
        raise CronExpressionError(f"No values parsed for field '{field}'")

    return values


def _parse_weekday_field(field: str) -> Set[int]:
    """Parse the day-of-week field, returning Python weekday numbers (0=Monday)."""
    raw_values = _parse_cron_field(field, 0, 7)
    converted = {(value - 1) % 7 for value in raw_values}
    return converted


def _expand_part(part: str, minimum: int, maximum: int) -> List[int]:
    """Expand a cron field segment like '5', '1-5/2', or '*/15'."""
    if not part:
        raise CronExpressionError("Empty cron segment")

    step = 1
    if "/" in part:
        base, step_str = part.split("/", 1)
        part = base or "*"
        try:
            step = int(step_str)
        except ValueError as exc:
            raise CronExpressionError(f"Invalid cron step '{step_str}'") from exc
        if step <= 0:
            raise CronExpressionError("Cron step must be a positive integer")

    if part in ("*", "?"):
        start, end = minimum, maximum
    elif "-" in part:
        start_str, end_str = part.split("-", 1)
        try:
            start = int(start_str)
            end = int(end_str)
        except ValueError as exc:
            raise CronExpressionError(f"Invalid cron range '{part}'") from exc
    else:
        try:
            value = int(part)
        except ValueError as exc:
            raise CronExpressionError(f"Invalid cron value '{part}'") from exc
        start = end = value

    if start < minimum or end > maximum or start > end:
        raise CronExpressionError(
            f"Cron values {start}-{end} outside allowed range {minimum}-{maximum}"
        )

    return list(range(start, end + 1, step))

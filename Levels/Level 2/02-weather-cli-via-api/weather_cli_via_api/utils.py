"""Utility helpers for the weather CLI."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

UNIT_LABELS = {
    "metric": {"temp": "°C", "wind": "m/s"},
    "imperial": {"temp": "°F", "wind": "mph"},
    "standard": {"temp": "K", "wind": "m/s"},
}


def format_unix_timestamp(ts: int | float, tz_offset: int | float) -> str:
    """Convert a UNIX timestamp and timezone offset to an ISO-like string."""
    tz = timezone(timedelta(seconds=int(tz_offset)))
    dt = datetime.fromtimestamp(int(ts), tz=tz)
    return dt.strftime("%Y-%m-%d %H:%M")


def temperature_unit_label(units: str) -> str:
    """Return the temperature unit label for the given units code."""
    return UNIT_LABELS.get(units, UNIT_LABELS["metric"])["temp"]


def wind_speed_unit_label(units: str) -> str:
    """Return the wind speed unit label for the given units code."""
    return UNIT_LABELS.get(units, UNIT_LABELS["metric"])["wind"]


def convert_temperature(value: float, from_units: str, to_units: str) -> float:
    """Convert temperature between OpenWeatherMap-supported units."""
    if from_units == to_units:
        return value
    kelvin = value
    if from_units == "metric":
        kelvin = value + 273.15
    elif from_units == "imperial":
        kelvin = (value - 32) * 5 / 9 + 273.15
    elif from_units == "standard":
        kelvin = value
    else:
        raise ValueError(f"Unsupported temperature units: {from_units}")

    if to_units == "metric":
        return kelvin - 273.15
    if to_units == "imperial":
        return (kelvin - 273.15) * 9 / 5 + 32
    if to_units == "standard":
        return kelvin
    raise ValueError(f"Unsupported temperature units: {to_units}")


def convert_wind_speed(value: float, from_units: str, to_units: str) -> float:
    """Convert wind speed between OpenWeatherMap-supported units."""
    if from_units == to_units:
        return value

    # Normalize to meters per second as baseline.
    if from_units == "imperial":
        base_mps = value * 0.44704
    elif from_units in {"metric", "standard"}:
        base_mps = value
    else:
        raise ValueError(f"Unsupported wind speed units: {from_units}")

    if to_units in {"metric", "standard"}:
        return base_mps
    if to_units == "imperial":
        return base_mps / 0.44704
    raise ValueError(f"Unsupported wind speed units: {to_units}")

"""Core services for the weather CLI."""

from __future__ import annotations

import logging
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable

import requests

from .cache import ResponseCache
from .utils import (
    convert_temperature,
    convert_wind_speed,
    format_unix_timestamp,
    temperature_unit_label,
    wind_speed_unit_label,
)

API_BASE_URL = "https://api.openweathermap.org/data/2.5"
GEOCODE_URL = "https://api.openweathermap.org/geo/1.0/direct"
VALID_UNITS = {"metric", "imperial", "standard"}


class WeatherServiceError(RuntimeError):
    """Raised when interacting with the weather service fails."""


@dataclass
class ResolvedLocation:
    """Result of resolving a user-supplied location."""

    query: str
    name: str
    lat: float
    lon: float
    country: str | None = None
    state: str | None = None

    @property
    def display_name(self) -> str:
        """Return a friendly display name for the location."""
        parts: list[str] = [self.name]
        if self.state and self.state not in parts:
            parts.append(self.state)
        if self.country:
            parts.append(self.country)
        return ", ".join(parts)


@dataclass
class ForecastEntry:
    """Represents a single forecast entry."""

    timestamp: str
    description: str
    temperature: float


@dataclass
class WeatherReport:
    """Structured data for a weather report."""

    location: str
    description: str
    temperature: float
    feels_like: float
    humidity: int
    wind_speed: float
    sunrise: str
    sunset: str
    units: str = "metric"
    forecast: list[ForecastEntry] | None = None
    display_units: list[str] | None = None

    def to_text(self) -> str:
        """Render the report in a human-readable format."""
        temp_unit = temperature_unit_label(self.units)
        wind_unit = wind_speed_unit_label(self.units)

        lines = [
            f"Location: {self.location}",
            f"Condition: {self.description}",
            f"Temperature: {self.temperature:.1f}{temp_unit} (feels like {self.feels_like:.1f}{temp_unit})",
            f"Humidity: {self.humidity}%",
            f"Wind: {self.wind_speed:.1f} {wind_unit}",
            f"Sunrise: {self.sunrise}",
            f"Sunset: {self.sunset}",
        ]
        if self.forecast:
            lines.append("Forecast:")
            for entry in self.forecast:
                lines.append(
                    f"  - {entry.timestamp}: {entry.description} at {entry.temperature:.1f}{temp_unit}"
                )
        if self.display_units:
            lines.append("Conversions:")
            for alt_unit in self.display_units:
                temp_alt = convert_temperature(self.temperature, self.units, alt_unit)
                feels_alt = convert_temperature(self.feels_like, self.units, alt_unit)
                wind_alt = convert_wind_speed(self.wind_speed, self.units, alt_unit)
                lines.append(
                    "  - "
                    f"{alt_unit.title()}: "
                    f"{temp_alt:.1f}{temperature_unit_label(alt_unit)} "
                    f"(feels {feels_alt:.1f}{temperature_unit_label(alt_unit)}); "
                    f"wind {wind_alt:.1f} {wind_speed_unit_label(alt_unit)}"
                )
        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        """Convert the report to a dictionary for JSON serialization."""
        result: dict[str, Any] = {
            "location": self.location,
            "description": self.description,
            "temperature": self.temperature,
            "feels_like": self.feels_like,
            "humidity": self.humidity,
            "wind_speed": self.wind_speed,
            "sunrise": self.sunrise,
            "sunset": self.sunset,
            "units": self.units,
        }

        if self.forecast:
            result["forecast"] = [
                {
                    "timestamp": entry.timestamp,
                    "description": entry.description,
                    "temperature": entry.temperature,
                }
                for entry in self.forecast
            ]

        if self.display_units:
            result["conversions"] = []
            for alt_unit in self.display_units:
                temp_alt = convert_temperature(self.temperature, self.units, alt_unit)
                feels_alt = convert_temperature(self.feels_like, self.units, alt_unit)
                wind_alt = convert_wind_speed(self.wind_speed, self.units, alt_unit)
                result["conversions"].append(
                    {
                        "unit": alt_unit,
                        "temperature": temp_alt,
                        "feels_like": feels_alt,
                        "wind_speed": wind_alt,
                        "temperature_unit": temperature_unit_label(alt_unit),
                        "wind_unit": wind_speed_unit_label(alt_unit),
                    }
                )

        return result


class WeatherClient:
    """Client responsible for fetching and rendering weather data."""

    def __init__(
        self,
        api_key: str | None = None,
        *,
        use_cache: bool = True,
        cache_ttl: int = 600,
        cache_path: str | None = None,
        session: requests.Session | None = None,
    ) -> None:
        self._api_key = api_key
        self.use_cache = use_cache
        self.cache_ttl = cache_ttl
        self._session = session or requests.Session()
        self._cache = (
            ResponseCache(Path(cache_path))
            if cache_path and use_cache
            else (ResponseCache() if use_cache else None)
        )

    def get_weather(
        self,
        location: str,
        *,
        units: str = "metric",
        include_forecast: bool = False,
        display_units: Iterable[str] | None = None,
        format_mode: str = "simple",
    ) -> str | WeatherReport:
        """Fetch weather data for the provided location."""
        location_query = location.strip()
        if not location_query:
            raise WeatherServiceError("Location must not be empty.")

        normalized_units = self._normalize_units(units)
        normalized_display = self._normalize_display_units(
            display_units, normalized_units
        )
        resolved_location = self._resolve_location(location_query)
        cache_key = self._cache_key(
            resolved_location, normalized_units, include_forecast
        )

        payload: dict[str, Any] | None = None
        if self.use_cache and self._cache:
            payload = self._cache.get(cache_key, self.cache_ttl)
            if payload:
                logging.info(
                    "Using cached weather data for %s (%.4f, %.4f)",
                    resolved_location.display_name,
                    resolved_location.lat,
                    resolved_location.lon,
                )

        if not payload:
            logging.info(
                "Fetching weather data for %s from API",
                resolved_location.display_name,
            )
            payload = self._fetch_payload(
                resolved_location, normalized_units, include_forecast
            )
            if self.use_cache and self._cache:
                self._cache.set(cache_key, payload)

        report = self._build_report(
            location_query,
            resolved_location,
            payload["current"],
            payload.get("forecast"),
            normalized_units,
            normalized_display,
        )

        if format_mode == "simple":
            return report.to_text()
        return report

    def _fetch_payload(
        self,
        location: ResolvedLocation,
        units: str,
        include_forecast: bool,
    ) -> dict[str, Any]:
        params = self._build_params(location, units)
        current = self._fetch("weather", params)
        forecast = self._fetch("forecast", params) if include_forecast else None
        return {"current": current, "forecast": forecast}

    def _fetch(self, endpoint: str, params: dict[str, Any]) -> dict[str, Any]:
        url = f"{API_BASE_URL}/{endpoint}"
        safe_params = {k: v for k, v in params.items() if k != "appid"}
        logging.debug("GET %s params=%s", url, safe_params)
        try:
            response = self._session.get(url, params=params, timeout=10)
        except requests.RequestException as exc:
            raise WeatherServiceError(
                f"Network error while fetching weather data: {exc}"
            ) from exc

        try:
            payload: dict[str, Any] = response.json()
        except ValueError as exc:
            raise WeatherServiceError(
                "Received invalid JSON from weather service."
            ) from exc

        if response.status_code >= 400:
            self._raise_api_error(payload, response.status_code, endpoint)

        code = payload.get("cod")
        try:
            code_int = int(code)
        except (TypeError, ValueError):
            code_int = response.status_code

        if code_int != 200:
            self._raise_api_error(payload, code_int, endpoint)
        return payload

    def _raise_api_error(
        self, payload: dict[str, Any], status: int, endpoint: str
    ) -> None:
        message = payload.get("message") or "Unexpected error"
        raise WeatherServiceError(
            f"API request to '{endpoint}' failed (status {status}): {message}"
        )

    def _build_params(self, location: ResolvedLocation, units: str) -> dict[str, Any]:
        return {
            "lat": location.lat,
            "lon": location.lon,
            "units": units,
            "appid": self._resolve_api_key(),
        }

    def _build_report(
        self,
        location_query: str,
        resolved: ResolvedLocation,
        current: dict[str, Any],
        forecast: dict[str, Any] | None,
        units: str,
        display_units: list[str] | None,
    ) -> WeatherReport:
        try:
            weather_entry = current["weather"][0]
            main = current["main"]
            sys = current["sys"]
            wind = current.get("wind", {})
        except (KeyError, IndexError, TypeError) as exc:
            raise WeatherServiceError("Weather data missing expected fields.") from exc

        tz_offset = int(current.get("timezone", 0))
        city = current.get("name") or resolved.name or location_query
        country = sys.get("country") or resolved.country

        location_display = city
        if resolved.state and resolved.state not in location_display:
            location_display = f"{location_display}, {resolved.state}"
        if country:
            location_display = f"{location_display}, {country}"

        sunrise = format_unix_timestamp(int(sys["sunrise"]), tz_offset)
        sunset = format_unix_timestamp(int(sys["sunset"]), tz_offset)

        forecast_entries = self._prepare_forecast(forecast, units) if forecast else None

        return WeatherReport(
            location=location_display,
            description=str(weather_entry.get("description", "")).title(),
            temperature=float(main.get("temp", 0)),
            feels_like=float(main.get("feels_like", 0)),
            humidity=int(main.get("humidity", 0)),
            wind_speed=float(wind.get("speed", 0)),
            sunrise=sunrise,
            sunset=sunset,
            units=units,
            forecast=forecast_entries,
            display_units=display_units,
        )

    def _prepare_forecast(
        self,
        forecast_payload: dict[str, Any],
        units: str,
    ) -> list[ForecastEntry]:
        tz_offset = int(forecast_payload.get("city", {}).get("timezone", 0))
        entries: list[ForecastEntry] = []
        seen_dates: set[str] = set()

        for item in forecast_payload.get("list", []):
            try:
                timestamp = format_unix_timestamp(int(item["dt"]), tz_offset)
                description = str(item["weather"][0]["description"]).title()
                temperature = float(item["main"]["temp"])
            except (KeyError, IndexError, TypeError, ValueError):
                continue

            date_key = timestamp.split(" ")[0]
            if date_key in seen_dates:
                continue
            seen_dates.add(date_key)
            entries.append(
                ForecastEntry(
                    timestamp=timestamp,
                    description=description,
                    temperature=temperature,
                )
            )
            if len(entries) == 5:
                break
        return entries

    def _normalize_units(self, units: str) -> str:
        normalized = units.lower()
        if normalized not in VALID_UNITS:
            raise WeatherServiceError(
                f"Unsupported units '{units}'. Choose from metric, imperial, standard."
            )
        return normalized

    def _normalize_display_units(
        self, display_units: Iterable[str] | None, primary_units: str
    ) -> list[str] | None:
        if not display_units:
            return None
        normalized: list[str] = []
        for unit in display_units:
            normalized_unit = self._normalize_units(unit)
            if normalized_unit not in normalized and normalized_unit != primary_units:
                normalized.append(normalized_unit)
        return normalized or None

    def _cache_key(
        self, location: ResolvedLocation, units: str, include_forecast: bool
    ) -> str:
        return (
            f"{location.lat:.4f},{location.lon:.4f}|{units}|forecast={include_forecast}"
        )

    def _resolve_location(self, location: str) -> ResolvedLocation:
        coordinate_candidate = self._try_parse_coordinates(location)
        if coordinate_candidate:
            return coordinate_candidate

        cache_key = f"geo::{location.lower()}"
        if self.use_cache and self._cache:
            cached = self._cache.get(cache_key, max(self.cache_ttl, 3600))
            if cached:
                return ResolvedLocation(**cached)

        params = {
            "q": location,
            "limit": 1,
            "appid": self._resolve_api_key(),
        }
        logging.debug("GEOCODE %s params=%s", GEOCODE_URL, {**params, "appid": "***"})
        try:
            response = self._session.get(GEOCODE_URL, params=params, timeout=10)
            response.raise_for_status()
            payload = response.json()
        except requests.RequestException as exc:
            raise WeatherServiceError(f"Failed to geocode '{location}': {exc}") from exc
        except ValueError as exc:
            raise WeatherServiceError("Invalid geocoding response received.") from exc

        if not isinstance(payload, list) or not payload:
            raise WeatherServiceError(f"No geocoding results found for '{location}'.")

        entry = payload[0]
        try:
            resolved = ResolvedLocation(
                query=location,
                name=str(entry.get("name") or location),
                lat=float(entry["lat"]),
                lon=float(entry["lon"]),
                country=entry.get("country"),
                state=entry.get("state"),
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise WeatherServiceError(
                "Geocoding response missing required fields."
            ) from exc

        if self.use_cache and self._cache:
            self._cache.set(cache_key, asdict(resolved))
        return resolved

    def _try_parse_coordinates(self, location: str) -> ResolvedLocation | None:
        parts = [item.strip() for item in location.split(",")]
        if len(parts) != 2:
            return None
        try:
            lat = float(parts[0])
            lon = float(parts[1])
        except ValueError:
            return None
        name = f"{lat:.4f},{lon:.4f}"
        return ResolvedLocation(
            query=location,
            name=name,
            lat=lat,
            lon=lon,
        )

    def _resolve_api_key(self) -> str:
        api_key = (
            self._api_key
            or os.getenv("WEATHER_API_KEY")
            or os.getenv("OPENWEATHER_API_KEY")
        )
        if not api_key:
            raise WeatherServiceError(
                "An API key is required. Provide via --api-key or set WEATHER_API_KEY environment variable."
            )
        return api_key

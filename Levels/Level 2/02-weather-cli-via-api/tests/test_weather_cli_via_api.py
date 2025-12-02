from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

import pytest
import requests

from weather_cli_via_api.core import WeatherClient, WeatherServiceError
from weather_cli_via_api.main import main as cli_main
from weather_cli_via_api.rendering import render_report
from weather_cli_via_api.utils import temperature_unit_label, wind_speed_unit_label


class FakeResponse:
    def __init__(self, payload: Any, status_code: int = 200) -> None:
        self._payload = payload
        self.status_code = status_code

    def json(self) -> Any:
        return self._payload

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise requests.HTTPError(f"status={self.status_code}")


class FakeSession:
    def __init__(self, responses: dict[str, Iterable[tuple[Any, int]]]) -> None:
        self.responses = {key: list(value) for key, value in responses.items()}
        self.calls: list[str] = []

    def get(self, url: str, params: dict[str, Any], timeout: int) -> FakeResponse:
        endpoint = url.rstrip("/").split("/")[-1]
        self.calls.append(endpoint)
        queue = self.responses.get(endpoint, [])
        if not queue:
            raise AssertionError(f"No fake response defined for endpoint '{endpoint}'")
        payload, status = queue.pop(0)
        return FakeResponse(payload, status)


def make_geocode_payload(
    name: str,
    *,
    lat: float,
    lon: float,
    country: str = "GB",
    state: str | None = None,
) -> list[dict[str, Any]]:
    return [
        {
            "name": name,
            "lat": lat,
            "lon": lon,
            "country": country,
            "state": state,
        }
    ]


def make_current_payload(overrides: dict[str, Any] | None = None) -> dict[str, Any]:
    base = {
        "cod": 200,
        "name": "London",
        "timezone": 0,
        "weather": [{"description": "light rain"}],
        "main": {"temp": 12.5, "feels_like": 11.0, "humidity": 82},
        "sys": {"country": "GB", "sunrise": 1_700_000_000, "sunset": 1_700_036_000},
        "wind": {"speed": 3.6},
    }
    if overrides:
        base.update(overrides)
    return base


def make_forecast_payload(days: int = 5, *, tz_offset: int = 0) -> dict[str, Any]:
    items = []
    base_timestamp = 1_700_000_000
    for index in range(days * 2):
        day_offset = index // 2
        timestamp = base_timestamp + (day_offset * 86_400) + (index % 2) * 14_400
        items.append(
            {
                "dt": timestamp,
                "weather": [{"description": f"day {day_offset} clouds"}],
                "main": {"temp": 10.0 + day_offset},
            }
        )
    return {"cod": "200", "city": {"timezone": tz_offset}, "list": items}


def build_client(
    *,
    api_key: str | None = "token",
    use_cache: bool = False,
    cache_path: Path | None = None,
    responses: dict[str, Iterable[tuple[Any, int]]] | None = None,
) -> WeatherClient:
    session = FakeSession(responses or {})
    return WeatherClient(
        api_key=api_key,
        use_cache=use_cache,
        cache_ttl=600,
        cache_path=str(cache_path) if cache_path else None,
        session=session,
    )


def test_get_weather_formats_report_with_forecast_and_conversions(
    tmp_path: Path,
) -> None:
    responses = {
        "direct": [(make_geocode_payload("London", lat=51.5074, lon=-0.1278), 200)],
        "weather": [(make_current_payload(), 200)],
        "forecast": [(make_forecast_payload(), 200)],
    }
    client = build_client(
        use_cache=False, cache_path=tmp_path / "cache.json", responses=responses
    )

    report = client.get_weather(
        "London",
        units="metric",
        include_forecast=True,
        display_units=["imperial", "standard"],
    )

    assert "Location: London, GB" in report
    assert "Forecast:" in report
    assert temperature_unit_label("metric") in report
    assert wind_speed_unit_label("metric") in report
    assert "Conversions:" in report
    assert "Imperial" in report
    assert "Standard" in report


def test_get_weather_rejects_invalid_units(tmp_path: Path) -> None:
    client = build_client(
        use_cache=False, cache_path=tmp_path / "cache.json", responses={}
    )

    with pytest.raises(WeatherServiceError):
        client.get_weather("51.5074,-0.1278", units="bogus")


def test_get_weather_requires_api_key(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.delenv("WEATHER_API_KEY", raising=False)
    monkeypatch.delenv("OPENWEATHER_API_KEY", raising=False)
    client = build_client(
        api_key=None, use_cache=False, cache_path=tmp_path / "cache.json", responses={}
    )

    with pytest.raises(WeatherServiceError):
        client.get_weather("51.5074,-0.1278")


def test_get_weather_uses_cache_when_available(tmp_path: Path) -> None:
    cache_file = tmp_path / "cache.json"
    priming_responses = {
        "weather": [
            (
                make_current_payload(
                    {
                        "name": "Paris",
                        "sys": {
                            "country": "FR",
                            "sunrise": 1_700_000_000,
                            "sunset": 1_700_036_000,
                        },
                    }
                ),
                200,
            )
        ],
        "forecast": [(make_forecast_payload(), 200)],
    }
    priming_client = build_client(
        use_cache=True, cache_path=cache_file, responses=priming_responses
    )
    priming_client.get_weather("48.8566,2.3522", include_forecast=True)

    class NoCallSession:
        def get(self, *args: Any, **kwargs: Any) -> None:
            raise AssertionError(
                "Network call should not be executed when cache is valid"
            )

    cached_client = WeatherClient(
        api_key="token",
        use_cache=True,
        cache_ttl=600,
        cache_path=str(cache_file),
        session=NoCallSession(),  # type: ignore[arg-type]
    )

    report = cached_client.get_weather("48.8566,2.3522", include_forecast=True)
    assert "Paris, FR" in report


def test_cache_entry_expires_when_ttl_elapsed(tmp_path: Path) -> None:
    cache_file = tmp_path / "cache.json"
    prime_responses = {
        "weather": [
            (
                make_current_payload(
                    {
                        "name": "Roma",
                        "sys": {
                            "country": "IT",
                            "sunrise": 1_700_000_000,
                            "sunset": 1_700_036_000,
                        },
                        "timezone": 0,
                    }
                ),
                200,
            )
        ]
    }
    client = build_client(
        use_cache=True, cache_path=cache_file, responses=prime_responses
    )
    client.get_weather("41.9028,12.4964")

    cache_data = json.loads(cache_file.read_text())
    for item in cache_data.values():
        item["timestamp"] = 0
    cache_file.write_text(json.dumps(cache_data))

    fresh_responses = {
        "weather": [
            (
                make_current_payload(
                    {
                        "name": "Rome",
                        "sys": {
                            "country": "IT",
                            "sunrise": 1_700_000_000,
                            "sunset": 1_700_036_000,
                        },
                        "timezone": 0,
                    }
                ),
                200,
            )
        ]
    }
    fresh_client = build_client(
        use_cache=True, cache_path=cache_file, responses=fresh_responses
    )
    fresh_client.cache_ttl = 10

    report = fresh_client.get_weather("41.9028,12.4964")
    assert "Rome, IT" in report


def test_get_weather_raises_on_api_error(tmp_path: Path) -> None:
    responses = {
        "weather": [({"cod": 401, "message": "Invalid API key"}, 401)],
    }
    client = build_client(
        use_cache=False, cache_path=tmp_path / "cache.json", responses=responses
    )

    with pytest.raises(WeatherServiceError):
        client.get_weather("40.4168,-3.7038")


def test_forecast_is_limited_to_five_entries(tmp_path: Path) -> None:
    responses = {
        "weather": [(make_current_payload(), 200)],
        "forecast": [(make_forecast_payload(days=10), 200)],
    }
    client = build_client(
        use_cache=False, cache_path=tmp_path / "cache.json", responses=responses
    )

    report = client.get_weather("38.7223,-9.1393", include_forecast=True)
    assert report.count("  - ") == 5


def test_geocoding_failure_raises(tmp_path: Path) -> None:
    responses = {"direct": [([], 200)]}
    client = build_client(
        use_cache=False, cache_path=tmp_path / "cache.json", responses=responses
    )

    with pytest.raises(WeatherServiceError):
        client.get_weather("Unknown City")


def test_main_returns_error_code_on_failure(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    caplog: pytest.LogCaptureFixture,
) -> None:
    class FailingClient:
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            pass

        def get_weather(self, *args: Any, **kwargs: Any) -> str:
            raise WeatherServiceError("boom")

    monkeypatch.setenv("WEATHER_API_KEY", "token")
    monkeypatch.setattr("weather_cli_via_api.main.WeatherClient", FailingClient)

    exit_code = cli_main(["Rome", "--no-use-cache", "--format", "simple"])

    assert exit_code == 1
    assert "boom" in caplog.text
    captured = capsys.readouterr()
    assert "Error for Rome: boom" in captured.out


def test_main_prints_multiple_reports(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    class SuccessClient:
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            pass

        def get_weather(self, location: str, format_mode: str = "simple", **_: Any) -> str | WeatherReport:
            if format_mode == "simple":
                return f"report for {location}"
            else:
                # Return a mock WeatherReport for non-simple modes
                from weather_cli_via_api.core import WeatherReport
                return WeatherReport(
                    location=location,
                    description="Test",
                    temperature=20.0,
                    feels_like=18.0,
                    humidity=50,
                    wind_speed=5.0,
                    sunrise="08:00",
                    sunset="18:00",
                    units="metric"
                )

    monkeypatch.setenv("WEATHER_API_KEY", "token")
    monkeypatch.setattr("weather_cli_via_api.main.WeatherClient", SuccessClient)

    exit_code = cli_main(["Berlin", "Paris", "--display-units", "metric", "--format", "simple"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "report for Berlin" in captured.out
    assert "report for Paris" in captured.out
    assert captured.out.count("report for") == 2


def test_render_report_rich_format(tmp_path: Path) -> None:
    responses = {
        "direct": [(make_geocode_payload("London", lat=51.5074, lon=-0.1278), 200)],
        "weather": [(make_current_payload(), 200)],
        "forecast": [(make_forecast_payload(), 200)],
    }
    client = build_client(
        use_cache=False, cache_path=tmp_path / "cache.json", responses=responses
    )

    report = client.get_weather(
        "London",
        units="metric",
        include_forecast=True,
        display_units=["imperial"],
        format_mode="rich",
    )

    rendered = render_report(report, "rich")

    # Check that rich formatting elements are present
    assert "Weather for London" in rendered
    assert "Condition" in rendered
    assert "Temperature" in rendered
    assert "5-Day Forecast" in rendered
    assert "Unit Conversions" in rendered
    assert "Light Rain" in rendered
    assert "12.5°C" in rendered


def test_render_report_json_format(tmp_path: Path) -> None:
    responses = {
        "direct": [(make_geocode_payload("London", lat=51.5074, lon=-0.1278), 200)],
        "weather": [(make_current_payload(), 200)],
        "forecast": [(make_forecast_payload(), 200)],
    }
    client = build_client(
        use_cache=False, cache_path=tmp_path / "cache.json", responses=responses
    )

    report = client.get_weather(
        "London",
        units="metric",
        include_forecast=True,
        display_units=["imperial"],
        format_mode="json",
    )

    rendered = render_report(report, "json")

    # Parse as JSON to verify it's valid
    import json
    data = json.loads(rendered)

    assert data["location"] == "London, GB"
    assert data["temperature"] == 12.5
    assert data["description"] == "Light Rain"
    assert "forecast" in data
    assert len(data["forecast"]) == 5
    assert "conversions" in data
    assert len(data["conversions"]) == 1
    assert data["conversions"][0]["unit"] == "imperial"


def test_main_with_json_format(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    class SuccessClient:
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            pass

        def get_weather(self, location: str, format_mode: str = "simple", **_: Any) -> str | WeatherReport:
            if format_mode == "simple":
                return f"report for {location}"
            else:
                # Return a mock WeatherReport for non-simple modes
                from weather_cli_via_api.core import WeatherReport
                return WeatherReport(
                    location=location,
                    description="Test",
                    temperature=20.0,
                    feels_like=18.0,
                    humidity=50,
                    wind_speed=5.0,
                    sunrise="08:00",
                    sunset="18:00",
                    units="metric"
                )

    monkeypatch.setenv("WEATHER_API_KEY", "token")
    monkeypatch.setattr("weather_cli_via_api.main.WeatherClient", SuccessClient)

    exit_code = cli_main(["Berlin", "--format", "json"])

    captured = capsys.readouterr()
    assert exit_code == 0

    # Should be valid JSON
    import json
    data = json.loads(captured.out)
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["location"] == "Berlin"


def test_main_with_rich_format(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    class SuccessClient:
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            pass

        def get_weather(self, location: str, format_mode: str = "simple", **_: Any) -> str | WeatherReport:
            if format_mode == "simple":
                return f"report for {location}"
            else:
                # Return a mock WeatherReport for non-simple modes
                from weather_cli_via_api.core import WeatherReport
                return WeatherReport(
                    location=location,
                    description="Test",
                    temperature=20.0,
                    feels_like=18.0,
                    humidity=50,
                    wind_speed=5.0,
                    sunrise="08:00",
                    sunset="18:00",
                    units="metric"
                )

    monkeypatch.setenv("WEATHER_API_KEY", "token")
    monkeypatch.setattr("weather_cli_via_api.main.WeatherClient", SuccessClient)

    exit_code = cli_main(["Berlin", "--format", "rich"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Weather for Berlin" in captured.out

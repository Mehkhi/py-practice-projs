## Weather CLI via API

Command-line utility for fetching current weather conditions (and optional 5-day forecasts) from the OpenWeatherMap API. It highlights robust error handling, response caching, and a clean interface suitable for everyday use.

- Uses `requests` to call OpenWeatherMap's current and forecast endpoints
- Caches JSON responses locally to minimize redundant API calls
- Resolves place names through OpenWeatherMap geocoding and accepts raw coordinates
- Presents readable reports with temperatures, humidity, wind, and sunrise/sunset times
- Optional forecast summaries extracted from the 5-day / 3-hour feed
- Supports multiple locations in one invocation
- Adds optional temperature and wind conversions across metric, imperial, and Kelvin units
- Logs important events and surfaces actionable error messages

### Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Configuration

- Provide an API key via the `--api-key` flag or the `WEATHER_API_KEY` (fallback `OPENWEATHER_API_KEY`) environment variable.
- Choose output units with `--units {metric,imperial,standard}`. Defaults to metric.
- Add converted temperatures and wind speeds with `--display-units ...` (values from the same set as `--units`).
- Toggle caching with `--use-cache/--no-use-cache` and change the TTL using `--cache-ttl` (seconds).
- Override the cache file location with `--cache-path PATH`.
- Show a daily forecast summary with `--forecast`.
- Choose output format with `--format {simple,rich,json}`. Defaults to rich.

### Usage

```bash
# Current conditions with caching enabled (rich format by default)
python -m weather_cli_via_api "Paris,FR" --units metric

# Simple text format output
python -m weather_cli_via_api "Paris,FR" --format simple

# JSON format output for programmatic use
python -m weather_cli_via_api "Paris,FR" --format json

# Fetch two cities at once with converted outputs and forecast summaries
python -m weather_cli_via_api "Seattle,US" "London,UK" \
  --forecast --display-units imperial standard

# Provide raw coordinates and custom cache location
python -m weather_cli_via_api "47.6062,-122.3321" --cache-path ~/.weather_cache.json
```

Sample output:

**Simple format:**
```
Location: Seattle, US
Condition: Light Rain
Temperature: 9.2°C (feels like 6.5°C)
Humidity: 87%
Wind: 4.8 m/s
Sunrise: 2023-11-16 07:11
Sunset: 2023-11-16 16:27
Forecast:
  - 2023-11-17 12:00: Broken Clouds at 10.8°C
  - 2023-11-18 12:00: Light Rain at 11.2°C
  - 2023-11-19 12:00: Overcast Clouds at 10.5°C
  - 2023-11-20 12:00: Broken Clouds at 9.8°C
  - 2023-11-21 12:00: Light Rain at 8.9°C
```

**Rich format:** (default - displays colorful tables with borders)

**JSON format:**
```json
[
  {
    "location": "Seattle, US",
    "description": "Light Rain",
    "temperature": 9.2,
    "feels_like": 6.5,
    "humidity": 87,
    "wind_speed": 4.8,
    "sunrise": "2023-11-16 07:11",
    "sunset": "2023-11-16 16:27",
    "units": "metric",
    "forecast": [
      {
        "timestamp": "2023-11-17 12:00",
        "description": "Broken Clouds",
        "temperature": 10.8
      }
    ]
  }
]
```

### Development

- Run tests with `python3 -m pytest`.
- The test suite mocks network calls; no external traffic is generated.
- Code is type hinted and documented; run `ruff` or similar linters as desired.

### Known Limitations

- Requires a valid OpenWeatherMap API key (free tier works well).
- Geocoding picks the first matching location returned by the API; ambiguous names may need coordinates.
- Forecast summaries retain the first available time block per day rather than hourly granularity.
- Caching is file-based; remove the cache file to flush stored responses manually.

"""Command-line entry point for the weather CLI."""

from __future__ import annotations

import argparse
import json
import logging

from .core import WeatherClient, WeatherReport, WeatherServiceError
from .rendering import render_error, render_report


def _build_parser() -> argparse.ArgumentParser:
    """Create the CLI argument parser."""
    parser = argparse.ArgumentParser(
        description="Fetch current weather conditions from a weather API."
    )
    parser.add_argument(
        "locations",
        nargs="+",
        metavar="location",
        help="One or more location queries (e.g. 'London,UK' or ZIP code).",
    )
    parser.add_argument(
        "-u",
        "--units",
        default="metric",
        choices=["metric", "imperial", "standard"],
        help="Units for temperature and wind speed.",
    )
    parser.add_argument(
        "--api-key",
        dest="api_key",
        help="API key for the weather service (overrides env var).",
    )
    parser.add_argument(
        "--use-cache",
        dest="use_cache",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Enable or disable response caching.",
    )
    parser.add_argument(
        "--cache-ttl",
        dest="cache_ttl",
        type=int,
        default=600,
        help="Cache time-to-live in seconds (default: 600).",
    )
    parser.add_argument(
        "--cache-path",
        dest="cache_path",
        help="Optional path to store cached responses.",
    )
    parser.add_argument(
        "--forecast",
        action="store_true",
        help="Include a short 5-day / 3-hour interval forecast if available.",
    )
    parser.add_argument(
        "--display-units",
        nargs="+",
        choices=["metric", "imperial", "standard"],
        help="Also display converted values in the provided units.",
    )
    parser.add_argument(
        "--format",
        dest="format_mode",
        default="rich",
        choices=["simple", "rich", "json"],
        help="Output format (default: rich).",
    )
    parser.add_argument(
        "-v", "--verbose", action="count", default=0, help="Increase output verbosity."
    )
    return parser


def _configure_logging(verbosity: int) -> None:
    """Configure logging based on verbosity level."""
    level = logging.WARNING
    if verbosity == 1:
        level = logging.INFO
    elif verbosity >= 2:
        level = logging.DEBUG
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")


def main(argv: list[str] | None = None) -> int:
    """Run the CLI."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    _configure_logging(args.verbose)

    try:
        client = WeatherClient(
            api_key=args.api_key,
            use_cache=args.use_cache,
            cache_ttl=args.cache_ttl,
            cache_path=args.cache_path,
        )

        reports = []
        has_errors = False
        for location in args.locations:
            try:
                report_data = client.get_weather(
                    location,
                    units=args.units,
                    include_forecast=args.forecast,
                    display_units=args.display_units,
                    format_mode=args.format_mode,
                )

                if args.format_mode == "simple":
                    reports.append(str(report_data))
                else:
                    reports.append(render_report(report_data, args.format_mode))
            except WeatherServiceError as exc:
                has_errors = True
                error_msg = render_error(str(exc), args.format_mode)
                if args.format_mode == "json":
                    reports.append(error_msg)
                else:
                    logging.error("%s", exc)
                    if args.format_mode == "rich":
                        reports.append(error_msg)
                    else:
                        reports.append(f"Error for {location}: {exc}")

        if args.format_mode == "json":
            # For JSON mode, output as a JSON array
            json_reports = []
            for report in reports:
                try:
                    json_reports.append(json.loads(report))
                except json.JSONDecodeError:
                    json_reports.append({"error": report})
            print(json.dumps(json_reports, indent=2))
        else:
            print("\n\n".join(reports))
        return 1 if has_errors else 0

    except WeatherServiceError as exc:
        error_msg = render_error(str(exc), args.format_mode)
        if args.format_mode == "json":
            print(error_msg)
        else:
            logging.error("%s", exc)
            if args.format_mode == "rich":
                print(error_msg)
            else:
                print(f"Error: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

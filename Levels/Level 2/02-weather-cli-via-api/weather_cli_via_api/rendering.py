"""Rich rendering helpers for the weather CLI."""

from __future__ import annotations

import json
from typing import Any

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text
    from rich.box import ROUNDED
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

from .core import WeatherReport
from .utils import temperature_unit_label, wind_speed_unit_label


def render_report(report: WeatherReport, format_mode: str) -> str:
    """Render a weather report in the specified format."""
    if format_mode == "json":
        return json.dumps(report.to_dict(), indent=2)
    elif format_mode == "rich" and RICH_AVAILABLE:
        console = Console()
        with console.capture() as capture:
            _render_rich_report(console, report)
        return capture.get()
    else:
        return report.to_text()


def _render_rich_report(console: Console, report: WeatherReport) -> None:
    """Render a weather report using rich formatting."""
    temp_unit = temperature_unit_label(report.units)
    wind_unit = wind_speed_unit_label(report.units)

    # Current weather table
    current_table = Table(title=f"Weather for {report.location}", box=ROUNDED)
    current_table.add_column("Metric", style="cyan", no_wrap=True)
    current_table.add_column("Value", style="white")

    current_table.add_row("Condition", Text(report.description, style="yellow"))
    current_table.add_row(
        "Temperature",
        f"{report.temperature:.1f}{temp_unit} (feels like {report.feels_like:.1f}{temp_unit})"
    )
    current_table.add_row("Humidity", f"{report.humidity}%")
    current_table.add_row("Wind", f"{report.wind_speed:.1f} {wind_unit}")
    current_table.add_row("Sunrise", report.sunrise)
    current_table.add_row("Sunset", report.sunset)

    console.print(Panel(current_table, box=ROUNDED))

    # Forecast table
    if report.forecast:
        forecast_table = Table(title="5-Day Forecast", box=ROUNDED)
        forecast_table.add_column("Date", style="cyan", no_wrap=True)
        forecast_table.add_column("Description", style="yellow")
        forecast_table.add_column("Temperature", style="white")

        for entry in report.forecast:
            date = entry.timestamp.split(" ")[0]
            forecast_table.add_row(
                date,
                entry.description,
                f"{entry.temperature:.1f}{temp_unit}"
            )

        console.print(Panel(forecast_table, box=ROUNDED))

    # Conversions table
    if report.display_units:
        conversions_table = Table(title="Unit Conversions", box=ROUNDED)
        conversions_table.add_column("Unit System", style="cyan", no_wrap=True)
        conversions_table.add_column("Temperature", style="white")
        conversions_table.add_column("Feels Like", style="white")
        conversions_table.add_column("Wind Speed", style="white")

        for conversion in report.to_dict().get("conversions", []):
            conversions_table.add_row(
                conversion["unit"].title(),
                f"{conversion['temperature']:.1f}{conversion['temperature_unit']}",
                f"{conversion['feels_like']:.1f}{conversion['temperature_unit']}",
                f"{conversion['wind_speed']:.1f} {conversion['wind_unit']}"
            )

        console.print(Panel(conversions_table, box=ROUNDED))


def render_error(message: str, format_mode: str) -> str:
    """Render an error message in the specified format."""
    if format_mode == "json":
        return json.dumps({"error": message}, indent=2)
    elif format_mode == "rich" and RICH_AVAILABLE:
        console = Console()
        with console.capture() as capture:
            console.print(Panel(Text(message, style="red"), title="Error", box=ROUNDED))
        return capture.get()
    else:
        return f"Error: {message}"

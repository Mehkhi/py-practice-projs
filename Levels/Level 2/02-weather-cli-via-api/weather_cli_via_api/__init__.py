"""Weather CLI package initialization."""

from __future__ import annotations

from .core import WeatherClient, WeatherServiceError

__all__ = ["__version__", "WeatherClient", "WeatherServiceError"]

__version__ = "0.1.0"

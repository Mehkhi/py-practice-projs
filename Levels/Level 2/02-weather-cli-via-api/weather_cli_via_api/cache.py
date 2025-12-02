"""Simple JSON file-based cache for API responses."""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Any

DEFAULT_CACHE_NAME = "weather_cli_cache.json"


def _default_cache_path() -> Path:
    """Return the default cache file path."""
    base = Path.home() / ".cache"
    if not base.exists():
        try:
            base.mkdir(parents=True, exist_ok=True)
        except OSError:
            logging.debug("Falling back to home directory for cache storage")
            return Path.home() / DEFAULT_CACHE_NAME
    return base / DEFAULT_CACHE_NAME


class ResponseCache:
    """JSON-backed cache for storing API responses."""

    def __init__(self, cache_path: Path | None = None) -> None:
        self.cache_path = cache_path or _default_cache_path()

    def _read_cache(self) -> dict[str, Any]:
        if not self.cache_path.exists():
            return {}
        try:
            raw = self.cache_path.read_text(encoding="utf-8")
            return json.loads(raw) if raw else {}
        except (OSError, json.JSONDecodeError):
            logging.debug("Cache file is unreadable; starting with empty cache")
            return {}

    def _write_cache(self, data: dict[str, Any]) -> None:
        try:
            self.cache_path.parent.mkdir(parents=True, exist_ok=True)
            self.cache_path.write_text(json.dumps(data), encoding="utf-8")
        except OSError as exc:
            logging.debug("Unable to persist cache: %s", exc)

    def get(self, key: str, max_age: int) -> Any | None:
        """Retrieve cached data if it is still fresh."""
        cache = self._read_cache()
        entry = cache.get(key)
        if not entry:
            return None
        if int(time.time()) - int(entry.get("timestamp", 0)) > max_age:
            logging.debug("Cache entry for %s expired", key)
            return None
        return entry.get("value")

    def set(self, key: str, value: Any) -> None:
        """Store a value in the cache."""
        cache = self._read_cache()
        cache[key] = {"timestamp": int(time.time()), "value": value}
        self._write_cache(cache)

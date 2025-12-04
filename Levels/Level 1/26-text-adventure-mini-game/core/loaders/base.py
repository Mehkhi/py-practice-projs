"""
Shared utilities for loader modules.

Loaders default to a tolerant schema policy: they log and skip malformed data
while still returning usable defaults. Set the environment variable
``STRICT_SCHEMA=1`` to raise ``ValueError`` instead when schema issues are
encountered.
"""

import copy
import json
import os
from dataclasses import dataclass
from typing import Any, Dict, Mapping, MutableMapping, Optional, Sequence, Tuple

from core.logging_utils import (
    format_schema_message,
    log_debug,
    log_schema_warning,
    log_warning,
)

STRICT_SCHEMA = os.environ.get("STRICT_SCHEMA", "").lower() in {"1", "true", "yes", "on"}


@dataclass
class _JsonCacheEntry:
    """Cached JSON payload keyed by absolute path."""

    mtime: Optional[float]
    data: Any


@dataclass
class _LookupCacheEntry:
    """Cached section lookups keyed by (path, section, key_field)."""

    mtime: Optional[float]
    lookup: Dict[str, Any]


_JSON_CACHE: Dict[str, _JsonCacheEntry] = {}
_LOOKUP_CACHE: Dict[Tuple[str, str, str], _LookupCacheEntry] = {}


def _canonical_path(path: str) -> str:
    """Normalize paths to keep cache keys consistent."""
    return os.path.abspath(path)


def _safe_get_mtime(path: str) -> Optional[float]:
    """Return file mtime or None when missing/inaccessible."""
    try:
        return os.path.getmtime(path)
    except OSError:
        return None


def _copy_data(data: Any) -> Any:
    """Defensive deep copy for cache outputs."""
    try:
        return copy.deepcopy(data)
    except Exception:  # pragma: no cover  # deepcopy should work for JSON-compatible data
        return data


def detach_json_data(data: Any) -> Any:
    """
    Deep-copy JSON-derived data to break references to cached payloads.

    Useful for loaders that opt out of load_json_file(copy_data=True) but still
    need to hand mutable structures to gameplay objects without mutating the
    shared cache.
    """
    return _copy_data(data)


def _invalidate_lookups_for(path: str) -> None:
    """Drop lookup caches tied to a JSON path."""
    stale_keys = [key for key in _LOOKUP_CACHE if key[0] == path]
    for key in stale_keys:
        _LOOKUP_CACHE.pop(key, None)


def clear_json_cache(path: Optional[str] = None) -> None:
    """
    Clear cached JSON payloads and derived lookups.

    Args:
        path: Optional path to clear. Clears all entries when None.
    """
    if path is None:
        _JSON_CACHE.clear()
        _LOOKUP_CACHE.clear()
        return

    canonical = _canonical_path(path)
    _JSON_CACHE.pop(canonical, None)
    _invalidate_lookups_for(canonical)


def load_json_file(
    path: str,
    default: Any = None,
    context: Optional[str] = None,
    warn_on_missing: bool = False,
    *,
    use_cache: bool = True,
    force_reload: bool = False,
    copy_data: bool = True,
) -> Any:
    """
    Load a JSON file with standardized error handling and caching.

    Args:
        path: Path to JSON file
        default: Default value to return on failure (defaults to {})
        context: Optional context string for more descriptive log messages
            (e.g., "Loading quest data" or "items")
        warn_on_missing: If True, log a warning when file is missing.
            If False, only log at debug level.
        use_cache: When True, reuse cached payloads keyed by file path/mtime.
        force_reload: Skip cache and re-read from disk even if cached.
        copy_data: Return a deep copy of cached data to prevent accidental
            mutation of the cached payload.

    Returns:
        Parsed JSON data (deep-copied by default), or default value on failure.
        Note: JSON can be any type (dict, list, etc.) depending on file contents.
    """
    if default is None:
        default = {}

    canonical_path = _canonical_path(path)
    mtime = _safe_get_mtime(canonical_path)

    if force_reload and use_cache:
        _JSON_CACHE.pop(canonical_path, None)
        _invalidate_lookups_for(canonical_path)

    if use_cache and not force_reload and mtime is not None:
        cached = _JSON_CACHE.get(canonical_path)
        if cached and cached.mtime == mtime:
            return _copy_data(cached.data) if copy_data else cached.data
        if cached:
            _JSON_CACHE.pop(canonical_path, None)
            _invalidate_lookups_for(canonical_path)

    if mtime is None:
        if warn_on_missing:
            msg = f"File not found at {canonical_path}"
            if context:
                msg = f"{context}: {msg}"
            log_warning(msg)
        else:
            log_debug(f"JSON file not found at {canonical_path}, using default")
        return _copy_data(default) if copy_data else default

    try:
        with open(canonical_path, "r") as file_handle:
            data = json.load(file_handle)
    except Exception as exc:  # pylint: disable=broad-except
        msg = f"Failed to load JSON file from {canonical_path}: {exc}"
        if context:
            msg = f"{context}: {msg}"
        log_warning(msg)
        _JSON_CACHE.pop(canonical_path, None)
        _invalidate_lookups_for(canonical_path)
        return _copy_data(default) if copy_data else default

    if use_cache:
        _JSON_CACHE[canonical_path] = _JsonCacheEntry(mtime=mtime, data=data)

    return _copy_data(data) if copy_data else data


def _build_lookup(data: Any, section: str, key_field: str) -> Dict[str, Any]:
    """Create an id->entry mapping from a section of JSON data."""
    if not isinstance(data, Mapping):
        return {}

    section_data = data.get(section, {})
    if isinstance(section_data, Mapping):
        return {str(key): value for key, value in section_data.items()}

    if isinstance(section_data, list):
        lookup: Dict[str, Any] = {}
        for entry in section_data:
            if isinstance(entry, Mapping) and key_field in entry:
                lookup[str(entry[key_field])] = entry
        return lookup

    return {}


def get_cached_lookup(
    path: str,
    section: str,
    key_field: str = "id",
    *,
    default: Any = None,
    copy_lookup: bool = True,
) -> Dict[str, Any]:
    """
    Build (and cache) an id->record mapping for a JSON section.

    Args:
        path: Path to JSON file
        section: Top-level section name to index (e.g., "achievements")
        key_field: Field name inside each entry to use as the key
        default: Default payload to use when the file is missing/unreadable
        copy_lookup: Return a deep copy of the lookup to keep the cache immutable

    Returns:
        Dict mapping ids to the original entry dictionaries.
    """
    canonical_path = _canonical_path(path)
    mtime = _safe_get_mtime(canonical_path)
    cache_key = (canonical_path, section, key_field)

    if mtime is not None:
        cached = _LOOKUP_CACHE.get(cache_key)
        if cached and cached.mtime == mtime:
            return _copy_data(cached.lookup) if copy_lookup else cached.lookup
        if cached:
            _LOOKUP_CACHE.pop(cache_key, None)

    data = load_json_file(
        canonical_path,
        default=default,
        context=f"Loading {section} lookup" if section else None,
        warn_on_missing=False,
        use_cache=True,
        copy_data=False,
    )
    lookup = _build_lookup(data, section, key_field)

    if mtime is not None:
        _LOOKUP_CACHE[cache_key] = _LookupCacheEntry(mtime=mtime, lookup=lookup)

    return _copy_data(lookup) if copy_lookup else lookup


def warm_json_cache(
    paths: Sequence[str],
    *,
    warn_on_missing: bool = False,
    lookups: Optional[Mapping[str, Sequence[Tuple[str, str]]]] = None,
) -> Dict[str, Any]:
    """
    Preload and cache JSON files (and optional lookups) for faster access.

    Args:
        paths: Iterable of file paths to preload
        warn_on_missing: Whether to warn about missing files during warmup
        lookups: Optional mapping of path -> iterable of (section, key_field)
            pairs to precompute lookup dictionaries for.

    Returns:
        Mapping of the provided paths to their loaded payloads.
    """
    warmed: Dict[str, Any] = {}
    lookup_map: Dict[str, Sequence[Tuple[str, str]]] = {}
    if lookups:
        lookup_map = {_canonical_path(k): v for k, v in lookups.items()}

    for raw_path in paths:
        data = load_json_file(
            raw_path,
            default={},
            warn_on_missing=warn_on_missing,
            use_cache=True,
            copy_data=False,
        )
        warmed[raw_path] = _copy_data(data)

        canonical = _canonical_path(raw_path)
        for section, key_field in lookup_map.get(canonical, ()):
            get_cached_lookup(
                canonical,
                section,
                key_field,
                default={},
                copy_lookup=False,
            )

    return warmed


def _handle_schema_issue(
    context: str,
    section: str,
    identifier: Optional[str],
    message: str,
) -> None:
    """Apply the global schema policy: log and continue, or raise when strict."""
    if STRICT_SCHEMA:
        raise ValueError(format_schema_message(context, message, section, identifier))
    log_schema_warning(context, message, section=section, identifier=identifier)


def ensure_dict(
    data: Any,
    *,
    context: str,
    section: str,
    identifier: Optional[str] = None,
    default: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Ensure the provided data is a dictionary.

    Returns a dictionary (or default) and logs per schema policy when the value
    is not a dict.
    """
    if isinstance(data, MutableMapping):
        return dict(data)

    fallback: Dict[str, Any] = default if default is not None else {}
    _handle_schema_issue(
        context,
        section,
        identifier,
        f"expected object/dict, got {type(data).__name__}",
    )
    return fallback


def ensure_list(
    data: Any,
    *,
    context: str,
    section: str,
    identifier: Optional[str] = None,
    default: Optional[Sequence[Any]] = None,
) -> list:
    """
    Ensure the provided data is a list.

    Returns a list (or default) and logs per schema policy when the value is
    not a list.
    """
    if isinstance(data, list):
        return data

    fallback = list(default) if default is not None else []
    _handle_schema_issue(
        context,
        section,
        identifier,
        f"expected list/array, got {type(data).__name__}",
    )
    return fallback


def validate_required_keys(
    obj: Mapping[str, Any],
    keys: Sequence[str],
    *,
    context: str,
    section: str,
    identifier: Optional[str] = None,
) -> bool:
    """Validate presence of required keys, logging once if any are missing."""
    missing = [key for key in keys if key not in obj]
    if missing:
        _handle_schema_issue(
            context,
            section,
            identifier,
            f"missing required field(s): {', '.join(missing)}",
        )
        return False
    return True

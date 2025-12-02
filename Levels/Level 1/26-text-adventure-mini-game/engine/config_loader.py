"""Configuration loading helpers with environment overrides."""

import json
import os
from typing import Any, Dict

from core.logging_utils import log_warning


def _coerce_bool(value: Any) -> bool:
    """Convert common truthy/falsey string/int forms into a bool."""
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        return value.strip().lower() in ("1", "true", "yes", "on", "debug")
    return False


def _apply_bool_setting(
    merged: Dict[str, Any],
    config_key: str,
    env_keys: tuple[str, ...],
    default: bool,
) -> None:
    """Apply a boolean setting with optional environment overrides."""
    env_value = None
    for key in env_keys:
        if key in os.environ:
            env_value = os.environ.get(key)
            break
    if env_value is not None:
        merged[config_key] = _coerce_bool(env_value)
    else:
        merged[config_key] = _coerce_bool(merged.get(config_key, default))


def apply_debug_ai_override(config: Dict[str, Any]) -> Dict[str, Any]:
    """Return a copy of config with AI-related env overrides applied."""
    merged = dict(config or {})

    _apply_bool_setting(merged, "debug_ai", ("DEBUG_AI", "AI_DEBUG"), False)
    _apply_bool_setting(
        merged,
        "ai_phase_feedback",
        ("AI_PHASE_FEEDBACK", "AI_PHASE_MESSAGES"),
        False,
    )
    _apply_bool_setting(
        merged,
        "ai_validation_enabled",
        ("AI_VALIDATION", "AI_VALIDATE_ASSETS"),
        True,
    )
    _apply_bool_setting(
        merged,
        "ai_profile_coverage_check",
        ("AI_PROFILE_COVERAGE", "AI_VALIDATE_PROFILES"),
        True,
    )

    return merged


def load_config(config_path: str = "data/config.json") -> Dict[str, Any]:
    """Load config with environment overrides applied; callers should not reapply."""
    config: Dict[str, Any] = {}
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                config = json.load(f)
        except Exception as exc:
            log_warning(f"Failed to load config from {config_path}: {exc}")

    return apply_debug_ai_override(config)

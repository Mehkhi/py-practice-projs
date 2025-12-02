"""Compatibility shim that re-exports hint types from core.

The canonical implementations now live in ``core.secret_boss_hints`` to keep
Core independent from Engine. This module remains for backward compatibility
with engine imports.
"""

from core.secret_boss_hints import BossHint, HintManager, HintType

__all__ = ["BossHint", "HintManager", "HintType"]

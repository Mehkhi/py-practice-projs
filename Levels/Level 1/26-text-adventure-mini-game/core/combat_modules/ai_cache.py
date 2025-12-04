"""Cache management utilities for AI decision-making.

This module provides cache management and bucket utilities used by the AI system
for performance optimization. Caches are used to avoid redundant computations
for phase determination, rule evaluation, and tactics availability.

Cache size limits:
    - Phase cache: 100 entries (HP bucket-based)
    - Rule cache: 200 entries (HP/SP bucket-based)
    - Tactics cache: 10 turns (per-turn availability)
"""

import hashlib
import json
from typing import Dict, Any

# Cache size limits for AI decision caches
# These can be tuned based on memory constraints and battle complexity
_PHASE_CACHE_MAX_SIZE = 100  # Max entries in phase determination cache
_RULE_CACHE_MAX_SIZE = 200   # Max entries in rule evaluation cache
_TACTICS_CACHE_MAX_TURNS = 10  # Max turns to keep in tactics cache

# HP bucket size for phase caching (5% granularity)
_HP_BUCKET_SIZE = 5
# SP bucket size for rule caching (10% granularity, coarser since SP changes less frequently)
_SP_BUCKET_SIZE = 10


class AICacheMixin:
    """Mixin providing cache management methods for AI systems.

    This mixin assumes the host class has:
    - self._phase_cache: Dict (optional, created on demand)
    - self._rule_evaluation_cache: Dict (optional, created on demand)
    - self._tactics_cache: Dict (optional, created on demand)
    - self._rule_index: Dict (optional, created on demand)
    - self._last_rule_match_cache: Dict (optional, created on demand)
    """

    def _get_phase_cache(self) -> Dict:
        """Get or create the phase determination cache."""
        if not hasattr(self, '_phase_cache'):
            self._phase_cache = {}
        return self._phase_cache

    def _get_hp_bucket(self, hp_percent: float) -> int:
        """Round HP percentage to nearest bucket for caching.

        Uses _HP_BUCKET_SIZE (default 5%) granularity. This means HP values
        within 2.5% of each other will share the same bucket.

        Args:
            hp_percent: HP percentage (0-100)

        Returns:
            Bucket value (0, 5, 10, 15, ..., 100)
        """
        return int(round(hp_percent / _HP_BUCKET_SIZE) * _HP_BUCKET_SIZE)

    def _get_sp_bucket(self, sp_percent: float) -> int:
        """Round SP percentage to nearest bucket for caching.

        Uses _SP_BUCKET_SIZE (default 10%) granularity, coarser than HP buckets
        since SP changes less frequently during combat.

        Args:
            sp_percent: SP percentage (0-100)

        Returns:
            Bucket value (0, 10, 20, 30, ..., 100)
        """
        return int(round(sp_percent / _SP_BUCKET_SIZE) * _SP_BUCKET_SIZE)

    def _get_profile_hash(self, profile: Dict[str, Any]) -> str:
        """Generate a stable hash for an AI profile dictionary.

        This method creates a content-based hash that remains stable even if
        the profile dict object is recreated (e.g., from JSON reloading).
        This ensures cache keys remain valid across profile reloads.

        Args:
            profile: AI profile dictionary to hash

        Returns:
            Hexadecimal MD5 hash string of the profile content
        """
        if not profile:
            return "0"
        content = json.dumps(profile, sort_keys=True)
        return hashlib.md5(content.encode()).hexdigest()

    def _get_rule_evaluation_cache(self) -> Dict:
        """Get or create the rule evaluation cache."""
        if not hasattr(self, '_rule_evaluation_cache'):
            self._rule_evaluation_cache = {}
        return self._rule_evaluation_cache

    def clear_ai_caches(self) -> None:
        """Clear all AI decision caches.

        Call this method when:
        - Battle state is reset
        - AI profiles are modified/reloaded
        - Starting a new battle with the same BattleSystem instance

        Note on cache key stability:
            The phase and rule caches use content-based hashes (via _get_profile_hash)
            for cache keys, ensuring stability even if profile/rule dict objects are
            recreated. This prevents stale cache entries when profiles are reloaded.
        """
        if hasattr(self, '_phase_cache'):
            self._phase_cache.clear()
        if hasattr(self, '_rule_evaluation_cache'):
            self._rule_evaluation_cache.clear()
        if hasattr(self, '_tactics_cache'):
            self._tactics_cache.clear()
        if hasattr(self, '_rule_index'):
            self._rule_index.clear()
        if hasattr(self, '_last_rule_match_cache'):
            self._last_rule_match_cache.clear()


# Export cache size constants for use by other modules
__all__ = [
    'AICacheMixin',
    '_PHASE_CACHE_MAX_SIZE',
    '_RULE_CACHE_MAX_SIZE',
    '_TACTICS_CACHE_MAX_TURNS',
    '_HP_BUCKET_SIZE',
    '_SP_BUCKET_SIZE',
]

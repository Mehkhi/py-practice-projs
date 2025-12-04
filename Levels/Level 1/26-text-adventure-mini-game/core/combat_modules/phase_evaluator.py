"""Phase evaluation and state management for multi-phase AI.

This module provides phase determination and state tracking for enemies with
multi-phase AI profiles. Phases are defined by HP thresholds and allow enemies
to change behavior as their HP decreases.

Phase selection logic:
    - Phases are sorted by threshold descending (highest first)
    - First phase where current HP >= threshold is selected
    - If no phase matches, lowest threshold phase is used
    - Phase changes trigger feedback messages for bosses/alpha enemies

Performance optimization:
    - Results are cached based on HP percentage buckets (5% granularity)
    - Cache key includes enemy ID, HP bucket, and profile object identity
    - Cache uses FIFO eviction when size exceeds limit
"""

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

if TYPE_CHECKING:
    from core.combat import BattleParticipant

from .ai_cache import AICacheMixin, _PHASE_CACHE_MAX_SIZE


class PhaseEvaluatorMixin(AICacheMixin):
    """Mixin providing phase evaluation methods for AI systems.

    This mixin assumes the host class has:
    - self.enemies: List[BattleParticipant]
    - self.turn_counter: int
    - self.debug_ai: bool
    - self.phase_feedback: bool
    - self.message_log: List[str]
    - self._hp_percent(participant) -> float
    - self._get_hp_bucket(hp_percent) -> int
    - self._get_phase_cache() -> Dict
    """

    def _determine_phase(
        self,
        enemy: "BattleParticipant"
    ) -> Tuple[List[Dict[str, Any]], str, Optional[int], bool]:
        """Determine the current phase for an enemy based on HP thresholds.

        This method analyzes the enemy's AI profile to determine which phase
        rules should be active. Phases are defined by HP thresholds (minimum HP
        percentage required to be in that phase).

        Phase selection logic:
        - Phases are sorted by threshold descending (highest first)
        - First phase where current HP >= threshold is selected
        - If no phase matches, lowest threshold phase is used
        - If no phases defined, returns default rules

        Performance optimization:
        - Results are cached based on HP percentage buckets (5% granularity)
        - Cache key includes enemy ID, HP bucket, and profile content hash
        - Cache uses FIFO eviction when size exceeds _PHASE_CACHE_MAX_SIZE

        Cache key stability note:
            The cache uses content-based hashing (via _get_profile_hash) for
            cache keys, ensuring stability even if profile dict objects are
            recreated. This prevents stale entries when profiles are reloaded.

        Args:
            enemy: The enemy participant to determine phase for

        Returns:
            Tuple of:
            - rules: List of rules for the current phase
            - name: Phase name (e.g., "aggressive", "desperate")
            - threshold: HP threshold for this phase (None if no phases)
            - has_phases: True if multi-phase structure exists

        Example:
            If enemy has 60% HP and phases at 50% and 25%:
            - Returns phase at 50% threshold (highest applicable)
            If enemy has 20% HP:
            - Returns phase at 25% threshold (lowest, as fallback)

        Note:
            This method does not mutate enemy state. Use _update_phase_state
            to track phase changes and trigger feedback.
        """
        ai_profile = enemy.ai_profile or {}
        hp_percent = self._hp_percent(enemy)
        hp_bucket = self._get_hp_bucket(hp_percent)

        # Create cache key using enemy ID, HP bucket, and profile content hash
        # Use content-based hash for stability across profile reloads
        profile_hash = self._get_profile_hash(ai_profile)
        cache_key = (enemy.entity.entity_id, hp_bucket, profile_hash)

        # Check cache
        phase_cache = self._get_phase_cache()
        if cache_key in phase_cache:
            return phase_cache[cache_key]

        # Check for multi-phase structure
        if 'phases' in ai_profile:
            phases = ai_profile['phases']

            # Sort phases by threshold descending to find highest applicable threshold
            sorted_phases = sorted(phases, key=lambda p: p.get('hp_threshold', 0), reverse=True)

            # Find the first phase where HP is >= threshold (threshold represents HP floor)
            for phase in sorted_phases:
                threshold = phase.get('hp_threshold', 0)
                if hp_percent >= threshold:
                    result = (phase.get('rules', []), phase.get('name', f"phase_{sorted_phases.index(phase)+1}"), threshold, True)
                    phase_cache[cache_key] = result
                    # Limit cache size to prevent memory leaks (FIFO eviction)
                    # Note: Python 3.7+ dicts maintain insertion order, so next(iter()) gets oldest
                    if len(phase_cache) > _PHASE_CACHE_MAX_SIZE:
                        oldest_key = next(iter(phase_cache))
                        del phase_cache[oldest_key]
                    return result

            # If no phase matches, return the lowest threshold phase's rules
            if sorted_phases:
                last_phase = sorted_phases[-1]
                result = (last_phase.get('rules', []), last_phase.get('name', f"phase_{len(sorted_phases)}"), last_phase.get('hp_threshold', 0), True)
                phase_cache[cache_key] = result
                if len(phase_cache) > _PHASE_CACHE_MAX_SIZE:
                    oldest_key = next(iter(phase_cache))
                    del phase_cache[oldest_key]
                return result

        # Fallback to simple rules structure
        result = (ai_profile.get('rules', []), "default", None, False)
        phase_cache[cache_key] = result
        if len(phase_cache) > _PHASE_CACHE_MAX_SIZE:
            oldest_key = next(iter(phase_cache))
            del phase_cache[oldest_key]
        return result

    def _get_current_phase_rules(self, enemy: "BattleParticipant") -> List[Dict[str, Any]]:
        """Get rules for the current phase based on HP thresholds."""
        rules, _, _, _ = self._determine_phase(enemy)
        return rules

    def _get_current_phase_name(self, enemy: "BattleParticipant") -> str:
        """Get the name of the current phase for debugging."""
        _, name, _, _ = self._determine_phase(enemy)
        return name

    def _is_phase_feedback_candidate(self, enemy: "BattleParticipant") -> bool:
        """Return True if enemy should surface phase change messages to the player."""
        enemy_type = getattr(enemy.entity, "enemy_type", "").lower()
        name = (enemy.entity.name or "").lower()
        return enemy_type == "boss" or "alpha" in name

    def _update_phase_state(
        self,
        enemy: "BattleParticipant",
        phase_name: str,
        threshold: Optional[int],
        has_phases: bool
    ) -> None:
        """Track current phase and surface player-facing feedback when it changes."""
        previous = enemy.current_phase
        enemy.current_phase = phase_name

        if not has_phases:
            return

        if previous != phase_name:
            # Clear rule match cache when phase changes
            if hasattr(self, '_last_rule_match_cache'):
                # Remove all entries for this enemy
                keys_to_remove = [k for k in self._last_rule_match_cache.keys()
                                if k[0] == enemy.entity.entity_id]
                for key in keys_to_remove:
                    del self._last_rule_match_cache[key]

            if self.phase_feedback and self._is_phase_feedback_candidate(enemy):
                hp_text = f"{self._hp_percent(enemy):.0f}% HP" if enemy.stats.max_hp > 0 else "0% HP"
                self.message_log.append(f"PHASE: {enemy.entity.name} shifts tactics to {phase_name} at {hp_text}!")
            if self.debug_ai:
                threshold_text = f"threshold {threshold}%" if threshold is not None else "no threshold"
                self.message_log.append(f"AI {enemy.entity.name}: Entering phase {phase_name} ({threshold_text})")

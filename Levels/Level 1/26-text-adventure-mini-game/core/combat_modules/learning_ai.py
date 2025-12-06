"""Learning AI system that adapts to player patterns."""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from collections import defaultdict


@dataclass
class PlayerPattern:
    """Tracks a pattern in player behavior."""
    pattern_type: str  # "skill_preference", "target_preference", "heal_threshold", etc.
    value: Any
    confidence: float = 0.0  # 0.0 to 1.0
    sample_count: int = 0


class LearningAI:
    """Learns player habits during combat and produces counter-strategies."""

    def __init__(self, min_samples: int = 3, reanalysis_threshold: int = 3):
        """Configure thresholds for pattern detection and reanalysis."""
        # Track player action history
        self.player_actions: List[Dict[str, Any]] = []

        # Learned patterns
        self.patterns: Dict[str, PlayerPattern] = {}

        # Counters for pattern detection
        self.skill_usage: Dict[str, int] = defaultdict(int)
        self.target_choices: Dict[str, int] = defaultdict(int)  # "weakest", "strongest", "random"
        self.action_type_counts: Dict[str, int] = defaultdict(int)
        self.heal_hp_thresholds: List[float] = []  # HP% when player heals
        self.guard_patterns: List[int] = []  # Turns when player guards

        # Adaptation state
        self.adaptation_level: int = 0  # Increases as AI learns more
        self.min_samples_for_adaptation: int = min_samples
        self.reanalysis_threshold: int = reanalysis_threshold

        # Performance optimization: cache counter-strategy and track if patterns need re-analysis
        self._counter_strategy_cache: Optional[Dict[str, Any]] = None
        self._patterns_analyzed: bool = False
        self._last_analysis_action_count: int = 0

    def record_player_action(
        self,
        action_type: str,
        skill_id: Optional[str],
        target_id: Optional[str],
        actor_hp_percent: float,
        target_hp_percent: Optional[float],
        turn_number: int,
        all_enemy_ids: List[str],
        weakest_enemy_id: Optional[str],
        strongest_enemy_id: Optional[str]
    ) -> None:
        """Record a player action for later pattern analysis."""
        action_record = {
            "action_type": action_type,
            "skill_id": skill_id,
            "target_id": target_id,
            "actor_hp_percent": actor_hp_percent,
            "target_hp_percent": target_hp_percent,
            "turn_number": turn_number
        }
        self.player_actions.append(action_record)

        # Update counters
        self.action_type_counts[action_type] += 1

        if skill_id:
            self.skill_usage[skill_id] += 1

        # Detect target preference
        if target_id and all_enemy_ids:
            if target_id == weakest_enemy_id:
                self.target_choices["weakest"] += 1
            elif target_id == strongest_enemy_id:
                self.target_choices["strongest"] += 1
            else:
                self.target_choices["random"] += 1

        # Track heal thresholds
        if action_type in ("SKILL", "ITEM") and skill_id and "heal" in skill_id.lower():
            self.heal_hp_thresholds.append(actor_hp_percent)

        # Track guard patterns
        if action_type == "GUARD":
            self.guard_patterns.append(turn_number)

        # Defer pattern analysis until counter-strategy is requested
        # This improves performance by avoiding analysis on every action
        # Patterns will be analyzed lazily in get_counter_strategy()

    def _analyze_patterns(self) -> None:
        """Derive learned patterns from recorded actions when enough samples exist."""
        total_actions = len(self.player_actions)
        if total_actions < self.min_samples_for_adaptation:
            return

        # Detect favorite skill
        if self.skill_usage:
            favorite_skill = max(self.skill_usage.items(), key=lambda x: x[1])
            if favorite_skill[1] >= 2:
                confidence = min(1.0, favorite_skill[1] / total_actions)
                self.patterns["favorite_skill"] = PlayerPattern(
                    pattern_type="favorite_skill",
                    value=favorite_skill[0],
                    confidence=confidence,
                    sample_count=favorite_skill[1]
                )

        # Detect target preference
        if sum(self.target_choices.values()) >= 3:
            total_targets = sum(self.target_choices.values())
            preferred = max(self.target_choices.items(), key=lambda x: x[1])
            confidence = preferred[1] / total_targets
            if confidence >= 0.5:  # At least 50% consistent
                self.patterns["target_preference"] = PlayerPattern(
                    pattern_type="target_preference",
                    value=preferred[0],
                    confidence=confidence,
                    sample_count=total_targets
                )

        # Detect heal threshold
        if len(self.heal_hp_thresholds) >= 2:
            avg_heal_threshold = sum(self.heal_hp_thresholds) / len(self.heal_hp_thresholds)
            self.patterns["heal_threshold"] = PlayerPattern(
                pattern_type="heal_threshold",
                value=avg_heal_threshold,
                confidence=min(1.0, len(self.heal_hp_thresholds) / 5),
                sample_count=len(self.heal_hp_thresholds)
            )

        # Detect action type preference
        if total_actions >= 5:
            preferred_action = max(self.action_type_counts.items(), key=lambda x: x[1])
            confidence = preferred_action[1] / total_actions
            self.patterns["action_preference"] = PlayerPattern(
                pattern_type="action_preference",
                value=preferred_action[0],
                confidence=confidence,
                sample_count=total_actions
            )

        # Update adaptation level
        self.adaptation_level = len([p for p in self.patterns.values() if p.confidence >= 0.5])

    def get_counter_strategy(self) -> Dict[str, Any]:
        """Return a cached counter-strategy, re-analyzing patterns when new actions arrive."""
        # Check if we need to re-analyze patterns
        current_action_count = len(self.player_actions)
        needs_reanalysis = (
            not self._patterns_analyzed or
            current_action_count - self._last_analysis_action_count >= self.reanalysis_threshold or
            self._counter_strategy_cache is None
        )

        if needs_reanalysis:
            # Analyze patterns if we have enough samples
            if current_action_count >= self.min_samples_for_adaptation:
                self._analyze_patterns()
            self._last_analysis_action_count = current_action_count
            self._patterns_analyzed = True
            # Invalidate cache to force regeneration
            self._counter_strategy_cache = None

        # Return cached strategy if available
        if self._counter_strategy_cache is not None:
            return self._counter_strategy_cache

        # Generate new strategy
        strategy = {
            "weight_modifiers": {},
            "target_adjustments": {},
            "priority_actions": [],
            "avoid_actions": []
        }

        # Counter target preference
        if "target_preference" in self.patterns:
            pref = self.patterns["target_preference"]
            if pref.confidence >= 0.6:
                if pref.value == "weakest":
                    # Player focuses weak targets - have weak enemies guard more
                    strategy["weight_modifiers"]["guard_when_weak"] = 1.5
                    strategy["priority_actions"].append("protect_weak_ally")
                elif pref.value == "strongest":
                    # Player focuses strong targets - strong enemies should be aggressive
                    strategy["weight_modifiers"]["aggressive_when_targeted"] = 1.3

        # Counter heal threshold
        if "heal_threshold" in self.patterns:
            heal_pattern = self.patterns["heal_threshold"]
            if heal_pattern.confidence >= 0.5:
                threshold = heal_pattern.value
                # If player heals at high HP, be more aggressive
                if threshold > 50:
                    strategy["weight_modifiers"]["aggressive"] = 1.4
                # If player waits until low HP, try to burst them down
                else:
                    strategy["priority_actions"].append("focus_fire")

        # Counter favorite skill
        if "favorite_skill" in self.patterns:
            skill_pattern = self.patterns["favorite_skill"]
            if skill_pattern.confidence >= 0.5:
                skill_id = skill_pattern.value
                # If player uses fire skills, prioritize fire-resistant enemies
                if "fire" in skill_id.lower():
                    strategy["target_adjustments"]["prefer_fire_resist"] = True
                # If player uses healing, be more aggressive to outpace healing
                if "heal" in skill_id.lower():
                    strategy["weight_modifiers"]["aggressive"] = 1.3

        # Counter action preference
        if "action_preference" in self.patterns:
            action_pref = self.patterns["action_preference"]
            if action_pref.confidence >= 0.6:
                if action_pref.value == "SKILL":
                    # Player relies on skills - try to drain their SP
                    strategy["priority_actions"].append("sp_drain")
                elif action_pref.value == "GUARD":
                    # Player guards often - use armor-piercing or wait them out
                    strategy["weight_modifiers"]["skill_over_attack"] = 1.5

        # Cache the strategy
        self._counter_strategy_cache = strategy
        return strategy

    def has_learned_patterns(self) -> bool:
        """Check if the AI has learned any high-confidence patterns.

        Returns:
            True if at least one pattern has confidence >= 0.5, False otherwise.
        """
        return any(p.confidence >= 0.5 for p in self.patterns.values())

    def get_adaptation_summary(self) -> str:
        """Get a human-readable summary of learned patterns."""
        if not self.patterns:
            return "AI is still learning player patterns..."

        summaries = []
        for pattern in self.patterns.values():
            if pattern.confidence >= 0.5:
                if pattern.pattern_type == "favorite_skill":
                    summaries.append(f"Player favors {pattern.value} ({pattern.confidence:.0%} confidence)")
                elif pattern.pattern_type == "target_preference":
                    summaries.append(f"Player targets {pattern.value} enemies ({pattern.confidence:.0%} confidence)")
                elif pattern.pattern_type == "heal_threshold":
                    summaries.append(f"Player heals around {pattern.value:.0f}% HP ({pattern.confidence:.0%} confidence)")

        if summaries:
            return "AI has learned: " + "; ".join(summaries)
        return "AI is still learning player patterns..."

"""Learning AI integration driver for adaptive enemy behavior.

This module provides integration hooks between the battle system and the learning
AI system. It handles recording player actions for pattern detection and
applying counter-strategies to modify enemy behavior.

Learning AI integration:
    - Records player actions with context (HP, targets, turn number)
    - Applies counter-strategies to modify rule weights
    - Detects player patterns (skill preferences, target preferences, heal thresholds)
    - Generates adaptive responses (aggressive, guard_when_weak, focus_fire)

Performance optimization:
    - Only creates copies for rules that will be modified
    - Uses selective deep copy for modified rules only
"""

import copy
from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from core.combat import BattleCommand, BattleParticipant
    from .learning_ai import LearningAI


class LearningDriverMixin:
    """Mixin providing learning AI integration methods for AI systems.

    This mixin assumes the host class has:
    - self.players: List[BattleParticipant]
    - self.enemies: List[BattleParticipant]
    - self.learning_ai: Optional[LearningAI]
    - self.debug_ai: bool
    - self.message_log: List[str]
    - self.turn_counter: int
    - self._hp_percent(participant) -> float
    - self._find_participant(entity_id) -> Optional[BattleParticipant]
    """

    def _record_player_action_for_learning(self, cmd: "BattleCommand") -> None:
        """Record a player action for the learning AI to analyze."""
        if not self.learning_ai:
            return

        # Find the actor
        actor = self._find_participant(cmd.actor_id)
        if not actor:
            return

        # Get target info
        target_id = cmd.target_ids[0] if cmd.target_ids else None
        target = self._find_participant(target_id) if target_id else None
        target_hp_pct = self._hp_percent(target) if target else None

        # Get enemy info for target preference detection
        alive_enemies = [e for e in self.enemies if e.is_alive()]
        all_enemy_ids = [e.entity.entity_id for e in alive_enemies]

        weakest_enemy_id = None
        strongest_enemy_id = None
        if alive_enemies:
            weakest = min(alive_enemies, key=lambda e: e.stats.hp)
            strongest = max(alive_enemies, key=lambda e: e.stats.hp)
            weakest_enemy_id = weakest.entity.entity_id
            strongest_enemy_id = strongest.entity.entity_id

        self.learning_ai.record_player_action(
            action_type=cmd.action_type.name,
            skill_id=cmd.skill_id,
            target_id=target_id,
            actor_hp_percent=self._hp_percent(actor),
            target_hp_percent=target_hp_pct,
            turn_number=self.turn_counter,
            all_enemy_ids=all_enemy_ids,
            weakest_enemy_id=weakest_enemy_id,
            strongest_enemy_id=strongest_enemy_id
        )

    def _apply_counter_strategy(
        self,
        rules: List[Dict[str, Any]],
        enemy: "BattleParticipant",
        counter_strategy: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Apply learning AI counter-strategy to modify rule weights.

        This method modifies rule weights based on learned player patterns.
        The learning AI detects player behavior (favorite skills, target
        preferences, heal thresholds) and generates counter-strategies.

        Performance optimization:
        - Only creates copies for rules that will be modified
        - Uses selective deep copy for modified rules only

        Weight modifications:
        - aggressive: Increases attack action weights
        - guard_when_weak: Increases guard weights when enemy HP < 40%
        - skill_over_attack: Increases skill weights over attack weights

        Priority actions:
        - focus_fire: Boosts attacks targeting weakest enemy
        - protect_weak_ally: Boosts guard/ally-targeting actions

        Args:
            rules: List of rule dictionaries (will be selectively copied)
            enemy: The enemy participant (for HP checks)
            counter_strategy: Dict with 'weight_modifiers' and 'priority_actions'

        Returns:
            List[Dict[str, Any]]: Rules with adjusted weights. If any rules were
                modified, returns a new list containing selectively deep-copied
                modified rules alongside original unmodified rules. If no
                modifications were needed (empty counter_strategy or no matching
                rules), returns the original rules list unchanged (not a copy).

        Example counter_strategy:
            {
                "weight_modifiers": {
                    "aggressive": 1.4,
                    "guard_when_weak": 1.5
                },
                "priority_actions": ["focus_fire", "protect_weak_ally"]
            }

        This would:
        - Double attack weights (1.4x multiplier)
        - Increase guard weights by 50% when enemy HP < 40%
        - Boost focus fire and ally protection actions by 50%

        See also:
            LearningAI.get_counter_strategy: Generates counter-strategies
            _select_ai_action: Uses modified weights for selection
        """
        weight_mods = counter_strategy.get('weight_modifiers', {})
        priority_actions = counter_strategy.get('priority_actions', [])

        # Check if any modifications will be applied
        has_modifications = bool(weight_mods or priority_actions)
        if not has_modifications:
            return rules

        hp_percent = self._hp_percent(enemy)
        modified_rules = []
        needs_copy = False

        for rule in rules:
            action_type = rule.get('action', {}).get('type', '')
            target_strategy = rule.get('action', {}).get('target_strategy', '')
            original_weight = rule.get('weight', 1)
            new_weight = original_weight
            rule_modified = False

            # Apply aggressive modifier
            if 'aggressive' in weight_mods and action_type == 'attack':
                new_weight *= weight_mods['aggressive']
                rule_modified = True

            # Apply guard_when_weak modifier
            if 'guard_when_weak' in weight_mods:
                if action_type == 'guard' and hp_percent < 40:
                    new_weight *= weight_mods['guard_when_weak']
                    rule_modified = True

            # Apply skill_over_attack modifier
            if 'skill_over_attack' in weight_mods and action_type == 'skill':
                new_weight *= weight_mods['skill_over_attack']
                rule_modified = True

            # Boost priority actions
            if 'focus_fire' in priority_actions and target_strategy == 'weakest_enemy':
                new_weight *= 1.5
                rule_modified = True

            if 'protect_weak_ally' in priority_actions:
                if action_type == 'guard' or target_strategy == 'weakest_ally':
                    new_weight *= 1.3
                    rule_modified = True

            if rule_modified:
                # Only copy if modified
                rule_copy = copy.deepcopy(rule)
                rule_copy['weight'] = new_weight
                modified_rules.append(rule_copy)
                needs_copy = True
            else:
                # No modification - use original
                modified_rules.append(rule)

        # If no rules were modified, return original
        if not needs_copy:
            return rules

        return modified_rules

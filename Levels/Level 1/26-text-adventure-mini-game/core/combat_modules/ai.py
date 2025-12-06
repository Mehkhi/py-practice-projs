"""AI decision-making mixin for the combat system.

Handles rule evaluation, tactics, and learning integration while deferring
imports to avoid circular references with core.combat."""

import copy
from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from core.combat import BattleCommand, BattleParticipant
    from .tactics import TacticsCoordinator
    from .learning_ai import LearningAI

from .conditions import ConditionEvaluatorMixin
from .targeting import TargetingMixin
from .ai_cache import AICacheMixin
from .phase_evaluator import PhaseEvaluatorMixin
from .rule_indexer import RuleIndexerMixin
from .tactics_driver import TacticsDriverMixin
from .learning_driver import LearningDriverMixin
from core.constants import (
    AI_AGGRESSIVE_ATTACK_MULTIPLIER,
    AI_AGGRESSIVE_SKILL_MULTIPLIER,
    AI_DEFENSIVE_GUARD_MULTIPLIER,
    AI_DEFENSIVE_HOLY_MULTIPLIER,
    AI_SUPPORT_ITEM_MULTIPLIER,
    AI_SUPPORT_ALLY_SKILL_MULTIPLIER,
    AI_FALLBACK_GUARD_HP_THRESHOLD,
    AI_RULE_CACHE_MAX_SIZE,
)


class BattleAIMixin(
    ConditionEvaluatorMixin,
    TargetingMixin,
    PhaseEvaluatorMixin,  # Includes AICacheMixin
    RuleIndexerMixin,  # Includes AICacheMixin
    TacticsDriverMixin,  # Includes AICacheMixin
    LearningDriverMixin
):
    """AI utilities for BattleSystem (phases, rules, tactics, learning).

    Host classes should expose player/enemy lists, skills/items, a message log,
    RNG instance, and a queue for pending commands.
    """

    def perform_enemy_actions(self) -> None:
        """Run the enemy turn: tick tactics, apply learning tweaks, queue commands, then advance state."""
        from core.combat import BattleState

        self.turn_counter += 1

        # Tick tactic cooldowns
        if self.tactics_coordinator:
            self.tactics_coordinator.tick_cooldowns()

        # Try coordinated tactics first
        coordinated_enemies: set = set()
        if self.enable_coordination and len([e for e in self.enemies if e.is_alive()]) >= 2:
            coordinated_enemies = self._attempt_coordinated_tactics()

        # Apply learning AI counter-strategy if available
        counter_strategy = None
        if self.learning_ai and self.learning_ai.adaptation_level > 0:
            counter_strategy = self.learning_ai.get_counter_strategy()
            if self.debug_ai:
                self.message_log.append(f"AI adapting: {self.learning_ai.get_adaptation_summary()}")

        for enemy in self.enemies:
            if not enemy.is_alive():
                continue

            # Skip enemies that already have coordinated actions
            if enemy.entity.entity_id in coordinated_enemies:
                continue

            cmd = self._select_ai_action(enemy, counter_strategy)
            if cmd:
                self.pending_commands.append(cmd)

        self.state = BattleState.RESOLVE_ACTIONS

    def _select_ai_action(
        self,
        enemy: "BattleParticipant",
        counter_strategy: Optional[Dict[str, Any]] = None
    ) -> Optional["BattleCommand"]:
        """Select an action for an enemy using phase-aware rules and learning modifiers.

        Falls back to a basic attack when no profile exists.
        """
        if not enemy.ai_profile:
            # Fallback to simple attack if no AI profile
            return self._get_fallback_action(enemy)

        # Get current phase rules (multi-phase support) and record phase shifts
        current_phase_rules, phase_name, threshold, has_phases = self._determine_phase(enemy)
        self._update_phase_state(enemy, phase_name, threshold, has_phases)

        # Apply behavior type modifications
        current_phase_rules = self._apply_behavior_type_modifications(current_phase_rules, enemy)

        # Apply learning AI counter-strategy weight modifiers
        if counter_strategy:
            current_phase_rules = self._apply_counter_strategy(current_phase_rules, enemy, counter_strategy)

        # Try memoization first: check if we have a cached valid rule for this phase/state
        memo_key = (enemy.entity.entity_id, phase_name, self.turn_counter)
        if not hasattr(self, '_last_rule_match_cache'):
            self._last_rule_match_cache = {}

        # Check memoized rule (if phase and turn match, and state hasn't changed significantly)
        if memo_key in self._last_rule_match_cache:
            memoized_rule = self._last_rule_match_cache[memo_key]
            if memoized_rule in current_phase_rules:
                # Quick validation: check if rule still passes
                if self._evaluate_ai_rule(memoized_rule, enemy):
                    valid_rules = [memoized_rule]
                    if self.debug_ai:
                        self.message_log.append(f"AI {enemy.entity.name}: Using memoized rule")
                else:
                    # Rule no longer valid, remove from cache
                    del self._last_rule_match_cache[memo_key]
                    valid_rules = []
            else:
                # Rule not in current phase, clear cache
                del self._last_rule_match_cache[memo_key]
                valid_rules = []
        else:
            valid_rules = []

        # If no memoized rule, evaluate rules
        if not valid_rules:
            # Pre-filter rules using index to reduce evaluation overhead
            candidate_rules = self._get_candidate_rules(current_phase_rules, enemy)

            # Evaluate pre-filtered candidate rules
            for rule in candidate_rules:
                if self._evaluate_ai_rule(rule, enemy):
                    valid_rules.append(rule)

            # Memoize first valid rule for next time (if phase/state similar)
            if valid_rules:
                self._last_rule_match_cache[memo_key] = valid_rules[0]
                # Limit cache size
                if len(self._last_rule_match_cache) > AI_RULE_CACHE_MAX_SIZE:
                    oldest_key = next(iter(self._last_rule_match_cache))
                    del self._last_rule_match_cache[oldest_key]

        if self.debug_ai:
            self.message_log.append(f"AI {enemy.entity.name}: Phase {phase_name}, {len(valid_rules)} valid rules")

        if not valid_rules:
            # Use fallback action if no rules pass
            return self._get_fallback_action(enemy)

        # Weighted random selection from valid rules
        weights = [rule.get('weight', 1) for rule in valid_rules]
        selected_rule = self.rng.choices(valid_rules, weights=weights, k=1)[0]

        if self.debug_ai:
            self.message_log.append(f"AI {enemy.entity.name}: Selected rule with action {selected_rule['action']['type']}")

        return self._create_command_from_rule(selected_rule, enemy)


    def _apply_behavior_type_modifications(
        self,
        rules: List[Dict[str, Any]],
        enemy: "BattleParticipant"
    ) -> List[Dict[str, Any]]:
        """Apply behavior type modifications to rule weights.

        Performance optimization:
        - Determines modification need BEFORE copying to avoid wasted deep copies
        - Only creates copies when weight will actually change
        - Balanced behavior returns original rules without copying
        """
        behavior_type = enemy.ai_profile.get('behavior_type', 'balanced')

        # Balanced behavior doesn't modify weights - return original
        if behavior_type == 'balanced':
            return rules

        modified_rules = []
        any_modified = False

        for rule in rules:
            action_type = rule.get('action', {}).get('type', '')
            target_strategy = rule.get('action', {}).get('target_strategy', '')
            original_weight = rule.get('weight', 1)
            new_weight = original_weight
            should_modify = False

            if behavior_type == 'aggressive':
                # Boost attack and damage skill weights
                if action_type == 'attack':
                    new_weight = original_weight * AI_AGGRESSIVE_ATTACK_MULTIPLIER
                    should_modify = True
                elif action_type == 'skill':
                    skill_id = rule.get('action', {}).get('skill_id', '')
                    skill = self.skills.get(skill_id)
                    if skill and skill.element in ['physical', 'fire']:
                        new_weight = original_weight * AI_AGGRESSIVE_SKILL_MULTIPLIER
                        should_modify = True

            elif behavior_type == 'defensive':
                # Boost guard, heal, and self-targeting weights
                if action_type == 'guard' or target_strategy == 'self':
                    new_weight = original_weight * AI_DEFENSIVE_GUARD_MULTIPLIER
                    should_modify = True
                elif action_type == 'skill':
                    skill_id = rule.get('action', {}).get('skill_id', '')
                    skill = self.skills.get(skill_id)
                    if skill and skill.element == 'holy':
                        new_weight = original_weight * AI_DEFENSIVE_HOLY_MULTIPLIER
                        should_modify = True

            elif behavior_type == 'support':
                # Boost ally-targeting and item usage weights
                if action_type == 'item' or target_strategy in ['weakest_ally', 'random_ally']:
                    new_weight = original_weight * AI_SUPPORT_ITEM_MULTIPLIER
                    should_modify = True
                elif action_type == 'skill':
                    skill_id = rule.get('action', {}).get('skill_id', '')
                    skill = self.skills.get(skill_id)
                    if skill and skill.target_pattern in ['single_ally', 'all_allies']:
                        new_weight = original_weight * AI_SUPPORT_ALLY_SKILL_MULTIPLIER
                        should_modify = True

            if should_modify:
                # Only copy if we're actually modifying
                rule_copy = copy.deepcopy(rule)
                rule_copy['weight'] = new_weight
                modified_rules.append(rule_copy)
                any_modified = True
            else:
                # No modification needed - use original reference
                modified_rules.append(rule)

        # If no rules were modified, return original list to save memory
        if not any_modified:
            return rules

        return modified_rules

    def _get_fallback_action(self, enemy: "BattleParticipant") -> Optional["BattleCommand"]:
        """Get fallback action when no AI rules pass or no profile exists."""
        alive_players = [p for p in self.players if p.is_alive()]
        if not alive_players:
            return None

        # Check for fallback_action in AI profile
        fallback_action = None
        if enemy.ai_profile and 'fallback_action' in enemy.ai_profile:
            fallback_action = enemy.ai_profile['fallback_action']

        if fallback_action:
            if self.debug_ai:
                self.message_log.append(f"AI {enemy.entity.name}: Using fallback action {fallback_action['type']}")
            return self._create_command_from_action_dict(fallback_action, enemy)

        # Contextual flavorful fallbacks to avoid repetitive basic attacks
        guard_options: List[Dict[str, Any]] = []
        item_options: List[Dict[str, Any]] = []
        attack_options: List[Dict[str, Any]] = []

        # Regroup when hurt
        if enemy.stats.max_hp > 0 and enemy.stats.hp <= enemy.stats.max_hp * AI_FALLBACK_GUARD_HP_THRESHOLD:
            guard_options.append({"type": "guard", "target_strategy": "self"})

        # Use a healing item if available
        for item_id, count in enemy.items.items():
            if count > 0 and item_id in self.items:
                item = self.items[item_id]
                if item.effect_id and item.effect_id.startswith("heal"):
                    item_options.append({"type": "item", "item_id": item_id, "target_strategy": "self"})
                    break

        # Mix up attack targeting if nothing else stands out
        attack_options.append({"type": "attack", "target_strategy": "weakest_enemy"})
        attack_options.append({"type": "attack", "target_strategy": "random_enemy"})

        if item_options:
            chosen_fallback = item_options[0] if len(item_options) == 1 else self.rng.choice(item_options)
        elif guard_options:
            chosen_fallback = guard_options[0] if len(guard_options) == 1 else self.rng.choice(guard_options)
        else:
            chosen_fallback = self.rng.choice(attack_options)
        if self.debug_ai:
            self.message_log.append(f"AI {enemy.entity.name}: Using contextual fallback {chosen_fallback['type']}")

        return self._create_command_from_action_dict(chosen_fallback, enemy)

    def _create_command_from_action_dict(
        self,
        action: Dict[str, Any],
        enemy: "BattleParticipant"
    ) -> Optional["BattleCommand"]:
        """Create a BattleCommand from an action dictionary."""
        from core.combat import ActionType, BattleCommand

        action_type_str = action['type']

        # Map string to ActionType
        action_type_map = {
            'attack': ActionType.ATTACK,
            'skill': ActionType.SKILL,
            'item': ActionType.ITEM,
            'guard': ActionType.GUARD,
            'talk': ActionType.TALK,
            'flee': ActionType.FLEE
        }

        if action_type_str not in action_type_map:
            if self.debug_ai:
                self.message_log.append(f"AI {enemy.entity.name}: Unknown action type {action_type_str}")
            return self._get_fallback_action(enemy)

        action_type = action_type_map[action_type_str]

        # Get targets based on strategy
        target_ids = self._apply_target_strategy(action.get('target_strategy', 'random_enemy'), enemy)

        # Validate skill/item availability
        if action_type == ActionType.SKILL:
            skill_id = action.get('skill_id')
            if not skill_id or skill_id not in enemy.skills:
                if self.debug_ai:
                    self.message_log.append(f"AI {enemy.entity.name}: Skill {skill_id} not available")
                return self._get_fallback_action(enemy)

            skill = self.skills.get(skill_id)
            if not skill or enemy.stats.sp < skill.cost_sp:
                if self.debug_ai:
                    self.message_log.append(f"AI {enemy.entity.name}: Not enough SP for {skill_id}")
                return self._get_fallback_action(enemy)

            return BattleCommand(
                actor_id=enemy.entity.entity_id,
                action_type=action_type,
                skill_id=skill_id,
                target_ids=target_ids
            )

        elif action_type == ActionType.ITEM:
            item_id = action.get('item_id')
            if not item_id or item_id not in enemy.items or enemy.items[item_id] <= 0:
                if self.debug_ai:
                    self.message_log.append(f"AI {enemy.entity.name}: Item {item_id} not available")
                return self._get_fallback_action(enemy)

            return BattleCommand(
                actor_id=enemy.entity.entity_id,
                action_type=action_type,
                item_id=item_id,
                target_ids=target_ids
            )

        # For attack, guard, talk, flee
        return BattleCommand(
            actor_id=enemy.entity.entity_id,
            action_type=action_type,
            target_ids=target_ids
        )

    def _create_command_from_rule(
        self,
        rule: Dict[str, Any],
        enemy: "BattleParticipant"
    ) -> Optional["BattleCommand"]:
        """Create a BattleCommand from a selected AI rule."""
        action = rule['action']
        return self._create_command_from_action_dict(action, enemy)

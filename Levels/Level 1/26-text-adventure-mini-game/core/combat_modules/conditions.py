"""Condition evaluation for AI rule-based decision making.

This module provides condition evaluators used by the AI system to determine
when rules should apply based on battle state, HP/SP levels, status effects,
and party composition.

Note on deferred imports:
    This module uses TYPE_CHECKING to avoid circular import issues with
    core.combat types.
"""

from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from core.combat import BattleParticipant

from .tactics import CoordinatedTactic


class ConditionEvaluatorMixin:
    """Mixin providing condition evaluation methods for AI systems.

    This mixin assumes the host class has:
    - self.players: List[BattleParticipant]
    - self.enemies: List[BattleParticipant]
    - self.turn_counter: int
    - self.debug_ai: bool
    - self._hp_percent(participant) -> float
    - self._get_hp_bucket(hp_percent) -> int
    - self._get_sp_bucket(sp_percent) -> int
    - self._get_rule_evaluation_cache() -> Dict
    """

    def _evaluate_ai_rule(self, rule: Dict[str, Any], enemy: "BattleParticipant") -> bool:
        """Evaluate whether an AI rule's conditions are met.

        This method checks all conditions in a rule's condition dictionary.
        All conditions must pass for the rule to be valid.

        Performance optimizations:
        - Early exit on first failed condition (fail-fast)
        - Cache results for rules with simple conditions (HP/SP/turn only)
        - Skip expensive party status scans when not needed

        Supported conditions:
        - hp_percent: {min, max} - Enemy HP percentage range
        - sp_percent: {min, max} - Enemy SP percentage range
        - morale: {min, max} - Enemy morale level (for spare mechanics)
        - turn_number: {min, max} - Current turn number
        - allies_alive: {min, max} - Number of alive enemy allies
        - enemies_alive: {min, max} - Number of alive player characters
        - status_effects: List of "has_X" or "no_X" strings
        - ally_status_effects: Status requirements for enemy party
        - enemy_status_effects: Status requirements for player party

        Args:
            rule: Rule dictionary with 'conditions' key
            enemy: The enemy participant to evaluate conditions for

        Returns:
            True if all conditions are met, False otherwise

        Example rule:
            {
                "conditions": {
                    "hp_percent": {"min": 0, "max": 50},
                    "allies_alive": {"min": 1},
                    "enemy_status_effects": {"has": ["poison"]}
                },
                "action": {"type": "skill", "skill_id": "desperate_strike"},
                "weight": 2
            }

        This rule would only be valid when:
        - Enemy HP is between 0-50%
        - At least 1 enemy ally is alive
        - At least one player has poison status
        """
        # Import cache size limit from ai module
        from .ai import _RULE_CACHE_MAX_SIZE

        conditions = rule.get('conditions', {})

        # Check if this is a simple rule (only HP/SP/turn/morale) that can be cached
        has_complex_conditions = any(key in conditions for key in [
            'allies_alive', 'enemies_alive', 'status_effects',
            'ally_status_effects', 'enemy_status_effects'
        ])

        # Try cache lookup for simple rules
        if not has_complex_conditions:
            hp_percent = self._hp_percent(enemy)
            hp_bucket = self._get_hp_bucket(hp_percent)
            sp_percent = (enemy.stats.sp / enemy.stats.max_sp * 100) if enemy.stats.max_sp > 0 else 0
            sp_bucket = self._get_sp_bucket(sp_percent)
            rule_id = id(rule)  # Use rule identity as part of cache key
            cache_key = (enemy.entity.entity_id, rule_id, hp_bucket, sp_bucket, self.turn_counter)

            rule_cache = self._get_rule_evaluation_cache()
            if cache_key in rule_cache:
                return rule_cache[cache_key]

            # Evaluate and cache result
            result = self._evaluate_ai_rule_conditions(conditions, enemy)
            rule_cache[cache_key] = result

            # Limit cache size (FIFO eviction, relies on Python 3.7+ dict ordering)
            if len(rule_cache) > _RULE_CACHE_MAX_SIZE:
                oldest_key = next(iter(rule_cache))
                del rule_cache[oldest_key]

            return result
        else:
            # Complex rule - evaluate directly (no caching)
            return self._evaluate_ai_rule_conditions(conditions, enemy)

    def _evaluate_ai_rule_conditions(
        self,
        conditions: Dict[str, Any],
        enemy: "BattleParticipant"
    ) -> bool:
        """Evaluate rule conditions against current battle state.

        Args:
            conditions: Dictionary of conditions to evaluate
            enemy: The enemy participant to evaluate conditions for

        Returns:
            True if all conditions are met, False otherwise
        """
        # HP percentage condition (early exit)
        if 'hp_percent' in conditions:
            if enemy.stats.max_hp <= 0:
                return False
            hp_percent = (enemy.stats.hp / enemy.stats.max_hp) * 100
            min_hp = conditions['hp_percent'].get('min', 0)
            max_hp = conditions['hp_percent'].get('max', 100)
            if not (min_hp <= hp_percent <= max_hp):
                return False

        # SP percentage condition (early exit)
        if 'sp_percent' in conditions:
            if enemy.stats.max_sp <= 0:
                return False
            sp_percent = (enemy.stats.sp / enemy.stats.max_sp) * 100
            min_sp = conditions['sp_percent'].get('min', 0)
            max_sp = conditions['sp_percent'].get('max', 100)
            if not (min_sp <= sp_percent <= max_sp):
                return False

        # Morale condition (early exit)
        if 'morale' in conditions:
            min_morale = conditions['morale'].get('min', 0)
            max_morale = conditions['morale'].get('max', 3)
            if not (min_morale <= enemy.morale <= max_morale):
                return False

        # Turn number condition (early exit)
        if 'turn_number' in conditions:
            min_turn = conditions['turn_number'].get('min', 1)
            max_turn = conditions['turn_number'].get('max', 99)
            if not (min_turn <= self.turn_counter <= max_turn):
                return False

        # Allies alive condition (early exit)
        if 'allies_alive' in conditions:
            alive_allies = len([e for e in self.enemies if e.is_alive()])
            min_allies = conditions['allies_alive'].get('min', 0)
            max_allies = conditions['allies_alive'].get('max', 99)
            if not (min_allies <= alive_allies <= max_allies):
                return False

        # Enemies alive condition (early exit)
        if 'enemies_alive' in conditions:
            alive_enemies = len([p for p in self.players if p.is_alive()])
            min_enemies = conditions['enemies_alive'].get('min', 0)
            max_enemies = conditions['enemies_alive'].get('max', 99)
            if not (min_enemies <= alive_enemies <= max_enemies):
                return False

        # Status effects condition (early exit)
        if 'status_effects' in conditions:
            for status_condition in conditions['status_effects']:
                if status_condition.startswith('has_'):
                    status_id = status_condition[4:]
                    if status_id not in enemy.stats.status_effects:
                        return False
                elif status_condition.startswith('no_'):
                    status_id = status_condition[3:]
                    if status_id in enemy.stats.status_effects:
                        return False

        # Ally status effects condition (expensive - only check if needed)
        if 'ally_status_effects' in conditions:
            if not self._check_party_status_conditions(
                self.enemies, conditions['ally_status_effects'], exclude=enemy
            ):
                return False

        # Enemy (player-side) status effects condition (expensive - only check if needed)
        if 'enemy_status_effects' in conditions:
            if not self._check_party_status_conditions(
                self.players, conditions['enemy_status_effects']
            ):
                return False

        return True

    def _check_party_status_conditions(
        self,
        party: List["BattleParticipant"],
        requirement: Any,
        exclude: Optional["BattleParticipant"] = None
    ) -> bool:
        """Evaluate status requirements against a party.

        Supports multiple requirement formats:
        - List of strings: ["has_poison", "no_bleed"]
        - Dict format: {"has": ["poison"], "any": ["weak"], "not": ["shield"]}
        - Single string: "poison"

        Args:
            party: List of participants to check
            requirement: Status requirement (list, dict, or string)
            exclude: Optional participant to exclude from checks

        Returns:
            True if all requirements are met, False otherwise
        """
        if requirement is None:
            return True

        has_list: List[str] = []
        not_list: List[str] = []
        any_list: List[str] = []

        if isinstance(requirement, list):
            for entry in requirement:
                if isinstance(entry, str) and entry.startswith('has_'):
                    has_list.append(entry[4:])
                elif isinstance(entry, str) and entry.startswith('no_'):
                    not_list.append(entry[3:])
                elif isinstance(entry, str):
                    has_list.append(entry)
        elif isinstance(requirement, dict):
            has_list.extend(requirement.get('has', []))
            any_list.extend(requirement.get('any', []))
            not_list.extend(requirement.get('not', []))
            not_list.extend(requirement.get('none', []))
        elif isinstance(requirement, str):
            has_list.append(requirement)
        else:
            return True

        for status_id in has_list:
            if not self._party_has_status(party, status_id, exclude):
                return False

        if any_list:
            if not any(self._party_has_status(party, status_id, exclude) for status_id in any_list):
                return False

        for status_id in not_list:
            if self._party_has_status(party, status_id, exclude):
                return False

        return True

    def _party_has_status(
        self,
        party: List["BattleParticipant"],
        status_id: str,
        exclude: Optional["BattleParticipant"] = None
    ) -> bool:
        """Return True if any member of the party has a status effect.

        Args:
            party: List of participants to check
            status_id: Status effect ID to look for
            exclude: Optional participant to exclude from the check

        Returns:
            True if any alive party member (except excluded) has the status
        """
        for participant in party:
            if participant == exclude or not participant.is_alive():
                continue
            if status_id in participant.stats.status_effects:
                return True
        return False

    def _check_tactic_conditions(self, tactic: CoordinatedTactic) -> bool:
        """Check if tactic trigger conditions are met.

        Args:
            tactic: The coordinated tactic to check conditions for

        Returns:
            True if all trigger conditions are met, False otherwise
        """
        conditions = tactic.trigger_conditions

        if 'enemies_alive' in conditions:
            alive = len([e for e in self.enemies if e.is_alive()])
            min_val = conditions['enemies_alive'].get('min', 0)
            max_val = conditions['enemies_alive'].get('max', 99)
            if not (min_val <= alive <= max_val):
                return False

        if 'player_hp_percent' in conditions:
            # Check if any player meets the HP condition
            for player in self.players:
                if player.is_alive():
                    hp_pct = self._hp_percent(player)
                    min_hp = conditions['player_hp_percent'].get('min', 0)
                    max_hp = conditions['player_hp_percent'].get('max', 100)
                    if min_hp <= hp_pct <= max_hp:
                        break
            else:
                return False

        if 'ally_hp_percent' in conditions:
            # Check if any ally (enemy) meets the HP condition
            for enemy in self.enemies:
                if enemy.is_alive():
                    hp_pct = self._hp_percent(enemy)
                    min_hp = conditions['ally_hp_percent'].get('min', 0)
                    max_hp = conditions['ally_hp_percent'].get('max', 100)
                    if min_hp <= hp_pct <= max_hp:
                        break
            else:
                return False

        if 'turn_number' in conditions:
            min_turn = conditions['turn_number'].get('min', 1)
            max_turn = conditions['turn_number'].get('max', 99)
            if not (min_turn <= self.turn_counter <= max_turn):
                return False

        if 'enemy_status_effects' in conditions:
            if not self._check_party_status_conditions(
                self.players, conditions['enemy_status_effects']
            ):
                return False

        return True

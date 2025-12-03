"""AI decision-making for the combat system.

This module contains the BattleAIMixin which provides all AI decision-making
methods for BattleSystem, including phase management, rule evaluation,
coordinated tactics, and learning AI integration.

Note on deferred imports:
    Several methods use deferred imports (e.g., `from core.combat import ActionType`)
    inside function bodies. This is intentional to avoid circular import issues between
    core/combat/__init__.py (which defines types) and this module (which is imported by it).
    Python caches imports, so the performance impact is negligible after the first call.

Refactored modules:
    - conditions.py: Condition evaluators (ConditionEvaluatorMixin)
    - targeting.py: Target selection strategies (TargetingMixin)
"""

import copy
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

if TYPE_CHECKING:
    from core.combat import BattleCommand, BattleParticipant

from .conditions import ConditionEvaluatorMixin
from .tactics import CoordinatedTactic
from .targeting import TargetingMixin

# Cache size limits for AI decision caches
# These can be tuned based on memory constraints and battle complexity
_PHASE_CACHE_MAX_SIZE = 100  # Max entries in phase determination cache
_RULE_CACHE_MAX_SIZE = 200   # Max entries in rule evaluation cache
_TACTICS_CACHE_MAX_TURNS = 10  # Max turns to keep in tactics cache

# HP bucket size for phase caching (5% granularity)
_HP_BUCKET_SIZE = 5
# SP bucket size for rule caching (10% granularity, coarser since SP changes less frequently)
_SP_BUCKET_SIZE = 10


class BattleAIMixin(ConditionEvaluatorMixin, TargetingMixin):
    """Mixin providing AI decision-making methods for BattleSystem.

    This mixin assumes the host class has:
    - self.players: List[BattleParticipant]
    - self.enemies: List[BattleParticipant]
    - self.skills: Dict[str, Skill]
    - self.items: Dict[str, Item]
    - self.message_log: List[str]
    - self.rng: random.Random
    - self.debug_ai: bool
    - self.phase_feedback: bool
    - self.turn_counter: int
    - self.enable_coordination: bool
    - self.enable_learning: bool
    - self.tactics_coordinator: Optional[TacticsCoordinator]
    - self.learning_ai: Optional[LearningAI]
    - self.pending_commands: List[BattleCommand]
    - self._find_participant(entity_id) -> Optional[BattleParticipant]
    - self._hp_percent(participant) -> float
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
        """
        return int(round(hp_percent / _HP_BUCKET_SIZE) * _HP_BUCKET_SIZE)

    def _get_sp_bucket(self, sp_percent: float) -> int:
        """Round SP percentage to nearest bucket for caching.

        Uses _SP_BUCKET_SIZE (default 10%) granularity, coarser than HP buckets
        since SP changes less frequently during combat.
        """
        return int(round(sp_percent / _SP_BUCKET_SIZE) * _SP_BUCKET_SIZE)

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
            The phase and rule caches use id() of dict objects (AI profiles, rules)
            as part of cache keys for efficiency. This assumes object identity
            stability during a battle. If profiles/rules are recreated (e.g., from
            JSON reloading), call this method to prevent stale cache entries.
        """
        if hasattr(self, '_phase_cache'):
            self._phase_cache.clear()
        if hasattr(self, '_rule_evaluation_cache'):
            self._rule_evaluation_cache.clear()
        if hasattr(self, '_tactics_cache'):
            self._tactics_cache.clear()

    def perform_enemy_actions(self) -> None:
        """Perform AI actions for enemies using rule-based decision making.

        This method orchestrates the entire enemy turn:
        1. Increments turn counter
        2. Ticks tactic cooldowns for coordinated tactics
        3. Attempts coordinated tactics (if enabled and conditions met)
        4. Gets learning AI counter-strategy (if adaptation level > 0)
        5. For each enemy not in a coordinated action:
           - Selects action using AI profile rules
           - Applies phase management, behavior type, and counter-strategy
           - Creates and queues battle command

        The method processes all enemies and transitions battle state to
        RESOLVE_ACTIONS when complete.

        Coordinated tactics take priority - enemies participating in coordination
        skip individual action selection. The learning AI counter-strategy
        modifies rule weights to counter detected player patterns.

        See also:
            _select_ai_action: Individual enemy action selection
            _attempt_coordinated_tactics: Multi-enemy coordination
            _apply_counter_strategy: Learning AI weight modifications
        """
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
        """Select an action for an enemy using AI profile rules with multi-phase support.

        This method implements the core AI decision-making logic:
        1. Determines current phase based on HP thresholds
        2. Updates phase state and triggers feedback if phase changed
        3. Applies behavior type modifications (aggressive/defensive/support)
        4. Applies learning AI counter-strategy weight modifiers
        5. Evaluates all phase rules against current conditions
        6. Selects from valid rules using weighted random selection
        7. Creates battle command from selected rule

        Args:
            enemy: The enemy participant to select an action for
            counter_strategy: Optional learning AI counter-strategy dict with
                weight_modifiers and priority_actions

        Returns:
            BattleCommand if action selected, None if no valid action available
            (including when fallback action fails due to no valid targets)

        The AI profile structure supports:
        - Simple rules: List of rules with conditions and actions
        - Multi-phase: Phases with HP thresholds, each with their own rules
        - Behavior types: aggressive, defensive, support, balanced
        - Fallback actions: Used when no rules pass

        Example AI profile:
            {
                "phases": [
                    {
                        "name": "aggressive",
                        "hp_threshold": 50,
                        "rules": [{"conditions": {...}, "action": {...}}]
                    },
                    {
                        "name": "desperate",
                        "hp_threshold": 25,
                        "rules": [{"conditions": {...}, "action": {...}}]
                    }
                ],
                "behavior_type": "aggressive",
                "fallback_action": {"type": "attack", "target_strategy": "random_enemy"}
            }

        See also:
            _determine_phase: Phase selection based on HP
            _evaluate_ai_rule: Condition evaluation
            _apply_counter_strategy: Learning AI modifications
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

        # Evaluate all rules
        valid_rules = []
        for rule in current_phase_rules:
            if self._evaluate_ai_rule(rule, enemy):
                valid_rules.append(rule)

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

    def _get_current_phase_rules(self, enemy: "BattleParticipant") -> List[Dict[str, Any]]:
        """Get rules for the current phase based on HP thresholds."""
        rules, _, _, _ = self._determine_phase(enemy)
        return rules

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
        - Cache key includes enemy ID, HP bucket, and profile object identity
        - Cache uses FIFO eviction when size exceeds _PHASE_CACHE_MAX_SIZE

        Cache key stability note:
            The cache uses id(ai_profile) as part of the key for efficiency.
            This assumes the AI profile dict object remains the same during battle.
            If profiles are reloaded or recreated, call clear_ai_caches() to
            prevent stale entries.

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

        # Create cache key using enemy ID, HP bucket, and profile identity
        # Use id() of profile dict as a simple hash (profile structure rarely changes)
        profile_id = id(ai_profile) if ai_profile else 0
        cache_key = (enemy.entity.entity_id, hp_bucket, profile_id)

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
            if self.phase_feedback and self._is_phase_feedback_candidate(enemy):
                hp_text = f"{self._hp_percent(enemy):.0f}% HP" if enemy.stats.max_hp > 0 else "0% HP"
                self.message_log.append(f"PHASE: {enemy.entity.name} shifts tactics to {phase_name} at {hp_text}!")
            if self.debug_ai:
                threshold_text = f"threshold {threshold}%" if threshold is not None else "no threshold"
                self.message_log.append(f"AI {enemy.entity.name}: Entering phase {phase_name} ({threshold_text})")

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
                    new_weight = original_weight * 2
                    should_modify = True
                elif action_type == 'skill':
                    skill_id = rule.get('action', {}).get('skill_id', '')
                    skill = self.skills.get(skill_id)
                    if skill and skill.element in ['physical', 'fire']:
                        new_weight = original_weight * 1.5
                        should_modify = True

            elif behavior_type == 'defensive':
                # Boost guard, heal, and self-targeting weights
                if action_type == 'guard' or target_strategy == 'self':
                    new_weight = original_weight * 2
                    should_modify = True
                elif action_type == 'skill':
                    skill_id = rule.get('action', {}).get('skill_id', '')
                    skill = self.skills.get(skill_id)
                    if skill and skill.element == 'holy':
                        new_weight = original_weight * 1.5
                        should_modify = True

            elif behavior_type == 'support':
                # Boost ally-targeting and item usage weights
                if action_type == 'item' or target_strategy in ['weakest_ally', 'random_ally']:
                    new_weight = original_weight * 2
                    should_modify = True
                elif action_type == 'skill':
                    skill_id = rule.get('action', {}).get('skill_id', '')
                    skill = self.skills.get(skill_id)
                    if skill and skill.target_pattern in ['single_ally', 'all_allies']:
                        new_weight = original_weight * 1.5
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
        if enemy.stats.max_hp > 0 and enemy.stats.hp <= enemy.stats.max_hp * 0.35:
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

    # ========================================================================
    # COORDINATED TACTICS METHODS
    # ========================================================================

    def _attempt_coordinated_tactics(self) -> set:
        """Attempt to execute coordinated tactics between multiple enemies.

        This method attempts to find and execute a coordinated tactic that
        multiple enemies can perform together. Coordinated tactics provide
        combo bonuses and more strategic enemy behavior.

        Performance optimization:
        - Caches available tactics per turn (computed once per turn)
        - Early exit if no tactics available or insufficient enemies

        Process:
        1. Gets available tactics (built-in + custom from AI profiles)
        2. Shuffles tactics for variety
        3. For each tactic:
           - Matches required roles to available enemies
           - Checks trigger conditions (HP, turn count, status effects)
           - If valid, executes tactic and assigns actions to participating enemies
        4. Only one coordinated tactic executes per turn

        Coordinated tactics provide:
        - Combo damage bonuses (e.g., 1.3x for pincer attack)
        - Role-based actions (tank guards, DPS attacks, healer heals)
        - Strategic timing based on conditions

        Returns:
            set: Enemy entity IDs participating in coordination. These enemies
                skip individual action selection in perform_enemy_actions().
                Returns empty set if:
                - tactics_coordinator is None
                - Fewer than 2 enemies are alive
                - No tactics are available or meet conditions

        Example tactics:
        - "pincer_attack": Two DPS enemies attack same target (1.3x damage)
        - "tank_and_spank": Tank guards while DPS attacks
        - "focus_fire": Multiple enemies focus weakest player (1.5x damage)
        - "heal_support": Healer heals while DPS attacks

        See also:
            TacticsCoordinator: Manages tactic cooldowns and availability
            CoordinatedTactic: Tactic definition with roles and conditions
        """
        if not self.tactics_coordinator:
            return set()

        alive_enemies = [e for e in self.enemies if e.is_alive()]
        if len(alive_enemies) < 2:
            return set()

        coordinated_ids = set()

        # Cache available tactics per turn (computed once per turn)
        cache_key = f"tactics_turn_{self.turn_counter}"
        if not hasattr(self, '_tactics_cache') or cache_key not in getattr(self, '_tactics_cache', {}):
            if not hasattr(self, '_tactics_cache'):
                self._tactics_cache = {}
            custom_tactics = self._get_custom_tactics_from_profiles()
            available_tactics = self.tactics_coordinator.get_available_tactics(custom_tactics)
            # Shuffle to add variety
            self.rng.shuffle(available_tactics)
            self._tactics_cache[cache_key] = available_tactics
            # Limit cache size (keep recent turns only)
            # Use numerical sorting to ensure proper FIFO eviction (not lexicographic)
            if len(self._tactics_cache) > _TACTICS_CACHE_MAX_TURNS:
                oldest_key = min(
                    (k for k in self._tactics_cache.keys() if k.startswith("tactics_turn_")),
                    key=lambda k: int(k.split("_")[-1])
                )
                del self._tactics_cache[oldest_key]
        else:
            available_tactics = self._tactics_cache[cache_key]

        # Early exit if no tactics available
        if not available_tactics:
            return set()

        for tactic in available_tactics:
            # Check if we have enough enemies with required roles
            role_assignments = self._match_roles_to_enemies(tactic.required_roles, alive_enemies, coordinated_ids)
            if not role_assignments:
                continue

            # Check trigger conditions
            if not self._check_tactic_conditions(tactic):
                continue

            # Execute the coordinated tactic
            if self.debug_ai:
                self.message_log.append(f"Enemies coordinate: {tactic.name}!")

            # Announce the tactic to the player with bonus info
            bonus_text = f"{tactic.combo_bonus:.1f}x" if tactic.combo_bonus != 1.0 else ""
            if bonus_text:
                self.message_log.append(f"TACTIC: The enemies coordinate a {tactic.name}! ({bonus_text} damage)")
            else:
                self.message_log.append(f"TACTIC: The enemies coordinate a {tactic.name}!")

            for role, enemy in role_assignments.items():
                action_template = tactic.actions.get(role)
                if not action_template:
                    # Use default action for role
                    action_template = {"type": "attack", "target_strategy": "random_enemy"}

                # Apply combo bonus
                enemy.combo_bonus = tactic.combo_bonus

                # Mark enemy as coordinating (for UI display)
                enemy.coordinated_action = {
                    "tactic_name": tactic.name,
                    "combo_bonus": tactic.combo_bonus
                }

                # Create command from action template
                cmd = self._create_command_from_action_dict(action_template, enemy)
                if cmd:
                    self.pending_commands.append(cmd)
                    coordinated_ids.add(enemy.entity.entity_id)

            # Mark tactic as used
            self.tactics_coordinator.use_tactic(tactic)

            # Only execute one coordinated tactic per turn
            break

        return coordinated_ids

    def _get_custom_tactics_from_profiles(self) -> List[CoordinatedTactic]:
        """Extract custom tactics defined in enemy AI profiles."""
        custom_tactics = []
        seen_ids = set()

        for enemy in self.enemies:
            if enemy.ai_profile and 'custom_tactics' in enemy.ai_profile:
                for tactic_data in enemy.ai_profile['custom_tactics']:
                    tactic_id = tactic_data.get('tactic_id')
                    if tactic_id and tactic_id not in seen_ids:
                        seen_ids.add(tactic_id)
                        custom_tactics.append(CoordinatedTactic(
                            tactic_id=tactic_id,
                            name=tactic_data.get('name', tactic_id),
                            required_roles=tactic_data.get('required_roles', ['dps', 'dps']),
                            min_enemies=tactic_data.get('min_enemies', 2),
                            cooldown_turns=tactic_data.get('cooldown_turns', 2),
                            trigger_conditions=tactic_data.get('trigger_conditions', {}),
                            actions=tactic_data.get('actions', {}),
                            combo_bonus=tactic_data.get('combo_bonus', 1.2)
                        ))

        return custom_tactics

    # ========================================================================
    # LEARNING AI METHODS
    # ========================================================================

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

"""Coordinated tactics execution driver for multi-enemy coordination.

This module provides the coordination logic that attempts to execute coordinated
tactics between multiple enemies. Coordinated tactics provide combo bonuses and
more strategic enemy behavior.

Coordinated tactics process:
    1. Gets available tactics (built-in + custom from AI profiles)
    2. Shuffles tactics for variety
    3. For each tactic:
       - Matches required roles to available enemies
       - Checks trigger conditions (HP, turn count, status effects)
       - If valid, executes tactic and assigns actions to participating enemies
    4. Only one coordinated tactic executes per turn

Performance optimization:
    - Caches available tactics per turn (computed once per turn)
    - Early exit if no tactics available or insufficient enemies
"""

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Set

if TYPE_CHECKING:
    from core.combat import BattleCommand, BattleParticipant
    from .tactics import TacticsCoordinator

from .tactics import CoordinatedTactic
from .ai_cache import AICacheMixin, _TACTICS_CACHE_MAX_TURNS


class TacticsDriverMixin(AICacheMixin):
    """Mixin providing coordinated tactics execution methods for AI systems.

    This mixin assumes the host class has:
    - self.enemies: List[BattleParticipant]
    - self.players: List[BattleParticipant]
    - self.turn_counter: int
    - self.debug_ai: bool
    - self.message_log: List[str]
    - self.rng: random.Random
    - self.pending_commands: List[BattleCommand]
    - self.tactics_coordinator: Optional[TacticsCoordinator]
    - self.enable_coordination: bool
    - self._match_roles_to_enemies(roles, enemies, assigned) -> Optional[Dict]
    - self._check_tactic_conditions(tactic) -> bool
    - self._create_command_from_action_dict(action, enemy) -> Optional[BattleCommand]
    - self._get_tactics_cache() -> Dict (from AICacheMixin)
    """

    def _attempt_coordinated_tactics(self) -> Set[str]:
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

        coordinated_ids: Set[str] = set()

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

"""Core battle system infrastructure.

This module contains the BattleSystemCore mixin which provides core battle
infrastructure methods for BattleSystem, including turn order, state management,
combo detection, and utility methods.
"""

from collections import defaultdict
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

if TYPE_CHECKING:
    from core.combat import BattleCommand, BattleParticipant, BattleState


class BattleSystemCore:
    """Mixin providing core battle infrastructure for BattleSystem.

    This mixin assumes the host class has:
    - self.players: List[BattleParticipant]
    - self.enemies: List[BattleParticipant]
    - self.skills: Dict[str, Skill]
    - self.items: Dict[str, Item]
    - self.message_log: List[str]
    - self.rng: random.Random
    - self.turn_order: List[BattleParticipant]
    - self.state: BattleState
    - self.pending_commands: List[BattleCommand]
    - self.turn_counter: int
    """

    def compute_turn_order(self) -> None:
        """Sort all alive participants by speed (Pokemon-style)."""
        all_participants = [p for p in self.players + self.enemies if p.is_alive()]
        all_participants.sort(key=lambda p: p.stats.get_effective_speed(), reverse=True)
        self.turn_order = all_participants

    def queue_player_command(self, cmd: "BattleCommand") -> None:
        """Queue a command from the player."""
        from core.combat import BattleState

        self.pending_commands.append(cmd)

        # Record player action for learning AI
        if self.learning_ai:
            self._record_player_action_for_learning(cmd)

        # If all players have acted, move to enemy phase
        if len(self.pending_commands) >= len([p for p in self.players if p.is_alive()]):
            self.state = BattleState.ENEMY_CHOOSE

    def perform_turn(self) -> None:
        """Resolve all queued commands in order."""
        from core.combat import BattleState

        if self.state != BattleState.RESOLVE_ACTIONS:
            return

        # Check for player combo attacks before processing
        self._apply_player_combo_bonuses()

        # Process commands in turn order
        commands_by_actor = {c.actor_id: c for c in self.pending_commands}
        for participant in self.turn_order:
            if not participant.is_alive():
                continue

            cmd = commands_by_actor.get(participant.entity.entity_id)
            if not cmd:
                continue

            self._execute_command(cmd, participant)

            # Escape immediately ends resolution for the round
            if self.state == BattleState.ESCAPED:
                break

        # Tick status effects
        for participant in self.players + self.enemies:
            if participant.is_alive():
                participant.stats.tick_status_effects()
            self._process_memory_boost_decay(participant)

        # Remove any guard bonuses now that the round is over
        self._reset_guard_bonuses()

        # Reset combo bonuses
        self._reset_combo_bonuses()

        # Clear commands
        self.pending_commands.clear()

        if self.state == BattleState.ESCAPED:
            return

        # Check battle end conditions
        if self.is_battle_over():
            result = self.get_result()
            if result == "victory":
                self.state = BattleState.VICTORY
            elif result == "defeat":
                self.state = BattleState.DEFEAT
        else:
            # Next turn
            self.compute_turn_order()
            self.state = BattleState.PLAYER_CHOOSE

    def _apply_player_combo_bonuses(self) -> None:
        """
        Detect and apply combo bonuses when multiple party members target the same enemy.

        Combo types:
        - Chain Attack (2+ attackers on same target): +20% damage per additional attacker
        - All-Out Attack (all alive players attack same target): +50% damage bonus
        - Elemental Combo (different elements on same target): +15% damage + chance for extra effect
        """
        from core.combat import ActionType

        # Get all player attack commands targeting enemies
        player_attacks: Dict[str, List[Tuple["BattleCommand", "BattleParticipant"]]] = defaultdict(list)

        for cmd in self.pending_commands:
            if cmd.action_type not in (ActionType.ATTACK, ActionType.SKILL):
                continue

            actor = self._find_participant(cmd.actor_id)
            if not actor or not actor.is_player_side:
                continue

            # Get target(s)
            for target_id in cmd.target_ids:
                target = self._find_participant(target_id)
                if target and not target.is_player_side:
                    player_attacks[target_id].append((cmd, actor))

        # Check for combos
        alive_players = len([p for p in self.players if p.is_alive()])

        for target_id, attacks in player_attacks.items():
            if len(attacks) < 2:
                continue

            target = self._find_participant(target_id)
            if not target:
                continue

            # Determine combo type and bonus
            combo_type = None
            combo_bonus = 1.0

            # All-Out Attack: all alive players attack same target
            if len(attacks) >= alive_players and alive_players >= 2:
                combo_type = "All-Out Attack"
                combo_bonus = 1.5
            # Chain Attack: 2+ attackers
            elif len(attacks) >= 2:
                combo_type = "Chain Attack"
                combo_bonus = 1.0 + (0.2 * (len(attacks) - 1))  # +20% per extra attacker

            # Check for elemental combo (different elements)
            elements = set()
            for cmd, actor in attacks:
                element = self._get_attack_element(cmd)
                if element and element != "physical":
                    elements.add(element)

            if len(elements) >= 2:
                combo_bonus += 0.15  # Extra 15% for elemental variety
                if combo_type:
                    combo_type += " + Elemental Fusion"
                else:
                    combo_type = "Elemental Fusion"

            # Apply combo bonus to all participating actors
            if combo_type:
                multiplier_text = f"{combo_bonus:.1f}x"
                self.message_log.append(f"COMBO: {combo_type}! ({multiplier_text} damage, {len(attacks)} attackers on {target.entity.name})")
                for cmd, actor in attacks:
                    actor.combo_bonus = combo_bonus

    def _get_attack_element(self, cmd: "BattleCommand") -> Optional[str]:
        """Get the element of an attack command."""
        if cmd.skill_id:
            # Check if it's a skill
            if cmd.skill_id in self.skills:
                return self.skills[cmd.skill_id].element
            # Check if it's a move
            from core.moves import get_moves_database
            moves_db = get_moves_database()
            move = moves_db.get_move(cmd.skill_id)
            if move:
                return move.element
        return "physical"

    def _reset_combo_bonuses(self) -> None:
        """Reset all combo bonuses and coordinated actions after turn resolution."""
        for participant in self.players + self.enemies:
            participant.combo_bonus = 1.0
            participant.coordinated_action = None

    def _reset_guard_bonuses(self) -> None:
        """Clear temporary guard defense bonuses at end of round."""
        for participant in self.players + self.enemies:
            if participant.guard_bonus:
                participant.stats.defense -= participant.guard_bonus
                participant.guard_bonus = 0

    def _process_memory_boost_decay(self, participant: "BattleParticipant") -> None:
        """Clear memory modifiers when boost expires."""
        if not participant or not getattr(participant, "stats", None):
            return
        if "memory_boost" in participant.stats.status_effects:
            return
        for key in list(participant.stats.equipment_modifiers.keys()):
            if key.startswith("memory_"):
                del participant.stats.equipment_modifiers[key]

    def is_battle_over(self) -> bool:
        """Check if battle is over.

        A battle ends when either:
        - All players are dead (HP <= 0)
        - All enemies are no longer active (dead OR spared)

        Note: Spared enemies are not considered 'alive' for battle purposes.
        The is_alive() check on BattleParticipant returns False if spared=True.
        """
        alive_players = [p for p in self.players if p.is_alive()]
        alive_enemies = [e for e in self.enemies if e.is_alive()]
        return len(alive_players) == 0 or len(alive_enemies) == 0

    def get_result(self) -> str:
        """Get battle result: 'victory', 'defeat', or 'escaped'."""
        from core.combat import BattleState

        if self.state == BattleState.ESCAPED:
            return "escaped"

        alive_players = [p for p in self.players if p.is_alive()]
        if len(alive_players) == 0:
            return "defeat"

        alive_enemies = [e for e in self.enemies if e.is_alive()]
        if len(alive_enemies) == 0:
            return "victory"

        return "ongoing"

    def _find_participant(self, entity_id: str) -> Optional["BattleParticipant"]:
        """Find a participant by entity ID."""
        for p in self.players + self.enemies:
            if p.entity.entity_id == entity_id:
                return p
        return None

    def _get_targets(
        self,
        pattern: str,
        target_ids: List[str],
        actor: "BattleParticipant"
    ) -> List["BattleParticipant"]:
        """Get targets based on target pattern."""
        if pattern == "single_enemy":
            if actor.is_player_side:
                return [self._find_participant(target_ids[0])] if target_ids else []
            else:
                return [self._find_participant(target_ids[0])] if target_ids else []
        elif pattern == "all_enemies":
            if actor.is_player_side:
                return [e for e in self.enemies if e.is_alive()]
            else:
                return [p for p in self.players if p.is_alive()]
        elif pattern == "self":
            return [actor]
        elif pattern == "single_ally":
            if actor.is_player_side:
                return [self._find_participant(target_ids[0])] if target_ids else []
            else:
                return [self._find_participant(target_ids[0])] if target_ids else []
        elif pattern == "all_allies":
            if actor.is_player_side:
                return [p for p in self.players if p.is_alive()]
            else:
                return [e for e in self.enemies if e.is_alive()]
        return []

    def _get_formation_modifiers(
        self,
        actor: "BattleParticipant",
        target: "BattleParticipant"
    ) -> Tuple[float, float]:
        """
        Get formation-based attack and defense modifiers.

        Returns:
            Tuple of (attack_mod, defense_mod) where:
            - attack_mod: Bonus/penalty to attacker's damage (e.g., 0.1 = +10%)
            - defense_mod: Bonus/penalty to target's damage reduction (e.g., 0.1 = -10% damage taken)
        """
        from core.constants import FORMATION_POSITIONS, DEFAULT_FORMATION_POSITION

        attack_mod = 0.0
        defense_mod = 0.0

        # Get attacker's formation position
        if actor.is_player_side:
            actor_entity = actor.entity
            if hasattr(actor_entity, "formation_position"):
                position = actor_entity.formation_position
                mods = FORMATION_POSITIONS.get(position, FORMATION_POSITIONS[DEFAULT_FORMATION_POSITION])
                attack_mod = mods.get("attack_mod", 0.0)

        # Get target's formation position for defense
        if target.is_player_side:
            target_entity = target.entity
            if hasattr(target_entity, "formation_position"):
                position = target_entity.formation_position
                mods = FORMATION_POSITIONS.get(position, FORMATION_POSITIONS[DEFAULT_FORMATION_POSITION])
                defense_mod = mods.get("defense_mod", 0.0)

        return attack_mod, defense_mod

    def _hp_percent(self, participant: "BattleParticipant") -> float:
        """Return HP percentage for a participant."""
        if participant.stats.max_hp <= 0:
            return 0.0
        return (participant.stats.hp / participant.stats.max_hp) * 100

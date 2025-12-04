"""Action execution for the combat system.

This module contains the ActionExecutorMixin which provides all action
execution methods for BattleSystem (attack, skill, item, guard, talk, flee).

The module uses the ActionHandler pattern (see action_handlers.py) to dispatch
actions to appropriate handlers, replacing the previous if/elif chains.
"""

from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from core.combat import BattleCommand, BattleParticipant, BattleState

from .action_handlers import get_action_handler_registry


class ActionExecutorMixin:
    """Mixin providing action execution methods for BattleSystem.

    This mixin assumes the host class has:
    - self.players: List[BattleParticipant]
    - self.enemies: List[BattleParticipant]
    - self.skills: Dict[str, Skill]
    - self.items: Dict[str, Item]
    - self.message_log: List[str]
    - self.rng: random.Random
    - self.rigged: bool
    - self._find_participant(entity_id) -> Optional[BattleParticipant]
    - self._get_targets(pattern, target_ids, actor) -> List[BattleParticipant]
    - self._get_formation_modifiers(actor, target) -> Tuple[float, float]
    - self._hp_percent(participant) -> float
    """

    def _execute_command(self, cmd: "BattleCommand", actor: "BattleParticipant") -> None:
        """Execute a battle command.

        This is the main entry point for action execution. It handles:
        1. Checking for incapacitating status effects (stun, sleep, frozen)
        2. Applying confusion effects (may redirect attacks)
        3. Routing to specific action handlers based on action type

        Action types handled:
        - ATTACK: Physical attack with damage calculation
        - SKILL: Skill/ability use with SP cost and effects
        - ITEM: Item consumption with various effects
        - GUARD: Defense boost for the turn
        - TALK: Undertale-style mercy/spare mechanic
        - FLEE: Escape attempt with success chance calculation
        - MEMORY: Calculator-style memory operations (M+, M-, MR, MC)

        Args:
            cmd: The battle command to execute
            actor: The participant executing the command

        Status effects that prevent action:
        - stun: Cannot act
        - sleep: Cannot act (wakes on damage)
        - frozen: Cannot act

        Confusion handling:
        - 50% chance confusion doesn't trigger
        - 25% chance to hit self
        - 75% chance to hit random target (ally or enemy)

        See also:
            _execute_attack: Physical attack execution
            _execute_skill: Skill execution
            _execute_item: Item use execution
            _execute_memory: Memory system operations
        """
        from core.combat import ActionType, BattleState

        # Check for incapacitating status effects
        if not actor.stats.can_act():
            incap_effect = self._get_incapacitating_effect_name(actor)
            self.message_log.append(f"{actor.entity.name} is {incap_effect} and cannot act!")
            return

        # Handle confusion - may redirect attack/skill to wrong target
        if actor.stats.is_confused() and cmd.action_type in (ActionType.ATTACK, ActionType.SKILL):
            cmd = self._apply_confusion(cmd, actor)

        # Dispatch to appropriate action handler via registry
        registry = get_action_handler_registry()
        if not registry.execute(self, cmd, actor):
            # Fallback for unknown action types (shouldn't happen with complete registry)
            self.message_log.append(f"{actor.entity.name} does nothing...")

    def _get_incapacitating_effect_name(self, actor: "BattleParticipant") -> str:
        """Get a display name for the incapacitating effect."""
        if "stun" in actor.stats.status_effects:
            return "stunned"
        if "sleep" in actor.stats.status_effects:
            return "asleep"
        if "frozen" in actor.stats.status_effects:
            return "frozen"
        return "incapacitated"

    def _apply_confusion(self, cmd: "BattleCommand", actor: "BattleParticipant") -> "BattleCommand":
        """Apply confusion effect - 50% chance to redirect attack to random target or self."""
        from core.combat import BattleCommand

        if self.rng.random() < 0.5:
            # Confusion doesn't trigger
            return cmd

        self.message_log.append(f"{actor.entity.name} is confused!")

        # 25% chance to hit self, 75% chance to hit random other target
        if self.rng.random() < 0.25:
            # Hit self
            new_cmd = BattleCommand(
                actor_id=cmd.actor_id,
                action_type=cmd.action_type,
                skill_id=cmd.skill_id,
                item_id=cmd.item_id,
                target_ids=[actor.entity.entity_id]
            )
            return new_cmd
        else:
            # Hit random target (could be ally or enemy)
            all_alive = [p for p in self.players + self.enemies if p.is_alive() and p != actor]
            if all_alive:
                random_target = self.rng.choice(all_alive)
                new_cmd = BattleCommand(
                    actor_id=cmd.actor_id,
                    action_type=cmd.action_type,
                    skill_id=cmd.skill_id,
                    item_id=cmd.item_id,
                    target_ids=[random_target.entity.entity_id]
                )
                return new_cmd

        return cmd

    def _execute_attack(self, cmd: "BattleCommand", actor: "BattleParticipant") -> None:
        """Execute an attack, optionally using a specific move."""
        if not cmd.target_ids:
            return

        target_id = cmd.target_ids[0]
        target = self._find_participant(target_id)
        if not target or not target.is_alive():
            return

        # Reset last-damage tracking for this attack
        actor.last_damage_dealt = 0
        target.last_damage_received = 0

        # Check if a specific move is being used (stored in skill_id for attacks)
        move = None
        move_name = "attack"
        move_power = 0
        move_element = "physical"
        move_accuracy = 100
        move_hits = 1
        move_status_id = None
        move_status_chance = 0.0

        if cmd.skill_id:
            # Try to load move from moves database
            from core.moves import get_moves_database
            moves_db = get_moves_database()
            move = moves_db.get_move(cmd.skill_id)
            if move:
                move_name = move.name
                move_power = move.power
                move_element = move.element
                move_accuracy = move.accuracy
                move_hits = move.hits
                move_status_id = move.status_inflict_id
                move_status_chance = move.status_chance

        # Rigged mode: enemy attacks always miss or deal minimal damage
        if self.rigged and not actor.is_player_side:
            # 70% chance to miss, 30% chance to deal 0-1 damage
            if self.rng.random() < 0.7:
                self.message_log.append(f"{actor.entity.name}'s attack missed!")
                return
            else:
                # Deal 0-1 damage (will likely be reduced to 0 by defense)
                damage = self.rng.randint(0, 1)
                old_hp = target.stats.hp
                if damage > 0:
                    target.stats.hp = max(0, target.stats.hp - damage)
                actual_damage = old_hp - target.stats.hp
                actor.last_damage_dealt = actual_damage
                target.last_damage_received = actual_damage
                self.message_log.append(
                    f"{actor.entity.name} attacks {target.entity.name} for {actual_damage} damage!"
                )
                return

        # Check accuracy
        if self.rng.randint(1, 100) > move_accuracy:
            self.message_log.append(f"{actor.entity.name}'s {move_name} missed!")
            return

        # Calculate base damage (use cached stats for performance)
        current_turn = getattr(self, 'turn_counter', 0)
        attack_power = actor.get_cached_effective_attack(current_turn)
        base_damage = attack_power + move_power + self.rng.randint(-2, 2)

        # Apply formation modifiers
        attack_mod, defense_mod = self._get_formation_modifiers(actor, target)
        base_damage = int(base_damage * (1.0 + attack_mod))

        # Apply elemental weakness/resistance if not physical
        element_mult = 1.0
        affinity = "neutral"
        if move_element != "physical":
            element_mult, affinity = target.stats.get_element_multiplier(move_element)

        # Handle multi-hit moves
        total_damage = 0
        combo_applied = actor.combo_bonus > 1.0
        for hit in range(move_hits):
            damage = int(base_damage * element_mult)

            # Apply combo bonus
            if actor.combo_bonus > 1.0:
                damage = int(damage * actor.combo_bonus)

            # Critical hit chance based on luck (use cached stats)
            is_crit = False
            current_turn = getattr(self, 'turn_counter', 0)
            if self.rng.random() < (actor.get_cached_effective_luck(current_turn) / 100.0):
                damage = int(damage * 1.5)
                is_crit = True

            # Handle absorption (negative multiplier = healing)
            if element_mult < 0:
                heal_amount = int(abs(damage))
                target.stats.heal(heal_amount)
                if hit == 0:
                    self.message_log.append(
                        f"{actor.entity.name} uses {move_name} on {target.entity.name}!"
                    )
                    self.message_log.append(
                        f"{target.entity.name} absorbs {move_element} and heals {heal_amount} HP!"
                    )
                continue
            elif element_mult == 0:
                # Immune - no damage
                if hit == 0:
                    self.message_log.append(
                        f"{actor.entity.name} uses {move_name} on {target.entity.name}!"
                    )
                    self.message_log.append(
                        f"{target.entity.name} is immune to {move_element}!"
                    )
                continue

            # Apply formation defense modifier
            damage = int(damage * (1.0 - defense_mod))
            damage = max(0, damage)

            old_hp = target.stats.hp
            target.stats.apply_damage(damage)
            actual_damage = old_hp - target.stats.hp
            total_damage += actual_damage

            if is_crit and hit == 0:
                self.message_log.append(f"{actor.entity.name} lands a critical hit!")

        # Log the attack result
        if move:
            self.message_log.append(
                f"{actor.entity.name} uses {move_name} on {target.entity.name} for {total_damage} damage!"
            )
        else:
            self.message_log.append(
                f"{actor.entity.name} attacks {target.entity.name} for {total_damage} damage!"
            )

        # Log elemental effectiveness
        if affinity == "weak":
            self.message_log.append(f"It's super effective! {target.entity.name} is weak to {move_element}!")
        elif affinity == "resist":
            self.message_log.append(f"It's not very effective... {target.entity.name} resists {move_element}.")

        # Apply status effect if move has one
        if move_status_id and self.rng.random() < move_status_chance:
            target.stats.add_status_effect(move_status_id, duration=3)
            self.message_log.append(f"{target.entity.name} is afflicted with {move_status_id}!")

        # Wake sleeping targets when damaged
        if target.stats.wake_from_sleep():
            self.message_log.append(f"{target.entity.name} woke up!")

        # Track damage for memory system
        actor.last_damage_dealt = total_damage
        target.last_damage_received = total_damage

        # Life drain mechanic: enemies heal when they damage players
        if total_damage > 0 and not actor.is_player_side and target.is_player_side:
            lifesteal_rate = getattr(self, "battle_context", {}).get("enemy_lifesteal", 0.0)
            if lifesteal_rate > 0.0:
                heal_amount = int(total_damage * lifesteal_rate)
                if heal_amount > 0:
                    old_hp = actor.stats.hp
                    actor.stats.heal(heal_amount)
                    actual_heal = actor.stats.hp - old_hp
                    if actual_heal > 0:
                        self.message_log.append(
                            f"{actor.entity.name} drains {actual_heal} HP from the damage!"
                        )

    def _execute_skill(self, cmd: "BattleCommand", actor: "BattleParticipant") -> None:
        """Execute a skill."""
        if not cmd.skill_id or cmd.skill_id not in self.skills:
            return

        skill = self.skills[cmd.skill_id]

        # Check SP cost
        if actor.stats.sp < skill.cost_sp:
            self.message_log.append(f"{actor.entity.name} doesn't have enough SP!")
            return

        actor.stats.sp -= skill.cost_sp

        # Get targets based on pattern
        targets = self._get_targets(skill.target_pattern, cmd.target_ids, actor)
        current_turn = getattr(self, 'turn_counter', 0)

        for target in targets:
            if not target or not target.is_alive():
                continue

            # Handle healing skills differently
            if skill.element == "holy" and skill.target_pattern in ["single_ally", "all_allies"]:
                # Healing skill
                before = target.stats.hp
                target.stats.heal(skill.power)
                healed = target.stats.hp - before
                self.message_log.append(
                    f"{actor.entity.name} uses {skill.name} on {target.entity.name} and heals {healed} HP!"
                )
            else:
                # Damage skill
                base_damage = skill.power
                if actor.is_player_side:
                    base_damage += actor.get_cached_effective_magic(current_turn)
                else:
                    # Enemy spells should scale from magic to respect caster stats
                    offensive_stat = (
                        actor.get_cached_effective_magic(current_turn)
                        if skill.element != "physical"
                        else actor.get_cached_effective_attack(current_turn)
                    )
                    base_damage += offensive_stat

                damage = base_damage + self.rng.randint(-3, 3)

                # Apply combo bonus
                if actor.combo_bonus > 1.0:
                    damage = int(damage * actor.combo_bonus)

                # Apply elemental weakness/resistance multiplier
                element_mult, affinity = target.stats.get_element_multiplier(skill.element)

                # Handle absorption (negative multiplier = healing)
                if element_mult < 0:
                    heal_amount = int(abs(damage * element_mult))
                    target.stats.heal(heal_amount)
                    self.message_log.append(
                        f"{actor.entity.name} uses {skill.name} on {target.entity.name}!"
                    )
                    self.message_log.append(
                        f"{target.entity.name} absorbs {skill.element} and heals {heal_amount} HP!"
                    )
                elif element_mult == 0:
                    # Immune - no damage
                    self.message_log.append(
                        f"{actor.entity.name} uses {skill.name} on {target.entity.name}!"
                    )
                    self.message_log.append(
                        f"{target.entity.name} is immune to {skill.element}!"
                    )
                else:
                    # Apply multiplier to damage
                    damage = int(damage * element_mult)
                    old_hp = target.stats.hp
                    target.stats.apply_damage(damage)
                    actual_damage = old_hp - target.stats.hp

                    # Build message with affinity feedback
                    msg = f"{actor.entity.name} uses {skill.name} on {target.entity.name} for {actual_damage} damage!"
                    self.message_log.append(msg)

                    if affinity == "weak":
                        self.message_log.append(f"It's super effective! {target.entity.name} is weak to {skill.element}!")
                    elif affinity == "resist":
                        self.message_log.append(f"It's not very effective... {target.entity.name} resists {skill.element}.")

                    # Apply status effect (only on actual damage)
                    if skill.status_inflict_id and self.rng.random() < skill.status_chance:
                        target.stats.add_status_effect(skill.status_inflict_id, duration=3)
                        self.message_log.append(f"{target.entity.name} is afflicted with {skill.status_inflict_id}!")

                    # Wake sleeping targets when damaged
                    if target.stats.wake_from_sleep():
                        self.message_log.append(f"{target.entity.name} woke up!")

    def _execute_item(self, cmd: "BattleCommand", actor: "BattleParticipant") -> None:
        """Execute item use.

        Uses the item_effects registry to dispatch to the appropriate handler.
        This replaces the previous large if/elif chain with a cleaner registry pattern.
        """
        from core.combat import BattleState
        from .item_effects import execute_item_effect

        if not cmd.item_id or cmd.item_id not in self.items:
            self.message_log.append(f"{actor.entity.name} fumbles with an unknown item...")
            return

        item = self.items[cmd.item_id]

        # Check both player inventory and enemy items
        inventory = getattr(actor.entity, "inventory", None)
        enemy_items = actor.items if not actor.is_player_side else {}

        has_item = False
        if inventory is not None and inventory.has(item.id, 1):
            has_item = True
        elif enemy_items and enemy_items.get(item.id, 0) > 0:
            has_item = True

        if not has_item:
            self.message_log.append(f"{actor.entity.name} has no {item.name} left!")
            return

        target = actor  # Default to self-targeting for consumables
        if cmd.target_ids:
            target_participant = self._find_participant(cmd.target_ids[0])
            if target_participant and target_participant.is_alive():
                target = target_participant

        # Build context for effect handlers
        context = {
            "participants": self.participants,
            "is_boss_battle": self._is_boss_battle(),
        }

        # Execute the effect using the registry
        result = execute_item_effect(item.effect_id, actor, target, item, context)

        # Add messages to battle log
        for message in result.messages:
            self.message_log.append(message)

        # Handle state changes (e.g., escape)
        if result.state_change == "escaped":
            self.state = BattleState.ESCAPED

        # Consume item from player inventory or enemy items (only if effect was handled)
        if result.success:
            if inventory is not None:
                inventory.remove(item.id, 1)
            elif enemy_items:
                enemy_items[item.id] = enemy_items.get(item.id, 0) - 1
                if enemy_items[item.id] <= 0:
                    del enemy_items[item.id]

    def _execute_guard(self, cmd: "BattleCommand", actor: "BattleParticipant") -> None:
        """Execute guard action."""
        # Apply a temporary defense boost for the rest of this round
        if actor.guard_bonus:
            actor.stats.defense -= actor.guard_bonus
        actor.guard_bonus = 5
        actor.stats.defense += actor.guard_bonus
        self.message_log.append(f"{actor.entity.name} guards!")

    def _execute_talk(self, cmd: "BattleCommand", actor: "BattleParticipant") -> None:
        """Execute talk action (Undertale-style mercy mechanic)."""
        if not cmd.target_ids:
            return

        target_id = cmd.target_ids[0]
        target = self._find_participant(target_id)
        if not target or not target.is_alive():
            return
        if target.spared:
            self.message_log.append(f"{target.entity.name} is already calm.")
            return

        # Get spare configuration from entity with type validation
        entity = target.entity
        spareable = getattr(entity, "spareable", True)  # Default: all enemies can be spared

        spare_threshold = getattr(entity, "spare_threshold", self.spare_threshold)
        if not isinstance(spare_threshold, (int, float)):
            spare_threshold = self.spare_threshold

        spare_hp_threshold = getattr(entity, "spare_hp_threshold", 100)  # HP % below which sparing is easier
        if not isinstance(spare_hp_threshold, (int, float)):
            spare_hp_threshold = 100

        spare_messages = getattr(entity, "spare_messages", {})

        # Check if enemy is spareable
        if not spareable:
            self.message_log.append(f"{target.entity.name} refuses to listen!")
            return

        # Calculate HP percentage (default to 100% if max_hp is somehow 0 to avoid division by zero)
        hp_percent = (target.stats.hp / target.stats.max_hp * 100) if target.stats.max_hp > 0 else 100

        # Base morale increase
        morale_gain = 1

        # Bonus morale if HP is below threshold (enemy is weakened and more receptive)
        if hp_percent <= spare_hp_threshold:
            morale_gain = 2
            self.message_log.append(f"{actor.entity.name} reaches out to {target.entity.name}...")
        else:
            self.message_log.append(f"{actor.entity.name} talks to {target.entity.name}...")

        target.morale += morale_gain

        # Display contextual spare message based on morale progress
        morale_ratio = target.morale / spare_threshold
        if spare_messages:
            if morale_ratio >= 1.0:
                pass  # Will be spared, message handled below
            elif morale_ratio >= 0.6:
                if "ready" in spare_messages:
                    self.message_log.append(spare_messages["ready"])
            elif morale_ratio >= 0.3:
                if "wavering" in spare_messages:
                    self.message_log.append(spare_messages["wavering"])
            else:
                if "not_ready" in spare_messages:
                    self.message_log.append(spare_messages["not_ready"])

        # If morale high enough, enemy can be spared
        if target.morale >= spare_threshold:
            target.spared = True
            if spare_messages and "spared" in spare_messages:
                self.message_log.append(spare_messages["spared"])
            else:
                self.message_log.append(f"{target.entity.name} seems more friendly now and leaves the fight!")

    def _execute_flee(self, cmd: "BattleCommand", actor: "BattleParticipant") -> None:
        """Execute flee action with proper success rate calculation."""
        from core.combat import BattleState

        # Check if this is a boss battle (escape should be blocked or very difficult)
        is_boss_battle = self._is_boss_battle()

        if is_boss_battle:
            self.message_log.append(f"{actor.entity.name} tries to flee, but there's no escaping this battle!")
            return

        flee_chance = self._calculate_flee_chance(actor)

        if self.rng.random() < flee_chance:
            self.state = BattleState.ESCAPED
            self.message_log.append(f"{actor.entity.name} fled!")
        else:
            self.message_log.append(f"{actor.entity.name} couldn't escape!")

    def _calculate_flee_chance(self, actor: "BattleParticipant") -> float:
        """
        Calculate flee success rate based on multiple factors.

        Formula: base_chance + speed_bonus - enemy_penalty + luck_bonus + turn_bonus
        - Base chance: 30%
        - Speed bonus: (actor_speed - avg_enemy_speed) / 100, capped at +/-20%
        - Luck bonus: actor_luck / 200, capped at 10%
        - Turn bonus: 5% per turn (encourages fleeing after failed attempts)
        - Low HP bonus: +15% if actor HP < 25%

        Final chance is clamped between 10% (always some hope) and 95% (never guaranteed).
        """
        base_chance = 0.30

        # Calculate average enemy speed
        alive_enemies = [e for e in self.enemies if e.is_alive()]
        if alive_enemies:
            current_turn = getattr(self, 'turn_counter', 0)
            avg_enemy_speed = sum(e.get_cached_effective_speed(current_turn) for e in alive_enemies) / len(alive_enemies)
        else:
            avg_enemy_speed = 0

        current_turn = getattr(self, 'turn_counter', 0)
        actor_speed = actor.get_cached_effective_speed(current_turn)

        # Speed differential bonus/penalty (capped at +/-20%)
        speed_diff = (actor_speed - avg_enemy_speed) / 100.0
        speed_bonus = max(-0.20, min(0.20, speed_diff))

        # Luck bonus (up to 10%)
        current_turn = getattr(self, 'turn_counter', 0)
        luck_bonus = min(0.10, actor.get_cached_effective_luck(current_turn) / 200.0)

        # Turn bonus (5% per turn, up to 25%)
        turn_bonus = min(0.25, self.turn_counter * 0.05)

        # Low HP desperation bonus
        hp_percent = actor.stats.hp / actor.stats.max_hp if actor.stats.max_hp > 0 else 1.0
        low_hp_bonus = 0.15 if hp_percent < 0.25 else 0.0

        # Calculate final chance
        flee_chance = base_chance + speed_bonus + luck_bonus + turn_bonus + low_hp_bonus

        # Clamp between 10% and 95%
        return max(0.10, min(0.95, flee_chance))

    def _execute_memory(self, cmd: "BattleCommand", actor: "BattleParticipant") -> None:
        """Execute a memory operation (store/recall/subtract/clear).

        The memory system provides calculator-style stat manipulation:

        Operations:
            M+ (STORE): Store a stat value in memory. Overwrites any existing value.
            M- (SUBTRACT): Subtract a stat value from the stored memory (floor at 0).
            MR (RECALL): Apply stored value as a temporary buff (see _apply_memory_recall).
            MC (CLEAR): Reset memory to 0 and clear the stat type.

        Supported stats for store/subtract:
            - attack: Effective attack power
            - defense: Effective defense
            - magic: Effective magic power
            - speed: Effective speed
            - current_hp: Current HP (not max)
            - last_damage: Damage dealt in the last attack

        Design notes:
            - Memory persists across turns until recalled or cleared
            - Recall applies half the stored value as a buff (to prevent overpowered stacking)
            - current_hp and last_damage can be stored but don't apply buffs on recall
              (they're tracked for strategic value, e.g., storing damage for comparison)
        """
        from core.combat import MemoryOperation

        op = cmd.memory_operation
        stat_type = cmd.memory_stat

        if op is None:
            return

        if op == MemoryOperation.STORE:
            value = self._get_memory_stat_value(actor, stat_type)
            actor.memory_value = value
            actor.memory_stat_type = stat_type
            self.message_log.append(f"{actor.entity.name} stores {stat_type}: {value}!")

        elif op == MemoryOperation.SUBTRACT:
            value = self._get_memory_stat_value(actor, stat_type)
            actor.memory_value = max(0, actor.memory_value - value)
            self.message_log.append(
                f"{actor.entity.name} subtracts {value}. Memory: {actor.memory_value}"
            )

        elif op == MemoryOperation.RECALL:
            if actor.memory_value > 0:
                applied_buff = self._apply_memory_recall(actor)
                if applied_buff > 0:
                    self.message_log.append(
                        f"{actor.entity.name} recalls {actor.memory_stat_type}! +{applied_buff} boost!"
                    )
                else:
                    self.message_log.append(
                        f"{actor.entity.name} recalls {actor.memory_stat_type}, but it has no combat effect!"
                    )
            else:
                self.message_log.append(f"{actor.entity.name} has no stored memory!")

        elif op == MemoryOperation.CLEAR:
            actor.memory_value = 0
            actor.memory_stat_type = None
            self.message_log.append(f"{actor.entity.name} clears memory.")

    def _get_memory_stat_value(self, actor: "BattleParticipant", stat_type: Optional[str]) -> int:
        """Get the value of a stat for memory storage.

        Args:
            actor: The battle participant whose stat to read
            stat_type: The stat type to get ("attack", "defense", "magic",
                      "speed", "current_hp", "last_damage")

        Returns:
            The current value of the specified stat, or 0 if invalid/None
        """
        if not stat_type:
            return 0

        stat_map = {
            "attack": lambda: actor.get_cached_effective_attack(getattr(self, 'turn_counter', 0)),
            "defense": lambda: actor.get_cached_effective_defense(getattr(self, 'turn_counter', 0)),
            "magic": lambda: actor.get_cached_effective_magic(getattr(self, 'turn_counter', 0)),
            "speed": lambda: actor.get_cached_effective_speed(getattr(self, 'turn_counter', 0)),
            "current_hp": lambda: actor.stats.hp,
            "last_damage": lambda: actor.last_damage_dealt,
        }

        if stat_type in stat_map:
            return stat_map[stat_type]()

        # Unknown stat type - log warning for debugging
        from core.logging_utils import log_warning
        log_warning(f"Unknown memory stat type requested: {stat_type}")
        return 0

    def _apply_memory_recall(self, actor: "BattleParticipant") -> int:
        """Apply memory recall as a temporary stat buff.

        The buff applies half the stored value to prevent overpowered stacking.
        For example, storing attack=20 and recalling gives +10 attack.

        Only combat stats (attack, defense, magic, speed) receive buffs.
        Non-combat stats (current_hp, last_damage) don't apply buffs but can
        still be stored for strategic purposes like damage comparison.

        The buff is tracked via 'memory_boost' status effect (2 turn duration).
        When the status expires, _process_memory_boost_decay clears the modifiers.

        Args:
            actor: The battle participant to apply the buff to

        Returns:
            The amount of buff applied (0 if non-combat stat)
        """
        stat_type = actor.memory_stat_type
        value = actor.memory_value

        if stat_type in ("attack", "defense", "magic", "speed"):
            applied_buff = value // 2
            current = actor.stats.equipment_modifiers.get(f"memory_{stat_type}", 0)
            actor.stats.equipment_modifiers[f"memory_{stat_type}"] = current + applied_buff
            actor.stats.add_status_effect("memory_boost", duration=2)
            return applied_buff

        # Non-combat stats don't apply buffs
        return 0

    def _is_boss_battle(self) -> bool:
        """Check if this is a boss battle by examining enemies."""
        # Check if any enemy is a boss
        for enemy in self.enemies:
            entity = enemy.entity
            # Check difficulty field
            if hasattr(entity, "difficulty") and entity.difficulty == "boss":
                return True
            # Check is_boss attribute
            if getattr(entity, "is_boss", False):
                return True
            # Check enemy type
            if hasattr(entity, "enemy_type") and entity.enemy_type == "boss":
                return True
        return False

    @property
    def participants(self) -> List["BattleParticipant"]:
        """Get all battle participants."""
        return self.players + self.enemies

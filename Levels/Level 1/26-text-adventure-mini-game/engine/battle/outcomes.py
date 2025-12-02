"""Battle outcome handling logic.

This module contains victory, defeat, and escape handling logic
for battle scenes, including reward distribution and achievements.
"""

from typing import Optional, List, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from core.moves import Move
    from core.combat import BattleState


class BattleOutcomesMixin:
    """Mixin providing battle outcome handling for BattleScene.

    This mixin handles:
    - Victory, defeat, and escape state transitions
    - Reward distribution (items, gold, EXP)
    - Achievement tracking
    - Bestiary updates
    - Ending determination and transitions

    Attributes expected from host class:
        battle_system: BattleSystem instance
        world: World instance for flags
        player: Player entity
        message_box: MessageBox for displaying messages
        encounter_id: Current encounter identifier
        manager: SceneManager for scene transitions
        rewards: Dict of encounter rewards
        source_trigger: Trigger that started the battle
        scale: Display scale factor
        assets: AssetManager instance
        moves_db: Moves database
    """

    def _handle_victory(self) -> None:
        """Handle battle victory."""
        from core.combat import BattleState

        self._finalize_outcome("victory")

        # Revive all defeated party members after victory
        self._revive_defeated_party_members()

        if not self._rewards_applied:
            self._rewards_applied = True
            reward_message_set = self._apply_rewards()
        else:
            reward_message_set = False

        # Set final_boss_defeated flag for final boss encounters
        if self.encounter_id == "final_boss" and self.battle_system.state == BattleState.VICTORY:
            self.world.set_flag("final_boss_defeated", True)

        # Check if this is the final boss and transition to ending
        if self.encounter_id == "final_boss" and self.battle_system.state == BattleState.VICTORY:
            self._transition_to_ending()
            return

        if not reward_message_set:
            summary = self._build_battle_summary()
            if self._victory_spared:
                self.message_box.set_text(f"You spared your foes. Peace wins the day!\n{summary}\nPress Enter to continue...")
            else:
                self.message_box.set_text(f"Victory! {summary}\nPress Enter to continue...")

    def _handle_defeat(self) -> None:
        """Handle battle defeat."""
        self._finalize_outcome("defeat")

        alive_enemies = [e for e in self.battle_system.enemies if e.is_alive()]
        enemy_count = len(alive_enemies)
        enemy_names = [e.entity.name[:15] for e in alive_enemies[:3]]

        if enemy_count == 0:
            defeat_msg = "Defeat! All enemies fell, but so did your party.\n"
        elif enemy_count == 1:
            defeat_msg = f"Defeat! {enemy_names[0]} remains.\n"
        elif enemy_count <= 3:
            defeat_msg = f"Defeat! {', '.join(enemy_names)} remain.\n"
        else:
            defeat_msg = f"Defeat! {enemy_count} enemies remain.\n"

        defeat_msg += "Tip: Level up or try new strategies.\nPress Enter to continue..."
        self.message_box.set_text(defeat_msg)

    def _handle_escape(self) -> None:
        """Handle successful escape."""
        self._finalize_outcome("escaped")

        alive_players = [p for p in self.battle_system.players if p.is_alive()]
        alive_count = len(alive_players)
        total_players = len(self.battle_system.players)

        escape_msg = "You escaped the battle!\n"

        if alive_count < total_players:
            escape_msg += f"Warning: {total_players - alive_count} party member(s) are unconscious.\n"

        if self.player.stats:
            hp_percent = (self.player.stats.hp / self.player.stats.max_hp * 100) if self.player.stats.max_hp > 0 else 0
            if hp_percent < 25:
                escape_msg += f"Your HP is critically low ({int(hp_percent)}%).\n"
            elif hp_percent < 50:
                escape_msg += f"Your HP is low ({int(hp_percent)}%).\n"

        escape_msg += "No rewards were earned. Press Enter to continue..."
        self.message_box.set_text(escape_msg)

    def _get_flag_as_int(self, flag_name: str, default: int = 0) -> int:
        """Safely get a world flag value as an integer."""
        value = self.world.get_flag(flag_name)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return default
        return int(value)

    def _increment_flag(self, flag_name: str, amount: int = 1) -> None:
        """Increment an integer world flag safely."""
        current = self._get_flag_as_int(flag_name, 0)
        self.world.set_flag(flag_name, current + amount)

    def _revive_defeated_party_members(self) -> None:
        """Revive all defeated party members after winning a battle."""
        from core.logging_utils import log_warning

        if self.player.stats and self.player.stats.hp <= 0:
            log_warning("Player was dead on victory - this indicates a logic error")
            self.player.stats.hp = max(1, self.player.stats.max_hp // 4)

        for member in getattr(self.player, "party", []):
            if member and member.stats and member.stats.hp <= 0:
                member.stats.hp = 1

    def _build_battle_summary(self) -> str:
        """Build a summary of battle statistics."""
        parts = []

        turns = self.battle_system.turn_counter
        if turns > 0:
            parts.append(f"Turns: {turns}")

        spared_count = sum(1 for e in self.battle_system.enemies if getattr(e, "spared", False))
        defeated_count = sum(1 for e in self.battle_system.enemies if not e.is_alive() and not getattr(e, "spared", False))

        if spared_count > 0 and defeated_count > 0:
            parts.append(f"Enemies: {spared_count} spared, {defeated_count} defeated")
        elif spared_count > 0:
            parts.append(f"Enemies: {spared_count} spared")
        elif defeated_count > 0:
            parts.append(f"Enemies: {defeated_count} defeated")

        alive_count = sum(1 for p in self.battle_system.players if p.is_alive())
        total_count = len(self.battle_system.players)
        if alive_count < total_count:
            parts.append(f"Party: {alive_count}/{total_count} standing")

        return " | ".join(parts) if parts else ""

    def _finalize_outcome(self, outcome: str) -> None:
        """Record outcome once and update flags/triggers."""
        if self._outcome_finalized:
            return
        self._outcome_finalized = True

        self._increment_flag("battles_total")

        if outcome == "victory":
            self._increment_flag("battles_won")
            self._victory_spared = all(enemy.spared for enemy in self.battle_system.enemies)
            self.world.set_flag("battle_won", True)
            self.world.set_flag("last_battle_spared", self._victory_spared)
            if self.source_trigger and getattr(self.source_trigger, "once", False):
                self.source_trigger.fired = True
            self._track_battle_achievements("victory")
            self._record_enemy_defeats()

        elif outcome == "defeat":
            self._track_battle_achievements("defeat")
            self._increment_flag("battles_lost")
            self.world.set_flag("battle_won", False)
            self.world.set_flag("last_battle_spared", False)
            if self.source_trigger and getattr(self.source_trigger, "once", False):
                self.source_trigger.fired = False

        elif outcome == "escaped":
            self._increment_flag("battles_escaped")
            self.world.set_flag("battle_won", False)
            self.world.set_flag("last_battle_spared", False)
            if self.source_trigger and getattr(self.source_trigger, "once", False):
                self.source_trigger.fired = False
            self._track_battle_achievements("escaped")

        enemies_spared = sum(1 for enemy in self.battle_system.enemies if getattr(enemy, "spared", False))
        enemies_defeated = sum(1 for enemy in self.battle_system.enemies if not getattr(enemy, "spared", False) and not enemy.is_alive())
        self._increment_flag("enemies_spared_total", enemies_spared)
        self._increment_flag("enemies_defeated_total", enemies_defeated)
        self.world.set_flag("last_battle_outcome", outcome)

    def _track_battle_achievements(self, outcome: str) -> None:
        """Track battle-related achievements via the event bus."""
        bus = getattr(self, "manager", None)
        bus = getattr(bus, "event_bus", None) if bus else None
        if not bus:
            return

        quest_manager = self.get_manager_attr(
            "quest_manager", "_track_battle_achievements"
        )

        if outcome == "victory":
            bus.publish("battle_won")
            for enemy in self.battle_system.enemies:
                if not enemy.is_alive() and not getattr(enemy, "spared", False):
                    enemy_type = getattr(enemy, "enemy_type", enemy.entity.entity_id)
                    bus.publish(
                        "enemy_killed",
                        enemy_type=enemy_type,
                        enemy_id=enemy.entity.entity_id,
                    )

                    if quest_manager:
                        progress_list = quest_manager.on_enemy_killed(
                            enemy_type, return_progress=True
                        )
                        for progress in progress_list:
                            if progress["completed"]:
                                self.battle_system.message_log.append(
                                    f"Quest objective complete: {progress['objective_desc']}"
                                )
                            else:
                                self.battle_system.message_log.append(
                                    f"Quest progress: {progress['objective_desc']} "
                                    f"({progress['current']}/{progress['required']})"
                                )

                    is_boss = getattr(enemy, "is_boss", False) or self.encounter_id in [
                        "final_boss",
                        "dragon_boss",
                        "demon_lord",
                    ]
                    if is_boss:
                        bus.publish("boss_killed", boss_id=enemy.entity.entity_id)

            for enemy in self.battle_system.enemies:
                if getattr(enemy, "spared", False):
                    enemy_type = getattr(enemy, "enemy_type", enemy.entity.entity_id)
                    bus.publish("battle_spared", enemy_type=enemy_type)

        elif outcome == "defeat":
            bus.publish("player_death")
        elif outcome == "escaped":
            bus.publish("battle_fled")

    def _record_enemy_encounters(self) -> None:
        """Record all enemies in this battle to the player's bestiary."""
        if not hasattr(self.player, 'bestiary') or not self.player.bestiary:
            return

        location = self.world.current_map_id if self.world else None

        for enemy_participant in self.battle_system.enemies:
            enemy = enemy_participant.entity
            enemy_type = getattr(enemy, "enemy_type", enemy.entity_id)

            base_stats = {}
            if enemy_participant.stats:
                base_stats = {
                    "max_hp": enemy_participant.stats.max_hp,
                    "max_sp": enemy_participant.stats.max_sp,
                    "attack": enemy_participant.stats.attack,
                    "defense": enemy_participant.stats.defense,
                    "magic": enemy_participant.stats.magic,
                    "speed": enemy_participant.stats.speed,
                }

            weaknesses = getattr(enemy_participant.stats, "weaknesses", []) if enemy_participant.stats else []
            resistances = getattr(enemy_participant.stats, "resistances", []) if enemy_participant.stats else []
            immunities = getattr(enemy_participant.stats, "immunities", []) if enemy_participant.stats else []
            absorbs = getattr(enemy_participant.stats, "absorbs", []) if enemy_participant.stats else []

            self.player.bestiary.record_encounter(
                enemy_type=enemy_type,
                name=enemy.name,
                sprite_id=getattr(enemy, "sprite_id", "enemy"),
                category=enemy_type,
                location=location,
                base_stats=base_stats,
                weaknesses=list(weaknesses),
                resistances=list(resistances),
                immunities=list(immunities),
                absorbs=list(absorbs),
            )

    def _record_enemy_defeats(self) -> None:
        """Record defeated enemies in the player's bestiary."""
        if not hasattr(self.player, 'bestiary') or not self.player.bestiary:
            return

        drops = list(self.rewards.get("items", {}).keys()) if self.rewards else []

        for enemy_participant in self.battle_system.enemies:
            if enemy_participant.is_alive() or getattr(enemy_participant, "spared", False):
                continue

            enemy = enemy_participant.entity
            enemy_type = getattr(enemy, "enemy_type", enemy.entity_id)

            base_stats = {}
            if enemy_participant.stats:
                base_stats = {
                    "max_hp": enemy_participant.stats.max_hp,
                    "max_sp": enemy_participant.stats.max_sp,
                    "attack": enemy_participant.stats.attack,
                    "defense": enemy_participant.stats.defense,
                    "magic": enemy_participant.stats.magic,
                    "speed": enemy_participant.stats.speed,
                }

            weaknesses = getattr(enemy_participant.stats, "weaknesses", []) if enemy_participant.stats else []
            resistances = getattr(enemy_participant.stats, "resistances", []) if enemy_participant.stats else []
            immunities = getattr(enemy_participant.stats, "immunities", []) if enemy_participant.stats else []
            absorbs = getattr(enemy_participant.stats, "absorbs", []) if enemy_participant.stats else []

            self.player.bestiary.record_defeat(
                enemy_type=enemy_type,
                name=enemy.name,
                sprite_id=getattr(enemy, "sprite_id", "enemy"),
                category=enemy_type,
                drops=drops,
                base_stats=base_stats,
                weaknesses=list(weaknesses),
                resistances=list(resistances),
                immunities=list(immunities),
                absorbs=list(absorbs),
            )

    def _determine_ending(self) -> str:
        """Determine which ending to show based on world flags."""
        from core.endings import determine_ending
        return determine_ending(self.world)

    def _transition_to_ending(self) -> None:
        """Transition to the ending scene after final boss victory."""
        ending_id = self._determine_ending()

        self.world.set_flag("ending_last_id", ending_id)
        self.world.set_flag("ending_good_unlocked", ending_id == "good")
        self.world.set_flag("ending_neutral_unlocked", ending_id == "neutral")
        self.world.set_flag("ending_bad_unlocked", ending_id == "bad")

        from ..ending_scene import EndingScene

        save_manager = self.get_manager_attr(
            "save_manager", "_transition_to_ending"
        )
        save_slot = self.manager.save_slot if self.manager else 1

        ending_scene = EndingScene(
            self.manager,
            self.world,
            self.player,
            ending_id,
            scale=self.scale,
            assets=self.assets,
            save_manager=save_manager,
            save_slot=save_slot
        )
        self.manager.replace(ending_scene)

    def _return_to_title_screen(self) -> None:
        """Return to the title screen after defeat."""
        from ..title_scene import TitleScene

        save_manager = self.get_manager_attr(
            "save_manager", "_return_to_title_screen"
        )

        for map_obj in self.world.maps.values():
            for trigger in map_obj.triggers:
                trigger.fired = False

        for map_id in self.world.map_overworld_enemies:
            for enemy in self.world.get_map_overworld_enemies(map_id):
                enemy.defeated = False

        title_scene = TitleScene(
            self.manager,
            save_manager=save_manager,
            scale=self.scale,
            assets=self.assets,
        )

        while len(self.manager.stack) > 1:
            self.manager.stack.pop()
        self.manager.replace(title_scene)

    def _apply_rewards(self) -> bool:
        """Grant encounter rewards (items, flags, EXP, gold)."""
        reward_items = self.rewards.get("items", {})
        reward_flags = self.rewards.get("flags", [])
        reward_exp = self.rewards.get("exp", 0)
        reward_gold = self.rewards.get("gold", 0)

        quest_manager = self.get_manager_attr("quest_manager", "_apply_rewards")
        bus = getattr(self, "manager", None)
        bus = getattr(bus, "event_bus", None) if bus else None
        if self.player.inventory:
            for item_id, qty in reward_items.items():
                self.player.inventory.add(item_id, qty)
                if quest_manager:
                    quest_manager.on_item_collected(item_id, qty)

        for flag in reward_flags:
            self.world.set_flag(flag, True)

        if reward_gold > 0:
            current_gold = self.world.get_flag("gold")
            if current_gold is False or current_gold is True:
                current_gold = 0
            new_gold = int(current_gold) + reward_gold
            self.world.set_flag("gold", new_gold)
            if bus:
                bus.publish("gold_changed", total_gold=new_gold)

        level_ups = []
        pending_move_learns = []
        if reward_exp > 0:
            if self.player.stats:
                player_level_ups = self.player.stats.add_exp(reward_exp)
                for new_level, gains, skill_points in player_level_ups:
                    level_ups.append((self.player.name, new_level))
                    if skill_points > 0 and hasattr(self.player, 'skill_tree_progress'):
                        self.player.skill_tree_progress.add_skill_points(skill_points)
                    if bus:
                        bus.publish("level_up", new_level=new_level)
                    new_move = self._check_new_move_for_level(self.player, new_level)
                    if new_move:
                        pending_move_learns.append((self.player, new_move))

            for member in getattr(self.player, "party", []):
                if member and member.stats:
                    member_level_ups = member.stats.add_exp(reward_exp)
                    for new_level, gains, skill_points in member_level_ups:
                        level_ups.append((member.name, new_level))
                        if skill_points > 0 and hasattr(member, 'skill_tree_progress'):
                            member.skill_tree_progress.add_skill_points(skill_points)
                        if bus:
                            bus.publish("level_up", new_level=new_level)
                        new_move = self._check_new_move_for_level(member, new_level)
                        if new_move:
                            pending_move_learns.append((member, new_move))

        self._pending_move_learns = pending_move_learns

        prefix = "Mercy win!" if self._victory_spared else "Victory!"
        reward_parts = []

        if reward_exp > 0:
            reward_parts.append(f"+{reward_exp} EXP")
        if reward_gold > 0:
            reward_parts.append(f"+{reward_gold} Gold")
        if reward_items:
            items_text = ", ".join(f"{item_id} x{qty}" for item_id, qty in reward_items.items())
            reward_parts.append(f"Loot: {items_text}")
        if level_ups:
            for name, new_level in level_ups:
                reward_parts.append(f"{name} LEVEL UP! Lv.{new_level}")

        if reward_parts:
            rewards_text = " | ".join(reward_parts)
            self.message_box.set_text(f"{prefix} {rewards_text}\nPress Enter to continue...")
            return True

        return False

    def _check_new_move_for_level(self, entity, level: int) -> Optional["Move"]:
        """Check if entity can learn a new move at this level."""
        player_class = getattr(entity, "player_class", None)
        if not player_class:
            role = getattr(entity, "role", None)
            if role:
                role_to_class = {
                    "fighter": "warrior",
                    "mage": "mage",
                    "healer": "cleric",
                    "support": "bard",
                }
                player_class = role_to_class.get(role, "warrior")
            else:
                player_class = "warrior"

        learned_moves = getattr(entity, "learned_moves", [])
        new_move = self.moves_db.get_new_move_for_level(player_class, level, learned_moves)
        return new_move

    def _trigger_next_move_learn(self) -> None:
        """Trigger the move learning scene for the next pending move."""
        if not self._pending_move_learns:
            self.manager.pop()
            return

        entity, move = self._pending_move_learns.pop(0)

        from ..move_learn_scene import MoveLearnScene

        def on_complete():
            if self._pending_move_learns:
                self._trigger_next_move_learn()
            else:
                self.manager.pop()

        learn_scene = MoveLearnScene(
            self.manager,
            entity,
            move,
            on_complete=on_complete,
            assets=self.assets,
            scale=self.scale,
        )
        self.manager.push(learn_scene)

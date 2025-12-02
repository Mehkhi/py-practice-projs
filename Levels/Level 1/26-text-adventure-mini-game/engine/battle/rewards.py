"""Battle reward and outcome handling helpers for `BattleScene`."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, TYPE_CHECKING

from core.combat import MemoryOperation
from core.moves import Move
from core.logging_utils import log_warning
from core.tutorial_system import TipTrigger

if TYPE_CHECKING:
    from core.world import World
    from core.entities import Player
    from core.combat import BattleSystem
    from engine.battle_scene import BattleScene


@dataclass
class BattleRewardsHandler:
    """Encapsulates reward application and outcome bookkeeping.

    This class mirrors the old `_apply_rewards`, `_finalize_outcome`,
    `_track_battle_achievements`, `_record_enemy_encounters`,
    `_record_enemy_defeats`, `_check_new_move_for_level`, and
    `_trigger_next_move_learn` methods on `BattleScene`, but keeps the
    heavy logic out of the scene class itself.
    """

    world: "World"
    player: "Player"
    battle_system: "BattleSystem"
    scene: "BattleScene"
    rewards: Dict[str, Any] = field(default_factory=dict)

    _pending_move_learns: List[Tuple[Any, Move]] = field(default_factory=list)
    _outcome_finalized: bool = False
    _victory_spared: bool = False

    def apply_rewards(self) -> bool:
        """Grant encounter rewards (items, flags, EXP, gold)."""
        reward_items = self.rewards.get("items", {})
        reward_flags = self.rewards.get("flags", [])
        reward_exp = self.rewards.get("exp", 0)
        reward_gold = self.rewards.get("gold", 0)
        quest_manager = self.scene.get_manager_attr("quest_manager", "_apply_rewards")
        bus = getattr(self.scene.manager, "event_bus", None) if self.scene.manager else None

        # Grant items
        if self.player.inventory:
            for item_id, qty in reward_items.items():
                self.player.inventory.add(item_id, qty)
                if quest_manager:
                    quest_manager.on_item_collected(item_id, qty)

        # Set flags
        for flag in reward_flags:
            self.world.set_flag(flag, True)

        # Grant gold
        if reward_gold > 0:
            current_gold = self.world.get_flag("gold")
            if current_gold is False or current_gold is True:
                current_gold = 0
            new_gold = int(current_gold) + reward_gold
            self.world.set_flag("gold", new_gold)
            if bus:
                bus.publish("gold_changed", total_gold=new_gold)

        # Grant EXP and handle level-ups
        level_ups: List[Tuple[str, int]] = []
        pending_move_learns: List[Tuple[Any, Move]] = []
        if reward_exp > 0:
            # Player
            if self.player.stats:
                player_level_ups = self.player.stats.add_exp(reward_exp)
                self._process_level_ups(
                    owner=self.player,
                    level_ups=player_level_ups,
                    bus=bus,
                    level_ups_out=level_ups,
                    pending_moves_out=pending_move_learns,
                )

            # Party members
            for member in getattr(self.player, "party", []):
                if member and member.stats:
                    member_level_ups = member.stats.add_exp(reward_exp)
                    self._process_level_ups(
                        owner=member,
                        level_ups=member_level_ups,
                        bus=bus,
                        level_ups_out=level_ups,
                        pending_moves_out=pending_move_learns,
                    )

        self._pending_move_learns = pending_move_learns

        # Build reward message
        prefix = "Mercy win!" if self._victory_spared else "Victory!"
        reward_parts: List[str] = []

        if reward_exp > 0:
            reward_parts.append(f"+{reward_exp} EXP")
        if reward_gold > 0:
            reward_parts.append(f"+{reward_gold} Gold")
        if reward_items:
            items_text = ", ".join(f"{item_id} x{qty}" for item_id, qty in reward_items.items())
            reward_parts.append(f"Loot: {items_text}")
        if level_ups:
            tutorial_manager = self.scene.get_manager_attr(
                "tutorial_manager", "_apply_rewards_level_ups"
            )
            if tutorial_manager:
                tutorial_manager.trigger_tip(TipTrigger.FIRST_LEVEL_UP)
            for name, new_level in level_ups:
                reward_parts.append(f"{name} LEVEL UP! Lv.{new_level}")

        if reward_parts:
            rewards_text = " | ".join(reward_parts)
            self.scene.message_box.set_text(
                f"{prefix} {rewards_text}\nPress Enter to continue..."
            )
            return True

        return False

    def finalize_outcome(self, outcome: str) -> None:
        """Record outcome once and update flags/triggers."""
        if self._outcome_finalized:
            return
        self._outcome_finalized = True

        self._increment_flag("battles_total")

        if outcome == "victory":
            self._increment_flag("battles_won")

            self._victory_spared = all(
                enemy.spared for enemy in self.battle_system.enemies
            )
            self.world.set_flag("battle_won", True)
            self.world.set_flag("last_battle_spared", self._victory_spared)
            if self.scene.source_trigger and getattr(self.scene.source_trigger, "once", False):
                self.scene.source_trigger.fired = True

            self._track_battle_achievements("victory")
            self._record_enemy_defeats()
        elif outcome == "defeat":
            self._track_battle_achievements("defeat")
            self._increment_flag("battles_lost")
            self.world.set_flag("battle_won", False)
            self.world.set_flag("last_battle_spared", False)
            if self.scene.source_trigger and getattr(self.scene.source_trigger, "once", False):
                self.scene.source_trigger.fired = False
        elif outcome == "escaped":
            self._increment_flag("battles_escaped")
            self.world.set_flag("battle_won", False)
            self.world.set_flag("last_battle_spared", False)
            if self.scene.source_trigger and getattr(self.scene.source_trigger, "once", False):
                self.scene.source_trigger.fired = False
            self._track_battle_achievements("escaped")

        enemies_spared = sum(
            1 for enemy in self.battle_system.enemies if getattr(enemy, "spared", False)
        )
        enemies_defeated = sum(
            1
            for enemy in self.battle_system.enemies
            if not getattr(enemy, "spared", False) and not enemy.is_alive()
        )

        self._increment_flag("enemies_spared_total", enemies_spared)
        self._increment_flag("enemies_defeated_total", enemies_defeated)

        self.world.set_flag("last_battle_outcome", outcome)

    # --- Helper methods originally on BattleScene ---

    def _get_flag_as_int(self, flag_name: str, default: int = 0) -> int:
        value = self.world.get_flag(flag_name)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return default
        return int(value)

    def _increment_flag(self, flag_name: str, amount: int = 1) -> None:
        current = self._get_flag_as_int(flag_name, 0)
        self.world.set_flag(flag_name, current + amount)

    def _track_battle_achievements(self, outcome: str) -> None:
        bus = getattr(self.scene.manager, "event_bus", None) if self.scene.manager else None
        if not bus:
            return

        quest_manager = self.scene.get_manager_attr(
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
                                    "Quest progress: "
                                    f"{progress['objective_desc']} "
                                    f"({progress['current']}/{progress['required']})"
                                )

                    is_boss = getattr(enemy, "is_boss", False) or self.scene.encounter_id in [
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

    def _record_enemy_defeats(self) -> None:
        player = self.player
        if not hasattr(player, "bestiary") or not player.bestiary:
            return

        drops = list(self.rewards.get("items", {}).keys()) if self.rewards else []

        for enemy_participant in self.battle_system.enemies:
            if enemy_participant.is_alive() or getattr(enemy_participant, "spared", False):
                continue

            enemy = enemy_participant.entity
            enemy_type = getattr(enemy, "enemy_type", enemy.entity_id)

            base_stats: Dict[str, Any] = {}
            if enemy_participant.stats:
                base_stats = {
                    "max_hp": enemy_participant.stats.max_hp,
                    "max_sp": enemy_participant.stats.max_sp,
                    "attack": enemy_participant.stats.attack,
                    "defense": enemy_participant.stats.defense,
                    "magic": enemy_participant.stats.magic,
                    "speed": enemy_participant.stats.speed,
                }

            weaknesses = (
                getattr(enemy_participant.stats, "weaknesses", [])
                if enemy_participant.stats
                else []
            )
            resistances = (
                getattr(enemy_participant.stats, "resistances", [])
                if enemy_participant.stats
                else []
            )
            immunities = (
                getattr(enemy_participant.stats, "immunities", [])
                if enemy_participant.stats
                else []
            )
            absorbs = (
                getattr(enemy_participant.stats, "absorbs", [])
                if enemy_participant.stats
                else []
            )

            player.bestiary.record_defeat(
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

    def _process_level_ups(
        self,
        owner: Any,
        level_ups: List[Tuple[int, Dict[str, Any], int]],
        bus: Any,
        level_ups_out: List[Tuple[str, int]],
        pending_moves_out: List[Tuple[Any, Move]],
    ) -> None:
        for new_level, _gains, skill_points in level_ups:
            level_ups_out.append((owner.name, new_level))
            if skill_points > 0 and hasattr(owner, "skill_tree_progress"):
                owner.skill_tree_progress.add_skill_points(skill_points)
            if bus:
                bus.publish("level_up", new_level=new_level)
            new_move = self._check_new_move_for_level(owner, new_level)
            if new_move:
                pending_moves_out.append((owner, new_move))

    def _check_new_move_for_level(self, entity: Any, level: int) -> Optional[Move]:
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
        new_move = self.scene.moves_db.get_new_move_for_level(
            player_class, level, learned_moves
        )
        return new_move

    def trigger_next_move_learn(self) -> None:
        """Trigger the move learning scene for the next pending move."""
        if not self._pending_move_learns:
            self.scene.manager.pop()
            return

        entity, move = self._pending_move_learns.pop(0)

        from engine.move_learn_scene import MoveLearnScene

        def on_complete() -> None:
            if self._pending_move_learns:
                self.trigger_next_move_learn()
            else:
                self.scene.manager.pop()

        learn_scene = MoveLearnScene(
            self.scene.manager,
            entity,
            move,
            on_complete=on_complete,
            assets=self.scene.assets,
            scale=self.scene.scale,
        )
        self.scene.manager.push(learn_scene)

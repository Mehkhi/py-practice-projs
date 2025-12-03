"""Battle target selection and turn-advancement mixin."""

from typing import Optional, List

import math
import pygame

from ..theme import Colors


class BattleTargetingMixin:
    """Mixin providing target selection and actor turn management."""

    def _reset_targeting_context(self, reset_menus: bool = False) -> None:
        """Return to main menu and clear pending targeting/action state."""
        self.waiting_for_target = False
        self.menu_mode = "main"
        self.pending_skill_id = None
        self.pending_item_id = None
        self.pending_move_id = None
        self.target_side = None
        self.target_type = None
        self._include_downed_allies = False
        if reset_menus:
            self.skill_menu = None
            self.item_menu = None
            self.move_menu = None
            self.memory_menu = None
            self.memory_stat_menu = None
            self.item_menu_mapping.clear()
            self.move_menu_mapping.clear()
            self._pending_memory_op = None

    def _handle_target_input(self, event: pygame.event.Event) -> None:
        """Handle input during target selection mode."""
        if event.key in (pygame.K_LEFT, pygame.K_UP):
            self._move_target_selection(-1)
        elif event.key in (pygame.K_RIGHT, pygame.K_DOWN):
            self._move_target_selection(1)
        elif event.key == pygame.K_RETURN:
            self._select_target()
        elif event.key == pygame.K_ESCAPE:
            self._cancel_target_selection()

    def _cancel_target_selection(self) -> None:
        """Cancel target selection and return to main menu."""
        self._reset_targeting_context()
        actor = self._current_actor()
        if actor:
            self.message_box.set_text(f"{actor.entity.name}'s turn. Choose an action.")
        else:
            self.message_box.set_text("No allies ready to act.")

    def _begin_target_selection(self, target_type: str, message: Optional[str] = None) -> None:
        """Enter target selection mode for the chosen action."""
        pool: List = []
        self.target_side = None
        include_downed_allies = target_type == "single_ally" and self._should_include_downed_allies()
        if target_type == "single_enemy":
            pool = self._alive_enemies()
            self.target_side = "enemy"
            if not pool:
                self.message_box.set_text("No valid targets.")
                return
        elif target_type == "single_ally":
            pool = self._alive_allies(include_downed_allies)
            self.target_side = "ally"
            if not pool:
                self.message_box.set_text("No valid allies.")
                return
        else:
            return

        self._include_downed_allies = include_downed_allies if self.target_side == "ally" else False
        self.menu_mode = "target"
        self.waiting_for_target = True
        self.target_type = target_type
        self.target_index = 0
        if message:
            self.message_box.set_text(message)

    def _move_target_selection(self, delta: int) -> None:
        """Move target cursor while skipping invalid targets."""
        if self.target_side == "enemy":
            pool = self._alive_enemies()
        elif self.target_side == "ally":
            pool = self._alive_allies(getattr(self, "_include_downed_allies", False))
        else:
            return
        if not pool:
            return
        self.target_index = (self.target_index + delta) % len(pool)

    def _select_target(self) -> None:
        """Confirm a target and queue the corresponding command."""
        from core.combat import BattleCommand, ActionType

        actor = self._current_actor()
        if not actor:
            self._reset_targeting_context()
            self.message_box.set_text("No active ally to act.")
            return

        if self.target_side == "enemy":
            pool = self._alive_enemies()
        elif self.target_side == "ally":
            pool = self._alive_allies(getattr(self, "_include_downed_allies", False))
        else:
            return

        if not pool:
            self._reset_targeting_context()
            self.message_box.set_text("No valid targets.")
            return

        target_participant = pool[self.target_index % len(pool)]
        target_id = target_participant.entity.entity_id

        if self.pending_skill_id:
            cmd = BattleCommand(
                actor_id=actor.entity.entity_id,
                action_type=ActionType.SKILL,
                skill_id=self.pending_skill_id,
                target_ids=[target_id],
            )
        elif self.pending_item_id:
            cmd = BattleCommand(
                actor_id=actor.entity.entity_id,
                action_type=ActionType.ITEM,
                item_id=self.pending_item_id,
                target_ids=[target_id],
            )
        elif self.pending_move_id:
            # Attack with a specific move
            cmd = BattleCommand(
                actor_id=actor.entity.entity_id,
                action_type=ActionType.ATTACK,
                skill_id=self.pending_move_id,  # Store move_id in skill_id field
                target_ids=[target_id],
            )
            # Start animation for the move
            move = self.moves_db.get_move(self.pending_move_id)
            if move:
                self._start_move_animation(move, target_participant)
        else:
            if self.target_side != "enemy":
                self.waiting_for_target = False
                self.menu_mode = "main"
                self.message_box.set_text("No action queued.")
                self.target_side = None
                self.target_type = None
                return
            cmd = BattleCommand(
                actor_id=actor.entity.entity_id,
                action_type=ActionType.ATTACK,
                target_ids=[target_id],
            )
        self.battle_system.queue_player_command(cmd)
        self._reset_targeting_context()
        self.message_box.set_text(f"{actor.entity.name}'s action queued!")
        self._advance_actor_after_command()

    def _alive_enemies(self):
        """Return a list of living enemy participants."""
        return [e for e in self.battle_system.enemies if e.is_alive()]

    def _alive_allies(self, include_downed: bool = False):
        """Return a list of ally participants, optionally including downed allies."""
        allies = []
        for participant in self.battle_system.players:
            if participant.is_alive():
                allies.append(participant)
            elif include_downed and getattr(participant, "stats", None) and getattr(participant.stats, "hp", 0) <= 0:
                allies.append(participant)
        return allies

    def _should_include_downed_allies(self) -> bool:
        """Determine if targeting should include downed allies (revive items/skills)."""
        if self.pending_item_id and getattr(self, "items_db", None):
            item = self.items_db.get(self.pending_item_id)
            effect_id = getattr(item, "effect_id", None)
            if effect_id and str(effect_id).startswith("revive"):
                return True
        return False

    def _find_next_alive_index(self, start_index: int = 0) -> Optional[int]:
        """Find the index of the next living ally from a starting point."""
        for idx in range(start_index, len(self.battle_system.players)):
            if self.battle_system.players[idx].is_alive():
                return idx
        return None

    def _current_actor(self):
        """Get the currently active battle participant for menu actions."""
        if self.active_player_index is None:
            return None
        if not (0 <= self.active_player_index < len(self.battle_system.players)):
            self.active_player_index = None
            return None
        actor = self.battle_system.players[self.active_player_index]
        if not actor.is_alive():
            next_index = self._find_next_alive_index(self.active_player_index + 1)
            if next_index is None:
                # No alive actors found - set index to None so safety check can trigger
                self.active_player_index = None
                return None
            self.active_player_index = next_index
            actor = self.battle_system.players[self.active_player_index]
        return actor

    def _reset_player_phase(self) -> None:
        """Reset UI state for the start of a player command phase."""
        self.active_player_index = self._find_next_alive_index(0)
        self._reset_targeting_context(reset_menus=True)
        self.main_menu.selected_index = 0
        self._player_phase_initialized = True
        actor = self._current_actor()
        if actor:
            self.message_box.set_text(f"{actor.entity.name}'s turn. Choose an action.")
        else:
            self.message_box.set_text("No allies ready to act.")

    def _advance_actor_after_command(self) -> None:
        """Move to the next living ally after issuing a command."""
        start_index = (
            (self.active_player_index + 1) if self.active_player_index is not None else 0
        )
        next_index = self._find_next_alive_index(start_index)
        self._reset_targeting_context(reset_menus=True)
        if next_index is None:
            self.active_player_index = None
            return
        self.active_player_index = next_index
        actor = self._current_actor()
        if actor:
            self.message_box.set_text(f"{actor.entity.name}'s turn. Choose an action.")

    def _draw_target_cursor(self, surface: pygame.Surface, x: int = 0, y: int = 0) -> None:
        """Draw a target cursor at the given position."""
        # Draw a downward pointing arrow
        color = Colors.ACCENT
        offset = int(math.sin(pygame.time.get_ticks() / 150) * 5)

        points = [
            (x, y - 20 + offset),
            (x - 10, y - 35 + offset),
            (x + 10, y - 35 + offset),
        ]
        pygame.draw.polygon(surface, color, points)
        pygame.draw.polygon(surface, Colors.BLACK, points, 2)

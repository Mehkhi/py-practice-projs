"""Coordinator for overworld triggers and interactions."""

from __future__ import annotations

from typing import Any, TYPE_CHECKING

from core.logging_utils import log_warning

from .triggers import (
    TriggerContext,
    get_handler_for_trigger_type,
    get_npc_handler,
    get_puzzle_handler,
    get_warp_handler,
)

if TYPE_CHECKING:
    from core.world import Trigger
    from engine.world_scene import WorldScene


class TriggerHandler:
    """Routes triggers to strategy handlers and delegates interactions."""

    def __init__(self, scene: "WorldScene"):
        self.scene = scene
        self.puzzle_manager = getattr(scene, "puzzle_manager", None)
        self._context = TriggerContext(scene=scene)
        self._warp_handler = get_warp_handler()
        self._puzzle_handler = get_puzzle_handler()
        self._npc_handler = get_npc_handler()

    def check_triggers(self) -> None:
        current_map = self.scene.world.get_current_map()
        trigger = current_map.get_trigger_at(self.scene.player.x, self.scene.player.y)
        if trigger:
            self.handle_trigger(trigger)
            return

        warp = current_map.get_warp_at(self.scene.player.x, self.scene.player.y)
        self._warp_handler.handle_map_warp(warp, self._context)

    def handle_trigger(self, trigger: "Trigger") -> None:
        if trigger.trigger_type != "battle":
            show_message = trigger.id != self.scene._last_blocked_trigger
            if not self.scene._requirements_met(trigger.data, show_message=show_message):
                self.scene._last_blocked_trigger = trigger.id
                return
            self.scene._last_blocked_trigger = None

        handler = get_handler_for_trigger_type(trigger.trigger_type)
        if not handler:
            log_warning(f"No handler registered for trigger type '{trigger.trigger_type}'")
            return

        handler.handle(trigger, self._context)

    def warp_with_transition(self, target_map_id: str, target_x: int, target_y: int) -> None:
        self._warp_handler.warp_with_transition(self._context, target_map_id, target_x, target_y)

    def interact(self) -> None:
        if self._interact_with_dialogue_trigger_if_present():
            return

        if self._puzzle_handler.interact_with_puzzle_if_present(self._context):
            return

        npc = self.scene._find_nearby_npc()
        if npc:
            self._npc_handler.interact_with_npc(npc, self._context)

    def _interact_with_dialogue_trigger_if_present(self) -> bool:
        current_map = self.scene.world.get_current_map()
        trigger = current_map.get_trigger_at(self.scene.player.x, self.scene.player.y)
        if trigger and trigger.trigger_type == "dialogue":
            self.handle_trigger(trigger)
            return True
        return False

    def _check_puzzle_interaction(self, direction: str) -> bool:
        return self._puzzle_handler.check_puzzle_push(direction, self._context)

    def _open_brain_teaser(self, teaser_id: str) -> None:
        self._puzzle_handler.open_brain_teaser(teaser_id, self._context)

    def _open_dialogue_then_puzzle(self, intro_dialogue_id: str, teaser_id: str) -> None:
        self._puzzle_handler.open_dialogue_then_puzzle(intro_dialogue_id, teaser_id, self._context)

    def _trigger_first_puzzle_tip(self) -> None:
        self._puzzle_handler.trigger_first_puzzle_tip(self._context)

    def _trigger_puzzle_solved_tip(self, puzzle: Any) -> None:
        self._puzzle_handler.trigger_puzzle_solved_tip(self._context, puzzle)

    def _handle_fishing_spot(self, spot_id: str) -> None:
        self._puzzle_handler.handle_fishing_spot(spot_id, self._context)

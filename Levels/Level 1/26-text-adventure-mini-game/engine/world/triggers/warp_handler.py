"""Warp trigger handling and map transition helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, TYPE_CHECKING

from core.logging_utils import log_warning

from .base import TriggerContext, TriggerHandlerStrategy
from .warp_effects import (
    AUTO_SAVE_MANAGER_ATTRS,
    handle_challenge_warp,
    track_exploration_achievement,
    trigger_area_tutorials,
    try_auto_save,
)

if TYPE_CHECKING:
    from core.world import Trigger
    from engine.world_scene import WorldScene


class WarpHandler:
    """Handles warp validation, transitions, and challenge dungeon warps."""

    def handle_map_warp(self, warp: Any, context: TriggerContext) -> None:
        if not warp:
            return

        if getattr(warp, "challenge_dungeon_id", None):
            handle_challenge_warp(warp, context, self.warp_with_transition)
            return

        scene = context.scene
        current_map = scene.world.get_current_map()
        current_pos = (current_map.map_id, scene.player.x, scene.player.y)
        if scene._warp_cooldown_pos == current_pos:
            return

        warp_key = f"warp_{warp.target_map_id}_{warp.x}_{warp.y}"
        if scene._can_use_warp(warp, show_message=scene._last_blocked_trigger != warp_key):
            scene._last_blocked_trigger = None
            self.warp_with_transition(context, warp.target_map_id, warp.target_x, warp.target_y)
        else:
            scene._last_blocked_trigger = warp_key

    def warp_with_transition(
        self, context: TriggerContext, target_map_id: str, target_x: int, target_y: int
    ) -> None:
        """Warp to a new map after validating target coordinates."""
        scene = context.scene
        if not self._validate_target(scene, target_map_id, target_x, target_y):
            return

        scene._pending_warp = (target_map_id, target_x, target_y)

        def do_warp() -> None:
            pending = scene._pending_warp
            if pending:
                self._perform_warp(context, *pending)

        scene.transition.fade_out_in(on_switch=do_warp, duration=0.5)

    def _validate_target(self, scene: "WorldScene", target_map_id: str, target_x: int, target_y: int) -> bool:
        if target_map_id not in scene.world.maps:
            log_warning(
                f"Attempted to warp to non-existent map '{target_map_id}' "
                f"from map '{scene.world.current_map_id}'"
            )
            return False

        target_map = scene.world.maps[target_map_id]
        if target_x < 0 or target_y < 0:
            log_warning(
                f"Attempted to warp to invalid coordinates ({target_x}, {target_y}) "
                f"in map '{target_map_id}' (negative coordinates)"
            )
            return False

        if target_x >= target_map.width or target_y >= target_map.height:
            log_warning(
                f"Attempted to warp to out-of-bounds coordinates ({target_x}, {target_y}) "
                f"in map '{target_map_id}' (map size: {target_map.width}x{target_map.height})"
            )
            return False

        if not target_map.is_walkable(target_x, target_y):
            log_warning(
                f"Attempted to warp to non-walkable tile ({target_x}, {target_y}) "
                f"in map '{target_map_id}'"
            )
            return False

        return True

    def _perform_warp(self, context: TriggerContext, map_id: str, x: int, y: int) -> None:
        scene = context.scene
        scene.world.set_current_map(map_id)
        scene.player.set_position(x, y)
        scene._pending_warp = None

        scene._warp_cooldown_pos = (map_id, x, y)
        scene._update_map_weather()
        scene._preload_map_sprites()

        trigger_area_tutorials(scene, map_id)
        track_exploration_achievement(scene, map_id)
        try_auto_save(scene, AUTO_SAVE_MANAGER_ATTRS)

        challenge_manager = scene.get_manager_attr(
            "challenge_dungeon_manager", "do_warp_challenge_floor_check"
        )
        if challenge_manager and challenge_manager.active_dungeon_id:
            dungeon = challenge_manager.dungeons.get(challenge_manager.active_dungeon_id)
            if dungeon and map_id in getattr(dungeon, "map_ids", []):
                challenge_manager.start_floor()


@dataclass
class WarpTriggerHandler(TriggerHandlerStrategy):
    """Handles `warp` triggers by delegating to WarpHandler."""

    warp_handler: WarpHandler
    trigger_type: str = "warp"

    def handle(self, trigger: "Trigger", context: TriggerContext) -> None:
        scene = context.scene
        current_map = scene.world.get_current_map()
        warp = current_map.get_warp_at(scene.player.x, scene.player.y)
        if warp and scene._can_use_warp(warp):
            self.warp_handler.warp_with_transition(context, warp.target_map_id, warp.target_x, warp.target_y)


@dataclass
class ChallengeSelectTriggerHandler(TriggerHandlerStrategy):
    """Opens the challenge dungeon selection scene."""

    trigger_type: str = "challenge_select"

    def handle(self, trigger: "Trigger", context: TriggerContext) -> None:
        scene = context.scene
        challenge_manager = scene.get_manager_attr(
            "challenge_dungeon_manager", "handle_trigger_challenge_select"
        )
        if not challenge_manager:
            log_warning("Challenge dungeon manager not available")
            return

        from engine.challenge_select_scene import ChallengeSelectScene

        select_scene = ChallengeSelectScene(
            manager=scene.manager,
            challenge_manager=challenge_manager,
            player=scene.player,
            world=scene.world,
            assets=scene.assets,
            scale=scene.scale,
        )
        scene.manager.push(select_scene)
        trigger.fired = trigger.once


__all__ = [
    "AUTO_SAVE_MANAGER_ATTRS",
    "WarpHandler",
    "WarpTriggerHandler",
    "ChallengeSelectTriggerHandler",
]

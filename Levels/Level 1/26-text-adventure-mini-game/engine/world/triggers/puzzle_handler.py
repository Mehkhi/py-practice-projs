"""Puzzle interactions, fishing triggers, and brain teaser handling."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, TYPE_CHECKING

from .base import TriggerContext, TriggerHandlerStrategy
from .puzzle_actions import (
    get_element_in_facing_direction,
    interact_with_element,
    trigger_first_puzzle_tip,
    trigger_puzzle_solved_tip,
)

if TYPE_CHECKING:
    from core.world import Trigger


@dataclass
class PuzzleInteractionHandler:
    """Handles interactions with puzzle elements and mini-games."""

    def interact_with_puzzle_if_present(self, context: TriggerContext) -> bool:
        puzzle_manager = getattr(context.scene, "puzzle_manager", None)
        if not puzzle_manager:
            return False
        puzzle_element = get_element_in_facing_direction(context)
        if puzzle_element:
            interact_with_element(puzzle_element, context)
            return True
        return False

    def trigger_first_puzzle_tip(self, context: TriggerContext) -> None:
        trigger_first_puzzle_tip(context)

    def trigger_puzzle_solved_tip(self, context: TriggerContext, puzzle: Any) -> None:
        trigger_puzzle_solved_tip(context, puzzle)

    def check_puzzle_push(self, direction: str, context: TriggerContext) -> bool:
        puzzle_manager = getattr(context.scene, "puzzle_manager", None)
        if not puzzle_manager:
            return False

        dx_map = {"left": -1, "right": 1, "up": 0, "down": 0}
        dy_map = {"left": 0, "right": 0, "up": -1, "down": 1}
        dx = dx_map.get(direction, 0)
        dy = dy_map.get(direction, 0)

        target_x = context.scene.player.x + dx
        target_y = context.scene.player.y + dy

        puzzle = puzzle_manager.get_puzzle_for_map(context.scene.world.current_map_id)
        if not puzzle:
            return False

        trigger_first_puzzle_tip(context)
        element = puzzle_manager.get_element_at(context.scene.world.current_map_id, target_x, target_y)

        from core.puzzles import PuzzleElementType

        if element and element.element_type == PuzzleElementType.PUSHABLE_BLOCK:
            moved = puzzle_manager.push_block(element, direction, context.scene.world)
            if moved:
                trigger_puzzle_solved_tip(context, puzzle)
            return moved

        return False

    def open_brain_teaser(self, teaser_id: str, context: TriggerContext) -> None:
        brain_teaser_manager = context.scene.get_manager_attr("brain_teaser_manager", "_open_brain_teaser")
        if not brain_teaser_manager:
            from core.logging_utils import log_warning

            log_warning("Brain teaser trigger activated but no brain_teaser_manager available")
            return

        teaser = brain_teaser_manager.get_teaser(teaser_id)
        if not teaser:
            from core.logging_utils import log_warning

            log_warning(f"Brain teaser '{teaser_id}' not found")
            return

        from engine.brain_teaser_scene import BrainTeaserScene

        puzzle_scene = BrainTeaserScene(
            context.scene.manager,
            teaser,
            brain_teaser_manager,
            player=context.scene.player,
            world=context.scene.world,
            assets=context.scene.assets,
            scale=context.scene.scale,
        )
        context.scene.manager.push(puzzle_scene)

    def open_dialogue_then_puzzle(self, intro_dialogue_id: str, teaser_id: str, context: TriggerContext) -> None:
        context.scene._pending_brain_teaser = teaser_id
        context.scene._start_dialogue(intro_dialogue_id)

    def handle_fishing_spot(self, spot_id: str, context: TriggerContext) -> None:
        tutorial_manager = context.scene.get_manager_attr("tutorial_manager", "_handle_fishing_spot")
        if tutorial_manager:
            from core.tutorial_system import TipTrigger

            tutorial_manager.trigger_tip(TipTrigger.FIRST_FISHING_SPOT)

        fishing_system = context.scene.get_manager_attr("fishing_system", "_handle_fishing_spot")
        if not fishing_system:
            from core.logging_utils import log_warning

            log_warning("Fishing trigger activated but no fishing_system available")
            return

        spot = fishing_system.spots.get(spot_id)
        if not spot:
            from core.logging_utils import log_warning

            log_warning(f"Fishing spot '{spot_id}' not found")
            return

        from engine.fishing_scene import FishingScene

        fishing_scene = FishingScene(
            context.scene.manager,
            fishing_system,
            spot,
            context.scene.player,
            context.scene.world,
            assets=context.scene.assets,
            scale=context.scene.scale,
        )
        context.scene.manager.push(fishing_scene)



@dataclass
class FishingTriggerHandler(TriggerHandlerStrategy):
    """Handles `fishing` triggers.

    Fishing itself is now started manually via the inventory (using a fishing rod),
    so this handler no longer opens the fishing mini-game directly.

    However, we still need to respect the trigger's `once` flag so that
    one-time fishing triggers don't keep firing forever.
    """

    puzzle_handler: PuzzleInteractionHandler
    trigger_type: str = "fishing"

    def handle(self, trigger: "Trigger", context: TriggerContext) -> None:
        # Fishing is now manual - player must use a fishing rod from inventory.
        # We intentionally do NOT start the fishing scene here anymore.
        #
        # Still mark the trigger as fired if it's a one-time trigger so that the
        # trigger system's `once` logic continues to work as expected.
        trigger.fired = trigger.once


@dataclass
class BrainTeaserTriggerHandler(TriggerHandlerStrategy):
    """Handles `brain_teaser` triggers."""

    puzzle_handler: PuzzleInteractionHandler
    trigger_type: str = "brain_teaser"

    def handle(self, trigger: "Trigger", context: TriggerContext) -> None:
        teaser_id = trigger.data.get("teaser_id")
        intro = trigger.data.get("intro_dialogue")
        if not teaser_id:
            return

        if intro:
            self.puzzle_handler.open_dialogue_then_puzzle(intro, teaser_id, context)
        else:
            self.puzzle_handler.open_brain_teaser(teaser_id, context)
        trigger.fired = trigger.once


__all__ = [
    "PuzzleInteractionHandler",
    "FishingTriggerHandler",
    "BrainTeaserTriggerHandler",
]

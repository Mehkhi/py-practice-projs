"""Helper functions for puzzle interactions and tutorial tips."""

from __future__ import annotations

from typing import Any, Optional, TYPE_CHECKING

from .base import TriggerContext

if TYPE_CHECKING:
    from engine.world_scene import WorldScene


def get_element_in_facing_direction(context: TriggerContext) -> Optional[Any]:
    puzzle_manager = getattr(context.scene, "puzzle_manager", None)
    if not puzzle_manager:
        return None

    facing = getattr(context.scene, "player_facing", "down")
    dx_map = {"left": -1, "right": 1, "up": 0, "down": 0}
    dy_map = {"left": 0, "right": 0, "up": -1, "down": 1}

    dx = dx_map.get(facing, 0)
    dy = dy_map.get(facing, 0)

    target_x = context.scene.player.x + dx
    target_y = context.scene.player.y + dy

    return puzzle_manager.get_element_at(context.scene.world.current_map_id, target_x, target_y)


def trigger_first_puzzle_tip(context: TriggerContext) -> None:
    if not context.scene.world.get_flag("_tutorial_first_dungeon_puzzle", False):
        tutorial_manager = context.scene.get_manager_attr("tutorial_manager", "_trigger_first_puzzle_tip")
        if not tutorial_manager:
            return
        from core.tutorial_system import TipTrigger

        context.scene.world.set_flag("_tutorial_first_dungeon_puzzle", True)
        tutorial_manager.trigger_tip(TipTrigger.FIRST_DUNGEON_PUZZLE)


def trigger_puzzle_solved_tip(context: TriggerContext, puzzle: Any) -> None:
    if not puzzle or not getattr(puzzle, "solved", False):
        return

    if not context.scene.world.get_flag("_tutorial_first_puzzle_solved", False):
        tutorial_manager = context.scene.get_manager_attr("tutorial_manager", "_trigger_puzzle_solved_tip")
        if not tutorial_manager:
            return
        from core.tutorial_system import TipTrigger

        context.scene.world.set_flag("_tutorial_first_puzzle_solved", True)
        tutorial_manager.trigger_tip(TipTrigger.FIRST_PUZZLE_SOLVED)


def interact_with_element(element: Any, context: TriggerContext) -> None:
    from core.puzzles import PuzzleElementType, SequencePuzzle

    puzzle_manager = getattr(context.scene, "puzzle_manager", None)
    if not element or not puzzle_manager:
        return

    puzzle = puzzle_manager.get_puzzle_for_map(context.scene.world.current_map_id)
    if not puzzle:
        return

    trigger_first_puzzle_tip(context)

    if element.element_type in (PuzzleElementType.SWITCH, PuzzleElementType.LEVER):
        if element.data.get("action") == "reset_puzzle":
            dialogue_id = element.data.get("confirmation_dialogue")
            if dialogue_id:
                if context.scene.world.get_flag("_temp_reset_confirmed"):
                    context.scene.world.set_flag("_temp_reset_confirmed", False)
                    puzzle_manager.reset_puzzle(puzzle.puzzle_id)
                    context.scene._show_inline_message("Puzzle reset!")
                else:
                    context.scene._start_dialogue(dialogue_id)
                return
            puzzle_manager.reset_puzzle(puzzle.puzzle_id)
            context.scene._show_inline_message("Puzzle reset!")
            return

    if element.element_type in (PuzzleElementType.SWITCH, PuzzleElementType.LEVER):
        puzzle_manager.toggle_switch(element)
        if isinstance(puzzle, SequencePuzzle):
            correct, complete = puzzle.record_activation(element.element_id)
            if not correct:
                element.visual_state = "error"
                context.scene._show_inline_message("Wrong sequence! Try again.")
            elif complete and puzzle_manager.check_puzzle_solved(puzzle):
                puzzle.solved = True
                if puzzle.reward_trigger_id:
                    current_map = context.scene.world.get_current_map()
                    current_map.fire_trigger(puzzle.reward_trigger_id)
        else:
            if not puzzle.solved and puzzle_manager.check_puzzle_solved(puzzle):
                puzzle.solved = True
                if puzzle.reward_trigger_id:
                    current_map = context.scene.world.get_current_map()
                    current_map.fire_trigger(puzzle.reward_trigger_id)

    elif element.element_type == PuzzleElementType.TORCH_HOLDER:
        if puzzle_manager.light_torch(element, context.scene.player):
            context.scene._show_inline_message("You lit the torch!")
            if not puzzle.solved and puzzle_manager.check_puzzle_solved(puzzle):
                puzzle.solved = True
                if puzzle.reward_trigger_id:
                    current_map = context.scene.world.get_current_map()
                    current_map.fire_trigger(puzzle.reward_trigger_id)
        else:
            context.scene._show_inline_message("You need something to light this with...")

    elif element.element_type == PuzzleElementType.TELEPORTER:
        dest_x, dest_y = puzzle_manager.use_teleporter(element, context.scene.player.x, context.scene.player.y)
        if dest_x != context.scene.player.x or dest_y != context.scene.player.y:
            context.scene.player.set_position(dest_x, dest_y)
            context.scene._show_inline_message("Teleported!")

    elif element.element_type == PuzzleElementType.GATE:
        if puzzle_manager._check_gate_conditions(element, puzzle):
            if element.state == "closed":
                element.state = "open"
                element.solid = False
                element.visual_state = "animating"
                context.scene._show_inline_message("Gate opened!")
        else:
            context.scene._show_inline_message("The gate is locked. Find a way to open it.")

    trigger_puzzle_solved_tip(context, puzzle)


__all__ = [
    "get_element_in_facing_direction",
    "interact_with_element",
    "trigger_first_puzzle_tip",
    "trigger_puzzle_solved_tip",
]

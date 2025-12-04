"""Puzzle solve condition checking logic."""

from typing import Dict, List

from .models import DungeonPuzzle, PuzzleElementType, SequencePuzzle


def check_puzzle_solved(puzzle: DungeonPuzzle) -> bool:
    """
    Check if all solution conditions are met.

    Conditions can be:
    - {"type": "all_plates_pressed"}
    - {"type": "all_switches_on"}
    - {"type": "blocks_on_targets", "targets": [[x,y], [x,y]]}
    - {"type": "element_state", "element_id": "...", "state": "..."}
    - {"type": "sequence_complete"} (for SequencePuzzle)
    """
    # Check if this is a sequence puzzle
    if isinstance(puzzle, SequencePuzzle):
        if puzzle.required_sequence:
            if len(puzzle.current_sequence) == len(puzzle.required_sequence):
                # Check if sequence matches
                if puzzle.current_sequence == puzzle.required_sequence:
                    return True
            return False

    for condition in puzzle.solution_conditions:
        condition_type = condition.get("type")

        if condition_type == "all_plates_pressed":
            plates = [
                elem
                for elem in puzzle.elements.values()
                if elem.element_type == PuzzleElementType.PRESSURE_PLATE
            ]
            if not all(plate.state == "activated" for plate in plates):
                return False

        elif condition_type == "all_switches_on":
            switches = [
                elem
                for elem in puzzle.elements.values()
                if elem.element_type == PuzzleElementType.SWITCH
            ]
            if not all(switch.state == "on" or switch.state == "activated" for switch in switches):
                return False

        elif condition_type == "blocks_on_targets":
            targets = condition.get("targets", [])
            blocks = [
                elem
                for elem in puzzle.elements.values()
                if elem.element_type == PuzzleElementType.PUSHABLE_BLOCK
            ]
            block_positions = {(block.x, block.y) for block in blocks}
            target_set = {tuple(t) for t in targets}
            if block_positions != target_set:
                return False

        elif condition_type == "element_state":
            element_id = condition.get("element_id")
            required_state = condition.get("state")
            if element_id in puzzle.elements:
                if puzzle.elements[element_id].state != required_state:
                    return False
            else:
                return False

        elif condition_type == "sequence_complete":
            if isinstance(puzzle, SequencePuzzle):
                if len(puzzle.current_sequence) == len(puzzle.required_sequence):
                    if puzzle.current_sequence == puzzle.required_sequence:
                        continue  # This condition is met
            return False

    return True

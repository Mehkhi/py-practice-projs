"""Puzzle data loader."""

from typing import Dict

from core.constants import PUZZLES_JSON
from core.loaders.base import (
    ensure_dict,
    ensure_list,
    load_json_file,
    validate_required_keys,
)
from core.logging_utils import log_schema_warning


def load_puzzles_from_json(
    filepath: str = PUZZLES_JSON,
) -> Dict[str, "DungeonPuzzle"]:
    """Load puzzles from JSON file.

    Args:
        filepath: Path to the puzzles JSON file

    Returns:
        Dictionary mapping puzzle_id to DungeonPuzzle, or empty dict if file missing
    """
    from core.puzzles import DungeonPuzzle, SequencePuzzle, PuzzleElement, PuzzleElementType

    data = load_json_file(
        filepath,
        default={"puzzles": {}},
        context="Loading puzzles",
        warn_on_missing=True,
    )

    context = "puzzle loader"
    data = ensure_dict(data, context=context, section="root")

    puzzles: Dict[str, DungeonPuzzle] = {}
    puzzles_data = ensure_dict(
        data.get("puzzles", {}),
        context=context,
        section="puzzles",
    )

    for puzzle_id, puzzle_data in puzzles_data.items():
        puzzle_entry = ensure_dict(
            puzzle_data,
            context=context,
            section="puzzle",
            identifier=puzzle_id,
        )
        if not validate_required_keys(
            puzzle_entry,
            ("puzzle_id", "map_id", "name", "elements"),
            context=context,
            section="puzzle",
            identifier=puzzle_id,
        ):
            continue

        # Load elements
        elements: Dict[str, PuzzleElement] = {}
        elements_data = ensure_dict(
            puzzle_entry.get("elements", {}),
            context=context,
            section="elements",
            identifier=puzzle_id,
        )

        for element_id, element_data in elements_data.items():
            element_entry = ensure_dict(
                element_data,
                context=context,
                section="element",
                identifier=element_id,
            )
            if not validate_required_keys(
                element_entry,
                ("element_id", "element_type", "x", "y"),
                context=context,
                section="element",
                identifier=element_id,
            ):
                continue

            # Convert element_type string to enum
            try:
                element_type = PuzzleElementType(element_entry["element_type"])
            except ValueError:
                log_schema_warning(
                    context,
                    f"invalid element_type '{element_entry['element_type']}', skipping element",
                    section="element",
                    identifier=element_id,
                )
                continue

            element = PuzzleElement(
                element_id=element_entry["element_id"],
                element_type=element_type,
                x=element_entry["x"],
                y=element_entry["y"],
                state=element_entry.get("state", "default"),
                linked_elements=ensure_list(
                    element_entry.get("linked_elements", []),
                    context=context,
                    section="element.linked_elements",
                    identifier=element_id,
                ),
                sprite_id=element_entry.get("sprite_id", ""),
                solid=element_entry.get("solid", True),
                data=ensure_dict(
                    element_entry.get("data", {}),
                    context=context,
                    section="element.data",
                    identifier=element_id,
                ),
            )
            elements[element_id] = element

        # Create puzzle - check if it's a sequence puzzle
        solution_conditions = ensure_list(
            puzzle_entry.get("solution_conditions", []),
            context=context,
            section="puzzle.solution_conditions",
            identifier=puzzle_id,
        )
        if puzzle_entry.get("puzzle_type") == "sequence" or "required_sequence" in puzzle_entry:
            puzzle = SequencePuzzle(
                puzzle_id=puzzle_entry["puzzle_id"],
                map_id=puzzle_entry["map_id"],
                name=puzzle_entry["name"],
                elements=elements,
                solution_conditions=solution_conditions,
                reward_trigger_id=puzzle_entry.get("reward_trigger_id"),
                solved=False,
                hint=puzzle_entry.get("hint", ""),
                required_sequence=ensure_list(
                    puzzle_entry.get("required_sequence", []),
                    context=context,
                    section="puzzle.required_sequence",
                    identifier=puzzle_id,
                ),
                current_sequence=[],
            )
        else:
            puzzle = DungeonPuzzle(
                puzzle_id=puzzle_entry["puzzle_id"],
                map_id=puzzle_entry["map_id"],
                name=puzzle_entry["name"],
                elements=elements,
                solution_conditions=solution_conditions,
                reward_trigger_id=puzzle_entry.get("reward_trigger_id"),
                solved=False,
                hint=puzzle_entry.get("hint", ""),
            )
        puzzles[puzzle.puzzle_id] = puzzle

    return puzzles

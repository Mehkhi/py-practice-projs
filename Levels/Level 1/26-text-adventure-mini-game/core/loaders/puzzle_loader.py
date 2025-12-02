"""Puzzle data loader."""

from typing import Dict

from core.loaders.base import load_json_file
from core.logging_utils import log_warning


def load_puzzles_from_json(
    filepath: str = "data/puzzles.json",
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

    if not isinstance(data, dict):
        raise ValueError("Puzzle data must be a dictionary at the top level")

    puzzles: Dict[str, DungeonPuzzle] = {}
    puzzles_data = data.get("puzzles", {})
    if not isinstance(puzzles_data, dict):
        raise ValueError("Puzzle data 'puzzles' section must be a dictionary")

    for puzzle_id, puzzle_data in puzzles_data.items():
        if not isinstance(puzzle_data, dict):
            raise ValueError(f"Puzzle '{puzzle_id}' entry must be a dictionary")
        # Validate required fields
        if "puzzle_id" not in puzzle_data:
            log_warning("Puzzle missing 'puzzle_id', skipping")
            continue
        if "map_id" not in puzzle_data:
            log_warning(f"Puzzle '{puzzle_id}' missing 'map_id', skipping")
            continue
        if "name" not in puzzle_data:
            log_warning(f"Puzzle '{puzzle_id}' missing 'name', skipping")
            continue
        if "elements" not in puzzle_data:
            log_warning(f"Puzzle '{puzzle_id}' missing 'elements', skipping")
            continue

        # Load elements
        elements: Dict[str, PuzzleElement] = {}
        elements_data = puzzle_data.get("elements", {})
        if not isinstance(elements_data, dict):
            raise ValueError(f"Puzzle '{puzzle_id}' elements must be a dictionary")

        for element_id, element_data in elements_data.items():
            if not isinstance(element_data, dict):
                raise ValueError(f"Puzzle '{puzzle_id}' element '{element_id}' must be a dictionary")
            # Validate required element fields
            if "element_id" not in element_data:
                log_warning(
                    f"Element in puzzle '{puzzle_id}' missing 'element_id', skipping"
                )
                continue
            if "element_type" not in element_data:
                log_warning(
                    f"Element '{element_id}' in puzzle '{puzzle_id}' missing 'element_type', skipping"
                )
                continue
            if "x" not in element_data:
                log_warning(
                    f"Element '{element_id}' in puzzle '{puzzle_id}' missing 'x', skipping"
                )
                continue
            if "y" not in element_data:
                log_warning(
                    f"Element '{element_id}' in puzzle '{puzzle_id}' missing 'y', skipping"
                )
                continue

            # Convert element_type string to enum
            try:
                element_type = PuzzleElementType(element_data["element_type"])
            except ValueError:
                log_warning(
                    f"Element '{element_id}' in puzzle '{puzzle_id}': "
                    f"invalid element_type '{element_data['element_type']}', skipping"
                )
                continue

            element = PuzzleElement(
                element_id=element_data["element_id"],
                element_type=element_type,
                x=element_data["x"],
                y=element_data["y"],
                state=element_data.get("state", "default"),
                linked_elements=element_data.get("linked_elements", []),
                sprite_id=element_data.get("sprite_id", ""),
                solid=element_data.get("solid", True),
                data=element_data.get("data", {}),
            )
            elements[element_id] = element

        # Create puzzle - check if it's a sequence puzzle
        if puzzle_data.get("puzzle_type") == "sequence" or "required_sequence" in puzzle_data:
            puzzle = SequencePuzzle(
                puzzle_id=puzzle_data["puzzle_id"],
                map_id=puzzle_data["map_id"],
                name=puzzle_data["name"],
                elements=elements,
                solution_conditions=puzzle_data.get("solution_conditions", []),
                reward_trigger_id=puzzle_data.get("reward_trigger_id"),
                solved=False,
                hint=puzzle_data.get("hint", ""),
                required_sequence=puzzle_data.get("required_sequence", []),
                current_sequence=[],
            )
        else:
            puzzle = DungeonPuzzle(
                puzzle_id=puzzle_data["puzzle_id"],
                map_id=puzzle_data["map_id"],
                name=puzzle_data["name"],
                elements=elements,
                solution_conditions=puzzle_data.get("solution_conditions", []),
                reward_trigger_id=puzzle_data.get("reward_trigger_id"),
                solved=False,
                hint=puzzle_data.get("hint", ""),
            )
        puzzles[puzzle_id] = puzzle

    return puzzles

"""Teleporter mechanics."""

from typing import Tuple

from ..models import PuzzleElement, PuzzleElementType, DungeonPuzzle


def use_teleporter(
    element: PuzzleElement, entity_x: int, entity_y: int, puzzle: DungeonPuzzle
) -> Tuple[int, int]:
    """Get destination coordinates for teleporter."""
    if element.element_type != PuzzleElementType.TELEPORTER:
        return (entity_x, entity_y)

    if not element.linked_elements:
        return (entity_x, entity_y)

    # Find the linked teleporter
    linked_id = element.linked_elements[0]
    if linked_id in puzzle.elements:
        linked = puzzle.elements[linked_id]
        return (linked.x, linked.y)

    return (entity_x, entity_y)

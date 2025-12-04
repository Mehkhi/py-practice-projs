"""Block pushing and ice sliding mechanics."""

from typing import Tuple, TYPE_CHECKING

from ..models import PuzzleElement, PuzzleElementType, DungeonPuzzle

if TYPE_CHECKING:
    from ...world import World


def calculate_push_destination(
    x: int, y: int, direction: str, world: "World", puzzle: DungeonPuzzle
) -> Tuple[int, int, str]:
    """
    Calculate where a block ends up when pushed.

    Returns (final_x, final_y, result) where result is:
    - "moved": Block moved to new position
    - "blocked": Block couldn't move
    - "fell": Block fell into pit
    - "slid": Block slid on ice
    """
    # Direction offsets
    dx_map = {"left": -1, "right": 1, "up": 0, "down": 0}
    dy_map = {"left": 0, "right": 0, "up": -1, "down": 1}

    dx = dx_map.get(direction, 0)
    dy = dy_map.get(direction, 0)

    if dx == 0 and dy == 0:
        return (x, y, "blocked")

    current_x, current_y = x, y
    current_map = world.get_current_map()

    # Check for ice sliding
    next_x = current_x + dx
    next_y = current_y + dy

    # Check if there's an ice tile element at this position
    for element in puzzle.elements.values():
        if element.element_type == PuzzleElementType.ICE_TILE and element.x == next_x and element.y == next_y:
            # Block will slide on ice
            return _slide_on_ice(current_x, current_y, dx, dy, world, puzzle)

    # Check for teleporter
    teleporter = None
    for element in puzzle.elements.values():
        if element.element_type == PuzzleElementType.TELEPORTER and element.x == next_x and element.y == next_y:
            teleporter = element
            break

    if teleporter:
        linked_id = teleporter.linked_elements[0] if teleporter.linked_elements else None
        linked = puzzle.elements.get(linked_id) if linked_id else None
        if linked:
            dest_x, dest_y = linked.x, linked.y
            # Validate destination is walkable and unblocked
            if not current_map.is_walkable(dest_x, dest_y):
                return (current_x, current_y, "blocked")
            for other in puzzle.elements.values():
                if other.solid and other.x == dest_x and other.y == dest_y:
                    return (current_x, current_y, "blocked")
            entities = world.get_map_entities(current_map.map_id)
            for entity in entities:
                if getattr(entity, "solid", True) and getattr(entity, "x", None) == dest_x and getattr(entity, "y", None) == dest_y:
                    return (current_x, current_y, "blocked")
            return (dest_x, dest_y, "moved")

    # Check for pit
    pit_element = None
    for element in puzzle.elements.values():
        if element.element_type == PuzzleElementType.PIT and element.x == next_x and element.y == next_y:
            pit_element = element
            break

    if pit_element:
        return (next_x, next_y, "fell")

    # Check collision
    if not current_map.is_walkable(next_x, next_y):
        return (current_x, current_y, "blocked")

    # Check for other puzzle elements blocking
    for element in puzzle.elements.values():
        if element.solid and element.x == next_x and element.y == next_y:
            # Can't push into another solid element
            return (current_x, current_y, "blocked")

    # Check for entities blocking
    entities = world.get_map_entities(current_map.map_id)
    for entity in entities:
        if hasattr(entity, 'x') and hasattr(entity, 'y'):
            if entity.x == next_x and entity.y == next_y:
                if getattr(entity, 'solid', True):
                    return (current_x, current_y, "blocked")

    return (next_x, next_y, "moved")


def _slide_on_ice(
    start_x: int, start_y: int, dx: int, dy: int, world: "World", puzzle: DungeonPuzzle
) -> Tuple[int, int, str]:
    """Calculate final position when sliding on ice."""
    current_x, current_y = start_x, start_y
    current_map = world.get_current_map()

    # Slide until hitting an obstacle
    while True:
        next_x = current_x + dx
        next_y = current_y + dy

        # Check if still on ice
        on_ice = False
        for element in puzzle.elements.values():
            if element.element_type == PuzzleElementType.ICE_TILE and element.x == next_x and element.y == next_y:
                on_ice = True
                break

        if not on_ice:
            # No more ice, stop here
            break

        # Check collision
        if not current_map.is_walkable(next_x, next_y):
            return (current_x, current_y, "slid")

        # Check for other puzzle elements
        blocked = False
        for element in puzzle.elements.values():
            if element.solid and element.x == next_x and element.y == next_y:
                blocked = True
                break

        if blocked:
            return (current_x, current_y, "slid")

        # Check for entities
        entities = world.get_map_entities(current_map.map_id)
        for entity in entities:
            if hasattr(entity, 'x') and hasattr(entity, 'y'):
                if entity.x == next_x and entity.y == next_y:
                    if getattr(entity, 'solid', True):
                        return (current_x, current_y, "slid")

        # Can slide further
        current_x, current_y = next_x, next_y

    return (current_x, current_y, "slid")


def push_block(
    element: PuzzleElement, direction: str, world: "World", puzzle: DungeonPuzzle
) -> bool:
    """
    Attempt to push a block in a direction.

    Returns True if block moved.

    Handles: collision, pits, ice sliding, chain reactions.
    """
    if element.element_type != PuzzleElementType.PUSHABLE_BLOCK:
        return False

    # Calculate destination
    final_x, final_y, result = calculate_push_destination(
        element.x, element.y, direction, world, puzzle
    )

    if result == "blocked":
        # Set visual feedback for blocked block
        element.visual_state = "flashing"
        return False

    # Handle pit - block disappears
    if result == "fell":
        # Remove block from puzzle
        del puzzle.elements[element.element_id]
        return True

    # Move block to new position
    element.x = final_x
    element.y = final_y
    element.visual_state = "normal"  # Reset visual state after successful move

    return True


def is_on_ice(puzzle: DungeonPuzzle, x: int, y: int) -> bool:
    """Check if a position is on an ice tile."""
    for element in puzzle.elements.values():
        if element.element_type == PuzzleElementType.ICE_TILE and element.x == x and element.y == y:
            return True
    return False


def calculate_player_slide_destination(
    puzzle: DungeonPuzzle, start_x: int, start_y: int, dx: int, dy: int, world: "World"
) -> Tuple[int, int]:
    """
    Calculate where a player ends up when sliding on ice.

    Returns (final_x, final_y).
    """
    # Check if starting position is on ice
    if not is_on_ice(puzzle, start_x, start_y):
        return (start_x, start_y)

    # Use the same sliding logic as blocks
    final_x, final_y, _ = _slide_on_ice(start_x, start_y, dx, dy, world, puzzle)
    return (final_x, final_y)

"""Switches, doors, and gates mechanics."""

from typing import List, TYPE_CHECKING

from ..models import PuzzleElement, PuzzleElementType, DungeonPuzzle

if TYPE_CHECKING:
    from ...world import World


def activate_element(element: PuzzleElement, puzzle: DungeonPuzzle) -> List[str]:
    """
    Activate an element (switch, lever, plate).

    Returns list of linked element IDs that changed state.
    """
    changed_ids = []

    if element.element_type == PuzzleElementType.PRESSURE_PLATE:
        if element.state == "default":
            element.state = "activated"
            element.visual_state = "glowing"
            changed_ids.append(element.element_id)
        # Pressure plates don't toggle off when deactivated, they're state-based

    elif element.element_type == PuzzleElementType.SWITCH:
        # Toggle switch
        if element.state == "default" or element.state == "off":
            element.state = "on"
        else:
            element.state = "off"
        changed_ids.append(element.element_id)

    elif element.element_type == PuzzleElementType.LEVER:
        # Lever stays in position (one-way activation)
        if element.state == "default" or element.state == "off":
            element.state = "on"
            changed_ids.append(element.element_id)

    # Update linked elements
    for linked_id in element.linked_elements:
        if linked_id in puzzle.elements:
            linked = puzzle.elements[linked_id]
            if linked.element_type == PuzzleElementType.DOOR:
                # Check if all linked plates/switches are activated
                if _check_door_conditions(linked, puzzle):
                    if linked.state == "closed":
                        linked.state = "open"
                        linked.solid = False
                        changed_ids.append(linked_id)
                else:
                    if linked.state == "open":
                        linked.state = "closed"
                        linked.solid = True
                        changed_ids.append(linked_id)

            elif linked.element_type == PuzzleElementType.GATE:
                # Similar to door but may have more complex conditions
                if _check_gate_conditions(linked, puzzle):
                    if linked.state == "closed":
                        linked.state = "open"
                        linked.solid = False
                        changed_ids.append(linked_id)
                else:
                    if linked.state == "open":
                        linked.state = "closed"
                        linked.solid = True
                        changed_ids.append(linked_id)

    return changed_ids


def toggle_switch(element: PuzzleElement, puzzle: DungeonPuzzle) -> None:
    """Toggle switch state between on/off. Levers stay on once activated."""
    if element.element_type not in (PuzzleElementType.SWITCH, PuzzleElementType.LEVER):
        return

    if element.element_type == PuzzleElementType.LEVER:
        # Lever stays in position (one-way activation)
        if element.state == "off" or element.state == "default":
            element.state = "on"
    else:
        # Switch toggles
        if element.state == "off" or element.state == "default":
            element.state = "on"
        else:
            element.state = "off"

    _propagate_state_change(element, puzzle)


def _check_door_conditions(door: PuzzleElement, puzzle: DungeonPuzzle) -> bool:
    """Check if door should be open based on linked elements."""
    # Find elements that link to this door
    linked_elements = []
    for element in puzzle.elements.values():
        if door.element_id in element.linked_elements:
            linked_elements.append(element)

    if not linked_elements:
        return door.state == "open"

    # Check if all linked elements are activated
    requires_all = door.data.get("requires_all_links", True)
    if requires_all:
        return all(
            elem.state == "activated" or elem.state == "open"
            for elem in linked_elements
        )
    else:
        return any(
            elem.state == "activated" or elem.state == "open"
            for elem in linked_elements
        )


def _check_gate_conditions(gate: PuzzleElement, puzzle: DungeonPuzzle) -> bool:
    """Check if gate should be open based on conditions."""
    # Check if gate has explicit conditions in data
    if "conditions" in gate.data:
        conditions = gate.data["conditions"]
        for condition in conditions:
            element_id = condition.get("element_id")
            required_state = condition.get("state")
            if element_id in puzzle.elements:
                element = puzzle.elements[element_id]
                if element.state != required_state:
                    return False
        return True  # All conditions met

    # Fall back to door logic if no explicit conditions
    return _check_door_conditions(gate, puzzle)


def _propagate_state_change(element: PuzzleElement, puzzle: DungeonPuzzle) -> None:
    """Propagate state changes to linked elements."""
    for linked_id in element.linked_elements:
        if linked_id in puzzle.elements:
            linked = puzzle.elements[linked_id]
            if linked.element_type == PuzzleElementType.DOOR:
                if _check_door_conditions(linked, puzzle):
                    if linked.state == "closed":
                        linked.state = "open"
                        linked.solid = False
                        linked.visual_state = "animating"
                else:
                    if linked.state == "open":
                        linked.state = "closed"
                        linked.solid = True
                        linked.visual_state = "animating"
            elif linked.element_type == PuzzleElementType.GATE:
                if _check_gate_conditions(linked, puzzle):
                    if linked.state == "closed":
                        linked.state = "open"
                        linked.solid = False
                        linked.visual_state = "animating"
                else:
                    if linked.state == "open":
                        linked.state = "closed"
                        linked.solid = True
                        linked.visual_state = "animating"


def check_step_triggers(puzzle: DungeonPuzzle, x: int, y: int) -> List[str]:
    """Check for pressure plates and other step-triggered elements."""
    changed_ids = []

    plates = [
        elem for elem in puzzle.elements.values()
        if elem.element_type == PuzzleElementType.PRESSURE_PLATE and elem.x == x and elem.y == y
    ]

    for plate in plates:
        if plate.state == "default":
            changed_ids.extend(activate_element(plate, puzzle))

    return changed_ids

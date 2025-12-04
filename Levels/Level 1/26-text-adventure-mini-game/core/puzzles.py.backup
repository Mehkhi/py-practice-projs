"""Dungeon puzzle system for interactive puzzles."""

import copy
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional, Tuple, Set, TYPE_CHECKING

from .logging_utils import log_warning

if TYPE_CHECKING:
    from .world import World
    from .entities.player import Player


class PuzzleElementType(Enum):
    """Types of puzzle elements."""

    PUSHABLE_BLOCK = "pushable_block"
    PRESSURE_PLATE = "pressure_plate"
    SWITCH = "switch"  # Toggle on interact
    DOOR = "door"  # Blocks passage until opened
    GATE = "gate"  # Like door but requires multiple conditions
    TELEPORTER = "teleporter"
    ICE_TILE = "ice_tile"  # Slide until hitting wall
    PIT = "pit"  # Block falls in, fills pit
    LEVER = "lever"  # Stays in position
    TORCH_HOLDER = "torch_holder"  # Requires torch item


@dataclass
class PuzzleElement:
    """A single interactive puzzle element."""

    element_id: str
    element_type: PuzzleElementType
    x: int
    y: int
    state: str = "default"  # "default", "activated", "open", "closed", etc.
    linked_elements: List[str] = field(default_factory=list)  # IDs of elements this affects
    sprite_id: str = ""
    solid: bool = True
    data: Dict = field(default_factory=dict)  # Type-specific data
    visual_state: str = "normal"  # "normal", "flashing", "glowing", "animating", "error"


@dataclass
class DungeonPuzzle:
    """A complete puzzle with multiple elements and a solution state."""

    puzzle_id: str
    map_id: str
    name: str = ""
    elements: Dict[str, PuzzleElement] = field(default_factory=dict)
    solution_conditions: List[Dict] = field(default_factory=list)  # Conditions that must be true to "solve"
    reward_trigger_id: Optional[str] = None  # Trigger to fire when solved
    solved: bool = False
    hint: str = ""  # Optional hint text
    _initial_state: Optional[Dict] = field(default=None, init=False, repr=False)  # For reset


@dataclass
class SequencePuzzle(DungeonPuzzle):
    """Puzzle requiring elements activated in specific order."""

    required_sequence: List[str] = field(default_factory=list)  # Element IDs in order
    current_sequence: List[str] = field(default_factory=list)  # Currently activated sequence

    def record_activation(self, element_id: str) -> Tuple[bool, bool]:
        """
        Record an activation. Returns (correct_so_far, puzzle_complete).

        If wrong, resets sequence.
        """
        if not self.required_sequence:
            return (True, True)  # No sequence required, always correct

        # Check if this is the next expected element
        expected_index = len(self.current_sequence)
        if expected_index >= len(self.required_sequence):
            # Sequence already complete, ignore
            return (True, True)

        expected_id = self.required_sequence[expected_index]
        if element_id == expected_id:
            # Correct - add to sequence
            self.current_sequence.append(element_id)
            # Check if sequence is now complete
            if len(self.current_sequence) == len(self.required_sequence):
                return (True, True)
            return (True, False)
        else:
            # Wrong - reset sequence
            self.current_sequence = []
            return (False, False)


class PuzzleManager:
    """Manages all dungeon puzzles and their state.

    Implements the Saveable protocol for automatic save/load via SaveContext.
    """

    save_key: str = "puzzles"

    def __init__(self, puzzles: Optional[Dict[str, DungeonPuzzle]] = None):
        """Initialize puzzle manager with optional puzzle definitions."""
        self.puzzles: Dict[str, DungeonPuzzle] = puzzles or {}
        self.active_puzzle_id: Optional[str] = None

        # Store initial states for reset functionality
        for puzzle in self.puzzles.values():
            self._save_initial_state(puzzle)

    def _save_initial_state(self, puzzle: DungeonPuzzle) -> None:
        """Save initial state of puzzle for reset functionality."""
        initial_elements = {}
        for element_id, element in puzzle.elements.items():
            # Store a deep copy so removed elements can be restored
            initial_elements[element_id] = copy.deepcopy(element)
        puzzle._initial_state = {
            "elements": initial_elements,
            "solved": puzzle.solved,
        }

    def get_puzzle_for_map(self, map_id: str) -> Optional[DungeonPuzzle]:
        """Get the puzzle on a given map, if any."""
        for puzzle in self.puzzles.values():
            if puzzle.map_id == map_id:
                return puzzle
        return None

    def get_element_at(self, map_id: str, x: int, y: int) -> Optional[PuzzleElement]:
        """Get puzzle element at position."""
        puzzle = self.get_puzzle_for_map(map_id)
        if not puzzle:
            return None

        for element in puzzle.elements.values():
            if element.x == x and element.y == y:
                return element
        return None

    def push_block(
        self, element: PuzzleElement, direction: str, world: "World"
    ) -> bool:
        """
        Attempt to push a block in a direction.

        Returns True if block moved.

        Handles: collision, pits, ice sliding, chain reactions.
        """
        if element.element_type != PuzzleElementType.PUSHABLE_BLOCK:
            return False

        puzzle = self.get_puzzle_for_map(world.current_map_id)
        if not puzzle:
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
            # Check for step triggers at the pit location
            self._check_step_triggers(world.current_map_id, final_x, final_y, is_block=True, world=world)
            return True

        # Move block to new position
        old_x, old_y = element.x, element.y
        element.x = final_x
        element.y = final_y
        element.visual_state = "normal"  # Reset visual state after successful move

        # Check step triggers at new position
        self._check_step_triggers(world.current_map_id, final_x, final_y, is_block=True, world=world)

        # Check if puzzle is now solved
        if not puzzle.solved:
            if self.check_puzzle_solved(puzzle):
                puzzle.solved = True
                if puzzle.reward_trigger_id:
                    # Fire reward trigger
                    current_map = world.get_current_map()
                    current_map.fire_trigger(puzzle.reward_trigger_id)

        return True

    def activate_element(self, element: PuzzleElement) -> List[str]:
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
        puzzle = None
        for p in self.puzzles.values():
            if element.element_id in p.elements:
                puzzle = p
                break

        if puzzle:
            for linked_id in element.linked_elements:
                if linked_id in puzzle.elements:
                    linked = puzzle.elements[linked_id]
                    if linked.element_type == PuzzleElementType.DOOR:
                        # Check if all linked plates/switches are activated
                        if self._check_door_conditions(linked, puzzle):
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
                        if self._check_gate_conditions(linked, puzzle):
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


    def _check_door_conditions(self, door: PuzzleElement, puzzle: DungeonPuzzle) -> bool:
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

    def toggle_switch(self, element: PuzzleElement) -> None:
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

        self._propagate_state_change(element)

    def light_torch(self, element: PuzzleElement, player) -> bool:
        """Light torch if player has torch item. Returns True if successful."""
        if element.element_type != PuzzleElementType.TORCH_HOLDER:
            return False

        if element.state == "lit":
            return True  # Already lit

        # Check if player has torch or lantern
        if not player.inventory:
            return False

        has_torch = player.inventory.has("torch") or player.inventory.has("lantern")
        if not has_torch:
            return False

        # Consume the item
        if player.inventory.has("torch"):
            player.inventory.remove("torch", 1)
        elif player.inventory.has("lantern"):
            player.inventory.remove("lantern", 1)

        element.state = "lit"
        self._propagate_state_change(element)
        return True

    def use_teleporter(
        self, element: PuzzleElement, entity_x: int, entity_y: int
    ) -> Tuple[int, int]:
        """Get destination coordinates for teleporter."""
        if element.element_type != PuzzleElementType.TELEPORTER:
            return (entity_x, entity_y)

        if not element.linked_elements:
            return (entity_x, entity_y)

        # Find the linked teleporter
        puzzle = None
        for p in self.puzzles.values():
            if element.element_id in p.elements:
                puzzle = p
                break

        if not puzzle:
            return (entity_x, entity_y)

        linked_id = element.linked_elements[0]
        if linked_id in puzzle.elements:
            linked = puzzle.elements[linked_id]
            return (linked.x, linked.y)

        return (entity_x, entity_y)

    def _propagate_state_change(self, element: PuzzleElement) -> None:
        """Propagate state changes to linked elements."""
        puzzle = None
        for p in self.puzzles.values():
            if element.element_id in p.elements:
                puzzle = p
                break

        if not puzzle:
            return

        for linked_id in element.linked_elements:
            if linked_id in puzzle.elements:
                linked = puzzle.elements[linked_id]
                if linked.element_type == PuzzleElementType.DOOR:
                    if self._check_door_conditions(linked, puzzle):
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
                    if self._check_gate_conditions(linked, puzzle):
                        if linked.state == "closed":
                            linked.state = "open"
                            linked.solid = False
                            linked.visual_state = "animating"
                    else:
                        if linked.state == "open":
                            linked.state = "closed"
                            linked.solid = True
                            linked.visual_state = "animating"

    def _check_gate_conditions(self, gate: PuzzleElement, puzzle: DungeonPuzzle) -> bool:
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
        return self._check_door_conditions(gate, puzzle)

    def _check_step_triggers(
        self, map_id: str, x: int, y: int, is_block: bool, world: "World"
    ) -> None:
        """Check for pressure plates and other step-triggered elements."""
        puzzle = self.get_puzzle_for_map(map_id)
        if not puzzle:
            return

        plates = [
            elem for elem in puzzle.elements.values()
            if elem.element_type == PuzzleElementType.PRESSURE_PLATE and elem.x == x and elem.y == y
        ]

        for plate in plates:
            if plate.state == "default":
                self.activate_element(plate)
        if not puzzle.solved and self.check_puzzle_solved(puzzle):
            puzzle.solved = True
            if puzzle.reward_trigger_id:
                current_map = world.get_current_map()
                current_map.fire_trigger(puzzle.reward_trigger_id)

    def check_puzzle_solved(self, puzzle: DungeonPuzzle) -> bool:
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

    def is_on_ice(self, map_id: str, x: int, y: int) -> bool:
        """Check if a position is on an ice tile."""
        puzzle = self.get_puzzle_for_map(map_id)
        if not puzzle:
            return False

        for element in puzzle.elements.values():
            if element.element_type == PuzzleElementType.ICE_TILE and element.x == x and element.y == y:
                return True
        return False

    def calculate_player_slide_destination(
        self, start_x: int, start_y: int, dx: int, dy: int, world: "World"
    ) -> Tuple[int, int]:
        """
        Calculate where a player ends up when sliding on ice.

        Returns (final_x, final_y).
        """
        puzzle = self.get_puzzle_for_map(world.current_map_id)
        if not puzzle:
            return (start_x, start_y)

        # Check if starting position is on ice
        if not self.is_on_ice(world.current_map_id, start_x, start_y):
            return (start_x, start_y)

        # Use the same sliding logic as blocks
        final_x, final_y, _ = _slide_on_ice(start_x, start_y, dx, dy, world, puzzle)
        return (final_x, final_y)

    def reset_puzzle(self, puzzle_id: str) -> None:
        """Reset puzzle to initial state."""
        if puzzle_id not in self.puzzles:
            return

        puzzle = self.puzzles[puzzle_id]
        if not puzzle._initial_state:
            return

        # Restore elements (including ones that were removed like pit-filled blocks)
        for element_id, saved_element in puzzle._initial_state["elements"].items():
            if element_id in puzzle.elements:
                element = puzzle.elements[element_id]
                element.x = saved_element.x
                element.y = saved_element.y
                element.state = saved_element.state
                element.solid = saved_element.solid
                element.sprite_id = saved_element.sprite_id
                element.linked_elements = list(saved_element.linked_elements)
                element.data = copy.deepcopy(saved_element.data)
                element.visual_state = "normal"
            else:
                restored = copy.deepcopy(saved_element)
                restored.visual_state = "normal"
                puzzle.elements[element_id] = restored

        # Restore solved state
        puzzle.solved = puzzle._initial_state["solved"]

    def serialize(self) -> Dict:
        """Serialize all puzzle states."""
        data = {
            "puzzles": {}
        }
        for puzzle_id, puzzle in self.puzzles.items():
            puzzle_data = {
                "puzzle_id": puzzle.puzzle_id,
                "solved": puzzle.solved,
                "elements": {}
            }
            if isinstance(puzzle, SequencePuzzle):
                puzzle_data["current_sequence"] = list(puzzle.current_sequence)
            for element_id, element in puzzle.elements.items():
                puzzle_data["elements"][element_id] = {
                    "x": element.x,
                    "y": element.y,
                    "state": element.state,
                }
            data["puzzles"][puzzle_id] = puzzle_data
        return data

    @classmethod
    def deserialize(
        cls, data: Dict, puzzle_definitions: Dict[str, DungeonPuzzle]
    ) -> "PuzzleManager":
        """Deserialize puzzle state."""
        manager = cls(puzzle_definitions)
        puzzles_data = data.get("puzzles", {})

        for puzzle_id, puzzle_data in puzzles_data.items():
            if puzzle_id not in manager.puzzles:
                continue

            puzzle = manager.puzzles[puzzle_id]
            puzzle.solved = puzzle_data.get("solved", False)
            if isinstance(puzzle, SequencePuzzle):
                puzzle.current_sequence = list(puzzle_data.get("current_sequence", []))

            elements_data = puzzle_data.get("elements", {})
            for element_id, element_data in elements_data.items():
                if element_id in puzzle.elements:
                    element = puzzle.elements[element_id]
                    element.x = element_data.get("x", element.x)
                    element.y = element_data.get("y", element.y)
                    element.state = element_data.get("state", element.state)

        return manager

    def deserialize_into(self, data: Dict) -> None:
        """Restore state from saved data (Saveable protocol)."""
        puzzles_data = data.get("puzzles", {})

        for puzzle_id, puzzle_data in puzzles_data.items():
            if puzzle_id not in self.puzzles:
                continue

            puzzle = self.puzzles[puzzle_id]
            puzzle.solved = puzzle_data.get("solved", False)
            if isinstance(puzzle, SequencePuzzle):
                puzzle.current_sequence = list(puzzle_data.get("current_sequence", []))

            elements_data = puzzle_data.get("elements", {})
            for element_id, element_data in elements_data.items():
                if element_id in puzzle.elements:
                    element = puzzle.elements[element_id]
                    element.x = element_data.get("x", element.x)
                    element.y = element_data.get("y", element.y)
                    element.state = element_data.get("state", element.state)


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

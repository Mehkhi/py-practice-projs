"""Puzzle manager with registry and persistence functionality."""

import copy
from typing import Dict, List, Optional, Tuple, TYPE_CHECKING

from .models import DungeonPuzzle, PuzzleElement
from .conditions import check_puzzle_solved
from .mechanics.blocks_ice import push_block, is_on_ice, calculate_player_slide_destination, calculate_push_destination
from .mechanics.switches import activate_element, toggle_switch, check_step_triggers, _check_gate_conditions
from .mechanics.teleporters import use_teleporter
from .mechanics.torches import light_torch

if TYPE_CHECKING:
    from .world import World
    from .entities.player import Player


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
        if element.element_type.value != "pushable_block":
            return False

        puzzle = self.get_puzzle_for_map(world.current_map_id)
        if not puzzle:
            return False

        # Calculate destination coordinates before moving the block
        final_x, final_y, _ = calculate_push_destination(
            element.x, element.y, direction, world, puzzle
        )

        # Use the mechanic function
        moved = push_block(element, direction, world, puzzle)

        # Check step triggers at destination position if moved
        # Use calculated coordinates so pit landings trigger correctly
        if moved:
            self._check_step_triggers(world.current_map_id, final_x, final_y, is_block=True, world=world)

            # Check if puzzle is now solved
            if not puzzle.solved:
                if check_puzzle_solved(puzzle):
                    puzzle.solved = True
                    if puzzle.reward_trigger_id:
                        # Fire reward trigger
                        current_map = world.get_current_map()
                        current_map.fire_trigger(puzzle.reward_trigger_id)

        return moved

    def activate_element(self, element: PuzzleElement) -> List[str]:
        """
        Activate an element (switch, lever, plate).

        Returns list of linked element IDs that changed state.
        """
        # Find the puzzle containing this element
        puzzle = None
        for p in self.puzzles.values():
            if element.element_id in p.elements:
                puzzle = p
                break

        if not puzzle:
            return []

        # Use the mechanic function
        return activate_element(element, puzzle)

    def toggle_switch(self, element: PuzzleElement) -> None:
        """Toggle switch state between on/off. Levers stay on once activated."""
        # Find the puzzle containing this element
        puzzle = None
        for p in self.puzzles.values():
            if element.element_id in p.elements:
                puzzle = p
                break

        if puzzle:
            toggle_switch(element, puzzle)

    def light_torch(self, element: PuzzleElement, player) -> bool:
        """Light torch if player has torch item. Returns True if successful."""
        # Find the puzzle containing this element
        puzzle = None
        for p in self.puzzles.values():
            if element.element_id in p.elements:
                puzzle = p
                break

        if not puzzle:
            return False

        # Use the mechanic function
        return light_torch(element, player, puzzle)

    def use_teleporter(
        self, element: PuzzleElement, entity_x: int, entity_y: int
    ) -> Tuple[int, int]:
        """Get destination coordinates for teleporter."""
        # Find the puzzle containing this element
        puzzle = None
        for p in self.puzzles.values():
            if element.element_id in p.elements:
                puzzle = p
                break

        if not puzzle:
            return (entity_x, entity_y)

        # Use the mechanic function
        return use_teleporter(element, entity_x, entity_y, puzzle)

    def _check_step_triggers(
        self, map_id: str, x: int, y: int, is_block: bool, world: "World"
    ) -> None:
        """Check for pressure plates and other step-triggered elements."""
        puzzle = self.get_puzzle_for_map(map_id)
        if not puzzle:
            return

        # Use the mechanic function
        changed_ids = check_step_triggers(puzzle, x, y)

        # Check if puzzle is now solved (check even if no changes for other triggers)
        if not puzzle.solved:
            if check_puzzle_solved(puzzle):
                puzzle.solved = True
                if puzzle.reward_trigger_id:
                    current_map = world.get_current_map()
                    current_map.fire_trigger(puzzle.reward_trigger_id)

    def check_puzzle_solved(self, puzzle: DungeonPuzzle) -> bool:
        """
        Check if all solution conditions are met.

        Delegates to the conditions module.
        """
        return check_puzzle_solved(puzzle)

    def is_on_ice(self, map_id: str, x: int, y: int) -> bool:
        """Check if a position is on an ice tile."""
        puzzle = self.get_puzzle_for_map(map_id)
        if not puzzle:
            return False

        return is_on_ice(puzzle, x, y)

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

        return calculate_player_slide_destination(puzzle, start_x, start_y, dx, dy, world)

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
            # Handle sequence puzzles
            if hasattr(puzzle, 'current_sequence'):
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
            # Handle sequence puzzles
            if hasattr(puzzle, 'current_sequence'):
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
            # Handle sequence puzzles
            if hasattr(puzzle, 'current_sequence'):
                puzzle.current_sequence = list(puzzle_data.get("current_sequence", []))

            elements_data = puzzle_data.get("elements", {})
            for element_id, element_data in elements_data.items():
                if element_id in puzzle.elements:
                    element = puzzle.elements[element_id]
                    element.x = element_data.get("x", element.x)
                    element.y = element_data.get("y", element.y)
                    element.state = element_data.get("state", element.state)

    def _check_gate_conditions(self, gate: PuzzleElement, puzzle: DungeonPuzzle) -> bool:
        """Check if gate should be open based on conditions."""
        return _check_gate_conditions(gate, puzzle)

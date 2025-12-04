"""Data models for dungeon puzzle system."""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional, Tuple


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

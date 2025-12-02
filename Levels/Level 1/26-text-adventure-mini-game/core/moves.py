"""Move system for attack moves in combat."""

import json
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from .logging_utils import log_warning


@dataclass
class MoveAnimation:
    """Animation data for a move."""
    type: str  # "slash", "impact", "fire", "ice", "lightning", "dark", "holy", "burst", "ultimate", etc.
    color: Tuple[int, int, int]  # RGB color
    duration: float  # Animation duration in seconds
    frames: int  # Number of animation frames


@dataclass
class Move:
    """A combat move that can be used in battle."""
    id: str
    name: str
    description: str
    power: int
    accuracy: int  # 0-100 percentage
    element: str  # "physical", "fire", "ice", "lightning", "dark", "holy", "arcane"
    animation: MoveAnimation
    learn_level: int = 1  # Level at which this move can be learned
    hits: int = 1  # Number of hits (for multi-hit moves)
    status_inflict_id: Optional[str] = None  # Status effect to inflict
    status_chance: float = 0.0  # Chance to inflict status (0.0-1.0)


def load_move_from_dict(data: Dict) -> Move:
    """Create a Move from a dictionary."""
    anim_data = data.get("animation", {})
    animation = MoveAnimation(
        type=anim_data.get("type", "impact"),
        color=tuple(anim_data.get("color", [255, 255, 255])),
        duration=anim_data.get("duration", 0.3),
        frames=anim_data.get("frames", 4)
    )

    return Move(
        id=data["id"],
        name=data["name"],
        description=data.get("description", ""),
        power=data.get("power", 10),
        accuracy=data.get("accuracy", 90),
        element=data.get("element", "physical"),
        animation=animation,
        learn_level=data.get("learn_level", 1),
        hits=data.get("hits", 1),
        status_inflict_id=data.get("status_inflict_id"),
        status_chance=data.get("status_chance", 0.0)
    )


class MoveDatabase:
    """Database of all available moves."""

    def __init__(self):
        self.moves: Dict[str, Move] = {}
        self.class_starting_moves: Dict[str, List[str]] = {}
        self.class_learnable_moves: Dict[str, List[str]] = {}

    def get_move(self, move_id: str) -> Optional[Move]:
        """Get a move by ID."""
        return self.moves.get(move_id)

    def get_starting_moves(self, player_class: str) -> List[str]:
        """Get starting moves for a class."""
        return self.class_starting_moves.get(player_class, ["punch", "kick"])

    def get_learnable_moves(self, player_class: str) -> List[str]:
        """Get all moves learnable by a class."""
        return self.class_learnable_moves.get(player_class, [])

    def get_moves_for_level(self, player_class: str, level: int, current_moves: List[str]) -> List[Move]:
        """
        Get moves that can be learned at a specific level.

        Returns moves that:
        1. Are learnable by the class
        2. Have learn_level <= the given level
        3. Are not already known
        """
        learnable = self.get_learnable_moves(player_class)
        available = []

        for move_id in learnable:
            if move_id in current_moves:
                continue
            move = self.get_move(move_id)
            if move and move.learn_level <= level:
                available.append(move)

        return available

    def get_new_move_for_level(self, player_class: str, level: int, current_moves: List[str]) -> Optional[Move]:
        """
        Get a new move to learn at a specific level.

        Returns the highest-level move that can be learned at this level
        that isn't already known.
        """
        available = self.get_moves_for_level(player_class, level, current_moves)
        if not available:
            return None

        # Sort by learn_level descending to get the most advanced move
        available.sort(key=lambda m: m.learn_level, reverse=True)

        # Return the first move that matches the current level exactly, or the highest available
        for move in available:
            if move.learn_level == level:
                return move

        return None  # No new move at this exact level


def load_moves_database(path: str = os.path.join("data", "moves.json")) -> MoveDatabase:
    """Load the moves database from JSON."""
    db = MoveDatabase()

    if not os.path.exists(path):
        # Create default moves if file doesn't exist
        return db

    try:
        with open(path, "r") as f:
            data = json.load(f)
    except Exception as exc:
        log_warning(f"Failed to load moves data: {exc}")
        return db

    # Load moves
    for move_data in data.get("moves", []):
        move = load_move_from_dict(move_data)
        db.moves[move.id] = move

    # Load class starting moves
    db.class_starting_moves = data.get("class_starting_moves", {})

    # Load class learnable moves
    db.class_learnable_moves = data.get("class_learnable_moves", {})

    return db


# Global moves database instance
_moves_db: Optional[MoveDatabase] = None


def get_moves_database() -> MoveDatabase:
    """Get the global moves database, loading it if necessary."""
    global _moves_db
    if _moves_db is None:
        _moves_db = load_moves_database()
    return _moves_db


from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple, Dict

Coord = Tuple[int, int]

# Shapes are defined as 4x4 matrices per rotation state using coordinates of filled cells.
# Each shape lists 4 rotation states (0..3). For O, all states are the same.
SHAPES: Dict[str, List[List[Coord]]] = {
    "I": [
        [(0,1),(1,1),(2,1),(3,1)],
        [(2,0),(2,1),(2,2),(2,3)],
        [(0,2),(1,2),(2,2),(3,2)],
        [(1,0),(1,1),(1,2),(1,3)],
    ],
    "O": [
        [(1,1),(2,1),(1,2),(2,2)],
        [(1,1),(2,1),(1,2),(2,2)],
        [(1,1),(2,1),(1,2),(2,2)],
        [(1,1),(2,1),(1,2),(2,2)],
    ],
    "T": [
        [(1,1),(0,2),(1,2),(2,2)],
        [(1,1),(1,2),(2,1),(1,3)],
        [(0,2),(1,2),(2,2),(1,3)],
        [(1,1),(0,2),(1,2),(1,3)],
    ],
    "S": [
        [(1,1),(2,1),(0,2),(1,2)],
        [(1,1),(1,2),(2,2),(2,3)],
        [(1,2),(2,2),(0,3),(1,3)],
        [(0,1),(0,2),(1,2),(1,3)],
    ],
    "Z": [
        [(0,1),(1,1),(1,2),(2,2)],
        [(2,1),(1,2),(2,2),(1,3)],
        [(0,2),(1,2),(1,3),(2,3)],
        [(1,1),(0,2),(1,2),(0,3)],
    ],
    "J": [
        [(0,1),(0,2),(1,2),(2,2)],
        [(1,1),(2,1),(1,2),(1,3)],
        [(0,2),(1,2),(2,2),(2,3)],
        [(1,1),(1,2),(0,3),(1,3)],
    ],
    "L": [
        [(2,1),(0,2),(1,2),(2,2)],
        [(1,1),(1,2),(1,3),(2,3)],
        [(0,2),(1,2),(2,2),(0,3)],
        [(0,1),(1,1),(1,2),(1,3)],
    ],
}

KINDS = list(SHAPES.keys())

@dataclass
class Piece:
    kind: str
    rot: int = 0  # 0..3

    def blocks(self) -> List[Coord]:
        return SHAPES[self.kind][self.rot % 4]

    def rotated(self, delta: int) -> "Piece":
        return Piece(self.kind, (self.rot + delta) % 4)

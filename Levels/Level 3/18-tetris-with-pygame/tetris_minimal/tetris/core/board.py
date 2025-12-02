
from __future__ import annotations
from typing import List, Optional, Tuple

class Board:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        # grid[y][x] holds None or a piece kind (e.g., 'T')
        self.grid: List[List[Optional[str]]] = [
            [None for _ in range(width)] for _ in range(height)
        ]

    def inside(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and y < self.height

    def collides(self, cells: List[Tuple[int,int]], pos: Tuple[int,int]) -> bool:
        px, py = pos
        for (cx, cy) in cells:
            x, y = px + cx, py + cy
            # allow negative y (piece entering from above), but still collide if beyond bottom or x out of bounds
            if x < 0 or x >= self.width or y >= self.height:
                return True
            if y >= 0 and self.grid[y][x] is not None:
                return True
        return False

    def lock_piece(self, kind: str, cells: List[Tuple[int,int]], pos: Tuple[int,int]) -> int:
        px, py = pos
        for (cx, cy) in cells:
            x, y = px + cx, py + cy
            if y >= 0:
                self.grid[y][x] = kind
        cleared = self._clear_lines()
        return cleared

    def _clear_lines(self) -> int:
        new_rows: List[List[Optional[str]]] = []
        cleared = 0
        for row in self.grid:
            if all(cell is not None for cell in row):
                cleared += 1
            else:
                new_rows.append(row)
        while len(new_rows) < self.height:
            new_rows.insert(0, [None for _ in range(self.width)])
        self.grid = new_rows
        return cleared

    def drop_distance(self, cells, pos) -> int:
        # how many rows we can move down before colliding
        px, py = pos
        d = 0
        while True:
            trial_pos = (px, py + d + 1)
            if self.collides(cells, trial_pos):
                return d
            d += 1

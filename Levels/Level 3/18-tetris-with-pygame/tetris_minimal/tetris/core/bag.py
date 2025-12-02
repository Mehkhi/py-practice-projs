
import random
from typing import List
from .piece import KINDS

class Bag:
    def __init__(self, seed: int | None = None):
        self._seed = seed  # Store seed for deterministic recreation
        self.rng = random.Random(seed)
        self._bag: List[str] = []

    def _refill(self) -> None:
        self._bag = KINDS[:]
        self.rng.shuffle(self._bag)

    def take(self) -> str:
        if not self._bag:
            self._refill()
        return self._bag.pop()

    def peek(self) -> str:
        if not self._bag:
            self._refill()
        return self._bag[-1]

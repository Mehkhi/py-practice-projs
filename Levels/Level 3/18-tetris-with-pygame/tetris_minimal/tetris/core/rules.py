
from dataclasses import dataclass

SCORE_TABLE = {0:0, 1:100, 2:300, 3:500, 4:800}
LINES_PER_LEVEL = 10

def gravity_ms(level: int) -> int:
    # Decrease by ~60ms per level, not less than 80ms
    return max(80, 800 - (level - 1) * 60)

@dataclass
class ScoreState:
    score: int = 0
    level: int = 1
    lines: int = 0

    def on_clear(self, cleared: int) -> None:
        self.score += SCORE_TABLE.get(cleared, 0) * self.level
        self.lines += cleared
        # level up every LINES_PER_LEVEL lines
        target_level = self.lines // LINES_PER_LEVEL + 1
        if target_level > self.level:
            self.level = target_level

    def on_soft_drop(self) -> None:
        self.score += 1  # optional tiny reward per soft step

    def on_hard_drop(self, distance: int) -> None:
        self.score += 2 * distance

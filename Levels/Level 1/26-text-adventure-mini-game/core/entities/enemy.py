"""Enemy entity definition."""

from dataclasses import dataclass, field
from typing import Dict, List

from .base import Entity, _sync_base_and_current_skills


@dataclass
class Enemy(Entity):
    """Enemy entity for combat."""

    enemy_type: str = "generic"
    base_skills: List[str] = field(default_factory=list)
    skills: List[str] = field(default_factory=list)
    level: int = 1  # Enemy level for stat scaling and rewards
    difficulty: str = "normal"  # "easy", "normal", "hard", "elite", "boss"
    # Spare/mercy mechanic configuration
    spareable: bool = True  # Whether this enemy can be spared via Talk
    spare_threshold: int = 3  # Morale needed to spare (higher = harder to spare)
    spare_hp_threshold: int = 100  # HP% below which morale gain is doubled
    spare_messages: Dict[str, str] = field(
        default_factory=dict
    )  # Custom messages for spare stages

    def __post_init__(self) -> None:
        """Initialize enemy-specific defaults."""
        if self.faction == "neutral":
            self.faction = "enemy"
        _sync_base_and_current_skills(self)

    def is_dead(self) -> bool:
        """Check if enemy is dead."""
        return self.stats.is_dead() if self.stats else False

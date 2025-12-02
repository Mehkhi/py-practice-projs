"""Non-player character entity definition."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .base import Entity, _sync_base_and_current_skills


@dataclass
class NPC(Entity):
    """Non-player character entity."""

    dialogue_id: Optional[str] = None  # maps into dialogue.json
    role: Optional[str] = None
    base_skills: List[str] = field(default_factory=list)
    skills: List[str] = field(default_factory=list)
    default_map_id: Optional[str] = None  # where the NPC is usually found
    # Deprecated: use shop_id instead. Retained for backward compatibility.
    shop_inventory: Dict[str, int] = field(default_factory=dict)
    shop_id: Optional[str] = None  # reference to shop in data/shops.json (preferred)

    def __post_init__(self) -> None:
        """Initialize NPC-specific defaults."""
        if self.faction == "neutral":
            self.faction = "npc"
        self.solid = True  # NPCs block movement - player cannot walk through them
        _sync_base_and_current_skills(self)

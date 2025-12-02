"""Hints and discovery system for secret bosses.

This module manages hints that players can discover about secret bosses
through NPCs, lore items, environmental clues, and direct information.
"""

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Set, Tuple

if TYPE_CHECKING:
    pass


class HintType(Enum):
    """Types of hints about secret bosses."""

    RUMOR = "rumor"  # Vague NPC dialogue
    LORE_ITEM = "lore_item"  # Collectible text
    ENVIRONMENTAL = "environmental"  # Visual clue in world
    DIRECT = "direct"  # Clear direction


@dataclass
class BossHint:
    """A hint about a secret boss."""

    hint_id: str
    boss_id: str
    hint_type: HintType
    content: str
    location_map_id: Optional[str] = None
    location_x: Optional[int] = None
    location_y: Optional[int] = None
    trigger_type: str = "dialogue"  # "dialogue", "examine", "item"
    reveal_level: int = 1  # 1=vague, 2=moderate, 3=specific


class HintManager:
    """Manages discovery of secret boss hints.

    Implements the Saveable protocol for automatic save/load via SaveContext.
    """

    save_key: str = "hints"

    def __init__(self, hints: Dict[str, BossHint]):
        """Initialize the hint manager.

        Args:
            hints: Dictionary mapping hint_id to BossHint definitions
        """
        self.hints = hints
        self.discovered_hints: Set[str] = set()

    def discover_hint(self, hint_id: str) -> Optional[BossHint]:
        """Mark a hint as discovered. Returns the hint if new.

        Args:
            hint_id: The hint ID to mark as discovered

        Returns:
            The BossHint if newly discovered, None if already known
        """
        if hint_id in self.discovered_hints:
            return None
        self.discovered_hints.add(hint_id)
        return self.hints.get(hint_id)

    def get_hints_for_boss(self, boss_id: str) -> List[BossHint]:
        """Get all discovered hints for a boss.

        Args:
            boss_id: The boss ID to get hints for

        Returns:
            List of discovered BossHint objects for the boss
        """
        return [
            hint
            for hint in self.hints.values()
            if hint.boss_id == boss_id and hint.hint_id in self.discovered_hints
        ]

    def get_discovery_progress(self, boss_id: str) -> Tuple[int, int]:
        """Get (discovered, total) hints for a boss.

        Args:
            boss_id: The boss ID to check progress for

        Returns:
            Tuple of (discovered_count, total_count)
        """
        total = [hint for hint in self.hints.values() if hint.boss_id == boss_id]
        discovered = [
            hint for hint in total if hint.hint_id in self.discovered_hints
        ]
        return (len(discovered), len(total))

    def serialize(self) -> Dict[str, Any]:
        """Serialize discovery state.

        Returns:
            Dictionary containing serialized state
        """
        return {
            "discovered_hints": list(self.discovered_hints),
        }

    @classmethod
    def deserialize(
        cls, data: Dict[str, Any], hints: Dict[str, BossHint]
    ) -> "HintManager":
        """Deserialize state from saved data.

        Args:
            data: Dictionary containing serialized state
            hints: Dictionary mapping hint_id to BossHint definitions

        Returns:
            HintManager instance with restored state
        """
        manager = cls(hints)
        manager.discovered_hints = set(data.get("discovered_hints", []))
        return manager

    def deserialize_into(self, data: Dict[str, Any]) -> None:
        """Restore state from saved data (Saveable protocol)."""
        self.discovered_hints = set(data.get("discovered_hints", []))


__all__ = ["BossHint", "HintType", "HintManager"]

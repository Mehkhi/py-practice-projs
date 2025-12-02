"""Tutorial and help system for contextual tips and help overlays."""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional, Set, Tuple


class TipTrigger(Enum):
    """Events that can trigger contextual tips."""

    FIRST_BATTLE = auto()
    FIRST_SHOP_VISIT = auto()
    FIRST_LEVEL_UP = auto()
    FIRST_STATUS_EFFECT = auto()
    FIRST_PARTY_MEMBER = auto()
    FIRST_QUEST_ACCEPTED = auto()
    FIRST_ITEM_PICKUP = auto()
    FIRST_EQUIPMENT_CHANGE = auto()
    FIRST_SKILL_UNLOCK = auto()
    FIRST_CRAFTING = auto()
    FIRST_SAVE = auto()
    FIRST_DEATH = auto()
    LOW_HP_WARNING = auto()
    LOW_SP_WARNING = auto()
    ENTERED_DUNGEON = auto()
    ENTERED_TOWN = auto()
    NIGHT_TIME_FIRST = auto()
    SHOP_CLOSED = auto()
    FIRST_FISHING_SPOT = auto()
    FIRST_FISH_CAUGHT = auto()
    FIRST_LEGENDARY_FISH = auto()
    FIRST_GAMBLING = auto()
    FIRST_GAMBLING_WIN = auto()
    FIRST_GAMBLING_LOSS = auto()
    FIRST_ARENA_VISIT = auto()
    FIRST_ARENA_BET = auto()
    FIRST_DUNGEON_PUZZLE = auto()
    FIRST_PUZZLE_SOLVED = auto()
    FIRST_BRAIN_TEASER = auto()
    POST_GAME_START = auto()
    NEAR_COMPLETION = auto()


@dataclass
class TutorialTip:
    """A single tutorial tip."""

    tip_id: str
    trigger: TipTrigger
    title: str
    content: str
    priority: int = 5  # 1-10, higher = more important
    category: str = "general"  # For grouping in help overlay
    requires_tips: List[str] = field(default_factory=list)  # Tips that must be seen first


@dataclass
class HelpEntry:
    """An entry in the help overlay (always available)."""

    entry_id: str
    title: str
    content: str
    category: str
    order: int = 0  # Display order within category


class TutorialManager:
    """Manages tutorial tips, dismissals, and help entries.

    Implements the Saveable protocol for automatic save/load via SaveContext.
    """

    save_key: str = "tutorial"

    def __init__(self) -> None:
        self.tips: Dict[str, TutorialTip] = {}
        self.help_entries: Dict[str, HelpEntry] = {}
        self.dismissed_tips: Set[str] = set()  # Tips player chose not to see again
        self.seen_tips: Set[str] = set()  # Tips player has seen at least once
        self.pending_tips: List[str] = []  # Queue of tips to show
        self.tips_enabled: bool = True  # Global toggle

    def register_tip(self, tip: TutorialTip) -> None:
        """Register a tutorial tip."""
        self.tips[tip.tip_id] = tip

    def register_help_entry(self, entry: HelpEntry) -> None:
        """Register a help overlay entry."""
        self.help_entries[entry.entry_id] = entry

    def trigger_tip(self, trigger: TipTrigger) -> Optional[TutorialTip]:
        """
        Called when an event occurs that might trigger a tip.

        Returns the tip to show, or None if no tip should be shown.
        Checks: tips_enabled, already dismissed, prerequisites met.
        """
        if not self.tips_enabled:
            return None

        # Find tips that match this trigger
        matching_tips = [
            tip for tip in self.tips.values() if tip.trigger == trigger
        ]

        if not matching_tips:
            return None

        # Find the best tip to show (highest priority, prerequisites met)
        best_tip = None
        best_priority = -1

        for tip in matching_tips:
            if not self.can_show_tip(tip.tip_id):
                continue

            if tip.priority > best_priority:
                best_priority = tip.priority
                best_tip = tip

        if best_tip:
            # Add to pending queue if not already there
            if best_tip.tip_id not in self.pending_tips:
                self.pending_tips.append(best_tip.tip_id)
                # Sort by priority (descending)
                self.pending_tips.sort(
                    key=lambda tip_id: self.tips[tip_id].priority, reverse=True
                )

        return best_tip

    def dismiss_tip(self, tip_id: str, permanently: bool = False) -> None:
        """
        Mark a tip as seen. If permanently=True, never show again.
        """
        self.seen_tips.add(tip_id)

        if permanently:
            self.dismissed_tips.add(tip_id)

        # Remove from pending queue if present
        if tip_id in self.pending_tips:
            self.pending_tips.remove(tip_id)

    def get_help_entries_by_category(self) -> Dict[str, List[HelpEntry]]:
        """Get all help entries grouped by category."""
        grouped: Dict[str, List[HelpEntry]] = {}
        for entry in self.help_entries.values():
            if entry.category not in grouped:
                grouped[entry.category] = []
            grouped[entry.category].append(entry)

        # Sort each category by order
        for category in grouped:
            grouped[category].sort(key=lambda e: e.order)

        return grouped

    def get_pending_tip(self) -> Optional[TutorialTip]:
        """Get the next tip from the queue (highest priority first)."""
        if not self.pending_tips:
            return None

        tip_id = self.pending_tips.pop(0)
        return self.tips.get(tip_id)

    def can_show_tip(self, tip_id: str) -> bool:
        """Check if a tip can be shown (not dismissed, prerequisites met)."""
        if tip_id not in self.tips:
            return False

        if tip_id in self.dismissed_tips:
            return False

        tip = self.tips[tip_id]

        # Check prerequisites
        for required_tip_id in tip.requires_tips:
            if required_tip_id not in self.seen_tips:
                return False

        return True

    def serialize(self) -> Dict:
        """Serialize state for saving."""
        return {
            "dismissed_tips": list(self.dismissed_tips),
            "seen_tips": list(self.seen_tips),
            "tips_enabled": self.tips_enabled,
        }

    @classmethod
    def deserialize(
        cls,
        data: Dict,
        tips: Dict[str, TutorialTip],
        help_entries: Dict[str, HelpEntry],
    ) -> "TutorialManager":
        """Deserialize from save data."""
        manager = cls()
        manager.tips = tips
        manager.help_entries = help_entries
        manager.dismissed_tips = set(data.get("dismissed_tips", []))
        manager.seen_tips = set(data.get("seen_tips", []))
        manager.tips_enabled = data.get("tips_enabled", True)
        return manager

    def deserialize_into(self, data: Dict) -> None:
        """Restore state from saved data (Saveable protocol)."""
        self.dismissed_tips = set(data.get("dismissed_tips", []))
        self.seen_tips = set(data.get("seen_tips", []))
        self.tips_enabled = data.get("tips_enabled", True)

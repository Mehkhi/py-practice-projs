"""Data structures for achievements."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class AchievementCategory(Enum):
    """Categories for organizing achievements."""
    STORY = "story"
    COMBAT = "combat"
    EXPLORATION = "exploration"
    ACTIVITIES = "activities"
    CHALLENGE = "challenge"
    SECRET = "secret"
    # Legacy categories for backward compatibility
    QUESTS = "quests"  # Maps to STORY
    COLLECTION = "collection"  # Maps to ACTIVITIES
    SOCIAL = "social"  # Maps to ACTIVITIES
    MASTERY = "mastery"  # Maps to ACTIVITIES


class AchievementRarity(Enum):
    """Rarity tiers for achievements."""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"


@dataclass
class Achievement:
    """A single achievement definition."""
    id: str
    name: str
    description: str
    category: AchievementCategory = AchievementCategory.COMBAT
    rarity: AchievementRarity = AchievementRarity.COMMON
    icon_id: Optional[str] = None
    points: int = 10  # Achievement points value

    # Progress tracking
    target_count: int = 1  # How many times to trigger
    current_count: int = 0
    unlocked: bool = False
    unlock_time: Optional[str] = None  # ISO timestamp

    # Trigger conditions
    trigger_type: str = "flag"  # flag, kill, collect, quest, level, etc.
    trigger_target: str = ""  # What to track (enemy type, item id, etc.)

    # Rewards
    reward_gold: int = 0
    reward_exp: int = 0
    reward_items: Dict[str, int] = field(default_factory=dict)
    reward_title: Optional[str] = None  # Unlockable title

    # Hidden achievements
    hidden: bool = False  # Don't show until unlocked
    hidden_description: str = "???"  # Shown when hidden

    # Prerequisites
    required_achievements: List[str] = field(default_factory=list)

    def update_progress(self, amount: int = 1) -> bool:
        """Update achievement progress. Returns True if newly unlocked."""
        if self.unlocked:
            return False

        self.current_count = min(self.current_count + amount, self.target_count)

        if self.current_count >= self.target_count:
            self.unlocked = True
            self.unlock_time = datetime.now().isoformat()
            return True

        return False

    def get_progress_percent(self) -> float:
        """Get progress as a percentage (0.0 to 1.0)."""
        if self.target_count <= 0:
            return 1.0 if self.unlocked else 0.0
        return min(1.0, self.current_count / self.target_count)

    def get_display_description(self) -> str:
        """Get description, respecting hidden status."""
        if self.hidden and not self.unlocked:
            return self.hidden_description
        return self.description

    def get_display_name(self) -> str:
        """Get name, respecting hidden status."""
        if self.hidden and not self.unlocked:
            return "???"
        return self.name

    def get_unlock_display(self) -> str:
        """Get a friendly unlock timestamp or Locked label."""
        if not self.unlock_time or not self.unlocked:
            return "Locked"
        try:
            unlocked_at = datetime.fromisoformat(self.unlock_time)
            return unlocked_at.strftime("%b %d, %Y  %I:%M %p")
        except ValueError:
            return self.unlock_time

    def get_reward_lines(self) -> List[str]:
        """Return human-readable reward strings for UI rendering."""
        lines: List[str] = []

        if self.reward_title:
            lines.append(f"Title: {self.reward_title}")
        if self.reward_gold:
            lines.append(f"{self.reward_gold} Gold")
        if self.reward_exp:
            lines.append(f"{self.reward_exp} EXP")
        if self.reward_items:
            for item_id, qty in self.reward_items.items():
                display_name = item_id.replace("_", " ").title()
                lines.append(f"{display_name} x{qty}")

        if not lines:
            lines.append("No rewards")
        return lines

    def get_progress_text(self) -> str:
        """Return textual progress summary for detail panes."""
        if self.unlocked:
            return "Completed"
        if self.target_count <= 1:
            return "Incomplete"
        return f"{self.current_count}/{self.target_count}"

    def to_dict(self) -> Dict[str, Any]:
        """Serialize achievement state for saving."""
        return {
            "id": self.id,
            "current_count": self.current_count,
            "unlocked": self.unlocked,
            "unlock_time": self.unlock_time,
            "points": self.points,
        }

    @classmethod
    def from_definition(cls, data: Dict[str, Any]) -> "Achievement":
        """Create achievement from JSON definition."""
        category_str = data.get("category", "combat")
        category_map = {
            "quests": "story",
            "collection": "activities",
            "social": "activities",
            "mastery": "activities",
        }
        category_str = category_map.get(category_str, category_str)

        try:
            category = AchievementCategory(category_str)
        except ValueError:
            category = AchievementCategory.COMBAT

        rarity = AchievementRarity(data.get("rarity", "common"))

        points = data.get("points")
        if points is None:
            rarity_points = {
                "common": 10,
                "uncommon": 15,
                "rare": 25,
                "epic": 50,
                "legendary": 100,
            }
            points = rarity_points.get(rarity.value, 10)

        return cls(
            id=data["id"],
            name=data.get("name", data["id"]),
            description=data.get("description", ""),
            category=category,
            rarity=rarity,
            icon_id=data.get("icon_id"),
            points=points,
            target_count=data.get("target_count", 1),
            current_count=0,
            unlocked=False,
            unlock_time=None,
            trigger_type=data.get("trigger_type", "flag"),
            trigger_target=data.get("trigger_target", ""),
            reward_gold=data.get("reward_gold", 0),
            reward_exp=data.get("reward_exp", 0),
            reward_items=data.get("reward_items", {}),
            reward_title=data.get("reward_title"),
            hidden=data.get("hidden", False),
            hidden_description=data.get("hidden_description", "???"),
            required_achievements=data.get("required_achievements", []),
        )

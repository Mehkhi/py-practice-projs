"""Quest and QuestObjective dataclasses for the quest system."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class QuestStatus(Enum):
    """Status of a quest."""
    LOCKED = "locked"       # Not yet available
    AVAILABLE = "available" # Can be started
    ACTIVE = "active"       # Currently in progress
    COMPLETED = "completed" # All objectives done
    FAILED = "failed"       # Quest failed


class ObjectiveType(Enum):
    """Types of quest objectives."""
    KILL = "kill"           # Kill X enemies of type Y
    COLLECT = "collect"     # Collect X items
    TALK = "talk"           # Talk to NPC
    REACH = "reach"         # Reach a location/map
    FLAG = "flag"           # Check world flag
    CUSTOM = "custom"       # Custom condition


@dataclass
class QuestObjective:
    """A single objective within a quest."""
    id: str
    description: str
    objective_type: ObjectiveType = ObjectiveType.FLAG
    target: str = ""        # Target ID (enemy type, item id, npc id, map id, flag name)
    required_count: int = 1
    current_count: int = 0
    completed: bool = False
    optional: bool = False  # Optional objectives don't block completion

    def update_progress(self, amount: int = 1) -> bool:
        """Update objective progress and check for completion.

        This method increments the objective's current_count by the specified
        amount (capped at required_count) and marks it as completed if the
        threshold is reached.

        Args:
            amount: Amount to increment progress (default 1)

        Returns:
            True if the objective was newly completed (just reached required_count),
            False if already completed or not yet complete

        Progress is capped at required_count to prevent over-counting.
        Once completed, further calls return False without modifying state.

        Example:
            Objective requires 5 kills, current_count is 4:
            - update_progress(1) -> current_count becomes 5, completed=True, returns True
            - update_progress(1) -> current_count stays 5, returns False
        """
        if self.completed:
            return False
        self.current_count = min(self.current_count + amount, self.required_count)
        if self.current_count >= self.required_count:
            self.completed = True
            return True
        return False

    def set_completed(self) -> None:
        """Mark objective as completed."""
        self.current_count = self.required_count
        self.completed = True

    def get_progress_text(self) -> str:
        """Get progress display text."""
        if self.required_count == 1:
            return "[X]" if self.completed else "[ ]"
        return f"({self.current_count}/{self.required_count})"

    def to_dict(self) -> Dict[str, Any]:
        """Serialize objective to dict."""
        return {
            "id": self.id,
            "current_count": self.current_count,
            "completed": self.completed,
        }

    @classmethod
    def from_definition(cls, data: Dict[str, Any]) -> "QuestObjective":
        """Create objective from JSON definition."""
        return cls(
            id=data["id"],
            description=data.get("description", ""),
            objective_type=ObjectiveType(data.get("type", "flag")),
            target=data.get("target", ""),
            required_count=data.get("required_count", 1),
            current_count=0,
            completed=False,
            optional=data.get("optional", False),
        )


@dataclass
class Quest:
    """A quest with objectives and rewards."""
    id: str
    name: str
    description: str
    objectives: List[QuestObjective] = field(default_factory=list)
    status: QuestStatus = QuestStatus.LOCKED

    # Prerequisites
    required_flags: List[str] = field(default_factory=list)  # World flags needed to unlock
    required_quests: List[str] = field(default_factory=list) # Quest IDs that must be completed

    # Rewards
    reward_gold: int = 0
    reward_exp: int = 0
    reward_items: Dict[str, int] = field(default_factory=dict)  # item_id -> quantity
    reward_flags: List[str] = field(default_factory=list)  # Flags to set on completion
    reward_recipes: List[str] = field(default_factory=list)  # Recipe IDs to discover on completion

    # Class/Subclass-specific rewards: {class_id: {item_id: quantity}}
    class_rewards: Dict[str, Dict[str, int]] = field(default_factory=dict)
    subclass_rewards: Dict[str, Dict[str, int]] = field(default_factory=dict)

    # Metadata
    category: str = "main"  # main, side, bounty
    giver_npc: Optional[str] = None  # NPC who gives the quest
    turn_in_npc: Optional[str] = None  # NPC to turn in to (defaults to giver)
    tracked: bool = False  # Whether this quest is currently tracked in the HUD
    difficulty: str = "Normal"
    recommended_level: Optional[int] = None
    tags: List[str] = field(default_factory=list)

    # Failure conditions
    fail_on_flags: List[str] = field(default_factory=list)  # Flags that cause failure if set
    fail_on_npc_death: Optional[str] = None  # NPC ID whose death fails the quest
    time_limit_turns: Optional[int] = None  # Fail after X turns (for timed quests)
    turns_elapsed: int = 0  # Track turns for timed quests

    def is_complete(self) -> bool:
        """Check if all required objectives are completed."""
        return all(obj.completed for obj in self.objectives if not obj.optional)

    def get_active_objectives(self) -> List[QuestObjective]:
        """Get incomplete objectives."""
        return [obj for obj in self.objectives if not obj.completed]

    def get_objective(self, objective_id: str) -> Optional[QuestObjective]:
        """Get objective by ID."""
        for obj in self.objectives:
            if obj.id == objective_id:
                return obj
        return None

    def update_objective(self, objective_id: str, amount: int = 1) -> bool:
        """Update a specific objective's progress. Returns True if quest is now complete."""
        obj = self.get_objective(objective_id)
        if obj:
            obj.update_progress(amount)
        return self.is_complete()

    def check_flag_objectives(self, world_flags: Dict[str, Any]) -> bool:
        """Check and update flag-based objectives.

        This method checks all FLAG-type objectives in this quest and marks
        them as completed if the corresponding flag is set in world_flags.

        Args:
            world_flags: Dictionary of world flags (flag_name -> value)

        Returns:
            True if at least one objective was updated (marked as completed),
            False if no objectives were updated

        Only FLAG-type objectives are checked. Other objective types (KILL,
        COLLECT, TALK, REACH) are updated via their respective event handlers.

        This method is typically called by QuestManager.check_flag_objectives()
        which processes all active quests.
        """
        updated = False
        for obj in self.objectives:
            if obj.objective_type == ObjectiveType.FLAG and not obj.completed:
                if world_flags.get(obj.target):
                    obj.set_completed()
                    updated = True
        return updated

    def check_failure_conditions(self, world_flags: Dict[str, Any]) -> bool:
        """
        Check if any failure conditions are met.
        Returns True if the quest should fail.
        """
        if self.status != QuestStatus.ACTIVE:
            return False

        # Check fail_on_flags
        for flag in self.fail_on_flags:
            if world_flags.get(flag):
                return True

        # Check time limit
        if self.time_limit_turns is not None and self.turns_elapsed >= self.time_limit_turns:
            return True

        return False

    def increment_turn(self) -> bool:
        """
        Increment turn counter for timed quests.
        Returns True if quest has now exceeded time limit.
        """
        if self.status != QuestStatus.ACTIVE:
            return False
        if self.time_limit_turns is None:
            return False
        self.turns_elapsed += 1
        return self.turns_elapsed >= self.time_limit_turns

    def to_dict(self) -> Dict[str, Any]:
        """Serialize quest state to dict."""
        return {
            "id": self.id,
            "status": self.status.value,
            "objectives": [obj.to_dict() for obj in self.objectives],
            "tracked": self.tracked,
            "turns_elapsed": self.turns_elapsed,
        }

    @classmethod
    def from_definition(cls, data: Dict[str, Any]) -> "Quest":
        """Create quest from JSON definition."""
        objectives = [
            QuestObjective.from_definition(obj_data)
            for obj_data in data.get("objectives", [])
        ]
        return cls(
            id=data["id"],
            name=data.get("name", data["id"]),
            description=data.get("description", ""),
            objectives=objectives,
            status=QuestStatus.LOCKED,
            required_flags=data.get("required_flags", []),
            required_quests=data.get("required_quests", []),
            reward_gold=data.get("reward_gold", 0),
            reward_exp=data.get("reward_exp", 0),
            reward_items=data.get("reward_items", {}),
            reward_flags=data.get("reward_flags", []),
            reward_recipes=data.get("reward_recipes", []),
            class_rewards=data.get("class_rewards", {}),
            subclass_rewards=data.get("subclass_rewards", {}),
            category=data.get("category", "main"),
            giver_npc=data.get("giver_npc"),
            turn_in_npc=data.get("turn_in_npc"),
            fail_on_flags=data.get("fail_on_flags", []),
            fail_on_npc_death=data.get("fail_on_npc_death"),
            time_limit_turns=data.get("time_limit_turns"),
            difficulty=data.get("difficulty", "Normal"),
            recommended_level=data.get("recommended_level"),
            tags=list(data.get("tags", [])),
        )

    def get_rewards_for_class(self, player_class: Optional[str], player_subclass: Optional[str]) -> Dict[str, int]:
        """Get combined rewards including class/subclass-specific items."""
        rewards = dict(self.reward_items)

        # Add class-specific rewards
        if player_class and player_class in self.class_rewards:
            for item_id, qty in self.class_rewards[player_class].items():
                rewards[item_id] = rewards.get(item_id, 0) + qty

        # Add subclass-specific rewards
        if player_subclass and player_subclass in self.subclass_rewards:
            for item_id, qty in self.subclass_rewards[player_subclass].items():
                rewards[item_id] = rewards.get(item_id, 0) + qty

        return rewards

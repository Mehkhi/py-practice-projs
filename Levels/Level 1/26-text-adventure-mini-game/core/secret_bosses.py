"""Secret boss system for post-game content.

Secret bosses are powerful optional encounters with unique unlock conditions.
They can be discovered through hints and unlocked via multiple condition types.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, TYPE_CHECKING

from .time_system import TimeOfDay

if TYPE_CHECKING:
    from .achievements import AchievementManager
    from .entities import Player
    from .world import World
    from .post_game import PostGameManager


class UnlockConditionType(Enum):
    """Types of conditions to unlock secret bosses."""

    FLAG_SET = "flag_set"  # Specific flag must be true
    FLAGS_ALL = "flags_all"  # All listed flags must be true
    FLAGS_ANY = "flags_any"  # Any listed flag must be true
    ACHIEVEMENT = "achievement"  # Specific achievement unlocked
    BOSSES_DEFEATED = "bosses_defeated"  # List of bosses must be defeated
    ITEM_POSSESSED = "item_possessed"  # Must have specific item
    LEVEL_MINIMUM = "level_minimum"  # Player level requirement
    TIME_OF_DAY = "time_of_day"  # Must be specific time
    SPECIAL = "special"  # Custom condition check (uses flag pattern)


@dataclass
class UnlockCondition:
    """A single unlock condition."""

    condition_type: UnlockConditionType
    data: Dict[str, Any]
    description: str  # Human-readable hint
    hidden: bool = False  # If True, don't show in hints until close to unlock


@dataclass
class SecretBoss:
    """A secret boss definition."""

    boss_id: str
    name: str
    title: str  # e.g., "The Forgotten One"
    description: str
    encounter_id: str  # Reference to encounters.json
    location_map_id: str
    location_x: int
    location_y: int
    unlock_conditions: List[UnlockCondition]
    spawn_trigger_type: str  # "interact", "step", "time_based"
    lore_entries: List[str]  # IDs of lore fragments about this boss
    rewards: Dict[str, Any]
    unique_drops: List[str]  # Guaranteed item drops on first defeat
    achievement_id: Optional[str] = None
    rematch_available: bool = True  # Can fight again after first defeat
    post_game_only: bool = False


class SecretBossManager:
    """Manages secret boss discovery and encounters.

    Implements the Saveable protocol for automatic save/load via SaveContext.
    """

    save_key: str = "secret_bosses"

    def __init__(self, bosses: Dict[str, SecretBoss]):
        """Initialize the secret boss manager.

        Args:
            bosses: Dictionary mapping boss_id to SecretBoss definitions
        """
        self.bosses = bosses
        self.discovered: Set[str] = set()  # Boss IDs player knows about
        self.defeated: Set[str] = set()  # Boss IDs player has defeated
        self.available: Set[str] = set()  # Boss IDs currently unlocked

    def check_unlock_condition(
        self,
        condition: UnlockCondition,
        world: "World",
        player: "Player",
        achievement_manager: "AchievementManager",
        day_night_cycle: Optional[Any] = None,
    ) -> bool:
        """Check if a single condition is met.

        Args:
            condition: The unlock condition to check
            world: World object for flag checks
            player: Player object for level and inventory checks
            achievement_manager: AchievementManager for achievement checks
            day_night_cycle: Optional DayNightCycle for time checks

        Returns:
            True if condition is met, False otherwise
        """
        if condition.condition_type == UnlockConditionType.FLAG_SET:
            flag = condition.data.get("flag")
            if not flag:
                return False
            return world.get_flag(flag, False)

        elif condition.condition_type == UnlockConditionType.FLAGS_ALL:
            flags = condition.data.get("flags", [])
            if not flags:
                return False
            return all(world.get_flag(f, False) for f in flags)

        elif condition.condition_type == UnlockConditionType.FLAGS_ANY:
            flags = condition.data.get("flags", [])
            if not flags:
                return False
            return any(world.get_flag(f, False) for f in flags)

        elif condition.condition_type == UnlockConditionType.ACHIEVEMENT:
            ach_id = condition.data.get("achievement_id")
            if not ach_id:
                return False
            achievement = achievement_manager.get_achievement(ach_id)
            return achievement is not None and achievement.unlocked

        elif condition.condition_type == UnlockConditionType.BOSSES_DEFEATED:
            bosses = condition.data.get("boss_ids", [])
            if not bosses:
                return False
            return all(bid in self.defeated for bid in bosses)

        elif condition.condition_type == UnlockConditionType.ITEM_POSSESSED:
            item_id = condition.data.get("item_id")
            if not item_id:
                return False
            if not player.inventory:
                return False
            return player.inventory.has(item_id, 1)

        elif condition.condition_type == UnlockConditionType.LEVEL_MINIMUM:
            # Level checks are handled via post_game_manager in check_boss_available
            # This method is called from check_boss_available which has post_game_manager
            # For backward compatibility, we still check level here but it should
            # be bypassed by post_game_manager.check_level_lock in check_boss_available
            level = condition.data.get("level", 1)
            if not player.stats:
                return False
            return player.stats.level >= level

        elif condition.condition_type == UnlockConditionType.TIME_OF_DAY:
            required_time_str = condition.data.get("time")
            if not required_time_str or not day_night_cycle:
                return False
            try:
                required_time = TimeOfDay[required_time_str.upper()]
            except KeyError:
                return False
            current_time = day_night_cycle.get_time_of_day()
            return current_time == required_time

        elif condition.condition_type == UnlockConditionType.SPECIAL:
            # Check flag pattern: secret_boss_{boss_id}_unlocked
            # Note: boss_id needs to be passed from check_boss_available
            # For now, we'll use a generic flag check
            flag_name = condition.data.get("flag")
            if flag_name:
                return world.get_flag(flag_name, False)
            return False

        return False

    def check_boss_available(
        self,
        boss_id: str,
        world: "World",
        player: "Player",
        achievement_manager: "AchievementManager",
        post_game_manager: "PostGameManager",
        day_night_cycle: Optional[Any] = None,
    ) -> bool:
        """Check if a secret boss is currently available.

        Args:
            boss_id: The boss ID to check
            world: World object for flag checks
            player: Player object for level and inventory checks
            achievement_manager: AchievementManager for achievement checks
            post_game_manager: PostGameManager for post-game state and level checks,
                or a bool indicating post-game status (for testing)
            day_night_cycle: Optional DayNightCycle for time checks

        Returns:
            True if boss is available, False otherwise
        """
        boss = self.bosses.get(boss_id)
        if not boss:
            return False

        # Handle bool/None for backwards compatibility with tests
        if isinstance(post_game_manager, bool):
            is_post_game = post_game_manager

            def _level_ok(required: int) -> bool:
                if is_post_game:
                    return True
                return bool(player.stats and player.stats.level >= required)
        elif post_game_manager is None:
            is_post_game = False

            def _level_ok(required: int) -> bool:
                return bool(player.stats and player.stats.level >= required)
        else:
            is_post_game = post_game_manager.state.final_boss_defeated

            def _level_ok(required: int) -> bool:
                return post_game_manager.check_level_lock(
                    required, player.stats.level if player.stats else 0
                )

        # Post-game only check
        if boss.post_game_only and not is_post_game:
            return False

        # Check all unlock conditions
        for condition in boss.unlock_conditions:
            # Level requirement (removed post-game)
            if condition.condition_type == UnlockConditionType.LEVEL_MINIMUM:
                level_req = condition.data.get("level", 1)
                if not _level_ok(level_req):
                    return False
                continue  # Skip the normal check since we handled it above

            # For SPECIAL conditions, inject boss_id into data if needed
            if condition.condition_type == UnlockConditionType.SPECIAL:
                if "flag" not in condition.data:
                    # Use default pattern
                    condition.data["flag"] = f"secret_boss_{boss_id}_unlocked"

            if not self.check_unlock_condition(
                condition, world, player, achievement_manager, day_night_cycle
            ):
                return False

        return True

    def update_available_bosses(
        self,
        world: "World",
        player: "Player",
        achievement_manager: "AchievementManager",
        post_game_manager: "PostGameManager",
        day_night_cycle: Optional[Any] = None,
    ) -> List[str]:
        """Update which bosses are available.

        Args:
            world: World object for flag checks
            player: Player object for level and inventory checks
            achievement_manager: AchievementManager for achievement checks
            post_game_manager: PostGameManager for post-game state and level checks
            day_night_cycle: Optional DayNightCycle for time checks

        Returns:
            List of newly unlocked boss IDs
        """
        newly_unlocked = []

        for boss_id, boss in self.bosses.items():
            was_available = boss_id in self.available
            is_available = self.check_boss_available(
                boss_id,
                world,
                player,
                achievement_manager,
                post_game_manager,
                day_night_cycle,
            )

            if is_available and not was_available:
                self.available.add(boss_id)
                newly_unlocked.append(boss_id)
            elif not is_available and was_available:
                self.available.discard(boss_id)

        return newly_unlocked

    def discover_boss(self, boss_id: str) -> bool:
        """Mark a boss as discovered (player found hints).

        Args:
            boss_id: The boss ID to mark as discovered

        Returns:
            True if newly discovered, False if already known
        """
        if boss_id not in self.discovered:
            self.discovered.add(boss_id)
            return True
        return False

    def defeat_boss(self, boss_id: str) -> Dict[str, Any]:
        """Mark boss as defeated and return rewards.

        Args:
            boss_id: The boss ID that was defeated

        Returns:
            Dictionary containing rewards (includes unique_drops on first defeat)
        """
        boss = self.bosses.get(boss_id)
        if not boss:
            return {}

        first_defeat = boss_id not in self.defeated
        self.defeated.add(boss_id)

        rewards = dict(boss.rewards)
        if first_defeat:
            rewards["unique_drops"] = boss.unique_drops.copy()

        return rewards

    def create_mirror_encounter(self, player: "Player") -> Dict[str, Any]:
        """Create a dynamic encounter that mirrors the player.

        Called when entering mirror boss fight. The mirror boss copies
        the player's stats and abilities.

        Args:
            player: The player entity to mirror

        Returns:
            Dictionary containing encounter data with mirrored enemy
        """
        if not player.stats:
            # Fallback if player has no stats
            return {
                "enemies": [{
                    "name": "Shadow Unknown",
                    "sprite_id": "mirror_player",
                    "stats": {
                        "hp": 100,
                        "max_hp": 100,
                        "attack": 10,
                        "defense": 5,
                        "magic": 10,
                        "speed": 5
                    },
                    "skills": [],
                    "ai_profile": {
                        "behavior_type": "adaptive",
                        "mirrors_player": True
                    }
                }],
                "backdrop_id": "bg_mirror_realm",
                "difficulty": "secret"
            }

        # Copy player stats, with HP boosted by 20%
        mirror_hp = int(player.stats.max_hp * 1.2)
        mirror_stats = {
            "hp": mirror_hp,
            "max_hp": mirror_hp,
            "attack": player.stats.attack,
            "defense": player.stats.defense,
            "magic": player.stats.magic,
            "speed": player.stats.speed,
            "luck": player.stats.luck if hasattr(player.stats, "luck") else 1,
            "max_sp": player.stats.max_sp if hasattr(player.stats, "max_sp") else 10,
            "sp": player.stats.sp if hasattr(player.stats, "sp") else player.stats.max_sp if hasattr(player.stats, "max_sp") else 10
        }

        # Copy up to 4 player skills
        mirror_skills = list(player.skills)[:4] if player.skills else []

        return {
            "enemies": [{
                "name": f"Shadow {player.name}",
                "sprite_id": "mirror_player",
                "stats": mirror_stats,
                "skills": mirror_skills,
                "ai_profile": {
                    "behavior_type": "adaptive",
                    "mirrors_player": True
                }
            }],
            "backdrop_id": "bg_mirror_realm",
            "difficulty": "secret"
        }

    def get_unlock_hints(self, boss_id: str) -> List[str]:
        """Get hints for how to unlock a boss.

        Args:
            boss_id: The boss ID to get hints for

        Returns:
            List of hint descriptions (excludes hidden conditions)
        """
        boss = self.bosses.get(boss_id)
        if not boss:
            return []

        hints = []
        for condition in boss.unlock_conditions:
            if not condition.hidden:
                hints.append(condition.description)

        return hints

    def serialize(self) -> Dict[str, Any]:
        """Serialize discovery and defeat state.

        Returns:
            Dictionary containing serialized state
        """
        return {
            "discovered": list(self.discovered),
            "defeated": list(self.defeated),
            "available": list(self.available),
        }

    @classmethod
    def deserialize(
        cls, data: Dict[str, Any], bosses: Dict[str, SecretBoss]
    ) -> "SecretBossManager":
        """Deserialize state from saved data.

        Args:
            data: Dictionary containing serialized state
            bosses: Dictionary mapping boss_id to SecretBoss definitions

        Returns:
            SecretBossManager instance with restored state
        """
        manager = cls(bosses)
        manager.discovered = set(data.get("discovered", []))
        manager.defeated = set(data.get("defeated", []))
        manager.available = set(data.get("available", []))
        return manager

    def deserialize_into(self, data: Dict[str, Any]) -> None:
        """Restore state from saved data (Saveable protocol)."""
        self.discovered = set(data.get("discovered", []))
        self.defeated = set(data.get("defeated", []))
        self.available = set(data.get("available", []))

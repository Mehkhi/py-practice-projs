"""Post-game integration system for managing unlocks after final boss defeat."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Any, TYPE_CHECKING

if TYPE_CHECKING:
    pass


@dataclass
class PostGameUnlock:
    """Something that unlocks after beating the game."""

    unlock_id: str
    name: str
    description: str
    unlock_type: str  # "dungeon", "boss", "feature", "cosmetic", "difficulty"
    requires_ending: Optional[str] = None  # Specific ending required, or None for any


@dataclass
class PostGameState:
    """Tracks post-game progression."""

    final_boss_defeated: bool = False
    ending_achieved: Optional[str] = None
    post_game_time: float = 0.0  # Playtime after final boss
    secret_bosses_defeated: int = 0
    challenge_dungeons_cleared: int = 0
    true_ending_unlocked: bool = False


class PostGameManager:
    """Manages post-game content and unlocks.

    Implements the Saveable protocol for automatic save/load via SaveContext.
    """

    save_key: str = "post_game"

    def __init__(self, unlocks: Dict[str, PostGameUnlock]):
        """
        Initialize post-game manager.

        Args:
            unlocks: Dictionary mapping unlock_id to PostGameUnlock definitions
        """
        self.unlocks = unlocks
        self.state = PostGameState()
        self.active_unlocks: Set[str] = set()

    def on_final_boss_defeated(self, ending_id: str) -> List[PostGameUnlock]:
        """
        Called when final boss is defeated.

        Args:
            ending_id: The ending ID that was achieved

        Returns:
            List of newly unlocked content
        """
        self.state.final_boss_defeated = True
        self.state.ending_achieved = ending_id

        newly_unlocked = []
        for unlock_id, unlock in self.unlocks.items():
            if unlock_id in self.active_unlocks:
                continue

            # Check if this unlock is now available
            if unlock.requires_ending is None or unlock.requires_ending == ending_id:
                self.active_unlocks.add(unlock_id)
                newly_unlocked.append(unlock)

        return newly_unlocked

    def is_unlocked(self, unlock_id: str) -> bool:
        """
        Check if a specific unlock is active.

        Args:
            unlock_id: The unlock ID to check

        Returns:
            True if unlock is active, False otherwise
        """
        return unlock_id in self.active_unlocks

    def check_level_lock(self, required_level: int, player_level: int) -> bool:
        """
        Check if level requirement is met.
        Post-game removes all level locks.

        Args:
            required_level: The required level
            player_level: The player's current level

        Returns:
            True if requirement is met (always True post-game), False otherwise
        """
        if self.state.final_boss_defeated:
            return True  # All level locks removed
        return player_level >= required_level

    def add_post_game_time(self, dt: float) -> None:
        """Accumulate post-game playtime once credits have been cleared."""
        if dt < 0 or not self.state.final_boss_defeated:
            return
        self.state.post_game_time += float(dt)

    def get_post_game_message(self) -> str:
        """
        Get message to display on return to world after credits.

        Returns:
            Welcome message string
        """
        return (
            "Congratulations on completing the main story!\n\n"
            "All level restrictions have been removed.\n"
            "New challenges await:\n"
            "- All Challenge Dungeons are now accessible\n"
            "- Legendary tier content unlocked\n"
            "- Secret bosses may reveal themselves\n\n"
            "Seek the ultimate challenge!"
        )

    def serialize(self) -> Dict[str, Any]:
        """
        Serialize post-game state.

        Returns:
            Dictionary containing serialized state
        """
        return {
            "final_boss_defeated": self.state.final_boss_defeated,
            "ending_achieved": self.state.ending_achieved,
            "post_game_time": self.state.post_game_time,
            "secret_bosses_defeated": self.state.secret_bosses_defeated,
            "challenge_dungeons_cleared": self.state.challenge_dungeons_cleared,
            "true_ending_unlocked": self.state.true_ending_unlocked,
            "active_unlocks": list(self.active_unlocks),
        }

    @classmethod
    def deserialize(cls, data: Dict[str, Any], unlocks: Dict[str, PostGameUnlock]) -> "PostGameManager":
        """
        Deserialize post-game state.

        Args:
            data: Dictionary containing serialized state
            unlocks: Dictionary mapping unlock_id to PostGameUnlock definitions

        Returns:
            PostGameManager instance with restored state
        """
        manager = cls(unlocks)
        manager.state.final_boss_defeated = data.get("final_boss_defeated", False)
        manager.state.ending_achieved = data.get("ending_achieved")
        manager.state.post_game_time = data.get("post_game_time", 0.0)
        manager.state.secret_bosses_defeated = data.get("secret_bosses_defeated", 0)
        manager.state.challenge_dungeons_cleared = data.get("challenge_dungeons_cleared", 0)
        manager.state.true_ending_unlocked = data.get("true_ending_unlocked", False)
        manager.active_unlocks = set(data.get("active_unlocks", []))
        return manager

    def deserialize_into(self, data: Dict[str, Any]) -> None:
        """Restore state from saved data (Saveable protocol)."""
        self.state.final_boss_defeated = data.get("final_boss_defeated", False)
        self.state.ending_achieved = data.get("ending_achieved")
        self.state.post_game_time = data.get("post_game_time", 0.0)
        self.state.secret_bosses_defeated = data.get("secret_bosses_defeated", 0)
        self.state.challenge_dungeons_cleared = data.get("challenge_dungeons_cleared", 0)
        self.state.true_ending_unlocked = data.get("true_ending_unlocked", False)
        self.active_unlocks = set(data.get("active_unlocks", []))

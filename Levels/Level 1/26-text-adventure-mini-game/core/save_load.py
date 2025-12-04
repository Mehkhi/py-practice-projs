"""Save and load system for game state.

This module provides the SaveManager class which handles saving and loading
game state to/from numbered slots. The actual serialization, deserialization,
migration, and validation logic is delegated to submodules in core/save/.
"""

import json
import os
import tempfile
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

from .logging_utils import log_warning
from .path_validation import (
    ensure_directory_exists,
    validate_path_inside_base,
    validate_save_slot,
)
from .save import (
    DEFAULT_STARTING_MAP,
    SAVE_FILE_VERSION,
    DeserializationResources,
    SaveContext,
    deserialize_state,
    deserialize_state_from_context,
    serialize_state,
    serialize_state_from_context,
    validate_save_data,
)

if TYPE_CHECKING:
    from .achievements import AchievementManager
    from .brain_teasers import BrainTeaserManager
    from .entities import Player
    from .arena import ArenaManager
    from .fishing import FishingSystem
    from .gambling import GamblingManager
    from .npc_schedules import ScheduleManager
    from .puzzles import PuzzleManager
    from .quests import QuestManager
    from .time_system import DayNightCycle
    from .weather import WeatherSystem
    from .world import World
    from .challenge_dungeons import ChallengeDungeonManager
    from .secret_bosses import SecretBossManager
    from .post_game import PostGameManager
    from .tutorial_system import TutorialManager
    from .secret_boss_hints import HintManager

# Re-export constants for backwards compatibility
__all__ = ["SaveManager", "SaveContext", "SAVE_FILE_VERSION", "DEFAULT_STARTING_MAP"]


class SaveManager:
    """Manages saving and loading game state.

    This class provides high-level save/load operations using numbered slots.
    It handles atomic file writes to prevent corruption and provides
    preview functionality for save slot UI.
    """

    def __init__(
        self,
        save_dir: str = "saves",
        resources: Optional[DeserializationResources] = None
    ):
        """Initialize the SaveManager.

        Args:
            save_dir: Directory to store save files in
            resources: Optional cache of asset data/loaders reused across loads

        Raises:
            ValueError: If save_dir is invalid or cannot be created
        """
        # Validate and resolve save directory
        success, resolved_dir = ensure_directory_exists(save_dir, create_if_missing=True)
        if not success or not resolved_dir:
            raise ValueError(f"Invalid save directory: {save_dir}")
        self.save_dir = resolved_dir
        self.deserialization_resources: Optional[DeserializationResources] = resources or DeserializationResources()

    def _resolve_resources(
        self,
        resources: Optional[DeserializationResources]
    ) -> Optional[DeserializationResources]:
        """Choose per-call resources or the manager default."""
        if resources is not None:
            return resources
        return self.deserialization_resources

    def serialize_state(
        self,
        world: "World",
        player: "Player",
        quest_manager: Optional["QuestManager"] = None,
        day_night_cycle: Optional["DayNightCycle"] = None,
        achievement_manager: Optional["AchievementManager"] = None,
        weather_system: Optional["WeatherSystem"] = None,
        fishing_system: Optional["FishingSystem"] = None,
        puzzle_manager: Optional["PuzzleManager"] = None,
        brain_teaser_manager: Optional["BrainTeaserManager"] = None,
        gambling_manager: Optional["GamblingManager"] = None,
        arena_manager: Optional["ArenaManager"] = None,
        challenge_dungeon_manager: Optional["ChallengeDungeonManager"] = None,
        secret_boss_manager: Optional["SecretBossManager"] = None,
        hint_manager: Optional["HintManager"] = None,
        post_game_manager: Optional["PostGameManager"] = None,
        tutorial_manager: Optional["TutorialManager"] = None,
        schedule_manager: Optional["ScheduleManager"] = None
    ) -> Dict[str, Any]:
        """Serialize world, player, and quest state to a JSON-safe dict.

        Args:
            world: World object containing map and flag state
            player: Player object containing inventory, stats, party, etc.
            quest_manager: Optional QuestManager for quest state
            day_night_cycle: Optional DayNightCycle for time state
            achievement_manager: Optional AchievementManager for achievement state
            weather_system: Optional WeatherSystem for weather state
            puzzle_manager: Optional PuzzleManager for puzzle state
            brain_teaser_manager: Optional BrainTeaserManager for brain teaser state
            gambling_manager: Optional GamblingManager for gambling state
            arena_manager: Optional ArenaManager for arena state
            schedule_manager: Optional ScheduleManager for NPC schedule state

        Returns:
            Complete JSON-safe dictionary of game state
        """
        return serialize_state(
            world, player, quest_manager, day_night_cycle,
            achievement_manager, weather_system, fishing_system, puzzle_manager,
            brain_teaser_manager, gambling_manager, arena_manager,
            challenge_dungeon_manager, secret_boss_manager, hint_manager,
            post_game_manager, tutorial_manager, schedule_manager
        )

    def validate_save_data(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate save file structure and required fields.

        Args:
            data: The loaded save data dictionary

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        return validate_save_data(data)

    def deserialize_state(
        self,
        data: Dict[str, Any],
        world: "World",
        quest_manager: Optional["QuestManager"] = None,
        day_night_cycle: Optional["DayNightCycle"] = None,
        achievement_manager: Optional["AchievementManager"] = None,
        weather_system: Optional["WeatherSystem"] = None,
        fishing_system: Optional["FishingSystem"] = None,
        puzzle_manager: Optional["PuzzleManager"] = None,
        brain_teaser_manager: Optional["BrainTeaserManager"] = None,
        gambling_manager: Optional["GamblingManager"] = None,
        arena_manager: Optional["ArenaManager"] = None,
        challenge_dungeon_manager: Optional["ChallengeDungeonManager"] = None,
        secret_boss_manager: Optional["SecretBossManager"] = None,
        hint_manager: Optional["HintManager"] = None,
        post_game_manager: Optional["PostGameManager"] = None,
        tutorial_manager: Optional["TutorialManager"] = None,
        schedule_manager: Optional["ScheduleManager"] = None,
        resources: Optional[DeserializationResources] = None
    ) -> "Player":
        """Deserialize player state from a dict.

        This method handles version checking, migration, and recovery before
        deserializing the game state.

        Args:
            data: The loaded save data dictionary
            world: World object to restore state into
            quest_manager: Optional QuestManager for quest state
            day_night_cycle: Optional DayNightCycle for time state
            achievement_manager: Optional AchievementManager for achievement state
            weather_system: Optional WeatherSystem for weather state
            puzzle_manager: Optional PuzzleManager for puzzle state
            brain_teaser_manager: Optional BrainTeaserManager for brain teaser state
            gambling_manager: Optional GamblingManager for gambling state
            arena_manager: Optional ArenaManager for arena state
            challenge_dungeon_manager: Optional ChallengeDungeonManager for dungeon state
            secret_boss_manager: Optional SecretBossManager for secret boss state
            hint_manager: Optional HintManager for hint state
            post_game_manager: Optional PostGameManager for post-game state
            tutorial_manager: Optional TutorialManager for tutorial state
            schedule_manager: Optional ScheduleManager for NPC schedule state
            resources: Optional cache of asset data/loaders reused across loads

        Returns:
            Player object with restored state
        """
        resolved_resources = self._resolve_resources(resources)
        return deserialize_state(
            data, world, quest_manager, day_night_cycle,
            achievement_manager, weather_system, fishing_system, puzzle_manager,
            brain_teaser_manager, gambling_manager, arena_manager,
            challenge_dungeon_manager, secret_boss_manager, hint_manager,
            post_game_manager, tutorial_manager, schedule_manager, resolved_resources
        )

    def save_to_slot(
        self,
        slot: int,
        world: "World",
        player: "Player",
        quest_manager: Optional["QuestManager"] = None,
        day_night_cycle: Optional["DayNightCycle"] = None,
        achievement_manager: Optional["AchievementManager"] = None,
        weather_system: Optional["WeatherSystem"] = None,
        fishing_system: Optional["FishingSystem"] = None,
        puzzle_manager: Optional["PuzzleManager"] = None,
        brain_teaser_manager: Optional["BrainTeaserManager"] = None,
        gambling_manager: Optional["GamblingManager"] = None,
        arena_manager: Optional["ArenaManager"] = None,
        challenge_dungeon_manager: Optional["ChallengeDungeonManager"] = None,
        secret_boss_manager: Optional["SecretBossManager"] = None,
        hint_manager: Optional["HintManager"] = None,
        post_game_manager: Optional["PostGameManager"] = None,
        tutorial_manager: Optional["TutorialManager"] = None,
        schedule_manager: Optional["ScheduleManager"] = None
    ) -> None:
        """Save game state to a numbered slot.

        Uses atomic write (write to temp file, then rename) to prevent
        corruption if the save is interrupted.

        Args:
            slot: Save slot number (1-based)
            world: World object containing map and flag state
            player: Player object containing inventory, stats, party, etc.
            quest_manager: Optional QuestManager for quest state
            day_night_cycle: Optional DayNightCycle for time state
            achievement_manager: Optional AchievementManager for achievement state
            weather_system: Optional WeatherSystem for weather state
            puzzle_manager: Optional PuzzleManager for puzzle state
            brain_teaser_manager: Optional BrainTeaserManager for brain teaser state
            gambling_manager: Optional GamblingManager for gambling state
            arena_manager: Optional ArenaManager for arena state
            challenge_dungeon_manager: Optional ChallengeDungeonManager for dungeon state
            secret_boss_manager: Optional SecretBossManager for secret boss state
            hint_manager: Optional HintManager for hint state
            post_game_manager: Optional PostGameManager for post-game state
            tutorial_manager: Optional TutorialManager for tutorial state
            schedule_manager: Optional ScheduleManager for NPC schedule state

        Raises:
            ValueError: If slot number is invalid
        """
        # Validate slot number and generate safe filename
        is_valid, filename = validate_save_slot(slot)
        if not is_valid or not filename:
            raise ValueError(f"Invalid save slot number: {slot}")

        # Validate path stays within save directory
        is_valid_path, save_path = validate_path_inside_base(
            filename, self.save_dir, allow_absolute=False
        )
        if not is_valid_path or not save_path:
            raise ValueError(f"Invalid save path for slot {slot}")
        data = self.serialize_state(
            world, player, quest_manager, day_night_cycle,
            achievement_manager, weather_system, fishing_system, puzzle_manager,
            brain_teaser_manager, gambling_manager, arena_manager,
            challenge_dungeon_manager, secret_boss_manager, hint_manager,
            post_game_manager, tutorial_manager, schedule_manager
        )

        # Write to a temporary file first, then atomically rename
        # This prevents corruption if the process is interrupted during write
        temp_fd = None
        temp_path = None
        try:
            temp_fd, temp_path = tempfile.mkstemp(dir=self.save_dir, suffix=".json")
            with os.fdopen(temp_fd, 'w') as f:
                temp_fd = None  # os.fdopen takes ownership of the fd
                json.dump(data, f, indent=2)
            os.replace(temp_path, save_path)  # Atomic on POSIX; near-atomic on Windows
            temp_path = None  # Successfully moved, don't clean up
        except Exception:
            # Clean up temp file if something went wrong
            if temp_fd is not None:
                try:
                    os.close(temp_fd)
                except OSError:
                    pass
            if temp_path is not None and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except OSError:
                    pass
            raise

    def load_from_slot(
        self,
        slot: int,
        world: "World",
        quest_manager: Optional["QuestManager"] = None,
        day_night_cycle: Optional["DayNightCycle"] = None,
        achievement_manager: Optional["AchievementManager"] = None,
        weather_system: Optional["WeatherSystem"] = None,
        fishing_system: Optional["FishingSystem"] = None,
        puzzle_manager: Optional["PuzzleManager"] = None,
        brain_teaser_manager: Optional["BrainTeaserManager"] = None,
        gambling_manager: Optional["GamblingManager"] = None,
        arena_manager: Optional["ArenaManager"] = None,
        challenge_dungeon_manager: Optional["ChallengeDungeonManager"] = None,
        secret_boss_manager: Optional["SecretBossManager"] = None,
        hint_manager: Optional["HintManager"] = None,
        post_game_manager: Optional["PostGameManager"] = None,
        tutorial_manager: Optional["TutorialManager"] = None,
        schedule_manager: Optional["ScheduleManager"] = None,
        resources: Optional[DeserializationResources] = None
    ) -> "Player":
        """Load game state from a numbered slot.

        Args:
            slot: Save slot number (1-based)
            world: World object to restore state into
            quest_manager: Optional QuestManager for quest state
            day_night_cycle: Optional DayNightCycle for time state
            achievement_manager: Optional AchievementManager for achievement state
            weather_system: Optional WeatherSystem for weather state
            puzzle_manager: Optional PuzzleManager for puzzle state
            brain_teaser_manager: Optional BrainTeaserManager for brain teaser state
            gambling_manager: Optional GamblingManager for gambling state
            arena_manager: Optional ArenaManager for arena state
            secret_boss_manager: Optional SecretBossManager for secret boss state
            schedule_manager: Optional ScheduleManager for NPC schedule state
            resources: Optional cache of asset data/loaders reused across loads

        Returns:
            Player object with restored state

        Raises:
            FileNotFoundError: If the save slot does not exist
            ValueError: If the save file is corrupted (invalid JSON syntax) or slot is invalid
        """
        # Validate slot number and generate safe filename
        is_valid, filename = validate_save_slot(slot)
        if not is_valid or not filename:
            raise ValueError(f"Invalid save slot number: {slot}")

        # Validate path stays within save directory
        is_valid_path, save_path = validate_path_inside_base(
            filename, self.save_dir, allow_absolute=False
        )
        if not is_valid_path or not save_path:
            raise ValueError(f"Invalid save path for slot {slot}")

        if not os.path.exists(save_path):
            raise FileNotFoundError(f"Save slot {slot} not found")

        # Attempt to load JSON with error handling
        try:
            with open(save_path, 'r') as f:
                data = json.load(f)
        except json.JSONDecodeError as exc:
            log_warning(f"Save slot {slot}: JSON decode error at {save_path}: {exc}")
            # For completely corrupted JSON (syntax errors), we cannot recover
            # Only valid JSON with missing fields can be recovered
            raise ValueError(f"Save slot {slot} is corrupted (invalid JSON syntax) and cannot be recovered: {exc}") from exc
        except OSError as exc:
            log_warning(f"Save slot {slot}: IO error reading {save_path}: {exc}")
            raise ValueError(f"Save slot {slot} cannot be read: {exc}") from exc

        # Validate, migrate, and recover if needed (handled in deserialize_state)
        resolved_resources = self._resolve_resources(resources)
        return self.deserialize_state(
            data, world, quest_manager, day_night_cycle,
            achievement_manager, weather_system, fishing_system, puzzle_manager,
            brain_teaser_manager, gambling_manager, arena_manager,
            challenge_dungeon_manager, secret_boss_manager, hint_manager,
            post_game_manager, tutorial_manager, schedule_manager, resolved_resources
        )

    def slot_exists(self, slot: int) -> bool:
        """Check if a save slot exists.

        Args:
            slot: Save slot number (1-based)

        Returns:
            True if the slot exists, False otherwise
        """
        is_valid, filename = validate_save_slot(slot)
        if not is_valid or not filename:
            return False

        is_valid_path, save_path = validate_path_inside_base(
            filename, self.save_dir, allow_absolute=False
        )
        if not is_valid_path or not save_path:
            return False

        return os.path.exists(save_path)

    def get_slot_preview(self, slot: int) -> Optional[Dict[str, Any]]:
        """Get preview information for a save slot without fully loading.

        Returns a dict with:
            - name: Player name
            - level: Player level
            - location: Current map ID (formatted)
            - play_time: Formatted playtime string
            - timestamp: When the save was created
            - player_class: Player's class
            - player_subclass: Player's subclass

        Args:
            slot: Save slot number (1-based)

        Returns:
            Preview dictionary or None if slot doesn't exist or can't be read
        """
        is_valid, filename = validate_save_slot(slot)
        if not is_valid or not filename:
            return None

        is_valid_path, save_path = validate_path_inside_base(
            filename, self.save_dir, allow_absolute=False
        )
        if not is_valid_path or not save_path:
            return None

        if not os.path.exists(save_path):
            return None

        try:
            with open(save_path, 'r') as f:
                data = json.load(f)

            # Validate save data before generating preview
            is_valid, errors = self.validate_save_data(data)
            if not is_valid:
                log_warning(f"Save slot {slot}: Validation failed in preview: {', '.join(errors)}")
                return None

            player_data = data.get("player", {})
            meta_data = data.get("meta", {})
            world_data = data.get("world", {})
            stats_data = player_data.get("stats", {})

            # Format playtime
            play_time_seconds = meta_data.get("play_time_seconds", 0)
            if not isinstance(play_time_seconds, (int, float)):
                play_time_seconds = 0
            hours = int(play_time_seconds // 3600)
            minutes = int((play_time_seconds % 3600) // 60)
            play_time_str = f"{hours}h {minutes:02d}m"

            # Format timestamp
            timestamp_str = meta_data.get("timestamp", "")
            if timestamp_str:
                try:
                    dt = datetime.fromisoformat(timestamp_str)
                    timestamp_str = dt.strftime("%b %d, %Y %I:%M %p")
                except (ValueError, TypeError):
                    timestamp_str = "Unknown"
            else:
                timestamp_str = "Unknown"

            # Format location name
            location = world_data.get("current_map_id", "Unknown")
            location_formatted = location.replace("_", " ").title()

            return {
                "name": player_data.get("name", "Unknown"),
                "level": stats_data.get("level", 1),
                "location": location_formatted,
                "play_time": play_time_str,
                "timestamp": timestamp_str,
                "player_class": player_data.get("player_class", ""),
                "player_subclass": player_data.get("player_subclass", ""),
            }
        except (json.JSONDecodeError, OSError, KeyError):
            return None

    def delete_slot(self, slot: int) -> bool:
        """Delete a save slot.

        Args:
            slot: Save slot number (1-based)

        Returns:
            True if deleted successfully, False if not found or deletion failed
        """
        is_valid, filename = validate_save_slot(slot)
        if not is_valid or not filename:
            return False

        is_valid_path, save_path = validate_path_inside_base(
            filename, self.save_dir, allow_absolute=False
        )
        if not is_valid_path or not save_path:
            return False

        if os.path.exists(save_path):
            try:
                os.remove(save_path)
                return True
            except OSError as exc:
                log_warning(f"Failed to delete save slot {slot}: {exc}")
                return False
        return False

    # -------------------------------------------------------------------------
    # SaveContext-based API (preferred for new code)
    # -------------------------------------------------------------------------

    def serialize_with_context(self, context: SaveContext) -> Dict[str, Any]:
        """Serialize game state using SaveContext.

        This is the preferred API for new code. Instead of passing 15+ optional
        manager parameters, pass a single SaveContext with registered managers.

        Args:
            context: SaveContext containing world, player, and registered managers.

        Returns:
            Complete JSON-safe dictionary of game state.
        """
        return serialize_state_from_context(context)

    def deserialize_with_context(
        self,
        data: Dict[str, Any],
        context: SaveContext,
        resources: Optional[DeserializationResources] = None
    ) -> "Player":
        """Deserialize game state using SaveContext.

        This is the preferred API for new code. Instead of passing 15+ optional
        manager parameters, pass a single SaveContext with registered managers.

        Args:
            data: The loaded save data dictionary.
            context: SaveContext containing world, player, and registered managers.
            resources: Optional cache of asset data/loaders reused across loads

        Returns:
            Player object with restored state.
        """
        resolved_resources = self._resolve_resources(resources)
        return deserialize_state_from_context(data, context, resolved_resources)

    def save_to_slot_with_context(self, slot: int, context: SaveContext) -> None:
        """Save game state to a numbered slot using SaveContext.

        This is the preferred API for new code. Uses atomic write (write to
        temp file, then rename) to prevent corruption if the save is interrupted.

        Args:
            slot: Save slot number (1-based).
            context: SaveContext containing world, player, and registered managers.

        Raises:
            ValueError: If slot number is invalid
        """
        is_valid, filename = validate_save_slot(slot)
        if not is_valid or not filename:
            raise ValueError(f"Invalid save slot number: {slot}")

        is_valid_path, save_path = validate_path_inside_base(
            filename, self.save_dir, allow_absolute=False
        )
        if not is_valid_path or not save_path:
            raise ValueError(f"Invalid save path for slot {slot}")
        data = self.serialize_with_context(context)

        # Write to a temporary file first, then atomically rename
        temp_fd = None
        temp_path = None
        try:
            temp_fd, temp_path = tempfile.mkstemp(dir=self.save_dir, suffix=".json")
            with os.fdopen(temp_fd, 'w') as f:
                temp_fd = None  # os.fdopen takes ownership of the fd
                json.dump(data, f, indent=2)
            os.replace(temp_path, save_path)  # Atomic on POSIX
            temp_path = None  # Successfully moved
        except Exception:
            if temp_fd is not None:
                try:
                    os.close(temp_fd)
                except OSError:
                    pass
            if temp_path is not None and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except OSError:
                    pass
            raise

    def load_from_slot_with_context(
        self,
        slot: int,
        context: SaveContext,
        resources: Optional[DeserializationResources] = None
    ) -> "Player":
        """Load game state from a numbered slot using SaveContext.

        This is the preferred API for new code.

        Args:
            slot: Save slot number (1-based).
            context: SaveContext containing world, player, and registered managers.
            resources: Optional cache of asset data/loaders reused across loads

        Returns:
            Player object with restored state.

        Raises:
            FileNotFoundError: If the save slot does not exist.
            ValueError: If the save file is corrupted (invalid JSON syntax) or slot is invalid.
        """
        is_valid, filename = validate_save_slot(slot)
        if not is_valid or not filename:
            raise ValueError(f"Invalid save slot number: {slot}")

        is_valid_path, save_path = validate_path_inside_base(
            filename, self.save_dir, allow_absolute=False
        )
        if not is_valid_path or not save_path:
            raise ValueError(f"Invalid save path for slot {slot}")

        if not os.path.exists(save_path):
            raise FileNotFoundError(f"Save slot {slot} not found")

        try:
            with open(save_path, 'r') as f:
                data = json.load(f)
        except json.JSONDecodeError as exc:
            log_warning(f"Save slot {slot}: JSON decode error at {save_path}: {exc}")
            raise ValueError(
                f"Save slot {slot} is corrupted (invalid JSON syntax): {exc}"
            ) from exc
        except OSError as exc:
            log_warning(f"Save slot {slot}: IO error reading {save_path}: {exc}")
            raise ValueError(f"Save slot {slot} cannot be read: {exc}") from exc

        return self.deserialize_with_context(data, context, resources)

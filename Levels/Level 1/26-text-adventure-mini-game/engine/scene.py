"""Scene system for managing different game modes."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TYPE_CHECKING

import pygame

if TYPE_CHECKING:
    from core.save_load import SaveManager
    from core.quests import QuestManager
    from core.time_system import DayNightCycle
    from core.weather import WeatherSystem
    from core.achievements import AchievementManager
    from core.items import Item
    from core.npc_schedules import ScheduleManager
    from core.tutorial_system import TutorialManager
    from core.fishing import FishingSystem
    from core.brain_teasers import BrainTeaserManager
    from core.gambling import GamblingManager
    from core.arena import ArenaManager
    from core.challenge_dungeons import ChallengeDungeonManager
    from core.secret_bosses import SecretBossManager
    from core.post_game import PostGameManager
    from engine.secret_boss_hints import HintManager
    from engine.event_bus import EventBus


class Scene(ABC):
    """Base class for all game scenes."""

    def __init__(self, manager: Optional["SceneManager"] = None):
        self.manager = manager

    def get_manager_attr(self, name: str, caller: str = "") -> Optional[Any]:
        """Safely get a manager-like attribute from the scene manager.

        Args:
            name: Manager attribute name (e.g., 'achievement_manager', 'encounters_data')
            caller: Optional caller context for better log messages

        Returns:
            The attribute value (typically a manager or data store) or None if
            the scene manager is missing or the attribute is unavailable.

        Notes:
            Scenes should prefer this helper (or the typed SceneManager
            accessors such as get_achievement_manager()) instead of accessing
            SceneManager attributes directly, and must always handle a None
            result gracefully.
        """
        if not self.manager:
            from core.logging_utils import log_warning

            context = f" (requested by {caller})" if caller else ""
            log_warning(f"SceneManager not available when accessing {name}{context}")
            return None
        return self.manager.get_manager(name, caller)

    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle a pygame event."""
        pass

    @abstractmethod
    def update(self, dt: float) -> None:
        """Update scene state. dt is delta time in seconds."""
        pass

    @abstractmethod
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the scene to the surface."""
        pass


class SceneManager:
    """Manages the scene stack and provides access to game managers.

    Manager Categories:

    Core Managers (logically core, but may be None if a subsystem fails to load):
        - save_manager: Handles save/load operations
        - quest_manager: Tracks quest progress
        - achievement_manager: Tracks achievements

    Optional Managers (feature-specific, may be None):
        - tutorial_manager: First-time player guidance
        - gambling_manager: Gambling minigame state
        - arena_manager: Arena battle state
        - fishing_system: Fishing minigame state
        - brain_teaser_manager: Brain teaser puzzles
        - challenge_dungeon_manager: Challenge dungeon progress
        - secret_boss_manager: Secret boss encounters
        - hint_manager: Secret boss hint system
        - post_game_manager: Post-game unlocks

    Environmental Systems (world state):
        - day_night_cycle: Time of day
        - weather_system: Weather effects
        - schedule_manager: NPC schedules

    Data Stores (read-only databases):
        - party_prototypes: Party member definitions
        - items_db: Item database
        - encounters_data: Encounter definitions used by battles and bestiary

    All manager and data-store attributes are annotated as Optional so they can
    cleanly represent disabled features or failed loads. Scenes should retrieve
    them via Scene.get_manager_attr() or the dedicated get_<manager>() methods
    and be prepared to handle None.

    Use get_manager() for safe access.
    """

    def __init__(
        self,
        initial_scene: Scene,
        save_manager: Optional["SaveManager"] = None,
        save_slot: int = 1,
        quest_manager: Optional["QuestManager"] = None,
        day_night_cycle: Optional["DayNightCycle"] = None,
        weather_system: Optional["WeatherSystem"] = None,
        achievement_manager: Optional["AchievementManager"] = None,
        party_prototypes: Optional[Dict[str, Any]] = None,
        items_db: Optional[Dict[str, "Item"]] = None,
        schedule_manager: Optional["ScheduleManager"] = None,
        tutorial_manager: Optional["TutorialManager"] = None,
        fishing_system: Optional["FishingSystem"] = None,
        brain_teaser_manager: Optional["BrainTeaserManager"] = None,
        gambling_manager: Optional["GamblingManager"] = None,
        arena_manager: Optional["ArenaManager"] = None,
        challenge_dungeon_manager: Optional["ChallengeDungeonManager"] = None,
        secret_boss_manager: Optional["SecretBossManager"] = None,
        hint_manager: Optional["HintManager"] = None,
        post_game_manager: Optional["PostGameManager"] = None,
        encounters_data: Optional[Dict[str, Dict[str, Any]]] = None,
        event_bus: Optional["EventBus"] = None,
    ):
        """Initialize scene manager with core and optional managers.

        Core managers:
            - save_manager, quest_manager, achievement_manager
        Optional managers:
            - tutorial_manager, gambling_manager, arena_manager,
              fishing_system, brain_teaser_manager, challenge_dungeon_manager,
              secret_boss_manager, hint_manager, post_game_manager
        Environmental systems:
            - day_night_cycle, weather_system, schedule_manager
        Data stores:
            - party_prototypes, items_db
        """
        self.stack: List[Scene] = [initial_scene]
        self.save_manager = save_manager
        self.save_slot = max(1, int(save_slot))
        self.quest_manager = quest_manager
        self.day_night_cycle = day_night_cycle
        self.weather_system = weather_system
        self.achievement_manager = achievement_manager
        self.party_prototypes = party_prototypes or {}  # Loaded party member definitions
        self.items_db = items_db or {}  # Items database for equipment
        self.schedule_manager = schedule_manager
        self.tutorial_manager = tutorial_manager
        self.fishing_system = fishing_system
        self.brain_teaser_manager = brain_teaser_manager
        self.gambling_manager = gambling_manager
        self.arena_manager = arena_manager
        self.challenge_dungeon_manager = challenge_dungeon_manager
        self.secret_boss_manager = secret_boss_manager
        self.hint_manager = hint_manager
        self.post_game_manager = post_game_manager
        # Shared encounter definitions for scenes that need them (e.g. WorldScene).
        # This is treated like a manager-accessible data store rather than
        # a strict manager object.
        self.encounters_data: Optional[Dict[str, Dict[str, Any]]] = encounters_data
        # Shared event bus for high-level domain events (combat, exploration, etc.)
        self.event_bus: Optional["EventBus"] = event_bus
        self.quit_requested = False
        if initial_scene:
            initial_scene.manager = self

    def get_manager(self, name: str, caller: str = "") -> Optional[Any]:
        """Safely get a manager by name with logging if missing.

        Args:
            name: Manager attribute name (e.g., 'achievement_manager')
            caller: Optional caller context for better log messages

        Returns:
            The manager instance or None if not available
        """
        manager = getattr(self, name, None)
        if manager is None:
            # Suppress warnings for optional managers during auto-save operations
            # since it's expected that some optional managers may not be available
            if caller != "_try_auto_save":
                from core.logging_utils import log_warning

                context = f" (requested by {caller})" if caller else ""
                log_warning(f"{name} not available{context}")
        return manager

    def get_save_manager(self, caller: str = "") -> Optional["SaveManager"]:
        """Get save manager with logging if missing."""
        return self.get_manager("save_manager", caller)

    def get_quest_manager(self, caller: str = "") -> Optional["QuestManager"]:
        """Get quest manager with logging if missing."""
        return self.get_manager("quest_manager", caller)

    def get_achievement_manager(
        self, caller: str = ""
    ) -> Optional["AchievementManager"]:
        """Get achievement manager with logging if missing."""
        return self.get_manager("achievement_manager", caller)

    def get_day_night_cycle(self, caller: str = "") -> Optional["DayNightCycle"]:
        """Get day/night cycle with logging if missing."""
        return self.get_manager("day_night_cycle", caller)

    def get_weather_system(self, caller: str = "") -> Optional["WeatherSystem"]:
        """Get weather system with logging if missing."""
        return self.get_manager("weather_system", caller)

    def get_schedule_manager(self, caller: str = "") -> Optional["ScheduleManager"]:
        """Get schedule manager with logging if missing."""
        return self.get_manager("schedule_manager", caller)

    def get_tutorial_manager(self, caller: str = "") -> Optional["TutorialManager"]:
        """Get tutorial manager with logging if missing."""
        return self.get_manager("tutorial_manager", caller)

    def get_fishing_system(self, caller: str = "") -> Optional["FishingSystem"]:
        """Get fishing system with logging if missing."""
        return self.get_manager("fishing_system", caller)

    def get_brain_teaser_manager(
        self, caller: str = ""
    ) -> Optional["BrainTeaserManager"]:
        """Get brain teaser manager with logging if missing."""
        return self.get_manager("brain_teaser_manager", caller)

    def get_gambling_manager(self, caller: str = "") -> Optional["GamblingManager"]:
        """Get gambling manager with logging if missing."""
        return self.get_manager("gambling_manager", caller)

    def get_arena_manager(self, caller: str = "") -> Optional["ArenaManager"]:
        """Get arena manager with logging if missing."""
        return self.get_manager("arena_manager", caller)

    def get_challenge_dungeon_manager(
        self, caller: str = ""
    ) -> Optional["ChallengeDungeonManager"]:
        """Get challenge dungeon manager with logging if missing."""
        return self.get_manager("challenge_dungeon_manager", caller)

    def get_secret_boss_manager(
        self, caller: str = ""
    ) -> Optional["SecretBossManager"]:
        """Get secret boss manager with logging if missing."""
        return self.get_manager("secret_boss_manager", caller)

    def get_hint_manager(self, caller: str = "") -> Optional["HintManager"]:
        """Get hint manager with logging if missing."""
        return self.get_manager("hint_manager", caller)

    def get_post_game_manager(
        self, caller: str = ""
    ) -> Optional["PostGameManager"]:
        """Get post-game manager with logging if missing."""
        return self.get_manager("post_game_manager", caller)

    def current(self) -> Scene:
        """Get the current active scene."""
        return self.stack[-1]

    def push(self, scene: Scene) -> None:
        """Push a new scene onto the stack."""
        scene.manager = self
        self.stack.append(scene)

    def pop(self) -> None:
        """Pop the current scene from the stack."""
        if len(self.stack) > 1:
            self.stack.pop()

    def replace(self, scene: Scene) -> None:
        """Replace the current scene."""
        scene.manager = self
        self.stack[-1] = scene

    def get_scene_of_type(self, scene_type: type) -> Optional[Scene]:
        """Return the most recent scene on the stack matching the given type."""
        for scene in reversed(self.stack):
            if isinstance(scene, scene_type):
                return scene
        return None

"""Base classes and utilities for save deserialization."""

import os
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, Dict, Optional, Tuple, Protocol

from ...logging_utils import log_warning

if TYPE_CHECKING:
    from ...achievements import AchievementManager
    from ...arena import ArenaManager
    from ...brain_teasers import BrainTeaser, BrainTeaserManager
    from ...challenge_dungeons import ChallengeDungeonManager
    from ...entities import Player
    from ...fishing import FishingSystem
    from ...gambling import GamblingManager
    from ...npc_schedules import ScheduleManager
    from ...puzzles import DungeonPuzzle, PuzzleManager
    from ...quests import QuestManager
    from ...secret_boss_hints import HintManager
    from ...secret_bosses import SecretBossManager
    from ...time_system import DayNightCycle
    from ...tutorial_system import TutorialManager
    from ...weather import WeatherSystem
    from ...world import World


class DomainDeserializer(Protocol):
    """Protocol for domain-specific deserializers."""

    def deserialize(self, data: Dict[str, Any], context: "DeserializerContext", resources: "DeserializationResources") -> None:
        """Apply deserialization for a domain."""


@dataclass
class DeserializerContext:
    """Context passed to domain deserializers."""

    world: "World"
    player: Optional["Player"] = None
    items_db: Optional[Dict[str, Any]] = None
    quest_manager: Optional["QuestManager"] = None
    day_night_cycle: Optional["DayNightCycle"] = None
    achievement_manager: Optional["AchievementManager"] = None
    weather_system: Optional["WeatherSystem"] = None
    fishing_system: Optional["FishingSystem"] = None
    puzzle_manager: Optional["PuzzleManager"] = None
    brain_teaser_manager: Optional["BrainTeaserManager"] = None
    gambling_manager: Optional["GamblingManager"] = None
    arena_manager: Optional["ArenaManager"] = None
    challenge_dungeon_manager: Optional["ChallengeDungeonManager"] = None
    secret_boss_manager: Optional["SecretBossManager"] = None
    hint_manager: Optional["HintManager"] = None
    post_game_manager: Optional[Any] = None
    tutorial_manager: Optional["TutorialManager"] = None
    schedule_manager: Optional["ScheduleManager"] = None


@dataclass
class DeserializationResources:
    """Cache for asset data used during deserialization."""

    items_db: Optional[Dict[str, Any]] = None
    skill_trees: Optional[Dict[str, Any]] = None
    fish_db: Optional[Dict[str, Any]] = None
    fishing_spots: Optional[Dict[str, Any]] = None
    puzzle_definitions: Optional[Dict[str, "DungeonPuzzle"]] = None
    brain_teaser_definitions: Optional[Dict[str, "BrainTeaser"]] = None
    challenge_dungeons: Optional[Dict[str, Any]] = None
    challenge_modifiers: Optional[Dict[str, Any]] = None
    secret_boss_definitions: Optional[Dict[str, Any]] = None
    hint_definitions: Optional[Dict[str, Any]] = None
    post_game_unlocks: Optional[Dict[str, Any]] = None
    tutorial_data: Optional[Tuple[Dict[str, Any], Dict[str, Any]]] = None
    items_loader: Optional[Callable[[], Dict[str, Any]]] = None
    skill_tree_loader: Optional[Callable[[], Dict[str, Any]]] = None
    fishing_loader: Optional[Callable[[], Tuple[Dict[str, Any], Dict[str, Any]]]] = None
    puzzle_loader: Optional[Callable[[], Dict[str, "DungeonPuzzle"]]] = None
    brain_teaser_loader: Optional[Callable[[], Dict[str, "BrainTeaser"]]] = None
    challenge_loader: Optional[Callable[[], Tuple[Dict[str, Any], Dict[str, Any]]]] = None
    secret_boss_loader: Optional[Callable[[], Dict[str, Any]]] = None
    hint_loader: Optional[Callable[[], Dict[str, Any]]] = None
    post_game_loader: Optional[Callable[[], Dict[str, Any]]] = None
    tutorial_loader: Optional[Callable[[], Tuple[Dict[str, Any], Dict[str, Any]]]] = None

    def resolve_items_db(self) -> Dict[str, Any]:
        """Return cached or loaded items database."""
        if self.items_db is not None:
            return self.items_db

        if self.items_loader:
            self.items_db = self.items_loader()
        else:
            from ...items import load_items_from_json

            self.items_db = load_items_from_json(os.path.join("data", "items.json"))
        return self.items_db

    def resolve_skill_trees(self) -> Dict[str, Any]:
        """Return cached or loaded skill trees."""
        if self.skill_trees is not None:
            return self.skill_trees

        from ...skill_tree import load_skill_trees_from_json

        loader = self.skill_tree_loader or load_skill_trees_from_json
        self.skill_trees = loader()
        return self.skill_trees

    def resolve_fishing_data(
        self,
        existing_fish_db: Optional[Dict[str, Any]] = None,
        existing_spots: Optional[Dict[str, Any]] = None,
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Return fishing definitions, preferring existing manager data."""
        if existing_fish_db is not None and existing_spots is not None:
            self.fish_db = existing_fish_db
            self.fishing_spots = existing_spots
            return existing_fish_db, existing_spots

        if self.fish_db is not None and self.fishing_spots is not None:
            return self.fish_db, self.fishing_spots

        if self.fishing_loader:
            fish_db, spots = self.fishing_loader()
        else:
            from core.loaders.fishing_loader import load_fishing_data

            fish_db, spots = load_fishing_data()

        self.fish_db = fish_db
        self.fishing_spots = spots
        return fish_db, spots

    def resolve_puzzles(self, puzzle_manager: Optional["PuzzleManager"] = None) -> Dict[str, "DungeonPuzzle"]:
        """Return puzzle definitions, preferring existing manager cache."""
        if puzzle_manager and getattr(puzzle_manager, "puzzles", None) is not None:
            self.puzzle_definitions = puzzle_manager.puzzles
            return puzzle_manager.puzzles

        if self.puzzle_definitions is not None:
            return self.puzzle_definitions

        if self.puzzle_loader:
            self.puzzle_definitions = self.puzzle_loader()
        else:
            from core.loaders.puzzle_loader import load_puzzles_from_json

            self.puzzle_definitions = load_puzzles_from_json()
        return self.puzzle_definitions

    def resolve_brain_teasers(
        self,
        brain_teaser_manager: Optional["BrainTeaserManager"] = None,
    ) -> Dict[str, "BrainTeaser"]:
        """Return brain teaser definitions, preferring existing manager cache."""
        if brain_teaser_manager and getattr(brain_teaser_manager, "teasers", None) is not None:
            self.brain_teaser_definitions = brain_teaser_manager.teasers
            return brain_teaser_manager.teasers

        if self.brain_teaser_definitions is not None:
            return self.brain_teaser_definitions

        if self.brain_teaser_loader:
            self.brain_teaser_definitions = self.brain_teaser_loader()
        else:
            from core.loaders.brain_teaser_loader import load_brain_teasers

            self.brain_teaser_definitions = load_brain_teasers()
        return self.brain_teaser_definitions

    def resolve_challenge_dungeons(
        self,
        challenge_dungeon_manager: Optional["ChallengeDungeonManager"] = None,
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Return challenge dungeon definitions."""
        if (
            challenge_dungeon_manager
            and getattr(challenge_dungeon_manager, "dungeons", None) is not None
            and getattr(challenge_dungeon_manager, "modifiers", None) is not None
        ):
            self.challenge_dungeons = challenge_dungeon_manager.dungeons
            self.challenge_modifiers = challenge_dungeon_manager.modifiers
            return challenge_dungeon_manager.dungeons, challenge_dungeon_manager.modifiers

        if self.challenge_dungeons is not None and self.challenge_modifiers is not None:
            return self.challenge_dungeons, self.challenge_modifiers

        if self.challenge_loader:
            dungeons, modifiers = self.challenge_loader()
        else:
            from core.loaders.challenge_loader import load_challenge_dungeons

            dungeons, modifiers = load_challenge_dungeons()

        self.challenge_dungeons = dungeons
        self.challenge_modifiers = modifiers
        return dungeons, modifiers

    def resolve_secret_bosses(
        self,
        secret_boss_manager: Optional["SecretBossManager"] = None,
    ) -> Dict[str, Any]:
        """Return secret boss definitions."""
        if secret_boss_manager and getattr(secret_boss_manager, "bosses", None) is not None:
            self.secret_boss_definitions = secret_boss_manager.bosses
            return secret_boss_manager.bosses

        if self.secret_boss_definitions is not None:
            return self.secret_boss_definitions

        if self.secret_boss_loader:
            self.secret_boss_definitions = self.secret_boss_loader()
        else:
            from core.loaders.secret_boss_loader import load_secret_bosses

            self.secret_boss_definitions = load_secret_bosses()
        return self.secret_boss_definitions

    def resolve_hint_definitions(self, hint_manager: Optional["HintManager"] = None) -> Dict[str, Any]:
        """Return secret boss hint definitions."""
        if hint_manager and getattr(hint_manager, "hints", None) is not None:
            self.hint_definitions = hint_manager.hints
            return hint_manager.hints

        if self.hint_definitions is not None:
            return self.hint_definitions

        if self.hint_loader:
            self.hint_definitions = self.hint_loader()
        else:
            from core.loaders.secret_boss_loader import load_secret_boss_hints

            self.hint_definitions = load_secret_boss_hints()
        return self.hint_definitions

    def resolve_post_game_unlocks(self, post_game_manager: Optional[Any] = None) -> Dict[str, Any]:
        """Return post-game unlock definitions."""
        if post_game_manager and getattr(post_game_manager, "unlocks", None) is not None:
            self.post_game_unlocks = post_game_manager.unlocks
            return post_game_manager.unlocks

        if self.post_game_unlocks is not None:
            return self.post_game_unlocks

        if self.post_game_loader:
            self.post_game_unlocks = self.post_game_loader()
        else:
            from ...data_loader import load_post_game_unlocks

            self.post_game_unlocks = load_post_game_unlocks()
        return self.post_game_unlocks

    def resolve_tutorial_data(
        self,
        tutorial_manager: Optional["TutorialManager"] = None,
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Return tutorial tips/help entries."""
        if tutorial_manager and (
            getattr(tutorial_manager, "tips", None) is not None
            and getattr(tutorial_manager, "help_entries", None) is not None
        ):
            self.tutorial_data = (tutorial_manager.tips, tutorial_manager.help_entries)
            return self.tutorial_data

        if self.tutorial_data is not None:
            return self.tutorial_data

        if self.tutorial_loader:
            tips, help_entries = self.tutorial_loader()
        else:
            from core.loaders.tutorial_loader import load_tutorial_tips

            tips, help_entries = load_tutorial_tips()

        self.tutorial_data = (tips, help_entries)
        return tips, help_entries


def safe_log_warning(message: str) -> None:
    """Log a warning while tolerating logger failures."""
    try:
        log_warning(message)
    except Exception:
        pass

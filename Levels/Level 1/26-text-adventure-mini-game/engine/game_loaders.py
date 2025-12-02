"""Helper functions for loading game data and systems."""

import os
from typing import Any, Dict, Optional

from core.logging_utils import log_warning
from core.world import Map, Tile, World, load_world_from_data
from core.dialogue import DialogueTree, load_dialogue_from_json
from core.items import Item, load_items_from_json
from core.encounters import load_encounters_from_json
from core.quests import QuestManager, load_quest_manager
from core.time_system import DayNightCycle
from core.weather import WeatherSystem
from core.achievements import AchievementManager, load_achievement_manager
from core.entities import load_party_members_from_json
from core.tutorial_system import TutorialManager
from core.fishing import FishingSystem
from core.brain_teasers import BrainTeaserManager
from core.arena import ArenaManager
from core.challenge_dungeons import ChallengeDungeonManager
from core.post_game import PostGameManager
from core.secret_bosses import SecretBossManager
from engine.secret_boss_hints import HintManager
from core.gambling import GamblingManager
from core.data_loader import (
    load_fishing_data,
    load_brain_teasers,
    load_arena_data,
    load_challenge_dungeons,
    load_post_game_unlocks,
    load_secret_bosses,
    load_secret_boss_hints,
    load_tutorial_data,
)


def load_world(config: Dict[str, Any]) -> World:
    """Load the game world from data files."""
    world = load_world_from_data("data")

    starting_map = config.get("starting_map", "forest_path")
    if starting_map in world.maps:
        world.current_map_id = starting_map

    if not world.maps:
        tiles = [[Tile("grass", True, "grass") for _ in range(10)] for _ in range(10)]
        default_map = Map("forest_path", 10, 10, tiles)
        world.add_map(default_map)
        world.current_map_id = "forest_path"

    return world


def load_dialogue() -> Optional[DialogueTree]:
    """Load dialogue tree from data/dialogue.json."""
    dialogue_path = os.path.join("data", "dialogue.json")
    if os.path.exists(dialogue_path):
        try:
            return load_dialogue_from_json(dialogue_path)
        except Exception as exc:
            log_warning(f"Failed to load dialogue from {dialogue_path}: {exc}")
    return None


def load_items_db(mod_loader: Any, mods_enabled: bool) -> Dict[str, Item]:
    """Load item definitions from data/items.json with optional mod overrides."""
    items_path = os.path.join("data", "items.json")
    merged_data = None
    if mod_loader and mods_enabled:
        merged_data = mod_loader.merge_data(items_path, data_key="items")
    return load_items_from_json(items_path, data=merged_data)


def load_encounters_data(mod_loader: Any, mods_enabled: bool) -> Dict[str, Dict[str, Any]]:
    """Load encounter definitions with optional mod overrides."""
    encounters_path = os.path.join("data", "encounters.json")
    merged_data = None
    if mod_loader and mods_enabled:
        merged_data = mod_loader.merge_data(encounters_path, data_key="encounters")
    return load_encounters_from_json(encounters_path, data=merged_data)


def load_quest_manager_safe(world_flags: Dict[str, Any]) -> Optional[QuestManager]:
    """Load quest definitions and create quest manager."""
    try:
        manager = load_quest_manager(os.path.join("data", "quests.json"))
        manager.check_prerequisites(world_flags)
        return manager
    except Exception as exc:
        log_warning(f"Failed to load quest manager from data/quests.json: {exc}")
        return None


def create_day_night_cycle(config: Dict[str, Any]) -> DayNightCycle:
    """Create and configure the day/night cycle system."""
    if not config.get("day_night_enabled", True):
        return DayNightCycle(paused=True)

    start_hour = config.get("day_night_start_hour", 6)
    time_scale = config.get("day_night_time_scale", 1.0)
    return DayNightCycle(
        current_time=float(start_hour * 60),
        time_scale=time_scale,
    )


def create_weather_system(config: Dict[str, Any]) -> WeatherSystem:
    """Create and configure the weather system."""
    if not config.get("weather_enabled", True):
        return WeatherSystem(enabled=False)

    return WeatherSystem(
        min_change_interval=config.get("weather_min_change_interval", 180.0),
        max_change_interval=config.get("weather_max_change_interval", 600.0),
        transition_duration=config.get("weather_transition_duration", 5.0),
    )


def load_achievement_manager_safe(event_bus: Any) -> Optional[AchievementManager]:
    """Load achievement definitions and create achievement manager."""
    try:
        return load_achievement_manager(os.path.join("data", "achievements.json"), event_bus=event_bus)
    except Exception as exc:
        log_warning(f"Failed to load achievement manager from data/achievements.json: {exc}")
        return None


def load_party_prototypes(items_db: Dict[str, Item]) -> Dict[str, Any]:
    """Load party member definitions for recruitment."""
    try:
        return load_party_members_from_json(
            os.path.join("data", "party_members.json"),
            items_db=items_db
        )
    except Exception as exc:
        log_warning(f"Failed to load party prototypes from data/party_members.json: {exc}")
        return {}


def create_tutorial_manager() -> TutorialManager:
    """Create and configure the tutorial manager."""
    try:
        tips, help_entries = load_tutorial_data()
        manager = TutorialManager()
        for tip in tips.values():
            manager.register_tip(tip)
        for entry in help_entries.values():
            manager.register_help_entry(entry)
        return manager
    except Exception as exc:
        log_warning(f"Failed to load tutorial manager from data/tutorial_tips.json: {exc}")
        return TutorialManager()


def load_fishing_system() -> FishingSystem:
    """Load fishing data and create FishingSystem."""
    try:
        fish_db, spots = load_fishing_data(os.path.join("data", "fishing.json"))
        return FishingSystem(fish_db, spots)
    except Exception as exc:
        log_warning(f"Failed to load fishing system from data/fishing.json: {exc}")
        return FishingSystem({}, {})


def load_brain_teaser_manager() -> BrainTeaserManager:
    """Load brain teaser data and create BrainTeaserManager."""
    try:
        teasers = load_brain_teasers(os.path.join("data", "brain_teasers.json"))
        return BrainTeaserManager(teasers)
    except Exception as exc:
        log_warning(f"Failed to load brain teaser manager from data/brain_teasers.json: {exc}")
        return BrainTeaserManager({})


def load_arena_manager() -> ArenaManager:
    """Load arena data and create ArenaManager."""
    try:
        return load_arena_data(os.path.join("data", "arena.json"))
    except Exception as exc:
        log_warning(f"Failed to load arena manager from data/arena.json: {exc}")
        return ArenaManager({})


def load_post_game_manager() -> PostGameManager:
    """Load post-game unlocks and create PostGameManager."""
    unlocks = load_post_game_unlocks("data/post_game_unlocks.json")
    return PostGameManager(unlocks)


def load_challenge_dungeon_manager() -> ChallengeDungeonManager:
    """Load challenge dungeon data and create ChallengeDungeonManager."""
    try:
        dungeons, modifiers = load_challenge_dungeons(os.path.join("data", "challenge_dungeons.json"))
        return ChallengeDungeonManager(dungeons, modifiers)
    except Exception as exc:
        log_warning(f"Failed to load challenge dungeon manager from data/challenge_dungeons.json: {exc}")
        return ChallengeDungeonManager({}, {})


def load_secret_boss_manager() -> SecretBossManager:
    """Load secret boss data and create SecretBossManager."""
    try:
        bosses = load_secret_bosses(os.path.join("data", "secret_bosses.json"))
        return SecretBossManager(bosses)
    except Exception as exc:
        log_warning(f"Failed to load secret boss manager from data/secret_bosses.json: {exc}")
        return SecretBossManager({})


def load_hint_manager() -> HintManager:
    """Load secret boss hints and create HintManager."""
    try:
        hints = load_secret_boss_hints(os.path.join("data", "secret_boss_hints.json"))
        return HintManager(hints)
    except Exception as exc:
        log_warning(f"Failed to load hint manager from data/secret_boss_hints.json: {exc}")
        return HintManager({})


def load_gambling_manager() -> GamblingManager:
    """Load gambling system."""
    return GamblingManager()

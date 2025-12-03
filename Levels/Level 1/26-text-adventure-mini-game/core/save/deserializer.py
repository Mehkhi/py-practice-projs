"""Coordinator for save deserialization."""

from typing import TYPE_CHECKING, Any, Dict, Optional

from ..logging_utils import log_warning
from .context import SaveContext
from .deserializers import (
    DEFAULT_DESERIALIZERS,
    DeserializationResources,
    DeserializerContext,
    deserialize_bestiary,
    deserialize_crafting_progress,
    deserialize_party_member,
    deserialize_skill_tree_progress,
    deserialize_stats,
    deserialize_world_runtime_state,
    run_deserializers,
    deserialize_puzzle_manager,
    deserialize_brain_teaser_manager,
    deserialize_gambling_manager,
    deserialize_challenge_dungeon_manager,
)
from .migration import get_save_version, migrate_save_data
from .serializer import SAVE_FILE_VERSION
from .validation import _is_validation_quiet, recover_partial_save, validate_save_data

if TYPE_CHECKING:
    from ..entities import Player
    from ..world import World


def _migrate_and_validate(data: Dict[str, Any]) -> Dict[str, Any]:
    version = get_save_version(data)
    if version < SAVE_FILE_VERSION:
        data = migrate_save_data(data, version, SAVE_FILE_VERSION)

    try:
        is_valid, errors = validate_save_data(data)
        if not is_valid:
            if not _is_validation_quiet():
                log_warning(f"Save data validation failed: {', '.join(errors)}. Attempting recovery.")
            data = recover_partial_save(data)
    except Exception as exc:
        if not _is_validation_quiet():
            log_warning(f"Error during save validation: {exc}. Attempting recovery.")
        data = recover_partial_save(data)
    return data


def _build_context(
    world: "World",
    quest_manager: Optional[Any] = None,
    day_night_cycle: Optional[Any] = None,
    achievement_manager: Optional[Any] = None,
    weather_system: Optional[Any] = None,
    fishing_system: Optional[Any] = None,
    puzzle_manager: Optional[Any] = None,
    brain_teaser_manager: Optional[Any] = None,
    gambling_manager: Optional[Any] = None,
    arena_manager: Optional[Any] = None,
    challenge_dungeon_manager: Optional[Any] = None,
    secret_boss_manager: Optional[Any] = None,
    hint_manager: Optional[Any] = None,
    post_game_manager: Optional[Any] = None,
    tutorial_manager: Optional[Any] = None,
    schedule_manager: Optional[Any] = None,
) -> DeserializerContext:
    return DeserializerContext(
        world=world,
        quest_manager=quest_manager,
        day_night_cycle=day_night_cycle,
        achievement_manager=achievement_manager,
        weather_system=weather_system,
        fishing_system=fishing_system,
        puzzle_manager=puzzle_manager,
        brain_teaser_manager=brain_teaser_manager,
        gambling_manager=gambling_manager,
        arena_manager=arena_manager,
        challenge_dungeon_manager=challenge_dungeon_manager,
        secret_boss_manager=secret_boss_manager,
        hint_manager=hint_manager,
        post_game_manager=post_game_manager,
        tutorial_manager=tutorial_manager,
        schedule_manager=schedule_manager,
    )


def _context_from_save_context(save_context: SaveContext) -> DeserializerContext:
    return DeserializerContext(
        world=save_context.world,
        quest_manager=save_context.get("quests"),
        day_night_cycle=save_context.get("day_night"),
        achievement_manager=save_context.get("achievements"),
        weather_system=save_context.get("weather"),
        fishing_system=save_context.get("fishing"),
        puzzle_manager=save_context.get("puzzles"),
        brain_teaser_manager=save_context.get("brain_teasers"),
        gambling_manager=save_context.get("gambling"),
        arena_manager=save_context.get("arena"),
        challenge_dungeon_manager=save_context.get("challenge_dungeons"),
        secret_boss_manager=save_context.get("secret_bosses"),
        hint_manager=save_context.get("hints"),
        post_game_manager=save_context.get("post_game"),
        tutorial_manager=save_context.get("tutorial"),
        schedule_manager=save_context.get("npc_schedules"),
    )


def deserialize_state(
    data: Dict[str, Any],
    world: "World",
    quest_manager: Optional[Any] = None,
    day_night_cycle: Optional[Any] = None,
    achievement_manager: Optional[Any] = None,
    weather_system: Optional[Any] = None,
    fishing_system: Optional[Any] = None,
    puzzle_manager: Optional[Any] = None,
    brain_teaser_manager: Optional[Any] = None,
    gambling_manager: Optional[Any] = None,
    arena_manager: Optional[Any] = None,
    challenge_dungeon_manager: Optional[Any] = None,
    secret_boss_manager: Optional[Any] = None,
    hint_manager: Optional[Any] = None,
    post_game_manager: Optional[Any] = None,
    tutorial_manager: Optional[Any] = None,
    schedule_manager: Optional[Any] = None,
    resources: Optional[DeserializationResources] = None,
) -> "Player":
    """Deserialize player state and related systems."""
    processed_data = _migrate_and_validate(data)
    resources = resources or DeserializationResources()
    context = _build_context(
        world=world,
        quest_manager=quest_manager,
        day_night_cycle=day_night_cycle,
        achievement_manager=achievement_manager,
        weather_system=weather_system,
        fishing_system=fishing_system,
        puzzle_manager=puzzle_manager,
        brain_teaser_manager=brain_teaser_manager,
        gambling_manager=gambling_manager,
        arena_manager=arena_manager,
        challenge_dungeon_manager=challenge_dungeon_manager,
        secret_boss_manager=secret_boss_manager,
        hint_manager=hint_manager,
        post_game_manager=post_game_manager,
        tutorial_manager=tutorial_manager,
        schedule_manager=schedule_manager,
    )
    run_deserializers(processed_data, context, resources, DEFAULT_DESERIALIZERS)
    return context.player


def deserialize_state_from_context(
    data: Dict[str, Any],
    context: SaveContext,
    resources: Optional[DeserializationResources] = None,
) -> "Player":
    """Deserialize game state using a SaveContext registry."""
    processed_data = _migrate_and_validate(data)
    resources = resources or DeserializationResources()
    deserializer_context = _context_from_save_context(context)
    run_deserializers(processed_data, deserializer_context, resources, DEFAULT_DESERIALIZERS)
    context.player = deserializer_context.player
    if processed_data:
        context.deserialize_managers(processed_data)
    return deserializer_context.player


__all__ = [
    "DeserializationResources",
    "deserialize_stats",
    "deserialize_skill_tree_progress",
    "deserialize_crafting_progress",
    "deserialize_bestiary",
    "deserialize_party_member",
    "deserialize_puzzle_manager",
    "deserialize_brain_teaser_manager",
    "deserialize_world_runtime_state",
    "deserialize_state",
    "deserialize_state_from_context",
    "deserialize_gambling_manager",
    "deserialize_challenge_dungeon_manager",
]

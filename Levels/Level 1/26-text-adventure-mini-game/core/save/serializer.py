"""Serialization logic for game state.

This module contains all functions for converting game objects to JSON-safe dictionaries.
"""

from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, Optional

from .context import SaveContext

if TYPE_CHECKING:
    from ..achievements import AchievementManager
    from ..bestiary import Bestiary
    from ..brain_teasers import BrainTeaserManager
    from ..crafting import CraftingProgress
    from ..entities import PartyMember, Player
    from ..arena import ArenaManager
    from ..fishing import FishingSystem
    from ..gambling import GamblingManager
    from ..npc_schedules import ScheduleManager
    from ..puzzles import PuzzleManager
    from ..quests import QuestManager
    from ..skill_tree import SkillTreeProgress
    from ..stats import Stats
    from ..time_system import DayNightCycle
    from ..weather import WeatherSystem
    from ..world import World
    from ..challenge_dungeons import ChallengeDungeonManager
    from ..secret_bosses import SecretBossManager
    from ..post_game import PostGameManager
    from ..tutorial_system import TutorialManager
    from ..secret_boss_hints import HintManager

# Current save file format version
SAVE_FILE_VERSION = 1

# Default starting map for new/recovered saves
DEFAULT_STARTING_MAP = "forest_path"


def serialize_entity_stats(stats: Optional["Stats"]) -> Optional[Dict[str, Any]]:
    """Serialize stats to a JSON-safe dict.

    Note: skill_tree_modifiers and equipment_modifiers are NOT serialized here.
    They are recalculated from skill_tree_progress and equipment on load
    to ensure bonuses are always consistent with the source data.

    Args:
        stats: Stats object to serialize, or None

    Returns:
        JSON-safe dictionary or None if stats is None
    """
    if not stats:
        return None
    status_effects = {}
    effects = getattr(stats, "status_effects", {})
    if isinstance(effects, dict):
        status_effects = {
            status_id: {
                "duration": getattr(effect, "duration", 0),
                "stacks": getattr(effect, "stacks", 0)
            }
            for status_id, effect in effects.items()
        }

    return {
        "max_hp": stats.max_hp,
        "hp": stats.hp,
        "max_sp": stats.max_sp,
        "sp": stats.sp,
        "attack": stats.attack,
        "defense": stats.defense,
        "magic": stats.magic,
        "speed": stats.speed,
        "luck": stats.luck,
        "level": stats.level,
        "exp": stats.exp,
        "status_effects": status_effects
    }


def serialize_skill_tree_progress(progress: "SkillTreeProgress") -> Dict[str, Any]:
    """Serialize skill tree progress to a JSON-safe dict.

    Args:
        progress: SkillTreeProgress object to serialize

    Returns:
        JSON-safe dictionary
    """
    return progress.serialize()


def serialize_party_member(member: "PartyMember") -> Dict[str, Any]:
    """Serialize a party member to a JSON-safe dict.

    Uses direct attribute access for all dataclass fields to surface bugs immediately.
    memory_value and memory_stat_type are now explicit dataclass fields via CombatantMixin.

    Args:
        member: PartyMember object to serialize

    Returns:
        JSON-safe dictionary
    """
    return {
        "entity_id": member.entity_id,
        "name": member.name,
        "x": member.x,
        "y": member.y,
        "sprite_id": member.sprite_id,
        "equipment": member.equipment,
        "base_skills": member.base_skills,
        "skills": member.skills,
        "learned_moves": member.learned_moves,
        "role": member.role,
        "portrait_id": member.portrait_id,
        "formation_position": member.formation_position,
        "stats": serialize_entity_stats(member.stats),
        "memory_value": member.memory_value,
        "memory_stat_type": member.memory_stat_type,
        "skill_tree_progress": serialize_skill_tree_progress(member.skill_tree_progress) if member.skill_tree_progress else None
    }


def serialize_world_runtime_state(world: "World") -> Dict[str, Any]:
    """Serialize world runtime state: triggers, enemies, etc.

    Args:
        world: World object to serialize runtime state from

    Returns:
        JSON-safe dictionary with trigger_states and enemy_states
    """
    # Serialize fired trigger states per map
    trigger_states: Dict[str, Dict[str, bool]] = {}
    for map_id, map_obj in world.maps.items():
        fired_triggers = {}
        for trigger in map_obj.triggers:
            if trigger.fired:
                fired_triggers[trigger.id] = True
        if fired_triggers:
            trigger_states[map_id] = fired_triggers

    # Serialize defeated overworld enemy states per map
    enemy_states: Dict[str, Dict[str, bool]] = {}
    for map_id, enemies in world.map_overworld_enemies.items():
        defeated_enemies = {}
        for enemy in enemies:
            if enemy.defeated:
                defeated_enemies[enemy.entity_id] = True
        if defeated_enemies:
            enemy_states[map_id] = defeated_enemies

    return {
        "trigger_states": trigger_states,
        "enemy_states": enemy_states,
    }


def serialize_crafting_progress(progress: Optional["CraftingProgress"]) -> Optional[Dict[str, Any]]:
    """Serialize crafting progress to a JSON-safe dict.

    Args:
        progress: CraftingProgress object to serialize, or None

    Returns:
        JSON-safe dictionary or None if progress is None
    """
    if not progress:
        return None
    return progress.to_dict()


def serialize_bestiary(bestiary: Optional["Bestiary"]) -> Optional[Dict[str, Any]]:
    """Serialize bestiary to a JSON-safe dict.

    Args:
        bestiary: Bestiary object to serialize, or None

    Returns:
        JSON-safe dictionary or None if bestiary is None
    """
    if not bestiary:
        return None
    return bestiary.serialize()


def serialize_puzzle_manager(puzzle_manager: Optional["PuzzleManager"]) -> Optional[Dict[str, Any]]:
    """Serialize puzzle manager to a JSON-safe dict.

    Args:
        puzzle_manager: PuzzleManager object to serialize, or None

    Returns:
        JSON-safe dictionary or None if puzzle_manager is None
    """
    if not puzzle_manager:
        return None
    return puzzle_manager.serialize()


def serialize_brain_teaser_manager(brain_teaser_manager: Optional["BrainTeaserManager"]) -> Optional[Dict[str, Any]]:
    """Serialize brain teaser manager to a JSON-safe dict.

    Args:
        brain_teaser_manager: BrainTeaserManager object to serialize, or None

    Returns:
        JSON-safe dictionary or None if brain_teaser_manager is None
    """
    if not brain_teaser_manager:
        return None
    return brain_teaser_manager.serialize()


def serialize_gambling_manager(gambling_manager: Optional["GamblingManager"]) -> Optional[Dict[str, Any]]:
    """Serialize gambling manager to a JSON-safe dict.

    Args:
        gambling_manager: GamblingManager object to serialize, or None

    Returns:
        JSON-safe dictionary or None if gambling_manager is None
    """
    if not gambling_manager:
        return None
    return gambling_manager.serialize()


def serialize_arena_manager(arena_manager: Optional["ArenaManager"]) -> Optional[Dict[str, Any]]:
    """Serialize arena manager to a JSON-safe dict.

    Args:
        arena_manager: ArenaManager object to serialize, or None

    Returns:
        JSON-safe dictionary or None if arena_manager is None
    """
    if not arena_manager:
        return None
    return arena_manager.serialize()


def serialize_challenge_dungeon_manager(
    challenge_dungeon_manager: Optional["ChallengeDungeonManager"]
) -> Optional[Dict[str, Any]]:
    """Serialize challenge dungeon manager to a JSON-safe dict.

    Args:
        challenge_dungeon_manager: ChallengeDungeonManager object to serialize, or None

    Returns:
        JSON-safe dictionary or None if challenge_dungeon_manager is None
    """
    if not challenge_dungeon_manager:
        return None
    return challenge_dungeon_manager.serialize()


def serialize_post_game_manager(
    post_game_manager: Optional["PostGameManager"]
) -> Optional[Dict[str, Any]]:
    """Serialize post-game manager to a JSON-safe dict.

    Args:
        post_game_manager: PostGameManager object to serialize, or None

    Returns:
        JSON-safe dictionary or None if post_game_manager is None
    """
    if not post_game_manager:
        return None
    return post_game_manager.serialize()


def serialize_state(
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

    Returns:
        Complete JSON-safe dictionary of game state
    """
    skill_tree_progress = getattr(player, "skill_tree_progress", None)

    # Get playtime from world flags
    play_time = world.get_flag("play_time_seconds")
    if not isinstance(play_time, (int, float)):
        play_time = 0.0

    data: Dict[str, Any] = {
        "meta": {
            "version": SAVE_FILE_VERSION,
            "timestamp": datetime.now().isoformat(),
            "play_time_seconds": play_time,
        },
        "world": {
            "current_map_id": world.current_map_id,
            "flags": world.flags,
            "visited_maps": sorted(world.visited_maps),
            "runtime_state": serialize_world_runtime_state(world),
        },
        "player": {
            "entity_id": getattr(player, "entity_id", "player"),
            "name": getattr(player, "name", "Hero"),
            "x": getattr(player, "x", 0),
            "y": getattr(player, "y", 0),
            "inventory": player.inventory.get_all_items() if getattr(player, "inventory", None) else {},
            "hotbar_slots": player.inventory.hotbar_slots.copy() if getattr(player, "inventory", None) else {},
            "equipment": getattr(player, "equipment", {}),
            "skills": getattr(player, "base_skills", getattr(player, "skills", [])),
            "learned_moves": getattr(player, "learned_moves", []),
            "stats": serialize_entity_stats(getattr(player, "stats", None)),
            "memory_value": getattr(player, "memory_value", 0),
            "memory_stat_type": getattr(player, "memory_stat_type", None),
            "party": [
                serialize_party_member(m)
                for m in (
                    []
                    if not isinstance(getattr(player, "party", []), (list, tuple))
                    else getattr(player, "party", [])
                )
            ],
            "party_formation": getattr(player, "party_formation", {}),
            "formation_position": getattr(player, "formation_position", "front"),
            "skill_tree_progress": serialize_skill_tree_progress(skill_tree_progress) if skill_tree_progress else None,
            "player_class": getattr(player, "player_class", None),
            "player_subclass": getattr(player, "player_subclass", None),
            "crafting_progress": serialize_crafting_progress(getattr(player, "crafting_progress", None)),
            "bestiary": serialize_bestiary(getattr(player, "bestiary", None))
        }
    }

    # Serialize quest state if manager provided
    if quest_manager:
        data["quests"] = quest_manager.serialize_state()

    # Serialize day/night cycle state
    if day_night_cycle:
        data["day_night"] = day_night_cycle.serialize()

    # Serialize achievement state
    if achievement_manager:
        data["achievements"] = achievement_manager.serialize_state()

    # Serialize weather system state
    if weather_system:
        data["weather"] = weather_system.serialize()

    # Serialize fishing system state
    if fishing_system:
        data["fishing"] = fishing_system.serialize()

    # Serialize puzzle system state
    if puzzle_manager:
        data["puzzles"] = serialize_puzzle_manager(puzzle_manager)

    # Serialize brain teaser system state
    if brain_teaser_manager:
        data["brain_teasers"] = serialize_brain_teaser_manager(brain_teaser_manager)

    # Serialize gambling system state
    if gambling_manager:
        data["gambling"] = serialize_gambling_manager(gambling_manager)

    # Serialize arena system state
    if arena_manager:
        data["arena"] = serialize_arena_manager(arena_manager)

    # Serialize challenge dungeon system state
    if challenge_dungeon_manager:
        data["challenge_dungeons"] = serialize_challenge_dungeon_manager(challenge_dungeon_manager)

    # Serialize secret boss manager state
    if secret_boss_manager:
        data["secret_bosses"] = secret_boss_manager.serialize()

    # Serialize hint manager state
    if hint_manager:
        data["hints"] = hint_manager.serialize()

    # Serialize post-game manager state
    if post_game_manager:
        data["post_game"] = serialize_post_game_manager(post_game_manager)

    # Serialize tutorial manager state
    if tutorial_manager:
        data["tutorial"] = tutorial_manager.serialize()

    # Serialize schedule manager state
    if schedule_manager:
        data["npc_schedules"] = schedule_manager.serialize()

    return data


def serialize_state_from_context(context: SaveContext) -> Dict[str, Any]:
    """Serialize game state from a SaveContext.

    This is the new API that uses the SaveContext registry to automatically
    serialize all registered managers without requiring explicit parameters.

    Args:
        context: SaveContext containing world, player, and registered managers

    Returns:
        Complete JSON-safe dictionary of game state
    """
    world = context.world
    player = context.player
    skill_tree_progress = getattr(player, "skill_tree_progress", None)

    # Get playtime from world flags
    play_time = world.get_flag("play_time_seconds")
    if not isinstance(play_time, (int, float)):
        play_time = 0.0

    data: Dict[str, Any] = {
        "meta": {
            "version": SAVE_FILE_VERSION,
            "timestamp": datetime.now().isoformat(),
            "play_time_seconds": play_time,
        },
        "world": {
            "current_map_id": world.current_map_id,
            "flags": world.flags,
            "visited_maps": sorted(world.visited_maps),
            "runtime_state": serialize_world_runtime_state(world),
        },
        "player": {
            "entity_id": getattr(player, "entity_id", "player"),
            "name": getattr(player, "name", "Hero"),
            "x": getattr(player, "x", 0),
            "y": getattr(player, "y", 0),
            "inventory": player.inventory.get_all_items() if getattr(player, "inventory", None) else {},
            "hotbar_slots": player.inventory.hotbar_slots.copy() if getattr(player, "inventory", None) else {},
            "equipment": getattr(player, "equipment", {}),
            "skills": getattr(player, "base_skills", getattr(player, "skills", [])),
            "learned_moves": getattr(player, "learned_moves", []),
            "stats": serialize_entity_stats(getattr(player, "stats", None)),
            "memory_value": getattr(player, "memory_value", 0),
            "memory_stat_type": getattr(player, "memory_stat_type", None),
            "party": [
                serialize_party_member(m)
                for m in (
                    []
                    if not isinstance(getattr(player, "party", []), (list, tuple))
                    else getattr(player, "party", [])
                )
            ],
            "party_formation": getattr(player, "party_formation", {}),
            "formation_position": getattr(player, "formation_position", "front"),
            "skill_tree_progress": serialize_skill_tree_progress(skill_tree_progress) if skill_tree_progress else None,
            "player_class": getattr(player, "player_class", None),
            "player_subclass": getattr(player, "player_subclass", None),
            "crafting_progress": serialize_crafting_progress(getattr(player, "crafting_progress", None)),
            "bestiary": serialize_bestiary(getattr(player, "bestiary", None))
        }
    }

    # Serialize all registered managers automatically
    manager_data = context.serialize_managers()
    data.update(manager_data)

    return data

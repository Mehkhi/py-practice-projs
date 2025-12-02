"""Helper functions for warp side effects and validations."""

from __future__ import annotations

from typing import Any, Callable, List, Optional, TYPE_CHECKING

from core.logging_utils import log_info, log_warning
from core.save.context import SaveContext

from .base import TriggerContext

if TYPE_CHECKING:
    from engine.world_scene import WorldScene


AUTO_SAVE_MANAGER_ATTRS: List[str] = [
    "day_night_cycle",
    "achievement_manager",
    "weather_system",
    "schedule_manager",
    "fishing_system",
    "puzzle_manager",
    "brain_teaser_manager",
    "gambling_manager",
    "arena_manager",
    "challenge_dungeon_manager",
    "secret_boss_manager",
    "hint_manager",
    "post_game_manager",
    "tutorial_manager",
]


def trigger_area_tutorials(scene: "WorldScene", map_id: str) -> None:
    tutorial_manager = scene.get_manager_attr("tutorial_manager", "_trigger_area_tutorials")
    if not tutorial_manager:
        return

    area_type = get_area_type(scene, map_id)
    if not area_type:
        return

    from core.tutorial_system import TipTrigger

    if area_type == "dungeon":
        if not scene.world.get_flag("_tutorial_entered_dungeon", False):
            scene.world.set_flag("_tutorial_entered_dungeon", True)
            tutorial_manager.trigger_tip(TipTrigger.ENTERED_DUNGEON)
    elif area_type == "town":
        if not scene.world.get_flag("_tutorial_entered_town", False):
            scene.world.set_flag("_tutorial_entered_town", True)
            tutorial_manager.trigger_tip(TipTrigger.ENTERED_TOWN)


def get_area_type(scene: "WorldScene", map_id: str) -> Optional[str]:
    map_id_lower = map_id.lower()

    town_keywords = ("town", "city", "village")
    if any(keyword in map_id_lower for keyword in town_keywords):
        return "town"

    challenge_manager = scene.get_manager_attr("challenge_dungeon_manager", "_get_area_type")
    if challenge_manager:
        for dungeon in challenge_manager.dungeons.values():
            if map_id in getattr(dungeon, "map_ids", []):
                return "dungeon"

    dungeon_keywords = (
        "dungeon",
        "cave",
        "cavern",
        "crypt",
        "ruins",
        "maze",
        "gauntlet",
        "spire",
        "abyss",
        "sanctum",
        "fortress",
        "trial",
        "void",
        "realm",
        "lair",
        "throne",
        "crater",
        "pass",
        "grove",
        "chamber",
        "gateway",
    )
    if any(keyword in map_id_lower for keyword in dungeon_keywords):
        return "dungeon"

    return None


def track_exploration_achievement(scene: "WorldScene", map_id: str) -> None:
    if scene.manager and getattr(scene.manager, "event_bus", None):
        scene.manager.event_bus.publish("map_entered", map_id=map_id)

    if scene.quest_manager:
        updated_quests = scene.quest_manager.on_map_entered(map_id)
        if updated_quests:
            for quest_id in updated_quests:
                quest = scene.quest_manager.get_quest(quest_id)
                if quest and quest.is_complete():
                    scene._show_quest_notification(
                        f"Quest Ready: {quest.name}",
                        "Return to the quest giver to claim your reward!",
                    )


def try_auto_save(scene: "WorldScene", manager_attrs: List[str]) -> None:
    if not scene.auto_save_enabled or not scene.auto_save_on_map_change:
        return

    if not scene.save_manager:
        return

    current_map = scene.world.current_map_id
    if current_map == scene._last_auto_save_map:
        return

    scene._last_auto_save_map = current_map

    try:
        context = SaveContext(world=scene.world, player=scene.player)

        quest_manager = getattr(scene, "quest_manager", None)
        if quest_manager:
            context.register_if_saveable(quest_manager)

        if scene.manager:
            for attr_name in manager_attrs:
                manager_obj = scene.manager.get_manager(attr_name, "_try_auto_save")
                if manager_obj is not None:
                    context.register_if_saveable(manager_obj)

        scene.save_manager.save_to_slot_with_context(scene.save_slot, context)
        log_info(f"Auto-saved to slot {scene.save_slot}")
    except Exception as exc:
        log_warning(f"Auto-save failed for slot {scene.save_slot}: {exc}")


def handle_challenge_warp(
    warp: Any,
    context: TriggerContext,
    warp_fn: Callable[[TriggerContext, str, int, int], None],
) -> None:
    challenge_id = getattr(warp, "challenge_dungeon_id", None)
    if not challenge_id:
        return

    scene = context.scene
    challenge_manager = scene.get_manager_attr("challenge_dungeon_manager", "_handle_warp")
    if not challenge_manager:
        log_warning("Challenge dungeon warp activated but no challenge_dungeon_manager available")
        return

    post_game_manager = scene.get_manager_attr("post_game_manager", "_handle_warp")
    if not post_game_manager:
        scene._show_inline_message("Post-game system not available")
        return

    player_level = scene.player.stats.level
    can_enter, reason = challenge_manager.can_enter(challenge_id, player_level, post_game_manager)
    if not can_enter:
        scene._show_inline_message(f"Cannot enter: {reason}")
        return

    _show_challenge_dungeon_prompt(challenge_id, warp, context, warp_fn)


def _show_challenge_dungeon_prompt(
    challenge_id: str,
    warp: Any,
    context: TriggerContext,
    warp_fn: Callable[[TriggerContext, str, int, int], None],
) -> None:
    scene = context.scene
    challenge_manager = scene.get_manager_attr("challenge_dungeon_manager", "_show_challenge_dungeon_prompt")
    if not challenge_manager:
        return

    dungeon = challenge_manager.dungeons.get(challenge_id)
    if not dungeon:
        return

    modifier_names: List[str] = []
    for mod_id in dungeon.modifiers:
        mod = challenge_manager.modifiers.get(mod_id)
        if mod:
            modifier_names.append(mod.name)

    modifier_text = ", ".join(modifier_names) if modifier_names else "None"
    tier_text = dungeon.tier.value.title()
    _ = (
        f"Enter {dungeon.name}?\n"
        f"Tier: {tier_text}\n"
        f"Description: {dungeon.description}\n"
        f"Modifiers: {modifier_text}"
    )

    challenge_manager.enter_dungeon(challenge_id)
    warp_fn(context, warp.target_map_id, warp.target_x, warp.target_y)


__all__ = [
    "AUTO_SAVE_MANAGER_ATTRS",
    "get_area_type",
    "handle_challenge_warp",
    "track_exploration_achievement",
    "trigger_area_tutorials",
    "try_auto_save",
]

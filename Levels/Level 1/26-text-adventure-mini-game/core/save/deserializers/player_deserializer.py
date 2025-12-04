"""Player and party member deserialization."""

from typing import Any, Dict, List, Optional

from ...bestiary import Bestiary
from ...constants import DEFAULT_FORMATION_POSITION, FORMATION_POSITIONS, SUPPORTED_EQUIP_SLOTS
from ...entities import PartyMember, Player
from ...entities.base import MAX_LEARNED_MOVES
from ...items import Inventory
from ...logging_utils import log_warning
from ...skill_tree import SkillTreeManager, SkillTreeProgress
from ...stats import Stats, StatusEffect, create_default_player_stats, MAX_LEVEL
from ...crafting import CraftingProgress
from .base import DeserializationResources, DeserializerContext, DomainDeserializer, safe_log_warning


def deserialize_stats(stats_data: Optional[Dict[str, Any]]) -> Optional[Stats]:
    """Deserialize stats from a dict."""
    if not stats_data:
        return None

    # Clamp level to valid range (1 to MAX_LEVEL)
    raw_level = stats_data.get("level", 1)
    clamped_level = max(1, min(MAX_LEVEL, raw_level))

    stats = Stats(
        max_hp=stats_data["max_hp"],
        hp=stats_data["hp"],
        max_sp=stats_data["max_sp"],
        sp=stats_data["sp"],
        attack=stats_data["attack"],
        defense=stats_data["defense"],
        magic=stats_data["magic"],
        speed=stats_data["speed"],
        luck=stats_data["luck"],
        level=clamped_level,
        exp=stats_data.get("exp", 0),
    )

    for status_id, effect_data in stats_data.get("status_effects", {}).items():
        stats.status_effects[status_id] = StatusEffect(
            id=status_id,
            duration=effect_data["duration"],
            stacks=effect_data["stacks"],
        )
    return stats


def deserialize_skill_tree_progress(data: Optional[Dict[str, Any]]) -> SkillTreeProgress:
    """Deserialize skill tree progress from a dict."""
    if not data:
        return SkillTreeProgress()
    return SkillTreeProgress.deserialize(data)


def deserialize_crafting_progress(data: Optional[Dict[str, Any]]) -> Optional[CraftingProgress]:
    """Deserialize crafting progress from a dict."""
    if not data:
        return None
    return CraftingProgress.from_dict(data)


def deserialize_bestiary(data: Optional[Dict[str, Any]]) -> Bestiary:
    """Deserialize bestiary from a dict."""
    if not data:
        return Bestiary()
    return Bestiary.from_dict(data)


def _build_equipment(equipment_data: Dict[str, Any]) -> Dict[str, Optional[str]]:
    equipment = {slot: None for slot in SUPPORTED_EQUIP_SLOTS}
    for slot, item_id in equipment_data.items():
        if slot in SUPPORTED_EQUIP_SLOTS:
            equipment[slot] = item_id
    return equipment


def _apply_skill_tree_bonuses(member: PartyMember, stats: Optional[Stats], progress: SkillTreeProgress, resources: DeserializationResources) -> None:
    if not stats:
        return
    try:
        trees = resources.resolve_skill_trees()
        tree_manager = SkillTreeManager(trees)
        tree_manager.apply_skill_tree_bonuses(stats, progress)
        skill_tree_skills = progress.get_all_unlocked_skills(trees)
        for skill_id in skill_tree_skills:
            if hasattr(member, "base_skills") and skill_id not in member.base_skills:
                member.base_skills.append(skill_id)
            if hasattr(member, "skills") and skill_id not in member.skills:
                member.skills.append(skill_id)
    except Exception as exc:
        log_warning(f"failed to apply skill tree bonuses for party member {member.name}: {exc}")


def deserialize_party_member(
    member_data: Dict[str, Any],
    items_db: Dict[str, Any],
    resources: Optional[DeserializationResources] = None,
) -> PartyMember:
    """Deserialize a party member from a dict."""
    resources = resources or DeserializationResources()
    stats = deserialize_stats(member_data.get("stats"))
    skill_tree_progress = deserialize_skill_tree_progress(member_data.get("skill_tree_progress"))
    formation_raw = member_data.get("formation_position", "middle")
    formation_position = formation_raw if formation_raw in FORMATION_POSITIONS else DEFAULT_FORMATION_POSITION
    if formation_raw != formation_position:
        safe_log_warning(f"Invalid formation_position '{formation_raw}' for party member, using '{formation_position}'")

    member = PartyMember(
        entity_id=member_data.get("entity_id", ""),
        name=member_data.get("name", ""),
        x=member_data.get("x", 0),
        y=member_data.get("y", 0),
        sprite_id=member_data.get("sprite_id", "party_member"),
        stats=stats,
        equipment=_build_equipment(member_data.get("equipment", {})),
        base_skills=list(member_data.get("base_skills", [])),
        skills=list(member_data.get("skills", [])),
        learned_moves=list(member_data.get("learned_moves", [])),
        role=member_data.get("role", "fighter"),
        portrait_id=member_data.get("portrait_id"),
        formation_position=formation_position,
        skill_tree_progress=skill_tree_progress,
        memory_value=member_data.get("memory_value", 0),
        memory_stat_type=member_data.get("memory_stat_type"),
    )

    try:
        member.recompute_equipment(items_db)
    except Exception as exc:
        safe_log_warning(f"failed to recompute equipment for party member {member.name}: {exc}")

    if skill_tree_progress:
        _apply_skill_tree_bonuses(member, stats, skill_tree_progress, resources)
    return member


def _restore_hotbar(inventory: Inventory, player_data: Dict[str, Any]) -> None:
    hotbar_slots = player_data.get("hotbar_slots", {})
    if not isinstance(hotbar_slots, dict):
        return
    for slot_str, item_id in hotbar_slots.items():
        try:
            slot = int(slot_str) if isinstance(slot_str, str) else slot_str
            if 1 <= slot <= 9 and inventory.has(item_id):
                inventory.set_hotbar_item(slot, item_id)
        except (ValueError, TypeError):
            continue


def _restore_equipment_and_skills(player: Player, player_data: Dict[str, Any]) -> None:
    equipment_data = player_data.get("equipment", {})
    if isinstance(equipment_data, dict) and hasattr(player, "equipment"):
        for slot, item_id in equipment_data.items():
            if slot in SUPPORTED_EQUIP_SLOTS:
                player.equipment[slot] = item_id

    learned_moves = player_data.get("learned_moves", [])
    if isinstance(learned_moves, list):
        player.learned_moves = list(learned_moves)[:MAX_LEARNED_MOVES]

    skills_data = player_data.get("skills", [])
    if isinstance(skills_data, list):
        player.base_skills = list(skills_data)
        player.skills = list(skills_data)


def _apply_player_skill_tree(player: Player, player_data: Dict[str, Any], resources: DeserializationResources) -> None:
    skill_tree_data = player_data.get("skill_tree_progress")
    if not isinstance(skill_tree_data, dict):
        return
    player.skill_tree_progress = deserialize_skill_tree_progress(skill_tree_data)
    if not player.stats:
        return
    try:
        trees = resources.resolve_skill_trees()
        tree_manager = SkillTreeManager(trees)
        tree_manager.apply_skill_tree_bonuses(player.stats, player.skill_tree_progress)
        skill_tree_skills = player.skill_tree_progress.get_all_unlocked_skills(trees)
        for skill_id in skill_tree_skills:
            if hasattr(player, "base_skills") and skill_id not in player.base_skills:
                player.base_skills.append(skill_id)
            if hasattr(player, "skills") and skill_id not in player.skills:
                player.skills.append(skill_id)
    except Exception as exc:
        safe_log_warning(f"failed to apply skill tree bonuses on load: {exc}")


def _restore_progress(player: Player, player_data: Dict[str, Any]) -> None:
    crafting_data = player_data.get("crafting_progress")
    if isinstance(crafting_data, dict):
        player.crafting_progress = deserialize_crafting_progress(crafting_data)

    bestiary_data = player_data.get("bestiary")
    if isinstance(bestiary_data, dict):
        player.bestiary = deserialize_bestiary(bestiary_data)


def _create_player(player_data: Dict[str, Any], stats: Optional[Stats], inventory: Inventory) -> Player:
    player_class = player_data.get("player_class")
    player_subclass = player_data.get("player_subclass")
    sprite_id = f"player_{player_class}_{player_subclass}" if player_class and player_subclass else "player"
    try:
        return Player(
            entity_id=player_data.get("entity_id", "player_1"),
            name=player_data.get("name", "Hero"),
            x=player_data.get("x", 0),
            y=player_data.get("y", 0),
            sprite_id=sprite_id,
            stats=stats,
            inventory=inventory,
            player_class=player_class,
            player_subclass=player_subclass,
            learned_moves=list(player_data.get("learned_moves", [])),
        )
    except Exception as exc:
        safe_log_warning(f"Failed to create player: {exc}. Using defaults.")
        return Player(
            entity_id="player_1",
            name="Hero",
            x=0,
            y=0,
            sprite_id="player",
            stats=create_default_player_stats(),
            inventory=Inventory(),
            learned_moves=list(player_data.get("learned_moves", [])),
        )


def _restore_player_attributes(player: Player, player_data: Dict[str, Any]) -> None:
    player.player_class = player_data.get("player_class")
    player.player_subclass = player_data.get("player_subclass")
    player.memory_value = player_data.get("memory_value", 0)
    player.memory_stat_type = player_data.get("memory_stat_type")
    formation = player_data.get("formation_position", "front")
    if formation in FORMATION_POSITIONS:
        player.formation_position = formation
    else:
        safe_log_warning(f"Invalid player formation position '{formation}', using 'front'")
        player.formation_position = "front"


def _load_inventory(player_data: Dict[str, Any]) -> Inventory:
    inventory = Inventory()
    for item_id, quantity in player_data.get("inventory", {}).items():
        inventory.add(item_id, quantity)
    _restore_hotbar(inventory, player_data)
    return inventory


class PlayerDeserializer(DomainDeserializer):
    """Deserialize the player core (stats, inventory, skills, bestiary)."""

    def deserialize(self, data: Dict[str, Any], context: DeserializerContext, resources: DeserializationResources) -> None:
        player_data = data.get("player", {})
        stats = deserialize_stats(player_data.get("stats"))
        if stats is None:
            stats = create_default_player_stats()

        inventory = _load_inventory(player_data)
        player = _create_player(player_data, stats, inventory)
        _restore_equipment_and_skills(player, player_data)
        _restore_player_attributes(player, player_data)

        items_db: Dict[str, Any] = {}
        try:
            items_db = resources.resolve_items_db()
            player.recompute_equipment(items_db)
        except Exception as exc:
            safe_log_warning(f"failed to recompute equipment on load: {exc}")

        _apply_player_skill_tree(player, player_data, resources)
        _restore_progress(player, player_data)

        context.player = player
        context.items_db = items_db

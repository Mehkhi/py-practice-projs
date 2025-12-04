"""Loader utilities for party members and NPCs."""

import json
import os
from typing import Dict, Optional, TYPE_CHECKING

from core.loaders.base import ensure_dict, ensure_list, validate_required_keys
from ..constants import DEFAULT_FORMATION_POSITION, FORMATION_POSITIONS, SUPPORTED_EQUIP_SLOTS
from ..logging_utils import log_schema_warning, log_warning, log_error
from ..stats import Stats
from .base import EQUIPMENT_LOG_PREFIX
from .npc import NPC
from .player import PartyMember

if TYPE_CHECKING:
    from ..items import Item


def load_party_members_from_json(
    path: str = os.path.join("data", "party_members.json"),
    items_db: Optional[Dict[str, "Item"]] = None,
) -> Dict[str, PartyMember]:
    """Load party member definitions from JSON into PartyMember prototypes keyed by ID."""
    members: Dict[str, PartyMember] = {}
    if not os.path.exists(path):
        return members

    context = "party member loader"
    items_db_cache = items_db

    def _get_items_db() -> Dict[str, "Item"]:
        nonlocal items_db_cache
        if items_db_cache is None:
            try:
                from ..items import load_items_from_json

                items_db_cache = load_items_from_json(os.path.join("data", "items.json"))
            except (OSError, json.JSONDecodeError, ValueError) as exc:
                log_warning(
                    f"{EQUIPMENT_LOG_PREFIX} Party member loader: failed to load items for equipment recompute: {exc}"
                )
                items_db_cache = {}
            except Exception as exc:
                log_error(
                    f"{EQUIPMENT_LOG_PREFIX} Party member loader: unexpected error loading items: {exc}"
                )
                items_db_cache = {}
        return items_db_cache or {}

    try:
        with open(path, "r") as f:
            raw_data = json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        log_warning(f"Failed to load party member data: {exc}")
        return members
    except Exception as exc:
        log_error(f"Unexpected error loading party member data: {exc}")
        return members

    data = ensure_dict(raw_data, context=context, section="root")
    members_data = ensure_dict(data.get("party_members", {}), context=context, section="party_members")

    for member_id, member_data in members_data.items():
        member_entry = ensure_dict(member_data, context=context, section="party_member", identifier=member_id)

        stats: Optional[Stats] = None
        stats_entry = member_entry.get("stats")
        if stats_entry is not None:
            stats_entry = ensure_dict(stats_entry, context=context, section="stats", identifier=member_id)
            if validate_required_keys(
                stats_entry,
                ("max_hp", "hp", "max_sp", "sp", "attack", "defense", "magic", "speed", "luck"),
                context=context,
                section="stats",
                identifier=member_id,
            ):
                stats = Stats(
                    max_hp=stats_entry.get("max_hp", 0),
                    hp=stats_entry.get("hp", 0),
                    max_sp=stats_entry.get("max_sp", 0),
                    sp=stats_entry.get("sp", 0),
                    attack=stats_entry.get("attack", 0),
                    defense=stats_entry.get("defense", 0),
                    magic=stats_entry.get("magic", 0),
                    speed=stats_entry.get("speed", 0),
                    luck=stats_entry.get("luck", 0),
                )

        base_skills = ensure_list(
            member_entry.get("base_skills", []),
            context=context,
            section="base_skills",
            identifier=member_id,
        )
        skills = ensure_list(
            member_entry.get("skills", []),
            context=context,
            section="skills",
            identifier=member_id,
        )
        equipment_data = ensure_dict(
            member_entry.get("equipment", {}),
            context=context,
            section="equipment",
            identifier=member_id,
        )
        equipment = {slot: None for slot in SUPPORTED_EQUIP_SLOTS}
        for slot, item_id in equipment_data.items():
            if slot in SUPPORTED_EQUIP_SLOTS:
                equipment[slot] = item_id
            else:
                log_schema_warning(
                    context,
                    f"unsupported equipment slot '{slot}', ignoring",
                    section="equipment",
                    identifier=member_id,
                )

        # Validate formation position from JSON
        raw_formation = member_entry.get("formation_position", DEFAULT_FORMATION_POSITION)
        formation_position = (
            raw_formation if raw_formation in FORMATION_POSITIONS else DEFAULT_FORMATION_POSITION
        )

        member = PartyMember(
            entity_id=member_entry.get("entity_id", member_id),
            name=member_entry.get("name", member_id),
            x=member_entry.get("x", 0),
            y=member_entry.get("y", 0),
            sprite_id=member_entry.get("sprite_id", "party_member"),
            stats=stats,
            faction="player",
            base_skills=list(base_skills),
            skills=list(skills),
            equipment=equipment,
            role=member_entry.get("role", "fighter"),
            portrait_id=member_entry.get("portrait_id"),
            formation_position=formation_position,
        )

        if equipment_data:
            member_items_db = _get_items_db()
            if member_items_db:
                member.recompute_equipment(member_items_db)
        members[member_id] = member
    return members


def load_npcs_from_json(
    path: str = os.path.join("data", "entities.json"),
    items_db: Optional[Dict[str, "Item"]] = None,
) -> Dict[str, NPC]:
    """Load NPC definitions from JSON into NPC prototypes keyed by ID."""
    npcs: Dict[str, NPC] = {}
    if not os.path.exists(path):
        return npcs

    context = "npc loader"
    items_db_cache = items_db

    def _get_items_db() -> Dict[str, "Item"]:
        nonlocal items_db_cache
        if items_db_cache is None:
            try:
                from ..items import load_items_from_json

                items_db_cache = load_items_from_json(os.path.join("data", "items.json"))
            except (OSError, json.JSONDecodeError, ValueError) as exc:
                log_warning(
                    f"{EQUIPMENT_LOG_PREFIX} NPC loader: failed to load items for equipment recompute: {exc}"
                )
                items_db_cache = {}
            except Exception as exc:
                log_error(
                    f"{EQUIPMENT_LOG_PREFIX} NPC loader: unexpected error loading items: {exc}"
                )
                items_db_cache = {}
        return items_db_cache or {}

    try:
        with open(path, "r") as f:
            raw_data = json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        log_warning(f"Failed to load NPC data: {exc}")
        return npcs
    except Exception as exc:
        log_error(f"Unexpected error loading NPC data: {exc}")
        return npcs

    data = ensure_dict(raw_data, context=context, section="root")
    npcs_data = ensure_dict(data.get("npcs", {}), context=context, section="npcs")

    for npc_id, npc_data in npcs_data.items():
        npc_entry = ensure_dict(npc_data, context=context, section="npc", identifier=npc_id)
        if npc_entry.get("type") not in (None, "npc"):
            continue

        stats: Optional[Stats] = None
        stats_entry = npc_entry.get("stats")
        if stats_entry is not None:
            stats_entry = ensure_dict(stats_entry, context=context, section="stats", identifier=npc_id)
            if validate_required_keys(
                stats_entry,
                ("max_hp", "hp", "max_sp", "sp", "attack", "defense", "magic", "speed", "luck"),
                context=context,
                section="stats",
                identifier=npc_id,
            ):
                stats = Stats(
                    max_hp=stats_entry.get("max_hp", 0),
                    hp=stats_entry.get("hp", 0),
                    max_sp=stats_entry.get("max_sp", 0),
                    sp=stats_entry.get("sp", 0),
                    attack=stats_entry.get("attack", 0),
                    defense=stats_entry.get("defense", 0),
                    magic=stats_entry.get("magic", 0),
                    speed=stats_entry.get("speed", 0),
                    luck=stats_entry.get("luck", 0),
                )

        base_skills = ensure_list(
            npc_entry.get("base_skills", []),
            context=context,
            section="base_skills",
            identifier=npc_id,
        )
        skills = ensure_list(
            npc_entry.get("skills", []),
            context=context,
            section="skills",
            identifier=npc_id,
        )
        equipment_data = ensure_dict(
            npc_entry.get("equipment", {}),
            context=context,
            section="equipment",
            identifier=npc_id,
        )
        equipment = {slot: None for slot in SUPPORTED_EQUIP_SLOTS}
        for slot, item_id in equipment_data.items():
            if slot in SUPPORTED_EQUIP_SLOTS:
                equipment[slot] = item_id
            else:
                log_schema_warning(
                    context,
                    f"unsupported equipment slot '{slot}', ignoring",
                    section="equipment",
                    identifier=npc_id,
                )

        npc = NPC(
            entity_id=npc_id,
            name=npc_entry.get("name", npc_id),
            x=npc_entry.get("x", 0),
            y=npc_entry.get("y", 0),
            sprite_id=npc_entry.get("sprite_id", "npc_default"),
            dialogue_id=npc_entry.get("dialogue_id"),
            stats=stats,
            faction=npc_entry.get("faction", "npc"),
            role=npc_entry.get("role"),
            base_skills=list(base_skills),
            skills=list(skills),
            equipment=equipment,
            default_map_id=npc_entry.get("default_map_id"),
            shop_inventory=npc_entry.get("shop_inventory", {}),
            shop_id=npc_entry.get("shop_id"),
        )

        if equipment_data:
            npc_items_db = _get_items_db()
            if npc_items_db:
                npc.recompute_equipment(npc_items_db)
        npcs[npc_id] = npc
    return npcs

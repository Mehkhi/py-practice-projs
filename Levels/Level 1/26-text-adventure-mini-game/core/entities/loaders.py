"""Loader utilities for party members and NPCs."""

import json
import os
from typing import Dict, Optional, TYPE_CHECKING

from ..constants import DEFAULT_FORMATION_POSITION, FORMATION_POSITIONS, SUPPORTED_EQUIP_SLOTS
from ..logging_utils import log_warning
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

    items_db_cache = items_db

    def _get_items_db() -> Dict[str, "Item"]:
        nonlocal items_db_cache
        if items_db_cache is None:
            try:
                from ..items import load_items_from_json

                items_db_cache = load_items_from_json(os.path.join("data", "items.json"))
            except Exception as exc:
                log_warning(
                    f"{EQUIPMENT_LOG_PREFIX} Party member loader: failed to load items for equipment recompute: {exc}"
                )
                items_db_cache = {}
        return items_db_cache or {}

    try:
        with open(path, "r") as f:
            data = json.load(f)
    except Exception as exc:
        log_warning(f"Failed to load party member data: {exc}")
        return members

    for member_id, member_data in data.get("party_members", {}).items():
        stats_data = member_data.get("stats")
        stats: Optional[Stats] = None
        if stats_data:
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
            )

        base_skills = member_data.get("base_skills", [])
        skills = member_data.get("skills", [])
        equipment_data = member_data.get("equipment") or {}
        equipment = {slot: None for slot in SUPPORTED_EQUIP_SLOTS}
        for slot, item_id in equipment_data.items():
            if slot in SUPPORTED_EQUIP_SLOTS:
                equipment[slot] = item_id

        # Validate formation position from JSON
        raw_formation = member_data.get("formation_position", DEFAULT_FORMATION_POSITION)
        formation_position = (
            raw_formation if raw_formation in FORMATION_POSITIONS else DEFAULT_FORMATION_POSITION
        )

        member = PartyMember(
            entity_id=member_data.get("entity_id", member_id),
            name=member_data.get("name", member_id),
            x=member_data.get("x", 0),
            y=member_data.get("y", 0),
            sprite_id=member_data.get("sprite_id", "party_member"),
            stats=stats,
            faction="player",
            base_skills=list(base_skills),
            skills=list(skills),
            equipment=equipment,
            role=member_data.get("role", "fighter"),
            portrait_id=member_data.get("portrait_id"),
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

    items_db_cache = items_db

    def _get_items_db() -> Dict[str, "Item"]:
        nonlocal items_db_cache
        if items_db_cache is None:
            try:
                from ..items import load_items_from_json

                items_db_cache = load_items_from_json(os.path.join("data", "items.json"))
            except Exception as exc:
                log_warning(
                    f"{EQUIPMENT_LOG_PREFIX} NPC loader: failed to load items for equipment recompute: {exc}"
                )
                items_db_cache = {}
        return items_db_cache or {}

    try:
        with open(path, "r") as f:
            data = json.load(f)
    except Exception as exc:
        log_warning(f"Failed to load NPC data: {exc}")
        return npcs

    for npc_id, npc_data in data.get("npcs", {}).items():
        if npc_data.get("type") not in (None, "npc"):
            continue
        stats_data = npc_data.get("stats")
        stats: Optional[Stats] = None
        if stats_data:
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
            )

        base_skills = npc_data.get("base_skills", [])
        skills = npc_data.get("skills", [])
        equipment_data = npc_data.get("equipment") or {}
        equipment = {slot: None for slot in SUPPORTED_EQUIP_SLOTS}
        for slot, item_id in equipment_data.items():
            if slot in SUPPORTED_EQUIP_SLOTS:
                equipment[slot] = item_id

        npc = NPC(
            entity_id=npc_id,
            name=npc_data.get("name", npc_id),
            x=npc_data.get("x", 0),
            y=npc_data.get("y", 0),
            sprite_id=npc_data.get("sprite_id", "npc_default"),
            dialogue_id=npc_data.get("dialogue_id"),
            stats=stats,
            faction=npc_data.get("faction", "npc"),
            role=npc_data.get("role"),
            base_skills=list(base_skills),
            skills=list(skills),
            equipment=equipment,
            default_map_id=npc_data.get("default_map_id"),
            shop_inventory=npc_data.get("shop_inventory", {}),
            shop_id=npc_data.get("shop_id"),
        )

        if equipment_data:
            npc_items_db = _get_items_db()
            if npc_items_db:
                npc.recompute_equipment(npc_items_db)
        npcs[npc_id] = npc
    return npcs

"""Entity package public API.

This module re-exports the main entity types and loader helpers so that
existing imports like `from core.entities import Player` continue to work.
"""

from ..constants import DEFAULT_FORMATION_POSITION, SUPPORTED_EQUIP_SLOTS
from ..logging_utils import log_warning
from .base import CombatantMixin, Entity, EQUIPMENT_LOG_PREFIX
from .enemy import Enemy
from .npc import NPC
from .overworld_enemy import OverworldEnemy
from .player import PartyMember, Player
from .loaders import load_npcs_from_json, load_party_members_from_json

__all__ = [
    "CombatantMixin",
    "Entity",
    "Player",
    "PartyMember",
    "Enemy",
    "OverworldEnemy",
    "NPC",
    "EQUIPMENT_LOG_PREFIX",
    "SUPPORTED_EQUIP_SLOTS",
    "DEFAULT_FORMATION_POSITION",
    "log_warning",
    "load_party_members_from_json",
    "load_npcs_from_json",
]

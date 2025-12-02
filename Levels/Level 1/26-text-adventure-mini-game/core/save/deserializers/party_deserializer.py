"""Party deserialization."""

from typing import Any, Dict, List

from ...constants import DEFAULT_FORMATION_POSITION, FORMATION_POSITIONS
from .base import DeserializationResources, DeserializerContext, DomainDeserializer, safe_log_warning
from .player_deserializer import deserialize_party_member


def _restore_party_members(player_data: Dict[str, Any], context: DeserializerContext, resources: DeserializationResources) -> None:
    party_data: List[Dict[str, Any]] = player_data.get("party", [])
    if not hasattr(context.player, "party"):
        return
    items_db = context.items_db or resources.resolve_items_db()
    for member_data in party_data:
        member = deserialize_party_member(member_data, items_db, resources)
        context.player.party.append(member)


def _restore_party_formation(player_data: Dict[str, Any], context: DeserializerContext) -> None:
    formation = player_data.get("party_formation", {})
    if not isinstance(formation, dict) or not hasattr(context.player, "party_formation"):
        return
    for member_id, position in formation.items():
        if position in FORMATION_POSITIONS:
            context.player.party_formation[member_id] = position
        else:
            safe_log_warning(f"Invalid formation position '{position}' for member '{member_id}', using default")
            context.player.party_formation[member_id] = DEFAULT_FORMATION_POSITION


def _restore_player_position(player_data: Dict[str, Any], context: DeserializerContext) -> None:
    player_formation = player_data.get("formation_position", "front")
    if not hasattr(context.player, "formation_position"):
        return
    if player_formation in FORMATION_POSITIONS:
        context.player.formation_position = player_formation
    else:
        safe_log_warning(f"Invalid player formation position '{player_formation}', using 'front'")
        context.player.formation_position = "front"


class PartyDeserializer(DomainDeserializer):
    """Deserialize party members and formation."""

    def deserialize(self, data: Dict[str, Any], context: DeserializerContext, resources: DeserializationResources) -> None:
        if context.player is None:
            return
        player_data = data.get("player", {})
        _restore_party_members(player_data, context, resources)
        _restore_party_formation(player_data, context)
        _restore_player_position(player_data, context)

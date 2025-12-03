"""Challenge dungeon data loader."""

from typing import Dict, Tuple

from core.constants import CHALLENGE_DUNGEONS_JSON
from core.loaders.base import (
    ensure_dict,
    ensure_list,
    load_json_file,
    validate_required_keys,
)
from core.logging_utils import log_schema_warning


def load_challenge_dungeons(
    filepath: str = CHALLENGE_DUNGEONS_JSON,
) -> Tuple[Dict[str, "ChallengeDungeon"], Dict[str, "ChallengeModifier"]]:
    """Load challenge dungeons and modifiers from JSON file.

    Args:
        filepath: Path to the challenge dungeons JSON file

    Returns:
        Tuple of (dungeons_dict, modifiers_dict), or empty dicts if file missing
    """
    from core.challenge_dungeons import (
        ChallengeDungeon,
        ChallengeModifier,
        ChallengeTier,
    )

    context = "challenge dungeons loader"
    data = load_json_file(
        filepath,
        default={"modifiers": {}, "dungeons": {}},
        context="Loading challenge dungeons",
        warn_on_missing=True,
    )

    modifiers: Dict[str, ChallengeModifier] = {}
    data = ensure_dict(data, context=context, section="root")
    modifiers_data = ensure_dict(
        data.get("modifiers", {}),
        context=context,
        section="modifiers",
    )

    for modifier_id, modifier_data in modifiers_data.items():
        modifier_data = ensure_dict(
            modifier_data,
            context=context,
            section="modifier",
            identifier=modifier_id,
        )
        if not validate_required_keys(
            modifier_data,
            ("modifier_id", "name", "description", "effect_type", "effect_data"),
            context=context,
            section="modifier",
            identifier=modifier_id,
        ):
            continue

        effect_data = ensure_dict(
            modifier_data.get("effect_data", {}),
            context=context,
            section="modifier.effect_data",
            identifier=modifier_id,
        )
        modifier = ChallengeModifier(
            modifier_id=modifier_data["modifier_id"],
            name=modifier_data["name"],
            description=modifier_data["description"],
            effect_type=modifier_data["effect_type"],
            effect_data=effect_data,
        )
        modifiers[modifier_id] = modifier

    dungeons: Dict[str, ChallengeDungeon] = {}
    dungeons_data = ensure_dict(
        data.get("dungeons", {}),
        context=context,
        section="dungeons",
    )

    for dungeon_id, dungeon_data in dungeons_data.items():
        dungeon_data = ensure_dict(
            dungeon_data,
            context=context,
            section="dungeon",
            identifier=dungeon_id,
        )
        if not validate_required_keys(
            dungeon_data,
            (
                "dungeon_id",
                "name",
                "description",
                "tier",
                "required_level",
                "map_ids",
                "entry_map_id",
                "entry_x",
                "entry_y",
                "modifiers",
                "rewards",
                "first_clear_rewards",
            ),
            context=context,
            section="dungeon",
            identifier=dungeon_id,
        ):
            continue

        try:
            tier = ChallengeTier(dungeon_data["tier"])
        except ValueError:
            log_schema_warning(
                context,
                f"invalid tier '{dungeon_data['tier']}', skipping dungeon",
                section="dungeon",
                identifier=dungeon_id,
            )
            continue

        modifiers_list = ensure_list(
            dungeon_data.get("modifiers", []),
            context=context,
            section="dungeon.modifiers",
            identifier=dungeon_id,
        )

        map_ids = ensure_list(
            dungeon_data.get("map_ids", []),
            context=context,
            section="dungeon.map_ids",
            identifier=dungeon_id,
        )

        dungeon = ChallengeDungeon(
            dungeon_id=dungeon_data["dungeon_id"],
            name=dungeon_data["name"],
            description=dungeon_data["description"],
            tier=tier,
            required_level=dungeon_data["required_level"],
            map_ids=map_ids,
            entry_map_id=dungeon_data["entry_map_id"],
            entry_x=dungeon_data["entry_x"],
            entry_y=dungeon_data["entry_y"],
            modifiers=modifiers_list,
            rewards=ensure_dict(
                dungeon_data.get("rewards", {}),
                context=context,
                section="dungeon.rewards",
                identifier=dungeon_id,
            ),
            first_clear_rewards=ensure_dict(
                dungeon_data.get("first_clear_rewards", {}),
                context=context,
                section="dungeon.first_clear_rewards",
                identifier=dungeon_id,
            ),
            time_limit=dungeon_data.get("time_limit"),
            no_save=dungeon_data.get("no_save", False),
            no_items=dungeon_data.get("no_items", False),
        )
        dungeons[dungeon_id] = dungeon

    return dungeons, modifiers

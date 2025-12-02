"""Challenge dungeon data loader."""

from typing import Dict, Tuple

from core.loaders.base import load_json_file
from core.logging_utils import log_warning


def load_challenge_dungeons(
    filepath: str = "data/challenge_dungeons.json",
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

    data = load_json_file(
        filepath,
        default={"modifiers": {}, "dungeons": {}},
        context="Loading challenge dungeons",
        warn_on_missing=True,
    )

    modifiers: Dict[str, ChallengeModifier] = {}
    modifiers_data = data.get("modifiers", {})

    for modifier_id, modifier_data in modifiers_data.items():
        # Validate required fields
        if "modifier_id" not in modifier_data:
            log_warning("Challenge modifier missing 'modifier_id', skipping")
            continue
        if "name" not in modifier_data:
            log_warning(
                f"Challenge modifier '{modifier_id}' missing 'name', skipping"
            )
            continue
        if "description" not in modifier_data:
            log_warning(
                f"Challenge modifier '{modifier_id}' missing 'description', skipping"
            )
            continue
        if "effect_type" not in modifier_data:
            log_warning(
                f"Challenge modifier '{modifier_id}' missing 'effect_type', skipping"
            )
            continue
        if "effect_data" not in modifier_data:
            log_warning(
                f"Challenge modifier '{modifier_id}' missing 'effect_data', skipping"
            )
            continue

        modifier = ChallengeModifier(
            modifier_id=modifier_data["modifier_id"],
            name=modifier_data["name"],
            description=modifier_data["description"],
            effect_type=modifier_data["effect_type"],
            effect_data=modifier_data.get("effect_data", {}),
        )
        modifiers[modifier_id] = modifier

    dungeons: Dict[str, ChallengeDungeon] = {}
    dungeons_data = data.get("dungeons", {})

    for dungeon_id, dungeon_data in dungeons_data.items():
        # Validate required fields
        if "dungeon_id" not in dungeon_data:
            log_warning("Challenge dungeon missing 'dungeon_id', skipping")
            continue
        if "name" not in dungeon_data:
            log_warning(
                f"Challenge dungeon '{dungeon_id}' missing 'name', skipping"
            )
            continue
        if "description" not in dungeon_data:
            log_warning(
                f"Challenge dungeon '{dungeon_id}' missing 'description', skipping"
            )
            continue
        if "tier" not in dungeon_data:
            log_warning(
                f"Challenge dungeon '{dungeon_id}' missing 'tier', skipping"
            )
            continue
        if "required_level" not in dungeon_data:
            log_warning(
                f"Challenge dungeon '{dungeon_id}' missing 'required_level', skipping"
            )
            continue
        if "map_ids" not in dungeon_data:
            log_warning(
                f"Challenge dungeon '{dungeon_id}' missing 'map_ids', skipping"
            )
            continue
        if "entry_map_id" not in dungeon_data:
            log_warning(
                f"Challenge dungeon '{dungeon_id}' missing 'entry_map_id', skipping"
            )
            continue
        if "entry_x" not in dungeon_data:
            log_warning(
                f"Challenge dungeon '{dungeon_id}' missing 'entry_x', skipping"
            )
            continue
        if "entry_y" not in dungeon_data:
            log_warning(
                f"Challenge dungeon '{dungeon_id}' missing 'entry_y', skipping"
            )
            continue
        if "modifiers" not in dungeon_data:
            log_warning(
                f"Challenge dungeon '{dungeon_id}' missing 'modifiers', skipping"
            )
            continue
        if "rewards" not in dungeon_data:
            log_warning(
                f"Challenge dungeon '{dungeon_id}' missing 'rewards', skipping"
            )
            continue
        if "first_clear_rewards" not in dungeon_data:
            log_warning(
                f"Challenge dungeon '{dungeon_id}' missing 'first_clear_rewards', skipping"
            )
            continue

        # Convert tier string to enum
        try:
            tier = ChallengeTier(dungeon_data["tier"])
        except ValueError:
            log_warning(
                f"Challenge dungeon '{dungeon_id}': invalid tier '{dungeon_data['tier']}', skipping"
            )
            continue

        dungeon = ChallengeDungeon(
            dungeon_id=dungeon_data["dungeon_id"],
            name=dungeon_data["name"],
            description=dungeon_data["description"],
            tier=tier,
            required_level=dungeon_data["required_level"],
            map_ids=dungeon_data.get("map_ids", []),
            entry_map_id=dungeon_data["entry_map_id"],
            entry_x=dungeon_data["entry_x"],
            entry_y=dungeon_data["entry_y"],
            modifiers=dungeon_data.get("modifiers", []),
            rewards=dungeon_data.get("rewards", {}),
            first_clear_rewards=dungeon_data.get("first_clear_rewards", {}),
            time_limit=dungeon_data.get("time_limit"),
            no_save=dungeon_data.get("no_save", False),
            no_items=dungeon_data.get("no_items", False),
        )
        dungeons[dungeon_id] = dungeon

    return dungeons, modifiers

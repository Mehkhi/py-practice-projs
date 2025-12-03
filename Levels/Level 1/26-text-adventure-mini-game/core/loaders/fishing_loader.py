"""Fishing data loader."""

from typing import Dict, List, Tuple

from core.constants import FISHING_JSON
from core.loaders.base import (
    ensure_dict,
    ensure_list,
    load_json_file,
    validate_required_keys,
)
from core.logging_utils import log_schema_warning


def load_fishing_data(
    filepath: str = FISHING_JSON,
) -> Tuple[Dict[str, "Fish"], Dict[str, "FishingSpot"]]:
    """Load fish and fishing spot definitions from JSON.

    Args:
        filepath: Path to the fishing data JSON file

    Returns:
        Tuple of (fish_dict, spots_dict), or empty dicts if file missing
    """
    from core.fishing import Fish, FishingSpot, FishRarity, WaterType

    context = "fishing loader"
    data = load_json_file(
        filepath,
        default={"fish": [], "spots": []},
        context="Loading fishing data",
        warn_on_missing=True,
    )

    data = ensure_dict(data, context=context, section="root")

    fish_db: Dict[str, Fish] = {}
    spots: Dict[str, FishingSpot] = {}

    fish_entries = ensure_list(
        data.get("fish", []),
        context=context,
        section="fish",
    )

    # Load fish
    for fish_data in fish_entries:
        candidate_id = fish_data.get("fish_id") if isinstance(fish_data, dict) else None
        fish_entry = ensure_dict(
            fish_data,
            context=context,
            section="fish",
            identifier=candidate_id,
        )
        fish_id = fish_entry.get("fish_id", candidate_id or "unknown")
        if not validate_required_keys(
            fish_entry,
            ("fish_id", "name", "rarity", "water_types"),
            context=context,
            section="fish",
            identifier=fish_id,
        ):
            continue

        # Convert rarity string to enum
        try:
            rarity = FishRarity(fish_entry["rarity"])
        except ValueError:
            log_schema_warning(
                context,
                f"invalid rarity '{fish_entry['rarity']}', skipping fish",
                section="fish",
                identifier=fish_id,
            )
            continue

        # Convert water type strings to enums
        water_types: List[WaterType] = []
        water_type_values = ensure_list(
            fish_entry.get("water_types", []),
            context=context,
            section="fish.water_types",
            identifier=fish_id,
        )
        for water_str in water_type_values:
            try:
                water_type = WaterType(water_str)
                water_types.append(water_type)
            except ValueError:
                log_schema_warning(
                    context,
                    f"invalid water type '{water_str}', skipping value",
                    section="fish.water_types",
                    identifier=fish_id,
                )

        if not water_types:
            log_schema_warning(
                context,
                "has no valid water types, skipping fish",
                section="fish",
                identifier=fish_id,
            )
            continue

        # Time periods are stored as strings (TimeOfDay enum names)
        time_periods = ensure_list(
            fish_entry.get("time_periods", []),
            context=context,
            section="fish.time_periods",
            identifier=fish_id,
        )

        fish = Fish(
            fish_id=fish_entry["fish_id"],
            name=fish_entry["name"],
            rarity=rarity,
            base_value=fish_entry.get("base_value", 0),
            water_types=water_types,
            time_periods=time_periods,
            min_size=fish_entry.get("min_size", 0.5),
            max_size=fish_entry.get("max_size", 1.0),
            catch_difficulty=fish_entry.get("catch_difficulty", 5),
            description=fish_entry.get("description", ""),
            item_id=fish_entry.get("item_id", ""),
        )
        fish_db[fish.fish_id] = fish

    spots_entries = ensure_list(
        data.get("spots", []),
        context=context,
        section="spots",
    )

    # Load fishing spots
    for spot_data in spots_entries:
        candidate_id = spot_data.get("spot_id") if isinstance(spot_data, dict) else None
        spot_entry = ensure_dict(
            spot_data,
            context=context,
            section="spots",
            identifier=candidate_id,
        )
        spot_id = spot_entry.get("spot_id", candidate_id or "unknown")
        if not validate_required_keys(
            spot_entry,
            ("spot_id", "name", "map_id", "x", "y", "water_type"),
            context=context,
            section="spots",
            identifier=spot_id,
        ):
            continue

        # Convert water type string to enum
        try:
            water_type = WaterType(spot_entry["water_type"])
        except ValueError:
            log_schema_warning(
                context,
                f"invalid water_type '{spot_entry['water_type']}', skipping spot",
                section="spots",
                identifier=spot_id,
            )
            continue

        spot = FishingSpot(
            spot_id=spot_entry["spot_id"],
            name=spot_entry["name"],
            map_id=spot_entry["map_id"],
            x=spot_entry["x"],
            y=spot_entry["y"],
            water_type=water_type,
            is_premium=spot_entry.get("is_premium", False),
            fish_pool=ensure_list(
                spot_entry.get("fish_pool", []),
                context=context,
                section="spots.fish_pool",
                identifier=spot_id,
            ),
            rarity_modifiers=ensure_dict(
                spot_entry.get("rarity_modifiers", {}),
                context=context,
                section="spots.rarity_modifiers",
                identifier=spot_id,
            ),
        )
        spots[spot.spot_id] = spot

    return fish_db, spots

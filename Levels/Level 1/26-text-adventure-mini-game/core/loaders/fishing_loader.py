"""Fishing data loader."""

from typing import Any, Dict, List, Tuple

from core.loaders.base import load_json_file
from core.logging_utils import log_warning


def load_fishing_data(
    filepath: str = "data/fishing.json",
) -> Tuple[Dict[str, "Fish"], Dict[str, "FishingSpot"]]:
    """Load fish and fishing spot definitions from JSON.

    Args:
        filepath: Path to the fishing data JSON file

    Returns:
        Tuple of (fish_dict, spots_dict), or empty dicts if file missing
    """
    from core.fishing import Fish, FishingSpot, FishRarity, WaterType

    data = load_json_file(
        filepath,
        default={"fish": [], "spots": []},
        context="Loading fishing data",
        warn_on_missing=True,
    )

    if not isinstance(data, dict):
        raise ValueError("Fishing data must be a dictionary at the top level")

    fish_db: Dict[str, Fish] = {}
    spots: Dict[str, FishingSpot] = {}

    fish_entries = data.get("fish", [])
    if not isinstance(fish_entries, list):
        raise ValueError("Fishing data 'fish' section must be a list")

    # Load fish
    for fish_data in fish_entries:
        if not isinstance(fish_data, dict):
            raise ValueError("Each fish entry must be a dictionary")
        # Validate required fields
        if "fish_id" not in fish_data:
            log_warning("Fish missing 'fish_id', skipping")
            continue
        if "name" not in fish_data:
            log_warning(
                f"Fish '{fish_data.get('fish_id', 'unknown')}' missing 'name', skipping"
            )
            continue
        if "rarity" not in fish_data:
            log_warning(
                f"Fish '{fish_data.get('fish_id', 'unknown')}' missing 'rarity', skipping"
            )
            continue
        if "water_types" not in fish_data:
            log_warning(
                f"Fish '{fish_data.get('fish_id', 'unknown')}' missing 'water_types', skipping"
            )
            continue

        # Convert rarity string to enum
        try:
            rarity = FishRarity(fish_data["rarity"])
        except ValueError:
            log_warning(
                f"Fish '{fish_data['fish_id']}': invalid rarity '{fish_data['rarity']}', skipping"
            )
            continue

        # Convert water type strings to enums
        water_types: List[WaterType] = []
        for water_str in fish_data.get("water_types", []):
            try:
                water_type = WaterType(water_str)
                water_types.append(water_type)
            except ValueError:
                log_warning(
                    f"Fish '{fish_data['fish_id']}': invalid water type '{water_str}', skipping"
                )

        if not water_types:
            log_warning(
                f"Fish '{fish_data['fish_id']}' has no valid water types, skipping"
            )
            continue

        # Time periods are stored as strings (TimeOfDay enum names)
        time_periods = fish_data.get("time_periods", [])

        fish = Fish(
            fish_id=fish_data["fish_id"],
            name=fish_data["name"],
            rarity=rarity,
            base_value=fish_data.get("base_value", 0),
            water_types=water_types,
            time_periods=time_periods,
            min_size=fish_data.get("min_size", 0.5),
            max_size=fish_data.get("max_size", 1.0),
            catch_difficulty=fish_data.get("catch_difficulty", 5),
            description=fish_data.get("description", ""),
            item_id=fish_data.get("item_id", ""),
        )
        fish_db[fish.fish_id] = fish

    spots_entries = data.get("spots", [])
    if not isinstance(spots_entries, list):
        raise ValueError("Fishing data 'spots' section must be a list")

    # Load fishing spots
    for spot_data in spots_entries:
        if not isinstance(spot_data, dict):
            raise ValueError("Each fishing spot entry must be a dictionary")
        # Validate required fields
        if "spot_id" not in spot_data:
            log_warning("Fishing spot missing 'spot_id', skipping")
            continue
        if "name" not in spot_data:
            log_warning(
                f"Fishing spot '{spot_data.get('spot_id', 'unknown')}' missing 'name', skipping"
            )
            continue
        if "map_id" not in spot_data:
            log_warning(
                f"Fishing spot '{spot_data.get('spot_id', 'unknown')}' missing 'map_id', skipping"
            )
            continue
        if "x" not in spot_data:
            log_warning(
                f"Fishing spot '{spot_data.get('spot_id', 'unknown')}' missing 'x', skipping"
            )
            continue
        if "y" not in spot_data:
            log_warning(
                f"Fishing spot '{spot_data.get('spot_id', 'unknown')}' missing 'y', skipping"
            )
            continue
        if "water_type" not in spot_data:
            log_warning(
                f"Fishing spot '{spot_data.get('spot_id', 'unknown')}' missing 'water_type', skipping"
            )
            continue

        # Convert water type string to enum
        try:
            water_type = WaterType(spot_data["water_type"])
        except ValueError:
            log_warning(
                f"Fishing spot '{spot_data['spot_id']}': invalid water_type '{spot_data['water_type']}', skipping"
            )
            continue

        spot = FishingSpot(
            spot_id=spot_data["spot_id"],
            name=spot_data["name"],
            map_id=spot_data["map_id"],
            x=spot_data["x"],
            y=spot_data["y"],
            water_type=water_type,
            is_premium=spot_data.get("is_premium", False),
            fish_pool=spot_data.get("fish_pool", []),
            rarity_modifiers=spot_data.get("rarity_modifiers", {}),
        )
        spots[spot.spot_id] = spot

    return fish_db, spots

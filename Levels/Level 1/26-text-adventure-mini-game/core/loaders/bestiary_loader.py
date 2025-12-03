"""Bestiary metadata helpers."""

from typing import Any, Dict, Set


def normalize_enemy_type(name: str) -> str:
    """Normalize enemy identifiers for consistent metadata keys."""
    return name.lower().replace(" ", "_")


def build_bestiary_metadata(
    encounters_data: Dict[str, Any],
) -> Dict[str, Dict[str, Any]]:
    """
    Aggregate weakness/drop/lore metadata for each enemy type from encounter data.

    Args:
        encounters_data: Raw encounters dictionary (encounter_id -> encounter def)

    Returns:
        Dict keyed by enemy_type containing normalized metadata lists.
    """
    metadata: Dict[str, Dict[str, Any]] = {}

    for encounter in encounters_data.values():
        if not isinstance(encounter, dict):
            continue

        rewards = encounter.get("rewards", {})
        reward_items: Set[str] = set()
        if isinstance(rewards, dict):
            reward_items = set(rewards.get("items", {}).keys())

        backdrop = encounter.get("backdrop_id", "")

        enemies = encounter.get("enemies", [])
        if not isinstance(enemies, list):
            continue

        for enemy in enemies:
            if not isinstance(enemy, dict):
                continue

            enemy_type = enemy.get("type") or enemy.get("name")
            if not enemy_type:
                continue
            enemy_type = normalize_enemy_type(enemy_type)

            meta = metadata.setdefault(
                enemy_type,
                {
                    "names": set(),
                    "weaknesses": set(),
                    "resistances": set(),
                    "immunities": set(),
                    "absorbs": set(),
                    "drops": set(),
                    "locations": set(),
                    "sprite_id": enemy.get("sprite_id", "enemy"),
                    "category": enemy.get("category", "monster"),
                    "description": "",
                    "_has_authored_description": False,
                },
            )

            meta["names"].add(
                enemy.get("name", enemy_type.replace("_", " ").title())
            )
            if backdrop:
                meta["locations"].add(backdrop)

            for key in ("weaknesses", "resistances", "immunities", "absorbs"):
                for element in enemy.get(key, []) or []:
                    meta[key].add(element)

            for drop_id in enemy.get("items", {}).keys():
                meta["drops"].add(drop_id)
            meta["drops"].update(reward_items)

            # Preserve highest quality sprite/category if available
            if enemy.get("sprite_id"):
                meta["sprite_id"] = enemy["sprite_id"]
            if enemy.get("category"):
                meta["category"] = enemy["category"]

            authored_description = enemy.get("description") or encounter.get("description")
            if authored_description:
                meta["description"] = authored_description
                meta["_has_authored_description"] = True
            elif not meta["_has_authored_description"] and not meta["description"]:
                difficulty = enemy.get("difficulty")
                difficulty_text = (
                    difficulty.replace("_", " ").title()
                    if isinstance(difficulty, str)
                    else "Unknown"
                )
                location_text = (
                    backdrop.replace("_", " ").title()
                    if backdrop
                    else "unknown regions"
                )
                meta["description"] = (
                    f"A {difficulty_text} threat encountered near {location_text}. "
                    "Field notes recommend exploiting elemental weaknesses when possible."
                )

    normalized: Dict[str, Dict[str, Any]] = {}
    for enemy_type, meta in metadata.items():
        normalized[enemy_type] = {
            "names": sorted(meta["names"]),
            "weaknesses": sorted(meta["weaknesses"]),
            "resistances": sorted(meta["resistances"]),
            "immunities": sorted(meta["immunities"]),
            "absorbs": sorted(meta["absorbs"]),
            "drops": sorted(meta["drops"]),
            "locations": sorted(meta["locations"]),
            "sprite_id": meta["sprite_id"],
            "category": meta["category"],
            "description": meta["description"],
        }
    return normalized

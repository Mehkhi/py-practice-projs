"""Secret boss and hint loaders."""

from typing import Dict, List, Tuple, TYPE_CHECKING

from core.loaders.base import load_json_file
from core.logging_utils import log_warning

if TYPE_CHECKING:
    from core.secret_boss_hints import BossHint
    from core.secret_bosses import SecretBoss


def load_secret_bosses(
    filepath: str = "data/secret_bosses.json",
) -> Dict[str, "SecretBoss"]:
    """Load secret boss definitions from JSON file.

    Args:
        filepath: Path to the secret bosses JSON file

    Returns:
        Dictionary mapping boss_id to SecretBoss, or empty dict if file missing
    """
    from core.secret_bosses import SecretBoss, UnlockCondition, UnlockConditionType

    data = load_json_file(
        filepath,
        default={"bosses": {}},
        context="Loading secret bosses",
        warn_on_missing=True,
    )

    bosses: Dict[str, SecretBoss] = {}
    bosses_data = data.get("bosses", {})

    for boss_id, boss_data in bosses_data.items():
        # Validate required fields
        if "boss_id" not in boss_data:
            log_warning("Secret boss missing 'boss_id', skipping")
            continue
        if "name" not in boss_data:
            log_warning(f"Secret boss '{boss_id}' missing 'name', skipping")
            continue
        if "encounter_id" not in boss_data:
            log_warning(f"Secret boss '{boss_id}' missing 'encounter_id', skipping")
            continue
        if "location_map_id" not in boss_data:
            log_warning(
                f"Secret boss '{boss_id}' missing 'location_map_id', skipping"
            )
            continue
        if "unlock_conditions" not in boss_data:
            log_warning(
                f"Secret boss '{boss_id}' missing 'unlock_conditions', skipping"
            )
            continue

        # Parse unlock conditions
        unlock_conditions: List[UnlockCondition] = []
        for cond_data in boss_data.get("unlock_conditions", []):
            if "condition_type" not in cond_data:
                log_warning(
                    f"Unlock condition in boss '{boss_id}' missing 'condition_type', skipping"
                )
                continue
            if "data" not in cond_data:
                log_warning(
                    f"Unlock condition in boss '{boss_id}' missing 'data', skipping"
                )
                continue
            if "description" not in cond_data:
                log_warning(
                    f"Unlock condition in boss '{boss_id}' missing 'description', skipping"
                )
                continue

            # Convert condition_type string to enum
            try:
                condition_type = UnlockConditionType(cond_data["condition_type"])
            except ValueError:
                log_warning(
                    f"Secret boss '{boss_id}': invalid condition_type '{cond_data['condition_type']}', skipping"
                )
                continue

            condition = UnlockCondition(
                condition_type=condition_type,
                data=cond_data.get("data", {}),
                description=cond_data.get("description", ""),
                hidden=cond_data.get("hidden", False),
            )
            unlock_conditions.append(condition)

        # Create SecretBoss
        boss = SecretBoss(
            boss_id=boss_data["boss_id"],
            name=boss_data.get("name", ""),
            title=boss_data.get("title", ""),
            description=boss_data.get("description", ""),
            encounter_id=boss_data["encounter_id"],
            location_map_id=boss_data["location_map_id"],
            location_x=boss_data.get("location_x", 0),
            location_y=boss_data.get("location_y", 0),
            unlock_conditions=unlock_conditions,
            spawn_trigger_type=boss_data.get("spawn_trigger_type", "interact"),
            lore_entries=boss_data.get("lore_entries", []),
            rewards=boss_data.get("rewards", {}),
            unique_drops=boss_data.get("unique_drops", []),
            achievement_id=boss_data.get("achievement_id"),
            rematch_available=boss_data.get("rematch_available", True),
            post_game_only=boss_data.get("post_game_only", False),
        )
        bosses[boss_id] = boss

    return bosses


def load_secret_boss_hints(
    filepath: str = "data/secret_boss_hints.json",
) -> Dict[str, "BossHint"]:
    """Load secret boss hint definitions from JSON file.

    Args:
        filepath: Path to the secret boss hints JSON file

    Returns:
        Dictionary mapping hint_id to BossHint, or empty dict if file missing
    """
    from core.secret_boss_hints import BossHint, HintType

    data = load_json_file(
        filepath,
        default={"hints": {}},
        context="Loading secret boss hints",
        warn_on_missing=True,
    )

    hints: Dict[str, BossHint] = {}
    hints_data = data.get("hints", {})

    for hint_id, hint_data in hints_data.items():
        # Validate required fields
        if "hint_id" not in hint_data:
            log_warning("Hint missing 'hint_id', skipping")
            continue
        if "boss_id" not in hint_data:
            log_warning(f"Hint '{hint_id}' missing 'boss_id', skipping")
            continue
        if "hint_type" not in hint_data:
            log_warning(f"Hint '{hint_id}' missing 'hint_type', skipping")
            continue
        if "content" not in hint_data:
            log_warning(f"Hint '{hint_id}' missing 'content', skipping")
            continue

        # Convert hint_type string to enum
        try:
            hint_type = HintType(hint_data["hint_type"])
        except ValueError:
            log_warning(
                f"Hint '{hint_id}': invalid hint_type '{hint_data['hint_type']}', skipping"
            )
            continue

        # Create BossHint
        hint = BossHint(
            hint_id=hint_data["hint_id"],
            boss_id=hint_data["boss_id"],
            hint_type=hint_type,
            content=hint_data["content"],
            location_map_id=hint_data.get("location_map_id"),
            location_x=hint_data.get("location_x"),
            location_y=hint_data.get("location_y"),
            trigger_type=hint_data.get("trigger_type", "dialogue"),
            reveal_level=hint_data.get("reveal_level", 1),
        )
        hints[hint_id] = hint

    return hints

"""Secret boss and hint loaders."""

from typing import Dict, List, Tuple, TYPE_CHECKING

from core.constants import SECRET_BOSS_HINTS_JSON, SECRET_BOSSES_JSON
from core.loaders.base import (
    ensure_dict,
    ensure_list,
    load_json_file,
    validate_required_keys,
)
from core.logging_utils import log_schema_warning

if TYPE_CHECKING:
    from core.secret_boss_hints import BossHint
    from core.secret_bosses import SecretBoss


def load_secret_bosses(
    filepath: str = SECRET_BOSSES_JSON,
) -> Dict[str, "SecretBoss"]:
    """Load secret boss definitions from JSON file.

    Args:
        filepath: Path to the secret bosses JSON file

    Returns:
        Dictionary mapping boss_id to SecretBoss, or empty dict if file missing
    """
    from core.secret_bosses import SecretBoss, UnlockCondition, UnlockConditionType

    context = "secret boss loader"
    data = load_json_file(
        filepath,
        default={"bosses": {}},
        context="Loading secret bosses",
        warn_on_missing=True,
    )

    bosses: Dict[str, SecretBoss] = {}
    data = ensure_dict(data, context=context, section="root")
    bosses_data = ensure_dict(
        data.get("bosses", {}),
        context=context,
        section="bosses",
    )

    for boss_id, boss_data in bosses_data.items():
        boss_entry = ensure_dict(
            boss_data,
            context=context,
            section="boss",
            identifier=boss_id,
        )
        if not validate_required_keys(
            boss_entry,
            ("boss_id", "name", "encounter_id", "location_map_id", "unlock_conditions"),
            context=context,
            section="boss",
            identifier=boss_id,
        ):
            continue

        # Parse unlock conditions
        unlock_conditions: List[UnlockCondition] = []
        for cond_data in ensure_list(
            boss_entry.get("unlock_conditions", []),
            context=context,
            section="boss.unlock_conditions",
            identifier=boss_id,
        ):
            cond_entry = ensure_dict(
                cond_data,
                context=context,
                section="unlock_condition",
                identifier=boss_id,
            )
            if not validate_required_keys(
                cond_entry,
                ("condition_type", "data", "description"),
                context=context,
                section="unlock_condition",
                identifier=boss_id,
            ):
                continue

            # Convert condition_type string to enum
            try:
                condition_type = UnlockConditionType(cond_entry["condition_type"])
            except ValueError:
                log_schema_warning(
                    context,
                    f"invalid condition_type '{cond_entry['condition_type']}', skipping condition",
                    section="unlock_condition",
                    identifier=boss_id,
                )
                continue

            condition = UnlockCondition(
                condition_type=condition_type,
                data=cond_entry.get("data", {}),
                description=cond_entry.get("description", ""),
                hidden=cond_entry.get("hidden", False),
            )
            unlock_conditions.append(condition)

        # Create SecretBoss
        boss = SecretBoss(
            boss_id=boss_entry["boss_id"],
            name=boss_entry.get("name", ""),
            title=boss_entry.get("title", ""),
            description=boss_entry.get("description", ""),
            encounter_id=boss_entry["encounter_id"],
            location_map_id=boss_entry["location_map_id"],
            location_x=boss_entry.get("location_x", 0),
            location_y=boss_entry.get("location_y", 0),
            unlock_conditions=unlock_conditions,
            spawn_trigger_type=boss_entry.get("spawn_trigger_type", "interact"),
            lore_entries=boss_entry.get("lore_entries", []),
            rewards=boss_entry.get("rewards", {}),
            unique_drops=boss_entry.get("unique_drops", []),
            achievement_id=boss_entry.get("achievement_id"),
            rematch_available=boss_entry.get("rematch_available", True),
            post_game_only=boss_entry.get("post_game_only", False),
        )
        bosses[boss_id] = boss

    return bosses


def load_secret_boss_hints(
    filepath: str = SECRET_BOSS_HINTS_JSON,
) -> Dict[str, "BossHint"]:
    """Load secret boss hint definitions from JSON file.

    Args:
        filepath: Path to the secret boss hints JSON file

    Returns:
        Dictionary mapping hint_id to BossHint, or empty dict if file missing
    """
    from core.secret_boss_hints import BossHint, HintType

    context = "secret boss hint loader"
    data = load_json_file(
        filepath,
        default={"hints": {}},
        context="Loading secret boss hints",
        warn_on_missing=True,
    )

    hints: Dict[str, BossHint] = {}
    data = ensure_dict(data, context=context, section="root")
    hints_data = ensure_dict(
        data.get("hints", {}),
        context=context,
        section="hints",
    )

    for hint_id, hint_data in hints_data.items():
        hint_entry = ensure_dict(
            hint_data,
            context=context,
            section="hint",
            identifier=hint_id,
        )
        if not validate_required_keys(
            hint_entry,
            ("hint_id", "boss_id", "hint_type", "content"),
            context=context,
            section="hint",
            identifier=hint_id,
        ):
            continue

        # Convert hint_type string to enum
        try:
            hint_type = HintType(hint_entry["hint_type"])
        except ValueError:
            log_schema_warning(
                context,
                f"invalid hint_type '{hint_entry['hint_type']}', skipping hint",
                section="hint",
                identifier=hint_id,
            )
            continue

        # Create BossHint
        hint = BossHint(
            hint_id=hint_entry["hint_id"],
            boss_id=hint_entry["boss_id"],
            hint_type=hint_type,
            content=hint_entry["content"],
            location_map_id=hint_entry.get("location_map_id"),
            location_x=hint_entry.get("location_x"),
            location_y=hint_entry.get("location_y"),
            trigger_type=hint_entry.get("trigger_type", "dialogue"),
            reveal_level=hint_entry.get("reveal_level", 1),
        )
        hints[hint_id] = hint

    return hints

"""Achievement data loader."""

from typing import Dict, TYPE_CHECKING

from core.constants import ACHIEVEMENTS_JSON
from core.loaders.base import ensure_dict, ensure_list, load_json_file, validate_required_keys
from core.logging_utils import log_schema_warning

if TYPE_CHECKING:
    from core.achievements import Achievement


def load_achievements_from_json(
    filepath: str = ACHIEVEMENTS_JSON,
) -> Dict[str, "Achievement"]:
    """Load achievement definitions from JSON file.

    Args:
        filepath: Path to the achievements JSON file

    Returns:
        Dictionary mapping achievement_id to Achievement, or empty dict if file missing
    """
    from core.achievements import Achievement

    context = "achievement loader"
    data = load_json_file(
        filepath,
        default={"achievements": []},
        context="Loading achievements",
        warn_on_missing=True,
    )

    data = ensure_dict(data, context=context, section="root")
    achievements: Dict[str, Achievement] = {}

    for ach_data in ensure_list(
        data.get("achievements", []),
        context=context,
        section="achievements",
    ):
        achievement_id = ach_data.get("id") if isinstance(ach_data, dict) else None
        ach_entry = ensure_dict(
            ach_data,
            context=context,
            section="achievement",
            identifier=achievement_id,
        )
        if not validate_required_keys(
            ach_entry,
            ("id",),
            context=context,
            section="achievement",
            identifier=ach_entry.get("id", "unknown"),
        ):
            continue

        try:
            achievement = Achievement.from_definition(ach_entry)
        except Exception as exc:  # pylint: disable=broad-except
            log_schema_warning(
                context,
                f"failed to parse achievement: {exc}",
                section="achievement",
                identifier=ach_entry.get("id", "unknown"),
            )
            continue

        achievements[achievement.id] = achievement

    return achievements

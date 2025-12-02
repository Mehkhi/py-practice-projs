"""Achievement data loader."""

import os
from typing import Dict, TYPE_CHECKING

from core.loaders.base import load_json_file
from core.logging_utils import log_warning

if TYPE_CHECKING:
    from core.achievements import Achievement


def load_achievements_from_json(
    filepath: str = os.path.join("data", "achievements.json"),
) -> Dict[str, "Achievement"]:
    """Load achievement definitions from JSON file.

    Args:
        filepath: Path to the achievements JSON file

    Returns:
        Dictionary mapping achievement_id to Achievement, or empty dict if file missing
    """
    from core.achievements import Achievement

    data = load_json_file(
        filepath,
        default={"achievements": []},
        context="Loading achievements",
        warn_on_missing=True,
    )

    achievements: Dict[str, Achievement] = {}

    for ach_data in data.get("achievements", []):
        # Validate required fields
        if "id" not in ach_data:
            log_warning("Achievement missing 'id', skipping")
            continue

        achievement = Achievement.from_definition(ach_data)
        achievements[achievement.id] = achievement

    return achievements

"""Post-game unlock data loader."""

import os
from typing import Dict, TYPE_CHECKING

from core.loaders.base import load_json_file
from core.logging_utils import log_warning

if TYPE_CHECKING:
    from core.post_game import PostGameUnlock


def load_post_game_unlocks(
    filepath: str = os.path.join("data", "post_game_unlocks.json"),
) -> Dict[str, "PostGameUnlock"]:
    """Load post-game unlock definitions from JSON file.

    Args:
        filepath: Path to the post-game unlocks JSON file

    Returns:
        Dictionary mapping unlock_id to PostGameUnlock, or empty dict if file missing
    """
    from core.post_game import PostGameUnlock

    data = load_json_file(
        filepath,
        default={"unlocks": {}},
        context="Loading post-game unlocks",
        warn_on_missing=True,
    )

    unlocks: Dict[str, PostGameUnlock] = {}
    unlocks_data = data.get("unlocks", {})

    for unlock_id, unlock_data in unlocks_data.items():
        # Validate required fields
        if "unlock_id" not in unlock_data:
            log_warning("Post-game unlock missing 'unlock_id', skipping")
            continue
        if "name" not in unlock_data:
            log_warning(f"Post-game unlock '{unlock_id}' missing 'name', skipping")
            continue
        if "description" not in unlock_data:
            log_warning(
                f"Post-game unlock '{unlock_id}' missing 'description', skipping"
            )
            continue
        if "unlock_type" not in unlock_data:
            log_warning(
                f"Post-game unlock '{unlock_id}' missing 'unlock_type', skipping"
            )
            continue

        unlock = PostGameUnlock(
            unlock_id=unlock_data["unlock_id"],
            name=unlock_data["name"],
            description=unlock_data["description"],
            unlock_type=unlock_data["unlock_type"],
            requires_ending=unlock_data.get("requires_ending"),
        )
        unlocks[unlock.unlock_id] = unlock

    return unlocks

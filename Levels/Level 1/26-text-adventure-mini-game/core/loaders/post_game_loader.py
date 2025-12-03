"""Post-game unlock data loader."""

from typing import Dict, TYPE_CHECKING

from core.constants import POST_GAME_UNLOCKS_JSON
from core.loaders.base import ensure_dict, load_json_file, validate_required_keys

if TYPE_CHECKING:
    from core.post_game import PostGameUnlock


def load_post_game_unlocks(
    filepath: str = POST_GAME_UNLOCKS_JSON,
) -> Dict[str, "PostGameUnlock"]:
    """Load post-game unlock definitions from JSON file.

    Args:
        filepath: Path to the post-game unlocks JSON file

    Returns:
        Dictionary mapping unlock_id to PostGameUnlock, or empty dict if file missing
    """
    from core.post_game import PostGameUnlock

    context = "post-game unlock loader"
    data = load_json_file(
        filepath,
        default={"unlocks": {}},
        context="Loading post-game unlocks",
        warn_on_missing=True,
    )

    unlocks: Dict[str, PostGameUnlock] = {}
    data = ensure_dict(data, context=context, section="root")
    unlocks_data = ensure_dict(
        data.get("unlocks", {}),
        context=context,
        section="unlocks",
    )

    for unlock_id, unlock_data in unlocks_data.items():
        unlock_entry = ensure_dict(
            unlock_data,
            context=context,
            section="unlock",
            identifier=unlock_id,
        )
        if not validate_required_keys(
            unlock_entry,
            ("unlock_id", "name", "description", "unlock_type"),
            context=context,
            section="unlock",
            identifier=unlock_id,
        ):
            continue

        unlock = PostGameUnlock(
            unlock_id=unlock_entry["unlock_id"],
            name=unlock_entry["name"],
            description=unlock_entry["description"],
            unlock_type=unlock_entry["unlock_type"],
            requires_ending=unlock_entry.get("requires_ending"),
        )
        unlocks[unlock.unlock_id] = unlock

    return unlocks

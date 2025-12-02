"""Tutorial data loaders."""

from typing import Dict, Tuple

from core.loaders.base import load_json_file
from core.logging_utils import log_warning


def load_tutorial_data(
    filepath: str = "data/tutorial_tips.json",
) -> Tuple[Dict[str, "TutorialTip"], Dict[str, "HelpEntry"]]:
    """Load tutorial tips and help entries from JSON.

    Args:
        filepath: Path to the tutorial tips JSON file

    Returns:
        Tuple of (tips_dict, help_entries_dict), or empty dicts if file missing
    """
    from core.tutorial_system import TutorialTip, HelpEntry, TipTrigger

    data = load_json_file(
        filepath,
        default={"tips": [], "help_entries": []},
        context="Loading tutorial data",
        warn_on_missing=True,
    )

    tips: Dict[str, TutorialTip] = {}
    help_entries: Dict[str, HelpEntry] = {}

    # Load tips
    for tip_data in data.get("tips", []):
        # Validate required fields
        if "tip_id" not in tip_data:
            log_warning("Tutorial tip missing 'tip_id', skipping")
            continue
        if "trigger" not in tip_data:
            log_warning(
                f"Tutorial tip '{tip_data.get('tip_id', 'unknown')}' missing 'trigger', skipping"
            )
            continue
        if "title" not in tip_data:
            log_warning(
                f"Tutorial tip '{tip_data.get('tip_id', 'unknown')}' missing 'title', skipping"
            )
            continue
        if "content" not in tip_data:
            log_warning(
                f"Tutorial tip '{tip_data.get('tip_id', 'unknown')}' missing 'content', skipping"
            )
            continue

        # Convert trigger string to enum
        try:
            trigger = TipTrigger[tip_data["trigger"]]
        except KeyError:
            log_warning(
                f"Tutorial tip '{tip_data['tip_id']}': invalid trigger '{tip_data['trigger']}', skipping"
            )
            continue

        tip = TutorialTip(
            tip_id=tip_data["tip_id"],
            trigger=trigger,
            title=tip_data["title"],
            content=tip_data["content"],
            priority=tip_data.get("priority", 5),
            category=tip_data.get("category", "general"),
            requires_tips=tip_data.get("requires_tips", []),
        )
        tips[tip.tip_id] = tip

    # Load help entries
    for entry_data in data.get("help_entries", []):
        # Validate required fields
        if "entry_id" not in entry_data:
            log_warning("Help entry missing 'entry_id', skipping")
            continue
        if "title" not in entry_data:
            log_warning(
                f"Help entry '{entry_data.get('entry_id', 'unknown')}' missing 'title', skipping"
            )
            continue
        if "content" not in entry_data:
            log_warning(
                f"Help entry '{entry_data.get('entry_id', 'unknown')}' missing 'content', skipping"
            )
            continue
        if "category" not in entry_data:
            log_warning(
                f"Help entry '{entry_data.get('entry_id', 'unknown')}' missing 'category', skipping"
            )
            continue

        entry = HelpEntry(
            entry_id=entry_data["entry_id"],
            title=entry_data["title"],
            content=entry_data["content"],
            category=entry_data["category"],
            order=entry_data.get("order", 0),
        )
        help_entries[entry.entry_id] = entry

    return tips, help_entries


def load_tutorial_tips(
    filepath: str = "data/tutorial_tips.json",
) -> Tuple[Dict[str, "TutorialTip"], Dict[str, "HelpEntry"]]:
    """Load tutorial tips and help entries from JSON.

    Args:
        filepath: Path to tutorial tips JSON file

    Returns:
        Tuple of (tips dict, help_entries dict)
    """
    from core.tutorial_system import TutorialTip, HelpEntry, TipTrigger

    data = load_json_file(
        filepath,
        default={"tips": [], "help_entries": []},
        context="Loading tutorial tips",
        warn_on_missing=True,
    )

    tips: Dict[str, TutorialTip] = {}
    for tip_data in data.get("tips", []):
        try:
            trigger = TipTrigger[tip_data["trigger"]]
        except (KeyError, ValueError):
            log_warning(
                f"Tutorial tip '{tip_data.get('tip_id', 'unknown')}': invalid trigger '{tip_data.get('trigger')}', skipping"
            )
            continue

        if (
            "tip_id" not in tip_data
            or "title" not in tip_data
            or "content" not in tip_data
        ):
            log_warning("Tutorial tip missing required fields, skipping entry")
            continue

        tip = TutorialTip(
            tip_id=tip_data["tip_id"],
            trigger=trigger,
            title=tip_data.get("title", tip_data["tip_id"]),
            content=tip_data.get("content", ""),
            priority=int(tip_data.get("priority", 5)),
            category=tip_data.get("category", "general"),
            requires_tips=tip_data.get("requires_tips", []),
        )
        tips[tip.tip_id] = tip

    help_entries: Dict[str, HelpEntry] = {}
    for entry_data in data.get("help_entries", []):
        if (
            "entry_id" not in entry_data
            or "title" not in entry_data
            or "content" not in entry_data
        ):
            log_warning("Help entry missing required fields, skipping entry")
            continue

        entry = HelpEntry(
            entry_id=entry_data["entry_id"],
            title=entry_data.get("title", entry_data["entry_id"]),
            content=entry_data.get("content", ""),
            category=entry_data.get("category", "General"),
            order=int(entry_data.get("order", 0)),
        )
        help_entries[entry.entry_id] = entry

    return tips, help_entries

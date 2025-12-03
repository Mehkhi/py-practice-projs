"""Tutorial data loaders."""

from typing import Dict, Tuple

from core.constants import TUTORIAL_TIPS_JSON
from core.loaders.base import (
    ensure_dict,
    ensure_list,
    load_json_file,
    validate_required_keys,
)
from core.logging_utils import log_schema_warning


def _parse_tutorial_file(
    filepath: str, *, context: str
) -> Tuple[Dict[str, "TutorialTip"], Dict[str, "HelpEntry"]]:
    """Shared parsing for tutorial tip/help files."""
    from core.tutorial_system import HelpEntry, TipTrigger, TutorialTip

    raw_data = load_json_file(
        filepath,
        default={"tips": [], "help_entries": []},
        context="Loading tutorial tips",
        warn_on_missing=True,
    )
    data = ensure_dict(raw_data, context=context, section="root")

    tips: Dict[str, TutorialTip] = {}
    for tip_data in ensure_list(
        data.get("tips", []),
        context=context,
        section="tips",
    ):
        tip_identifier = tip_data.get("tip_id") if isinstance(tip_data, dict) else None
        tip_entry = ensure_dict(
            tip_data,
            context=context,
            section="tip",
            identifier=tip_identifier,
        )
        if not validate_required_keys(
            tip_entry,
            ("tip_id", "trigger", "title", "content"),
            context=context,
            section="tip",
            identifier=tip_entry.get("tip_id", "unknown"),
        ):
            continue

        try:
            trigger = TipTrigger[tip_entry["trigger"]]
        except KeyError:
            log_schema_warning(
                context,
                f"invalid trigger '{tip_entry['trigger']}', skipping tip",
                section="tip",
                identifier=tip_entry.get("tip_id", "unknown"),
            )
            continue

        tip = TutorialTip(
            tip_id=tip_entry["tip_id"],
            trigger=trigger,
            title=tip_entry["title"],
            content=tip_entry["content"],
            priority=int(tip_entry.get("priority", 5)),
            category=tip_entry.get("category", "general"),
            requires_tips=ensure_list(
                tip_entry.get("requires_tips", []),
                context=context,
                section="tip.requires_tips",
                identifier=tip_entry.get("tip_id", "unknown"),
            ),
        )
        tips[tip.tip_id] = tip

    help_entries: Dict[str, HelpEntry] = {}
    for entry_data in ensure_list(
        data.get("help_entries", []),
        context=context,
        section="help_entries",
    ):
        entry_identifier = entry_data.get("entry_id") if isinstance(entry_data, dict) else None
        entry_entry = ensure_dict(
            entry_data,
            context=context,
            section="help_entry",
            identifier=entry_identifier,
        )
        if not validate_required_keys(
            entry_entry,
            ("entry_id", "title", "content", "category"),
            context=context,
            section="help_entry",
            identifier=entry_entry.get("entry_id", "unknown"),
        ):
            continue

        entry = HelpEntry(
            entry_id=entry_entry["entry_id"],
            title=entry_entry.get("title", entry_entry["entry_id"]),
            content=entry_entry.get("content", ""),
            category=entry_entry["category"],
            order=int(entry_entry.get("order", 0)),
        )
        help_entries[entry.entry_id] = entry

    return tips, help_entries


def load_tutorial_data(
    filepath: str = TUTORIAL_TIPS_JSON,
) -> Tuple[Dict[str, "TutorialTip"], Dict[str, "HelpEntry"]]:
    """Canonical tutorial data loader (shared by both public entry points)."""
    return _parse_tutorial_file(filepath, context="tutorial loader")


def load_tutorial_tips(
    filepath: str = TUTORIAL_TIPS_JSON,
) -> Tuple[Dict[str, "TutorialTip"], Dict[str, "HelpEntry"]]:
    """Compatibility wrapper around ``load_tutorial_data``."""
    return _parse_tutorial_file(filepath, context="tutorial tips loader")

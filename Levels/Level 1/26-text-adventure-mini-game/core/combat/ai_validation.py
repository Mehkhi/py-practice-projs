"""AI profile validation helpers."""

from typing import Dict, Optional

from core.items import Item
from core.combat import Skill


def iter_ai_actions(ai_profile: Optional[dict]):
    """Yield (phase_name, action_dict) tuples for AI validation."""
    if not ai_profile:
        return

    for rule in ai_profile.get("rules", []) or []:
        action = rule.get("action") if isinstance(rule, dict) else None
        if action:
            yield ("default", action)

    for phase in ai_profile.get("phases", []) or []:
        phase_name = phase.get("name", "phase") if isinstance(phase, dict) else "phase"
        for rule in phase.get("rules", []) or []:
            action = rule.get("action") if isinstance(rule, dict) else None
            if action:
                yield (phase_name, action)

    fallback = ai_profile.get("fallback_action") if ai_profile else None
    if fallback:
        yield ("fallback", fallback)


def validate_ai_profile_dict(
    ai_profile: Optional[dict],
    skills: Dict[str, Skill],
    items_db: Dict[str, Item],
    encounter_id: str,
    enemy_id: str,
    warn=print,
) -> None:
    """Warn on missing skill_id/item_id references in an AI profile."""
    if not ai_profile:
        return

    for phase_name, action in iter_ai_actions(ai_profile):
        action_type = action.get("type")
        if action_type == "skill":
            skill_id = action.get("skill_id")
            if skill_id and skill_id not in skills:
                warn(
                    f"Warning: Encounter '{encounter_id}' enemy '{enemy_id}' references "
                    f"unknown skill_id '{skill_id}' in AI profile (phase '{phase_name}')"
                )
        elif action_type == "item":
            item_id = action.get("item_id")
            if item_id and item_id not in items_db:
                warn(
                    f"Warning: Encounter '{encounter_id}' enemy '{enemy_id}' references "
                    f"unknown item_id '{item_id}' in AI profile (phase '{phase_name}')"
                )


def warn_missing_profile(encounter_id: str, enemy_data: dict, warn=print) -> None:
    """Warn when an encounter is missing an AI profile and default is not allowed."""
    if enemy_data.get("ai_profile") or enemy_data.get("allow_default_ai"):
        return

    warn(
        f"Warning: Encounter '{encounter_id}' enemy '{enemy_data.get('id')}' has no ai_profile "
        "and is not marked allow_default_ai; will use basic fallback AI."
    )

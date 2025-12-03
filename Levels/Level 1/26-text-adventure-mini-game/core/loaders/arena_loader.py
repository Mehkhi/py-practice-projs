"""Arena data loader."""

from typing import Dict

from core.constants import ARENA_JSON
from core.loaders.base import ensure_dict, ensure_list, load_json_file, validate_required_keys


def load_arena_data(filepath: str = ARENA_JSON) -> "ArenaManager":
    """Load arena fighters and schedule from JSON file.

    Args:
        filepath: Path to the arena data JSON file

    Returns:
        ArenaManager instance with loaded fighters, or empty manager if file missing
    """
    from core.arena import ArenaManager, ArenaFighter

    context = "arena loader"
    data = load_json_file(
        filepath,
        default={"fighters": {}, "arena_schedule": {}},
        context="Loading arena data",
        warn_on_missing=True,
    )

    data = ensure_dict(data, context=context, section="root")
    fighters: Dict[str, ArenaFighter] = {}
    fighters_data = ensure_dict(
        data.get("fighters", {}),
        context=context,
        section="fighters",
    )

    for fighter_id, fighter_data in fighters_data.items():
        fighter_data = ensure_dict(
            fighter_data,
            context=context,
            section="fighter",
            identifier=fighter_id,
        )
        if not validate_required_keys(
            fighter_data,
            ("fighter_id", "name", "sprite_id", "stats", "skills", "odds"),
            context=context,
            section="fighter",
            identifier=fighter_id,
        ):
            continue

        stats = ensure_dict(
            fighter_data.get("stats", {}),
            context=context,
            section="stats",
            identifier=fighter_id,
        )
        if not validate_required_keys(
            stats,
            ("hp", "attack", "defense", "speed"),
            context=context,
            section="stats",
            identifier=fighter_id,
        ):
            continue

        skills = ensure_list(
            fighter_data.get("skills", []),
            context=context,
            section="skills",
            identifier=fighter_id,
        )

        fighter = ArenaFighter(
            fighter_id=fighter_data["fighter_id"],
            name=fighter_data["name"],
            sprite_id=fighter_data["sprite_id"],
            stats=stats,
            skills=skills,
            odds=float(fighter_data.get("odds", 2.0)),
            wins=0,
            losses=0,
        )
        fighters[fighter_id] = fighter

    arena_schedule = ensure_dict(
        data.get("arena_schedule", {}),
        context=context,
        section="arena_schedule",
    )
    manager = ArenaManager(fighters, arena_schedule)
    return manager

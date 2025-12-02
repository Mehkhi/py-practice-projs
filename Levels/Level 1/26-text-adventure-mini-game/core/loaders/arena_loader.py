"""Arena data loader."""

from typing import Dict

from core.loaders.base import load_json_file
from core.logging_utils import log_warning


def load_arena_data(filepath: str = "data/arena.json") -> "ArenaManager":
    """Load arena fighters and schedule from JSON file.

    Args:
        filepath: Path to the arena data JSON file

    Returns:
        ArenaManager instance with loaded fighters, or empty manager if file missing
    """
    from core.arena import ArenaManager, ArenaFighter

    data = load_json_file(
        filepath,
        default={"fighters": {}, "arena_schedule": {}},
        context="Loading arena data",
        warn_on_missing=True,
    )

    fighters: Dict[str, ArenaFighter] = {}
    fighters_data = data.get("fighters", {})

    for fighter_id, fighter_data in fighters_data.items():
        # Validate required fields
        if "fighter_id" not in fighter_data:
            log_warning("Arena fighter missing 'fighter_id', skipping")
            continue
        if "name" not in fighter_data:
            log_warning(f"Arena fighter '{fighter_id}' missing 'name', skipping")
            continue
        if "sprite_id" not in fighter_data:
            log_warning(f"Arena fighter '{fighter_id}' missing 'sprite_id', skipping")
            continue
        if "stats" not in fighter_data:
            log_warning(f"Arena fighter '{fighter_id}' missing 'stats', skipping")
            continue
        if "skills" not in fighter_data:
            log_warning(f"Arena fighter '{fighter_id}' missing 'skills', skipping")
            continue
        if "odds" not in fighter_data:
            log_warning(f"Arena fighter '{fighter_id}' missing 'odds', skipping")
            continue

        # Validate stats
        stats = fighter_data.get("stats", {})
        required_stats = ["hp", "attack", "defense", "speed"]
        for stat in required_stats:
            if stat not in stats:
                log_warning(
                    f"Arena fighter '{fighter_id}' missing stat '{stat}', skipping"
                )
                break
        else:
            fighter = ArenaFighter(
                fighter_id=fighter_data["fighter_id"],
                name=fighter_data["name"],
                sprite_id=fighter_data["sprite_id"],
                stats=stats,
                skills=fighter_data.get("skills", []),
                odds=float(fighter_data.get("odds", 2.0)),
                wins=0,
                losses=0,
            )
            fighters[fighter_id] = fighter

    arena_schedule = data.get("arena_schedule", {})
    manager = ArenaManager(fighters, arena_schedule)
    return manager

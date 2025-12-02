"""Brain teaser data loader."""

from typing import Dict

from core.loaders.base import load_json_file
from core.logging_utils import log_warning


def load_brain_teasers(
    filepath: str = "data/brain_teasers.json",
) -> Dict[str, "BrainTeaser"]:
    """Load brain teaser puzzles from JSON file.

    Args:
        filepath: Path to the brain teasers JSON file

    Returns:
        Dictionary mapping teaser_id to BrainTeaser, or empty dict if file missing
    """
    from core.brain_teasers import (
        BrainTeaser,
        BrainTeaserType,
        Riddle,
        WordScramble,
        NumberSequence,
        PatternMatch,
        SimonSays,
        LockCombination,
    )

    data = load_json_file(
        filepath,
        default={"teasers": {}},
        context="Loading brain teasers",
        warn_on_missing=True,
    )

    if not isinstance(data, dict):
        raise ValueError("Brain teaser data must be a dictionary at the top level")

    teasers: Dict[str, BrainTeaser] = {}
    teasers_data = data.get("teasers", {})
    if not isinstance(teasers_data, dict):
        raise ValueError("Brain teaser data 'teasers' section must be a dictionary")

    for teaser_id, teaser_data in teasers_data.items():
        if not isinstance(teaser_data, dict):
            raise ValueError(f"Brain teaser '{teaser_id}' entry must be a dictionary")
        # Validate required fields
        if "teaser_id" not in teaser_data:
            log_warning("Brain teaser missing 'teaser_id', skipping")
            continue
        if "teaser_type" not in teaser_data:
            log_warning(
                f"Brain teaser '{teaser_id}' missing 'teaser_type', skipping"
            )
            continue
        if "name" not in teaser_data:
            log_warning(f"Brain teaser '{teaser_id}' missing 'name', skipping")
            continue
        if "data" not in teaser_data:
            log_warning(f"Brain teaser '{teaser_id}' missing 'data', skipping")
            continue

        # Convert teaser_type string to enum
        try:
            teaser_type = BrainTeaserType(teaser_data["teaser_type"])
        except ValueError:
            log_warning(
                f"Brain teaser '{teaser_id}': invalid teaser_type '{teaser_data['teaser_type']}', skipping"
            )
            continue

        # Parse puzzle data based on type
        puzzle_data = teaser_data["data"]
        if not isinstance(puzzle_data, dict):
            raise ValueError(f"Brain teaser '{teaser_id}' data must be a dictionary")
        puzzle_obj = None

        if teaser_type == BrainTeaserType.RIDDLE:
            if "question" not in puzzle_data or "answer" not in puzzle_data:
                log_warning(
                    f"Riddle '{teaser_id}' missing required fields, skipping"
                )
                continue
            puzzle_obj = Riddle(
                riddle_id=puzzle_data.get("riddle_id", teaser_id),
                question=puzzle_data["question"],
                answer=puzzle_data["answer"],
                alternatives=puzzle_data.get("alternatives", []),
                hint=puzzle_data.get("hint", ""),
                difficulty=puzzle_data.get("difficulty", 1),
            )

        elif teaser_type == BrainTeaserType.WORD_SCRAMBLE:
            if "word" not in puzzle_data or "scrambled" not in puzzle_data:
                log_warning(
                    f"Word scramble '{teaser_id}' missing required fields, skipping"
                )
                continue
            puzzle_obj = WordScramble(
                puzzle_id=puzzle_data.get("puzzle_id", teaser_id),
                word=puzzle_data["word"],
                scrambled=puzzle_data["scrambled"],
                hint=puzzle_data.get("hint", ""),
                category=puzzle_data.get("category", ""),
            )

        elif teaser_type == BrainTeaserType.NUMBER_SEQUENCE:
            if "sequence" not in puzzle_data or "answer" not in puzzle_data:
                log_warning(
                    f"Number sequence '{teaser_id}' missing required fields, skipping"
                )
                continue
            puzzle_obj = NumberSequence(
                puzzle_id=puzzle_data.get("puzzle_id", teaser_id),
                sequence=puzzle_data["sequence"],
                answer=puzzle_data["answer"],
                pattern_description=puzzle_data.get(
                    "pattern_description", ""
                ),
            )

        elif teaser_type == BrainTeaserType.PATTERN_MATCH:
            if "grid" not in puzzle_data or "answer_position" not in puzzle_data:
                log_warning(
                    f"Pattern match '{teaser_id}' missing required fields, skipping"
                )
                continue
            puzzle_obj = PatternMatch(
                puzzle_id=puzzle_data.get("puzzle_id", teaser_id),
                grid=puzzle_data["grid"],
                answer_position=tuple(puzzle_data["answer_position"]),
                puzzle_type=puzzle_data.get("puzzle_type", "odd_one_out"),
            )

        elif teaser_type == BrainTeaserType.SIMON_SAYS:
            if "sequence_length" not in puzzle_data:
                log_warning(
                    f"Simon Says '{teaser_id}' missing required fields, skipping"
                )
                continue
            puzzle_obj = SimonSays(
                puzzle_id=puzzle_data.get("puzzle_id", teaser_id),
                sequence_length=puzzle_data["sequence_length"],
                colors=puzzle_data.get(
                    "colors", ["red", "blue", "green", "yellow"]
                ),
            )

        elif teaser_type == BrainTeaserType.LOCK_COMBINATION:
            if "combination" not in puzzle_data:
                log_warning(
                    f"Lock combination '{teaser_id}' missing required fields, skipping"
                )
                continue
            puzzle_obj = LockCombination(
                puzzle_id=puzzle_data.get("puzzle_id", teaser_id),
                combination=puzzle_data["combination"],
                num_dials=puzzle_data.get(
                    "num_dials", len(puzzle_data["combination"])
                ),
                max_value=puzzle_data.get("max_value", 9),
                clues=puzzle_data.get("clues", []),
            )

        elif teaser_type == BrainTeaserType.SLIDING_TILES:
            if "solution" not in puzzle_data:
                log_warning(
                    f"Sliding tiles '{teaser_id}' missing solution grid, skipping"
                )
                continue
            puzzle_obj = {"solution": puzzle_data["solution"]}

        if not puzzle_obj:
            log_warning(
                f"Failed to create puzzle object for '{teaser_id}', skipping"
            )
            continue

        # Create BrainTeaser wrapper
        teaser = BrainTeaser(
            teaser_id=teaser_data["teaser_id"],
            teaser_type=teaser_type,
            name=teaser_data["name"],
            data=puzzle_obj,
            rewards=teaser_data.get("rewards", {}),
            attempts_allowed=teaser_data.get("attempts_allowed", 3),
            solved=False,
        )
        teasers[teaser_id] = teaser

    return teasers

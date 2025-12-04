"""Brain teaser data loader."""

from typing import Dict, TYPE_CHECKING

from core.constants import BRAIN_TEASERS_JSON
from core.loaders.base import (
    detach_json_data,
    ensure_dict,
    ensure_list,
    load_json_file,
    validate_required_keys,
)
from core.logging_utils import log_schema_warning

if TYPE_CHECKING:
    from core.brain_teasers import BrainTeaser


def load_brain_teasers(
    filepath: str = BRAIN_TEASERS_JSON,
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

    context = "brain teaser loader"
    data = load_json_file(
        filepath,
        default={"teasers": {}},
        context="Loading brain teasers",
        warn_on_missing=True,
        copy_data=False,
    )

    data = ensure_dict(data, context=context, section="root")

    teasers: Dict[str, BrainTeaser] = {}
    teasers_data = ensure_dict(
        data.get("teasers", {}),
        context=context,
        section="teasers",
    )

    for teaser_id, teaser_data in teasers_data.items():
        teaser_entry = detach_json_data(
            ensure_dict(
                teaser_data,
                context=context,
                section="teasers",
                identifier=teaser_id,
            )
        )
        if not validate_required_keys(
            teaser_entry,
            ("teaser_id", "teaser_type", "name", "data"),
            context=context,
            section="teasers",
            identifier=teaser_id,
        ):
            continue

        # Ensure JSON key and inner teaser_id agree, so future refactors
        # cannot accidentally desync identifiers between content and code.
        inner_id = str(teaser_entry.get("teaser_id", teaser_id))
        if inner_id != teaser_id:
            log_schema_warning(
                context,
                f"outer key '{teaser_id}' does not match inner teaser_id '{inner_id}', using inner id",
                section="teasers",
                identifier=teaser_id,
            )


        # Convert teaser_type string to enum
        try:
            teaser_type = BrainTeaserType(teaser_entry["teaser_type"])
        except ValueError:
            log_schema_warning(
                context,
                f"invalid teaser_type '{teaser_entry['teaser_type']}', skipping teaser",
                section="teasers",
                identifier=teaser_id,
            )
            continue

        # Parse puzzle data based on type
        puzzle_data = detach_json_data(
            ensure_dict(
                teaser_entry["data"],
                context=context,
                section="teaser.data",
                identifier=teaser_id,
            )
        )
        puzzle_obj = None

        if teaser_type == BrainTeaserType.RIDDLE:
            if not validate_required_keys(
                puzzle_data,
                ("question", "answer"),
                context=context,
                section="teaser.data",
                identifier=teaser_id,
            ):
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
            if not validate_required_keys(
                puzzle_data,
                ("word", "scrambled"),
                context=context,
                section="teaser.data",
                identifier=teaser_id,
            ):
                continue
            puzzle_obj = WordScramble(
                puzzle_id=puzzle_data.get("puzzle_id", teaser_id),
                word=puzzle_data["word"],
                scrambled=puzzle_data["scrambled"],
                hint=puzzle_data.get("hint", ""),
                category=puzzle_data.get("category", ""),
            )

        elif teaser_type == BrainTeaserType.NUMBER_SEQUENCE:
            if not validate_required_keys(
                puzzle_data,
                ("sequence", "answer"),
                context=context,
                section="teaser.data",
                identifier=teaser_id,
            ):
                continue
            puzzle_obj = NumberSequence(
                puzzle_id=puzzle_data.get("puzzle_id", teaser_id),
                sequence=ensure_list(
                    puzzle_data.get("sequence", []),
                    context=context,
                    section="teaser.data.sequence",
                    identifier=teaser_id,
                ),
                answer=puzzle_data["answer"],
                pattern_description=puzzle_data.get(
                    "pattern_description", ""
                ),
            )

        elif teaser_type == BrainTeaserType.PATTERN_MATCH:
            if not validate_required_keys(
                puzzle_data,
                ("grid", "answer_position"),
                context=context,
                section="teaser.data",
                identifier=teaser_id,
            ):
                continue
            answer_position = ensure_list(
                puzzle_data.get("answer_position"),
                context=context,
                section="teaser.data.answer_position",
                identifier=teaser_id,
            )
            if len(answer_position) != 2:
                log_schema_warning(
                    context,
                    "answer_position must contain exactly 2 coordinates, skipping teaser",
                    section="teaser.data.answer_position",
                    identifier=teaser_id,
                )
                continue
            grid_values = ensure_list(
                puzzle_data.get("grid", []),
                context=context,
                section="teaser.data.grid",
                identifier=teaser_id,
            )
            puzzle_obj = PatternMatch(
                puzzle_id=puzzle_data.get("puzzle_id", teaser_id),
                grid=grid_values,
                answer_position=tuple(answer_position),
                puzzle_type=puzzle_data.get("puzzle_type", "odd_one_out"),
            )

        elif teaser_type == BrainTeaserType.SIMON_SAYS:
            if not validate_required_keys(
                puzzle_data,
                ("sequence_length",),
                context=context,
                section="teaser.data",
                identifier=teaser_id,
            ):
                continue
            puzzle_obj = SimonSays(
                puzzle_id=puzzle_data.get("puzzle_id", teaser_id),
                sequence_length=puzzle_data["sequence_length"],
                colors=ensure_list(
                    puzzle_data.get("colors", ["red", "blue", "green", "yellow"]),
                    context=context,
                    section="teaser.data.colors",
                    identifier=teaser_id,
                ),
            )

        elif teaser_type == BrainTeaserType.LOCK_COMBINATION:
            if not validate_required_keys(
                puzzle_data,
                ("combination",),
                context=context,
                section="teaser.data",
                identifier=teaser_id,
            ):
                continue
            combination = ensure_list(
                puzzle_data.get("combination", []),
                context=context,
                section="teaser.data.combination",
                identifier=teaser_id,
            )
            puzzle_obj = LockCombination(
                puzzle_id=puzzle_data.get("puzzle_id", teaser_id),
                combination=combination,
                num_dials=puzzle_data.get("num_dials", len(combination)),
                max_value=puzzle_data.get("max_value", 9),
                clues=ensure_list(
                    puzzle_data.get("clues", []),
                    context=context,
                    section="teaser.data.clues",
                    identifier=teaser_id,
                ),
            )

        elif teaser_type == BrainTeaserType.SLIDING_TILES:
            if not validate_required_keys(
                puzzle_data,
                ("solution",),
                context=context,
                section="teaser.data",
                identifier=teaser_id,
            ):
                continue
            puzzle_obj = {"solution": puzzle_data["solution"]}

        if not puzzle_obj:
            log_schema_warning(
                context,
                "failed to create puzzle object, skipping teaser",
                section="teasers",
                identifier=teaser_id,
            )
            continue

        # Create BrainTeaser wrapper
        teaser = BrainTeaser(
            teaser_id=teaser_entry["teaser_id"],
            teaser_type=teaser_type,
            name=teaser_entry["name"],
            data=puzzle_obj,
            rewards=teaser_entry.get("rewards", {}),
            attempts_allowed=teaser_entry.get("attempts_allowed", 3),
            solved=False,
        )
        # Use the inner teaser_id as the canonical key. This allows content
        # authors to rename outer JSON keys while keeping stable identifiers,
        # but we still log when they diverge.
        teasers[teaser.teaser_id] = teaser

    return teasers

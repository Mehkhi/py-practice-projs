"""Minigame deserialization (fishing, puzzles, brain teasers)."""

from typing import Any, Dict, Optional

from .base import DeserializationResources, DeserializerContext, DomainDeserializer


def deserialize_puzzle_manager(
    data: Optional[Dict[str, Any]],
    puzzle_definitions: Optional[Dict[str, Any]] = None,
) -> Optional[Any]:
    """Deserialize puzzle manager from a dict."""
    if not data:
        return None

    from ...puzzles import PuzzleManager
    from core.loaders.puzzle_loader import load_puzzles_from_json

    definitions = puzzle_definitions or load_puzzles_from_json()
    return PuzzleManager.deserialize(data, definitions)


def deserialize_brain_teaser_manager(
    data: Optional[Dict[str, Any]],
    teaser_definitions: Optional[Dict[str, Any]] = None,
) -> Optional[Any]:
    """Deserialize brain teaser manager from a dict."""
    if not data:
        return None

    from ...brain_teasers import BrainTeaserManager
    from core.loaders.brain_teaser_loader import load_brain_teasers

    definitions = teaser_definitions or load_brain_teasers()
    return BrainTeaserManager.deserialize(data, definitions)


def _restore_fishing(data: Dict[str, Any], context: DeserializerContext, resources: DeserializationResources) -> None:
    if not context.fishing_system or "fishing" not in data:
        return
    from ...fishing import FishingSystem

    fishing_data = data["fishing"]
    fish_db, spots = resources.resolve_fishing_data(
        getattr(context.fishing_system, "fish_db", None),
        getattr(context.fishing_system, "spots", None),
    )
    restored = FishingSystem.deserialize(fishing_data, fish_db, spots)
    context.fishing_system.player_records = restored.player_records
    context.fishing_system.total_catches = restored.total_catches
    context.fishing_system.catches_per_spot = restored.catches_per_spot


def _restore_puzzles(data: Dict[str, Any], context: DeserializerContext, resources: DeserializationResources) -> None:
    if not context.puzzle_manager or "puzzles" not in data:
        return
    puzzles_data = data["puzzles"]
    definitions = resources.resolve_puzzles(context.puzzle_manager)
    restored_manager = deserialize_puzzle_manager(puzzles_data, definitions)
    if restored_manager:
        for puzzle_id, puzzle in restored_manager.puzzles.items():
            if puzzle_id in context.puzzle_manager.puzzles:
                manager_puzzle = context.puzzle_manager.puzzles[puzzle_id]
                manager_puzzle.solved = puzzle.solved
                for element_id, element in puzzle.elements.items():
                    if element_id in manager_puzzle.elements:
                        manager_element = manager_puzzle.elements[element_id]
                        manager_element.x = element.x
                        manager_element.y = element.y
                        manager_element.state = element.state
    puzzles_raw = puzzles_data.get("puzzles", {})
    for puzzle_id, puzzle_state in puzzles_raw.items():
        if puzzle_id in context.puzzle_manager.puzzles:
            context.puzzle_manager.puzzles[puzzle_id].solved = puzzle_state.get(
                "solved",
                context.puzzle_manager.puzzles[puzzle_id].solved,
            )


def _restore_brain_teasers(data: Dict[str, Any], context: DeserializerContext, resources: DeserializationResources) -> None:
    if not context.brain_teaser_manager or "brain_teasers" not in data:
        return
    brain_teasers_data = data["brain_teasers"]
    definitions = resources.resolve_brain_teasers(context.brain_teaser_manager)
    restored_manager = deserialize_brain_teaser_manager(brain_teasers_data, definitions)
    if restored_manager:
        context.brain_teaser_manager.solved_teasers = restored_manager.solved_teasers.copy()
        context.brain_teaser_manager.attempts = restored_manager.attempts.copy()
        for teaser_id in restored_manager.solved_teasers:
            if teaser_id in context.brain_teaser_manager.teasers:
                context.brain_teaser_manager.teasers[teaser_id].solved = True


class MinigameDeserializer(DomainDeserializer):
    """Deserialize all minigame-related systems."""

    def deserialize(self, data: Dict[str, Any], context: DeserializerContext, resources: DeserializationResources) -> None:
        _restore_fishing(data, context, resources)
        _restore_puzzles(data, context, resources)
        _restore_brain_teasers(data, context, resources)

"""Domain-specific deserializers and registry."""

from typing import Dict, Any, Iterable, List

from .base import DeserializationResources, DeserializerContext, DomainDeserializer
from .party_deserializer import PartyDeserializer
from .player_deserializer import (
    PlayerDeserializer,
    deserialize_bestiary,
    deserialize_crafting_progress,
    deserialize_party_member,
    deserialize_skill_tree_progress,
    deserialize_stats,
)
from .progress_deserializer import (
    ProgressDeserializer,
    deserialize_challenge_dungeon_manager,
    deserialize_gambling_manager,
)
from .quest_deserializer import QuestDeserializer
from .time_weather_deserializer import TimeWeatherDeserializer
from .world_deserializer import WorldDeserializer, deserialize_world_runtime_state
from .minigame_deserializer import (
    MinigameDeserializer,
    deserialize_brain_teaser_manager,
    deserialize_puzzle_manager,
)


DEFAULT_DESERIALIZERS: List[DomainDeserializer] = [
    PlayerDeserializer(),
    PartyDeserializer(),
    WorldDeserializer(),
    QuestDeserializer(),
    TimeWeatherDeserializer(),
    MinigameDeserializer(),
    ProgressDeserializer(),
]


def run_deserializers(
    data: Dict[str, Any],
    context: DeserializerContext,
    resources: DeserializationResources,
    deserializers: Iterable[DomainDeserializer] = DEFAULT_DESERIALIZERS,
) -> None:
    """Run all registered domain deserializers in order."""
    for deserializer in deserializers:
        deserializer.deserialize(data, context, resources)


__all__ = [
    "DeserializationResources",
    "DeserializerContext",
    "DomainDeserializer",
    "run_deserializers",
    "deserialize_stats",
    "deserialize_skill_tree_progress",
    "deserialize_crafting_progress",
    "deserialize_bestiary",
    "deserialize_party_member",
    "deserialize_world_runtime_state",
    "deserialize_puzzle_manager",
    "deserialize_brain_teaser_manager",
    "deserialize_gambling_manager",
    "deserialize_challenge_dungeon_manager",
]

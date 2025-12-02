"""Quest deserialization."""

from typing import Any, Dict

from .base import DeserializationResources, DeserializerContext, DomainDeserializer


class QuestDeserializer(DomainDeserializer):
    """Deserialize quest manager state."""

    def deserialize(self, data: Dict[str, Any], context: DeserializerContext, resources: DeserializationResources) -> None:
        if context.quest_manager and "quests" in data:
            context.quest_manager.deserialize_state(data["quests"])

"""Shared interfaces and registry utilities for world trigger handlers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from core.world import Trigger
    from engine.world_scene import WorldScene


@dataclass
class TriggerContext:
    """Lightweight context passed to trigger handlers."""

    scene: "WorldScene"


class TriggerHandlerStrategy(Protocol):
    """Protocol implemented by all trigger handlers."""

    trigger_type: str

    def handle(self, trigger: "Trigger", context: TriggerContext) -> None:  # pragma: no cover - interface only
        ...


class TriggerRegistry:
    """Registry mapping trigger types to handler implementations."""

    def __init__(self) -> None:
        self._handlers: Dict[str, TriggerHandlerStrategy] = {}

    def register(self, handler: TriggerHandlerStrategy) -> None:
        self._handlers[handler.trigger_type] = handler

    def get(self, trigger_type: str) -> Optional[TriggerHandlerStrategy]:
        return self._handlers.get(trigger_type)

    def all(self) -> Dict[str, TriggerHandlerStrategy]:
        return dict(self._handlers)


__all__ = ["TriggerContext", "TriggerHandlerStrategy", "TriggerRegistry"]

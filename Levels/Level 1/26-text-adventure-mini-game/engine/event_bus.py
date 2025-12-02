"""Simple event bus for decoupled game events.

The EventBus provides a lightweight publish/subscribe mechanism that allows
systems like achievements, quests, and UI to listen for high-level game
events without tight coupling between modules.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Callable, DefaultDict, Dict, List


EventCallback = Callable[[Dict[str, Any]], None]


class EventBus:
    """Game-wide event bus for high-level domain events.

    Events are identified by a string name (e.g. ``\"enemy_killed\"``) and
    callbacks receive a single ``Dict[str, Any]`` payload. This keeps the
    interface simple and flexible while remaining type-friendly for callers.
    """

    def __init__(self) -> None:
        self._subscribers: DefaultDict[str, List[EventCallback]] = defaultdict(list)

    def subscribe(self, event_name: str, callback: EventCallback) -> None:
        """Subscribe a callback to an event.

        The callback will be invoked with a single payload dictionary whenever
        :meth:`publish` is called with the matching ``event_name``.
        """
        if callback not in self._subscribers[event_name]:
            self._subscribers[event_name].append(callback)

    def unsubscribe(self, event_name: str, callback: EventCallback) -> None:
        """Unsubscribe a callback from an event."""
        callbacks = self._subscribers.get(event_name)
        if not callbacks:
            return
        if callback in callbacks:
            callbacks.remove(callback)
        if not callbacks and event_name in self._subscribers:
            del self._subscribers[event_name]

    def publish(self, event_name: str, **payload: Any) -> None:
        """Publish an event with the given payload.

        All subscribers for ``event_name`` will be invoked in registration
        order. Exceptions from one subscriber are not caught here; callers
        should handle them at a higher level if needed.
        """
        callbacks = list(self._subscribers.get(event_name, ()))
        if not callbacks:
            return

        event_payload: Dict[str, Any] = dict(payload)
        for callback in callbacks:
            callback(event_payload)

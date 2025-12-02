"""Replay recording and playback utilities."""

import json
import os
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .logging_utils import log_warning

REPLAY_VERSION = "1.0"


@dataclass
class ReplayEvent:
    """A single replay event entry."""

    timestamp: float
    event_type: str
    payload: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ReplayLog:
    """Structured replay log containing metadata and recorded events."""

    version: str = REPLAY_VERSION
    metadata: Dict[str, Any] = field(default_factory=dict)
    events: List[ReplayEvent] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the replay log for JSON storage."""
        return {
            "version": self.version,
            "metadata": self.metadata,
            "events": [
                {"timestamp": event.timestamp, "type": event.event_type, "payload": event.payload}
                for event in self.events
            ],
        }


class ReplayRecorder:
    """Simple replay recorder that stores timestamped events in-memory."""

    def __init__(self, enabled: bool = False, metadata: Optional[Dict[str, Any]] = None):
        self.enabled = enabled
        self.log = ReplayLog(metadata=metadata or {})
        self._start_time = time.time()

    def record_event(self, event_type: str, payload: Optional[Dict[str, Any]] = None) -> None:
        """Record an event with a timestamp if recording is enabled."""
        if not self.enabled:
            return
        self.log.events.append(
            ReplayEvent(timestamp=self._elapsed(), event_type=event_type, payload=payload or {})
        )

    def record_state(self, state: Dict[str, Any]) -> None:
        """Record a snapshot of game state for debugging playback divergences."""
        self.record_event("state", state)

    def save(self, path: str) -> bool:
        """Write the replay log to disk."""
        if not self.enabled:
            return False
        try:
            with open(path, "w") as handle:
                json.dump(self.log.to_dict(), handle, indent=2)
            return True
        except Exception as exc:
            log_warning(f"Failed to save replay to {path}: {exc}")
            return False

    def _elapsed(self) -> float:
        """Return seconds since recording started."""
        return time.time() - self._start_time


class ReplayPlayer:
    """Load and iterate over a replay log."""

    def __init__(self, path: str):
        self.path = path
        self.log: Optional[ReplayLog] = None

    def load(self) -> bool:
        """Load a replay log from disk."""
        if not os.path.exists(self.path):
            log_warning(f"Replay file not found: {self.path}")
            return False

        try:
            with open(self.path, "r") as handle:
                raw = json.load(handle)
        except Exception as exc:
            log_warning(f"Failed to load replay file {self.path}: {exc}")
            return False

        events = [
            ReplayEvent(
                timestamp=entry.get("timestamp", 0.0),
                event_type=entry.get("type", "input"),
                payload=entry.get("payload", {}),
            )
            for entry in raw.get("events", [])
        ]
        self.log = ReplayLog(
            version=raw.get("version", REPLAY_VERSION),
            metadata=raw.get("metadata", {}),
            events=events,
        )
        return True

    def iter_events(self) -> List[ReplayEvent]:
        """Return a shallow copy of recorded events for playback."""
        return list(self.log.events) if self.log else []

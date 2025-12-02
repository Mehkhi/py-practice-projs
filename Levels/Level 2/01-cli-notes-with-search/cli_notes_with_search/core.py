"""Core note management logic for the CLI notes project."""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Dict, Iterable, List, Optional, Sequence
from uuid import uuid4


LOGGER = logging.getLogger(__name__)


@dataclass
class Note:
    """Data representation of a note."""

    id: str
    title: str
    content: str
    tags: List[str]
    created_at: str
    updated_at: str

    def to_dict(self) -> Dict[str, str]:
        """Serialize the note to a dictionary suitable for JSON storage."""
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "tags": self.tags,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, payload: Dict[str, object]) -> "Note":
        """Create a Note instance from serialized data."""
        tags = payload.get("tags", [])
        return cls(
            id=str(payload["id"]),
            title=str(payload.get("title", "")),
            content=str(payload.get("content", "")),
            tags=[str(tag) for tag in tags] if isinstance(tags, list) else [],
            created_at=str(payload.get("created_at", "")),
            updated_at=str(payload.get("updated_at", "")),
        )


class NoteManager:
    """Handles CRUD operations, persistence, and searching of notes."""

    def __init__(self, storage_path: Path | str, logger: Optional[logging.Logger] = None) -> None:
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._logger = logger or LOGGER
        self._notes: Dict[str, Note] = {}
        self._last_modified: Optional[int] = None
        self._load()

    @staticmethod
    def _timestamp() -> str:
        """Return an ISO-8601 timestamp with UTC timezone."""
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _normalize_tags(tags: Optional[Iterable[str]]) -> List[str]:
        """Normalize tags by lowering case and removing duplicates."""
        if not tags:
            return []
        normalized = {tag.strip().lower() for tag in tags if tag.strip()}
        return sorted(normalized)

    def _load(self) -> None:
        """Load notes from storage into memory."""
        if not self.storage_path.exists():
            self._notes = {}
            self._last_modified = None
            return

        try:
            with self.storage_path.open("r", encoding="utf-8") as handle:
                payload = json.load(handle)
        except json.JSONDecodeError as exc:
            self._logger.error("Failed to parse notes storage: %s", exc)
            self._notes = {}
            self._record_modified_time()
            return

        notes_payload = payload.get("notes") if isinstance(payload, dict) else payload
        if not isinstance(notes_payload, list):
            self._logger.error("Unexpected storage format; resetting notes.")
            self._notes = {}
            self._record_modified_time()
            return

        self._notes = {}
        for note_data in notes_payload:
            try:
                note = Note.from_dict(note_data)
            except (KeyError, TypeError, ValueError):
                self._logger.error("Skipping malformed note entry: %s", note_data)
                continue
            self._notes[note.id] = note
        self._record_modified_time()

    def _persist(self) -> None:
        """Persist notes to disk using an atomic write."""
        payload = {"notes": [note.to_dict() for note in self._notes.values()]}
        temp_path: Optional[Path] = None
        try:
            with NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                delete=False,
                dir=str(self.storage_path.parent),
            ) as temp_file:
                temp_path = Path(temp_file.name)
                json.dump(payload, temp_file, indent=2)
                temp_file.flush()
                os.fsync(temp_file.fileno())
        except OSError as exc:
            self._logger.error("Failed to persist notes: %s", exc)
            raise

        if temp_path is None:
            raise RuntimeError("Temporary file path was not created.")

        os.replace(temp_path, self.storage_path)
        self._record_modified_time()

    def _record_modified_time(self) -> None:
        """Track the storage file modification time."""
        try:
            self._last_modified = self.storage_path.stat().st_mtime_ns
        except FileNotFoundError:
            self._last_modified = None
        except OSError:
            # Ignore transient filesystem errors.
            pass

    def _refresh_if_stale(self) -> None:
        """Reload notes if the storage file changed on disk."""
        try:
            current_mtime = self.storage_path.stat().st_mtime_ns
        except FileNotFoundError:
            if self._notes:
                self._notes = {}
            self._last_modified = None
            return
        except OSError:
            return

        if self._last_modified != current_mtime:
            self._load()

    def list_notes(self, tags: Optional[Sequence[str]] = None) -> List[Note]:
        """Return notes optionally filtered by tags."""
        self._refresh_if_stale()
        if not tags:
            return sorted(self._notes.values(), key=lambda note: note.created_at)

        tag_set = {tag.lower() for tag in tags}
        return [
            note
            for note in sorted(self._notes.values(), key=lambda note: note.created_at)
            if tag_set.issubset(set(note.tags))
        ]

    def create_note(self, title: str, content: str, tags: Optional[Sequence[str]] = None) -> Note:
        """Create and persist a new note."""
        self._refresh_if_stale()
        if not title.strip():
            raise ValueError("Title cannot be empty.")
        if not content.strip():
            raise ValueError("Content cannot be empty.")

        note_id = uuid4().hex
        timestamp = self._timestamp()
        normalized_tags = self._normalize_tags(tags)

        note = Note(
            id=note_id,
            title=title.strip(),
            content=content.strip(),
            tags=normalized_tags,
            created_at=timestamp,
            updated_at=timestamp,
        )
        self._notes[note.id] = note
        self._persist()
        self._logger.info("Created note %s", note.id)
        return note

    def get_note(self, note_id: str) -> Optional[Note]:
        """Return a single note by its identifier."""
        self._refresh_if_stale()
        return self._notes.get(note_id)

    def delete_note(self, note_id: str) -> bool:
        """Delete a note with the provided identifier."""
        self._refresh_if_stale()
        if note_id not in self._notes:
            return False

        del self._notes[note_id]
        self._persist()
        self._logger.info("Deleted note %s", note_id)
        return True

    def search_notes(
        self, query: str, tags: Optional[Sequence[str]] = None
    ) -> List[Note]:
        """Return notes matching the search query and optional tags."""
        self._refresh_if_stale()
        query_lower = query.lower().strip()
        if not query_lower:
            raise ValueError("Search query cannot be empty.")

        candidates = self.list_notes(tags)
        return [
            note
            for note in candidates
            if query_lower in note.title.lower() or query_lower in note.content.lower()
        ]

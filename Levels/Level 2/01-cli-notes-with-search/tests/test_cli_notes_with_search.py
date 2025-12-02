"""Test suite for the CLI notes application."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from cli_notes_with_search.core import NoteManager
from cli_notes_with_search.main import main as cli_main


def read_storage(storage_path: Path) -> dict:
    """Load JSON payload from storage."""
    with storage_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def test_create_note_persists_data(tmp_path: Path) -> None:
    """Notes should persist to disk and expose metadata."""
    storage = tmp_path / "notes.json"
    manager = NoteManager(storage)
    note = manager.create_note("Test", "Body text", tags=["Work", "urgent"])

    payload = read_storage(storage)
    assert payload["notes"][0]["id"] == note.id
    assert note.created_at
    assert note.updated_at
    assert "urgent" in note.tags


def test_create_note_rejects_empty_fields(tmp_path: Path) -> None:
    """Creating a note requires non-empty title and content."""
    manager = NoteManager(tmp_path / "notes.json")
    with pytest.raises(ValueError):
        manager.create_note("", "content")
    with pytest.raises(ValueError):
        manager.create_note("Title", " ")


def test_list_notes_supports_tag_filtering(tmp_path: Path) -> None:
    """Listing notes can be filtered by tags."""
    manager = NoteManager(tmp_path / "notes.json")
    manager.create_note("First", "Body", tags=["work", "inbox"])
    manager.create_note("Second", "Body", tags=["personal"])

    filtered = manager.list_notes(tags=["work"])
    assert len(filtered) == 1
    assert filtered[0].title == "First"


def test_search_notes_matches_title_and_content(tmp_path: Path) -> None:
    """Search should match both title and content, case-insensitive."""
    manager = NoteManager(tmp_path / "notes.json")
    manager.create_note("Release plan", "Checklist for v1", tags=["work"])
    manager.create_note("Shopping list", "milk, bread", tags=["personal"])

    results = manager.search_notes("release")
    assert len(results) == 1
    assert results[0].title == "Release plan"

    results = manager.search_notes("milk")
    assert len(results) == 1
    assert results[0].title == "Shopping list"


def test_delete_note_removes_entry(tmp_path: Path) -> None:
    """Deleting a note removes it from storage."""
    manager = NoteManager(tmp_path / "notes.json")
    note = manager.create_note("Title", "content")
    assert manager.delete_note(note.id) is True
    assert manager.get_note(note.id) is None
    assert manager.delete_note("missing") is False


def test_notes_reload_from_disk(tmp_path: Path) -> None:
    """Notes should be restored when manager is re-instantiated."""
    storage = tmp_path / "notes.json"
    manager = NoteManager(storage)
    created = manager.create_note("Persisted", "content", tags=["tag"])

    new_manager = NoteManager(storage)
    note = new_manager.get_note(created.id)
    assert note is not None
    assert note.title == "Persisted"
    assert "tag" in note.tags


def test_cli_create_and_list(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """CLI create and list commands should work end-to-end."""
    storage = tmp_path / "notes.json"
    exit_code = cli_main(
        [
            "--store",
            str(storage),
            "create",
            "--title",
            "CLI note",
            "--content",
            "cli body",
            "--tag",
            "cli",
        ]
    )
    assert exit_code == 0

    exit_code = cli_main(["--store", str(storage), "list"])
    assert exit_code == 0

    captured = capsys.readouterr()
    assert "CLI note" in captured.out


def test_cli_view_missing_returns_error(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Viewing a missing note should set error code and stderr output."""
    storage = tmp_path / "notes.json"
    manager = NoteManager(storage)
    manager.create_note("Foo", "Bar")

    exit_code = cli_main(["--store", str(storage), "view", "missing"])
    assert exit_code == 1
    captured = capsys.readouterr()
    assert "not found" in captured.err.lower()


def test_cli_delete_with_confirmation(monkeypatch, tmp_path: Path) -> None:
    """CLI delete should respect confirmation prompts."""
    storage = tmp_path / "notes.json"
    manager = NoteManager(storage)
    note = manager.create_note("Title", "Body")

    monkeypatch.setattr("builtins.input", lambda _: "y")
    exit_code = cli_main(
        ["--store", str(storage), "delete", note.id]
    )
    assert exit_code == 0
    assert manager.get_note(note.id) is None

"""Utility helpers for rendering notes and common CLI helpers."""

from __future__ import annotations

from typing import Iterable

from .core import Note


def format_note_summary(note: Note) -> str:
    """Return a single-line summary of a note."""
    tags_display = ", ".join(note.tags) if note.tags else "-"
    return (
        f"[{note.id}] {note.title} | tags: {tags_display} | "
        f"created: {note.created_at} | updated: {note.updated_at}"
    )


def format_note_detail(note: Note) -> str:
    """Return a detailed, multi-line representation of a note."""
    lines = [
        f"ID        : {note.id}",
        f"Title     : {note.title}",
        f"Tags      : {', '.join(note.tags) if note.tags else '-'}",
        f"Created   : {note.created_at}",
        f"Updated   : {note.updated_at}",
        "Content:",
        note.content,
    ]
    return "\n".join(lines)


def join_tags(tags: Iterable[str]) -> str:
    """Join tags for display."""
    return ", ".join(sorted(tags)) if tags else "-"

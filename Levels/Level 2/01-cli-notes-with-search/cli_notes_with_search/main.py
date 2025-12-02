"""Command-line entry point for the CLI notes application."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import Iterable, Optional, Sequence

from .core import NoteManager
from .utils import format_note_detail, format_note_summary

DEFAULT_STORE = Path.home() / ".cli_notes.json"


def build_parser() -> argparse.ArgumentParser:
    """Build and return the argument parser for the CLI."""
    parser = argparse.ArgumentParser(
        prog="cli-notes",
        description="A command-line notes application with tagging and search.",
    )
    parser.add_argument(
        "--store",
        type=Path,
        default=DEFAULT_STORE,
        help=f"Path to notes storage file (default: {DEFAULT_STORE})",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        help="Logging level (e.g., INFO, DEBUG, WARNING).",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    create_parser = subparsers.add_parser("create", help="Create a new note.")
    create_parser.add_argument("--title", required=True, help="Title of the note.")
    create_parser.add_argument(
        "--content",
        help="Note body text. If omitted, content is read from stdin.",
    )
    create_parser.add_argument(
        "--content-file",
        type=Path,
        help="Path to a text file to use as note content.",
    )
    create_parser.add_argument(
        "--tag",
        action="append",
        dest="tags",
        default=[],
        help="Tag to associate with the note. May be provided multiple times.",
    )

    list_parser = subparsers.add_parser("list", help="List stored notes.")
    list_parser.add_argument(
        "--tag",
        action="append",
        dest="tags",
        default=[],
        help="Filter notes that contain all provided tags.",
    )

    view_parser = subparsers.add_parser("view", help="View a single note.")
    view_parser.add_argument("note_id", help="Identifier of the note to display.")

    delete_parser = subparsers.add_parser("delete", help="Delete a note.")
    delete_parser.add_argument("note_id", help="Identifier of the note to delete.")
    delete_parser.add_argument(
        "--yes",
        action="store_true",
        help="Skip confirmation prompt.",
    )

    search_parser = subparsers.add_parser("search", help="Search notes by text.")
    search_parser.add_argument("query", help="Text to search for in notes.")
    search_parser.add_argument(
        "--tag",
        action="append",
        dest="tags",
        default=[],
        help="Filter search results by tags.",
    )

    return parser


def configure_logging(level: str) -> None:
    """Configure logging for the CLI."""
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def resolve_content(args: argparse.Namespace) -> str:
    """Resolve the content for the create command."""
    if args.content_file:
        return args.content_file.read_text(encoding="utf-8")

    if args.content is not None:
        return args.content

    if not sys.stdin.isatty():
        return sys.stdin.read()

    raise ValueError("Content is required (pass --content, --content-file, or pipe stdin).")


def handle_list(manager: NoteManager, tags: Iterable[str]) -> int:
    """Handle the list command."""
    notes = manager.list_notes(tags=list(tags))
    if not notes:
        print("No notes found.")
        return 0

    for note in notes:
        print(format_note_summary(note))
    return 0


def handle_view(manager: NoteManager, note_id: str) -> int:
    """Handle the view command."""
    note = manager.get_note(note_id)
    if not note:
        print(f"Note {note_id} not found.", file=sys.stderr)
        return 1

    print(format_note_detail(note))
    return 0


def handle_delete(manager: NoteManager, note_id: str, confirmed: bool) -> int:
    """Handle the delete command."""
    if not confirmed:
        response = input(f"Delete note {note_id}? [y/N]: ").strip().lower()
        if response not in {"y", "yes"}:
            print("Aborted.")
            return 1

    deleted = manager.delete_note(note_id)
    if not deleted:
        print(f"Note {note_id} not found.", file=sys.stderr)
        return 1

    print(f"Deleted note {note_id}.")
    return 0


def handle_search(manager: NoteManager, query: str, tags: Iterable[str]) -> int:
    """Handle the search command."""
    try:
        results = manager.search_notes(query, tags=list(tags))
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if not results:
        print("No matching notes.")
        return 0

    for note in results:
        print(format_note_summary(note))
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Entry point for the CLI application."""
    parser = build_parser()
    args = parser.parse_args(argv)

    configure_logging(args.log_level)
    manager = NoteManager(args.store)

    if args.command == "create":
        try:
            content = resolve_content(args)
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 1
        try:
            note = manager.create_note(
                title=args.title,
                content=content,
                tags=args.tags,
            )
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 1
        print(f"Created note {note.id}.")
        return 0

    if args.command == "list":
        return handle_list(manager, args.tags)

    if args.command == "view":
        return handle_view(manager, args.note_id)

    if args.command == "delete":
        return handle_delete(manager, args.note_id, args.yes)

    if args.command == "search":
        return handle_search(manager, args.query, args.tags)

    parser.error("Unknown command.")
    return 2


if __name__ == "__main__":
    sys.exit(main())

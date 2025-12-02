# CLI Notes with Search

CLI Notes with Search is a command-line notes manager that stores notes in a JSON file, supports tagging, and provides full-text search. It is designed as a practical tool for managing small collections of notes directly from the terminal while demonstrating clean code architecture, persistence, and testing practices.

## Features

- Create, list, view, and delete notes with stable unique IDs.
- JSON storage with atomic writes to avoid data loss.
- Tag management with filtering across all commands.
- Full-text search across note titles and bodies.
- ISO-8601 timestamps for creation and updates.
- Structured logging for key operations.
- Extensive unit tests covering success paths and edge cases.

## Installation

1. **Clone the repository** (if you have not already):
   ```bash
   git clone https://github.com/your-org/your-repo.git
   cd your-repo/Level\ 2/01-cli-notes-with-search
   ```

2. **Create and activate a virtual environment** (recommended):
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   The project currently depends only on the Python standard library, so the requirements file acts as documentation.

## Usage

The CLI is exposed via the package module. From the project root:

```bash
python -m cli_notes_with_search.main [GLOBAL OPTIONS] <command> [COMMAND OPTIONS]
```

### Global Options

- `--store PATH` – Path to the JSON file that stores notes (default: `~/.cli_notes.json`).
- `--log-level LEVEL` – Logging verbosity (`INFO`, `DEBUG`, etc.). Default is `INFO`.

### Commands

- `create` – Create a note.
  ```bash
  python -m cli_notes_with_search.main create \
      --title "Release checklist" \
      --content "1. Tag release\n2. Build artefacts" \
      --tag devops --tag release
  ```
  You can also supply content via `--content-file` or by piping text to the command.

- `list` – List all notes (optionally filtered by tags).
  ```bash
  python -m cli_notes_with_search.main list --tag devops
  ```

- `view NOTE_ID` – Display the full contents of a note.
  ```bash
  python -m cli_notes_with_search.main view 9e9d70d0a23d4a0b8ced6cc2a5ddfd32
  ```

- `delete NOTE_ID` – Delete a note (prompts for confirmation unless `--yes` is provided).
  ```bash
  python -m cli_notes_with_search.main delete 9e9d70d0a23d4a0b8ced6cc2a5ddfd32 --yes
  ```

- `search QUERY` – Full-text search across titles and content, with optional tag filtering.
  ```bash
  python -m cli_notes_with_search.main search release --tag devops
  ```

## Configuration

- **Storage location**: Adjust with `--store`. Point it to a project-specific JSON file if you manage multiple collections.
- **Logging**: Set `--log-level` to `DEBUG` for troubleshooting. Logs use the standard logging system, so you can redirect output or configure handlers in a wrapper script if needed.

## Testing

The project ships with a pytest suite covering note creation, listing, searching, deletion, serialization, and CLI behaviours.

```bash
pytest
```

## Known Limitations

- Notes are stored as plain JSON without encryption. Do not store sensitive information without additional protection.
- Concurrent edits from multiple processes can lead to race conditions. Atomic writes reduce risk, but a coordination mechanism (such as file locking) would be needed for robust multi-process safety.
- The search feature is case-insensitive substring matching. Fuzzy search or stemming can be added as future enhancements.

## Project Structure

```
cli_notes_with_search/
├── __init__.py
├── core.py       # Note model and persistence logic
├── main.py       # CLI entry point
└── utils.py      # Formatting helpers
tests/
└── test_cli_notes_with_search.py
```

## License

This project is provided for educational purposes. Adapt it freely to match your workflow.

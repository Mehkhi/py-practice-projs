# AGENTS.md

Guidance for automation agents working in this repository. Mirrors `CLAUDE.md` conventions and adds search tooling notes.

## Project Overview
- Python/pygame JRPG engine with top-down exploration, turn-based combat, party/quest systems, and JSON-driven content.
- Strict Core (logic) ↔ Engine (pygame) separation; Engine may depend on Core, never the reverse.

## Environment Setup
- Always run Python via `.venv/bin/python3`; dependencies live in the bundled venv, not system Python.
- If you need tests with AI debug output: `AI_DEBUG=1 AI_PHASE_FEEDBACK=1 .venv/bin/python3 -m unittest discover -s . -p "test_*.py"`.

## Commands
- Run game: `.venv/bin/python3 text_adventure_mini_game.py`
- Run all tests: `.venv/bin/python3 -m unittest discover -s . -p "test_*.py"`
- Run single file: `.venv/bin/python3 -m unittest test_stats`
- Run specific test: `.venv/bin/python3 -m unittest test_stats.TestStats.test_is_dead_true`

## Search Tooling (mgrep)
- Use `mgrep` for all local searches instead of `rg`/`grep`.
- Describe intent in natural language: `mgrep "How are map chunks defined?"`
- Scope when helpful: `mgrep "battle loop" core`
- Limit noisy output: `mgrep -m 10 "quest reward handling"`
- Avoid vague queries like `mgrep "parser"`; be specific.

## Architecture Notes
- Core (`core/`) contains domain logic only; pygame must not appear here.
- Engine (`engine/`) handles rendering/input/scenes and can import Core.
- Scene stack pattern: `push`, `pop`, `replace` via `SceneManager`.

## Code Style
- Imports: stdlib → third-party (pygame) → local; use `TYPE_CHECKING` for type-only imports.
- Type hints on all functions; prefer `Optional`, `List`, `Dict`, `Tuple` from `typing`.
- Naming: PascalCase classes; snake_case functions/methods; `_private` helpers; UPPER_SNAKE constants.
- Data classes: use `@dataclass` with `field(default_factory=...)` for mutables.
- Error handling: check `os.path.exists()`, degrade gracefully, use `getattr()` for optional attrs.

## Testing
- Use `unittest` with descriptive names `test_<what>_<expected>`.
- Prefer testing Core logic without pygame; mock engine deps when needed.

## Common Pitfalls
- Using system Python instead of `.venv/bin/python3`.
- Importing Engine from Core (violates separation).
- Missing type hints or using mutable defaults directly.
- Breaking save format; ensure backward compatibility or add migrations.

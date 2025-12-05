# Code Review Notes

## High-Risk / Must-Verify
- **Battle phase missing handler now raises**: `BattlePhaseManager` raises `ValueError` and logs when a state has no handler; any unregistered states (including mods) will crash. Ensure all states are registered or gate the raise behind a config flag.
- **AI validation can be skipped**: `start_battle` only validates when `scene.ai_validator` is present; missing validator bypasses checks even if `ai_validation_enabled` is true. Add logging/exception or guarantee validator creation.
- **SceneManager.current now Optional**: Return type can be `None`; callers that assume a scene risk `AttributeError`. Audit callers or preserve non-None contract with logging.

## Gameplay/Balancing Changes
- **Status ticks changed**: Frozen/Stun/Confusion now apply HP/SP damage/drain and randomness via new constants. Update tests, seed randomness where needed, and re-check balance.
- **New status constants**: Added per-stack damage/drain and confusion self-hit chance; align AI/data expectations with these numbers.

## Initialization & Error Handling
- **RpgGame init refactor**: Extensive try/except; many subsystems quietly degrade to defaults. Risk of half-initialized game with later crashes. Consider surfacing critical failures.
- **Save load validation**: Load now rejects player objects missing `stats`, `inventory`, or `position`; returns False without user messaging. Ensure UI surfaces the failure or migration fills fields.
- **Replay cleanup**: `_flush_replay` always disables/clears recorder after save attempt; lifecycle differs from prior behavior.

## Rendering/Performance
- **NumPy fast paths**: Gradients/vignettes now use NumPy; `requirements.txt` adds `numpy>=1.20.0`. Verify build/install environments support it; fallback paths exist if import fails.
- **draw_rounded_panel import moved**: Module-scope import from overworld renderer; confirm no side-effecty imports during battle scene load.
- **Entity fallback sprites**: Missing assets draw colored placeholders and log debug; reduces crashes but may hide missing art—monitor logs.

## Data/Config
- **config.json newline removed**: Minor formatting change; may trigger strict format warnings.

## Tests
- Update/extend `tests/core/test_stats.py` (and related) for new status tick behaviors and randomness. Run with `.venv/bin/python3 -m pytest` from repo root.

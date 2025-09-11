# Super Calculator (Expression REPL)

Modernized, modular command-line calculator. Type expressions directly (e.g., `2+3*4`, `(2+3)/5`) and use control commands for memory and history. State can persist across runs.

## Features
- Expression input with precedence and parentheses using a safe AST evaluator
- Variables and assignment: `x = 2+3`, use `x*2`, built‑ins `ans` (last result) and `mem` (memory)
- Functions (float mode): `sqrt`, `sin`, `cos`, `tan`, `log`, `log10`, `exp`, `abs`, `round`
- Operators: `+ - * / ** % //` and parentheses, unary `+ -`
- History and memory: `hist`, `undo`, `redo`, `m+`, `m-`, `mr`
- History filters: `hist N` (last N), `hist /pattern/` (regex/substring)
- JSON persistence via `--state PATH` (persists memory, history, variables, precision, decimal mode, formatting)
- Precision formatting via `--precision N` or `precision off`
- Decimal mode (`--decimal`): uses exact decimal arithmetic; functions disabled in this mode
- Formatting options: thousands separators and scientific/engineering notation (`format ...` commands)
- Config introspection: `config` shows precision/decimal/thousands/notation

## Layout
- `main.py` — Entrypoint; parses flags and starts the REPL
- `super_calc/` — Package with:
  - `cli.py` — REPL loop, commands, printing
  - `expr.py` — Safe expression evaluator
  - `calculator.py` — Core state, history, memory, undo/redo
  - `persistence.py` — JSON save/load (backward-compatible)
  - `models.py` — `Calculation` dataclass
- `super-calc.py` — Compatibility wrapper (runs `main.py`)

## Usage
Run with main:

```bash
python3 "Levels/Level 1/01-hello-world-super-calculator/main.py" --precision 3 --state state.json
```

Or with the wrapper:

```bash
python3 "Levels/Level 1/01-hello-world-super-calculator/super-calc.py" --precision 3 --state state.json
```

At the `calc>` prompt:
- Enter expressions: `2+3*4`, `(2+3)/5`, `-3 + 2*4`, `x = 2+3`
- Use variables: `x*2`, `ans*2`, `mem/4`
- Commands summary:
  - Memory/history: `m+`, `m-`, `mr`, `undo`, `redo`, `hist`, `hist N`, `hist /pattern/`
  - Precision: `precision N`, `precision off`
  - Formatting: `format thousands on|off`, `format notation plain|scientific|engineering`
  - Help/config: `help`, `config`

### Install (optional, console script)

You can install this subproject as an editable package and use the `super-calc` entry point:

```bash
cd "Levels/Level 1/01-hello-world-super-calculator"
python3 -m pip install -e .

# Now run the CLI from anywhere
super-calc --precision 3 --state state.json
# Decimal mode example
super-calc --decimal --precision 3 --state state.json
```

### Smoke Test

After installing as above, you can run a quick smoke test to verify the entry point and core features:

```bash
# Run with a temporary state file
super-calc --precision 2 --state /tmp/supercalc_state.json <<'EOF'
2+3
hist 1
quit
EOF
```

You should see output including:

```
Result: 2+3 = 5
1) 2+3 = 5
```

## Examples
```
calc> 2+3
Result: 2+3 = 5
calc> ans*2
Result: ans*2 = 10
calc> mem
Result: mem = 0
calc> m+
Memory updated: memory = 10
calc> mem
Result: mem = 10
calc> 10/0
Result: undefined (division by zero)
calc> hist
1) 2+3 = 5
2) ans*2 = 10
```

Notes:
- `ans` is `0` before the first successful result.
- Division by zero prints an explicit message and does not update `ans` or history.
- Decimal mode disables functions; expressions still support operators and constants (`pi`, `e`).

## Limitations
- Function calls are limited to a whitelist in float mode; disabled in decimal mode.
- AST input is constrained to a safe subset (no attributes/subscripts/lambdas/comprehensions).

## Persistence Format
- JSON file includes: `memory`, `vars` (user variables), `decimal`, `format_thousands`, `format_notation`, `precision`, and a `history` array (`expr` or `op` entries).
- Loader accepts both legacy op-based entries and expression entries; preferences are optional and default safely.

## License
This project is for learning/practice. No specific license implied.

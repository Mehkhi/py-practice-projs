# Checklist — 01-hello-world-super-calculator

## Implementation Order
- [x] Command normalization and aliases (2/5)
- [x] Core operations: add, subtract, multiply, divide (1/5)
- [x] Division by zero handling (1/5)
- [x] Expression input and validation (2/5)
- [x] REPL input bar and UX (2/5)

## Tasks

- [x] Command normalization and aliases (2/5)
  - [x] Control commands have aliases (u/undo, r/redo, h/hist, q/quit/x/exit; m+/m-/mr).
  - [x] Invalid commands return `None` or a friendly message without crashing.

- [x] Core operations: add, subtract, multiply, divide (1/5)
  - [x] All four operations compute correct results for sample inputs.
  - [x] Output formatting is consistent and readable (e.g., fixed precision).

- [x] Division by zero handling (1/5)
  - [x] When denominator == 0, the program shows a clear message and does not crash.

- [x] Expression parsing and validation (2/5)
  - [x] Valid expressions evaluate with precedence and parentheses.
  - [x] Malformed expressions produce friendly errors and do not crash.
  - [x] Division by zero yields an "undefined" message and does not crash.
  - [ ] Unit tests deferred (manual verification for now).

- [x] REPL input bar and UX (2/5)
  - [x] Single prompt (`calc>`) accepts expressions and commands.
  - [x] Print one-line instructions on startup.
  - [x] Advertise variables and assignment in startup instructions (`ans`/`mem`, `name = expression`).
  - [x] Only advertise `quit` in instructions; accept `x/exit` as aliases.
  - [x] Blank input is ignored; EOF treated as `quit`.

## Bonus

- [-] Memory features (M+, M−, MR) and session history (3/5)
  - [x] Users can add to memory (M+) using the last result; friendly message if none.
  - [x] Users can subtract from memory (M−) using the last result; friendly message if none.
  - [x] Users can recall memory (MR) and see its value.
  - [x] Maintain calculation history with expression entries or (op, a, b, result).
  - [x] Print history (`hist`) in a readable, enumerated format.
  - [x] Implement undo: move last calculation from `history` to an `undone`/redo stack and update `last_result`.
  - [x] Implement redo: move last entry from `undone`/redo back to `history` and update `last_result`.
  - [x] Clear `undone`/redo stack whenever a new calculation is performed.
  - [x] Policy decided: undo/redo applies to calculations only (memory excluded).
  - [ ] Add unit tests for memory, history, undo, redo behaviors.

- [x] Persistence (optional)
  - [x] Save/restore memory and history to JSON between runs via `--state PATH`.
  - [x] Loads on start if file exists; saves on clean quit.
  - [x] Redo stack is not persisted (calculations only).
  - [x] Backward-compatible history format (supports legacy op-based entries and expr-based entries).
  - [x] Persist user variables (`vars`) in JSON and restore on load.

- [x] Expression parsing with precedence and parentheses (4/5)
  - [x] `2+3*4` evaluates to `14`, `(2+3)*4` evaluates to `20`.
  - [x] Malformed expressions produce friendly errors and do not crash.

- [ ] Configurable precision and modes via CLI flags (2/5)
  - [x] `--precision N` formats results accordingly.
    - Note: trims trailing zeros and trailing dot; avoids printing "-0".
  - [x] All required features continue to work with flags applied.

## Polish

- [x] Refactor core math into pure functions (`add`, `sub`, `mul`, `div`).
- [x] Consistent result formatting (e.g., trim float noise or fixed precision).
- [x] Align alias help: accept `x/exit` but only advertise `quit` in prompts.
- [x] Remove odd constructs (e.g., `(print)(...)`); keep style consistent.
- [x] Modular OO refactor into package (`super_calc/`) with `main.py`; keep `super-calc.py` wrapper for compatibility.

---

## Planned Enhancements (with concrete steps)

Note: Tests are deferred for this project; steps focus on implementation details and pseudocode.

- [x] 1. Variables and Assignment (name = expression)
  - [x] 1.1 `Calculator`: add `self.vars: dict[str, float] = {}` and helpers
    - [x] 1.1.1 `def set_var(self, name: str, value: float): self.vars[name.lower()] = float(value)`
    - [x] 1.1.2 `def get_symbols(self): return {"ans": 0.0 if self.last_result is None else float(self.last_result), "mem": float(self.memory), **self.vars}`
  - [x] 1.2 `StateStore.save/load`: persist variables
    - [x] 1.2.1 Save: include `"vars": calc.vars` in JSON
    - [x] 1.2.2 Load: `vars_map = {k.lower(): float(v) for k, v in data.get("vars", {}).items()}` then assign to `calc.vars = vars_map`
  - [x] 1.3 `SuperCalcCLI.run`: detect assignment lines before command/expression handling
    - [x] 1.3.1 Pseudocode:
      - `if '=' in line and re.match(r'^[A-Za-z_][A-Za-z0-9_]*\s*='):`
      - `name, rhs = line.split('=', 1)`; `name=name.strip()`; `rhs=rhs.strip()`
      - `value = evaluate(rhs, symbols=self.calc.get_symbols())`
      - `self.calc.set_var(name, value)`
      - Print: `Assigned: name = <formatted value>`
      - Do not add to history by default (optional: record as `Calculation(expr=f"{name}={rhs}", result=value)`).
  - [x] 1.4 Use variables in expressions (post-assignment)
    - [x] 1.4.1 In `super_calc/cli.py`, during non-assignment evaluation, replace local symbol map with `self.calc.get_symbols()`
      - Before: `symbols = {"ans": ..., "mem": ...}`
      - After: `symbols = self.calc.get_symbols()`
    - [x] 1.4.2 Verify: `x=2+3` then `x*2` evaluates to `10` without altering history for the assignment itself.
  - [x] 1.5 Prevent assigning to reserved names
    - [x] 1.5.1 In `super_calc/cli.py` assignment branch, add guard: `if name.lower() in ("ans","mem"): print("Cannot assign to reserved name 'ans' or 'mem'."); continue`
    - [x] 1.5.2 Rationale: keep `ans` and `mem` semantics consistent; avoid confusing shadowing.
  - [x] 1.6 Optional: Reserved identifiers override user vars
    - [x] 1.6.1 In `Calculator.get_symbols()`, build dict so reserved keys win: `return {**self.vars, "ans": ..., "mem": ...}` (place reserved last)
    - [x] 1.6.2 This sanitizes any legacy files where `vars` may contain `ans`/`mem` keys.

- [ ] 2. Math Functions and Constants (whitelist)
  - [x] 2.1 `super_calc/expr.py`: add whitelists
    - [x] 2.1.1 `FUNCS = {"sqrt": math.sqrt, "sin": math.sin, "cos": math.cos, "tan": math.tan, "log": math.log, "log10": math.log10, "exp": math.exp, "abs": abs, "round": round}`
    - [x] 2.1.2 `CONSTS = {"pi": math.pi, "e": math.e}`
  - [x] 2.2 Evaluator: support `ast.Call`
    - [x] 2.2.1 Pseudocode:
      - if `isinstance(node, ast.Call)`:
        - ensure `isinstance(node.func, ast.Name)`
        - `fname = node.func.id.lower()`; assert `fname in FUNCS`
        - forbid `node.keywords`, `starargs`, `kwargs`
        - eval `args = [eval_node(arg) for arg in node.args]`
        - special-case `round`: allow 1 or 2 args
        - return `float(FUNCS[fname](*args))`
    - [x] 2.2.2 Coerce `round` ndigits arg to int
      - In `expr.py` Call handling: if `fname == 'round' and len(args) == 2`, cast `args[1] = int(args[1])` before calling to match Python's signature.
  - [x] 2.3 Evaluator: support `ast.Name` lookup in `CONSTS` and `symbols` (vars/ans/mem)
    - [x] 2.3.1 Order: first `symbols`, then `CONSTS`; else raise `ValueError("Unknown identifier")`
  - [x] 2.4 CLI: update help text to list supported functions/constants.

- [x] 3. Additional Operators (** % //)
  - [x] 3.1 `expr.py` `BinOp` handling:
    - [x] 3.1.1 `ast.Pow`: `return left ** right`
    - [x] 3.1.2 `ast.Mod`: if `right == 0: raise ZeroDivisionError`; else `left % right`
    - [x] 3.1.3 `ast.FloorDiv`: if `right == 0: raise ZeroDivisionError`; else `left // right`

  - [x] 4. Help Command
    - [x] 4.1 `cli.py`: extend aliases: `{"help": "help", "?": "help"}`
  - [x] 4.2 Implement `print_help()`
      - [x] 4.2.1 Print operators: `+ - * / ** % //` and parentheses, unary `+ -`
      - [x] 4.2.2 Print variables: `ans`, `mem`, and user variables
      - [x] 4.2.3 Print functions/constants from evaluator (read from `FUNCS`/`CONSTS`)
      - [x] 4.2.4 Print commands: `m+ m- mr undo redo hist [N|/pattern/] precision N clear [all|hist|mem|vars] help quit`
      - [x] 4.2.5 Include assignment syntax and examples: `name = expression` (e.g., `x = 2+3`, then `x*2`)
      - [x] 4.2.6 Show precision variants explicitly: `precision N | precision off`
      - [x] 4.2.7 Align help with implemented features
        - If 9.x (history filtering) is not implemented yet, hide `/pattern/` hint.
        - After completing 9.x, re-add the filter syntax to help.
      - [x] 4.2.8 Add format commands to Help
        - Include: `format thousands on|off` and `format notation plain|scientific|engineering` in Commands.
      - [x] 4.2.9 Add `config` command to Help
        - Include: `config` (or `config show`) to display current settings: precision (or off), decimal mode (on/off), thousands (on/off), notation (plain/scientific/engineering).
      - [x] 4.2.10 Add short usage examples to Help (polish)
        - Examples: `hist 5`, `hist /add/`, `precision off`, `format notation scientific`, `x = 2+3`, `ans*2`.
    - [x] 4.3 Handle in `run()`: if `cmd == "help"`: call `print_help()` and `continue`

- [x] 5. Config Commands (precision, clear)
  - [x] 5.1 `cli.py`: parse on plain input (before expression eval)
    - [x] 5.1.1 `precision N`:
      - parse: `m = re.match(r'^precision\s+(\d+)$', line, re.I)`; set `self.precision = int(m.group(1))`; print confirmation
    - [x] 5.1.2 `clear` variants:
      - `clear hist`: `self.calc.history.clear(); self.calc.redo_stack.clear(); print('History cleared')`
      - `clear mem`: `self.calc.memory = 0.0; print('Memory cleared')`
      - `clear vars`: `self.calc.vars.clear(); print('Variables cleared')`
      - `clear all`: do all above and `self.calc.last_result = None`; print confirmation
    - [x] 5.1.3 `precision off` (disable fixed formatting)
      - In `cli.py`, before expression eval, match `^\s*precision\s+(off|none)\s*$` (case-insensitive): set `self.precision = None`; print `"Precision turned off"`.
      - Update help text (optional) to show `precision N | precision off` once implemented.
    - [x] 5.1.4 Clamp precision range
      - When handling `precision N`, validate `0 <= N <= 12`; if out of range, either clamp to nearest bound or reject with a friendly message.
      - Example (reject): `print("Precision must be between 0 and 12")` and do not change precision.
    - [x] 5.1.5 Friendly usage for invalid precision
      - If `precision` input does not match either digits or `off/none`, print: `"Usage: precision N (0-12) or precision off"` and continue without changing precision.
    - [x] 5.1.6 Persist precision across sessions (optional)
      - Save current `precision` (or `None` when off) to state JSON and restore on load; reflect restored value in `config` output.

- [x] 6. Readline History (optional but quick win)
  - [x] 6.1 `cli.py`: in `__init__`, attempt to import `readline`; if available:
    - [x] 6.1.1 Bind history file: `hist = os.path.join(os.path.expanduser('~'), '.super_calc_history')`
    - [x] 6.1.2 Try `readline.read_history_file(hist)`; on exit save with `readline.write_history_file(hist)`
    - [x] 6.1.3 Guard with try/except so it remains optional

- [x] 7. Decimal Mode (optional)
  - [x] 7.1 `main.py`: add `--decimal` flag (bool)
  - [x] 7.2 `expr.py`: accept backend mode; when decimal mode:
    - [x] 7.2.1 Parse numeric literals into `Decimal` via `Decimal(str(node.value))`
    - [x] 7.2.2 Implement ops `+ - * / ** % //` using Decimal
    - [x] 7.2.3 Disallow functions in decimal mode (raise `ValueError('functions unavailable in decimal mode')`) for first cut
  - [x] 7.3 `cli.py`: propagate mode to evaluator; update help text
  - [x] 7.4 Decimal mode polish
    - [x] 7.4.1 Startup banner alignment
      - In `cli.py` startup instructions, when `decimal_mode` is ON, replace the functions line with `Functions: disabled in decimal mode` to match help.
    - [x] 7.4.2 Targeted error message for functions in decimal mode
      - When `decimal_mode` is ON and an expression triggers the functions-disabled ValueError, print `"Functions are disabled in decimal mode."` instead of the generic malformed message.
  - [x] 7.5 Persist decimal mode
    - [x] Save `decimal_mode` to state JSON and restore on load.
    - [x] Ensure startup banner and Help reflect the restored mode before any commands run.

- [x] 8. Output Formatting Options (optional)
  - [x] 8.1 `cli.py`: extend formatter to support
    - [x] 8.1.1 Thousands separators: `f"{value:,.{prec}f}"` when enabled
    - [x] 8.1.2 Scientific/engineering notation modes
  - [x] 8.2 Add command: `format thousands on|off`, `format notation plain|scientific|engineering`
  - [x] 8.3 Persist formatting preferences
    - [x] Save `format_thousands` and `format_notation` to state JSON and restore on load.
    - [x] Verify restored settings affect output immediately after startup.
  - [x] 8.4 Show current configuration (optional)
    - [x] Add `config` command to print: precision (or off), decimal mode (on/off), thousands (on/off), notation (plain/scientific/engineering).

- [x] 9. History Filtering
  - [x] 9.1 `cli.py`: enhance `hist` command syntax
    - [x] 9.1.1 `hist 10` -> show last 10 entries
    - [x] 9.1.2 `hist /pattern/` -> case-insensitive substring or regex match on `expr` or `op`
    - [x] 9.1.3 Update help content to include filter usage once implemented
    - [x] 9.1.4 Friendly usage for invalid N (optional)
      - If `hist N` is used with `N <= 0`, print `"Usage: hist N (N>0)"` instead of `"History is empty."`.
  - [x] 9.2 Implementation sketch:
    - [x] 9.2.1 if token is digit: `entries = history[-n:]`
    - [x] 9.2.2 if token matches `/.*?/`: compile regex and filter

- [x] 10. Evaluator Hardening (with calls enabled)
  - [x] 10.1 In `expr.py`, centralize allowed node types set: `{Expression, Name, Constant/Num, BinOp, UnaryOp, Call}`
  - [x] 10.2 Before evaluation, recursively walk the AST and raise on any disallowed node (`Attribute`, `Subscript`, `Dict`, `List`, `Tuple`, `Lambda`, `Comprehension`, etc.)
  - [x] 10.3 Ensure `Call` only with `Name` and positional args; zero keywords

- [x] 11. Better Error Diagnostics
  - [x] 11.1 In `cli.py` around `evaluate(...)`:
    - [x] Catch `SyntaxError as e`; print the line and a caret under `e.offset` if present
    - [x] Example:
      - Input: `2+*3`
      - Output:
        - `Syntax error`
        - `  2+*3`
        - `    ^`
  - [x] 11.2 Improve generic error guidance
    - [x] When catching generic errors in expression eval, mention supported constructs:
      - Update message to: `"Malformed expression. Use numbers/variables (ans, mem, user vars), functions, + - * / ** % //, and parentheses."`
    - [x] Optionally differentiate common cases (unknown identifier vs unsupported operator) for clearer feedback.
  - [x] 11.3 Targeted function arity messages (polish)
    - Detect common wrong-arity cases (e.g., `round(x, y, z)`), and print: `"round expects 1 or 2 arguments."` instead of the generic message.

- [x] 12. Packaging (optional)
  - [x] 12.1 Add `pyproject.toml` with console script entry: `super-calc = main:main`
  - [x] 12.2 `README.md`: add install/usage section for the entry point
  - [x] 12.3 Smoke test instructions (polish)
    - Show `pip install -e .` and `super-calc --precision 2` working locally.
  - [x] 12.4 Metadata polish (polish)
    - Fill in `project.name`, `version`, `description`, `readme`, and Python version in `pyproject.toml`.
  - [x] 12.5 Add classifiers/license/keywords (polish)
    - Add Trove classifiers (e.g., Programming Language :: Python :: 3), `license` and `keywords` to `pyproject.toml`.

- [x] 13. Documentation Updates
  - [x] 13.1 Update `README.md` and `SPEC.md` to include:
    - [x] Variables/assignment, functions/constants, new operators
    - [x] Help/precision/clear/history filtering commands
    - [x] Decimal mode and formatting options, if enabled
  - [x] 13.2 Document `config` command and persisted preferences (decimal, precision, formatting)

--

## Additional Polish

- [x] 14. Code hygiene and cleanup
  - [x] 14.1 Remove unused legacy helpers
    - Identify and delete unused `format_number` (CLI uses `_fmt`), and any other dead code.
    - [x] Removed `format_number` from `super_calc/cli.py`.
  - [x] 14.2 Inline comments and docstrings
    - Add or refine short docstrings where missing for new commands (`config`, `format`), if helpful.
  - [x] 14.3 Consistent message style
    - Normalize punctuation/capitalization across messages (periods at end, consistent casing) for a clean UX.

---

## Planned Enhancements (continued)

- [ ] 15. Extract Formatter (no behavior change)
  - [ ] 15.1 File:super_calc/cli/formatter.py — introduce formatter module
    - [ ] 15.1.1 Add `@dataclass FormatOptions(precision: Optional[int], thousands: bool, notation: str)`
    - [ ] 15.1.2 Add `def fmt(value: float | None, opts: FormatOptions) -> str` (move logic from `SuperCalcCLI._fmt`)
    - [ ] 15.1.3 Pseudocode:
      - if value is None -> return "undefined"
      - val = float(value); use opts.notation: plain|scientific|engineering
      - apply precision trimming and thousands separators as in current `_fmt`
  - [ ] 15.2 File:super_calc/cli.py — adopt formatter via thin adapter
    - [ ] 15.2.1 Add import: `from .cli.formatter import FormatOptions, fmt as format_number`
    - [ ] 15.2.2 Add `self._fmt_opts = FormatOptions(self.precision, self.format_thousands, self.format_notation)` in `__init__`
    - [ ] 15.2.3 Replace body of `_fmt(self, value)` with `return format_number(value, self._fmt_opts)`
    - [ ] 15.2.4 Pseudocode:
      - Keep fields in sync: whenever precision/thousands/notation change, update `self._fmt_opts`
  - [ ] 15.3 File:super_calc/cli.py — sync options when commands run
    - [ ] 15.3.1 In `precision` handler: after updating `self.precision`, set `self._fmt_opts.precision = self.precision`
    - [ ] 15.3.2 In `format thousands` handler: set `self._fmt_opts.thousands = self.format_thousands`
    - [ ] 15.3.3 In `format notation` handler: set `self._fmt_opts.notation = self.format_notation`

- [ ] 16. Extract History View (no behavior change)
  - [ ] 16.1 File:super_calc/cli/history_view.py — add rendering + filtering helpers
    - [ ] 16.1.1 Add `def render_history(entries: list[Calculation], fmt: Callable[[float|None], str]) -> list[str]`
    - [ ] 16.1.2 Add `def filter_history(entries, token: str) -> list[Calculation]` (support N and `/pattern/`)
    - [ ] 16.1.3 Pseudocode:
      - render: enumerate; if entry.expr -> "{i}) {expr} = {fmt(result)}" else op form
      - filter: if token.isdigit() -> slice; elif `/.../` -> regex search on expr/op
  - [ ] 16.2 File:super_calc/cli.py — delegate history
    - [ ] 16.2.1 Replace `print_history()` body to call `render_history` and print each line
    - [ ] 16.2.2 In `hist` command with token, use `filter_history` then `render_history`

- [ ] 17. Command Registry (no behavior change)
  - [ ] 17.1 File:super_calc/cli/commands.py — registry and decorator
    - [ ] 17.1.1 Add `@dataclass Command(name, aliases, usage, handler)`
    - [ ] 17.1.2 Add `REGISTRY: dict[str, Command]` and `ALIASES: dict[str, str]`
    - [ ] 17.1.3 Add `def command(name: str, aliases: list[str], usage: str)` decorator to register handlers
    - [ ] 17.1.4 Pseudocode:
      - handler signature: `(cli: SuperCalcCLI, line: str) -> None`
      - register canonical name + aliases; normalize lowercased keys
  - [ ] 17.2 File:super_calc/cli/help_text.py — generate help from registry
    - [ ] 17.2.1 Add `def render_help(commands: Iterable[Command], funcs: Iterable[str], consts: Iterable[str], vars: Iterable[str], decimal_mode: bool) -> list[str]`
    - [ ] 17.2.2 Pseudocode:
      - Print operators, variables, functions/consts, commands with usages; respect decimal mode
  - [ ] 17.3 File:super_calc/cli.py — route through registry
    - [ ] 17.3.1 Replace `ALIASES` usage with `commands.ALIASES` (keep existing mapping for compatibility initially)
    - [ ] 17.3.2 Add a dispatch method: look up canonical name and call handler
    - [ ] 17.3.3 Pseudocode:
      - `cmd = commands.ALIASES.get(token)`; if handler exists -> handler(self, line)
  - [ ] 17.4 Move commands incrementally
    - [ ] 17.4.1 File:super_calc/cli/commands.py — add `help` handler (calls help_text)
    - [ ] 17.4.2 File:super_calc/cli/commands.py — add `config` handler
    - [ ] 17.4.3 File:super_calc/cli/commands.py — add `hist` handler (uses history_view)
    - [ ] 17.4.4 File:super_calc/cli/commands.py — add memory handlers: `m+`, `m-`, `mr`
    - [ ] 17.4.5 File:super_calc/cli/commands.py — add `undo` and `redo` handlers
    - [ ] 17.4.6 File:super_calc/cli/commands.py — add `precision` handler
    - [ ] 17.4.7 File:super_calc/cli/commands.py — add `format` handler (thousands/notation)
    - [ ] 17.4.8 File:super_calc/cli/commands.py — add `quit` handler (save state if configured)

- [ ] 18. Evaluator Abstraction (no behavior change)
  - [ ] 18.1 File:super_calc/eval/base.py — protocol and factory
    - [ ] 18.1.1 Add `Protocol Evaluator` with `evaluate(expr: str, symbols: dict[str,float]) -> float` and `supports_functions: bool`
    - [ ] 18.1.2 Add `def make_evaluator(decimal: bool) -> Evaluator`
  - [ ] 18.2 File:super_calc/eval/float_eval.py — thin wrapper around current evaluator
    - [ ] 18.2.1 Implement `FloatEvaluator` using `expr.evaluate(..., decimal=False)`
  - [ ] 18.3 File:super_calc/eval/decimal_eval.py — thin wrapper for decimal mode
    - [ ] 18.3.1 Implement `DecimalEvaluator` using `expr.evaluate(..., decimal=True)`
  - [ ] 18.4 File:super_calc/cli.py — use abstraction
    - [ ] 18.4.1 In `__init__`, `self.evaluator = make_evaluator(self.decimal_mode)`
    - [ ] 18.4.2 In expression/assignment evaluation, call `self.evaluator.evaluate(...)`
    - [ ] 18.4.3 When decimal mode toggles (if ever), rebuild evaluator

- [ ] 19. Function/Constant Registry (centralized specs)
  - [ ] 19.1 File:super_calc/eval/functions.py — define spec and registries
    - [ ] 19.1.1 Add `@dataclass FunctionSpec(name: str, fn, arity: tuple[int,...], decimal_ok: bool, doc: str)`
    - [ ] 19.1.2 Add `FUNCS: dict[str, FunctionSpec]` and `CONSTS: dict[str, float]`
    - [ ] 19.1.3 Pseudocode: populate with existing functions; `round` has arity (1,2), `decimal_ok=False`
  - [ ] 19.2 File:super_calc/expr.py — consume registry
    - [ ] 19.2.1 Replace inline `FUNCS`/`CONSTS` with imports from `eval.functions`
    - [ ] 19.2.2 Replace inline `arity` map with `spec.arity`; enforce `round` ndigits int
    - [ ] 19.2.3 Keep behavior identical (same errors/messages)
  - [ ] 19.3 File:super_calc/cli/help_text.py — list functions/constants from registry
    - [ ] 19.3.1 If decimal mode, indicate functions disabled; else show names

- [ ] 20. Micro-optimizations (no behavior change)
  - [ ] 20.1 File:super_calc/expr.py — cache parsed ASTs
    - [ ] 20.1.1 Add `parse_expr(expr: str) -> ast.AST` with `@lru_cache(maxsize=512)`
    - [ ] 20.1.2 Use `parse_expr` inside `evaluate` instead of `ast.parse`
  - [ ] 20.2 File:super_calc/expr.py — hoist constants
    - [ ] 20.2.1 Move `allowed_nodes` construction to module level once
    - [ ] 20.2.2 Reuse across evaluations
  - [ ] 20.3 File:super_calc/cli.py — precompile regexes
    - [ ] 20.3.1 Compile `hist` (`^\s*hist(\s+(\d+|/.+/))?\s*$`), `precision`, and `format` patterns at module import
    - [ ] 20.3.2 Replace `re.match` calls with compiled patterns
  - [ ] 20.4 File:super_calc/expr.py — avoid repeated `.lower()`
    - [ ] 20.4.1 Ensure symbol keys are pre-lowered; treat identifier lowering once per lookup

- [ ] 21. Persistence State Object + Schema Version
  - [ ] 21.1 File:super_calc/models.py — add `@dataclass State(...)` (memory, vars, decimal, formatting, precision, history)
  - [ ] 21.2 File:super_calc/persistence.py — read/write `State` and include `schema_version` top-level field
  - [ ] 21.3 File:super_calc/persistence.py — maintain backward compatibility (accept old shape; default missing fields)
  - [ ] 21.4 File:README.md — update Persistence Format section to mention `schema_version` (post-implementation)

- [ ] 22. Packaging: include new subpackages
  - [ ] 22.1 File:pyproject.toml — add packages `super_calc.cli`, `super_calc.eval`, `super_calc.core` (if created), `super_calc.persistence`
  - [ ] 22.2 File:super_calc/__init__.py — re-export new public APIs (if any) while keeping current exports stable
  - [ ] 22.3 Ensure editable install still exposes `super-calc` entrypoint

- [ ] 23. CLI Wrapper forwards `--decimal`
  - [ ] 23.1 File:super-calc.py — pass `decimal=args.decimal` to `main(...)`
  - [ ] 23.2 Verify wrapper parity with `main.py` for decimal mode

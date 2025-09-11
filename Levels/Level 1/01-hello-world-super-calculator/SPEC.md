## 1. 1. Hello World & Super-Calculator

> Updated for the expression‑driven REPL UI and modular package split.

### Overview & Core Skills

**What you’re building:** A modular, expression‑driven CLI calculator. Users type arithmetic expressions directly (e.g., `2+3*4`, `(2+3)/5`) and can issue control commands (`m+`, `m-`, `mr`, `undo`, `redo`, `hist`, `help`, `config`, `quit`). State (memory/history) and user preferences can persist across runs.

**Core skills:** Expression parsing and validation, defensive programming, separation of concerns (CLI vs. logic vs. persistence), simple JSON persistence, modular OO design, packaging.


### Required Features

- **Expression input (REPL) and validation** — **Difficulty 2/5**
  - **What it teaches:**
    - Building a small REPL and interpreting inputs.
    - Using a safe AST subset to validate and evaluate math expressions.
    - Clear feedback for malformed expressions without crashing.
  - **Acceptance criteria:**
    - Valid expressions evaluate with correct precedence and parentheses.
    - Malformed expressions show a friendly error and do not crash.
    - Blank input is ignored; EOF exits cleanly.
- **Core operations and operators** — **Difficulty 1/5**
  - **What it teaches:**
    - Mapping operations to functions for clarity and testability.
    - Floating‑point behavior and rounding considerations.
    - Simple functional design (pure functions for arithmetic).
  - **Acceptance criteria:**
    - Operators `+ - * / ** % //` compute correct results for sample inputs.
    - Output formatting is consistent and readable (e.g., fixed precision).
- **Division by zero handling** — **Difficulty 1/5**
  - **What it teaches:**
    - Guard clauses for exceptional cases (preventing runtime errors).
    - Separation of concerns: validation vs. computation vs. presentation.
    - User‑friendly error messages tied to the invalid operation.
  - **Acceptance criteria:**
    - When denominator == 0, the program shows a clear message and does not crash.
    - Result is treated as undefined; history/last result not updated.
- **Command normalization and aliases** — **Difficulty 2/5**
  - **What it teaches:**
    - User experience via flexible inputs for control commands.
    - Dictionary‑based dispatch and normalization (`strip()`, `lower()`).
    - Defensive programming: handling `None` and empty tokens.
  - **Acceptance criteria:**
    - Control commands have aliases (e.g., `u/undo`, `r/redo`, `h/hist`, `q/quit/x/exit`, `m+`, `m-`, `mr`).
    - Invalid commands return `None` or a friendly message without crashing.

### Bonus Features (Implemented)

- **Memory features (M+, M−, MR) and session history** — **Difficulty 3/5**
  - **What it teaches:**
    - Designing internal state (calculator memory/history) cleanly.
    - Serialization to JSON for persistence across sessions.
    - Command patterns that enable undo/redo semantics.
  - **Acceptance criteria:**
    - Users can add to memory, subtract from memory, and recall memory.
    - Optionally, undo/redo the last operation and print history.
- **Expression parsing with precedence and parentheses** — **Difficulty 4/5**
  - **What it teaches:**
    - Using Python's `ast` to safely evaluate a restricted grammar.
    - Operator precedence/associativity; clear errors for invalid syntax.
    - Keeping the evaluator pure and easy to isolate.
  - **Acceptance criteria:**
    - `2+3*4` evaluates to `14`, `(2+3)*4` evaluates to `20`.
    - Malformed expressions produce friendly errors and do not crash.
- **Configurable precision and modes via CLI flags** — **Difficulty 2/5**
  - **What it teaches:**
    - Command‑line UX with `argparse` and good `--help` messages.
    - Separating configuration (precision) from business logic.
    - Basic packaging considerations (entry points).
  - **Acceptance criteria:**
    - `--precision N` formats results accordingly; `precision off` disables fixed formatting.
    - Decimal mode (`--decimal`) uses exact decimal arithmetic; functions disabled in this mode.
    - Formatting options: thousands separators and scientific/engineering notation via `format` commands.
    - All features continue to work with flags applied.


**Current Status & Completion Criteria (this build)**  
- All required and listed bonus features above are implemented and manually verified via the REPL.  
- Unit tests are deferred for this iteration.  
- The code is split into a modular package (`super_calc/`) with a `main.py` entrypoint and a `super-calc.py` wrapper.  
- CLI flags supported: `--precision N`, `--state PATH`.  
- History persistence is backward‑compatible (supports legacy op‑based and new expression entries).  

Usage
- Preferred: `python3 Levels/Level\ 1/01-hello-world-super-calculator/main.py --precision 4 --state state.json`  
- Wrapper: `python3 Levels/Level\ 1/01-hello-world-super-calculator/super-calc.py --precision 4 --state state.json`  
- Optional install: `pip install -e Levels/Level\ 1/01-hello-world-super-calculator` then `super-calc --precision 4 --state state.json`  
- At the `calc>` prompt: type expressions or commands: memory/history (`m+`, `m-`, `mr`, `undo`, `redo`, `hist`, `hist N`, `hist /pattern/`), precision (`precision N`, `precision off`), formatting (`format thousands on|off`, `format notation plain|scientific|engineering`), and introspection (`help`, `config`).

---

## 2. What you build: Print text, read user input, perform + − × ÷ and show results.

### Overview & Core Skills

**What you’re building:** A small but complete CLI application focusing on clean input handling, core logic, and simple persistence.

**Core skills:** CLI parsing, functions, tests, JSON/CSV I/O.


### Required Features

- **Clear CLI and input validation** — **Difficulty 1/5**
  - **What it teaches:**
    - argparse
    - Defensive coding
  - **Acceptance criteria:**
    - Good --help; rejects invalid input
- **Core logic implemented cleanly** — **Difficulty 2/5**
  - **What it teaches:**
    - Functions
    - Tests
  - **Acceptance criteria:**
    - Happy paths covered by tests
- **Persistence if applicable** — **Difficulty 2/5**
  - **What it teaches:**
    - JSON/CSV I/O
  - **Acceptance criteria:**
    - Data survives restart
- **Basic logging** — **Difficulty 1/5**
  - **What it teaches:**
    - logging module
  - **Acceptance criteria:**
    - INFO/ERROR logs present

### Bonus Features

- **Config file support** — **Difficulty 2/5**
  - **What it teaches:**
    - YAML/JSON config
  - **Acceptance criteria:**
    - Config overrides CLI defaults
- **Packaging** — **Difficulty 2/5**
  - **What it teaches:**
    - pyproject.toml
  - **Acceptance criteria:**
    - Installable with entry point
- **Type hints & mypy** — **Difficulty 2/5**
  - **What it teaches:**
    - Typing
  - **Acceptance criteria:**
    - mypy passes or justified ignores


**Requirements for Project Completion**  
- All required features implemented and demonstrated.  
- At least **5 unit tests** (happy paths + edge cases).  
- A clear **README** with setup steps, usage examples, and limitations.  
- Code formatted with **black** and linted with **ruff/flake8**.  
- Public functions include **type hints**; `mypy` passes or deviations are documented.  

---

## 3. Skills: print(), input(), int/float, operators, functions, f-strings.

### Overview & Core Skills

**What you’re building:** A small but complete CLI application focusing on clean input handling, core logic, and simple persistence.

**Core skills:** CLI parsing, functions, tests, JSON/CSV I/O.


### Required Features

- **Clear CLI and input validation** — **Difficulty 1/5**
  - **What it teaches:**
    - argparse
    - Defensive coding
  - **Acceptance criteria:**
    - Good --help; rejects invalid input
- **Core logic implemented cleanly** — **Difficulty 2/5**
  - **What it teaches:**
    - Functions
    - Tests
  - **Acceptance criteria:**
    - Happy paths covered by tests
- **Persistence if applicable** — **Difficulty 2/5**
  - **What it teaches:**
    - JSON/CSV I/O
  - **Acceptance criteria:**
    - Data survives restart
- **Basic logging** — **Difficulty 1/5**
  - **What it teaches:**
    - logging module
  - **Acceptance criteria:**
    - INFO/ERROR logs present

### Bonus Features

- **Config file support** — **Difficulty 2/5**
  - **What it teaches:**
    - YAML/JSON config
  - **Acceptance criteria:**
    - Config overrides CLI defaults
- **Packaging** — **Difficulty 2/5**
  - **What it teaches:**
    - pyproject.toml
  - **Acceptance criteria:**
    - Installable with entry point
- **Type hints & mypy** — **Difficulty 2/5**
  - **What it teaches:**
    - Typing
  - **Acceptance criteria:**
    - mypy passes or justified ignores


**Requirements for Project Completion**  
- All required features implemented and demonstrated.  
- At least **5 unit tests** (happy paths + edge cases).  
- A clear **README** with setup steps, usage examples, and limitations.  
- Code formatted with **black** and linted with **ruff/flake8**.  
- Public functions include **type hints**; `mypy` passes or deviations are documented.  

---

## 4. Milestones: Handle invalid input; support order of operations; add unit tests with assert.

### Overview & Core Skills

**What you’re building:** A small but complete CLI application focusing on clean input handling, core logic, and simple persistence.

**Core skills:** CLI parsing, functions, tests, JSON/CSV I/O.


### Required Features

- **Menu and unit selection** — **Difficulty 1/5**
  - **What it teaches:**
    - Menus
    - Input parsing
    - Validation
  - **Acceptance criteria:**
    - Invalid entries re‑prompt
    - Help text visible
- **Core conversion logic** — **Difficulty 2/5**
  - **What it teaches:**
    - Factor tables and dictionary lookups.
    - Avoiding cumulative error via base units.
    - Extensible design for adding new units.
  - **Acceptance criteria:**
    - Converts between at least 4 unit pairs correctly.
    - Unsupported pairs produce helpful errors.
- **Rounding and formatting** — **Difficulty 1/5**
  - **What it teaches:**
    - Precision and rounding
    - Locale‑aware formatting (concepts)
  - **Acceptance criteria:**
    - Fixed decimal places optional
    - Consistent output
- **Batch conversions from file** — **Difficulty 2/5**
  - **What it teaches:**
    - CSV I/O
    - Error accumulation handling
  - **Acceptance criteria:**
    - Process file and produce output CSV

### Bonus Features

- **Support chained conversions** — **Difficulty 3/5**
  - **What it teaches:**
    - Graph of conversions
    - Path finding (simple)
  - **Acceptance criteria:**
    - m → ft → in works with rounding
- **Custom conversion factors file** — **Difficulty 2/5**
  - **What it teaches:**
    - Config files (YAML/JSON)
    - Validation of config
  - **Acceptance criteria:**
    - Schema‑validated factors are loaded
- **ASCII table/plot** — **Difficulty 2/5**
  - **What it teaches:**
    - Text tables
    - Basic visualization
  - **Acceptance criteria:**
    - Rendered table or histogram for ranges


**Requirements for Project Completion**  
- All required features implemented and demonstrated.  
- At least **5 unit tests** (happy paths + edge cases).  
- A clear **README** with setup steps, usage examples, and limitations.  
- Code formatted with **black** and linted with **ruff/flake8**.  
- Public functions include **type hints**; `mypy` passes or deviations are documented.  

---

## 5. Stretch goals: Add exponent, modulo, and memory recall (M+, M-).

### Overview & Core Skills

**What you’re building:** A small but complete CLI application focusing on clean input handling, core logic, and simple persistence.

**Core skills:** CLI parsing, functions, tests, JSON/CSV I/O.


### Required Features

- **Clear CLI and input validation** — **Difficulty 1/5**
  - **What it teaches:**
    - argparse
    - Defensive coding
  - **Acceptance criteria:**
    - Good --help; rejects invalid input
- **Core logic implemented cleanly** — **Difficulty 2/5**
  - **What it teaches:**
    - Functions
    - Tests
  - **Acceptance criteria:**
    - Happy paths covered by tests
- **Persistence if applicable** — **Difficulty 2/5**
  - **What it teaches:**
    - JSON/CSV I/O
  - **Acceptance criteria:**
    - Data survives restart
- **Basic logging** — **Difficulty 1/5**
  - **What it teaches:**
    - logging module
  - **Acceptance criteria:**
    - INFO/ERROR logs present

### Bonus Features

- **Config file support** — **Difficulty 2/5**
  - **What it teaches:**
    - YAML/JSON config
  - **Acceptance criteria:**
    - Config overrides CLI defaults
- **Packaging** — **Difficulty 2/5**
  - **What it teaches:**
    - pyproject.toml
  - **Acceptance criteria:**
    - Installable with entry point
- **Type hints & mypy** — **Difficulty 2/5**
  - **What it teaches:**
    - Typing
  - **Acceptance criteria:**
    - mypy passes or justified ignores


**Requirements for Project Completion**  
- All required features implemented and demonstrated.  
- At least **5 unit tests** (happy paths + edge cases).  
- A clear **README** with setup steps, usage examples, and limitations.  
- Code formatted with **black** and linted with **ruff/flake8**.  
- Public functions include **type hints**; `mypy` passes or deviations are documented.  

---

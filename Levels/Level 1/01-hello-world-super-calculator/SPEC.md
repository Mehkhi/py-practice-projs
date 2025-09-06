## 1. 1. Hello World & Super-Calculator

> **Note:** If you’re basing this on your `super-calc.py`, acceptance for command normalization should include mapping numeric and symbol aliases via an `ALIASES` dict and whitespace/uppercase normalization.

### Overview & Core Skills

**What you’re building:** A flexible command‑line calculator that accepts multiple aliases for operations and handles edge cases like division by zero.

**Core skills:** Parsing, defensive programming, mapping operations to functions, formatting, unit testing.


### Required Features

- **Parse and validate numeric input** — **Difficulty 2/5**
  - **What it teaches:**
    - Separating parsing from core logic using small functions.
    - Using `try/except` to guard against bad input and avoid crashes.
    - Clear user feedback loops that re‑prompt until valid data arrives.
  - **Acceptance criteria:**
    - Non‑numeric input does not crash the program and re‑prompts the user.
    - Empty/whitespace input is rejected.
    - Unit tests cover valid/invalid cases.
- **Core operations: add, subtract, multiply, divide** — **Difficulty 1/5**
  - **What it teaches:**
    - Mapping operations to functions for clarity and testability.
    - Floating‑point behavior and rounding considerations.
    - Simple functional design (pure functions for arithmetic).
  - **Acceptance criteria:**
    - All four operations compute correct results for sample inputs.
    - Output formatting is consistent and readable (e.g., fixed precision).
- **Division by zero handling** — **Difficulty 1/5**
  - **What it teaches:**
    - Guard clauses for exceptional cases (preventing runtime errors).
    - Separation of concerns: validation vs. computation vs. presentation.
    - User‑friendly error messages tied to the invalid operation.
  - **Acceptance criteria:**
    - When denominator == 0, the program shows a clear message and does not crash.
    - Unit tests cover zero and near‑zero denominators.
- **Command normalization and aliases** — **Difficulty 2/5**
  - **What it teaches:**
    - User experience via flexible inputs (e.g., `+`, `add`, `1`).
    - Dictionary‑based dispatch and normalization (`strip()`, `lower()`).
    - Defensive programming: handling `None` and empty tokens.
  - **Acceptance criteria:**
    - The same operation is invoked via multiple aliases (+, add, 1).
    - Invalid commands return `None` or a friendly message without crashing.

### Bonus Features

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
    - Tokenization and parsing strategies (shunting‑yard or recursive descent).
    - Operator precedence/associativity and error handling for invalid syntax.
    - Designing pure evaluators for testability.
  - **Acceptance criteria:**
    - `2+3*4` evaluates to `14`, `(2+3)*4` evaluates to `20`.
    - Malformed expressions produce friendly errors and do not crash.
- **Configurable precision and modes via CLI flags** — **Difficulty 2/5**
  - **What it teaches:**
    - Command‑line UX with `argparse` and good `--help` messages.
    - Separating configuration (precision) from business logic.
    - Basic packaging considerations (entry points).
  - **Acceptance criteria:**
    - `--precision N` formats results accordingly.
    - All required features continue to work with flags applied.


**Requirements for Project Completion**  
- All required features implemented and demonstrated.  
- At least **5 unit tests** (happy paths + edge cases).  
- A clear **README** with setup steps, usage examples, and limitations.  
- Code formatted with **black** and linted with **ruff/flake8**.  
- Public functions include **type hints**; `mypy` passes or deviations are documented.  

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

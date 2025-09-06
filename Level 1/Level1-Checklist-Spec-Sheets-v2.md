# Level 1 Checklist — Project Spec Sheets (Required + Bonus Features)
Each project includes feature‑level difficulty, acceptance criteria, and detailed learning outcomes.


### Difficulty Legend
- **1** = Very easy (few lines, minimal edge cases)
- **2** = Easy (simple logic, basic edge cases)
- **3** = Moderate (multiple components, careful handling)
- **4** = Hard (non‑trivial algorithms/design, extensive testing)
- **5** = Very hard (complex algorithms or architecture)

---

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

## 6. 2. Guess the Number

### Overview & Core Skills

**What you’re building:** A number‑guessing game with hints and scoring that builds core flow‑control skills.

**Core skills:** Randomness, loops, input validation, file I/O for persistence.


### Required Features

- **Random secret number and input validation** — **Difficulty 2/5**
  - **What it teaches:**
    - `random` module basics
    - Guarding input ranges
    - Replayable seeds for tests
  - **Acceptance criteria:**
    - Secret number in range
    - Invalid inputs re‑prompt
    - Tests with fixed seed
- **Higher/Lower hints and attempt counter** — **Difficulty 2/5**
  - **What it teaches:**
    - State tracking
    - Loop control
    - User feedback timing
  - **Acceptance criteria:**
    - Hints correct for all paths
    - Attempts displayed or logged
- **Best score persistence** — **Difficulty 2/5**
  - **What it teaches:**
    - File I/O
    - Data serialization (JSON)
  - **Acceptance criteria:**
    - Best score saved and loaded across runs
- **Replay loop (play again?)** — **Difficulty 1/5**
  - **What it teaches:**
    - Program structure
    - Resource cleanup
    - Loop invariants
  - **Acceptance criteria:**
    - Program re‑initializes state between games

### Bonus Features

- **Adaptive difficulty** — **Difficulty 3/5**
  - **What it teaches:**
    - Dynamic range sizing
    - Simple heuristics for UX
  - **Acceptance criteria:**
    - Range adjusts based on prior performance
- **Binary‑search coaching** — **Difficulty 2/5**
  - **What it teaches:**
    - Search strategies
    - Algorithmic thinking
  - **Acceptance criteria:**
    - Optional mode explains optimal next guess
- **Leaderboard** — **Difficulty 3/5**
  - **What it teaches:**
    - Sorting records
    - File locking/safety
  - **Acceptance criteria:**
    - Top N scores displayed with names


**Requirements for Project Completion**  
- All required features implemented and demonstrated.  
- At least **5 unit tests** (happy paths + edge cases).  
- A clear **README** with setup steps, usage examples, and limitations.  
- Code formatted with **black** and linted with **ruff/flake8**.  
- Public functions include **type hints**; `mypy` passes or deviations are documented.  

---

## 7. What you build: Computer picks a number; user guesses until correct with hints.

### Overview & Core Skills

**What you’re building:** A number‑guessing game with hints and scoring that builds core flow‑control skills.

**Core skills:** Randomness, loops, input validation, file I/O for persistence.


### Required Features

- **Random secret number and input validation** — **Difficulty 2/5**
  - **What it teaches:**
    - `random` module basics
    - Guarding input ranges
    - Replayable seeds for tests
  - **Acceptance criteria:**
    - Secret number in range
    - Invalid inputs re‑prompt
    - Tests with fixed seed
- **Higher/Lower hints and attempt counter** — **Difficulty 2/5**
  - **What it teaches:**
    - State tracking
    - Loop control
    - User feedback timing
  - **Acceptance criteria:**
    - Hints correct for all paths
    - Attempts displayed or logged
- **Best score persistence** — **Difficulty 2/5**
  - **What it teaches:**
    - File I/O
    - Data serialization (JSON)
  - **Acceptance criteria:**
    - Best score saved and loaded across runs
- **Replay loop (play again?)** — **Difficulty 1/5**
  - **What it teaches:**
    - Program structure
    - Resource cleanup
    - Loop invariants
  - **Acceptance criteria:**
    - Program re‑initializes state between games

### Bonus Features

- **Adaptive difficulty** — **Difficulty 3/5**
  - **What it teaches:**
    - Dynamic range sizing
    - Simple heuristics for UX
  - **Acceptance criteria:**
    - Range adjusts based on prior performance
- **Binary‑search coaching** — **Difficulty 2/5**
  - **What it teaches:**
    - Search strategies
    - Algorithmic thinking
  - **Acceptance criteria:**
    - Optional mode explains optimal next guess
- **Leaderboard** — **Difficulty 3/5**
  - **What it teaches:**
    - Sorting records
    - File locking/safety
  - **Acceptance criteria:**
    - Top N scores displayed with names


**Requirements for Project Completion**  
- All required features implemented and demonstrated.  
- At least **5 unit tests** (happy paths + edge cases).  
- A clear **README** with setup steps, usage examples, and limitations.  
- Code formatted with **black** and linted with **ruff/flake8**.  
- Public functions include **type hints**; `mypy` passes or deviations are documented.  

---

## 8. Skills: random, loops, conditionals, counters, replay loop.

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

## 9. Milestones: Limit attempts; show attempts used; track best score in a file.

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

## 10. Stretch goals: Binary-search hint mode (higher/lower guidance quality).

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

## 11. 3. Temperature Converter

### Overview & Core Skills

**What you’re building:** A reliable converter with menus, validation, and batch modes.

**Core skills:** Numeric conversions, rounding, CSV I/O, testable functions.


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
    - Formula translation into code and unit tests.
    - Rounding strategies and display formatting.
    - Input normalization and unit choice UX.
  - **Acceptance criteria:**
    - Correct conversions across sample values (known pairs).
    - Unit selection is validated and persisted (optional).
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

## 12. What you build: Convert Celsius↔Fahrenheit↔Kelvin with simple menu.

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
    - Formula translation into code and unit tests.
    - Rounding strategies and display formatting.
    - Input normalization and unit choice UX.
  - **Acceptance criteria:**
    - Correct conversions across sample values (known pairs).
    - Unit selection is validated and persisted (optional).
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

## 13. Skills: float math, branching, functions, docstrings.

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

## 14. Milestones: Validate ranges; round sensibly; support batch conversions from a file.

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

## 15. Stretch goals: Graph conversion table with text grid.

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

## 16. 4. Unit Converter

### Overview & Core Skills

**What you’re building:** A reliable converter with menus, validation, and batch modes.

**Core skills:** Numeric conversions, rounding, CSV I/O, testable functions.


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

## 17. What you build: Length/weight conversions (m↔ft, kg↔lb) with a tiny DSL-like menu.

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

## 18. Skills: dict lookups, mapping tables, functions, error messages.

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

## 19. Milestones: Centralize conversions; add tests for edge cases; persist last selection.

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

## 20. Stretch goals: Support chaining (m→ft→in) and custom factors file.

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

## 21. 5. Rock–Paper–Scissors

### Overview & Core Skills

**What you’re building:** Turn‑based game that teaches clean rule representation and state tracking.

**Core skills:** Random choice, state, rule tables, persistence.


### Required Features

- **User & computer choices** — **Difficulty 1/5**
  - **What it teaches:**
    - Input parsing
    - Random choice
  - **Acceptance criteria:**
    - Handles invalid input gracefully
- **Outcome rules** — **Difficulty 2/5**
  - **What it teaches:**
    - Conditional logic
    - Clean mapping tables
  - **Acceptance criteria:**
    - All outcomes correct; unit tests
- **Best‑of‑N series** — **Difficulty 2/5**
  - **What it teaches:**
    - State tracking
    - Win conditions
  - **Acceptance criteria:**
    - Series ends correctly with minimal extra input
- **Scoreboard** — **Difficulty 1/5**
  - **What it teaches:**
    - Formatting
    - Persistence basics
  - **Acceptance criteria:**
    - Current score visible; optional save

### Bonus Features

- **Lizard/Spock expansion** — **Difficulty 2/5**
  - **What it teaches:**
    - Extensible rule tables
  - **Acceptance criteria:**
    - All 5‑gesture outcomes correct
- **Simple AI (counter last move)** — **Difficulty 2/5**
  - **What it teaches:**
    - Heuristics
    - Stateful opponents
  - **Acceptance criteria:**
    - Win rate measurable vs random
- **Persistent stats** — **Difficulty 2/5**
  - **What it teaches:**
    - JSON store
    - Sessions
  - **Acceptance criteria:**
    - Lifetime W/L/T shown


**Requirements for Project Completion**  
- All required features implemented and demonstrated.  
- At least **5 unit tests** (happy paths + edge cases).  
- A clear **README** with setup steps, usage examples, and limitations.  
- Code formatted with **black** and linted with **ruff/flake8**.  
- Public functions include **type hints**; `mypy` passes or deviations are documented.  

---

## 22. What you build: Play against the computer with running score.

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

## 23. Skills: random choice, enums via constants, loops, input parsing.

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

## 24. Milestones: Best‑of‑N series; detect invalid input; pretty scoreboard.

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

## 25. Stretch goals: Add Lizard/Spock variant and simple AI (counter last move).

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

## 26. 6. Mad Libs Generator

### Overview & Core Skills

**What you’re building:** Template‑driven word game that teaches file handling and simple templating.

**Core skills:** Regex, string formatting, resource management.


### Required Features

- **Load template** — **Difficulty 1/5**
  - **What it teaches:**
    - File I/O
    - Resource paths
  - **Acceptance criteria:**
    - Missing file handled gracefully
- **Detect placeholders** — **Difficulty 2/5**
  - **What it teaches:**
    - Regex
    - Tokenization
  - **Acceptance criteria:**
    - All placeholders listed before prompting
- **Prompt and fill** — **Difficulty 1/5**
  - **What it teaches:**
    - Loops
    - String formatting
  - **Acceptance criteria:**
    - All placeholders filled; output coherent
- **Save completed story** — **Difficulty 1/5**
  - **What it teaches:**
    - Write files
    - Naming
  - **Acceptance criteria:**
    - Story saved in output folder

### Bonus Features

- **Multiple templates** — **Difficulty 1/5**
  - **What it teaches:**
    - Directory scanning
  - **Acceptance criteria:**
    - User can choose a template
- **Parts‑of‑speech hints** — **Difficulty 2/5**
  - **What it teaches:**
    - Metadata sidecar JSON
  - **Acceptance criteria:**
    - Prompts show the required POS
- **Random selection mode** — **Difficulty 1/5**
  - **What it teaches:**
    - random
  - **Acceptance criteria:**
    - Random template & sampling order


**Requirements for Project Completion**  
- All required features implemented and demonstrated.  
- At least **5 unit tests** (happy paths + edge cases).  
- A clear **README** with setup steps, usage examples, and limitations.  
- Code formatted with **black** and linted with **ruff/flake8**.  
- Public functions include **type hints**; `mypy` passes or deviations are documented.  

---

## 27. What you build: Prompt for words and inject into a story template.

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

## 28. Skills: string formatting, lists, files, basic templates.

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

## 29. Milestones: Load multiple templates from folder; save completed stories.

### Overview & Core Skills

**What you’re building:** Bill calculator with taxes, tips, and split logic.

**Core skills:** Decimal math, rounding, CSV export.


### Required Features

- **Subtotal, tax, tip calculation** — **Difficulty 1/5**
  - **What it teaches:**
    - Float vs Decimal
    - Rounding
  - **Acceptance criteria:**
    - Matches reference calculator within cents
- **Split evenly among diners** — **Difficulty 1/5**
  - **What it teaches:**
    - Division
    - Edge cases
  - **Acceptance criteria:**
    - 1..N diners works; remainders handled
- **Rounding strategy options** — **Difficulty 2/5**
  - **What it teaches:**
    - Bankers vs away‑from‑zero
  - **Acceptance criteria:**
    - User selects rounding mode
- **Input validation** — **Difficulty 1/5**
  - **What it teaches:**
    - Parsing
    - Error messages
  - **Acceptance criteria:**
    - Reject negative amounts; non‑numeric

### Bonus Features

- **Uneven splits** — **Difficulty 2/5**
  - **What it teaches:**
    - Weights/percentages
  - **Acceptance criteria:**
    - Shares by weight/percent
- **Receipt export** — **Difficulty 1/5**
  - **What it teaches:**
    - Text/CSV export
  - **Acceptance criteria:**
    - Printable receipt generated
- **Service fees & discounts** — **Difficulty 2/5**
  - **What it teaches:**
    - Order of operations
  - **Acceptance criteria:**
    - Configurable fee application order


**Requirements for Project Completion**  
- All required features implemented and demonstrated.  
- At least **5 unit tests** (happy paths + edge cases).  
- A clear **README** with setup steps, usage examples, and limitations.  
- Code formatted with **black** and linted with **ruff/flake8**.  
- Public functions include **type hints**; `mypy` passes or deviations are documented.  

---

## 30. Stretch goals: Randomly select template and required parts of speech.

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

## 31. 7. Palindrome & Anagram Checker

### Overview & Core Skills

**What you’re building:** Text analyzers focused on robust normalization and comparison.

**Core skills:** Unicode handling, collections, tests.


### Required Features

- **Normalization (case, spaces, punctuation)** — **Difficulty 2/5**
  - **What it teaches:**
    - Unicode/ASCII handling
    - Translation tables
  - **Acceptance criteria:**
    - Same result for 'A man, a plan…'
- **Palindrome check** — **Difficulty 1/5**
  - **What it teaches:**
    - Slicing
    - Two‑pointer technique
  - **Acceptance criteria:**
    - Odd/even length handled
- **Anagram check** — **Difficulty 2/5**
  - **What it teaches:**
    - collections.Counter
    - Sorting
  - **Acceptance criteria:**
    - Ignores spaces/punctuation
- **Unit tests** — **Difficulty 1/5**
  - **What it teaches:**
    - pytest basics
  - **Acceptance criteria:**
    - Dozens of cases incl. unicode

### Bonus Features

- **Batch file mode** — **Difficulty 2/5**
  - **What it teaches:**
    - File I/O
    - CLI parsing
  - **Acceptance criteria:**
    - Reads list and prints results
- **Performance on large lists** — **Difficulty 2/5**
  - **What it teaches:**
    - Algorithmic complexity
  - **Acceptance criteria:**
    - Handles 10k+ pairs quickly
- **Interactive hints** — **Difficulty 1/5**
  - **What it teaches:**
    - UX
  - **Acceptance criteria:**
    - Explain why not palindrome/anagram


**Requirements for Project Completion**  
- All required features implemented and demonstrated.  
- At least **5 unit tests** (happy paths + edge cases).  
- A clear **README** with setup steps, usage examples, and limitations.  
- Code formatted with **black** and linted with **ruff/flake8**.  
- Public functions include **type hints**; `mypy` passes or deviations are documented.  

---

## 32. What you build: Check if text is a palindrome; detect anagrams between two phrases.

### Overview & Core Skills

**What you’re building:** Text analyzers focused on robust normalization and comparison.

**Core skills:** Unicode handling, collections, tests.


### Required Features

- **Normalization (case, spaces, punctuation)** — **Difficulty 2/5**
  - **What it teaches:**
    - Unicode/ASCII handling
    - Translation tables
  - **Acceptance criteria:**
    - Same result for 'A man, a plan…'
- **Palindrome check** — **Difficulty 1/5**
  - **What it teaches:**
    - Slicing
    - Two‑pointer technique
  - **Acceptance criteria:**
    - Odd/even length handled
- **Anagram check** — **Difficulty 2/5**
  - **What it teaches:**
    - collections.Counter
    - Sorting
  - **Acceptance criteria:**
    - Ignores spaces/punctuation
- **Unit tests** — **Difficulty 1/5**
  - **What it teaches:**
    - pytest basics
  - **Acceptance criteria:**
    - Dozens of cases incl. unicode

### Bonus Features

- **Batch file mode** — **Difficulty 2/5**
  - **What it teaches:**
    - File I/O
    - CLI parsing
  - **Acceptance criteria:**
    - Reads list and prints results
- **Performance on large lists** — **Difficulty 2/5**
  - **What it teaches:**
    - Algorithmic complexity
  - **Acceptance criteria:**
    - Handles 10k+ pairs quickly
- **Interactive hints** — **Difficulty 1/5**
  - **What it teaches:**
    - UX
  - **Acceptance criteria:**
    - Explain why not palindrome/anagram


**Requirements for Project Completion**  
- All required features implemented and demonstrated.  
- At least **5 unit tests** (happy paths + edge cases).  
- A clear **README** with setup steps, usage examples, and limitations.  
- Code formatted with **black** and linted with **ruff/flake8**.  
- Public functions include **type hints**; `mypy` passes or deviations are documented.  

---

## 33. Skills: string methods, normalization, collections.Counter.

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

## 34. Milestones: Ignore punctuation/spacing; add unit tests.

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

## 35. Stretch goals: CLI mode with argparse and batch file input.

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

## 36. 8. Alarm & Countdown Timer

### Overview & Core Skills

**What you’re building:** Time utilities for alarms and timers with cancellation and snooze.

**Core skills:** Datetime parsing, loops, persistence.


### Required Features

- **Parse 'HH:MM' or durations (e.g., 10m, 1h)** — **Difficulty 2/5**
  - **What it teaches:**
    - datetime parsing
    - Edge cases around midnight
  - **Acceptance criteria:**
    - Invalid times rejected; tests
- **Countdown loop and notifications** — **Difficulty 1/5**
  - **What it teaches:**
    - time.sleep()
    - Loop design
  - **Acceptance criteria:**
    - Accurate countdown within 1s
- **Cancel/snooze** — **Difficulty 2/5**
  - **What it teaches:**
    - State transitions
    - Signals/KeyboardInterrupt
  - **Acceptance criteria:**
    - User can cancel or snooze safely
- **Multiple alarms** — **Difficulty 2/5**
  - **What it teaches:**
    - Data structures
    - Scheduling
  - **Acceptance criteria:**
    - Run multiple without blocking UI

### Bonus Features

- **Persist alarms to JSON** — **Difficulty 1/5**
  - **What it teaches:**
    - Serialization
  - **Acceptance criteria:**
    - Alarms restored on restart
- **Natural language times** — **Difficulty 3/5**
  - **What it teaches:**
    - Parsing libraries
    - Ambiguity handling
  - **Acceptance criteria:**
    - 'in 5 minutes' works predictably
- **System notifications/sounds** — **Difficulty 2/5**
  - **What it teaches:**
    - Cross‑platform nuances
  - **Acceptance criteria:**
    - Works on macOS/Win/Linux (documented)


**Requirements for Project Completion**  
- All required features implemented and demonstrated.  
- At least **5 unit tests** (happy paths + edge cases).  
- A clear **README** with setup steps, usage examples, and limitations.  
- Code formatted with **black** and linted with **ruff/flake8**.  
- Public functions include **type hints**; `mypy` passes or deviations are documented.  

---

## 37. What you build: Set an alarm or countdown that rings at time.

### Overview & Core Skills

**What you’re building:** Time utilities for alarms and timers with cancellation and snooze.

**Core skills:** Datetime parsing, loops, persistence.


### Required Features

- **Parse 'HH:MM' or durations (e.g., 10m, 1h)** — **Difficulty 2/5**
  - **What it teaches:**
    - datetime parsing
    - Edge cases around midnight
  - **Acceptance criteria:**
    - Invalid times rejected; tests
- **Countdown loop and notifications** — **Difficulty 1/5**
  - **What it teaches:**
    - time.sleep()
    - Loop design
  - **Acceptance criteria:**
    - Accurate countdown within 1s
- **Cancel/snooze** — **Difficulty 2/5**
  - **What it teaches:**
    - State transitions
    - Signals/KeyboardInterrupt
  - **Acceptance criteria:**
    - User can cancel or snooze safely
- **Multiple alarms** — **Difficulty 2/5**
  - **What it teaches:**
    - Data structures
    - Scheduling
  - **Acceptance criteria:**
    - Run multiple without blocking UI

### Bonus Features

- **Persist alarms to JSON** — **Difficulty 1/5**
  - **What it teaches:**
    - Serialization
  - **Acceptance criteria:**
    - Alarms restored on restart
- **Natural language times** — **Difficulty 3/5**
  - **What it teaches:**
    - Parsing libraries
    - Ambiguity handling
  - **Acceptance criteria:**
    - 'in 5 minutes' works predictably
- **System notifications/sounds** — **Difficulty 2/5**
  - **What it teaches:**
    - Cross‑platform nuances
  - **Acceptance criteria:**
    - Works on macOS/Win/Linux (documented)


**Requirements for Project Completion**  
- All required features implemented and demonstrated.  
- At least **5 unit tests** (happy paths + edge cases).  
- A clear **README** with setup steps, usage examples, and limitations.  
- Code formatted with **black** and linted with **ruff/flake8**.  
- Public functions include **type hints**; `mypy` passes or deviations are documented.  

---

## 38. Skills: time, datetime, while-loops, cross-platform beeps.

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

## 39. Milestones: Parse 'HH:MM' and '10m' formats; cancel option.

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

## 40. Stretch goals: Multiple alarms stored in JSON.

### Overview & Core Skills

**What you’re building:** Time utilities for alarms and timers with cancellation and snooze.

**Core skills:** Datetime parsing, loops, persistence.


### Required Features

- **Parse 'HH:MM' or durations (e.g., 10m, 1h)** — **Difficulty 2/5**
  - **What it teaches:**
    - datetime parsing
    - Edge cases around midnight
  - **Acceptance criteria:**
    - Invalid times rejected; tests
- **Countdown loop and notifications** — **Difficulty 1/5**
  - **What it teaches:**
    - time.sleep()
    - Loop design
  - **Acceptance criteria:**
    - Accurate countdown within 1s
- **Cancel/snooze** — **Difficulty 2/5**
  - **What it teaches:**
    - State transitions
    - Signals/KeyboardInterrupt
  - **Acceptance criteria:**
    - User can cancel or snooze safely
- **Multiple alarms** — **Difficulty 2/5**
  - **What it teaches:**
    - Data structures
    - Scheduling
  - **Acceptance criteria:**
    - Run multiple without blocking UI

### Bonus Features

- **Persist alarms to JSON** — **Difficulty 1/5**
  - **What it teaches:**
    - Serialization
  - **Acceptance criteria:**
    - Alarms restored on restart
- **Natural language times** — **Difficulty 3/5**
  - **What it teaches:**
    - Parsing libraries
    - Ambiguity handling
  - **Acceptance criteria:**
    - 'in 5 minutes' works predictably
- **System notifications/sounds** — **Difficulty 2/5**
  - **What it teaches:**
    - Cross‑platform nuances
  - **Acceptance criteria:**
    - Works on macOS/Win/Linux (documented)


**Requirements for Project Completion**  
- All required features implemented and demonstrated.  
- At least **5 unit tests** (happy paths + edge cases).  
- A clear **README** with setup steps, usage examples, and limitations.  
- Code formatted with **black** and linted with **ruff/flake8**.  
- Public functions include **type hints**; `mypy` passes or deviations are documented.  

---

## 41. 9. To‑Do List (Text File)

### Overview & Core Skills

**What you’re building:** Command‑line task manager with persistence and filtering.

**Core skills:** CRUD patterns, JSON storage, CLI UX.


### Required Features

- **Add/list/complete/delete** — **Difficulty 2/5**
  - **What it teaches:**
    - CRUD modeling
    - List/dict data structures
  - **Acceptance criteria:**
    - Each action works and updates state
- **Persistent storage (JSON)** — **Difficulty 2/5**
  - **What it teaches:**
    - Serialization
    - Atomic writes
  - **Acceptance criteria:**
    - Data survives restart; no partial files
- **IDs and timestamps** — **Difficulty 2/5**
  - **What it teaches:**
    - UUIDs or counters
    - datetime.now()
  - **Acceptance criteria:**
    - IDs unique; timestamps present
- **Input validation and confirmation** — **Difficulty 2/5**
  - **What it teaches:**
    - Defensive coding
  - **Acceptance criteria:**
    - Invalid IDs rejected; deletes confirmed

### Bonus Features

- **Due dates & priorities** — **Difficulty 2/5**
  - **What it teaches:**
    - Sorting
    - Comparators
  - **Acceptance criteria:**
    - Sort by priority/date; ties stable
- **Filters (today, overdue, priority)** — **Difficulty 2/5**
  - **What it teaches:**
    - Query patterns
  - **Acceptance criteria:**
    - CLI flags filter views
- **Recurring tasks** — **Difficulty 3/5**
  - **What it teaches:**
    - Scheduling rules
  - **Acceptance criteria:**
    - Tasks regenerate upon completion


**Requirements for Project Completion**  
- All required features implemented and demonstrated.  
- At least **5 unit tests** (happy paths + edge cases).  
- A clear **README** with setup steps, usage examples, and limitations.  
- Code formatted with **black** and linted with **ruff/flake8**.  
- Public functions include **type hints**; `mypy` passes or deviations are documented.  

---

## 42. What you build: Minimal task list saved to disk with add/list/complete/delete.

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

## 43. Skills: file I/O, lists, indexes, simple persistence.

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

## 44. Milestones: Unique IDs; timestamps; confirm destructive actions.

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

## 45. Stretch goals: Priorities and due dates; sort by priority.

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

## 46. 10. Address Book (CSV)

### Overview & Core Skills

**What you’re building:** Contact manager with validation and robust CSV handling.

**Core skills:** CSV I/O, regex validation, search.


### Required Features

- **Add/search/list contacts** — **Difficulty 2/5**
  - **What it teaches:**
    - CSV I/O
    - Indexing in memory
  - **Acceptance criteria:**
    - Search by name/email
- **Validate emails** — **Difficulty 2/5**
  - **What it teaches:**
    - Regex vs libraries
    - Data quality
  - **Acceptance criteria:**
    - Reject invalid emails with message
- **De‑duplicate entries** — **Difficulty 2/5**
  - **What it teaches:**
    - Keys & uniqueness
  - **Acceptance criteria:**
    - Prevent duplicates by email
- **Export/Import CSV** — **Difficulty 1/5**
  - **What it teaches:**
    - CSV dialects
  - **Acceptance criteria:**
    - Round‑trip preserves fields

### Bonus Features

- **vCard export** — **Difficulty 2/5**
  - **What it teaches:**
    - Format specs
  - **Acceptance criteria:**
    - Generates valid .vcf
- **Fuzzy search** — **Difficulty 3/5**
  - **What it teaches:**
    - Approximate matching
  - **Acceptance criteria:**
    - Ranked results for typos
- **Groups/labels** — **Difficulty 2/5**
  - **What it teaches:**
    - Data modeling
  - **Acceptance criteria:**
    - Assign/list by group


**Requirements for Project Completion**  
- All required features implemented and demonstrated.  
- At least **5 unit tests** (happy paths + edge cases).  
- A clear **README** with setup steps, usage examples, and limitations.  
- Code formatted with **black** and linted with **ruff/flake8**.  
- Public functions include **type hints**; `mypy` passes or deviations are documented.  

---

## 47. What you build: Store contacts in CSV; search by name or email.

### Overview & Core Skills

**What you’re building:** A small but complete CLI application focusing on clean input handling, core logic, and simple persistence.

**Core skills:** CLI parsing, functions, tests, JSON/CSV I/O.


### Required Features

- **Add/search/list contacts** — **Difficulty 2/5**
  - **What it teaches:**
    - CSV I/O
    - Indexing in memory
  - **Acceptance criteria:**
    - Search by name/email
- **Validate emails** — **Difficulty 2/5**
  - **What it teaches:**
    - Regex vs libraries
    - Data quality
  - **Acceptance criteria:**
    - Reject invalid emails with message
- **De‑duplicate entries** — **Difficulty 2/5**
  - **What it teaches:**
    - Keys & uniqueness
  - **Acceptance criteria:**
    - Prevent duplicates by email
- **Export/Import CSV** — **Difficulty 1/5**
  - **What it teaches:**
    - CSV dialects
  - **Acceptance criteria:**
    - Round‑trip preserves fields

### Bonus Features

- **vCard export** — **Difficulty 2/5**
  - **What it teaches:**
    - Format specs
  - **Acceptance criteria:**
    - Generates valid .vcf
- **Fuzzy search** — **Difficulty 3/5**
  - **What it teaches:**
    - Approximate matching
  - **Acceptance criteria:**
    - Ranked results for typos
- **Groups/labels** — **Difficulty 2/5**
  - **What it teaches:**
    - Data modeling
  - **Acceptance criteria:**
    - Assign/list by group


**Requirements for Project Completion**  
- All required features implemented and demonstrated.  
- At least **5 unit tests** (happy paths + edge cases).  
- A clear **README** with setup steps, usage examples, and limitations.  
- Code formatted with **black** and linted with **ruff/flake8**.  
- Public functions include **type hints**; `mypy` passes or deviations are documented.  

---

## 48. Skills: csv module, dict rows, basic search.

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

## 49. Milestones: Import/export; validate email; avoid duplicates.

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

## 50. Stretch goals: Support vCard export.

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

## 51. 11. Word Count (wc)

### Overview & Core Skills

**What you’re building:** A `wc`-style utility for counting text metrics across files and folders.

**Core skills:** Streaming I/O, recursion, CLI design.


### Required Features

- **Count lines/words/chars across files** — **Difficulty 2/5**
  - **What it teaches:**
    - Streaming I/O
    - Memory safety
  - **Acceptance criteria:**
    - Matches reference counts
- **Glob patterns and directories** — **Difficulty 2/5**
  - **What it teaches:**
    - pathlib
    - Recursion
  - **Acceptance criteria:**
    - Recurse when asked; ignore hidden if set
- **Totals across inputs** — **Difficulty 1/5**
  - **What it teaches:**
    - Aggregation
  - **Acceptance criteria:**
    - Shows per‑file and total
- **Robust CLI (argparse)** — **Difficulty 2/5**
  - **What it teaches:**
    - CLI UX
  - **Acceptance criteria:**
    - Good --help and exit codes

### Bonus Features

- **Top‑N frequent words** — **Difficulty 2/5**
  - **What it teaches:**
    - Counter
    - Stopwords
  - **Acceptance criteria:**
    - Outputs top‑N with counts
- **Encoding handling** — **Difficulty 3/5**
  - **What it teaches:**
    - UTF‑8/UTF‑16
    - Errors
  - **Acceptance criteria:**
    - Skips or reports undecodable files
- **Parallel processing** — **Difficulty 3/5**
  - **What it teaches:**
    - ThreadPool/ProcessPool
  - **Acceptance criteria:**
    - Speedup on many files


**Requirements for Project Completion**  
- All required features implemented and demonstrated.  
- At least **5 unit tests** (happy paths + edge cases).  
- A clear **README** with setup steps, usage examples, and limitations.  
- Code formatted with **black** and linted with **ruff/flake8**.  
- Public functions include **type hints**; `mypy` passes or deviations are documented.  

---

## 52. What you build: Count lines/words/chars across files like Unix wc.

### Overview & Core Skills

**What you’re building:** A `wc`-style utility for counting text metrics across files and folders.

**Core skills:** Streaming I/O, recursion, CLI design.


### Required Features

- **Count lines/words/chars across files** — **Difficulty 2/5**
  - **What it teaches:**
    - Streaming I/O
    - Memory safety
  - **Acceptance criteria:**
    - Matches reference counts
- **Glob patterns and directories** — **Difficulty 2/5**
  - **What it teaches:**
    - pathlib
    - Recursion
  - **Acceptance criteria:**
    - Recurse when asked; ignore hidden if set
- **Totals across inputs** — **Difficulty 1/5**
  - **What it teaches:**
    - Aggregation
  - **Acceptance criteria:**
    - Shows per‑file and total
- **Robust CLI (argparse)** — **Difficulty 2/5**
  - **What it teaches:**
    - CLI UX
  - **Acceptance criteria:**
    - Good --help and exit codes

### Bonus Features

- **Top‑N frequent words** — **Difficulty 2/5**
  - **What it teaches:**
    - Counter
    - Stopwords
  - **Acceptance criteria:**
    - Outputs top‑N with counts
- **Encoding handling** — **Difficulty 3/5**
  - **What it teaches:**
    - UTF‑8/UTF‑16
    - Errors
  - **Acceptance criteria:**
    - Skips or reports undecodable files
- **Parallel processing** — **Difficulty 3/5**
  - **What it teaches:**
    - ThreadPool/ProcessPool
  - **Acceptance criteria:**
    - Speedup on many files


**Requirements for Project Completion**  
- All required features implemented and demonstrated.  
- At least **5 unit tests** (happy paths + edge cases).  
- A clear **README** with setup steps, usage examples, and limitations.  
- Code formatted with **black** and linted with **ruff/flake8**.  
- Public functions include **type hints**; `mypy` passes or deviations are documented.  

---

## 53. Skills: argparse, pathlib, reading files, aggregation.

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

## 54. Milestones: Glob patterns; handle large files; unit tests.

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

## 55. Stretch goals: Top‑N most frequent words.

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

## 56. 12. Dice Roller Simulator

### Overview & Core Skills

**What you’re building:** Dice roller with statistics and extended rules.

**Core skills:** Parsing, randomness, statistics.


### Required Features

- **Parse NdM notation** — **Difficulty 2/5**
  - **What it teaches:**
    - Parsing strings
    - Validation
  - **Acceptance criteria:**
    - Rejects invalid forms with message
- **Roll dice and sum** — **Difficulty 1/5**
  - **What it teaches:**
    - random
    - Loops/list comps
  - **Acceptance criteria:**
    - Deterministic with seed in tests
- **Repeat rolls and stats** — **Difficulty 2/5**
  - **What it teaches:**
    - Mean/variance
    - Sampling
  - **Acceptance criteria:**
    - Shows distribution stats
- **Output formatting** — **Difficulty 1/5**
  - **What it teaches:**
    - Readable formatting
  - **Acceptance criteria:**
    - Clear breakdown per roll

### Bonus Features

- **ASCII histogram** — **Difficulty 2/5**
  - **What it teaches:**
    - Text plotting
  - **Acceptance criteria:**
    - Bins displayed correctly
- **Advantage/Disadvantage** — **Difficulty 2/5**
  - **What it teaches:**
    - Alternative rules
  - **Acceptance criteria:**
    - Implements 2d20 take high/low
- **Custom dice (FATE, percentile)** — **Difficulty 2/5**
  - **What it teaches:**
    - Extensibility
  - **Acceptance criteria:**
    - Supports common dice types


**Requirements for Project Completion**  
- All required features implemented and demonstrated.  
- At least **5 unit tests** (happy paths + edge cases).  
- A clear **README** with setup steps, usage examples, and limitations.  
- Code formatted with **black** and linted with **ruff/flake8**.  
- Public functions include **type hints**; `mypy` passes or deviations are documented.  

---

## 57. What you build: Roll NdM dice (e.g., 3d6) and show distribution.

### Overview & Core Skills

**What you’re building:** Dice roller with statistics and extended rules.

**Core skills:** Parsing, randomness, statistics.


### Required Features

- **Parse NdM notation** — **Difficulty 2/5**
  - **What it teaches:**
    - Parsing strings
    - Validation
  - **Acceptance criteria:**
    - Rejects invalid forms with message
- **Roll dice and sum** — **Difficulty 1/5**
  - **What it teaches:**
    - random
    - Loops/list comps
  - **Acceptance criteria:**
    - Deterministic with seed in tests
- **Repeat rolls and stats** — **Difficulty 2/5**
  - **What it teaches:**
    - Mean/variance
    - Sampling
  - **Acceptance criteria:**
    - Shows distribution stats
- **Output formatting** — **Difficulty 1/5**
  - **What it teaches:**
    - Readable formatting
  - **Acceptance criteria:**
    - Clear breakdown per roll

### Bonus Features

- **ASCII histogram** — **Difficulty 2/5**
  - **What it teaches:**
    - Text plotting
  - **Acceptance criteria:**
    - Bins displayed correctly
- **Advantage/Disadvantage** — **Difficulty 2/5**
  - **What it teaches:**
    - Alternative rules
  - **Acceptance criteria:**
    - Implements 2d20 take high/low
- **Custom dice (FATE, percentile)** — **Difficulty 2/5**
  - **What it teaches:**
    - Extensibility
  - **Acceptance criteria:**
    - Supports common dice types


**Requirements for Project Completion**  
- All required features implemented and demonstrated.  
- At least **5 unit tests** (happy paths + edge cases).  
- A clear **README** with setup steps, usage examples, and limitations.  
- Code formatted with **black** and linted with **ruff/flake8**.  
- Public functions include **type hints**; `mypy` passes or deviations are documented.  

---

## 58. Skills: parsing input, random, list comprehension.

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

## 59. Milestones: Roll many times; compute mean/variance.

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

## 60. Stretch goals: ASCII histogram chart.

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

## 61. 13. Stopwatch

### Overview & Core Skills

**What you’re building:** Time tracker with laps and export.

**Core skills:** High‑resolution timers, formatting, CSV output.


### Required Features

- **Start/stop/lap** — **Difficulty 1/5**
  - **What it teaches:**
    - time.perf_counter()
    - State machine
  - **Acceptance criteria:**
    - Lap times accurate within tolerance
- **Format output** — **Difficulty 1/5**
  - **What it teaches:**
    - String formatting
  - **Acceptance criteria:**
    - HH:MM:SS.mmm
- **Keyboard controls** — **Difficulty 2/5**
  - **What it teaches:**
    - Input handling
  - **Acceptance criteria:**
    - Start/stop/lap/reset via keys
- **Export sessions to CSV** — **Difficulty 1/5**
  - **What it teaches:**
    - CSV writing
  - **Acceptance criteria:**
    - Columns: start, stop, laps

### Bonus Features

- **Hotkeys (cross‑platform)** — **Difficulty 3/5**
  - **What it teaches:**
    - Platform differences
  - **Acceptance criteria:**
    - Documented support per OS
- **Session summary** — **Difficulty 2/5**
  - **What it teaches:**
    - Aggregation
  - **Acceptance criteria:**
    - Totals/averages computed
- **Autosave and resume** — **Difficulty 2/5**
  - **What it teaches:**
    - Persistence
  - **Acceptance criteria:**
    - Restore previous session


**Requirements for Project Completion**  
- All required features implemented and demonstrated.  
- At least **5 unit tests** (happy paths + edge cases).  
- A clear **README** with setup steps, usage examples, and limitations.  
- Code formatted with **black** and linted with **ruff/flake8**.  
- Public functions include **type hints**; `mypy` passes or deviations are documented.  

---

## 62. What you build: Start/stop/lap timing tool in the console.

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

## 63. Skills: time/perf_counter, state machine, formatting.

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

## 64. Milestones: Lap list; export to CSV; keyboard shortcuts.

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

## 65. Stretch goals: Save sessions and summarize totals.

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

## 66. 14. Multiplication Table Generator

### Overview & Core Skills

**What you’re building:** Table generator with formatting and export options.

**Core skills:** Nested loops, formatting, CLI options.


### Required Features

- **Generate table for range** — **Difficulty 1/5**
  - **What it teaches:**
    - Nested loops
  - **Acceptance criteria:**
    - Configurable range; defaults documented
- **Column alignment** — **Difficulty 1/5**
  - **What it teaches:**
    - Formatting
    - Width calc
  - **Acceptance criteria:**
    - Neat grid alignment
- **Save to text/CSV** — **Difficulty 1/5**
  - **What it teaches:**
    - File writing
  - **Acceptance criteria:**
    - Files created with expected content
- **CLI options** — **Difficulty 1/5**
  - **What it teaches:**
    - argparse
  - **Acceptance criteria:**
    - --start, --end, --step documented

### Bonus Features

- **Quiz mode** — **Difficulty 2/5**
  - **What it teaches:**
    - Randomization
    - User feedback
  - **Acceptance criteria:**
    - Score tracked over N questions
- **Random holes mode** — **Difficulty 2/5**
  - **What it teaches:**
    - Exercise design
  - **Acceptance criteria:**
    - Blank cells user fills in
- **Prime highlights** — **Difficulty 2/5**
  - **What it teaches:**
    - Number theory basics
  - **Acceptance criteria:**
    - Prime multiples highlighted


**Requirements for Project Completion**  
- All required features implemented and demonstrated.  
- At least **5 unit tests** (happy paths + edge cases).  
- A clear **README** with setup steps, usage examples, and limitations.  
- Code formatted with **black** and linted with **ruff/flake8**.  
- Public functions include **type hints**; `mypy` passes or deviations are documented.  

---

## 67. What you build: Print 1–12 multiplication tables (or chosen range).

### Overview & Core Skills

**What you’re building:** Table generator with formatting and export options.

**Core skills:** Nested loops, formatting, CLI options.


### Required Features

- **Generate table for range** — **Difficulty 1/5**
  - **What it teaches:**
    - Nested loops
  - **Acceptance criteria:**
    - Configurable range; defaults documented
- **Column alignment** — **Difficulty 1/5**
  - **What it teaches:**
    - Formatting
    - Width calc
  - **Acceptance criteria:**
    - Neat grid alignment
- **Save to text/CSV** — **Difficulty 1/5**
  - **What it teaches:**
    - File writing
  - **Acceptance criteria:**
    - Files created with expected content
- **CLI options** — **Difficulty 1/5**
  - **What it teaches:**
    - argparse
  - **Acceptance criteria:**
    - --start, --end, --step documented

### Bonus Features

- **Quiz mode** — **Difficulty 2/5**
  - **What it teaches:**
    - Randomization
    - User feedback
  - **Acceptance criteria:**
    - Score tracked over N questions
- **Random holes mode** — **Difficulty 2/5**
  - **What it teaches:**
    - Exercise design
  - **Acceptance criteria:**
    - Blank cells user fills in
- **Prime highlights** — **Difficulty 2/5**
  - **What it teaches:**
    - Number theory basics
  - **Acceptance criteria:**
    - Prime multiples highlighted


**Requirements for Project Completion**  
- All required features implemented and demonstrated.  
- At least **5 unit tests** (happy paths + edge cases).  
- A clear **README** with setup steps, usage examples, and limitations.  
- Code formatted with **black** and linted with **ruff/flake8**.  
- Public functions include **type hints**; `mypy` passes or deviations are documented.  

---

## 68. Skills: nested loops, formatting, functions.

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

## 69. Milestones: Column alignment; save to text/CSV.

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

## 70. Stretch goals: Quiz mode with scoring.

### Overview & Core Skills

**What you’re building:** Multiple‑choice quiz driven by JSON content with scoring and timers.

**Core skills:** JSON schema, shuffling, scoring, timers.


### Required Features

- **Load questions from JSON** — **Difficulty 1/5**
  - **What it teaches:**
    - JSON I/O
    - Schema validation
  - **Acceptance criteria:**
    - Invalid schema gives error
- **Shuffle answers** — **Difficulty 1/5**
  - **What it teaches:**
    - random.shuffle
  - **Acceptance criteria:**
    - Answer keys tracked correctly
- **Scoring and feedback** — **Difficulty 2/5**
  - **What it teaches:**
    - State tracking
    - UX
  - **Acceptance criteria:**
    - Score/percent accuracy shown
- **Input validation** — **Difficulty 1/5**
  - **What it teaches:**
    - Robust parsing
  - **Acceptance criteria:**
    - Reject invalid option indices

### Bonus Features

- **Timer per question** — **Difficulty 2/5**
  - **What it teaches:**
    - Timing
    - Graceful timeouts
  - **Acceptance criteria:**
    - Auto‑advance on timeout
- **Categories & difficulty filters** — **Difficulty 2/5**
  - **What it teaches:**
    - Querying subsets
  - **Acceptance criteria:**
    - Select category/difficulty via CLI
- **Export results to CSV** — **Difficulty 1/5**
  - **What it teaches:**
    - CSV writing
  - **Acceptance criteria:**
    - One row per quiz attempt


**Requirements for Project Completion**  
- All required features implemented and demonstrated.  
- At least **5 unit tests** (happy paths + edge cases).  
- A clear **README** with setup steps, usage examples, and limitations.  
- Code formatted with **black** and linted with **ruff/flake8**.  
- Public functions include **type hints**; `mypy` passes or deviations are documented.  

---

## 71. 15. Password Generator

### Overview & Core Skills

**What you’re building:** Secure password generator with entropy estimation and passphrases.

**Core skills:** Randomness, security trade‑offs, math/entropy.


### Required Features

- **Length and character classes** — **Difficulty 1/5**
  - **What it teaches:**
    - Random selection
    - String pools
  - **Acceptance criteria:**
    - Length respected; classes included
- **Ensure class coverage** — **Difficulty 2/5**
  - **What it teaches:**
    - Post‑validation & regeneration
  - **Acceptance criteria:**
    - At least one char from each chosen class
- **Avoid ambiguous chars** — **Difficulty 1/5**
  - **What it teaches:**
    - Sets/exclusion
  - **Acceptance criteria:**
    - Ambiguous set excluded if flag set
- **Entropy estimate** — **Difficulty 2/5**
  - **What it teaches:**
    - log2 math
  - **Acceptance criteria:**
    - Entropy printed; matches formula

### Bonus Features

- **Passphrase mode** — **Difficulty 2/5**
  - **What it teaches:**
    - Wordlists
    - Diceware
  - **Acceptance criteria:**
    - k words separated by delimiter
- **Clipboard integration** — **Difficulty 2/5**
  - **What it teaches:**
    - Security trade‑offs
  - **Acceptance criteria:**
    - Copy with warning; timeout clear (doc)
- **Breach list check** — **Difficulty 3/5**
  - **What it teaches:**
    - Offline bloom filter (optional)
  - **Acceptance criteria:**
    - Warns on common passwords


**Requirements for Project Completion**  
- All required features implemented and demonstrated.  
- At least **5 unit tests** (happy paths + edge cases).  
- A clear **README** with setup steps, usage examples, and limitations.  
- Code formatted with **black** and linted with **ruff/flake8**.  
- Public functions include **type hints**; `mypy` passes or deviations are documented.  

---

## 72. What you build: Create random passwords meeting length and class rules.

### Overview & Core Skills

**What you’re building:** Secure password generator with entropy estimation and passphrases.

**Core skills:** Randomness, security trade‑offs, math/entropy.


### Required Features

- **Length and character classes** — **Difficulty 1/5**
  - **What it teaches:**
    - Random selection
    - String pools
  - **Acceptance criteria:**
    - Length respected; classes included
- **Ensure class coverage** — **Difficulty 2/5**
  - **What it teaches:**
    - Post‑validation & regeneration
  - **Acceptance criteria:**
    - At least one char from each chosen class
- **Avoid ambiguous chars** — **Difficulty 1/5**
  - **What it teaches:**
    - Sets/exclusion
  - **Acceptance criteria:**
    - Ambiguous set excluded if flag set
- **Entropy estimate** — **Difficulty 2/5**
  - **What it teaches:**
    - log2 math
  - **Acceptance criteria:**
    - Entropy printed; matches formula

### Bonus Features

- **Passphrase mode** — **Difficulty 2/5**
  - **What it teaches:**
    - Wordlists
    - Diceware
  - **Acceptance criteria:**
    - k words separated by delimiter
- **Clipboard integration** — **Difficulty 2/5**
  - **What it teaches:**
    - Security trade‑offs
  - **Acceptance criteria:**
    - Copy with warning; timeout clear (doc)
- **Breach list check** — **Difficulty 3/5**
  - **What it teaches:**
    - Offline bloom filter (optional)
  - **Acceptance criteria:**
    - Warns on common passwords


**Requirements for Project Completion**  
- All required features implemented and demonstrated.  
- At least **5 unit tests** (happy paths + edge cases).  
- A clear **README** with setup steps, usage examples, and limitations.  
- Code formatted with **black** and linted with **ruff/flake8**.  
- Public functions include **type hints**; `mypy` passes or deviations are documented.  

---

## 73. Skills: random, string constants, validation.

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

## 74. Milestones: Avoid ambiguous chars; ensure class coverage.

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

## 75. Stretch goals: Passphrase mode using word list.

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

## 76. 16. Hangman (ASCII)

### Overview & Core Skills

**What you’re building:** Classic terminal game highlighting state, rendering, and fairness.

**Core skills:** Sets, game loops, assets.


### Required Features

- **Word list and random pick** — **Difficulty 1/5**
  - **What it teaches:**
    - File I/O
    - random.choice
  - **Acceptance criteria:**
    - Missing list handled
- **Display progress and wrong guesses** — **Difficulty 2/5**
  - **What it teaches:**
    - Sets
    - Rendering ASCII
  - **Acceptance criteria:**
    - Correctly reveals letters
- **Win/lose conditions** — **Difficulty 1/5**
  - **What it teaches:**
    - State logic
  - **Acceptance criteria:**
    - Ends at correct time
- **Replay** — **Difficulty 1/5**
  - **What it teaches:**
    - Looping
  - **Acceptance criteria:**
    - State resets cleanly

### Bonus Features

- **Difficulty levels** — **Difficulty 2/5**
  - **What it teaches:**
    - Parameterizing game rules
  - **Acceptance criteria:**
    - Max attempts vary by difficulty
- **Hint system** — **Difficulty 2/5**
  - **What it teaches:**
    - Information design
  - **Acceptance criteria:**
    - Limited hints; penalize attempts
- **ASCII art stages** — **Difficulty 1/5**
  - **What it teaches:**
    - Assets mgmt
  - **Acceptance criteria:**
    - Stages correspond to attempts left


**Requirements for Project Completion**  
- All required features implemented and demonstrated.  
- At least **5 unit tests** (happy paths + edge cases).  
- A clear **README** with setup steps, usage examples, and limitations.  
- Code formatted with **black** and linted with **ruff/flake8**.  
- Public functions include **type hints**; `mypy` passes or deviations are documented.  

---

## 77. What you build: Classic hangman game in terminal with a word list.

### Overview & Core Skills

**What you’re building:** Classic terminal game highlighting state, rendering, and fairness.

**Core skills:** Sets, game loops, assets.


### Required Features

- **Word list and random pick** — **Difficulty 1/5**
  - **What it teaches:**
    - File I/O
    - random.choice
  - **Acceptance criteria:**
    - Missing list handled
- **Display progress and wrong guesses** — **Difficulty 2/5**
  - **What it teaches:**
    - Sets
    - Rendering ASCII
  - **Acceptance criteria:**
    - Correctly reveals letters
- **Win/lose conditions** — **Difficulty 1/5**
  - **What it teaches:**
    - State logic
  - **Acceptance criteria:**
    - Ends at correct time
- **Replay** — **Difficulty 1/5**
  - **What it teaches:**
    - Looping
  - **Acceptance criteria:**
    - State resets cleanly

### Bonus Features

- **Difficulty levels** — **Difficulty 2/5**
  - **What it teaches:**
    - Parameterizing game rules
  - **Acceptance criteria:**
    - Max attempts vary by difficulty
- **Hint system** — **Difficulty 2/5**
  - **What it teaches:**
    - Information design
  - **Acceptance criteria:**
    - Limited hints; penalize attempts
- **ASCII art stages** — **Difficulty 1/5**
  - **What it teaches:**
    - Assets mgmt
  - **Acceptance criteria:**
    - Stages correspond to attempts left


**Requirements for Project Completion**  
- All required features implemented and demonstrated.  
- At least **5 unit tests** (happy paths + edge cases).  
- A clear **README** with setup steps, usage examples, and limitations.  
- Code formatted with **black** and linted with **ruff/flake8**.  
- Public functions include **type hints**; `mypy` passes or deviations are documented.  

---

## 78. Skills: sets, state updates, reading resources.

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

## 79. Milestones: Reveal progress; track wrong guesses; replay.

### Overview & Core Skills

**What you’re building:** A number‑guessing game with hints and scoring that builds core flow‑control skills.

**Core skills:** Randomness, loops, input validation, file I/O for persistence.


### Required Features

- **Random secret number and input validation** — **Difficulty 2/5**
  - **What it teaches:**
    - `random` module basics
    - Guarding input ranges
    - Replayable seeds for tests
  - **Acceptance criteria:**
    - Secret number in range
    - Invalid inputs re‑prompt
    - Tests with fixed seed
- **Higher/Lower hints and attempt counter** — **Difficulty 2/5**
  - **What it teaches:**
    - State tracking
    - Loop control
    - User feedback timing
  - **Acceptance criteria:**
    - Hints correct for all paths
    - Attempts displayed or logged
- **Best score persistence** — **Difficulty 2/5**
  - **What it teaches:**
    - File I/O
    - Data serialization (JSON)
  - **Acceptance criteria:**
    - Best score saved and loaded across runs
- **Replay loop (play again?)** — **Difficulty 1/5**
  - **What it teaches:**
    - Program structure
    - Resource cleanup
    - Loop invariants
  - **Acceptance criteria:**
    - Program re‑initializes state between games

### Bonus Features

- **Adaptive difficulty** — **Difficulty 3/5**
  - **What it teaches:**
    - Dynamic range sizing
    - Simple heuristics for UX
  - **Acceptance criteria:**
    - Range adjusts based on prior performance
- **Binary‑search coaching** — **Difficulty 2/5**
  - **What it teaches:**
    - Search strategies
    - Algorithmic thinking
  - **Acceptance criteria:**
    - Optional mode explains optimal next guess
- **Leaderboard** — **Difficulty 3/5**
  - **What it teaches:**
    - Sorting records
    - File locking/safety
  - **Acceptance criteria:**
    - Top N scores displayed with names


**Requirements for Project Completion**  
- All required features implemented and demonstrated.  
- At least **5 unit tests** (happy paths + edge cases).  
- A clear **README** with setup steps, usage examples, and limitations.  
- Code formatted with **black** and linted with **ruff/flake8**.  
- Public functions include **type hints**; `mypy` passes or deviations are documented.  

---

## 80. Stretch goals: Difficulty levels and hints.

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

## 81. 17. Quiz App from JSON

### Overview & Core Skills

**What you’re building:** Multiple‑choice quiz driven by JSON content with scoring and timers.

**Core skills:** JSON schema, shuffling, scoring, timers.


### Required Features

- **Load questions from JSON** — **Difficulty 1/5**
  - **What it teaches:**
    - JSON I/O
    - Schema validation
  - **Acceptance criteria:**
    - Invalid schema gives error
- **Shuffle answers** — **Difficulty 1/5**
  - **What it teaches:**
    - random.shuffle
  - **Acceptance criteria:**
    - Answer keys tracked correctly
- **Scoring and feedback** — **Difficulty 2/5**
  - **What it teaches:**
    - State tracking
    - UX
  - **Acceptance criteria:**
    - Score/percent accuracy shown
- **Input validation** — **Difficulty 1/5**
  - **What it teaches:**
    - Robust parsing
  - **Acceptance criteria:**
    - Reject invalid option indices

### Bonus Features

- **Timer per question** — **Difficulty 2/5**
  - **What it teaches:**
    - Timing
    - Graceful timeouts
  - **Acceptance criteria:**
    - Auto‑advance on timeout
- **Categories & difficulty filters** — **Difficulty 2/5**
  - **What it teaches:**
    - Querying subsets
  - **Acceptance criteria:**
    - Select category/difficulty via CLI
- **Export results to CSV** — **Difficulty 1/5**
  - **What it teaches:**
    - CSV writing
  - **Acceptance criteria:**
    - One row per quiz attempt


**Requirements for Project Completion**  
- All required features implemented and demonstrated.  
- At least **5 unit tests** (happy paths + edge cases).  
- A clear **README** with setup steps, usage examples, and limitations.  
- Code formatted with **black** and linted with **ruff/flake8**.  
- Public functions include **type hints**; `mypy` passes or deviations are documented.  

---

## 82. What you build: Ask multiple‑choice questions loaded from JSON.

### Overview & Core Skills

**What you’re building:** Bill calculator with taxes, tips, and split logic.

**Core skills:** Decimal math, rounding, CSV export.


### Required Features

- **Subtotal, tax, tip calculation** — **Difficulty 1/5**
  - **What it teaches:**
    - Float vs Decimal
    - Rounding
  - **Acceptance criteria:**
    - Matches reference calculator within cents
- **Split evenly among diners** — **Difficulty 1/5**
  - **What it teaches:**
    - Division
    - Edge cases
  - **Acceptance criteria:**
    - 1..N diners works; remainders handled
- **Rounding strategy options** — **Difficulty 2/5**
  - **What it teaches:**
    - Bankers vs away‑from‑zero
  - **Acceptance criteria:**
    - User selects rounding mode
- **Input validation** — **Difficulty 1/5**
  - **What it teaches:**
    - Parsing
    - Error messages
  - **Acceptance criteria:**
    - Reject negative amounts; non‑numeric

### Bonus Features

- **Uneven splits** — **Difficulty 2/5**
  - **What it teaches:**
    - Weights/percentages
  - **Acceptance criteria:**
    - Shares by weight/percent
- **Receipt export** — **Difficulty 1/5**
  - **What it teaches:**
    - Text/CSV export
  - **Acceptance criteria:**
    - Printable receipt generated
- **Service fees & discounts** — **Difficulty 2/5**
  - **What it teaches:**
    - Order of operations
  - **Acceptance criteria:**
    - Configurable fee application order


**Requirements for Project Completion**  
- All required features implemented and demonstrated.  
- At least **5 unit tests** (happy paths + edge cases).  
- A clear **README** with setup steps, usage examples, and limitations.  
- Code formatted with **black** and linted with **ruff/flake8**.  
- Public functions include **type hints**; `mypy` passes or deviations are documented.  

---

## 83. Skills: json, shuffling, scoring, input validation.

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

## 84. Milestones: Randomize answers; categories; percentage score.

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

## 85. Stretch goals: Timed questions and leader board file.

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

## 86. 18. String Templater for Emails

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

## 87. What you build: Fill placeholders in templates (e.g., {name}) from CSV.

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

## 88. Skills: format maps, csv DictReader, file writing.

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

## 89. Milestones: Preview mode; output one file per row.

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

## 90. Stretch goals: Jinja2 templating for loops/conditions.

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

## 91. 19. Countdown Pomodoro

### Overview & Core Skills

**What you’re building:** Time utilities for alarms and timers with cancellation and snooze.

**Core skills:** Datetime parsing, loops, persistence.


### Required Features

- **Parse 'HH:MM' or durations (e.g., 10m, 1h)** — **Difficulty 2/5**
  - **What it teaches:**
    - datetime parsing
    - Edge cases around midnight
  - **Acceptance criteria:**
    - Invalid times rejected; tests
- **Countdown loop and notifications** — **Difficulty 1/5**
  - **What it teaches:**
    - time.sleep()
    - Loop design
  - **Acceptance criteria:**
    - Accurate countdown within 1s
- **Cancel/snooze** — **Difficulty 2/5**
  - **What it teaches:**
    - State transitions
    - Signals/KeyboardInterrupt
  - **Acceptance criteria:**
    - User can cancel or snooze safely
- **Multiple alarms** — **Difficulty 2/5**
  - **What it teaches:**
    - Data structures
    - Scheduling
  - **Acceptance criteria:**
    - Run multiple without blocking UI

### Bonus Features

- **Persist alarms to JSON** — **Difficulty 1/5**
  - **What it teaches:**
    - Serialization
  - **Acceptance criteria:**
    - Alarms restored on restart
- **Natural language times** — **Difficulty 3/5**
  - **What it teaches:**
    - Parsing libraries
    - Ambiguity handling
  - **Acceptance criteria:**
    - 'in 5 minutes' works predictably
- **System notifications/sounds** — **Difficulty 2/5**
  - **What it teaches:**
    - Cross‑platform nuances
  - **Acceptance criteria:**
    - Works on macOS/Win/Linux (documented)


**Requirements for Project Completion**  
- All required features implemented and demonstrated.  
- At least **5 unit tests** (happy paths + edge cases).  
- A clear **README** with setup steps, usage examples, and limitations.  
- Code formatted with **black** and linted with **ruff/flake8**.  
- Public functions include **type hints**; `mypy` passes or deviations are documented.  

---

## 92. What you build: Pomodoro timer with work/break cycles in terminal.

### Overview & Core Skills

**What you’re building:** Focus timer with logging and summaries.

**Core skills:** State machines, timing, data aggregation.


### Required Features

- **Work/break cycles** — **Difficulty 1/5**
  - **What it teaches:**
    - State machine
    - Timing
  - **Acceptance criteria:**
    - Default 25/5 works; configurable
- **Countdown & notifications** — **Difficulty 1/5**
  - **What it teaches:**
    - time.sleep
    - UX
  - **Acceptance criteria:**
    - Accurate countdown; notifications at transitions
- **Pause/resume** — **Difficulty 2/5**
  - **What it teaches:**
    - State control
    - Signal handling
  - **Acceptance criteria:**
    - No drift after resume
- **Daily log** — **Difficulty 1/5**
  - **What it teaches:**
    - CSV/JSON logging
  - **Acceptance criteria:**
    - Session logged with timestamps

### Bonus Features

- **Custom schedules** — **Difficulty 2/5**
  - **What it teaches:**
    - Config files
  - **Acceptance criteria:**
    - YAML/JSON schedule applied
- **Weekly summary** — **Difficulty 2/5**
  - **What it teaches:**
    - Aggregation
  - **Acceptance criteria:**
    - Summary of sessions per day
- **Sound themes** — **Difficulty 1/5**
  - **What it teaches:**
    - Assets mgmt
  - **Acceptance criteria:**
    - Selectable sound pack


**Requirements for Project Completion**  
- All required features implemented and demonstrated.  
- At least **5 unit tests** (happy paths + edge cases).  
- A clear **README** with setup steps, usage examples, and limitations.  
- Code formatted with **black** and linted with **ruff/flake8**.  
- Public functions include **type hints**; `mypy` passes or deviations are documented.  

---

## 93. Skills: loops, sleep, simple state machine.

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

## 94. Milestones: Configurable durations; session summary.

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

## 95. Stretch goals: Sound notifications and daily log CSV.

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

## 96. 20. Tip & Bill Splitter

### Overview & Core Skills

**What you’re building:** Bill calculator with taxes, tips, and split logic.

**Core skills:** Decimal math, rounding, CSV export.


### Required Features

- **Subtotal, tax, tip calculation** — **Difficulty 1/5**
  - **What it teaches:**
    - Float vs Decimal
    - Rounding
  - **Acceptance criteria:**
    - Matches reference calculator within cents
- **Split evenly among diners** — **Difficulty 1/5**
  - **What it teaches:**
    - Division
    - Edge cases
  - **Acceptance criteria:**
    - 1..N diners works; remainders handled
- **Rounding strategy options** — **Difficulty 2/5**
  - **What it teaches:**
    - Bankers vs away‑from‑zero
  - **Acceptance criteria:**
    - User selects rounding mode
- **Input validation** — **Difficulty 1/5**
  - **What it teaches:**
    - Parsing
    - Error messages
  - **Acceptance criteria:**
    - Reject negative amounts; non‑numeric

### Bonus Features

- **Uneven splits** — **Difficulty 2/5**
  - **What it teaches:**
    - Weights/percentages
  - **Acceptance criteria:**
    - Shares by weight/percent
- **Receipt export** — **Difficulty 1/5**
  - **What it teaches:**
    - Text/CSV export
  - **Acceptance criteria:**
    - Printable receipt generated
- **Service fees & discounts** — **Difficulty 2/5**
  - **What it teaches:**
    - Order of operations
  - **Acceptance criteria:**
    - Configurable fee application order


**Requirements for Project Completion**  
- All required features implemented and demonstrated.  
- At least **5 unit tests** (happy paths + edge cases).  
- A clear **README** with setup steps, usage examples, and limitations.  
- Code formatted with **black** and linted with **ruff/flake8**.  
- Public functions include **type hints**; `mypy` passes or deviations are documented.  

---

## 97. What you build: Compute tip %, tax, and split among diners.

### Overview & Core Skills

**What you’re building:** Bill calculator with taxes, tips, and split logic.

**Core skills:** Decimal math, rounding, CSV export.


### Required Features

- **Subtotal, tax, tip calculation** — **Difficulty 1/5**
  - **What it teaches:**
    - Float vs Decimal
    - Rounding
  - **Acceptance criteria:**
    - Matches reference calculator within cents
- **Split evenly among diners** — **Difficulty 1/5**
  - **What it teaches:**
    - Division
    - Edge cases
  - **Acceptance criteria:**
    - 1..N diners works; remainders handled
- **Rounding strategy options** — **Difficulty 2/5**
  - **What it teaches:**
    - Bankers vs away‑from‑zero
  - **Acceptance criteria:**
    - User selects rounding mode
- **Input validation** — **Difficulty 1/5**
  - **What it teaches:**
    - Parsing
    - Error messages
  - **Acceptance criteria:**
    - Reject negative amounts; non‑numeric

### Bonus Features

- **Uneven splits** — **Difficulty 2/5**
  - **What it teaches:**
    - Weights/percentages
  - **Acceptance criteria:**
    - Shares by weight/percent
- **Receipt export** — **Difficulty 1/5**
  - **What it teaches:**
    - Text/CSV export
  - **Acceptance criteria:**
    - Printable receipt generated
- **Service fees & discounts** — **Difficulty 2/5**
  - **What it teaches:**
    - Order of operations
  - **Acceptance criteria:**
    - Configurable fee application order


**Requirements for Project Completion**  
- All required features implemented and demonstrated.  
- At least **5 unit tests** (happy paths + edge cases).  
- A clear **README** with setup steps, usage examples, and limitations.  
- Code formatted with **black** and linted with **ruff/flake8**.  
- Public functions include **type hints**; `mypy` passes or deviations are documented.  

---

## 98. Skills: float math, rounding, input sanitization.

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

## 99. Milestones: Handle uneven splits; service fee option.

### Overview & Core Skills

**What you’re building:** A small but complete CLI application focusing on clean input handling, core logic, and simple persistence.

**Core skills:** CLI parsing, functions, tests, JSON/CSV I/O.


### Required Features

- **Subtotal, tax, tip calculation** — **Difficulty 1/5**
  - **What it teaches:**
    - Float vs Decimal
    - Rounding
  - **Acceptance criteria:**
    - Matches reference calculator within cents
- **Split evenly among diners** — **Difficulty 1/5**
  - **What it teaches:**
    - Division
    - Edge cases
  - **Acceptance criteria:**
    - 1..N diners works; remainders handled
- **Rounding strategy options** — **Difficulty 2/5**
  - **What it teaches:**
    - Bankers vs away‑from‑zero
  - **Acceptance criteria:**
    - User selects rounding mode
- **Input validation** — **Difficulty 1/5**
  - **What it teaches:**
    - Parsing
    - Error messages
  - **Acceptance criteria:**
    - Reject negative amounts; non‑numeric

### Bonus Features

- **Uneven splits** — **Difficulty 2/5**
  - **What it teaches:**
    - Weights/percentages
  - **Acceptance criteria:**
    - Shares by weight/percent
- **Receipt export** — **Difficulty 1/5**
  - **What it teaches:**
    - Text/CSV export
  - **Acceptance criteria:**
    - Printable receipt generated
- **Service fees & discounts** — **Difficulty 2/5**
  - **What it teaches:**
    - Order of operations
  - **Acceptance criteria:**
    - Configurable fee application order


**Requirements for Project Completion**  
- All required features implemented and demonstrated.  
- At least **5 unit tests** (happy paths + edge cases).  
- A clear **README** with setup steps, usage examples, and limitations.  
- Code formatted with **black** and linted with **ruff/flake8**.  
- Public functions include **type hints**; `mypy` passes or deviations are documented.  

---

## 100. Stretch goals: Export receipt as text.

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

## 101. 21. BMI & Calorie Calculator

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

## 102. What you build: Compute BMI and estimate daily calories.

### Overview & Core Skills

**What you’re building:** Health metrics tool with profiles and charts.

**Core skills:** Formulas, unit conversion, plotting.


### Required Features

- **Compute BMI & category** — **Difficulty 1/5**
  - **What it teaches:**
    - Formulas
    - Branching
  - **Acceptance criteria:**
    - Correct thresholds applied
- **Metric/imperial units** — **Difficulty 1/5**
  - **What it teaches:**
    - Unit conversion
  - **Acceptance criteria:**
    - Conversions validated by tests
- **BMR & calorie estimate** — **Difficulty 2/5**
  - **What it teaches:**
    - Mifflin‑St Jeor/Harris‑Benedict
  - **Acceptance criteria:**
    - Activity multipliers applied
- **Profiles saved to JSON** — **Difficulty 1/5**
  - **What it teaches:**
    - Persistence
  - **Acceptance criteria:**
    - Load/update profiles

### Bonus Features

- **Charts over time** — **Difficulty 2/5**
  - **What it teaches:**
    - matplotlib
  - **Acceptance criteria:**
    - BMI over time plotted
- **Goal tracking** — **Difficulty 2/5**
  - **What it teaches:**
    - Delta calculations
  - **Acceptance criteria:**
    - Progress to target weight shown
- **Health tips (static)** — **Difficulty 1/5**
  - **What it teaches:**
    - Content design
  - **Acceptance criteria:**
    - Shows curated tips per category


**Requirements for Project Completion**  
- All required features implemented and demonstrated.  
- At least **5 unit tests** (happy paths + edge cases).  
- A clear **README** with setup steps, usage examples, and limitations.  
- Code formatted with **black** and linted with **ruff/flake8**.  
- Public functions include **type hints**; `mypy` passes or deviations are documented.  

---

## 103. Skills: formulas, constants, branching.

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

## 104. Milestones: Metric/imperial; sensible validation.

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

## 105. Stretch goals: Save personal profiles in JSON.

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

## 106. 22. Simple Interest & Compound Calculator

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

## 107. What you build: Compute interest over time; show yearly table.

### Overview & Core Skills

**What you’re building:** Financial calculator for simple/compound interest with exports.

**Core skills:** Math, loops, CSV, CLI.


### Required Features

- **Simple interest table** — **Difficulty 1/5**
  - **What it teaches:**
    - Loops
    - Formatting
  - **Acceptance criteria:**
    - Yearly rows correct
- **Compound interest by period** — **Difficulty 2/5**
  - **What it teaches:**
    - Compounding math
  - **Acceptance criteria:**
    - Monthly/quarterly/yearly handled
- **CSV export** — **Difficulty 1/5**
  - **What it teaches:**
    - CSV writing
  - **Acceptance criteria:**
    - Headers correct; numeric formatting
- **CLI options** — **Difficulty 1/5**
  - **What it teaches:**
    - argparse
  - **Acceptance criteria:**
    - --principal, --rate, --years, --periods

### Bonus Features

- **ASCII chart of growth** — **Difficulty 2/5**
  - **What it teaches:**
    - Text plotting
  - **Acceptance criteria:**
    - Monotonic curve rendered
- **IRR approximation (optional)** — **Difficulty 3/5**
  - **What it teaches:**
    - Root finding
  - **Acceptance criteria:**
    - Converges for valid cashflows
- **Multiple scenarios compare** — **Difficulty 2/5**
  - **What it teaches:**
    - Batch runs
  - **Acceptance criteria:**
    - Side‑by‑side tables


**Requirements for Project Completion**  
- All required features implemented and demonstrated.  
- At least **5 unit tests** (happy paths + edge cases).  
- A clear **README** with setup steps, usage examples, and limitations.  
- Code formatted with **black** and linted with **ruff/flake8**.  
- Public functions include **type hints**; `mypy` passes or deviations are documented.  

---

## 108. Skills: loops, math, formatting tables.

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

## 109. Milestones: Compound intervals; export CSV.

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

## 110. Stretch goals: ASCII chart of growth.

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

## 111. 23. Calendar Viewer

### Overview & Core Skills

**What you’re building:** Calendar printer with utility helpers and exports.

**Core skills:** calendar module, datetime, CLI UX.


### Required Features

- **Month/year calendars** — **Difficulty 1/5**
  - **What it teaches:**
    - calendar module
  - **Acceptance criteria:**
    - Matches system calendar
- **Highlight today & weekends** — **Difficulty 1/5**
  - **What it teaches:**
    - Formatting
  - **Acceptance criteria:**
    - Visual emphasis present
- **Jump to date utilities** — **Difficulty 1/5**
  - **What it teaches:**
    - datetime math
  - **Acceptance criteria:**
    - Next Friday/first Monday functions
- **CLI options** — **Difficulty 1/5**
  - **What it teaches:**
    - argparse
  - **Acceptance criteria:**
    - --month, --year, --today

### Bonus Features

- **iCal export for birthdays** — **Difficulty 2/5**
  - **What it teaches:**
    - ics file format
  - **Acceptance criteria:**
    - Valid .ics generated
- **Holiday highlighting** — **Difficulty 2/5**
  - **What it teaches:**
    - Lookup tables
  - **Acceptance criteria:**
    - Country settable; docs provided
- **Pay period calculator** — **Difficulty 2/5**
  - **What it teaches:**
    - Date arithmetic
  - **Acceptance criteria:**
    - Next payday computed


**Requirements for Project Completion**  
- All required features implemented and demonstrated.  
- At least **5 unit tests** (happy paths + edge cases).  
- A clear **README** with setup steps, usage examples, and limitations.  
- Code formatted with **black** and linted with **ruff/flake8**.  
- Public functions include **type hints**; `mypy` passes or deviations are documented.  

---

## 112. What you build: Show month/year calendars and upcoming dates.

### Overview & Core Skills

**What you’re building:** Calendar printer with utility helpers and exports.

**Core skills:** calendar module, datetime, CLI UX.


### Required Features

- **Month/year calendars** — **Difficulty 1/5**
  - **What it teaches:**
    - calendar module
  - **Acceptance criteria:**
    - Matches system calendar
- **Highlight today & weekends** — **Difficulty 1/5**
  - **What it teaches:**
    - Formatting
  - **Acceptance criteria:**
    - Visual emphasis present
- **Jump to date utilities** — **Difficulty 1/5**
  - **What it teaches:**
    - datetime math
  - **Acceptance criteria:**
    - Next Friday/first Monday functions
- **CLI options** — **Difficulty 1/5**
  - **What it teaches:**
    - argparse
  - **Acceptance criteria:**
    - --month, --year, --today

### Bonus Features

- **iCal export for birthdays** — **Difficulty 2/5**
  - **What it teaches:**
    - ics file format
  - **Acceptance criteria:**
    - Valid .ics generated
- **Holiday highlighting** — **Difficulty 2/5**
  - **What it teaches:**
    - Lookup tables
  - **Acceptance criteria:**
    - Country settable; docs provided
- **Pay period calculator** — **Difficulty 2/5**
  - **What it teaches:**
    - Date arithmetic
  - **Acceptance criteria:**
    - Next payday computed


**Requirements for Project Completion**  
- All required features implemented and demonstrated.  
- At least **5 unit tests** (happy paths + edge cases).  
- A clear **README** with setup steps, usage examples, and limitations.  
- Code formatted with **black** and linted with **ruff/flake8**.  
- Public functions include **type hints**; `mypy` passes or deviations are documented.  

---

## 113. Skills: calendar module, datetime, CLI options.

### Overview & Core Skills

**What you’re building:** Calendar printer with utility helpers and exports.

**Core skills:** calendar module, datetime, CLI UX.


### Required Features

- **Month/year calendars** — **Difficulty 1/5**
  - **What it teaches:**
    - calendar module
  - **Acceptance criteria:**
    - Matches system calendar
- **Highlight today & weekends** — **Difficulty 1/5**
  - **What it teaches:**
    - Formatting
  - **Acceptance criteria:**
    - Visual emphasis present
- **Jump to date utilities** — **Difficulty 1/5**
  - **What it teaches:**
    - datetime math
  - **Acceptance criteria:**
    - Next Friday/first Monday functions
- **CLI options** — **Difficulty 1/5**
  - **What it teaches:**
    - argparse
  - **Acceptance criteria:**
    - --month, --year, --today

### Bonus Features

- **iCal export for birthdays** — **Difficulty 2/5**
  - **What it teaches:**
    - ics file format
  - **Acceptance criteria:**
    - Valid .ics generated
- **Holiday highlighting** — **Difficulty 2/5**
  - **What it teaches:**
    - Lookup tables
  - **Acceptance criteria:**
    - Country settable; docs provided
- **Pay period calculator** — **Difficulty 2/5**
  - **What it teaches:**
    - Date arithmetic
  - **Acceptance criteria:**
    - Next payday computed


**Requirements for Project Completion**  
- All required features implemented and demonstrated.  
- At least **5 unit tests** (happy paths + edge cases).  
- A clear **README** with setup steps, usage examples, and limitations.  
- Code formatted with **black** and linted with **ruff/flake8**.  
- Public functions include **type hints**; `mypy` passes or deviations are documented.  

---

## 114. Milestones: Highlight today; jump to next payday/Friday.

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

## 115. Stretch goals: iCal export for birthdays.

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

## 116. 24. Flashcards (CLI)

### Overview & Core Skills

**What you’re building:** Study helper with spaced repetition and import/export.

**Core skills:** CSV, scheduling, stats.


### Required Features

- **Load Q/A from CSV** — **Difficulty 1/5**
  - **What it teaches:**
    - CSV I/O
  - **Acceptance criteria:**
    - Handles missing/extra columns
- **Randomized practice** — **Difficulty 1/5**
  - **What it teaches:**
    - random
  - **Acceptance criteria:**
    - Shuffles deck per session
- **Track correctness** — **Difficulty 2/5**
  - **What it teaches:**
    - State
    - Scoring
  - **Acceptance criteria:**
    - Per‑card stats kept
- **Promote/demote difficulty** — **Difficulty 2/5**
  - **What it teaches:**
    - Spaced repetition basics
  - **Acceptance criteria:**
    - Cards move between buckets

### Bonus Features

- **Leitner system** — **Difficulty 2/5**
  - **What it teaches:**
    - Scheduling
  - **Acceptance criteria:**
    - Session plan by box
- **Import/Export sessions** — **Difficulty 2/5**
  - **What it teaches:**
    - Serialization
  - **Acceptance criteria:**
    - Shareable session files
- **Tag‑based decks** — **Difficulty 2/5**
  - **What it teaches:**
    - Filtering
  - **Acceptance criteria:**
    - Study subsets by tag


**Requirements for Project Completion**  
- All required features implemented and demonstrated.  
- At least **5 unit tests** (happy paths + edge cases).  
- A clear **README** with setup steps, usage examples, and limitations.  
- Code formatted with **black** and linted with **ruff/flake8**.  
- Public functions include **type hints**; `mypy` passes or deviations are documented.  

---

## 117. What you build: Flip Q/A cards from CSV; spaced repetition lite.

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

## 118. Skills: csv, randomization, simple scheduling.

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

## 119. Milestones: Track correctness; promote/demote difficulty.

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

## 120. Stretch goals: Leitner box algorithm.

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

## 121. 25. File Organizer

### Overview & Core Skills

**What you’re building:** File tidier that moves files safely by rules with a dry‑run.

**Core skills:** Filesystem operations, hashing, YAML config.


### Required Features

- **Dry‑run preview** — **Difficulty 2/5**
  - **What it teaches:**
    - Safety practices
  - **Acceptance criteria:**
    - No files moved in preview
- **Move by extension** — **Difficulty 1/5**
  - **What it teaches:**
    - pathlib
    - shutil
  - **Acceptance criteria:**
    - Correct destination folders
- **Handle name collisions** — **Difficulty 2/5**
  - **What it teaches:**
    - De‑dup strategies
  - **Acceptance criteria:**
    - No overwrites; increments suffix
- **Ignore patterns** — **Difficulty 2/5**
  - **What it teaches:**
    - Glob patterns
  - **Acceptance criteria:**
    - Skips configured patterns

### Bonus Features

- **Rules via YAML** — **Difficulty 2/5**
  - **What it teaches:**
    - Config mgmt
  - **Acceptance criteria:**
    - Rules validated and applied
- **Duplicate detection** — **Difficulty 3/5**
  - **What it teaches:**
    - Hashes
  - **Acceptance criteria:**
    - Detect and move dupes to a folder
- **Undo last run** — **Difficulty 3/5**
  - **What it teaches:**
    - Command logs
  - **Acceptance criteria:**
    - Reverses the previous changes


**Requirements for Project Completion**  
- All required features implemented and demonstrated.  
- At least **5 unit tests** (happy paths + edge cases).  
- A clear **README** with setup steps, usage examples, and limitations.  
- Code formatted with **black** and linted with **ruff/flake8**.  
- Public functions include **type hints**; `mypy` passes or deviations are documented.  

---

## 122. What you build: Move files into folders by extension (Pictures, Docs…).

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

## 123. Skills: pathlib, os, shutil, safety checks.

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

## 124. Milestones: Dry‑run preview; handle name collisions.

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

## 125. Stretch goals: Rules via YAML config.

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

## 126. 26. Text Adventure Mini‑Game

### Overview & Core Skills

**What you’re building:** Text adventure with rooms, inventory, and encounters; data‑driven levels.

**Core skills:** Graph modeling, serialization, randomness.


### Required Features

- **Map as graph (rooms/exits)** — **Difficulty 2/5**
  - **What it teaches:**
    - Graph modeling
    - Dicts of dicts
  - **Acceptance criteria:**
    - Consistent connectivity; dead ends documented
- **Inventory system** — **Difficulty 2/5**
  - **What it teaches:**
    - Collections
    - Game state
  - **Acceptance criteria:**
    - Pick up/drop/use items
- **Simple combat/encounters** — **Difficulty 2/5**
  - **What it teaches:**
    - Turn loop
    - Randomness
  - **Acceptance criteria:**
    - Win/lose conditions clear
- **Save/load game** — **Difficulty 2/5**
  - **What it teaches:**
    - Serialization design
  - **Acceptance criteria:**
    - Resume from save reliably

### Bonus Features

- **Map loader from JSON** — **Difficulty 2/5**
  - **What it teaches:**
    - Data‑driven design
  - **Acceptance criteria:**
    - Level files define rooms/NPCs
- **Procedural events** — **Difficulty 3/5**
  - **What it teaches:**
    - Generators
    - Random events
  - **Acceptance criteria:**
    - Encounter rates configurable
- **Scripting hooks** — **Difficulty 4/5**
  - **What it teaches:**
    - Mini DSL or callback registry
  - **Acceptance criteria:**
    - Room/item scripts extend gameplay


**Requirements for Project Completion**  
- All required features implemented and demonstrated.  
- At least **5 unit tests** (happy paths + edge cases).  
- A clear **README** with setup steps, usage examples, and limitations.  
- Code formatted with **black** and linted with **ruff/flake8**.  
- Public functions include **type hints**; `mypy` passes or deviations are documented.  

---

## 127. What you build: Navigate rooms with inventory and simple combat.

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

## 128. Skills: dicts as graphs, loops, functions.

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

## 129. Milestones: Map loader from JSON; save/load game.

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

## 130. Stretch goals: Random encounters and items.

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

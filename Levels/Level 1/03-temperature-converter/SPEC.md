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

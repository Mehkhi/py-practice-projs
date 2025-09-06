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

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

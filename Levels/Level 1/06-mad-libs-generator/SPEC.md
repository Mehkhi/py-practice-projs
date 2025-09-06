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

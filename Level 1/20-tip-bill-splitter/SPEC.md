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

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

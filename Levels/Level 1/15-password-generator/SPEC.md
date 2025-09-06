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

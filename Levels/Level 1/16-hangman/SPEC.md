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

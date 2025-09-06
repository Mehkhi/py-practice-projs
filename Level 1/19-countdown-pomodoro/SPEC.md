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

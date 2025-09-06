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

## 31. 7. Palindrome & Anagram Checker

### Overview & Core Skills

**What you’re building:** Text analyzers focused on robust normalization and comparison.

**Core skills:** Unicode handling, collections, tests.


### Required Features

- **Normalization (case, spaces, punctuation)** — **Difficulty 2/5**
  - **What it teaches:**
    - Unicode/ASCII handling
    - Translation tables
  - **Acceptance criteria:**
    - Same result for 'A man, a plan…'
- **Palindrome check** — **Difficulty 1/5**
  - **What it teaches:**
    - Slicing
    - Two‑pointer technique
  - **Acceptance criteria:**
    - Odd/even length handled
- **Anagram check** — **Difficulty 2/5**
  - **What it teaches:**
    - collections.Counter
    - Sorting
  - **Acceptance criteria:**
    - Ignores spaces/punctuation
- **Unit tests** — **Difficulty 1/5**
  - **What it teaches:**
    - pytest basics
  - **Acceptance criteria:**
    - Dozens of cases incl. unicode

### Bonus Features

- **Batch file mode** — **Difficulty 2/5**
  - **What it teaches:**
    - File I/O
    - CLI parsing
  - **Acceptance criteria:**
    - Reads list and prints results
- **Performance on large lists** — **Difficulty 2/5**
  - **What it teaches:**
    - Algorithmic complexity
  - **Acceptance criteria:**
    - Handles 10k+ pairs quickly
- **Interactive hints** — **Difficulty 1/5**
  - **What it teaches:**
    - UX
  - **Acceptance criteria:**
    - Explain why not palindrome/anagram


**Requirements for Project Completion**  
- All required features implemented and demonstrated.  
- At least **5 unit tests** (happy paths + edge cases).  
- A clear **README** with setup steps, usage examples, and limitations.  
- Code formatted with **black** and linted with **ruff/flake8**.  
- Public functions include **type hints**; `mypy` passes or deviations are documented.  

---

## 32. What you build: Check if text is a palindrome; detect anagrams between two phrases.

### Overview & Core Skills

**What you’re building:** Text analyzers focused on robust normalization and comparison.

**Core skills:** Unicode handling, collections, tests.


### Required Features

- **Normalization (case, spaces, punctuation)** — **Difficulty 2/5**
  - **What it teaches:**
    - Unicode/ASCII handling
    - Translation tables
  - **Acceptance criteria:**
    - Same result for 'A man, a plan…'
- **Palindrome check** — **Difficulty 1/5**
  - **What it teaches:**
    - Slicing
    - Two‑pointer technique
  - **Acceptance criteria:**
    - Odd/even length handled
- **Anagram check** — **Difficulty 2/5**
  - **What it teaches:**
    - collections.Counter
    - Sorting
  - **Acceptance criteria:**
    - Ignores spaces/punctuation
- **Unit tests** — **Difficulty 1/5**
  - **What it teaches:**
    - pytest basics
  - **Acceptance criteria:**
    - Dozens of cases incl. unicode

### Bonus Features

- **Batch file mode** — **Difficulty 2/5**
  - **What it teaches:**
    - File I/O
    - CLI parsing
  - **Acceptance criteria:**
    - Reads list and prints results
- **Performance on large lists** — **Difficulty 2/5**
  - **What it teaches:**
    - Algorithmic complexity
  - **Acceptance criteria:**
    - Handles 10k+ pairs quickly
- **Interactive hints** — **Difficulty 1/5**
  - **What it teaches:**
    - UX
  - **Acceptance criteria:**
    - Explain why not palindrome/anagram


**Requirements for Project Completion**  
- All required features implemented and demonstrated.  
- At least **5 unit tests** (happy paths + edge cases).  
- A clear **README** with setup steps, usage examples, and limitations.  
- Code formatted with **black** and linted with **ruff/flake8**.  
- Public functions include **type hints**; `mypy` passes or deviations are documented.  

---

## 33. Skills: string methods, normalization, collections.Counter.

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

## 34. Milestones: Ignore punctuation/spacing; add unit tests.

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

## 35. Stretch goals: CLI mode with argparse and batch file input.

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

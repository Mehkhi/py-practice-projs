### 14) Production‑Grade CLI (click)
**What you’re building:** A robust CLI with subcommands, config, and logging.
**Core skills:** click, logging, config management, UX polish.

#### Required Features
- **R1. Subcommands & help** — **Difficulty 2/5**
  - **What it teaches:** Click groups, options, argument parsing.
  - **Acceptance criteria:** `--help` is clear; exit codes meaningful.

- **R2. Config files & precedence** — **Difficulty 2/5**
  - **What it teaches:** Search order (env → CLI → file), validation.
  - **Acceptance criteria:** Precedence honored; error on invalid config.

- **R3. Logging & progress bars** — **Difficulty 2/5**
  - **What it teaches:** Structured logs; progress feedback.
  - **Acceptance criteria:** `--log-level` works; progress bars update correctly.

- **R4. Testable core** — **Difficulty 2/5**
  - **What it teaches:** Keeping business logic out of CLI glue for tests.
  - **Acceptance criteria:** Unit tests import and test core functions directly.

#### Bonus Features
- **B1. Plugins via entry points** — **Difficulty 3/5**
  - **Teaches:** Dynamic command discovery.
  - **Acceptance:** Plugin package adds a new subcommand without code changes.

- **B2. Shell completions** — **Difficulty 2/5**
  - **Teaches:** Generating completion scripts.
  - **Acceptance:** Bash/Zsh completions install and work.

- **B3. Rich TUI output** — **Difficulty 2/5**
  - **Teaches:** `rich` tables, status spinners, tracebacks.
  - **Acceptance:** Commands render readable tables/tracebacks.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

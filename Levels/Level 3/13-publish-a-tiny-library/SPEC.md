### 13) Publish a Tiny Library
**What you’re building:** A small utility library with tests and packaging.
**Core skills:** `pyproject.toml`, packaging, versioning, CI tests.

#### Required Features
- **R1. Package skeleton** — **Difficulty 2/5**
  - **What it teaches:** Source layout (`src/`), metadata, classifiers.
  - **Acceptance criteria:** `pip install -e .` works; console scripts defined if needed.

- **R2. Tests & coverage** — **Difficulty 2/5**
  - **What it teaches:** `pytest` layout, coverage gate.
  - **Acceptance criteria:** Coverage ≥ 85%; CI green.

- **R3. Versioning & changelog** — **Difficulty 2/5**
  - **What it teaches:** SemVer; `__version__`; keep a `CHANGELOG.md`.
  - **Acceptance criteria:** Version bump pipeline documented.

- **R4. README & examples** — **Difficulty 1/5**
  - **What it teaches:** Clear docs and quickstart.
  - **Acceptance criteria:** README shows install/usage; examples run.

#### Bonus Features
- **B1. TestPyPI publish** — **Difficulty 2/5**
  - **Teaches:** Build (`build`/`hatch`) and upload (`twine`).
  - **Acceptance:** Package appears on TestPyPI; installable.

- **B2. Semantic release** — **Difficulty 3/5**
  - **Teaches:** Conventional commits; auto versioning.
  - **Acceptance:** Tag/release generated from commit messages.

- **B3. Typing & stubs** — **Difficulty 2/5**
  - **Teaches:** PEP 561 typing; `py.typed` marker.
  - **Acceptance:** Editors show rich intellisense; mypy passes for consumers.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

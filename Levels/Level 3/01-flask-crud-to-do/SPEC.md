### 1) Flask CRUD To‑Do (Full App)
**What you’re building:** Multi‑user to‑do app with authentication, SQLite, and templates.
**Core skills:** SQLAlchemy ORM, blueprints, CSRF, sessions, template design.

#### Required Features
- **R1. Data model & migrations** — **Difficulty 2/5**
  - **What it teaches:**
    - Modeling users and tasks (User, Task) with relationships and indexes.
    - Alembic migrations for schema evolution and deterministic DB state.
    - `nullable`, `unique`, and foreign key constraints as correctness tools.
  - **Acceptance criteria:**
    - `alembic upgrade head` creates tables reliably; downgrade works.
    - Index present on `(user_id, completed, due_at)`.

- **R2. Auth: register/login/logout with password hashing** — **Difficulty 3/5**
  - **What it teaches:**
    - `werkzeug.security` (or `argon2/bcrypt`) hashing & constant‑time checks.
    - Session management and secure cookies; remember‑me cookies trade‑offs.
    - CSRF protection on forms.
  - **Acceptance criteria:**
    - New user can register and log in; wrong password rejected without timing leak.
    - CSRF token required on POST forms.

- **R3. CRUD with filtering, sort, and pagination** — **Difficulty 3/5**
  - **What it teaches:**
    - Query composition (search by title, filter by status, due date ranges).
    - Pagination patterns (`limit/offset`) and UX for next/prev links.
    - Preventing N+1 queries with eager loading when needed.
  - **Acceptance criteria:**
    - List view supports `?status=open&sort=due_at&page=2` and is stable across refreshes.

- **R4. Flash messages & error handling** — **Difficulty 2/5**
  - **What it teaches:**
    - User feedback via `flash()`; redirect‑after‑POST.
    - Centralized error handlers (404/500) with friendly pages.
  - **Acceptance criteria:**
    - All CRUD flows show success/error flashes; custom 404/500 pages served.

#### Bonus Features
- **B1. RBAC and ownership checks** — **Difficulty 3/5**
  - **Teaches:** Role decorators, per‑record authorization, secure query filters.
  - **Acceptance:** Non‑owners cannot access/modify others’ tasks; admin can.

- **B2. Admin panel** — **Difficulty 3/5**
  - **Teaches:** Admin blueprint, list/search users, deactivate accounts.
  - **Acceptance:** Admin can list users and toggle active flag; audited changes.

- **B3. Rate limiting & audit log** — **Difficulty 3/5**
  - **Teaches:** Flask‑Limiter (or custom), structured audit logging.
  - **Acceptance:** Excessive POSTs return 429; audit entries persisted.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

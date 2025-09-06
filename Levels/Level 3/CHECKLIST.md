# Level 3 — Intermediate (Mid-level Developer)

Build real applications: production‑like web apps, async work, packaging, documentation, CI, and deeper algorithms/data handling.

## Checklist

- [ ] 1. Flask CRUD To‑Do (Full App)
  - What you build: Multi‑user to‑do with auth, SQLite, and templates.
  - Skills: ORM/SQLAlchemy, blueprints, CSRF, sessions.
  - Milestones: Edit/delete; filtering; pagination; flash messages.
  - Stretch goals: Role‑based access control (RBAC).

- [ ] 2. Auth Basics & Password Hashing
  - What you build: Login/logout with salted hashing and sessions.
  - Skills: werkzeug.security, session mgmt, secure cookies.
  - Milestones: Password reset tokens; email flow (dev mode).
  - Stretch goals: Rate limiting and account lockout.

- [ ] 3. REST API for To‑Do (FastAPI)
  - What you build: Expose CRUD endpoints with pydantic schemas.
  - Skills: FastAPI, pydantic, dependency injection, OpenAPI.
  - Milestones: Validation errors; pagination; filtering.
  - Stretch goals: JWT auth and API keys.

- [ ] 4. Async Web Scraper
  - What you build: Crawl many pages concurrently and store results.
  - Skills: asyncio, aiohttp, semaphore, backoff.
  - Milestones: Retry on failures; polite delays; caching.
  - Stretch goals: Pluggable pipelines (save to CSV/SQLite).

- [ ] 5. Background Jobs with Redis
  - What you build: Queue tasks and process with workers (RQ).
  - Skills: Redis, job queues, idempotency, retry.
  - Milestones: Job status tracking; dead‑letter queue.
  - Stretch goals: Scheduled/delayed jobs.

- [ ] 6. File Upload Service
  - What you build: Upload files via web form and serve securely.
  - Skills: Flask/FastAPI streaming, MIME checks, temp files.
  - Milestones: Virus scan hook; size limits; presigned URLs (local emulation).
  - Stretch goals: Chunked uploads and resume.

- [ ] 7. PDF Search (Mini Index)
  - What you build: Extract text and build an inverted index for search.
  - Skills: pdfminer/pypdf, tokenization, indexing.
  - Milestones: Phrase queries; ranking; snippets.
  - Stretch goals: Boolean operators and field weights.

- [ ] 8. EDA on Public Dataset
  - What you build: Clean, analyze, and visualize a dataset end‑to‑end.
  - Skills: pandas, groupby, plotting, notebooks.
  - Milestones: Data quality report; clear charts; README.
  - Stretch goals: Simple regression/classification baseline.

- [ ] 9. Stock Tracker with DB
  - What you build: Fetch prices daily and chart history.
  - Skills: scheduling, HTTP APIs, pandas, matplotlib.
  - Milestones: Moving averages; alerts; dockerized service.
  - Stretch goals: Backtesting simple strategies.

- [ ] 10. Word‑Frequency Analyzer
  - What you build: Compute TF and TF‑IDF on text corpus.
  - Skills: nltk/spacy basics, stopwords, math/logs.
  - Milestones: Top terms per document; export report.
  - Stretch goals: Interactive search over corpus.

- [ ] 11. Multi‑Client Chat Server
  - What you build: Socket server supporting multiple clients and rooms.
  - Skills: sockets, threading, protocols, concurrency.
  - Milestones: Usernames; private messages; persistence.
  - Stretch goals: Asyncio version and WebSocket gateway.

- [ ] 12. Dockerize a Web App
  - What you build: Containerize your Flask/FastAPI app with Compose.
  - Skills: Dockerfile, Compose, env vars, volumes.
  - Milestones: Separate dev/prod configs; healthcheck.
  - Stretch goals: CI to build image on pushes.

- [ ] 13. Publish a Tiny Library
  - What you build: Create a utility lib with tests and packaging.
  - Skills: pyproject.toml, packaging, versioning, semver.
  - Milestones: Type hints; readme; CI tests.
  - Stretch goals: Prepare for PyPI publish (test index).

- [ ] 14. Production‑Grade CLI (click)
  - What you build: CLI with subcommands, config file, and logging.
  - Skills: click, logging, config management, UX.
  - Milestones: Colors; progress bars; good help pages.
  - Stretch goals: Plugins via entry points.

- [ ] 15. Requests Caching Layer
  - What you build: Add transparent caching to API calls.
  - Skills: requests-cache, cache keys, invalidation.
  - Milestones: Cache metrics; stale‑while‑revalidate.
  - Stretch goals: Pluggable backends (disk/Redis).

- [ ] 16. OAuth GitHub Viewer
  - What you build: Login with GitHub and list user repos/issues.
  - Skills: OAuth2 dance, sessions, pagination APIs.
  - Milestones: Rate‑limit handling; caching; retries.
  - Stretch goals: Star/unstar from the UI.

- [ ] 17. Graph Algorithms Visualizer
  - What you build: Visualize BFS/DFS/shortest paths on a graph.
  - Skills: networkx, matplotlib, algorithms.
  - Milestones: Weighted edges; export images.
  - Stretch goals: Interactive GUI with PyQt/PySimpleGUI.

- [ ] 18. Tetris with pygame
  - What you build: Playable Tetris with scoring and increasing speed.
  - Skills: pygame loop, collision, game state.
  - Milestones: Pause/resume; high scores; levels.
  - Stretch goals: Ghost piece and hold slot.

- [ ] 19. Folder Watch ETL
  - What you build: Watch a folder and transform new files automatically.
  - Skills: watchdog, pipelines, error handling.
  - Milestones: Retry policy; quarantine failures; metrics.
  - Stretch goals: Parallel processing per file type.

- [ ] 20. Structured Logging
  - What you build: JSON logs with correlation IDs and rotation.
  - Skills: logging config, filters, RotatingFileHandler.
  - Milestones: Log schema; log levels; sampling.
  - Stretch goals: Ship logs to Elasticsearch (local).

- [ ] 21. Config Management
  - What you build: Typed settings with env overrides.
  - Skills: pydantic/dynaconf, secrets, profiles.
  - Milestones: Validation errors; .env files.
  - Stretch goals: Dynamic reload of config.

- [ ] 22. Docs Site (Sphinx/MkDocs)
  - What you build: Host docs for one of your apps/libraries.
  - Skills: autodoc, code fences, site build.
  - Milestones: API reference; tutorials; versioned docs.
  - Stretch goals: Deploy docs on CI to Pages.

- [ ] 23. Test Suite Mastery
  - What you build: Mocks, fixtures, and coverage for a web app.
  - Skills: pytest, unittest.mock, coverage.
  - Milestones: 90%+ coverage; flake8/black/isort.
  - Stretch goals: Mutation testing (mutmut).

- [ ] 24. GitHub Actions CI
  - What you build: Run tests, linting, and build on every push.
  - Skills: YAML pipelines, caching, matrices.
  - Milestones: Badge in README; artifact uploads.
  - Stretch goals: Release on tags with changelog.

- [ ] 25. PyInstaller Distribution
  - What you build: Ship a CLI as a single binary/exe.
  - Skills: pyinstaller, entry points, assets.
  - Milestones: Cross‑platform notes; update strategy.
  - Stretch goals: Auto‑update check on start.

---

## Detailed Spec Sheets — Level 3 (Intermediate)

This section expands each Level 3 checklist item into an implementation spec with **required features** and **bonus features**. Every feature includes a **difficulty rating**, an **extensive breakdown of what it teaches**, and **acceptance criteria** you can self‑verify.

### Difficulty Legend
- **1** = Very easy (few lines, minimal edge cases)
- **2** = Easy (simple logic, basic edge cases)
- **3** = Moderate (multiple components, careful handling)
- **4** = Hard (non‑trivial algorithms/design, extensive testing)
- **5** = Very hard (complex algorithms or architecture)

### Common Requirements for Project Completion
- All **required features** implemented and demonstrated.
- At least **8 unit tests** per project (happy paths + edge cases + error paths).
- Clear **README** with setup, run steps, examples, and limitations.
- Code formatted with **black** and linted with **ruff/flake8**; import order via **isort**.
- Public functions/methods include **type hints**; `mypy` (or `pyright`) passes or justifications are documented.
- Meaningful **logging** and **graceful error messages** for user‑visible failures.

> Tip: Track each feature as a GitHub issue. Label with `difficulty/x`, `type/required` or `type/bonus`.

---

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

### 2) Auth Basics & Password Hashing
**What you’re building:** A standalone auth module and demo app that implements secure login flows.
**Core skills:** Hashing (argon2/bcrypt), sessions, secure cookies.

#### Required Features
- **R1. Password hashing & verification** — **Difficulty 2/5**
  - **What it teaches:** Peppering vs salting; parameter selection; migration strategies.
  - **Acceptance criteria:** Hash includes parameters; rehash on login if params outdated.

- **R2. Session management** — **Difficulty 2/5**
  - **What it teaches:** Secure cookie flags (HttpOnly, Secure, SameSite), session fixation prevention.
  - **Acceptance criteria:** New session ID issued on login/logout; cookies configured securely.

- **R3. Password reset tokens (dev email)** — **Difficulty 3/5**
  - **What it teaches:** Signed tokens with expiry; one‑time use; email templating.
  - **Acceptance criteria:** Reset link invalid after use/expiry; audit logged.

- **R4. Account lockout & rate limiting** — **Difficulty 3/5**
  - **What it teaches:** Brute‑force mitigation; cooldown vs exponential backoff.
  - **Acceptance criteria:** After N failures, further attempts delayed or blocked per policy.

#### Bonus Features
- **B1. 2FA via TOTP** — **Difficulty 3/5**
  - **Teaches:** Time‑based codes, clock skew, backup codes.
  - **Acceptance:** TOTP setup QR; verification required at login if enabled.

- **B2. OAuth login (Google/GitHub)** — **Difficulty 3/5**
  - **Teaches:** Federated identity, account linking.
  - **Acceptance:** First login links to local account; subsequent logins succeed.

- **B3. Password strength meter** — **Difficulty 2/5**
  - **Teaches:** zxcvbn‑style feedback; UX for suggestions.
  - **Acceptance:** Weak passwords flagged with actionable tips.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 3) REST API for To‑Do (FastAPI)
**What you’re building:** A JSON API exposing To‑Do CRUD with typed schemas.
**Core skills:** FastAPI, pydantic, dependency injection, OpenAPI.

#### Required Features
- **R1. Pydantic models & validation** — **Difficulty 2/5**
  - **What it teaches:** Request/response models, field validators, error mapping.
  - **Acceptance criteria:** Invalid payloads return 422 with field errors.

- **R2. CRUD endpoints** — **Difficulty 2/5**
  - **What it teaches:** REST semantics (status codes, idempotence), path/query params.
  - **Acceptance criteria:** `POST/GET/PATCH/DELETE /todos` behave per spec; 404s for missing IDs.

- **R3. Filtering, sorting, pagination** — **Difficulty 2/5**
  - **What it teaches:** Query parameter design, limit/offset, stable ordering.
  - **Acceptance criteria:** `?q=open&sort=due_at&limit=20&offset=20` works.

- **R4. Error handlers & OpenAPI docs** — **Difficulty 1/5**
  - **What it teaches:** Exception handlers; auto docs at `/docs`.
  - **Acceptance criteria:** Custom errors map to JSON; schema examples present.

#### Bonus Features
- **B1. JWT auth** — **Difficulty 3/5**
  - **Teaches:** Token issuance/verification, scopes/claims, expiry.
  - **Acceptance:** Protected endpoints require `Authorization: Bearer <token>`.

- **B2. API keys** — **Difficulty 2/5**
  - **Teaches:** Header/query key acceptance; rotation.
  - **Acceptance:** Requests without valid key receive 401/403 with docs link.

- **B3. Rate limiting** — **Difficulty 2/5**
  - **Teaches:** Client quota enforcement; 429 handling.
  - **Acceptance:** Limits applied per key/IP with `Retry-After` header.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 4) Async Web Scraper
**What you’re building:** High‑throughput crawler that stores extracted data.
**Core skills:** `asyncio`, `aiohttp`, backoff, caching, respectful crawling.

#### Required Features
- **R1. Concurrent fetching with semaphore** — **Difficulty 3/5**
  - **What it teaches:** Async session reuse, bounded concurrency, cancellation.
  - **Acceptance criteria:** Concurrency limited; graceful shutdown on Ctrl‑C.

- **R2. Politeness: robots.txt & delays** — **Difficulty 2/5**
  - **What it teaches:** Robots parsing, per‑host delays, user‑agent etiquette.
  - **Acceptance criteria:** Disallowed paths skipped; logs show delay policy.

- **R3. Retry with exponential backoff** — **Difficulty 2/5**
  - **What it teaches:** Transient failure handling; jitter to avoid sync storms.
  - **Acceptance criteria:** 429/5xx retries; final failure recorded with reason.

- **R4. Extract & persist data** — **Difficulty 2/5**
  - **What it teaches:** CSS selectors/XPath, normalization, SQLite/CSV sinks.
  - **Acceptance criteria:** Schema documented; duplicate suppression implemented.

#### Bonus Features
- **B1. On‑disk HTML cache** — **Difficulty 2/5**
  - **Teaches:** URL→filename hashing, TTL, offline replays.
  - **Acceptance:** Cached pages reused; `--no-cache` bypass works.

- **B2. Pluggable pipelines** — **Difficulty 3/5**
  - **Teaches:** Hook system for transforms (e.g., clean→validate→store).
  - **Acceptance:** Adding a new pipeline stage requires no core changes.

- **B3. Sitemap discovery** — **Difficulty 2/5**
  - **Teaches:** Using sitemaps to seed URLs; deduping.
  - **Acceptance:** If sitemap exists, it’s crawled before fallback discovery.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 5) Background Jobs with Redis
**What you’re building:** Job queue with workers, retries, and status tracking.
**Core skills:** Redis (RQ/ARQ), idempotency, retry, dead‑letter queues.

#### Required Features
- **R1. Enqueue & worker process** — **Difficulty 2/5**
  - **What it teaches:** Producer/consumer model, serialization of job args.
  - **Acceptance criteria:** Jobs enqueued and executed by worker; failures visible.

- **R2. Retries & backoff** — **Difficulty 2/5**
  - **What it teaches:** Retry policies, max attempts, jitter.
  - **Acceptance criteria:** Retryable errors retried N times; non‑retryable go straight to DLQ.

- **R3. Idempotency keys** — **Difficulty 3/5**
  - **What it teaches:** De‑duplication of logically identical jobs.
  - **Acceptance criteria:** Same key within TTL enqueues once; others rejected/logged.

- **R4. Status & DLQ** — **Difficulty 2/5**
  - **What it teaches:** Job lifecycle, querying status, DLQ inspection tools.
  - **Acceptance criteria:** Status endpoints/CLI show queued/running/failed; DLQ export works.

#### Bonus Features
- **B1. Scheduled/delayed jobs** — **Difficulty 2/5**
  - **Teaches:** Time‑based enqueues; cron‑like scheduling basics.
  - **Acceptance:** Jobs fire at scheduled time; missed jobs policy documented.

- **B2. Priority queues** — **Difficulty 2/5**
  - **Teaches:** Separate queues and worker pools per priority.
  - **Acceptance:** High‑priority jobs preempt lower priority.

- **B3. Web dashboard** — **Difficulty 3/5**
  - **Teaches:** Minimal admin UI for queue stats and job details.
  - **Acceptance:** Dashboard shows counts, recent failures, retry actions.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 6) File Upload Service
**What you’re building:** Upload files safely and serve them securely.
**Core skills:** Streaming uploads, MIME checks, secure storage, presigned URLs.

#### Required Features
- **R1. Upload form & streaming** — **Difficulty 2/5**
  - **What it teaches:** Streaming file reads, temp file handling, size limits.
  - **Acceptance criteria:** Large file upload succeeds without OOM; size cap enforced.

- **R2. MIME validation & safe filenames** — **Difficulty 2/5**
  - **What it teaches:** Server‑side content sniffing; path traversal prevention.
  - **Acceptance criteria:** Disallowed types rejected; filenames sanitized.

- **R3. Secure serving** — **Difficulty 2/5**
  - **What it teaches:** Authorization checks, short‑lived URLs, cache headers.
  - **Acceptance criteria:** Private files require auth; `Cache-Control` configured.

- **R4. Virus scan hook** — **Difficulty 2/5**
  - **What it teaches:** Pluggable validation step; quarantine flow.
  - **Acceptance criteria:** Suspicious files held; users notified with next steps.

#### Bonus Features
- **B1. Presigned URL (local emulation)** — **Difficulty 3/5**
  - **Teaches:** Signed URLs, expiry, tamper detection.
  - **Acceptance:** Invalid/expired signatures rejected.

- **B2. Chunked uploads + resume** — **Difficulty 4/5**
  - **Teaches:** Multipart state tracking; idempotent chunk handling.
  - **Acceptance:** Interrupted uploads resume; hash verified on completion.

- **B3. Range requests** — **Difficulty 3/5**
  - **Teaches:** HTTP `Range`/`206 Partial Content` semantics.
  - **Acceptance:** Video scrubbing works; correct headers set.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 7) PDF Search (Mini Index)
**What you’re building:** Extract text and search PDFs with an inverted index.
**Core skills:** PDF text extraction, tokenization, indexing, ranking, snippets.

#### Required Features
- **R1. Text extraction** — **Difficulty 2/5**
  - **What it teaches:** `pdfminer`/`pypdf` trade‑offs; handling OCR‑less PDFs.
  - **Acceptance criteria:** Extracted text saved; pages tracked.

- **R2. Tokenization & normalization** — **Difficulty 2/5**
  - **What it teaches:** Lowercasing, stopword removal, optional stemming.
  - **Acceptance criteria:** Reproducible tokens for same input.

- **R3. Inverted index & phrase queries** — **Difficulty 3/5**
  - **What it teaches:** Posting lists, positions for phrase matching.
  - **Acceptance criteria:** `"machine learning"` phrase finds exact sequences.

- **R4. Ranking & snippets** — **Difficulty 3/5**
  - **What it teaches:** TF‑IDF/BM25 basics, windowed snippet generation.
  - **Acceptance criteria:** Results ranked deterministically; terms highlighted in snippets.

#### Bonus Features
- **B1. Boolean operators** — **Difficulty 3/5**
  - **Teaches:** AND/OR/NOT parsing and execution.
  - **Acceptance:** Complex queries return correct doc sets.

- **B2. Field weights** — **Difficulty 2/5**
  - **Teaches:** Title/heading boosts; scoring composition.
  - **Acceptance:** Title matches rank above body‑only matches.

- **B3. Persistent/compact index** — **Difficulty 3/5**
  - **Teaches:** On‑disk structures; compression; memory maps.
  - **Acceptance:** Index reloads fast; RAM usage documented.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 8) EDA on Public Dataset
**What you’re building:** End‑to‑end exploratory data analysis with visuals.
**Core skills:** pandas, groupby, plotting, notebooks, data quality.

#### Required Features
- **R1. Data loading & cleaning** — **Difficulty 2/5**
  - **What it teaches:** Schema inspection, missing values, type coercion.
  - **Acceptance criteria:** Cleaning steps are reproducible and scripted.

- **R2. Descriptive statistics & DQ report** — **Difficulty 2/5**
  - **What it teaches:** Summary stats, distribution checks, outlier flags.
  - **Acceptance criteria:** DQ markdown generated with tables/plots.

- **R3. Visualizations** — **Difficulty 2/5**
  - **What it teaches:** Appropriate chart selection; labeled axes; legends.
  - **Acceptance criteria:** At least 3 charts saved with captions.

- **R4. Notebook + README** — **Difficulty 1/5**
  - **What it teaches:** Narrative analysis; reproducibility notes.
  - **Acceptance criteria:** Notebook runs top‑to‑bottom without errors.

#### Bonus Features
- **B1. Baseline model (regression/classification)** — **Difficulty 3/5**
  - **Teaches:** Train/validation split; simple metrics; leakage pitfalls.
  - **Acceptance:** Baseline score reported and interpreted cautiously.

- **B2. Parameterized pipeline** — **Difficulty 2/5**
  - **Teaches:** Config‑driven ETL; CLI arguments.
  - **Acceptance:** Reruns with different params yield consistent outputs.

- **B3. Pre‑commit hooks** — **Difficulty 2/5**
  - **Teaches:** Auto‑format/lint on commit; notebook strip outputs.
  - **Acceptance:** Hooks enforced; CI verifies formatting.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 9) Stock Tracker with DB
**What you’re building:** Daily price ingester with analysis and charting.
**Core skills:** Scheduling, HTTP APIs, pandas, matplotlib, Dockerization.

#### Required Features
- **R1. Daily fetch & store** — **Difficulty 2/5**
  - **What it teaches:** Cron/`schedule` lib, idempotent inserts, API hygiene.
  - **Acceptance criteria:** Duplicate days do not create duplicate rows.

- **R2. Technical indicators** — **Difficulty 2/5**
  - **What it teaches:** Moving averages, RSI basics, rolling windows.
  - **Acceptance criteria:** Indicator columns correct for sample data.

- **R3. Alerts** — **Difficulty 2/5**
  - **What it teaches:** Threshold rules; notification channels.
  - **Acceptance criteria:** Alerts fire once per crossing; deduped.

- **R4. Charts & export** — **Difficulty 2/5**
  - **What it teaches:** Plotting with date axes; PNG/CSV outputs.
  - **Acceptance criteria:** Chart saved with legend; data export consistent.

#### Bonus Features
- **B1. Dockerized service** — **Difficulty 2/5**
  - **Teaches:** Container healthcheck; env configs.
  - **Acceptance:** `docker compose up` runs end‑to‑end.

- **B2. Backtesting (simple)** — **Difficulty 3/5**
  - **Teaches:** Strategy loops; performance metrics.
  - **Acceptance:** Equity curve and stats (CAGR, max drawdown) produced.

- **B3. Caching & rate‑limit handling** — **Difficulty 2/5**
  - **Teaches:** ETags/If‑Modified‑Since; backoff on 429.
  - **Acceptance:** Reduces API calls; compliant with provider rules.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 10) Word‑Frequency Analyzer
**What you’re building:** Compute TF and TF‑IDF across a corpus.
**Core skills:** Tokenization, stopwords, math/logs, report generation.

#### Required Features
- **R1. Normalization pipeline** — **Difficulty 2/5**
  - **What it teaches:** Case folding; punctuation removal; Unicode handling.
  - **Acceptance criteria:** Repeatable tokens on repeated runs.

- **R2. Term frequencies (per doc & global)** — **Difficulty 2/5**
  - **What it teaches:** Counting efficiently; handling very large docs.
  - **Acceptance criteria:** Counts match small hand‑computed examples.

- **R3. TF‑IDF scoring** — **Difficulty 2/5**
  - **What it teaches:** Log weighting; smoothing; sparse representations.
  - **Acceptance criteria:** Top terms per doc exported with scores.

- **R4. Reports (CSV/Markdown)** — **Difficulty 1/5**
  - **What it teaches:** Generating human‑readable summaries.
  - **Acceptance criteria:** Per‑doc and global reports saved.

#### Bonus Features
- **B1. Stemming/Lemmatization** — **Difficulty 2/5**
  - **Teaches:** NLTK/spaCy pipelines; recall vs precision trade‑offs.
  - **Acceptance:** Provide before/after examples; configurable.

- **B2. Interactive search** — **Difficulty 2/5**
  - **Teaches:** Query over index; ranked results.
  - **Acceptance:** Query returns ranked docs; snippets included.

- **B3. Memory optimization** — **Difficulty 3/5**
  - **Teaches:** On‑disk sparse matrices; chunked processing.
  - **Acceptance:** Handles corpora larger than RAM (document limits/throughput).

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 11) Multi‑Client Chat Server
**What you’re building:** TCP chat server with rooms and private messages.
**Core skills:** sockets, threading, protocols, concurrency, persistence.

#### Required Features
- **R1. Protocol & message framing** — **Difficulty 3/5**
  - **What it teaches:** Line/length‑prefixed protocols; partial reads; keep‑alive.
  - **Acceptance criteria:** Handles fragmented packets and large messages.

- **R2. Threaded server & rooms** — **Difficulty 3/5**
  - **What it teaches:** Thread per client (or threadpool), room broadcast.
  - **Acceptance criteria:** 20+ clients join/leave and chat reliably.

- **R3. Usernames & private messages** — **Difficulty 2/5**
  - **What it teaches:** Routing to specific clients; presence tracking.
  - **Acceptance criteria:** `/pm @user` works; unknown user handled.

- **R4. Persistence (optional logs)** — **Difficulty 2/5**
  - **What it teaches:** Server logs; per‑room history.
  - **Acceptance criteria:** History saved with timestamps.

#### Bonus Features
- **B1. Asyncio implementation** — **Difficulty 3/5**
  - **Teaches:** `asyncio` sockets, tasks, cancellation.
  - **Acceptance:** Parity with threaded version under load.

- **B2. WebSocket gateway** — **Difficulty 3/5**
  - **Teaches:** Bridge TCP↔WS; simple web client.
  - **Acceptance:** Browser clients can join rooms via WS.

- **B3. Flood control & moderation** — **Difficulty 2/5**
  - **Teaches:** Rate limits; mute/kick tools.
  - **Acceptance:** Abusive clients throttled; admin commands work.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 12) Dockerize a Web App
**What you’re building:** Containerized Flask/FastAPI app with Compose.
**Core skills:** Dockerfile, Compose, env vars, volumes, healthchecks.

#### Required Features
- **R1. Dockerfile (multi‑stage)** — **Difficulty 2/5**
  - **What it teaches:** Slim images, dependency caching, non‑root user.
  - **Acceptance criteria:** Image builds reproducibly; `docker run` works.

- **R2. docker‑compose.yml** — **Difficulty 2/5**
  - **What it teaches:** Service definitions, env files, volumes, ports.
  - **Acceptance criteria:** `docker compose up` boots app + DB.

- **R3. Dev vs Prod configs** — **Difficulty 2/5**
  - **What it teaches:** Different compose overrides; debug on/off.
  - **Acceptance criteria:** Prod disables debug and mounts; dev enables.

- **R4. Healthchecks** — **Difficulty 1/5**
  - **What it teaches:** Command‑based health; restart policies.
  - **Acceptance criteria:** Unhealthy container auto‑restarted.

#### Bonus Features
- **B1. CI image build** — **Difficulty 2/5**
  - **Teaches:** GH Actions caching; tags by commit/branch.
  - **Acceptance:** CI pushes image to registry (local or GHCR).

- **B2. Image scanning** — **Difficulty 2/5**
  - **Teaches:** Trivy/Grype; vulnerability gating.
  - **Acceptance:** CI fails on high severity vulns.

- **B3. Multi‑arch builds** — **Difficulty 3/5**
  - **Teaches:** `buildx` and QEMU; ARM64/AMD64 images.
  - **Acceptance:** Both arch images available.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

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

### 15) Requests Caching Layer
**What you’re building:** Transparent caching for HTTP requests.
**Core skills:** requests‑cache, cache keys, TTL, invalidation, metrics.

#### Required Features
- **R1. Cache key strategy** — **Difficulty 2/5**
  - **What it teaches:** Keys from method+URL+params+headers; Vary support.
  - **Acceptance criteria:** Distinct keys for differing query/headers.

- **R2. TTL & invalidation** — **Difficulty 2/5**
  - **What it teaches:** Expiry, manual purge, cache busting.
  - **Acceptance criteria:** Expired entries refreshed; manual invalidation works.

- **R3. Stale‑while‑revalidate** — **Difficulty 3/5**
  - **What it teaches:** Serving stale content while async refresh occurs.
  - **Acceptance criteria:** Second request serves fresh result post‑refresh.

- **R4. Metrics & logging** — **Difficulty 2/5**
  - **What it teaches:** Hit/miss rate, latency improvements.
  - **Acceptance criteria:** Metrics exported and chartable.

#### Bonus Features
- **B1. Pluggable backends (disk/Redis)** — **Difficulty 2/5**
  - **Teaches:** Backend abstractions; connection options.
  - **Acceptance:** Swapping backend requires only config change.

- **B2. Conditional requests** — **Difficulty 2/5**
  - **Teaches:** ETag/Last‑Modified; `If-None-Match`.
  - **Acceptance:** 304 responses handled; cache updated accordingly.

- **B3. Cache stampede protection** — **Difficulty 3/5**
  - **Teaches:** Single‑flight/locking around misses.
  - **Acceptance:** Under load, only one refresh occurs per key.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 16) OAuth GitHub Viewer
**What you’re building:** Login via GitHub and list repos/issues.
**Core skills:** OAuth2, sessions, pagination APIs, rate limit handling.

#### Required Features
- **R1. OAuth flow** — **Difficulty 3/5**
  - **What it teaches:** Authorization code grant, state param, CSRF protection.
  - **Acceptance criteria:** Valid callback exchanges code for token; state verified.

- **R2. List repos/issues with pagination** — **Difficulty 2/5**
  - **What it teaches:** Link headers parsing; page traversal.
  - **Acceptance criteria:** All pages visited; UI shows next/prev.

- **R3. Rate‑limit handling & caching** — **Difficulty 2/5**
  - **What it teaches:** Respecting GitHub limits; ETags; conditional requests.
  - **Acceptance criteria:** Hitting rate limit defers calls; UI messages friendly.

- **R4. Session & logout** — **Difficulty 1/5**
  - **What it teaches:** Session lifecycle; token revocation notes.
  - **Acceptance criteria:** Logout clears session; token not stored in plaintext.

#### Bonus Features
- **B1. Star/unstar UI** — **Difficulty 2/5**
  - **Teaches:** Authenticated write operations; optimistic UI.
  - **Acceptance:** Star state toggles and persists.

- **B2. Repo search** — **Difficulty 2/5**
  - **Teaches:** Query endpoints; debounced search.
  - **Acceptance:** Search results ranked; pagination preserved.

- **B3. Offline snapshot** — **Difficulty 2/5**
  - **Teaches:** Export repos/issues to JSON; read later.
  - **Acceptance:** Snapshot downloadable; timestamped.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 17) Graph Algorithms Visualizer
**What you’re building:** Visualize BFS/DFS/shortest paths on graphs.
**Core skills:** networkx, matplotlib, algorithms, data structures.

#### Required Features
- **R1. Graph ingestion** — **Difficulty 2/5**
  - **What it teaches:** Reading edge lists/adjacency; validation.
  - **Acceptance criteria:** Bad edges reported; graph summary printed.

- **R2. BFS/DFS traversals** — **Difficulty 2/5**
  - **What it teaches:** Frontier/visited sets; parent pointers.
  - **Acceptance criteria:** Traversal order shown; correctness tests.

- **R3. Shortest paths (Dijkstra)** — **Difficulty 3/5**
  - **What it teaches:** Priority queues; weights; path reconstruction.
  - **Acceptance criteria:** Path cost matches reference.

- **R4. Drawing** — **Difficulty 2/5**
  - **What it teaches:** Layouts; highlighting paths/visited nodes.
  - **Acceptance criteria:** Saved image with legend and annotations.

#### Bonus Features
- **B1. Interactive GUI** — **Difficulty 3/5**
  - **Teaches:** PyQt/PySimpleGUI controls; step‑through animations.
  - **Acceptance:** Buttons control algorithm steps; speed adjustable.

- **B2. A* heuristic** — **Difficulty 3/5**
  - **Teaches:** Heuristics; admissibility; consistency.
  - **Acceptance:** A* equals Dijkstra on zero heuristic; faster on good heuristic.

- **B3. Performance benchmarking** — **Difficulty 2/5**
  - **Teaches:** Big‑O discussion; empirical timing.
  - **Acceptance:** Benchmark report across sizes/densities.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 18) Tetris with pygame
**What you’re building:** Playable Tetris clone with scoring and levels.
**Core skills:** pygame loop, collision detection, game state, rendering.

#### Required Features
- **R1. Tetrominoes & rotation** — **Difficulty 3/5**
  - **What it teaches:** Piece systems (SRS), rotation kicks, state machines.
  - **Acceptance criteria:** All 7 pieces rotate/move without clipping.

- **R2. Collision & line clear** — **Difficulty 3/5**
  - **What it teaches:** Grid representation; collision checks; row clears.
  - **Acceptance criteria:** Lines clear; gravity and lock delay feel right.

- **R3. Scoring & levels** — **Difficulty 2/5**
  - **What it teaches:** Tetris scoring rules; speed scaling.
  - **Acceptance criteria:** Scores/levels update per line clears; UI shows HUD.

- **R4. Pause/resume & high scores** — **Difficulty 2/5**
  - **What it teaches:** Input handling; persistence to JSON.
  - **Acceptance criteria:** High scores saved/loaded; pause works.

#### Bonus Features
- **B1. Ghost piece & hold** — **Difficulty 2/5**
  - **Teaches:** Predictive rendering; swap mechanics.
  - **Acceptance:** Ghost shows landing; hold obeys rule (once per drop).

- **B2. Replays** — **Difficulty 3/5**
  - **Teaches:** Input recording; determinism.
  - **Acceptance:** Recorded games replay identically.

- **B3. Skins & themes** — **Difficulty 1/5**
  - **Teaches:** Asset management.
  - **Acceptance:** Selectable theme packs.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 19) Folder Watch ETL
**What you’re building:** Watch a folder and transform new files.
**Core skills:** watchdog, pipelines, error handling, retries, metrics.

#### Required Features
- **R1. Watcher & debounce** — **Difficulty 2/5**
  - **What it teaches:** File system events; debouncing partial writes.
  - **Acceptance criteria:** Only stable files processed; duplicates avoided.

- **R2. ETL pipeline** — **Difficulty 2/5**
  - **What it teaches:** Extract→Transform→Load stages; pluggability.
  - **Acceptance criteria:** New transforms can be added without core changes.

- **R3. Error handling & quarantine** — **Difficulty 2/5**
  - **What it teaches:** Moving bad files to quarantine with reason.
  - **Acceptance criteria:** Failures logged; quarantine directory structured.

- **R4. Metrics** — **Difficulty 2/5**
  - **What it teaches:** Throughput, latency, failure counts.
  - **Acceptance criteria:** Metrics printed/exported periodically.

#### Bonus Features
- **B1. Parallel processing** — **Difficulty 3/5**
  - **Teaches:** Thread/Process pools; concurrency bugs.
  - **Acceptance:** Throughput improves without data races.

- **B2. Config file** — **Difficulty 2/5**
  - **Teaches:** YAML for pipelines; validation.
  - **Acceptance:** Changing config alters behavior at next run.

- **B3. CDC (change data capture)** — **Difficulty 3/5**
  - **Teaches:** Capturing updates instead of only new files.
  - **Acceptance:** Modified files reprocessed per policy.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 20) Structured Logging
**What you’re building:** JSON logs with correlation IDs and rotation.
**Core skills:** logging config, filters, RotatingFileHandler, log sampling.

#### Required Features
- **R1. JSON log format** — **Difficulty 2/5**
  - **What it teaches:** Custom `Formatter` or libs; field design.
  - **Acceptance criteria:** Logs are valid JSON with timestamp, level, msg, context.

- **R2. Correlation/trace IDs** — **Difficulty 2/5**
  - **What it teaches:** Context vars; middleware to inject IDs.
  - **Acceptance criteria:** ID persists across request lifecycle.

- **R3. Rotation & retention** — **Difficulty 2/5**
  - **What it teaches:** File size/time rotation; retention policy.
  - **Acceptance criteria:** Old logs archived and pruned as configured.

- **R4. Log levels & sampling** — **Difficulty 2/5**
  - **What it teaches:** Verbosity control; sample noisy events.
  - **Acceptance criteria:** Level filtering works; sampling reduces volume.

#### Bonus Features
- **B1. Ship to Elasticsearch (local)** — **Difficulty 3/5**
  - **Teaches:** Log shipping, index templates, Kibana dashboards.
  - **Acceptance:** Logs visible in Kibana; fields indexed.

- **B2. OpenTelemetry attributes** — **Difficulty 2/5**
  - **Teaches:** Trace context in logs.
  - **Acceptance:** Span IDs appear; cross‑links enabled.

- **B3. PII redaction** — **Difficulty 2/5**
  - **Teaches:** Filters to mask sensitive data.
  - **Acceptance:** Emails/SSNs redacted per policy.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 21) Config Management
**What you’re building:** Typed settings with environment overrides.
**Core skills:** pydantic/dynaconf, secrets, profiles, validation.

#### Required Features
- **R1. Settings class** — **Difficulty 2/5**
  - **What it teaches:** `BaseSettings`, env var mapping, defaults.
  - **Acceptance criteria:** Values load from `.env` and process env.

- **R2. Profiles (dev/test/prod)** — **Difficulty 2/5**
  - **What it teaches:** Selecting profiles; override precedence.
  - **Acceptance criteria:** `APP_ENV=prod` loads prod overrides.

- **R3. Secrets handling** — **Difficulty 2/5**
  - **What it teaches:** Separate secret files; avoiding commits.
  - **Acceptance criteria:** Secrets not in VCS; missing secrets detected.

- **R4. Validation & helpful errors** — **Difficulty 2/5**
  - **What it teaches:** Custom validators; actionable messages.
  - **Acceptance criteria:** Invalid configs fail fast with clear output.

#### Bonus Features
- **B1. Dynamic reload** — **Difficulty 3/5**
  - **Teaches:** Watching files; hot‑reloading settings safely.
  - **Acceptance:** Changes applied without restart; documented caveats.

- **B2. Secret backends** — **Difficulty 3/5**
  - **Teaches:** Pluggable secret stores (env/JSON/file/OS keychain).
  - **Acceptance:** Backend switch via config only.

- **B3. Config schema export** — **Difficulty 2/5**
  - **Teaches:** Generating JSON Schema for settings.
  - **Acceptance:** Schema file generated; used for validation.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 22) Docs Site (Sphinx/MkDocs)
**What you’re building:** Documentation site for one of your apps/libs.
**Core skills:** autodoc, code fences, site build, theming, versioning.

#### Required Features
- **R1. Buildable docs skeleton** — **Difficulty 1/5**
  - **What it teaches:** Sphinx/MkDocs setup; theme selection.
  - **Acceptance criteria:** `make html` (or `mkdocs build`) succeeds.

- **R2. Autodoc/API reference** — **Difficulty 2/5**
  - **What it teaches:** Docstring style, API pages.
  - **Acceptance criteria:** Major modules documented with API pages.

- **R3. Tutorials/how‑tos** — **Difficulty 2/5**
  - **What it teaches:** Task‑oriented guides; examples.
  - **Acceptance criteria:** At least two working tutorials with code blocks.

- **R4. Versioned docs** — **Difficulty 2/5**
  - **What it teaches:** Multi‑version docs and navigation.
  - **Acceptance criteria:** At least two versions selectable.

#### Bonus Features
- **B1. CI deploy to Pages** — **Difficulty 2/5**
  - **Teaches:** GH Pages deploy; cache.
  - **Acceptance:** Docs auto‑published on main.

- **B2. Link & doc tests** — **Difficulty 2/5**
  - **Teaches:** Link checking; doctest.
  - **Acceptance:** CI checks links; doctests pass.

- **B3. Search & analytics** — **Difficulty 1/5**
  - **Teaches:** Built‑in search/Algolia; privacy notes.
  - **Acceptance:** Search works; analytics optional and documented.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 23) Test Suite Mastery
**What you’re building:** Comprehensive tests for a web app.
**Core skills:** pytest, unittest.mock, coverage, style tooling.

#### Required Features
- **R1. Coverage ≥ 90%** — **Difficulty 2/5**
  - **What it teaches:** Identifying untested paths; coverage budgeting.
  - **Acceptance criteria:** Coverage gate enforced in CI.

- **R2. Fixtures & parametrization** — **Difficulty 2/5**
  - **What it teaches:** Reusable setup; table‑driven tests.
  - **Acceptance criteria:** Minimal duplication; clear parametrized cases.

- **R3. Mocking I/O & boundaries** — **Difficulty 2/5**
  - **What it teaches:** Mocking network/files/DB; contract tests.
  - **Acceptance criteria:** External calls isolated; fast tests.

- **R4. Style & static checks** — **Difficulty 1/5**
  - **What it teaches:** black/ruff/isort/mypy integration.
  - **Acceptance criteria:** CI passes style and type checks.

#### Bonus Features
- **B1. Mutation testing (mutmut)** — **Difficulty 3/5**
  - **Teaches:** Measuring test effectiveness.
  - **Acceptance:** Mutation score reported; weak spots addressed.

- **B2. Property‑based tests** — **Difficulty 3/5**
  - **Teaches:** Hypothesis strategies; shrinking.
  - **Acceptance:** At least 2 meaningful properties verified.

- **B3. Parallel test matrix** — **Difficulty 2/5**
  - **Teaches:** OS/Python version matrices.
  - **Acceptance:** CI runs across 3 Python versions.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 24) GitHub Actions CI
**What you’re building:** CI to run tests, linting, and builds on each push.
**Core skills:** YAML pipelines, caching, matrices, artifacts.

#### Required Features
- **R1. Workflow YAML** — **Difficulty 2/5**
  - **What it teaches:** Jobs/steps; triggers; permissions.
  - **Acceptance criteria:** On push/PR, tests and linters run.

- **R2. Dependency caching** — **Difficulty 2/5**
  - **What it teaches:** Cache keys and performance trade‑offs.
  - **Acceptance criteria:** Subsequent runs are faster; cache key logged.

- **R3. Build & artifacts** — **Difficulty 2/5**
  - **What it teaches:** Packaging wheels; uploading artifacts.
  - **Acceptance criteria:** Artifacts downloadable from run.

- **R4. Matrix strategy** — **Difficulty 2/5**
  - **What it teaches:** Multi‑Python/OS testing.
  - **Acceptance criteria:** Jobs fan out and report status per cell.

#### Bonus Features
- **B1. Release on tags** — **Difficulty 2/5**
  - **Teaches:** Tag triggers; changelog generation.
  - **Acceptance:** Tagging `vX.Y.Z` triggers release job.

- **B2. Codecov integration** — **Difficulty 2/5**
  - **Teaches:** Coverage upload and gating.
  - **Acceptance:** Coverage badge in README; threshold enforced.

- **B3. Dependabot & linters** — **Difficulty 1/5**
  - **Teaches:** Automated dependency PRs; lint checks on PR.
  - **Acceptance:** Dependabot enabled; lint job required.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 25) PyInstaller Distribution
**What you’re building:** Ship a CLI as a single binary/exe.
**Core skills:** pyinstaller, entry points, including assets, cross‑platform notes.

#### Required Features
- **R1. Working spec & entry point** — **Difficulty 2/5**
  - **What it teaches:** PyInstaller spec; console entry; hidden imports.
  - **Acceptance criteria:** Binary runs on target OS; usage matches `pip` version.

- **R2. Bundle assets** — **Difficulty 2/5**
  - **What it teaches:** Adding data files; relative paths inside bundle.
  - **Acceptance criteria:** Assets load at runtime on all platforms.

- **R3. Update strategy & version checks** — **Difficulty 2/5**
  - **What it teaches:** Version endpoints; prompting for updates.
  - **Acceptance criteria:** App detects newer version and informs user.

- **R4. Cross‑platform notes** — **Difficulty 1/5**
  - **What it teaches:** macOS Gatekeeper/entitlements; Windows AV flags.
  - **Acceptance criteria:** README documents platform‑specific steps.

#### Bonus Features
- **B1. Auto‑update check** — **Difficulty 3/5**
  - **Teaches:** Secure download and integrity checks.
  - **Acceptance:** App can download newer binary and replace safely (or instruct user).

- **B2. Code signing/notarization** — **Difficulty 3/5**
  - **Teaches:** Signing flows and tooling.
  - **Acceptance:** Signed binaries verified by OS tools.

- **B3. Compression & size tuning** — **Difficulty 2/5**
  - **Teaches:** UPX (where legal), excluding modules.
  - **Acceptance:** Binary size reduced with unchanged behavior.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

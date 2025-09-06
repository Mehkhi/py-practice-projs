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

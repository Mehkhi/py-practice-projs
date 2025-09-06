# 125 Python Projects — From Novice to Principal Engineer

> Each level contains **25 projects**. For each project you’ll see: what you build, core skills, milestones to prove progress, and stretch goals to deepen learning.

## Level 1 — Beginner (Novice)

Foundations of Python: syntax, variables, control flow, functions, collections, basic I/O. Projects are short and focus on building comfort with the language and standard library.


#### Checklist
- [ ] 1. Hello World & Super-Calculator
- [ ] 2. Guess the Number
- [ ] 3. Temperature Converter
- [ ] 4. Unit Converter
- [ ] 5. Rock–Paper–Scissors
- [ ] 6. Mad Libs Generator
- [ ] 7. Palindrome & Anagram Checker
- [ ] 8. Alarm & Countdown Timer
- [ ] 9. To‑Do List (Text File)
- [ ] 10. Address Book (CSV)
- [ ] 11. Word Count (wc)
- [ ] 12. Dice Roller Simulator
- [ ] 13. Stopwatch
- [ ] 14. Multiplication Table Generator
- [ ] 15. Password Generator
- [ ] 16. Hangman (ASCII)
- [ ] 17. Quiz App from JSON
- [ ] 18. String Templater for Emails
- [ ] 19. Countdown Pomodoro
- [ ] 20. Tip & Bill Splitter
- [ ] 21. BMI & Calorie Calculator
- [ ] 22. Simple Interest & Compound Calculator
- [ ] 23. Calendar Viewer
- [ ] 24. Flashcards (CLI)
- [ ] 25. File Organizer
- [ ] 26. Text Adventure Mini‑Game

### 1. Hello World & Super-Calculator

**What you build:** Print text, read user input, perform + − × ÷ and show results.

**Skills you’ll learn:** print(), input(), int/float, operators, functions, f-strings.

**Milestones:** Handle invalid input; support order of operations; add unit tests with assert.

**Stretch goals:** Add exponent, modulo, and memory recall (M+, M-).


### 2. Guess the Number

**What you build:** Computer picks a number; user guesses until correct with hints.

**Skills you’ll learn:** random, loops, conditionals, counters, replay loop.

**Milestones:** Limit attempts; show attempts used; track best score in a file.

**Stretch goals:** Binary-search hint mode (higher/lower guidance quality).


### 3. Temperature Converter

**What you build:** Convert Celsius↔Fahrenheit↔Kelvin with simple menu.

**Skills you’ll learn:** float math, branching, functions, docstrings.

**Milestones:** Validate ranges; round sensibly; support batch conversions from a file.

**Stretch goals:** Graph conversion table with text grid.


### 4. Unit Converter

**What you build:** Length/weight conversions (m↔ft, kg↔lb) with a tiny DSL-like menu.

**Skills you’ll learn:** dict lookups, mapping tables, functions, error messages.

**Milestones:** Centralize conversions; add tests for edge cases; persist last selection.

**Stretch goals:** Support chaining (m→ft→in) and custom factors file.


### 5. Rock–Paper–Scissors

**What you build:** Play against the computer with running score.

**Skills you’ll learn:** random choice, enums via constants, loops, input parsing.

**Milestones:** Best‑of‑N series; detect invalid input; pretty scoreboard.

**Stretch goals:** Add Lizard/Spock variant and simple AI (counter last move).


### 6. Mad Libs Generator

**What you build:** Prompt for words and inject into a story template.

**Skills you’ll learn:** string formatting, lists, files, basic templates.

**Milestones:** Load multiple templates from folder; save completed stories.

**Stretch goals:** Randomly select template and required parts of speech.


### 7. Palindrome & Anagram Checker

**What you build:** Check if text is a palindrome; detect anagrams between two phrases.

**Skills you’ll learn:** string methods, normalization, collections.Counter.

**Milestones:** Ignore punctuation/spacing; add unit tests.

**Stretch goals:** CLI mode with argparse and batch file input.


### 8. Alarm & Countdown Timer

**What you build:** Set an alarm or countdown that rings at time.

**Skills you’ll learn:** time, datetime, while-loops, cross-platform beeps.

**Milestones:** Parse 'HH:MM' and '10m' formats; cancel option.

**Stretch goals:** Multiple alarms stored in JSON.


### 9. To‑Do List (Text File)

**What you build:** Minimal task list saved to disk with add/list/complete/delete.

**Skills you’ll learn:** file I/O, lists, indexes, simple persistence.

**Milestones:** Unique IDs; timestamps; confirm destructive actions.

**Stretch goals:** Priorities and due dates; sort by priority.


### 10. Address Book (CSV)

**What you build:** Store contacts in CSV; search by name or email.

**Skills you’ll learn:** csv module, dict rows, basic search.

**Milestones:** Import/export; validate email; avoid duplicates.

**Stretch goals:** Support vCard export.


### 11. Word Count (wc)

**What you build:** Count lines/words/chars across files like Unix wc.

**Skills you’ll learn:** argparse, pathlib, reading files, aggregation.

**Milestones:** Glob patterns; handle large files; unit tests.

**Stretch goals:** Top‑N most frequent words.


### 12. Dice Roller Simulator

**What you build:** Roll NdM dice (e.g., 3d6) and show distribution.

**Skills you’ll learn:** parsing input, random, list comprehension.

**Milestones:** Roll many times; compute mean/variance.

**Stretch goals:** ASCII histogram chart.


### 13. Stopwatch

**What you build:** Start/stop/lap timing tool in the console.

**Skills you’ll learn:** time/perf_counter, state machine, formatting.

**Milestones:** Lap list; export to CSV; keyboard shortcuts.

**Stretch goals:** Save sessions and summarize totals.


### 14. Multiplication Table Generator

**What you build:** Print 1–12 multiplication tables (or chosen range).

**Skills you’ll learn:** nested loops, formatting, functions.

**Milestones:** Column alignment; save to text/CSV.

**Stretch goals:** Quiz mode with scoring.


### 15. Password Generator

**What you build:** Create random passwords meeting length and class rules.

**Skills you’ll learn:** random, string constants, validation.

**Milestones:** Avoid ambiguous chars; ensure class coverage.

**Stretch goals:** Passphrase mode using word list.


### 16. Hangman (ASCII)

**What you build:** Classic hangman game in terminal with a word list.

**Skills you’ll learn:** sets, state updates, reading resources.

**Milestones:** Reveal progress; track wrong guesses; replay.

**Stretch goals:** Difficulty levels and hints.


### 17. Quiz App from JSON

**What you build:** Ask multiple‑choice questions loaded from JSON.

**Skills you’ll learn:** json, shuffling, scoring, input validation.

**Milestones:** Randomize answers; categories; percentage score.

**Stretch goals:** Timed questions and leader board file.


### 18. String Templater for Emails

**What you build:** Fill placeholders in templates (e.g., {name}) from CSV.

**Skills you’ll learn:** format maps, csv DictReader, file writing.

**Milestones:** Preview mode; output one file per row.

**Stretch goals:** Jinja2 templating for loops/conditions.


### 19. Countdown Pomodoro

**What you build:** Pomodoro timer with work/break cycles in terminal.

**Skills you’ll learn:** loops, sleep, simple state machine.

**Milestones:** Configurable durations; session summary.

**Stretch goals:** Sound notifications and daily log CSV.


### 20. Tip & Bill Splitter

**What you build:** Compute tip %, tax, and split among diners.

**Skills you’ll learn:** float math, rounding, input sanitization.

**Milestones:** Handle uneven splits; service fee option.

**Stretch goals:** Export receipt as text.


### 21. BMI & Calorie Calculator

**What you build:** Compute BMI and estimate daily calories.

**Skills you’ll learn:** formulas, constants, branching.

**Milestones:** Metric/imperial; sensible validation.

**Stretch goals:** Save personal profiles in JSON.


### 22. Simple Interest & Compound Calculator

**What you build:** Compute interest over time; show yearly table.

**Skills you’ll learn:** loops, math, formatting tables.

**Milestones:** Compound intervals; export CSV.

**Stretch goals:** ASCII chart of growth.


### 23. Calendar Viewer

**What you build:** Show month/year calendars and upcoming dates.

**Skills you’ll learn:** calendar module, datetime, CLI options.

**Milestones:** Highlight today; jump to next payday/Friday.

**Stretch goals:** iCal export for birthdays.


### 24. Flashcards (CLI)

**What you build:** Flip Q/A cards from CSV; spaced repetition lite.

**Skills you’ll learn:** csv, randomization, simple scheduling.

**Milestones:** Track correctness; promote/demote difficulty.

**Stretch goals:** Leitner box algorithm.


### 25. File Organizer

**What you build:** Move files into folders by extension (Pictures, Docs…).

**Skills you’ll learn:** pathlib, os, shutil, safety checks.

**Milestones:** Dry‑run preview; handle name collisions.

**Stretch goals:** Rules via YAML config.


### 26. Text Adventure Mini‑Game

**What you build:** Navigate rooms with inventory and simple combat.

**Skills you’ll learn:** dicts as graphs, loops, functions.

**Milestones:** Map loader from JSON; save/load game.

**Stretch goals:** Random encounters and items.


---

## Level 2 — Early Intermediate (Junior Developer)

Apply Python to practical tasks, small automation, simple GUIs and web/API usage. Learn packaging, testing, logging, and basic data handling.


#### Checklist
- [ ] 1. CLI Notes with Search
- [ ] 2. Weather CLI via API
- [ ] 3. Currency Converter (API)
- [ ] 4. SQLite Contact Manager
- [ ] 5. Web Log Analyzer
- [ ] 6. Image Organizer
- [ ] 7. Markdown → HTML Converter
- [ ] 8. Basic Web Scraper
- [ ] 9. PDF Merger/Splitter
- [ ] 10. CSV Cleaner
- [ ] 11. To‑Do GUI (Tkinter)
- [ ] 12. Rule‑Based Chatbot
- [ ] 13. Email Sender (CLI)
- [ ] 14. Local URL Shortener
- [ ] 15. Password Strength Checker
- [ ] 16. Flask Mini API
- [ ] 17. Microblog Skeleton
- [ ] 18. Testing Workshop
- [ ] 19. Backup & Zip Script
- [ ] 20. Task Scheduler
- [ ] 21. RSS Reader (CLI)
- [ ] 22. QR Code Generator
- [ ] 23. Excel Report Builder
- [ ] 24. Image Thumbnailer
- [ ] 25. CLI Address Autocomplete

### 1. CLI Notes with Search

**What you build:** Create, list, search, and tag notes stored in JSON.

**Skills you’ll learn:** argparse, json, search, timestamps, logging.

**Milestones:** Tag filter; fuzzy search; colored output.

**Stretch goals:** Encrypt notes using Fernet (cryptography).


### 2. Weather CLI via API

**What you build:** Fetch current weather by city using a public API.

**Skills you’ll learn:** requests, environment variables, error handling.

**Milestones:** Units switch; 5‑day forecast; retry with backoff.

**Stretch goals:** Cache responses on disk.


### 3. Currency Converter (API)

**What you build:** Convert between currencies using live rates.

**Skills you’ll learn:** requests, JSON parsing, Decimal for money.

**Milestones:** Historical rates; offline fallback rates file.

**Stretch goals:** Plot conversion history with matplotlib.


### 4. SQLite Contact Manager

**What you build:** CRUD contacts stored in SQLite via SQL queries.

**Skills you’ll learn:** sqlite3, schema design, parameterized queries.

**Milestones:** Unique constraints; pagination; migrations script.

**Stretch goals:** Search by phonetic match (soundex).


### 5. Web Log Analyzer

**What you build:** Parse Apache/Nginx logs and summarize traffic.

**Skills you’ll learn:** regex, datetime parsing, aggregation, CSV export.

**Milestones:** Top endpoints; status code breakdown; hourly chart.

**Stretch goals:** Detect basic anomalies (spikes).


### 6. Image Organizer

**What you build:** Sort images into folders by EXIF date.

**Skills you’ll learn:** Pillow, pathlib, shutil, metadata.

**Milestones:** Dry‑run; handle missing EXIF; duplicate detection.

**Stretch goals:** Rename using pattern YYYY‑MM‑DD_HH‑MM‑SS.


### 7. Markdown → HTML Converter

**What you build:** Turn .md files into HTML with templates.

**Skills you’ll learn:** markdown lib, Jinja2, file walking.

**Milestones:** TOC generation; code highlighting.

**Stretch goals:** Static site with navigation index.


### 8. Basic Web Scraper

**What you build:** Download a page and extract items (titles, links).

**Skills you’ll learn:** requests, BeautifulSoup, CSS selectors.

**Milestones:** Follow pagination; respect robots.txt; politeness delay.

**Stretch goals:** Export to SQLite for later querying.


### 9. PDF Merger/Splitter

**What you build:** Combine or split PDFs from the command line.

**Skills you’ll learn:** PyPDF2/pypdf, file I/O, argparse.

**Milestones:** Range selection; rotate; metadata copy.

**Stretch goals:** Bookmarks and table of contents.


### 10. CSV Cleaner

**What you build:** Load CSV, fix missing values, standardize columns.

**Skills you’ll learn:** pandas basics, dtype handling, writing CSV.

**Milestones:** Summary report; detect outliers; schema validation.

**Stretch goals:** Write data quality rules as YAML.


### 11. To‑Do GUI (Tkinter)

**What you build:** Desktop task list with add/complete and persistence.

**Skills you’ll learn:** Tkinter widgets, events, model‑view separation.

**Milestones:** Drag to reorder; save window state.

**Stretch goals:** Reminders via system notifications.


### 12. Rule‑Based Chatbot

**What you build:** Pattern‑match responses; small FAQ assistant.

**Skills you’ll learn:** regex, control flow, normalization.

**Milestones:** Fallback default; logging of conversations.

**Stretch goals:** Plug‑in architecture for handlers.


### 13. Email Sender (CLI)

**What you build:** Send templated emails via SMTP (test account).

**Skills you’ll learn:** smtplib, SSL/TLS, MIME, secrets handling.

**Milestones:** Dry‑run preview; attachments; rate limiting.

**Stretch goals:** Retry with exponential backoff.


### 14. Local URL Shortener

**What you build:** Map short codes to URLs and open in browser.

**Skills you’ll learn:** hashing, JSON store, input validation.

**Milestones:** Custom aliases; click counts.

**Stretch goals:** Tiny Flask front end.


### 15. Password Strength Checker

**What you build:** Score passwords by entropy and common rules.

**Skills you’ll learn:** regex, math/log2, file of common passwords.

**Milestones:** Feedback on weaknesses; unit tests.

**Stretch goals:** Dictionary/leetspeak checks.


### 16. Flask Mini API

**What you build:** Expose a couple of JSON endpoints with Flask.

**Skills you’ll learn:** routing, JSON response, blueprints, CORS.

**Milestones:** Input validation; error handlers; config per env.

**Stretch goals:** API docs with OpenAPI/Swagger.


### 17. Microblog Skeleton

**What you build:** Posts list/create/delete with SQLite and templates.

**Skills you’ll learn:** Flask, Jinja2, sessions, CSRF basics.

**Milestones:** Pagination; flash messages; tests with pytest.

**Stretch goals:** User accounts and login.


### 18. Testing Workshop

**What you build:** Backfill unit tests for 3 earlier projects.

**Skills you’ll learn:** pytest, fixtures, parametrization, coverage.

**Milestones:** 80%+ coverage; CI-friendly test commands.

**Stretch goals:** Property-based tests with hypothesis.


### 19. Backup & Zip Script

**What you build:** Zip important folders on schedule and rotate archives.

**Skills you’ll learn:** zipfile, pathlib, cron docs, logging.

**Milestones:** Exclude patterns; retention policy; checksum.

**Stretch goals:** Email success/failure report.


### 20. Task Scheduler

**What you build:** Run functions at intervals (every N minutes).

**Skills you’ll learn:** threading/timers, datetime math, graceful shutdown.

**Milestones:** Persist schedule; pause/resume.

**Stretch goals:** Crontab‑style parser.


### 21. RSS Reader (CLI)

**What you build:** Fetch feeds and display new items; mark as read.

**Skills you’ll learn:** feedparser, persistence, humanize times.

**Milestones:** Multiple feeds; filters; notify on new.

**Stretch goals:** Export to HTML digest.


### 22. QR Code Generator

**What you build:** Create QR codes from text/URLs and save PNGs.

**Skills you’ll learn:** qrcode/Pillow, file naming, CLI flags.

**Milestones:** Batch from CSV; logo overlay.

**Stretch goals:** Decode QR from images.


### 23. Excel Report Builder

**What you build:** Read CSV and write formatted Excel reports.

**Skills you’ll learn:** pandas, openpyxl/xlsxwriter, formatting.

**Milestones:** Conditional formatting; charts.

**Stretch goals:** Template with company branding.


### 24. Image Thumbnailer

**What you build:** Create thumbnails and preserve aspect ratios.

**Skills you’ll learn:** Pillow resize, pathlib glob, error handling.

**Milestones:** Quality settings; skip already processed.

**Stretch goals:** Concurrent processing with ThreadPool.


### 25. CLI Address Autocomplete

**What you build:** Local fuzzy search over addresses using trigram index.

**Skills you’ll learn:** text normalization, sets, basic indexing.

**Milestones:** Rank by score; paginate results.

**Stretch goals:** Persist compact index to disk.


---

## Level 3 — Intermediate (Mid-level Developer)

Build real applications: production‑like web apps, async work, packaging, documentation, CI, and deeper algorithms/data handling.


#### Checklist
- [ ] 1. Flask CRUD To‑Do (Full App)
- [ ] 2. Auth Basics & Password Hashing
- [ ] 3. REST API for To‑Do (FastAPI)
- [ ] 4. Async Web Scraper
- [ ] 5. Background Jobs with Redis
- [ ] 6. File Upload Service
- [ ] 7. PDF Search (Mini Index)
- [ ] 8. EDA on Public Dataset
- [ ] 9. Stock Tracker with DB
- [ ] 10. Word‑Frequency Analyzer
- [ ] 11. Multi‑Client Chat Server
- [ ] 12. Dockerize a Web App
- [ ] 13. Publish a Tiny Library
- [ ] 14. Production‑Grade CLI (click)
- [ ] 15. Requests Caching Layer
- [ ] 16. OAuth GitHub Viewer
- [ ] 17. Graph Algorithms Visualizer
- [ ] 18. Tetris with pygame
- [ ] 19. Folder Watch ETL
- [ ] 20. Structured Logging
- [ ] 21. Config Management
- [ ] 22. Docs Site (Sphinx/MkDocs)
- [ ] 23. Test Suite Mastery
- [ ] 24. GitHub Actions CI
- [ ] 25. PyInstaller Distribution

### 1. Flask CRUD To‑Do (Full App)

**What you build:** Multi‑user to‑do with auth, SQLite, and templates.

**Skills you’ll learn:** ORM/SQLAlchemy, blueprints, CSRF, sessions.

**Milestones:** Edit/delete; filtering; pagination; flash messages.

**Stretch goals:** Role‑based access control (RBAC).


### 2. Auth Basics & Password Hashing

**What you build:** Login/logout with salted hashing and sessions.

**Skills you’ll learn:** werkzeug.security, session mgmt, secure cookies.

**Milestones:** Password reset tokens; email flow (dev mode).

**Stretch goals:** Rate limiting and account lockout.


### 3. REST API for To‑Do (FastAPI)

**What you build:** Expose CRUD endpoints with pydantic schemas.

**Skills you’ll learn:** FastAPI, pydantic, dependency injection, OpenAPI.

**Milestones:** Validation errors; pagination; filtering.

**Stretch goals:** JWT auth and API keys.


### 4. Async Web Scraper

**What you build:** Crawl many pages concurrently and store results.

**Skills you’ll learn:** asyncio, aiohttp, semaphore, backoff.

**Milestones:** Retry on failures; polite delays; caching.

**Stretch goals:** Pluggable pipelines (save to CSV/SQLite).


### 5. Background Jobs with Redis

**What you build:** Queue tasks and process with workers (RQ).

**Skills you’ll learn:** Redis, job queues, idempotency, retry.

**Milestones:** Job status tracking; dead‑letter queue.

**Stretch goals:** Scheduled/delayed jobs.


### 6. File Upload Service

**What you build:** Upload files via web form and serve securely.

**Skills you’ll learn:** Flask/FastAPI streaming, MIME checks, temp files.

**Milestones:** Virus scan hook; size limits; presigned URLs (local emulation).

**Stretch goals:** Chunked uploads and resume.


### 7. PDF Search (Mini Index)

**What you build:** Extract text and build an inverted index for search.

**Skills you’ll learn:** pdfminer/pypdf, tokenization, indexing.

**Milestones:** Phrase queries; ranking; snippets.

**Stretch goals:** Boolean operators and field weights.


### 8. EDA on Public Dataset

**What you build:** Clean, analyze, and visualize a dataset end‑to‑end.

**Skills you’ll learn:** pandas, groupby, plotting, notebooks.

**Milestones:** Data quality report; clear charts; README.

**Stretch goals:** Simple regression/classification baseline.


### 9. Stock Tracker with DB

**What you build:** Fetch prices daily and chart history.

**Skills you’ll learn:** scheduling, HTTP APIs, pandas, matplotlib.

**Milestones:** Moving averages; alerts; dockerized service.

**Stretch goals:** Backtesting simple strategies.


### 10. Word‑Frequency Analyzer

**What you build:** Compute TF and TF‑IDF on text corpus.

**Skills you’ll learn:** nltk/spacy basics, stopwords, math/logs.

**Milestones:** Top terms per document; export report.

**Stretch goals:** Interactive search over corpus.


### 11. Multi‑Client Chat Server

**What you build:** Socket server supporting multiple clients and rooms.

**Skills you’ll learn:** sockets, threading, protocols, concurrency.

**Milestones:** Usernames; private messages; persistence.

**Stretch goals:** Asyncio version and WebSocket gateway.


### 12. Dockerize a Web App

**What you build:** Containerize your Flask/FastAPI app with Compose.

**Skills you’ll learn:** Dockerfile, Compose, env vars, volumes.

**Milestones:** Separate dev/prod configs; healthcheck.

**Stretch goals:** CI to build image on pushes.


### 13. Publish a Tiny Library

**What you build:** Create a utility lib with tests and packaging.

**Skills you’ll learn:** pyproject.toml, packaging, versioning, semver.

**Milestones:** Type hints; readme; CI tests.

**Stretch goals:** Prepare for PyPI publish (test index).


### 14. Production‑Grade CLI (click)

**What you build:** CLI with subcommands, config file, and logging.

**Skills you’ll learn:** click, logging, config management, UX.

**Milestones:** Colors; progress bars; good help pages.

**Stretch goals:** Plugins via entry points.


### 15. Requests Caching Layer

**What you build:** Add transparent caching to API calls.

**Skills you’ll learn:** requests-cache, cache keys, invalidation.

**Milestones:** Cache metrics; stale‑while‑revalidate.

**Stretch goals:** Pluggable backends (disk/Redis).


### 16. OAuth GitHub Viewer

**What you build:** Login with GitHub and list user repos/issues.

**Skills you’ll learn:** OAuth2 dance, sessions, pagination APIs.

**Milestones:** Rate‑limit handling; caching; retries.

**Stretch goals:** Star/unstar from the UI.


### 17. Graph Algorithms Visualizer

**What you build:** Visualize BFS/DFS/shortest paths on a graph.

**Skills you’ll learn:** networkx, matplotlib, algorithms.

**Milestones:** Weighted edges; export images.

**Stretch goals:** Interactive GUI with PyQt/PySimpleGUI.


### 18. Tetris with pygame

**What you build:** Playable Tetris with scoring and increasing speed.

**Skills you’ll learn:** pygame loop, collision, game state.

**Milestones:** Pause/resume; high scores; levels.

**Stretch goals:** Ghost piece and hold slot.


### 19. Folder Watch ETL

**What you build:** Watch a folder and transform new files automatically.

**Skills you’ll learn:** watchdog, pipelines, error handling.

**Milestones:** Retry policy; quarantine failures; metrics.

**Stretch goals:** Parallel processing per file type.


### 20. Structured Logging

**What you build:** JSON logs with correlation IDs and rotation.

**Skills you’ll learn:** logging config, filters, RotatingFileHandler.

**Milestones:** Log schema; log levels; sampling.

**Stretch goals:** Ship logs to Elasticsearch (local).


### 21. Config Management

**What you build:** Typed settings with env overrides.

**Skills you’ll learn:** pydantic/dynaconf, secrets, profiles.

**Milestones:** Validation errors; .env files.

**Stretch goals:** Dynamic reload of config.


### 22. Docs Site (Sphinx/MkDocs)

**What you build:** Host docs for one of your apps/libraries.

**Skills you’ll learn:** autodoc, code fences, site build.

**Milestones:** API reference; tutorials; versioned docs.

**Stretch goals:** Deploy docs on CI to Pages.


### 23. Test Suite Mastery

**What you build:** Mocks, fixtures, and coverage for a web app.

**Skills you’ll learn:** pytest, unittest.mock, coverage.

**Milestones:** 90%+ coverage; flake8/black/isort.

**Stretch goals:** Mutation testing (mutmut).


### 24. GitHub Actions CI

**What you build:** Run tests, linting, and build on every push.

**Skills you’ll learn:** YAML pipelines, caching, matrices.

**Milestones:** Badge in README; artifact uploads.

**Stretch goals:** Release on tags with changelog.


### 25. PyInstaller Distribution

**What you build:** Ship a CLI as a single binary/exe.

**Skills you’ll learn:** pyinstaller, entry points, assets.

**Milestones:** Cross‑platform notes; update strategy.

**Stretch goals:** Auto‑update check on start.


---

## Level 4 — Advanced (Senior Engineer)

Design for scale, reliability, and performance. Multiple services, observability, security, and data pipelines. Expect Docker, clouds (local emulation), and strong testing.


#### Checklist
- [ ] 1. FastAPI Production API
- [ ] 2. GraphQL Service
- [ ] 3. gRPC Microservices Pair
- [ ] 4. Event Pipeline with Kafka
- [ ] 5. Search Service
- [ ] 6. Recommendations (CF)
- [ ] 7. Realtime Dashboard
- [ ] 8. Feature Flags Service
- [ ] 9. Stripe‑like Payments (Test Mode)
- [ ] 10. Multi‑Tenant SaaS
- [ ] 11. Infra as Code (Pulumi/Terraform)
- [ ] 12. Observability Stack
- [ ] 13. Data Pipeline with Airflow/Prefect
- [ ] 14. ML Model Serving
- [ ] 15. Image Processing Pipeline
- [ ] 16. Geospatial Routing
- [ ] 17. Message Broker Workers
- [ ] 18. Distributed Locks
- [ ] 19. Sharding & Partitioning
- [ ] 20. Cython Acceleration
- [ ] 21. Async DB Layer
- [ ] 22. Security Hardening
- [ ] 23. Caching Strategies
- [ ] 24. Blue/Green Deploy (Compose)
- [ ] 25. Data Lake to Parquet + DuckDB

### 1. FastAPI Production API

**What you build:** JWT auth, roles, rate limit, and versioned endpoints.

**Skills you’ll learn:** FastAPI, JWT/OAuth2, pydantic models, dependency injection.

**Milestones:** Pagination/filter; validation; error mapping; OpenAPI docs.

**Stretch goals:** E2E tests with httpx + pytest.


### 2. GraphQL Service

**What you build:** Expose a GraphQL schema over existing data.

**Skills you’ll learn:** strawberry/graphene, resolvers, batching.

**Milestones:** Schema stitching; caching; dataloaders.

**Stretch goals:** Subscriptions via WebSockets.


### 3. gRPC Microservices Pair

**What you build:** User and Order services communicating over gRPC.

**Skills you’ll learn:** protobuf, gRPC, contracts, backward‑compatibility.

**Milestones:** Client libs; retries; deadlines; interceptors.

**Stretch goals:** Service mesh locally (Envoy).


### 4. Event Pipeline with Kafka

**What you build:** Ingest, transform, and sink events to a DB.

**Skills you’ll learn:** Kafka, producers/consumers, schemas, partitions.

**Milestones:** Exactly‑once semantics (discussion + at‑least‑once impl).

**Stretch goals:** Out‑of‑order handling with watermarking.


### 5. Search Service

**What you build:** Index documents and serve ranked search results.

**Skills you’ll learn:** Elasticsearch/OpenSearch, analyzers, query DSL.

**Milestones:** Highlighting; synonyms; pagination.

**Stretch goals:** Relevance tuning and evaluation.


### 6. Recommendations (CF)

**What you build:** Collaborative filtering movie/book recommender.

**Skills you’ll learn:** pandas, sparse matrices, cosine similarity.

**Milestones:** Cold‑start strategy; evaluation metrics.

**Stretch goals:** Implicit feedback (ALS) variant.


### 7. Realtime Dashboard

**What you build:** WebSocket stream of live metrics to frontend.

**Skills you’ll learn:** FastAPI websockets, pub/sub, backpressure.

**Milestones:** Reconnect logic; auth; history buffer.

**Stretch goals:** Server‑sent events fallback.


### 8. Feature Flags Service

**What you build:** Toggle features per user/segment with caching.

**Skills you’ll learn:** RBAC, caching (Redis), evaluation rules.

**Milestones:** Audit log; percentage rollouts.

**Stretch goals:** Targeting expressions DSL.


### 9. Stripe‑like Payments (Test Mode)

**What you build:** Create checkout sessions and verify webhooks.

**Skills you’ll learn:** webhooks, signature verify, idempotency keys.

**Milestones:** Receipts; refunds; error simulation.

**Stretch goals:** Retry/compensation transactions.


### 10. Multi‑Tenant SaaS

**What you build:** Isolate tenants in one DB (RLS or schema‑per‑tenant).

**Skills you’ll learn:** SQLAlchemy, tenancy models, security.

**Milestones:** Billing per tenant; quotas; audit trails.

**Stretch goals:** Tenant migrations automation.


### 11. Infra as Code (Pulumi/Terraform)

**What you build:** Provision app infra via code, reproducibly.

**Skills you’ll learn:** Pulumi/Terraform basics, state mgmt, modules.

**Milestones:** Dev/prod stacks; secrets; outputs.

**Stretch goals:** Policy as code checks.


### 12. Observability Stack

**What you build:** Logging, metrics, traces with OpenTelemetry.

**Skills you’ll learn:** Prometheus client, OTEL, context propagation.

**Milestones:** Dashboards; alert rules; SLO definitions.

**Stretch goals:** Trace‑based sampling strategies.


### 13. Data Pipeline with Airflow/Prefect

**What you build:** ETL DAG that moves and transforms data daily.

**Skills you’ll learn:** operators, retries, scheduling, XCom/artifacts.

**Milestones:** Backfills; parameterized runs.

**Stretch goals:** Data quality checks with Great Expectations.


### 14. ML Model Serving

**What you build:** Serve a versioned ML model behind an API.

**Skills you’ll learn:** FastAPI, model registry, pydantic, AB testing.

**Milestones:** Shadow traffic; metrics; drift alerts.

**Stretch goals:** Canary deploys with rollback.


### 15. Image Processing Pipeline

**What you build:** Transform images: resize, filters, OCR.

**Skills you’ll learn:** Pillow/OpenCV, queues, throughput tuning.

**Milestones:** Parallel workers; retries; metrics.

**Stretch goals:** GPU acceleration exploration.


### 16. Geospatial Routing

**What you build:** Shortest path between coordinates on a road graph.

**Skills you’ll learn:** osmnx, networkx, heuristics (A*).

**Milestones:** Avoid tolls; elevation cost; plotting routes.

**Stretch goals:** Turn‑by‑turn instruction generator.


### 17. Message Broker Workers

**What you build:** Producer/consumer system with RabbitMQ/Redis.

**Skills you’ll learn:** ack/requeue, dead letters, delivery modes.

**Milestones:** Exactly‑once illusions (idempotency).

**Stretch goals:** Priority queues and delayed messages.


### 18. Distributed Locks

**What you build:** Protect critical sections with Redis locks.

**Skills you’ll learn:** Redlock patterns, TTLs, fencing tokens.

**Milestones:** Renewal; lock contention tests.

**Stretch goals:** Lease‑based caches.


### 19. Sharding & Partitioning

**What you build:** Split data by key across DBs/partitions.

**Skills you’ll learn:** hashing, routing, rebalancing.

**Milestones:** Locality vs balance tradeoffs; metrics.

**Stretch goals:** Resharding without downtime (demo).


### 20. Cython Acceleration

**What you build:** Speed up a hot loop with Cython extension.

**Skills you’ll learn:** profiling, Cython types, build toolchain.

**Milestones:** 10x speedup; correctness tests.

**Stretch goals:** Compare PyPy/Numba variants.


### 21. Async DB Layer

**What you build:** Use async SQLAlchemy/SQLModel with connection pools.

**Skills you’ll learn:** async engines, transactions, pooling.

**Milestones:** Timeouts; retry; circuit breaker.

**Stretch goals:** Read replicas / write master split.


### 22. Security Hardening

**What you build:** Secrets mgmt, dependency scanning, input validation.

**Skills you’ll learn:** Bandit, pip‑audit, pydantic validators.

**Milestones:** CSP headers; secure cookies; CSRF tokens.

**Stretch goals:** Signed requests between services.


### 23. Caching Strategies

**What you build:** Local and Redis cache with invalidation rules.

**Skills you’ll learn:** TTL, LRU, cache stampede prevention.

**Milestones:** Write‑through vs write‑back; metrics.

**Stretch goals:** Hierarchical cache (L1/L2).


### 24. Blue/Green Deploy (Compose)

**What you build:** Switch traffic between two app versions safely.

**Skills you’ll learn:** nginx routing, healthchecks, rollback.

**Milestones:** Smoke tests; drain connections.

**Stretch goals:** Canary with percentage rollout.


### 25. Data Lake to Parquet + DuckDB

**What you build:** Ingest CSV→Parquet and query fast with DuckDB.

**Skills you’ll learn:** pandas, pyarrow, partitioning, SQL queries.

**Milestones:** Partition by date; statistics; manifest.

**Stretch goals:** Delta/iceberg style table basics (concept).


---

## Level 5 — Expert (Staff/Principal Engineer)

Systems design and platform work. You’ll prototype distributed systems, design for resiliency, and build reusable platforms that other teams can use. These are ambitious, multi‑week projects.


#### Checklist
- [ ] 1. Event‑Sourced System (CQRS)
- [ ] 2. Custom Task Queue
- [ ] 3. Consensus (Raft) Prototype
- [ ] 4. Mini Database Engine
- [ ] 5. Vector Search Service
- [ ] 6. Streaming Log Analytics
- [ ] 7. Rate Limiter Service
- [ ] 8. Feature Store for ML
- [ ] 9. Distributed Scheduler
- [ ] 10. Data Lineage & Governance
- [ ] 11. Predictive Caching Layer
- [ ] 12. Time‑Series Store
- [ ] 13. Ranking Experimentation Platform
- [ ] 14. Rules DSL Compiler
- [ ] 15. High‑Throughput HTTP Server
- [ ] 16. Retry/Backoff Library
- [ ] 17. Static Analysis Tooling
- [ ] 18. Schema Registry
- [ ] 19. Zero‑Downtime Migration Toolkit
- [ ] 20. Security & Compliance Scanner
- [ ] 21. Cost‑Aware Autoscaling Simulator
- [ ] 22. Chaos Engineering Toolkit
- [ ] 23. Multi‑Region Active‑Active Demo
- [ ] 24. Privacy‑Preserving Analytics
- [ ] 25. Observability Platform
- [ ] 26. Platform Starter Kits

### 1. Event‑Sourced System (CQRS)

**What you build:** Command/write model emits events; read model projects views.

**Skills you’ll learn:** domain modeling, event store, projections, idempotency.

**Milestones:** Rebuild read model; snapshots; replay speed.

**Stretch goals:** Multi‑tenant streams and GDPR delete.


### 2. Custom Task Queue

**What you build:** Design a Celery‑like queue with reliability semantics.

**Skills you’ll learn:** broker protocol, ack/retry, visibility timeout.

**Milestones:** At‑least‑once delivery; dead letters; metrics.

**Stretch goals:** Exactly‑once with dedupe keys and idempotency.


### 3. Consensus (Raft) Prototype

**What you build:** Replicated log with leader election and log compaction.

**Skills you’ll learn:** state machines, RPC, timeouts, quorum.

**Milestones:** Crash/recover; partition tests; snapshots.

**Stretch goals:** Membership changes during operation.


### 4. Mini Database Engine

**What you build:** Append‑only log, B‑Tree index, simple SQL parser.

**Skills you’ll learn:** storage layout, indexing, MVCC basics.

**Milestones:** Transactions; WAL; crash consistency tests.

**Stretch goals:** Query planner with cost estimates.


### 5. Vector Search Service

**What you build:** Embed text and serve nearest‑neighbor queries.

**Skills you’ll learn:** embeddings, ANN (faiss), indexing, batching.

**Milestones:** Upserts; versioning; recall@k evaluation.

**Stretch goals:** Hybrid BM25 + vector ranking.


### 6. Streaming Log Analytics

**What you build:** Ingest logs, index, and run query DSL (mini‑Splunk).

**Skills you’ll learn:** parsers, inverted index, time windows.

**Milestones:** Aggregations; alerting; dashboards.

**Stretch goals:** Query optimizer and hot/cold tiers.


### 7. Rate Limiter Service

**What you build:** Distributed token bucket with sliding window algorithm.

**Skills you’ll learn:** Redis scripts/Lua, clock skew, fairness.

**Milestones:** Global vs per‑key limits; headers; audits.

**Stretch goals:** Adaptive limits based on error budgets.


### 8. Feature Store for ML

**What you build:** Offline/online sync of features with freshness guarantees.

**Skills you’ll learn:** point‑in‑time joins, materialization, TTLs.

**Milestones:** Backfills; serving API; lineage metadata.

**Stretch goals:** Streaming features and drift detection.


### 9. Distributed Scheduler

**What you build:** Cron‑like system with leader election and failover.

**Skills you’ll learn:** locks, heartbeats, leases, idempotent jobs.

**Milestones:** Misfire handling; jitter; pause/resume.

**Stretch goals:** Cron expression shards and priorities.


### 10. Data Lineage & Governance

**What you build:** Track datasets, jobs, and their dependencies.

**Skills you’ll learn:** graph modeling, metadata store, hooks.

**Milestones:** Impact analysis; ownership; SLAs.

**Stretch goals:** OpenLineage integration and UI.


### 11. Predictive Caching Layer

**What you build:** Prefetch based on patterns with reinforcement learning lite.

**Skills you’ll learn:** Markov models/bandits, cache policy design.

**Milestones:** Hit‑rate metrics; ablation tests.

**Stretch goals:** Cost‑aware prefetching.


### 12. Time‑Series Store

**What you build:** Write‑optimized TSDB with compression and rollups.

**Skills you’ll learn:** columnar storage, delta encoding, downsampling.

**Milestones:** Compaction; retention; query engine.

**Stretch goals:** Cardinality management strategies.


### 13. Ranking Experimentation Platform

**What you build:** AB testing for ranking models with metrics pipeline.

**Skills you’ll learn:** experiment design, metric logging, stats.

**Milestones:** Guardrails; sequential testing; dashboards.

**Stretch goals:** Switchback tests for network effects.


### 14. Rules DSL Compiler

**What you build:** Create a small DSL and compile to Python AST.

**Skills you’ll learn:** parsing (lark/PLY), AST, codegen, safety.

**Milestones:** Static analysis; error reporting; tests.

**Stretch goals:** JIT via numba for numeric rules.


### 15. High‑Throughput HTTP Server

**What you build:** Tune uvicorn/uvloop, pool sizes, and kernel knobs.

**Skills you’ll learn:** async IO, load testing, profiling.

**Milestones:** Latency/throughput graphs; flamecharts.

**Stretch goals:** Zero‑copy responses and sendfile.


### 16. Retry/Backoff Library

**What you build:** Robust retries with jitter and circuit breaker.

**Skills you’ll learn:** decorators, exceptions, policies, packaging.

**Milestones:** Integrations; metrics; typed API.

**Stretch goals:** Publish to PyPI and semantic releases.


### 17. Static Analysis Tooling

**What you build:** Analyze Python AST to enforce org‑wide rules.

**Skills you’ll learn:** ast module, visitors, autofixes.

**Milestones:** Rule config; CI integration; reports.

**Stretch goals:** Language server protocol plugin.


### 18. Schema Registry

**What you build:** Centralize pydantic/Avro schemas with versioning and codegen.

**Skills you’ll learn:** compatibility checks, generators, registries.

**Milestones:** Deprecations; changelogs; governance flow.

**Stretch goals:** Multi‑language client SDKs.


### 19. Zero‑Downtime Migration Toolkit

**What you build:** Plan/apply DB schema/data changes safely.

**Skills you’ll learn:** expand‑contract, backfills, dual‑writes.

**Milestones:** Verification jobs; rollback; metrics.

**Stretch goals:** Auto‑generated plans from models.


### 20. Security & Compliance Scanner

**What you build:** Scan repos/infrastructure for policy violations.

**Skills you’ll learn:** AST, regex, config parsing, reporting.

**Milestones:** Baselines; auto‑fixes; suppression workflow.

**Stretch goals:** SBOM creation and diff.


### 21. Cost‑Aware Autoscaling Simulator

**What you build:** Simulate autoscaling based on workload and budgets.

**Skills you’ll learn:** queueing theory, policies, plotting.

**Milestones:** SLA/Cost frontier; scenario runner.

**Stretch goals:** RL‑based policy search.


### 22. Chaos Engineering Toolkit

**What you build:** Inject faults and run resilience experiments.

**Skills you’ll learn:** failure modes, experiments, observability.

**Milestones:** Steady‑state checks; blast radius limits.

**Stretch goals:** Automatic hypothesis generation.


### 23. Multi‑Region Active‑Active Demo

**What you build:** Run two regions with conflict resolution.

**Skills you’ll learn:** replication, CRDTs, traffic routing.

**Milestones:** Failover drills; consistency docs.

**Stretch goals:** Geo‑based routing and partition tests.


### 24. Privacy‑Preserving Analytics

**What you build:** Aggregate metrics with differential privacy noise.

**Skills you’ll learn:** DP basics, sensitivity, epsilon accounting.

**Milestones:** Utility vs privacy tradeoff plots.

**Stretch goals:** Federated learning simulation.


### 25. Observability Platform

**What you build:** Unified pipelines for logs/metrics/traces with SLOs.

**Skills you’ll learn:** OTEL collectors, exporters, SLO math.

**Milestones:** Error budget burn alerts; runbooks.

**Stretch goals:** Auto‑instrumentation playbooks.


### 26. Platform Starter Kits

**What you build:** Create cookiecutters/templates for teams to bootstrap apps.

**Skills you’ll learn:** cookiecutter, templates, docs, DX design.

**Milestones:** Secure defaults; CI/CD included; examples.

**Stretch goals:** Internal portal that scaffolds projects via UI.


---

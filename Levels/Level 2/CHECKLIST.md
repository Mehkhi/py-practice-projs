# Level 2 — Early Intermediate (Junior Developer)

Apply Python to practical tasks, small automation, simple GUIs and web/API usage. Learn packaging, testing, logging, and basic data handling.

## Checklist

- [ ] 1. CLI Notes with Search
  - What you build: Create, list, search, and tag notes stored in JSON.
  - Skills: argparse, json, search, timestamps, logging.
  - Milestones: Tag filter; fuzzy search; colored output.
  - Stretch goals: Encrypt notes using Fernet (cryptography).

- [ ] 2. Weather CLI via API
  - What you build: Fetch current weather by city using a public API.
  - Skills: requests, environment variables, error handling.
  - Milestones: Units switch; 5‑day forecast; retry with backoff.
  - Stretch goals: Cache responses on disk.

- [ ] 3. Currency Converter (API)
  - What you build: Convert between currencies using live rates.
  - Skills: requests, JSON parsing, Decimal for money.
  - Milestones: Historical rates; offline fallback rates file.
  - Stretch goals: Plot conversion history with matplotlib.

- [ ] 4. SQLite Contact Manager
  - What you build: CRUD contacts stored in SQLite via SQL queries.
  - Skills: sqlite3, schema design, parameterized queries.
  - Milestones: Unique constraints; pagination; migrations script.
  - Stretch goals: Search by phonetic match (soundex).

- [ ] 5. Web Log Analyzer
  - What you build: Parse Apache/Nginx logs and summarize traffic.
  - Skills: regex, datetime parsing, aggregation, CSV export.
  - Milestones: Top endpoints; status code breakdown; hourly chart.
  - Stretch goals: Detect basic anomalies (spikes).

- [ ] 6. Image Organizer
  - What you build: Sort images into folders by EXIF date.
  - Skills: Pillow, pathlib, shutil, metadata.
  - Milestones: Dry‑run; handle missing EXIF; duplicate detection.
  - Stretch goals: Rename using pattern YYYY‑MM‑DD_HH‑MM‑SS.

- [ ] 7. Markdown → HTML Converter
  - What you build: Turn .md files into HTML with templates.
  - Skills: markdown lib, Jinja2, file walking.
  - Milestones: TOC generation; code highlighting.
  - Stretch goals: Static site with navigation index.

- [ ] 8. Basic Web Scraper
  - What you build: Download a page and extract items (titles, links).
  - Skills: requests, BeautifulSoup, CSS selectors.
  - Milestones: Follow pagination; respect robots.txt; politeness delay.
  - Stretch goals: Export to SQLite for later querying.

- [ ] 9. PDF Merger/Splitter
  - What you build: Combine or split PDFs from the command line.
  - Skills: PyPDF2/pypdf, file I/O, argparse.
  - Milestones: Range selection; rotate; metadata copy.
  - Stretch goals: Bookmarks and table of contents.

- [ ] 10. CSV Cleaner
  - What you build: Load CSV, fix missing values, standardize columns.
  - Skills: pandas basics, dtype handling, writing CSV.
  - Milestones: Summary report; detect outliers; schema validation.
  - Stretch goals: Write data quality rules as YAML.

- [ ] 11. To‑Do GUI (Tkinter)
  - What you build: Desktop task list with add/complete and persistence.
  - Skills: Tkinter widgets, events, model‑view separation.
  - Milestones: Drag to reorder; save window state.
  - Stretch goals: Reminders via system notifications.

- [ ] 12. Rule‑Based Chatbot
  - What you build: Pattern‑match responses; small FAQ assistant.
  - Skills: regex, control flow, normalization.
  - Milestones: Fallback default; logging of conversations.
  - Stretch goals: Plug‑in architecture for handlers.

- [ ] 13. Email Sender (CLI)
  - What you build: Send templated emails via SMTP (test account).
  - Skills: smtplib, SSL/TLS, MIME, secrets handling.
  - Milestones: Dry‑run preview; attachments; rate limiting.
  - Stretch goals: Retry with exponential backoff.

- [ ] 14. Local URL Shortener
  - What you build: Map short codes to URLs and open in browser.
  - Skills: hashing, JSON store, input validation.
  - Milestones: Custom aliases; click counts.
  - Stretch goals: Tiny Flask front end.

- [ ] 15. Password Strength Checker
  - What you build: Score passwords by entropy and common rules.
  - Skills: regex, math/log2, file of common passwords.
  - Milestones: Feedback on weaknesses; unit tests.
  - Stretch goals: Dictionary/leetspeak checks.

- [ ] 16. Flask Mini API
  - What you build: Expose a couple of JSON endpoints with Flask.
  - Skills: routing, JSON response, blueprints, CORS.
  - Milestones: Input validation; error handlers; config per env.
  - Stretch goals: API docs with OpenAPI/Swagger.

- [ ] 17. Microblog Skeleton
  - What you build: Posts list/create/delete with SQLite and templates.
  - Skills: Flask, Jinja2, sessions, CSRF basics.
  - Milestones: Pagination; flash messages; tests with pytest.
  - Stretch goals: User accounts and login.

- [ ] 18. Testing Workshop
  - What you build: Backfill unit tests for 3 earlier projects.
  - Skills: pytest, fixtures, parametrization, coverage.
  - Milestones: 80%+ coverage; CI-friendly test commands.
  - Stretch goals: Property-based tests with hypothesis.

- [ ] 19. Backup & Zip Script
  - What you build: Zip important folders on schedule and rotate archives.
  - Skills: zipfile, pathlib, cron docs, logging.
  - Milestones: Exclude patterns; retention policy; checksum.
  - Stretch goals: Email success/failure report.

- [ ] 20. Task Scheduler
  - What you build: Run functions at intervals (every N minutes).
  - Skills: threading/timers, datetime math, graceful shutdown.
  - Milestones: Persist schedule; pause/resume.
  - Stretch goals: Crontab‑style parser.

- [ ] 21. RSS Reader (CLI)
  - What you build: Fetch feeds and display new items; mark as read.
  - Skills: feedparser, persistence, humanize times.
  - Milestones: Multiple feeds; filters; notify on new.
  - Stretch goals: Export to HTML digest.

- [ ] 22. QR Code Generator
  - What you build: Create QR codes from text/URLs and save PNGs.
  - Skills: qrcode/Pillow, file naming, CLI flags.
  - Milestones: Batch from CSV; logo overlay.
  - Stretch goals: Decode QR from images.

- [ ] 23. Excel Report Builder
  - What you build: Read CSV and write formatted Excel reports.
  - Skills: pandas, openpyxl/xlsxwriter, formatting.
  - Milestones: Conditional formatting; charts.
  - Stretch goals: Template with company branding.

- [ ] 24. Image Thumbnailer
  - What you build: Create thumbnails and preserve aspect ratios.
  - Skills: Pillow resize, pathlib glob, error handling.
  - Milestones: Quality settings; skip already processed.
  - Stretch goals: Concurrent processing with ThreadPool.

- [ ] 25. CLI Address Autocomplete
  - What you build: Local fuzzy search over addresses using trigram index.
  - Skills: text normalization, sets, basic indexing.
  - Milestones: Rank by score; paginate results.
  - Stretch goals: Persist compact index to disk.

---

## Detailed Spec Sheets — Level 2 (Early Intermediate)

This section turns each checklist item into an implementation spec with **required features** and **bonus features**. Every feature lists a **difficulty** rating, an **extensive breakdown of what it teaches**, and **acceptance criteria** so you can self‑verify.

### Difficulty Legend
- **1** = Very easy (few lines, minimal edge cases)
- **2** = Easy (simple logic, basic edge cases)
- **3** = Moderate (multiple components, careful handling)
- **4** = Hard (non‑trivial algorithms/design, extensive testing)
- **5** = Very hard (complex algorithms or architecture)

### Common Requirements for Project Completion
- All **required features** implemented and demonstrated.
- At least **5 unit tests** per project (happy paths + edge cases).
- A clear **README** with setup steps, usage examples, and limitations.
- Code formatted with **black** and linted with **ruff/flake8**.
- Public functions include **type hints**; `mypy` passes or deviations are documented.

> Use these as GitHub issues (one feature = one issue) with labels like `difficulty/2`, `type/required`, `type/bonus` for easy tracking.

---

### 1) CLI Notes with Search
**What you’re building:** A notes CLI that stores JSON notes with tags and simple search.
**Core skills:** `argparse`, JSON I/O, indexing, timestamps, logging.

#### Required Features
- **R1. Create/List/View/Delete notes (JSON store)** — **Difficulty 2/5**
  - **What it teaches:**
    - JSON schema design and forward‑compatible fields (e.g., `id`, `title`, `body`, `tags`, `created_at`, `updated_at`, `archived`).
    - Atomic writes (write temp file then rename) to avoid corruption.
    - Separation of concerns: storage layer vs CLI layer.
  - **Acceptance criteria:**
    - CRUD works with unique IDs; file remains valid JSON after interruptions.
    - `list` shows title + created time; `view` shows full note.

- **R2. Tagging and tag filters** — **Difficulty 2/5**
  - **What it teaches:**
    - Normalizing input (lowercasing tags, trimming whitespace).
    - Indexing by tags for O(1) lookups (build at load time).
    - Designing queries (AND vs OR semantics for multiple tags).
  - **Acceptance criteria:**
    - `--tag` filters include correct notes; multiple tags behave as documented.

- **R3. Full‑text search (contains match)** — **Difficulty 2/5**
  - **What it teaches:**
    - Tokenization basics and stopwords trade‑offs.
    - Precomputing a simple inverted index for titles/bodies.
    - UX: show snippets with highlighted terms.
  - **Acceptance criteria:**
    - `search "term"` returns ranked results; empty search is rejected.

- **R4. Timestamps + logging** — **Difficulty 1/5**
  - **What it teaches:**
    - `datetime.now().isoformat()` usage and consistency.
    - `logging` configuration (levels, handlers, log format).
  - **Acceptance criteria:**
    - Create/update times populate; basic INFO/ERROR logs written to file.

#### Bonus Features
- **B1. Fuzzy search (trigram / `difflib`)** — **Difficulty 3/5**
  - **What it teaches:** Similarity metrics, thresholds, and ranking UX.
  - **Acceptance criteria:** Misspellings still find likely notes with scores.

- **B2. Encryption at rest (Fernet)** — **Difficulty 3/5**
  - **What it teaches:** Key management, encrypt/decrypt boundaries, risks of losing keys.
  - **Acceptance criteria:** Encrypted file unreadable without key; CLI can decrypt transparently for the user.

- **B3. Colored output** — **Difficulty 1/5**
  - **What it teaches:** Terminal UX using `rich`/`colorama`.
  - **Acceptance criteria:** List/search/view commands render consistently with color.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 2) Weather CLI via API
**What you’re building:** Query a public weather API for current conditions.
**Core skills:** `requests`, environment variables, HTTP error handling.

#### Required Features
- **R1. API client with env‑based API key** — **Difficulty 2/5**
  - **What it teaches:** Using `os.environ`, 401/403 handling, defensive retries on 5xx.
  - **Acceptance criteria:** Missing/invalid key yields clear error; happy path prints weather.

- **R2. Units switch (metric/imperial)** — **Difficulty 1/5**
  - **What it teaches:** Parameterizing requests and formatting output consistently.
  - **Acceptance criteria:** `--units metric|imperial` alters both request params and display.

- **R3. City lookup and validation** — **Difficulty 2/5**
  - **What it teaches:** Normalizing city input, handling ambiguous cities (name + country code), and graceful "not found" paths.
  - **Acceptance criteria:** Ambiguous or invalid cities yield friendly guidance.

- **R4. 5‑day forecast (basic)** — **Difficulty 2/5**
  - **What it teaches:** Iterating API pages or list objects; summarizing min/max/avg per day.
  - **Acceptance criteria:** Prints a table of daily highs/lows with dates.

#### Bonus Features
- **B1. On‑disk response cache** — **Difficulty 2/5**
  - **What it teaches:** Cache keys, TTL control, invalidation strategy.
  - **Acceptance criteria:** Repeated calls hit cache; `--no-cache` bypass supported.

- **B2. Retry with exponential backoff** — **Difficulty 2/5**
  - **What it teaches:** Transient error handling patterns; jitter.
  - **Acceptance criteria:** 5xx/timeout retries logged; eventual failure explained.

- **B3. Geo‑coordinates support** — **Difficulty 2/5**
  - **What it teaches:** Accepting latitude/longitude inputs; validation.
  - **Acceptance criteria:** `--lat --lon` path returns same data as by city.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 3) Currency Converter (API)
**What you’re building:** Convert currencies using live rates.
**Core skills:** `requests`, JSON parsing, `Decimal` for money.

#### Required Features
- **R1. Live rates fetch + `Decimal` math** — **Difficulty 2/5**
  - **What it teaches:** Avoiding float rounding errors; validating currency codes.
  - **Acceptance criteria:** Known rate pairs compute accurately within tolerance.

- **R2. Historical rates** — **Difficulty 2/5**
  - **What it teaches:** Date parameters, time‑series handling, and formatting.
  - **Acceptance criteria:** `--date YYYY-MM-DD` uses that day’s rates.

- **R3. Offline fallback** — **Difficulty 2/5**
  - **What it teaches:** Caching last good snapshot; stale data warnings.
  - **Acceptance criteria:** No network still converts using last snapshot with banner.

- **R4. Validation & UX** — **Difficulty 1/5**
  - **What it teaches:** ISO codes, helpful errors, and examples in `--help`.
  - **Acceptance criteria:** Invalid codes rejected with suggestions.

#### Bonus Features
- **B1. Plot conversion history** — **Difficulty 2/5**
  - **What it teaches:** `matplotlib` line chart, date ticks, moving averages.
  - **Acceptance criteria:** Saves PNG with legend and units.

- **B2. Multi‑currency table** — **Difficulty 2/5**
  - **What it teaches:** Batch queries and table formatting.
  - **Acceptance criteria:** Base → many quote currencies table exported to CSV.

- **B3. Alerts on threshold** — **Difficulty 2/5**
  - **What it teaches:** Simple rules engine; notifications.
  - **Acceptance criteria:** Prints/plays alert when crossing a configured rate.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 4) SQLite Contact Manager
**What you’re building:** Manage contacts with SQLite via SQL queries.
**Core skills:** `sqlite3`, schema design, parameterized queries.

#### Required Features
- **R1. Schema and migrations** — **Difficulty 2/5**
  - **What it teaches:** Designing tables (`contacts`, `emails`, `phones`), indexes, and evolving schemas.
  - **Acceptance criteria:** Migration script upgrades DB without data loss.

- **R2. CRUD with parameterized SQL** — **Difficulty 2/5**
  - **What it teaches:** Preventing SQL injection; returning rows as dicts.
  - **Acceptance criteria:** Insert/update/delete and list/search work reliably.

- **R3. Unique constraints & de‑dup** — **Difficulty 2/5**
  - **What it teaches:** `UNIQUE` on email; conflict handling (`INSERT OR IGNORE`).
  - **Acceptance criteria:** Duplicate emails rejected gracefully.

- **R4. Pagination & sorting** — **Difficulty 1/5**
  - **What it teaches:** LIMIT/OFFSET and ORDER BY.
  - **Acceptance criteria:** Large lists page correctly; sort by name or created.

#### Bonus Features
- **B1. Phonetic search (soundex/metaphone)** — **Difficulty 3/5**
  - **What it teaches:** Fuzzy name matching; custom SQL functions.
  - **Acceptance criteria:** "Jon" finds "John"; ranked by closeness.

- **B2. Import/export CSV** — **Difficulty 2/5**
  - **What it teaches:** ETL patterns and schema validation.
  - **Acceptance criteria:** Round‑trips maintain data fidelity.

- **B3. Groups/labels** — **Difficulty 2/5**
  - **What it teaches:** Many‑to‑many relations.
  - **Acceptance criteria:** List contacts by group; add/remove groups.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 5) Web Log Analyzer
**What you’re building:** Parse and summarize Apache/Nginx logs.
**Core skills:** regex parsing, datetime, aggregation, CSV export.

#### Required Features
- **R1. Parser for Common/Combined Log Format** — **Difficulty 2/5**
  - **What it teaches:** Robust regex; handling malformed lines.
  - **Acceptance criteria:** ≥99% lines parsed on sample logs; bad lines counted.

- **R2. Status and endpoint summaries** — **Difficulty 2/5**
  - **What it teaches:** Group‑by aggregations; top‑N queries.
  - **Acceptance criteria:** Tables for status code distribution and top endpoints.

- **R3. Hourly traffic chart** — **Difficulty 2/5**
  - **What it teaches:** Time bucketing; time‑zone normalization.
  - **Acceptance criteria:** CSV and ASCII chart rendered for requests/hour.

- **R4. Export report** — **Difficulty 1/5**
  - **What it teaches:** Writing CSV/JSON summaries.
  - **Acceptance criteria:** Files created; consistent schema.

#### Bonus Features
- **B1. Bot/user‑agent filters** — **Difficulty 2/5**
  - **What it teaches:** UA heuristics; whitelist/blacklist configs.
  - **Acceptance criteria:** Filtered views exclude known bots.

- **B2. Spike/anomaly detection** — **Difficulty 3/5**
  - **What it teaches:** Rolling averages and z‑score alerts.
  - **Acceptance criteria:** Spikes flagged with threshold and timestamp.

- **B3. GeoIP breakdown (if DB available)** — **Difficulty 3/5**
  - **What it teaches:** IP→country lookup and grouping.
  - **Acceptance criteria:** Country histogram produced.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 6) Image Organizer
**What you’re building:** Sort photos into folders by EXIF date.
**Core skills:** Pillow, `pathlib`, `shutil`, metadata handling.

#### Required Features
- **R1. Read EXIF and derive capture date** — **Difficulty 2/5**
  - **What it teaches:** Robust EXIF parsing; fallback to file mtime.
  - **Acceptance criteria:** Images without EXIF still categorized by mtime.

- **R2. Dry‑run and plan preview** — **Difficulty 1/5**
  - **What it teaches:** Safety in file operations; printing planned moves.
  - **Acceptance criteria:** `--dry-run` moves nothing; shows intended actions.

- **R3. Destination scheme (YYYY/MM/DD)** — **Difficulty 1/5**
  - **What it teaches:** Path construction and directory creation.
  - **Acceptance criteria:** Files end up in the correct dated folders.

- **R4. Duplicate detection by hash** — **Difficulty 2/5**
  - **What it teaches:** Hashing strategies and collision handling.
  - **Acceptance criteria:** Duplicates moved or skipped with a report.

#### Bonus Features
- **B1. Rename to pattern** — **Difficulty 2/5**
  - **What it teaches:** Safe renames; conflict suffixing.
  - **Acceptance criteria:** `YYYY-MM-DD_HH-MM-SS_###.jpg` naming applied.

- **B2. Concurrency (ThreadPool)** — **Difficulty 3/5**
  - **What it teaches:** IO parallelism; progress reporting.
  - **Acceptance criteria:** Speed improves on many files; no data loss.

- **B3. Sidecar JSON manifest** — **Difficulty 2/5**
  - **What it teaches:** Recording move plans for undo.
  - **Acceptance criteria:** Manifest supports rollback of last run.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 7) Markdown → HTML Converter
**What you’re building:** Convert `.md` files to HTML with a template.
**Core skills:** `markdown` lib, Jinja2, file walking.

#### Required Features
- **R1. Convert MD → HTML with template** — **Difficulty 2/5**
  - **What it teaches:** Pipeline design; separating content from presentation.
  - **Acceptance criteria:** Body renders inside a base template; CSS linked.

- **R2. Code highlighting** — **Difficulty 2/5**
  - **What it teaches:** Markdown extensions and Pygments.
  - **Acceptance criteria:** Code blocks highlighted; languages respected.

- **R3. Table of contents (TOC)** — **Difficulty 2/5**
  - **What it teaches:** Heading parsing and anchor generation.
  - **Acceptance criteria:** TOC links jump to sections.

- **R4. Directory walk** — **Difficulty 1/5**
  - **What it teaches:** Recursing folders; writing outputs next to inputs.
  - **Acceptance criteria:** All `.md` in tree processed; skip output dir.

#### Bonus Features
- **B1. Static site index** — **Difficulty 2/5**
  - **What it teaches:** Generating navigation pages from the file tree.
  - **Acceptance criteria:** Index lists pages with titles and links.

- **B2. Sitemap & RSS (if blog)** — **Difficulty 2/5**
  - **What it teaches:** XML generation; date metadata.
  - **Acceptance criteria:** Valid XML files emitted.

- **B3. Asset copying** — **Difficulty 1/5**
  - **What it teaches:** Copying referenced images/css.
  - **Acceptance criteria:** Relative links resolve in output.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 8) Basic Web Scraper
**What you’re building:** Fetch a page and extract items (titles, links).
**Core skills:** `requests`, BeautifulSoup, CSS selectors.

#### Required Features
- **R1. Fetch and parse** — **Difficulty 1/5**
  - **What it teaches:** GET requests; HTML parsing; error handling.
  - **Acceptance criteria:** Non‑200s don’t crash; content parsed.

- **R2. Item extraction** — **Difficulty 2/5**
  - **What it teaches:** CSS selectors; normalization; deduping.
  - **Acceptance criteria:** Items listed with title + URL.

- **R3. Pagination follow** — **Difficulty 2/5**
  - **What it teaches:** Next‑page discovery; stopping criteria.
  - **Acceptance criteria:** Traverses until no next page or max limit.

- **R4. robots.txt & politeness** — **Difficulty 2/5**
  - **What it teaches:** Respectful scraping; delays; user agent setting.
  - **Acceptance criteria:** Respects disallow rules; throttle respected.

#### Bonus Features
- **B1. SQLite export** — **Difficulty 2/5**
  - **What it teaches:** Persisting items for later querying.
  - **Acceptance criteria:** Table created; duplicates avoided.

- **B2. Cache pages on disk** — **Difficulty 2/5**
  - **What it teaches:** Hashing URLs to filenames; TTL control.
  - **Acceptance criteria:** Re‑runs hit cache when fresh.

- **B3. Backoff & retry** — **Difficulty 2/5**
  - **What it teaches:** Retry policies with jitter.
  - **Acceptance criteria:** Transient failures don’t abort the crawl.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 9) PDF Merger/Splitter
**What you’re building:** Merge/split/rotate PDFs from the CLI.
**Core skills:** `pypdf`/PyPDF2, file I/O, `argparse`.

#### Required Features
- **R1. Merge PDFs in order** — **Difficulty 1/5**
  - **What it teaches:** File iteration; output writer basics.
  - **Acceptance criteria:** Output has pages in the given order.

- **R2. Split by ranges** — **Difficulty 2/5**
  - **What it teaches:** Range parsing (e.g., `1-3,7,10-`).
  - **Acceptance criteria:** Produces multiple files with correct ranges.

- **R3. Rotate pages** — **Difficulty 1/5**
  - **What it teaches:** Page transforms in PDF libs.
  - **Acceptance criteria:** Selected pages rotate 90/180 degrees.

- **R4. Metadata copy** — **Difficulty 1/5**
  - **What it teaches:** Reading/writing document info.
  - **Acceptance criteria:** Title/author copied where possible.

#### Bonus Features
- **B1. Bookmarks/TOC** — **Difficulty 3/5**
  - **What it teaches:** Outlines and destinations.
  - **Acceptance criteria:** Top‑level bookmarks created as specified.

- **B2. Password‑protected input** — **Difficulty 2/5**
  - **What it teaches:** Decrypting with provided password.
  - **Acceptance criteria:** Fails gracefully on wrong password.

- **B3. Linearization hint** — **Difficulty 2/5** *(conceptual)*
  - **What it teaches:** Web‑optimized PDFs.
  - **Acceptance criteria:** Documented whether library supports it.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 10) CSV Cleaner
**What you’re building:** Load a CSV, clean it, and write a standardized output.
**Core skills:** pandas basics, dtype handling, CSV writing.

#### Required Features
- **R1. Column normalization** — **Difficulty 2/5**
  - **What it teaches:** Renaming, trimming, and consistent casing.
  - **Acceptance criteria:** Mapping config applied; unknown columns logged.

- **R2. Missing values strategy** — **Difficulty 2/5**
  - **What it teaches:** Imputation rules (mean/median/const); per‑column policy.
  - **Acceptance criteria:** Null counts before/after reported.

- **R3. Dtype coercion** — **Difficulty 2/5**
  - **What it teaches:** `astype` conversions; error handling.
  - **Acceptance criteria:** Invalid rows reported; schema documented.

- **R4. Summary report** — **Difficulty 1/5**
  - **What it teaches:** Descriptives (min/max/mean); outlier flags.
  - **Acceptance criteria:** Writes a human‑readable summary file.

#### Bonus Features
- **B1. YAML data quality rules** — **Difficulty 3/5**
  - **What it teaches:** Declarative validation; schema checks.
  - **Acceptance criteria:** Violations listed per rule with counts.

- **B2. Outlier detection** — **Difficulty 2/5**
  - **What it teaches:** Z‑score/IQR basics.
  - **Acceptance criteria:** Rows flagged with reasons.

- **B3. Row‑level error CSV** — **Difficulty 2/5**
  - **What it teaches:** Issue tracking per row.
  - **Acceptance criteria:** Separate CSV of rejected rows produced.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 11) To‑Do GUI (Tkinter)
**What you’re building:** Desktop to‑do app with persistence.
**Core skills:** Tkinter widgets, events, model‑view separation.

#### Required Features
- **R1. Add/complete/delete tasks** — **Difficulty 2/5**
  - **What it teaches:** Event binding, list models, and sync to storage.
  - **Acceptance criteria:** UI updates in place; model saved to disk.

- **R2. Drag to reorder** — **Difficulty 3/5**
  - **What it teaches:** Drag‑and‑drop in Tkinter; index management.
  - **Acceptance criteria:** Order persists across sessions.

- **R3. Save window state** — **Difficulty 1/5**
  - **What it teaches:** Persisting geometry and column widths.
  - **Acceptance criteria:** Reopen restores window size/position.

- **R4. MV separation** — **Difficulty 2/5**
  - **What it teaches:** Keeping UI and logic separate for testing.
  - **Acceptance criteria:** Core list logic testable without GUI.

#### Bonus Features
- **B1. System notifications** — **Difficulty 2/5**
  - **What it teaches:** OS notification APIs and timing.
  - **Acceptance criteria:** Due tasks trigger notifications.

- **B2. Recurring tasks** — **Difficulty 3/5**
  - **What it teaches:** Scheduling rules; next occurrence calculation.
  - **Acceptance criteria:** Recurrence editable and durable.

- **B3. Themes** — **Difficulty 1/5**
  - **What it teaches:** Styling Tkinter widgets.
  - **Acceptance criteria:** At least two switchable themes.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 12) Rule‑Based Chatbot
**What you’re building:** A small FAQ assistant via patterns.
**Core skills:** regex, control flow, normalization.

#### Required Features
- **R1. Normalization pipeline** — **Difficulty 2/5**
  - **What it teaches:** Lowercasing, punctuation stripping, whitespace collapsing.
  - **Acceptance criteria:** Same intent recognized despite casing/punctuation.

- **R2. Intent patterns** — **Difficulty 2/5**
  - **What it teaches:** Regex design; capture groups for slots.
  - **Acceptance criteria:** Patterns drive responses; tests cover overlaps.

- **R3. Fallback default** — **Difficulty 1/5**
  - **What it teaches:** Guard rails when nothing matches; help text.
  - **Acceptance criteria:** Non‑matches produce friendly guidance.

- **R4. Conversation logging** — **Difficulty 1/5**
  - **What it teaches:** Appending JSONL transcripts; redacting secrets.
  - **Acceptance criteria:** Logs contain timestamp, input, intent, response.

#### Bonus Features
- **B1. Plug‑in handler architecture** — **Difficulty 3/5**
  - **What it teaches:** Dynamic imports; discovery; handler registry.
  - **Acceptance criteria:** New intents load without code changes.

- **B2. Context memory (short‑term)** — **Difficulty 3/5**
  - **What it teaches:** Sliding windows; simple state machines.
  - **Acceptance criteria:** Follow‑ups resolve pronouns within N turns.

- **B3. Test harness** — **Difficulty 2/5**
  - **What it teaches:** Golden files for input→output tests.
  - **Acceptance criteria:** `pytest` runs and validates sample conversations.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 13) Email Sender (CLI)
**What you’re building:** Send templated emails via SMTP (test account).
**Core skills:** `smtplib`, SSL/TLS, MIME, secrets handling.

#### Required Features
- **R1. SMTP client with TLS** — **Difficulty 2/5**
  - **What it teaches:** Auth flows; ports; STARTTLS vs SMTPS.
  - **Acceptance criteria:** Connects and sends via test SMTP; bad creds handled.

- **R2. Template rendering** — **Difficulty 2/5**
  - **What it teaches:** Jinja2 templates; variables from JSON/CSV.
  - **Acceptance criteria:** Personalization fields substituted correctly.

- **R3. Dry‑run preview** — **Difficulty 1/5**
  - **What it teaches:** Printing composed emails before send.
  - **Acceptance criteria:** `--dry-run` prints payload; sends nothing.

- **R4. Attachments & rate‑limit** — **Difficulty 2/5**
  - **What it teaches:** MIME parts; respecting provider rate limits.
  - **Acceptance criteria:** Attaches files; delays between sends configurable.

#### Bonus Features
- **B1. Exponential backoff on failure** — **Difficulty 2/5**
  - **What it teaches:** Retry with jitter; idempotency (avoid duplicates).
  - **Acceptance criteria:** Retries logged; stops after max attempts.

- **B2. CSV mail merge** — **Difficulty 2/5**
  - **What it teaches:** Batch personalization; per‑row status tracking.
  - **Acceptance criteria:** Success/failure report CSV produced.

- **B3. Signed messages (DKIM, optional)** — **Difficulty 4/5**
  - **What it teaches:** Email signing basics; deliverability.
  - **Acceptance criteria:** Documented setup; signatures added where supported.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 14) Local URL Shortener
**What you’re building:** Map short codes to URLs and open them.
**Core skills:** hashing, JSON store, input validation.

#### Required Features
- **R1. Short code generation** — **Difficulty 2/5**
  - **What it teaches:** Hash→base62, collision checks.
  - **Acceptance criteria:** Codes unique within store.

- **R2. URL validation & normalization** — **Difficulty 2/5**
  - **What it teaches:** Scheme checks, punycode/IDN basics, safe redirects.
  - **Acceptance criteria:** Invalid URLs rejected with reason.

- **R3. JSON persistence** — **Difficulty 1/5**
  - **What it teaches:** Durable writes and backups.
  - **Acceptance criteria:** Store survives restarts; backup file available.

- **R4. Open in browser** — **Difficulty 1/5**
  - **What it teaches:** `webbrowser` module usage.
  - **Acceptance criteria:** `open <code>` launches default browser.

#### Bonus Features
- **B1. Custom aliases** — **Difficulty 2/5**
  - **What it teaches:** Reserved names; conflict resolution.
  - **Acceptance criteria:** User‑provided short codes accepted if available.

- **B2. Click counts & last access** — **Difficulty 2/5**
  - **What it teaches:** Analytics fundamentals.
  - **Acceptance criteria:** Stats command prints counts and recent usage.

- **B3. Tiny Flask front‑end** — **Difficulty 2/5**
  - **What it teaches:** Minimal redirect service.
  - **Acceptance criteria:** `GET /<code>` redirects; 404 on unknown codes.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 15) Password Strength Checker
**What you’re building:** Score passwords by entropy and rules.
**Core skills:** regex, `math.log2`, common password lists.

#### Required Features
- **R1. Entropy estimation** — **Difficulty 2/5**
  - **What it teaches:** Character set sizes; length impact; bits of entropy.
  - **Acceptance criteria:** Entropy printed with rationale.

- **R2. Rule checks** — **Difficulty 2/5**
  - **What it teaches:** Minimum length, classes, repeated sequences.
  - **Acceptance criteria:** Violations listed with suggestions.

- **R3. Common password detection** — **Difficulty 2/5**
  - **What it teaches:** Large list lookup; memory considerations.
  - **Acceptance criteria:** Known bad passwords flagged instantly.

- **R4. Feedback summary** — **Difficulty 1/5**
  - **What it teaches:** Clear UX messaging; prioritizing recommendations.
  - **Acceptance criteria:** Ranked suggestions output.

#### Bonus Features
- **B1. Leetspeak variants** — **Difficulty 2/5**
  - **What it teaches:** Transformations; expanding match space.
  - **Acceptance criteria:** `p@ssw0rd` detected as weak.

- **B2. Offline Bloom filter** — **Difficulty 3/5**
  - **What it teaches:** Probabilistic data structures; false positives.
  - **Acceptance criteria:** Large dataset fit in memory with acceptable FP rate.

- **B3. zxcvbn‑style scoring (lite)** — **Difficulty 3/5**
  - **What it teaches:** Pattern finding; dictionary + keyboard walks.
  - **Acceptance criteria:** Composite score more correlated with actual strength.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 16) Flask Mini API
**What you’re building:** A tiny JSON API service.
**Core skills:** routing, JSON responses, blueprints, CORS.

#### Required Features
- **R1. Endpoints + blueprints** — **Difficulty 2/5**
  - **What it teaches:** Organizing routes and modularizing code.
  - **Acceptance criteria:** Namespaced routes; clean app factory.

- **R2. Input validation** — **Difficulty 2/5**
  - **What it teaches:** Marshmallow/pydantic‑style validation and error mapping.
  - **Acceptance criteria:** 400s include helpful messages with fields.

- **R3. Error handlers** — **Difficulty 1/5**
  - **What it teaches:** Centralized exception→response mapping.
  - **Acceptance criteria:** Consistent JSON error shape.

- **R4. CORS & config per env** — **Difficulty 1/5**
  - **What it teaches:** Environment configs; enabling specific origins.
  - **Acceptance criteria:** Dev vs prod configs documented and working.

#### Bonus Features
- **B1. OpenAPI/Swagger docs** — **Difficulty 2/5**
  - **What it teaches:** API discoverability and schemas.
  - **Acceptance criteria:** Docs served at `/docs`.

- **B2. API keys / simple auth** — **Difficulty 2/5**
  - **What it teaches:** Header parsing; secret rotation.
  - **Acceptance criteria:** Protected endpoint rejects missing/invalid keys.

- **B3. Rate limit** — **Difficulty 2/5**
  - **What it teaches:** Client‑side throttling via IP/key.
  - **Acceptance criteria:** Exceeding limits returns 429 with `Retry-After`.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 17) Microblog Skeleton
**What you’re building:** A simple blog with posts and templates.
**Core skills:** Flask, Jinja2, sessions, CSRF basics.

#### Required Features
- **R1. Post CRUD** — **Difficulty 2/5**
  - **What it teaches:** Forms, CSRF, template rendering.
  - **Acceptance criteria:** Create/edit/delete works; flash messages shown.

- **R2. Pagination** — **Difficulty 1/5**
  - **What it teaches:** OFFSET/LIMIT with nice UI.
  - **Acceptance criteria:** Page size consistent; next/prev links.

- **R3. Basic tests (pytest)** — **Difficulty 2/5**
  - **What it teaches:** App factory fixtures; client tests.
  - **Acceptance criteria:** CRUD covered; CSRF negative test.

- **R4. Sessions & auth stub** — **Difficulty 2/5**
  - **What it teaches:** Login/out flow (even if single user); secure cookies.
  - **Acceptance criteria:** Auth‑only routes guarded.

#### Bonus Features
- **B1. User accounts & login** — **Difficulty 3/5**
  - **What it teaches:** Password hashing; user table; decorators.
  - **Acceptance criteria:** Per‑user posts and ownership checks.

- **B2. Markdown posts** — **Difficulty 2/5**
  - **What it teaches:** Rendering MD to HTML with sanitization.
  - **Acceptance criteria:** Safe HTML; code highlighting.

- **B3. Tags & archive pages** — **Difficulty 2/5**
  - **What it teaches:** Many‑to‑many tagging; URL design.
  - **Acceptance criteria:** Tag pages list posts; archive by month.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 18) Testing Workshop
**What you’re building:** Backfill tests for 3 earlier projects.
**Core skills:** pytest, fixtures, parametrization, coverage.

#### Required Features
- **R1. Coverage ≥ 80%** — **Difficulty 2/5**
  - **What it teaches:** Finding and testing blind spots.
  - **Acceptance criteria:** Coverage report meets target.

- **R2. Fixtures and parametrization** — **Difficulty 2/5**
  - **What it teaches:** Reusable setup; table‑driven cases.
  - **Acceptance criteria:** Duplication minimized; test data clear.

- **R3. Edge cases & error paths** — **Difficulty 2/5**
  - **What it teaches:** Negative testing; exception assertions.
  - **Acceptance criteria:** Invalid inputs verified for clean failures.

- **R4. CI‑friendly commands** — **Difficulty 1/5**
  - **What it teaches:** Deterministic, seed‑stable runs.
  - **Acceptance criteria:** Single command runs full suite reliably.

#### Bonus Features
- **B1. Property‑based tests (hypothesis)** — **Difficulty 3/5**
  - **What it teaches:** Generative testing; shrinking.
  - **Acceptance criteria:** At least 1 property per project.

- **B2. Mutation testing (mutmut)** — **Difficulty 3/5**
  - **What it teaches:** Test effectiveness measurement.
  - **Acceptance criteria:** Non‑trivial mutation score documented.

- **B3. Snapshot/golden tests** — **Difficulty 2/5**
  - **What it teaches:** Verifying complex outputs.
  - **Acceptance criteria:** Golden files checked into repo.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 19) Backup & Zip Script
**What you’re building:** Zip important folders on a schedule and rotate.
**Core skills:** `zipfile`, `pathlib`, cron docs, logging.

#### Required Features
- **R1. Include/exclude patterns** — **Difficulty 2/5**
  - **What it teaches:** Glob patterns; ignore files; safety.
  - **Acceptance criteria:** Patterns applied; dry‑run prints result set.

- **R2. Create archive** — **Difficulty 1/5**
  - **What it teaches:** Zipping folder trees; compression level.
  - **Acceptance criteria:** Resulting archive opens and matches files.

- **R3. Retention policy** — **Difficulty 2/5**
  - **What it teaches:** Keeping last N or last N days; deletion safety.
  - **Acceptance criteria:** Old archives pruned as configured.

- **R4. Checksums & logs** — **Difficulty 2/5**
  - **What it teaches:** `hashlib` and operation logs for audits.
  - **Acceptance criteria:** Checksums file emitted; run log saved.

#### Bonus Features
- **B1. Incremental backups** — **Difficulty 3/5**
  - **What it teaches:** mtime comparisons; changed files only.
  - **Acceptance criteria:** Deltas computed; full backup on schedule.

- **B2. Email report** — **Difficulty 2/5**
  - **What it teaches:** SMTP integration; success/failure summary.
  - **Acceptance criteria:** Report delivered on completion.

- **B3. Parallel compression** — **Difficulty 3/5**
  - **What it teaches:** Threading; CPU vs IO trade‑offs.
  - **Acceptance criteria:** Large backups run measurably faster.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 20) Task Scheduler
**What you’re building:** Run functions at intervals.
**Core skills:** `threading`/timers, datetime math, graceful shutdown.

#### Required Features
- **R1. Schedule registry** — **Difficulty 2/5**
  - **What it teaches:** Registering jobs with intervals; IDs.
  - **Acceptance criteria:** Add/list/remove jobs via CLI.

- **R2. Runner & timing** — **Difficulty 2/5**
  - **What it teaches:** Timer threads; drift correction.
  - **Acceptance criteria:** Jobs fire at expected times (within tolerance).

- **R3. Persist schedule** — **Difficulty 1/5**
  - **What it teaches:** Saving jobs to JSON; reload on start.
  - **Acceptance criteria:** Survives restarts with same plan.

- **R4. Pause/resume & shutdown** — **Difficulty 2/5**
  - **What it teaches:** Signals and state.
  - **Acceptance criteria:** Ctrl‑C causes graceful stop after running jobs.

#### Bonus Features
- **B1. Crontab parser** — **Difficulty 3/5**
  - **What it teaches:** Cron expressions and next‑run calculation.
  - **Acceptance criteria:** Cron strings map to correct runtimes.

- **B2. Jitter** — **Difficulty 1/5**
  - **What it teaches:** Spreading load to avoid thundering herds.
  - **Acceptance criteria:** Optional jitter applies +/- seconds.

- **B3. Missfire policies** — **Difficulty 2/5**
  - **What it teaches:** What to do if job is late (skip vs catch up).
  - **Acceptance criteria:** Policy configurable and enforced.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 21) RSS Reader (CLI)
**What you’re building:** Fetch feeds, display new items, mark as read.
**Core skills:** `feedparser`, persistence, humanized times.

#### Required Features
- **R1. Subscribe/unsubscribe** — **Difficulty 2/5**
  - **What it teaches:** Managing a feed list and validating URLs.
  - **Acceptance criteria:** Subscriptions persist; invalid feeds rejected.

- **R2. Fetch & store entries** — **Difficulty 2/5**
  - **What it teaches:** Deduplication by GUID/URL; per‑feed state.
  - **Acceptance criteria:** New vs read items tracked correctly.

- **R3. Filters and search** — **Difficulty 2/5**
  - **What it teaches:** Tag/keyword filters; date filters.
  - **Acceptance criteria:** Commands show subsets as requested.

- **R4. Notifications on new** — **Difficulty 1/5**
  - **What it teaches:** Simple polling and notifying.
  - **Acceptance criteria:** New arrivals trigger a desktop/console alert.

#### Bonus Features
- **B1. HTML digest export** — **Difficulty 2/5**
  - **What it teaches:** Templating an offline digest page.
  - **Acceptance criteria:** A dated HTML report with links rendered.

- **B2. OPML import/export** — **Difficulty 2/5**
  - **What it teaches:** Interoperability with other readers.
  - **Acceptance criteria:** Round‑trip keeps titles and URLs.

- **B3. Offline mode** — **Difficulty 2/5**
  - **What it teaches:** Caching content; read later.
  - **Acceptance criteria:** Cached items viewable without network.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 22) QR Code Generator
**What you’re building:** Create QR codes from text/URLs and save PNGs.
**Core skills:** `qrcode`/Pillow, file naming, CLI flags.

#### Required Features
- **R1. Encode text/URL** — **Difficulty 1/5**
  - **What it teaches:** Basic QR generation; PIL image saving.
  - **Acceptance criteria:** Output PNG opens and scans.

- **R2. CLI flags** — **Difficulty 1/5**
  - **What it teaches:** Size, border, output path.
  - **Acceptance criteria:** `--size` and `--out` respected.

- **R3. Batch from CSV** — **Difficulty 2/5**
  - **What it teaches:** Reading rows and generating multiple files.
  - **Acceptance criteria:** Filenames derived from a CSV column.

- **R4. Logo overlay** — **Difficulty 2/5**
  - **What it teaches:** Compositing and error correction considerations.
  - **Acceptance criteria:** Overlaid logo doesn’t break scanning.

#### Bonus Features
- **B1. Decode QR** — **Difficulty 2/5**
  - **What it teaches:** Reverse path via `zbarlight`/OpenCV.
  - **Acceptance criteria:** Decodes sample images to text.

- **B2. Error correction levels** — **Difficulty 1/5**
  - **What it teaches:** L/M/Q/H trade‑offs.
  - **Acceptance criteria:** Level selectable and documented.

- **B3. SVG output** — **Difficulty 2/5**
  - **What it teaches:** Vector export and scaling.
  - **Acceptance criteria:** SVG renders correctly in browsers.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 23) Excel Report Builder
**What you’re building:** Read CSV and write a nicely formatted XLSX.
**Core skills:** pandas, openpyxl/xlsxwriter, formatting.

#### Required Features
- **R1. Load CSV → DataFrame** — **Difficulty 1/5**
  - **What it teaches:** Data import and dtype checks.
  - **Acceptance criteria:** Bad CSV yields a clear error report.

- **R2. Formatting & styles** — **Difficulty 2/5**
  - **What it teaches:** Column widths, number formats, header styles.
  - **Acceptance criteria:** Headers bold; numeric formats applied.

- **R3. Conditional formatting** — **Difficulty 2/5**
  - **What it teaches:** Highlighting based on rules.
  - **Acceptance criteria:** Cells meeting conditions are visually distinct.

- **R4. Chart** — **Difficulty 2/5**
  - **What it teaches:** Building a simple chart sheet.
  - **Acceptance criteria:** Chart references correct ranges and titles.

#### Bonus Features
- **B1. Template workbook** — **Difficulty 2/5**
  - **What it teaches:** Reusing styles and layouts.
  - **Acceptance criteria:** Output uses a base template file.

- **B2. Pivot table** — **Difficulty 3/5**
  - **What it teaches:** Summaries by categories.
  - **Acceptance criteria:** Pivot sheet generated with groupings.

- **B3. Multi‑sheet report** — **Difficulty 2/5**
  - **What it teaches:** Splitting datasets by key.
  - **Acceptance criteria:** One sheet per group key.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 24) Image Thumbnailer
**What you’re building:** Create thumbnails and preserve aspect ratio.
**Core skills:** Pillow resize, `pathlib` glob, error handling.

#### Required Features
- **R1. Discover images** — **Difficulty 1/5**
  - **What it teaches:** Glob patterns and extension filters.
  - **Acceptance criteria:** Prints count and sample of discovered files.

- **R2. Resize with aspect** — **Difficulty 2/5**
  - **What it teaches:** Thumbnail vs resize; fit vs fill.
  - **Acceptance criteria:** Output within max bounds; no distortion.

- **R3. Quality settings** — **Difficulty 1/5**
  - **What it teaches:** JPEG quality; PNG optimization.
  - **Acceptance criteria:** Quality flag affects output size visibly.

- **R4. Skip already processed** — **Difficulty 2/5**
  - **What it teaches:** Idempotency via hash/mtime markers.
  - **Acceptance criteria:** Re‑run avoids duplicate work.

#### Bonus Features
- **B1. ThreadPool concurrency** — **Difficulty 3/5**
  - **What it teaches:** IO parallelism and CPU limits.
  - **Acceptance criteria:** Large sets process faster with same results.

- **B2. Respect EXIF orientation** — **Difficulty 2/5**
  - **What it teaches:** Correcting rotation based on metadata.
  - **Acceptance criteria:** Portrait/landscape render correctly.

- **B3. Progressive JPEGs** — **Difficulty 2/5**
  - **What it teaches:** Web‑friendly image encodings.
  - **Acceptance criteria:** Progressive flag produces incremental load.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 25) CLI Address Autocomplete
**What you’re building:** Local fuzzy search over addresses using a trigram index.
**Core skills:** text normalization, sets, lightweight indexing.

#### Required Features
- **R1. Normalization** — **Difficulty 2/5**
  - **What it teaches:** Lowercasing, stripping punctuation, diacritics removal.
  - **Acceptance criteria:** "São Paulo" and "Sao Paulo" normalize identically.

- **R2. Trigram index build** — **Difficulty 3/5**
  - **What it teaches:** N‑gram tokenization; posting lists; memory trade‑offs.
  - **Acceptance criteria:** Index built once; persistent on disk (compact format).

- **R3. Ranking & pagination** — **Difficulty 2/5**
  - **What it teaches:** Scoring by trigram overlap; tie‑breakers; paging.
  - **Acceptance criteria:** Top‑k results stable; `--page` and `--limit` work.

- **R4. CLI query path** — **Difficulty 1/5**
  - **What it teaches:** `argparse` UX; quoting; fast path for exact matches.
  - **Acceptance criteria:** Exact match returns position 1; invalid queries explained.

#### Bonus Features
- **B1. Incremental indexing** — **Difficulty 3/5**
  - **What it teaches:** Append‑only segments and merges.
  - **Acceptance criteria:** New addresses added without full rebuild.

- **B2. Memory‑mapped index** — **Difficulty 3/5**
  - **What it teaches:** `mmap` for fast reads; zero‑copy slices.
  - **Acceptance criteria:** Start‑up time reduced vs in‑RAM index.

- **B3. Interactive TUI** — **Difficulty 2/5**
  - **What it teaches:** Type‑ahead with `prompt_toolkit`/`textual`.
  - **Acceptance criteria:** Live filtering as you type.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

``` 

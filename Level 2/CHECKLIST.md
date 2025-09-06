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

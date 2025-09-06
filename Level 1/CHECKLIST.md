# Level 1 — Beginner (Novice)

Foundations of Python: syntax, variables, control flow, functions, collections, basic I/O. Projects are short and focus on building comfort with the language and standard library.

## Checklist

- [ ] 1. Hello World & Super-Calculator
  - What you build: Print text, read user input, perform + − × ÷ and show results.
  - Skills: print(), input(), int/float, operators, functions, f-strings.
  - Milestones: Handle invalid input; support order of operations; add unit tests with assert.
  - Stretch goals: Add exponent, modulo, and memory recall (M+, M-).

- [ ] 2. Guess the Number
  - What you build: Computer picks a number; user guesses until correct with hints.
  - Skills: random, loops, conditionals, counters, replay loop.
  - Milestones: Limit attempts; show attempts used; track best score in a file.
  - Stretch goals: Binary-search hint mode (higher/lower guidance quality).

- [ ] 3. Temperature Converter
  - What you build: Convert Celsius↔Fahrenheit↔Kelvin with simple menu.
  - Skills: float math, branching, functions, docstrings.
  - Milestones: Validate ranges; round sensibly; support batch conversions from a file.
  - Stretch goals: Graph conversion table with text grid.

- [ ] 4. Unit Converter
  - What you build: Length/weight conversions (m↔ft, kg↔lb) with a tiny DSL-like menu.
  - Skills: dict lookups, mapping tables, functions, error messages.
  - Milestones: Centralize conversions; add tests for edge cases; persist last selection.
  - Stretch goals: Support chaining (m→ft→in) and custom factors file.

- [ ] 5. Rock–Paper–Scissors
  - What you build: Play against the computer with running score.
  - Skills: random choice, enums via constants, loops, input parsing.
  - Milestones: Best‑of‑N series; detect invalid input; pretty scoreboard.
  - Stretch goals: Add Lizard/Spock variant and simple AI (counter last move).

- [ ] 6. Mad Libs Generator
  - What you build: Prompt for words and inject into a story template.
  - Skills: string formatting, lists, files, basic templates.
  - Milestones: Load multiple templates from folder; save completed stories.
  - Stretch goals: Randomly select template and required parts of speech.

- [ ] 7. Palindrome & Anagram Checker
  - What you build: Check if text is a palindrome; detect anagrams between two phrases.
  - Skills: string methods, normalization, collections.Counter.
  - Milestones: Ignore punctuation/spacing; add unit tests.
  - Stretch goals: CLI mode with argparse and batch file input.

- [ ] 8. Alarm & Countdown Timer
  - What you build: Set an alarm or countdown that rings at time.
  - Skills: time, datetime, while-loops, cross-platform beeps.
  - Milestones: Parse 'HH:MM' and '10m' formats; cancel option.
  - Stretch goals: Multiple alarms stored in JSON.

- [ ] 9. To‑Do List (Text File)
  - What you build: Minimal task list saved to disk with add/list/complete/delete.
  - Skills: file I/O, lists, indexes, simple persistence.
  - Milestones: Unique IDs; timestamps; confirm destructive actions.
  - Stretch goals: Priorities and due dates; sort by priority.

- [ ] 10. Address Book (CSV)
  - What you build: Store contacts in CSV; search by name or email.
  - Skills: csv module, dict rows, basic search.
  - Milestones: Import/export; validate email; avoid duplicates.
  - Stretch goals: Support vCard export.

- [ ] 11. Word Count (wc)
  - What you build: Count lines/words/chars across files like Unix wc.
  - Skills: argparse, pathlib, reading files, aggregation.
  - Milestones: Glob patterns; handle large files; unit tests.
  - Stretch goals: Top‑N most frequent words.

- [ ] 12. Dice Roller Simulator
  - What you build: Roll NdM dice (e.g., 3d6) and show distribution.
  - Skills: parsing input, random, list comprehension.
  - Milestones: Roll many times; compute mean/variance.
  - Stretch goals: ASCII histogram chart.

- [ ] 13. Stopwatch
  - What you build: Start/stop/lap timing tool in the console.
  - Skills: time/perf_counter, state machine, formatting.
  - Milestones: Lap list; export to CSV; keyboard shortcuts.
  - Stretch goals: Save sessions and summarize totals.

- [ ] 14. Multiplication Table Generator
  - What you build: Print 1–12 multiplication tables (or chosen range).
  - Skills: nested loops, formatting, functions.
  - Milestones: Column alignment; save to text/CSV.
  - Stretch goals: Quiz mode with scoring.

- [ ] 15. Password Generator
  - What you build: Create random passwords meeting length and class rules.
  - Skills: random, string constants, validation.
  - Milestones: Avoid ambiguous chars; ensure class coverage.
  - Stretch goals: Passphrase mode using word list.

- [ ] 16. Hangman (ASCII)
  - What you build: Classic hangman game in terminal with a word list.
  - Skills: sets, state updates, reading resources.
  - Milestones: Reveal progress; track wrong guesses; replay.
  - Stretch goals: Difficulty levels and hints.

- [ ] 17. Quiz App from JSON
  - What you build: Ask multiple‑choice questions loaded from JSON.
  - Skills: json, shuffling, scoring, input validation.
  - Milestones: Randomize answers; categories; percentage score.
  - Stretch goals: Timed questions and leader board file.

- [ ] 18. String Templater for Emails
  - What you build: Fill placeholders in templates (e.g., {name}) from CSV.
  - Skills: format maps, csv DictReader, file writing.
  - Milestones: Preview mode; output one file per row.
  - Stretch goals: Jinja2 templating for loops/conditions.

- [ ] 19. Countdown Pomodoro
  - What you build: Pomodoro timer with work/break cycles in terminal.
  - Skills: loops, sleep, simple state machine.
  - Milestones: Configurable durations; session summary.
  - Stretch goals: Sound notifications and daily log CSV.

- [ ] 20. Tip & Bill Splitter
  - What you build: Compute tip %, tax, and split among diners.
  - Skills: float math, rounding, input sanitization.
  - Milestones: Handle uneven splits; service fee option.
  - Stretch goals: Export receipt as text.

- [ ] 21. BMI & Calorie Calculator
  - What you build: Compute BMI and estimate daily calories.
  - Skills: formulas, constants, branching.
  - Milestones: Metric/imperial; sensible validation.
  - Stretch goals: Save personal profiles in JSON.

- [ ] 22. Simple Interest & Compound Calculator
  - What you build: Compute interest over time; show yearly table.
  - Skills: loops, math, formatting tables.
  - Milestones: Compound intervals; export CSV.
  - Stretch goals: ASCII chart of growth.

- [ ] 23. Calendar Viewer
  - What you build: Show month/year calendars and upcoming dates.
  - Skills: calendar module, datetime, CLI options.
  - Milestones: Highlight today; jump to next payday/Friday.
  - Stretch goals: iCal export for birthdays.

- [ ] 24. Flashcards (CLI)
  - What you build: Flip Q/A cards from CSV; spaced repetition lite.
  - Skills: csv, randomization, simple scheduling.
  - Milestones: Track correctness; promote/demote difficulty.
  - Stretch goals: Leitner box algorithm.

- [ ] 25. File Organizer
  - What you build: Move files into folders by extension (Pictures, Docs…).
  - Skills: pathlib, os, shutil, safety checks.
  - Milestones: Dry‑run preview; handle name collisions.
  - Stretch goals: Rules via YAML config.

- [ ] 26. Text Adventure Mini‑Game
  - What you build: Navigate rooms with inventory and simple combat.
  - Skills: dicts as graphs, loops, functions.
  - Milestones: Map loader from JSON; save/load game.
  - Stretch goals: Random encounters and items.

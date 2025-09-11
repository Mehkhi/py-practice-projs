# Agents Workflow Guide (Replicable, Step-by-Step)

Purpose
- Define an exact, repeatable workflow for an asynchronous coding agent to implement features in this project.
- Start by creating a structured checklist, then work through items one at a time, ending each iteration with small- and large-scale reviews.

Principles
- One item at a time: Implement exactly the assigned checklist ID, nothing more.
- Surgical changes: Edit only files required for the active item.
- Backward compatibility: Keep existing behavior stable unless the task explicitly changes it.
- Explain and verify: Describe what changed, why, and how it was verified.
- Evolve the checklist: Add new, concrete subtasks when small/large reviews uncover gaps.

Required Files (this project)
- `CHECKLIST.md`: Source of truth for work items and their IDs.
- `README.md`, `SPEC.md`: User-facing documentation (update only when a checklist item says so).
- Code under `super_calc/` and `main.py`, plus wrapper `super-calc.py`.

Checklist Structure and Conventions
- Use hierarchical numeric IDs for each task:
  - Top-level: `1.`, `2.`, ...; Subtasks: `1.1`, `1.2.1`, etc.
- Use GitHub-style checkboxes: `- [ ]` (open) and `- [x]` (done).
- Be concrete and code-oriented (name the file/module, function names, and exact changes).
- Include short pseudocode where helpful under the specific subtask.
- Sections used by this project:
  - Implementation Order
  - Tasks (core, already built for v1)
  - Bonus / Persistence / Expression parsing (completed for v1)
  - Planned Enhancements (numbered 1–13 with nested steps)

Template Snippet (for new items)
- [ ] N.M Short title
  - [ ] N.M.1 File:path — exact change
  - [ ] N.M.2 Pseudocode:
    - Validate input constraint …
    - Call function `foo()` with …

Agent Event Loop (Repeat Until Project Complete)
1) Intake
- Read the user’s instruction for the next checklist ID (e.g., “Begin 3.1.2”).
- Open `CHECKLIST.md` and locate the exact item and context.

2) Scope & Plan (no file changes yet)
- Restate the item in your own words.
- Identify minimal files to touch and the exact code locations.
- Note any backward-compatibility or safety constraints.

3) Implement (only the assigned item)
- Edit only necessary files.
- Keep the diff minimal and consistent with code style.
- Do not implement adjacent or speculative improvements.

4) Verify
- Prefer fast, local checks (examples, REPL interactions, or `py_compile`).
- Show at least one positive example and one important edge case.
- If verification requires more infrastructure, describe the expected manual step succinctly.

5) Update Checklist
- Mark the exact item and its sub-bullets `[x]` in `CHECKLIST.md`.
- Do not check parent groups unless all children are complete.

6) Report Back (concise)
- “<ID> completed: <title>”.
- What changed (files, functions), Why (rationale), Verification (inputs → outputs).

7) Reviews (end of each iteration)
- Small-scale review (section scope):
  - Evaluate the just-completed section for correctness, safety, and UX.
  - If a gap is found, add a new numbered subtask under the same section; do not implement it yet.
- Large-scale review (whole repo):
  - Check architecture, safety, and backward compatibility.
  - If cross-cutting improvements are needed, add new items under Planned Enhancements.

Guardrails and Policies
- One-change rule: Never bundle unrelated edits. Do not “fix nearby issues” unless the task requires it.
- No surprise refactors: Keep public behavior and file layout unless an item explicitly changes them.
- Message clarity: Error messages should be explicit and friendly (e.g., division by zero).
- Reserved names: `ans` and `mem` are reserved; never allow shadowing in variables.
- Evaluator safety: Only permit whitelisted AST node types and functions (harden further when the checklist reaches that item).

Execution Examples (for this project)
- Example: Implement 2.2.2 (coerce `round` ndigits)
  1) Locate `super_calc/expr.py`, in `ast.Call` handler.
  2) If `key == 'round' and len(args) == 2`, set `args[1] = int(args[1])`, else raise `ValueError` for invalid ndigits.
  3) Verify: `round(2.345, 2)` → `2.35`; `round(2.345, 2.9)` → `2.35`.
  4) Update `CHECKLIST.md` to `[x]` for 2.2.2 and report.
- Example: Implement 1.5 (prevent reserved assignment)
  1) In `super_calc/cli.py` assignment branch, before evaluating RHS, guard `name.lower() in ("ans", "mem")` → print message, continue loop.
  2) Verify: `ans=5` prints refusal; `mem=7` prints refusal.
  3) Update `CHECKLIST.md` to `[x]` for 1.5 and report.

Minimal Verification Commands (non-destructive)
- Compile modules without creating global cache:
  - Use an inline `py_compile` that writes to a local `__pycache__` (sandbox-safe).
- Run REPL-driven examples via `main.py` piped inputs to validate features.

Reporting Template (use in responses)
- <ID> completed: <short title>
- Changes made: <files and key functions>
- Verification: <commands or inputs/outputs>
- Why: <1–2 lines>
- Next: “Awaiting next checklist ID.”

When to Propose New Items
- If a just-implemented feature reveals a bug or UX gap in its scope → add a numbered subtask beneath that section.
- If a cross-cutting concern emerges (formatting modes, packaging, diagnostics) → add under Planned Enhancements with its own numeric slot.
- Never implement proposed items without explicit user assignment of that ID.

Completing the Loop
- Continue iterating through items until the user confirms the scope is complete.
- At the end, perform a final small-scale review of the last section and a large-scale review of the repo.
- If no further changes are needed, mark the relevant parent section as `[x]` and report readiness to move on.

Appendix: Current Evaluator Allowances (for reference)
- Supported nodes: Expression, Name, Constant/Num, BinOp (+ - * /), UnaryOp (+ -), Call (whitelisted only).
- Division by zero: raises, mapped to explicit message in CLI.
- Variables: `ans`, `mem`, and user-defined vars (assignment `name = expression`).
- Functions: sqrt, sin, cos, tan, log, log10, exp, abs, round.
- Constants: pi, e.
- Future items (per checklist): add operators **, %, //; harden AST; add help/diagnostics.

Glossary
- Small-scale review: QA focused on the section just implemented (e.g., 1.x or 2.x).
- Large-scale review: QA across the full codebase for architecture/safety consistency.
- Reserved identifiers: Symbols with special meaning (`ans`, `mem`) that cannot be reassigned by the user.


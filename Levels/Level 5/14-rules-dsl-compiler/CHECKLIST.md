# Checklist — 14-rules-dsl-compiler

## Implementation Order
- [ ] R1. Grammar & parser (3/5)
- [ ] R2. AST + type checking (3/5)
- [ ] R3. Codegen to Python AST (3/5)
- [ ] R4. Static analysis & lints (3/5)

## Tasks

- [ ] R1. Grammar & parser (3/5)
  - [ ] Invalid syntax yields line/column with caret.

- [ ] R2. AST + type checking (3/5)
  - [ ] Type errors reported before codegen.

- [ ] R3. Codegen to Python AST (3/5)
  - [ ] Generated code passes tests and adheres to safety sandbox.

- [ ] R4. Static analysis & lints (3/5)
  - [ ] Programs exceeding limits are rejected with guidance.

## Bonus

- [ ] B1. JIT with numba (numeric rules) (4/5)

- [ ] B2. REPL + debugger (3/5)

- [ ] B3. Source maps (3/5)

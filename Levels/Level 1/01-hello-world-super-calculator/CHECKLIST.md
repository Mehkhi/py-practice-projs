# Checklist — 01-hello-world-super-calculator

## Implementation Order
- [-] Command normalization and aliases (2/5)
- [x] Core operations: add, subtract, multiply, divide (1/5)
- [x] Division by zero handling (1/5)
- [x] Parse and validate numeric input (2/5)

## Tasks

- [-] Command normalization and aliases (2/5)
  - [ ] The same operation is invoked via multiple aliases (+, add, 1).
  - [ ] Invalid commands return `None` or a friendly message without crashing.

- [x] Core operations: add, subtract, multiply, divide (1/5)
  - [x] All four operations compute correct results for sample inputs.
  - [x] Output formatting is consistent and readable (e.g., fixed precision).

- [x] Division by zero handling (1/5)
  - [x] When denominator == 0, the program shows a clear message and does not crash.
  - [x] Unit tests cover zero and near‑zero denominators.

- [x] Parse and validate numeric input (2/5)
  - [x] Non‑numeric input does not crash the program and re‑prompts the user.
  - [x] Empty/whitespace input is rejected.
  - [x] Unit tests cover valid/invalid cases.

## Bonus

- [ ] Memory features (M+, M−, MR) and session history (3/5)
  - [ ] Users can add to memory, subtract from memory, and recall memory.
  - [ ] Optionally, undo/redo the last operation and print history.

- [ ] Expression parsing with precedence and parentheses (4/5)
  - [ ] `2+3*4` evaluates to `14`, `(2+3)*4` evaluates to `20`.
  - [ ] Malformed expressions produce friendly errors and do not crash.

- [ ] Configurable precision and modes via CLI flags (2/5)
  - [ ] `--precision N` formats results accordingly.
  - [ ] All required features continue to work with flags applied.

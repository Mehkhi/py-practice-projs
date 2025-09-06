# Checklist — 22-simple-interest-compound-calculator

## Implementation Order
- [ ] Command normalization and aliases (2/5)
- [ ] Core operations: add, subtract, multiply, divide (1/5)
- [ ] Division by zero handling (1/5)
- [ ] Parse and validate numeric input (2/5)

## Tasks

- [ ] Command normalization and aliases (2/5)
  - [ ] The same operation is invoked via multiple aliases (+, add, 1).
  - [ ] Invalid commands return `None` or a friendly message without crashing.

- [ ] Core operations: add, subtract, multiply, divide (1/5)
  - [ ] All four operations compute correct results for sample inputs.
  - [ ] Output formatting is consistent and readable (e.g., fixed precision).

- [ ] Division by zero handling (1/5)
  - [ ] When denominator == 0, the program shows a clear message and does not crash.
  - [ ] Unit tests cover zero and near‑zero denominators.

- [ ] Parse and validate numeric input (2/5)
  - [ ] Non‑numeric input does not crash the program and re‑prompts the user.
  - [ ] Empty/whitespace input is rejected.
  - [ ] Unit tests cover valid/invalid cases.

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

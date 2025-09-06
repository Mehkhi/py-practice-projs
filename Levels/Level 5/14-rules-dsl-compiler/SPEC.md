### 14) Rules DSL Compiler
**What you’re building:** Small DSL that compiles to safe Python AST.
**Core skills:** Parsing (lark/PLY), AST, codegen, safety.

#### Required Features
- **R1. Grammar & parser** — **Difficulty 3/5**
  - **What it teaches:**
    - Grammar design; error recovery; helpful messages.
  - **Acceptance criteria:**
    - Invalid syntax yields line/column with caret.

- **R2. AST + type checking** — **Difficulty 3/5**
  - **What it teaches:**
    - Static checks (types, arity, undefined names).
  - **Acceptance criteria:**
    - Type errors reported before codegen.

- **R3. Codegen to Python AST** — **Difficulty 3/5**
  - **What it teaches:**
    - AST transforms; sandboxing builtins; resource limits.
  - **Acceptance criteria:**
    - Generated code passes tests and adheres to safety sandbox.

- **R4. Static analysis & lints** — **Difficulty 3/5**
  - **What it teaches:**
    - Complexity limits; recursion depth; constant folding.
  - **Acceptance criteria:**
    - Programs exceeding limits are rejected with guidance.

#### Bonus Features
- **B1. JIT with numba (numeric rules)** — **Difficulty 4/5**
  - **Teaches:** JIT trade‑offs; performance vs flexibility.
  - **Acceptance:** Speedup demonstrated on numeric workloads.
- **B2. REPL + debugger** — **Difficulty 3/5**
  - **Teaches:** Interactive shell; stepping through AST.
  - **Acceptance:** Users can eval and inspect rule execution.
- **B3. Source maps** — **Difficulty 3/5**
  - **Teaches:** Map DSL nodes to Python lines.
  - **Acceptance:** Errors reference original DSL spans.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

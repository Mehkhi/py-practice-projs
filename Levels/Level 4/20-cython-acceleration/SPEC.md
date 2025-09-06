### 20) Cython Acceleration
**What you’re building:** Speed up a hot loop with a Cython extension.
**Core skills:** Profiling, Cython types, compilation toolchain.

#### Required Features
- **R1. Find hotspots** — **Difficulty 2/5**
  - **Teaches:** cProfile, line_profiler, flamegraphs.
  - **Acceptance:** Baseline timings captured; hotspots identified.
- **R2. Cythonize loop** — **Difficulty 3/5**
  - **Teaches:** `cdef` types, boundscheck/nonecheck controls.
  - **Acceptance:** ≥10x speedup or documented limits.
- **R3. Correctness tests** — **Difficulty 2/5**
  - **Teaches:** Numeric accuracy vs speed.
  - **Acceptance:** Results match Python version across cases.
- **R4. Build & package** — **Difficulty 2/5**
  - **Teaches:** Setup/pyproject config; wheels.
  - **Acceptance:** Wheel builds on CI; import works.

#### Bonus Features
- **B1. Compare PyPy/Numba** — **Difficulty 2/5**
  - **Teaches:** Alternative runtimes/JIT.
  - **Acceptance:** Report with pros/cons and timings.
- **B2. SIMD/vectorization** — **Difficulty 3/5**
  - **Teaches:** `numpy`/C‑level loops.
  - **Acceptance:** Additional speedup demonstrated.
- **B3. Multi‑threading (GIL release)** — **Difficulty 3/5**
  - **Teaches:** `with nogil`; thread pools.
  - **Acceptance:** Scales with cores on CPU‑bound work.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

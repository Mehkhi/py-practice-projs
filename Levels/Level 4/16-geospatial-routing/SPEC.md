### 16) Geospatial Routing
**What you’re building:** Shortest routes on a road graph.
**Core skills:** osmnx import, networkx, heuristics (A*), plotting.

#### Required Features
- **R1. Graph build from OSM** — **Difficulty 2/5**
  - **Teaches:** Bounding box import; cleaning; weights (distance/time).
  - **Acceptance:** Graph stats printed; edges weighted.
- **R2. Dijkstra/A*** — **Difficulty 3/5**
  - **Teaches:** Priority queues; heuristics; admissibility.
  - **Acceptance:** A* ≤ Dijkstra expansions; paths valid.
- **R3. Constraints (avoid tolls/elevation)** — **Difficulty 3/5**
  - **Teaches:** Multi‑criteria costs; penalties.
  - **Acceptance:** Options change chosen path; tests verify.
- **R4. Map rendering** — **Difficulty 2/5**
  - **Teaches:** Plot routes; export images/GeoJSON.
  - **Acceptance:** Output renders path clearly with legend.

#### Bonus Features
- **B1. Turn‑by‑turn instructions** — **Difficulty 3/5**
  - **Teaches:** Segment names, bearings, instruction synthesis.
  - **Acceptance:** Human‑readable steps exported.
- **B2. Isochrones** — **Difficulty 3/5**
  - **Teaches:** Reachable area computation by time.
  - **Acceptance:** Polygons generated for N minutes.
- **B3. Traffic simulation (static)** — **Difficulty 3/5**
  - **Teaches:** Time‑dependent weights.
  - **Acceptance:** Scenario report comparing routes.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

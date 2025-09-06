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

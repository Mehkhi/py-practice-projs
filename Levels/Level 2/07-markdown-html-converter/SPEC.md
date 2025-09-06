### 7) Markdown → HTML Converter
**What you’re building:** Convert `.md` files to HTML with a template.
**Core skills:** `markdown` lib, Jinja2, file walking.

#### Required Features
- **R1. Convert MD → HTML with template** — **Difficulty 2/5**
  - **What it teaches:** Pipeline design; separating content from presentation.
  - **Acceptance criteria:** Body renders inside a base template; CSS linked.

- **R2. Code highlighting** — **Difficulty 2/5**
  - **What it teaches:** Markdown extensions and Pygments.
  - **Acceptance criteria:** Code blocks highlighted; languages respected.

- **R3. Table of contents (TOC)** — **Difficulty 2/5**
  - **What it teaches:** Heading parsing and anchor generation.
  - **Acceptance criteria:** TOC links jump to sections.

- **R4. Directory walk** — **Difficulty 1/5**
  - **What it teaches:** Recursing folders; writing outputs next to inputs.
  - **Acceptance criteria:** All `.md` in tree processed; skip output dir.

#### Bonus Features
- **B1. Static site index** — **Difficulty 2/5**
  - **What it teaches:** Generating navigation pages from the file tree.
  - **Acceptance criteria:** Index lists pages with titles and links.

- **B2. Sitemap & RSS (if blog)** — **Difficulty 2/5**
  - **What it teaches:** XML generation; date metadata.
  - **Acceptance criteria:** Valid XML files emitted.

- **B3. Asset copying** — **Difficulty 1/5**
  - **What it teaches:** Copying referenced images/css.
  - **Acceptance criteria:** Relative links resolve in output.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

### 25) PyInstaller Distribution
**What you’re building:** Ship a CLI as a single binary/exe.
**Core skills:** pyinstaller, entry points, including assets, cross‑platform notes.

#### Required Features
- **R1. Working spec & entry point** — **Difficulty 2/5**
  - **What it teaches:** PyInstaller spec; console entry; hidden imports.
  - **Acceptance criteria:** Binary runs on target OS; usage matches `pip` version.

- **R2. Bundle assets** — **Difficulty 2/5**
  - **What it teaches:** Adding data files; relative paths inside bundle.
  - **Acceptance criteria:** Assets load at runtime on all platforms.

- **R3. Update strategy & version checks** — **Difficulty 2/5**
  - **What it teaches:** Version endpoints; prompting for updates.
  - **Acceptance criteria:** App detects newer version and informs user.

- **R4. Cross‑platform notes** — **Difficulty 1/5**
  - **What it teaches:** macOS Gatekeeper/entitlements; Windows AV flags.
  - **Acceptance criteria:** README documents platform‑specific steps.

#### Bonus Features
- **B1. Auto‑update check** — **Difficulty 3/5**
  - **Teaches:** Secure download and integrity checks.
  - **Acceptance:** App can download newer binary and replace safely (or instruct user).

- **B2. Code signing/notarization** — **Difficulty 3/5**
  - **Teaches:** Signing flows and tooling.
  - **Acceptance:** Signed binaries verified by OS tools.

- **B3. Compression & size tuning** — **Difficulty 2/5**
  - **Teaches:** UPX (where legal), excluding modules.
  - **Acceptance:** Binary size reduced with unchanged behavior.

#### Completion Checklist
See **Common Requirements for Project Completion**.

---

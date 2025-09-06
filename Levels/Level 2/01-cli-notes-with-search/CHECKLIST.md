# Checklist — 01-cli-notes-with-search

## Implementation Order
- [ ] R1. Create/List/View/Delete notes (JSON store) (2/5)
- [ ] R2. Tagging and tag filters (2/5)
- [ ] R3. Full‑text search (contains match) (2/5)
- [ ] R4. Timestamps + logging (1/5)

## Tasks

- [ ] R1. Create/List/View/Delete notes (JSON store) (2/5)
  - [ ] CRUD works with unique IDs; file remains valid JSON after interruptions.
  - [ ] `list` shows title + created time; `view` shows full note.

- [ ] R2. Tagging and tag filters (2/5)
  - [ ] `--tag` filters include correct notes; multiple tags behave as documented.

- [ ] R3. Full‑text search (contains match) (2/5)
  - [ ] `search "term"` returns ranked results; empty search is rejected.

- [ ] R4. Timestamps + logging (1/5)
  - [ ] Create/update times populate; basic INFO/ERROR logs written to file.

## Bonus

- [ ] B1. Fuzzy search (trigram / `difflib`) (3/5)

- [ ] B2. Encryption at rest (Fernet) (3/5)

- [ ] B3. Colored output (1/5)

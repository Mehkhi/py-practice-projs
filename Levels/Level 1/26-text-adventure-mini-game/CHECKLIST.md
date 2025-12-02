# Checklist — 26-text-adventure-mini-game

## Implementation Order

- [x] Inventory system (2/5)
- [x] Map as graph (rooms/exits) (2/5)
- [x] Save/load game (2/5)
- [x] Simple combat/encounters (2/5)

## Tasks

- [x] Inventory system (2/5)
  - [x] Pick up/drop/use items
  - [x] Sorting, filtering, and hotbar
  - [x] Equipment system (weapons, armor, accessories)

- [x] Map as graph (rooms/exits) (2/5)
  - [x] Consistent connectivity; dead ends documented
  - [x] 28+ interconnected maps with warp validation
  - [x] Map connectivity analysis tools

- [x] Save/load game (2/5)
  - [x] Resume from save reliably
  - [x] Multiple save slots with versioning
  - [x] Corruption recovery and migration

- [x] Simple combat/encounters (2/5)
  - [x] Win/lose conditions clear
  - [x] Multi-phase boss battles
  - [x] Learning AI and coordinated tactics
  - [x] Spare/mercy mechanics

## Bonus

- [x] Map loader from JSON (2/5)
  - [x] Level files define rooms/NPCs
  - [x] All content data-driven

- [x] Procedural events (3/5)
  - [x] Encounter rates configurable
  - [x] Day/night cycle and weather system

- [x] Scripting hooks (4/5)
  - [x] Room/item scripts extend gameplay
  - [x] Quest system with objectives and rewards
  - [x] Dialogue trees with branching choices

## Additional Completed Features

- [x] Party system with recruitment and formations
- [x] Skill trees with unlockable nodes
- [x] Crafting system with recipe discovery
- [x] 40+ achievements with popup notifications
- [x] Bestiary tracking enemy encounters
- [x] Multiple endings based on player choices
- [x] New Game+ with progression carryover
- [x] Accessibility options (colorblind, font scaling)
- [x] 762 unit tests passing

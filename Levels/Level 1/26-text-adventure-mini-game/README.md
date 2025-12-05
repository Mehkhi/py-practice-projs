# JRPG Engine - Text Adventure Mini-Game

A full-featured JRPG engine with top-down pixel overworld, turn-based combat, and data-driven world system. Built with Python and pygame.

## What It Does

This game features:
- **Top-down overworld exploration** - Navigate 28+ tile-based maps with arrow keys or WASD
- **Turn-based combat** - Strategic battles with Attack, Skill, Item, Guard, Talk, Memory, and Flee options
- **Stats and status effects** - HP/SP system with 15+ status effects (poison, bleed, burn, frozen, etc.)
- **Party system** - Recruit companions with unique roles, skills, and formation positions
- **Equipment system** - Weapons, armor, and accessories with stat modifiers
- **Skill trees** - Unlock nodes for stat bonuses and new abilities
- **Crafting system** - Discover recipes and craft items from gathered materials
- **Quest system** - Main story quests and 20+ side quests with objectives and rewards
- **Multiple endings** - Three endings based on player choices and quest completion
- **Achievements** - 40+ achievements tracking milestones, stats, and exploration
- **Bestiary** - Track encountered enemies with discovery levels
- **Day/night cycle** - Time-based lighting and events
- **Weather system** - Dynamic weather affecting gameplay
- **Advanced AI** - Multi-phase boss battles, learning AI, and coordinated enemy tactics
- **Accessibility** - Colorblind modes, font scaling, and customizable controls
- **Data-driven design** - All content defined in JSON for easy modding
- **Save/Load system** - Multiple save slots with versioning and corruption recovery
- **New Game+** - Carry progress into subsequent playthroughs

## Installation

1. Make sure you have Python 3.7 or higher installed
2. Install pygame:
   ```bash
   pip install -r requirements.txt
   ```
3. Navigate to the project directory
4. Run the game:
   ```bash
   python text_adventure_mini_game.py
   ```

## Testing

Run all tests from the project root:
```bash
python run_tests.py
```

You can enable AI debug output and phase feedback during tests:
```bash
AI_DEBUG=1 AI_PHASE_FEEDBACK=1 python run_tests.py
```

## Controls



### Overworld
- **Arrow Keys** or **WASD** - Move player
- **Space** or **Enter** - Interact with objects/NPCs
- **ESC** - Open pause menu

### Pause Menu
- **Arrow Keys** - Navigate menu options
- **Enter** - Select option
- **ESC** - Resume game
- Options:
  - **Resume** - Return to overworld
  - **Save Game** - Save current progress to slot 1
  - **Quit** - Exit the game

### Battle
- **Arrow Keys** - Navigate menus
- **Enter** - Select option
- **ESC** - Cancel/Go back

## Gameplay

### Overworld
Explore interconnected maps in a top-down view. Walk into triggers to:
- Start battles
- Collect items
- Activate dialogue
- Warp to other maps

### Combat
Engage in turn-based battles with:
- **Attack** - Basic physical attack
- **Skill** - Use SP-consuming abilities (Fire Bolt, Heal, Poison Strike)
- **Item** - Use consumables from inventory
- **Guard** - Increase defense for one turn
- **Talk** - Undertale-style pacifist option (increases enemy morale)
- **Flee** - Attempt to escape battle

### Tutorial Battle
The game starts with a tutorial battle that guides you through each combat function:
- Step-by-step instructions for each action type
- Practice using Attack, Skill, Item, Guard, and Talk
- Learn victory conditions (defeat or spare enemies)
- After completing the tutorial, you'll transition to the overworld

### World Maps
The game features four interconnected areas:
1. **Forest Path** - Starting area with tutorial battle
2. **Dark Cave** - Dangerous cave with tougher enemies
3. **Secret Garden** - Hidden area with magic crystal
4. **Treasure Chamber** - Final area with boss encounter

## Project Structure

```
26-text-adventure-mini-game/
├── text_adventure_mini_game.py    # Entry point
├── requirements.txt               # Dependencies (pygame)
├── docs/                          # Documentation (architecture, systems, economy, guides)
│   ├── ARCHITECTURE.md
│   ├── SYSTEMS.md
│   ├── CONTENT_GUIDE.md
│   ├── ECONOMY_ANALYSIS.md
│   ├── ECONOMY_BALANCE.md
│   ├── DIFFICULTY_CURVE_ANALYSIS.md
│   ├── CHECKLIST.md
│   ├── plan.md
│   └── AGENTS.md
├── core/                           # Domain model (no pygame)
│   ├── world.py                    # Maps, tiles, warps, triggers
│   ├── entities.py                 # Player, Enemy, NPC
│   ├── stats.py                    # Stats and status effects
│   ├── items.py                    # Items and inventory
│   ├── combat.py                   # Battle system
│   ├── dialogue.py                 # Dialogue trees
│   └── save_load.py                # Save/load system
├── engine/                         # Presentation layer (pygame)
│   ├── game.py                     # Main game loop
│   ├── scene.py                    # Scene management
│   ├── world_scene.py              # Overworld scene
│   ├── battle_scene.py             # Battle scene
│   ├── ui.py                       # UI widgets
│   └── assets.py                   # Asset loading
├── data/                           # JSON configuration
│   ├── config.json                 # Game settings
│   ├── maps/                       # Map definitions
│   ├── items.json                  # Item definitions
│   ├── skills.json                 # Skill definitions
│   ├── encounters.json             # Battle encounters
│   └── dialogue.json               # Dialogue trees
└── assets/                         # Art assets
    ├── tilesets/                   # Tile graphics
    └── sprites/                     # Character/enemy sprites
```

## Documentation

Additional documentation lives in `docs/`:
- `docs/ARCHITECTURE.md` - Scene stack, data flow, save format, AI profile structure
- `docs/SYSTEMS.md` - Domain-specific systems (fishing, arena, scheduling, tutorials)
- `docs/CONTENT_GUIDE.md` - Writing and tone guidelines
- `docs/ECONOMY_ANALYSIS.md` / `docs/ECONOMY_BALANCE.md` - Economy modeling and balance notes
- `docs/DIFFICULTY_CURVE_ANALYSIS.md` - Difficulty tuning guide
- `docs/CHECKLIST.md` and `docs/plan.md` - Project checklist and planning notes
- `docs/AGENTS.md` - Automation/agent usage guidelines

## Architecture

The project follows a clean separation of concerns:

- **core/** - Pure domain logic with no pygame dependencies. All game rules, stats, combat, and world logic live here.
- **engine/** - Pygame-dependent presentation layer. Handles rendering, input, and scene management.
- **data/** - JSON files define all game content (maps, items, encounters) for easy modification.

This architecture makes the core logic testable and engine-agnostic.

## Features

### Core Systems
- ✅ Top-down overworld with tile-based movement (28+ maps)
- ✅ Map transitions via warps with validation
- ✅ Turn-based combat with Attack, Skill, Item, Guard, Talk, Memory, Flee
- ✅ Stats system (HP, SP, Attack, Defense, Magic, Speed, Luck)
- ✅ 15+ status effects (poison, bleed, burn, frozen, stun, sleep, etc.)
- ✅ 45+ skills with elements and status infliction
- ✅ Items and inventory with sorting, filtering, and hotbar
- ✅ Equipment system (weapons, armor, accessories)
- ✅ Save/load system with versioning, migration, and corruption recovery

### Party & Progression
- ✅ Party system with recruitment, roles, and formation positions
- ✅ Skill trees with unlockable nodes and stat bonuses
- ✅ Crafting system with recipe discovery
- ✅ Bestiary tracking enemy encounters

### Quest & Story
- ✅ Quest system with prerequisites, objectives, and rewards
- ✅ Main quest chain and 20+ side quests
- ✅ Multiple endings based on player choices
- ✅ Dialogue scenes with branching choices
- ✅ New Game+ with carryover progression

### Combat AI
- ✅ Multi-phase boss battles with HP-threshold transitions
- ✅ Learning AI that adapts to player patterns
- ✅ Coordinated enemy tactics
- ✅ Spare/mercy mechanics (Undertale-style)

### Polish
- ✅ Title screen with animated background
- ✅ 40+ achievements with popup notifications
- ✅ Day/night cycle with lighting effects
- ✅ Weather system affecting gameplay
- ✅ Accessibility options (colorblind modes, font scaling)
- ✅ Customizable controls
- ✅ Procedural placeholder sprites (337+ sprites)
- ✅ Data-driven design (all content in JSON files)

## Requirements

- Python 3.7+
- pygame >= 2.0.0

## Asset Notes

### Deterministic Placeholders
Missing sprites generate colored pixel-art placeholder images using a deterministic hash (blake2b) of the sprite ID. This ensures consistent colors across game runs, test environments, and different machines.

### Duplicate Sprite ID Detection
The asset system warns when the same sprite ID is found in multiple directories. Only the first sprite found is used. To detect duplicates before runtime:
```bash
python tools/lint_sprites.py
```

## Modding & Replays

- **Mods**: Place mods in `mods/<mod_id>/mod.json`. Required fields: `id`, `name`, `version`. Optional: `description`, `author`, `entry_point`, and `data_overrides` mapping a data key (e.g., `"items"`, `"encounters"`, `"classes"`, `"skills"`) to a relative JSON path inside the mod. Example:
  ```json
  {
    "id": "my_cool_mod",
    "name": "My Cool Mod",
    "version": "1.0.0",
    "description": "Adds new items and encounters",
    "data_overrides": {
      "items": "data/items_override.json",
      "encounters": "data/encounters_override.json"
    }
  }
  ```
  Mods are merged at load time; dicts are merged recursively, lists are concatenated, scalars overwrite.
- **Replay recording**: Enable with config `replay_record: true` or env `REPLAY_RECORD=1`. Optional `REPLAY_OUTPUT=/path/to/file.json` to choose destination; otherwise replays save under `replays/replay_<timestamp>.json`. Events capture logical actions after input translation (keyboard/controller).
- **Quieter save validation**: Set `SAVE_VALIDATION_QUIET=1` to suppress non-critical recovery warnings when loading sandboxed or test saves.

## Learning Objectives

This project demonstrates:
- Game loop architecture
- Scene management patterns
- Model-view separation
- Data-driven game design
- Turn-based combat systems
- Asset management
- Save/load serialization

## License

This project is part of a Python learning curriculum and is available for educational use.

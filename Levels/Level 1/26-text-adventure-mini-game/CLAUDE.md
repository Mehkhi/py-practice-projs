# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a full-featured JRPG engine built with Python and pygame, featuring:
- Top-down overworld exploration with 28+ tile-based maps
- Turn-based combat with strategic options (Attack, Skill, Item, Guard, Talk, Memory, Flee)
- Party system with recruitment, skill trees, and formation positioning
- Data-driven design (all content defined in JSON files)
- Comprehensive save/load system with versioning and migration
- Advanced combat AI with multi-phase bosses and learning AI
- Quest system, achievements, crafting, and multiple endings

## Environment Setup

**CRITICAL:** Always use `.venv/bin/python3` for all Python commands. Dependencies (pygame, pytest) are installed in the virtual environment, NOT system Python.

## Common Commands

### Running the Game
```bash
.venv/bin/python3 text_adventure_mini_game.py
```

### Testing
```bash
# Run all tests
.venv/bin/python3 -m unittest discover -s . -p "test_*.py"

# Run single test file
.venv/bin/python3 -m unittest test_stats

# Run specific test
.venv/bin/python3 -m unittest test_stats.TestStats.test_is_dead_true

# With AI debug output
AI_DEBUG=1 AI_PHASE_FEEDBACK=1 .venv/bin/python3 -m unittest discover -s . -p "test_*.py"
```

### Alternative test runner (if available)
```bash
./run_tests.sh
```

## Architecture

### Core Principles

**Separation of Concerns:** The codebase maintains strict separation between game logic (`core/`) and presentation (`engine/`):

- **`core/`** - Pure domain logic with NO pygame dependencies
  - Contains all game rules, stats, combat, world logic
  - Fully testable without pygame
  - Can be reused with different UI frameworks
  - Never imports from `engine/`

- **`engine/`** - Pygame-dependent presentation layer
  - Handles rendering, input, scene management
  - Imports from `core/` but never vice versa
  - Scenes are stack-based (push/pop for menus, replace for transitions)

- **`data/`** - JSON configuration files
  - Maps, items, skills, encounters, quests, dialogue
  - All game content defined here for easy modding
  - Loaded by `core/data_loader.py` and `core/loaders/` modules

**Dependency Direction:** Engine depends on Core, Core NEVER depends on Engine.

### Key Architectural Patterns

#### Scene Stack System
The `SceneManager` (`engine/scene.py`) maintains a stack of scenes:
- `push(scene)` - Add scene on top (e.g., opening pause menu)
- `pop()` - Return to previous scene
- `replace(scene)` - Replace current scene (e.g., title → world transition)

Common scene transitions:
- New Game: `TitleScene → NameEntryScene → ClassSelectionScene → SubclassSelectionScene → TutorialBattleScene → WorldScene`
- Battle: `WorldScene → BattleScene (push) → WorldScene (pop on victory/defeat)`
- Menu: `WorldScene → PauseMenuScene (push) → submenu (push) → pop back through stack`

#### Data Flow
1. Core defines data structures (`Player`, `World`, `Quest`, etc.)
2. SceneManager holds core managers (`SaveManager`, `QuestManager`, etc.)
3. Engine scenes access via `self.manager.save_manager`, `self.manager.quest_manager`, etc.
4. Engine observes core state and renders accordingly

#### Event Bus
`SceneManager.event_bus` provides publish/subscribe for high-level game events:
- Engine scenes publish: `"enemy_killed"`, `"battle_won"`, `"map_entered"`, `"npc_talked"`, etc.
- `AchievementManager` subscribes to track progress
- Keeps achievement logic centralized and decoupled

### Core Module Organization

#### Main Modules
- `core/world.py` - World, Map, Tile, Warp, Trigger classes
- `core/entities.py` - Player, Enemy, NPC, Entity base class
- `core/stats.py` - Stats and status effects system
- `core/items.py` - Item definitions and inventory
- `core/combat/` - Battle system components
- `core/combat_modules/` - AI, learning AI, tactics, spell systems
- `core/quests.py` - Quest management and tracking
- `core/save_load.py` - Save/load with versioning and migration
- `core/achievements.py` - Achievement tracking system
- `core/loaders/` - Domain-specific JSON loaders (fishing, arena, puzzles, etc.)

#### Data Loaders
Domain-specific loading logic lives in `core/loaders/`:
- `bestiary_loader.py` - Bestiary metadata from encounters
- `fishing_loader.py` - Fish and fishing spot definitions
- `puzzle_loader.py` - Dungeon puzzles
- `brain_teaser_loader.py` - Riddles and word scrambles
- `arena_loader.py` - Arena fighters and schedules
- `challenge_loader.py` - Challenge dungeons
- `secret_boss_loader.py` - Secret boss definitions
- `tutorial_loader.py` - Tutorial tips and help entries
- `npc_schedule_loader.py` - NPC schedules and behavior

### Engine Organization

#### Scene Types
- `engine/world_scene.py` - Overworld exploration
- `engine/battle_scene.py` - Turn-based combat
- `engine/title_scene.py` - Main menu
- `engine/*_scene.py` - Various specialized scenes (inventory, equipment, quest journal, etc.)
- `engine/base_menu_scene.py` - Base class for menu scenes

#### Rendering
- `engine/world/overworld_renderer.py` - Tile and entity rendering
- `engine/assets.py` - Asset loading (sprites, fonts, audio)
- `engine/ui/` - UI components (panels, buttons, tooltips)

#### Combat UI
- `engine/battle/` - Battle-specific UI components
- `engine/battle_scene.py` - Main battle scene coordinator

## Code Style Guidelines

### Imports
Order: stdlib → third-party (pygame) → local
```python
import os
from typing import Optional, List, Dict

import pygame

from core.entities import Player
from core.world import World
```

Use `TYPE_CHECKING` for type-only imports:
```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.world import World
```

### Type Hints
Use type hints on ALL functions:
```python
def calculate_damage(attack: int, defense: int) -> int:
    return max(1, attack - defense)
```

Use typing module types: `Optional`, `List`, `Dict`, `Tuple`, `Any`

### Naming Conventions
- **Classes:** PascalCase (`BattleSystem`, `QuestManager`)
- **Functions/methods:** snake_case (`get_active_quests`, `start_battle`)
- **Private methods:** Leading underscore (`_internal_helper`)
- **Constants:** UPPER_SNAKE_CASE (`MAX_PARTY_SIZE`, `SAVE_FILE_VERSION`)

### Data Classes
Use `@dataclass` with `field(default_factory=...)` for mutable defaults:
```python
from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class Player:
    name: str
    inventory: Dict[str, int] = field(default_factory=dict)
    skills: List[str] = field(default_factory=list)
```

### Error Handling
Prefer graceful degradation with warnings:
```python
import logging
import os

if not os.path.exists(data_path):
    logging.warning(f"Data file not found: {data_path}, using defaults")
    return default_values

# Use getattr for optional attributes
value = getattr(obj, 'optional_field', default_value)
```

### Testing
Use unittest framework with descriptive names:
```python
class TestBattleSystem(unittest.TestCase):
    def test_damage_calculation_basic_hit(self):
        # Test basic damage formula
        pass

    def test_healing_restores_hp_correctly(self):
        # Test healing mechanics
        pass
```

## Save File System

### Format
Save files are JSON-based with versioning (current: v1):
```json
{
  "meta": {
    "version": 1,
    "timestamp": "2025-11-30T11:27:41.128505",
    "play_time_seconds": 452.914
  },
  "world": {
    "current_map_id": "string",
    "flags": { "gold": 1000, "tutorial_completed": true },
    "runtime_state": { "trigger_states": {}, "enemy_states": {} }
  },
  "player": { ... },
  "quests": { ... },
  "achievements": { ... }
}
```

### Migration
`SaveManager` handles automatic migration when loading older save versions. Check `core/save_load.py` for migration logic.

### Validation
Saves are validated before loading. Set `SAVE_VALIDATION_QUIET=1` to suppress non-critical warnings in tests.

## AI System

### AI Profiles
Enemy AI is defined in `data/encounters.json` using rule-based profiles:

**Simple AI:**
```json
{
  "ai_profile": {
    "behavior_type": "aggressive",
    "rules": [
      {
        "conditions": { "hp_percent": {"min": 0, "max": 100} },
        "action": { "type": "attack", "target_strategy": "random_enemy" },
        "weight": 10
      }
    ],
    "fallback_action": { "type": "attack", "target_strategy": "random_enemy" }
  }
}
```

**Multi-Phase AI:**
```json
{
  "ai_profile": {
    "phases": [
      { "name": "phase_1", "hp_threshold": 70, "rules": [...] },
      { "name": "phase_2", "hp_threshold": 40, "rules": [...] }
    ]
  }
}
```

### Behavior Types
- `aggressive` - Boosts attack/damage skills (×2 attacks, ×1.5 fire/physical)
- `defensive` - Boosts guard/self-targeting (×2 guard/self, ×1.5 holy)
- `support` - Boosts items/ally-targeting (×2 items/allies, ×1.5 ally skills)
- `balanced` - No modifications (default)

### Advanced AI Features
- **Learning AI** (`core/combat_modules/learning_ai.py`) - Adapts to player patterns
- **Coordinated Tactics** (`core/combat_modules/tactics.py`) - Multi-enemy coordination
- **Phase Transitions** - Bosses change behavior at HP thresholds

## Quest System

Quests are defined in `data/quests.json` with:
- Prerequisites (required quests, flags, items)
- Objectives (kill, collect, talk, explore)
- Rewards (gold, items, XP)
- Multiple endings based on completion

Track via `QuestManager` (accessed through `SceneManager.quest_manager`).

## Modding Support

### Mod Structure
Place mods in `mods/<mod_id>/mod.json`:
```json
{
  "id": "my_mod",
  "name": "My Mod",
  "version": "1.0.0",
  "description": "Adds new content",
  "data_overrides": {
    "items": "data/items_override.json",
    "encounters": "data/encounters_override.json"
  }
}
```

Mods are merged at load time:
- Dicts merge recursively
- Lists concatenate
- Scalars overwrite

### Replay Recording
Enable with `REPLAY_RECORD=1` or config `replay_record: true`. Optional `REPLAY_OUTPUT=/path/to/file.json`.

## Documentation Reference

- `docs/ARCHITECTURE.md` - Scene stack, data flow, save format, AI profiles (very detailed)
- `docs/SYSTEMS.md` - Domain systems (fishing, arena, scheduling, tutorials)
- `docs/CONTENT_GUIDE.md` - Writing and tone guidelines
- `docs/ECONOMY_ANALYSIS.md` / `docs/ECONOMY_BALANCE.md` - Economy balance
- `docs/DIFFICULTY_CURVE_ANALYSIS.md` - Difficulty tuning
- `docs/AGENTS.md` - Automation guidelines (duplicates info in this file)

## Important Implementation Notes

### Never Break Core/Engine Separation
- Core modules must NOT import from engine
- Core should remain pygame-agnostic
- All pygame dependencies belong in engine

### Scene Lifecycle
All scenes must implement:
- `__init__(manager)` - Receives SceneManager reference
- `handle_event(event)` - Process pygame events
- `update(dt)` - Update state (dt in seconds)
- `draw(surface)` - Render to surface

### Memory System
Player and party members have calculator-style memory:
- `memory_value` - Stored numeric value
- `memory_stat_type` - Type of stat stored
- Used in battle for advanced strategies

### Status Effects
15+ status effects in `core/stats.py`:
- Damage over time: poison, bleed, burn
- Control: frozen, stun, sleep, charm
- Stat modifiers: weaken, slow
- Special: regeneration, shield, invincible

### Formation System
Party members have formation positions affecting combat:
- `front` - Takes more damage, deals more damage
- `middle` - Balanced position
- `back` - Takes less damage, deals less damage

### Crafting System
- Recipe discovery through gameplay
- Ingredient collection and management
- Crafting XP and level progression
- Tracked via `Player.crafting_progress`

## Common Pitfalls

1. **Using system Python instead of venv** - Always use `.venv/bin/python3`
2. **Importing engine in core** - Breaks architecture, never do this
3. **Missing type hints** - All functions should have type hints
4. **Mutable default arguments** - Use `field(default_factory=...)` in dataclasses
5. **Not checking file existence** - Use `os.path.exists()` before file operations
6. **Forgetting scene manager reference** - Scenes need `manager` to access shared state
7. **Breaking save format** - Always maintain backward compatibility or add migration

## Testing Best Practices

- Test core logic independently of pygame
- Use unittest framework consistently
- Name tests descriptively: `test_<what>_<expected>`
- Mock pygame dependencies when testing engine code
- Use `AI_DEBUG=1` for combat AI test debugging

## Performance Considerations

- Sprites are procedurally generated (337+ sprites) for rapid prototyping
- Asset loading is lazy where possible
- Battle animations are frame-based, not time-based
- Map rendering uses sprite groups for efficiency
- Save files are compressed JSON for smaller file size

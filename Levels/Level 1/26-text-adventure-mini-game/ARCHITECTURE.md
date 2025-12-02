# Game Architecture Documentation

This document provides a comprehensive overview of the game's system architecture, covering scene transitions, data flow patterns, save file format, and AI profile structure.

For detailed documentation of advanced systems (fishing, gambling, arena, NPC schedules, and the tutorial/help system), see `SYSTEMS.md`.

## Table of Contents

1. [Scene Transition Flow](#scene-transition-flow)
2. [Data Flow Between Core and Engine](#data-flow-between-core-and-engine)
3. [Save File Format Specification](#save-file-format-specification)
4. [AI Profile Structure](#ai-profile-structure)
5. [Advanced Systems Reference](#advanced-systems-reference)

---

## Scene Transition Flow

The game uses a scene-based architecture managed by a `SceneManager` that maintains a stack of scenes. This allows for hierarchical navigation (e.g., pause menu over world scene) and clean transitions between game modes.

### Scene Stack Architecture

The `SceneManager` class (`engine/scene.py`) maintains a stack of `Scene` objects:

```python
class SceneManager:
    def __init__(
        self,
        initial_scene: Scene,
        save_manager: Optional[SaveManager] = None,
        save_slot: int = 1,
        quest_manager: Optional[QuestManager] = None,
        day_night_cycle: Optional[DayNightCycle] = None,
        weather_system: Optional[WeatherSystem] = None,
        achievement_manager: Optional[AchievementManager] = None,
        party_prototypes: Optional[Dict[str, Any]] = None,
        items_db: Optional[Dict[str, Item]] = None,
    ):
        self.stack: List[Scene] = [initial_scene]
        # Shared state accessible to all scenes
        self.save_manager = save_manager
        self.save_slot = save_slot
        self.quest_manager = quest_manager
        self.day_night_cycle = day_night_cycle
        self.weather_system = weather_system
        self.achievement_manager = achievement_manager
        self.party_prototypes = party_prototypes
        self.items_db = items_db
        self.quit_requested = False  # Set True to exit game loop
```

**Stack Operations:**
- `push(scene)`: Add a new scene on top of the stack (e.g., opening a menu over the world)
- `pop()`: Remove the current scene and return to the previous one
- `replace(scene)`: Replace the current scene (e.g., transitioning from title to world)
- `current()`: Get the active scene (top of stack)

### Scene Lifecycle

All scenes inherit from the abstract `Scene` base class and must implement:

- `__init__(manager)`: Initialize the scene, receives `SceneManager` reference
- `handle_event(event)`: Process pygame events (keyboard, mouse, etc.)
- `update(dt)`: Update scene state each frame (dt = delta time in seconds)
- `draw(surface)`: Render the scene to the pygame surface

The main game loop (`engine/game.py`) calls these methods on the current scene:

```python
# Main loop
current_scene = self.scene_manager.current()
current_scene.handle_event(event)  # For each event
current_scene.update(dt)           # Each frame
current_scene.draw(self.screen)    # Each frame
```

### Common Transition Patterns

#### New Game Flow
```
TitleScene → NameEntryScene → ClassSelectionScene → SubclassSelectionScene → TutorialBattleScene → WorldScene
```

1. **Title → Name Entry**: User selects "New Game", `SceneManager.replace()` called
2. **Name Entry → Class Selection**: Name confirmed, `SceneManager.replace()` called
3. **Class Selection → Subclass Selection**: Class selected, `SceneManager.replace()` called
4. **Subclass Selection → Tutorial**: Subclass selected, `SceneManager.replace()` called
5. **Tutorial → World**: Tutorial completed, `SceneManager.replace()` called

#### Continue Game Flow
```
TitleScene → SaveSlotScene (load mode) → WorldScene
```

The save slot scene loads game state and transitions directly to the world scene.

#### Battle Transitions
```
WorldScene → BattleScene → WorldScene (victory/defeat/escape)
WorldScene → BattleScene → EndingScene (final boss victory)
```

- **World → Battle**: Triggered by enemy encounters or map triggers
  - `WorldScene._start_battle()` creates `BattleScene` and calls `manager.push()`
  - Battle scene receives world state, player, and encounter data

- **Battle → World**: Normal battle completion
  - On victory/defeat/escape, `BattleScene` calls `manager.pop()` to return
  - World scene handles post-battle cleanup (marking enemies defeated, etc.)

- **Battle → Ending**: Final boss victory
  - `BattleScene._transition_to_ending()` determines ending and calls `manager.replace()`
  - Ending scene shows cinematic and credits

#### Menu Scene Transitions
```
WorldScene → PauseMenuScene → [InventoryScene | EquipmentScene | QuestJournalScene | ...]
```

- **World → Pause Menu**: ESC key pressed, `manager.push()` called
- **Pause Menu → Sub-menus**: Menu option selected, `manager.push()` called
- **Sub-menu → Pause Menu**: ESC key pressed, `manager.pop()` called
- **Pause Menu → World**: ESC key pressed, `manager.pop()` called

All menu scenes use the push/pop pattern to maintain the world scene underneath.

### Transition Manager

The `TransitionManager` class (`engine/ui.py`) provides fade effects for smooth scene transitions:

```python
class TransitionManager:
    def __init__(self, default_duration: float = 0.5):
        ...

    def fade_out(
        self,
        duration: Optional[float] = None,
        on_complete: Optional[Callable[[], None]] = None,
        color: Tuple[int, int, int] = (0, 0, 0)
    ) -> None:
        """Start fade out (screen goes to black)."""

    def fade_in(
        self,
        duration: Optional[float] = None,
        on_complete: Optional[Callable[[], None]] = None,
        color: Tuple[int, int, int] = (0, 0, 0)
    ) -> None:
        """Start fade in (screen reveals from black)."""

    def fade_out_in(
        self,
        on_switch: Optional[Callable[[], None]] = None,
        duration: Optional[float] = None,
        color: Tuple[int, int, int] = (0, 0, 0)
    ) -> None:
        """Fade out, call on_switch at midpoint, then fade in."""

    def is_active(self) -> bool:
        """Return whether a transition is currently in progress."""
```

Common usage:
- Warp transitions: Fade out → change map → fade in
- Battle transitions: Fade out → start battle → fade in
- Scene replacements: Fade out → replace scene → fade in

### Scene Manager Shared State and Event Bus

The `SceneManager` provides shared state accessible to all scenes:

- **`save_manager`**: Handles save/load operations
- **`save_slot`**: Current save slot number (1-based)
- **`quest_manager`**: Manages quest state and objectives
- **`day_night_cycle`**: Tracks time of day
- **`weather_system`**: Manages weather state
- **`achievement_manager`**: Tracks achievements
- **`party_prototypes`**: Party member definitions for recruitment
- **`items_db`**: Item database for equipment/inventory
- **`quit_requested`**: Boolean flag to signal game exit
- **`event_bus`**: Lightweight game‑wide event bus for high‑level domain events

The **event bus** (`engine/event_bus.py`) implements a simple publish/subscribe pattern:

```python
from engine.event_bus import EventBus

bus = EventBus()

def on_enemy_killed(payload: Dict[str, Any]) -> None:
    enemy_type = payload.get("enemy_type", "")
    ...

bus.subscribe("enemy_killed", on_enemy_killed)
bus.publish("enemy_killed", enemy_type="wolf", enemy_id="wolf_01")
```

`RpgGame` creates a single `EventBus` instance and passes it into `SceneManager` and `AchievementManager`. Engine scenes publish high‑level events like `"enemy_killed"`, `"battle_won"`, `"map_entered"`, `"npc_talked"`, `"gold_changed"`, and `"fish_caught"`, while `AchievementManager` subscribes to those events and routes them through a generic `_check_trigger` helper, keeping achievement logic centralized and decoupled from individual scenes.

Scenes access this state via `self.manager.save_manager`, `self.manager.quest_manager`, etc.

---

## Data Flow Between Core and Engine

The game follows a clean separation between game logic (`core/`) and presentation (`engine/`), with a unidirectional dependency: engine depends on core, not vice versa.

### Architecture Overview

**`core/` Directory**: Pure game logic, no pygame dependencies
- Data structures: `World`, `Player`, `Entity`, `Item`, `Quest`, etc.
- Game systems: `QuestManager`, `SaveManager`, `BattleSystem`, `CraftingSystem`, etc.
- Business logic: Combat rules, quest evaluation, save/load serialization

**`engine/` Directory**: Pygame-based UI and rendering
- Scenes: `WorldScene`, `BattleScene`, `TitleScene`, etc.
- UI components: Buttons, menus, tooltips, message boxes
- Rendering: Sprite drawing, text rendering, animations
- Input handling: Keyboard/mouse event processing

### Data Flow Patterns

#### 1. Core Defines, Engine Uses

Core modules define data structures that engine modules consume:

```python
# core/entities.py
class Player(Entity):
    def __init__(self, entity_id: str, name: str, ...):
        self.entity_id = entity_id
        self.name = name
        self.stats = Stats(...)
        # ...

# engine/world_scene.py
class WorldScene(Scene):
    def __init__(self, manager, world: World, player: Player, ...):
        self.world = world  # core/world.py
        self.player = player  # core/entities.py
        # ...
```

#### 2. Scene Manager Passes Core Managers

The `SceneManager` holds references to core managers and passes them to scenes:

```python
# engine/game.py
scene_manager = SceneManager(
    initial_scene=title_scene,
    save_manager=save_manager,        # core/save_load.py
    quest_manager=quest_manager,      # core/quests.py
    achievement_manager=achievement_manager,  # core/achievements.py
    # ...
)

# engine/world_scene.py
class WorldScene(Scene):
    def __init__(self, manager, ...):
        self.manager = manager
        # Access via manager
        self.manager.quest_manager.start_quest(...)
        self.manager.save_manager.serialize_state(...)
```

#### 3. Engine Observes Core State

Engine scenes observe core state and render accordingly:

```python
# engine/world_scene.py
def update(self, dt: float):
    # Core world state drives engine behavior
    if self.world.get_flag("tutorial_completed"):
        # Enable certain features

    # Core quest state drives UI
    active_quests = self.manager.quest_manager.get_active_quests()
    # Update quest UI indicators
```

### Key Data Flow Paths

#### World State Flow
```
core/world.py (World class)
    ↓ (passed to)
engine/world_scene.py (WorldScene)
    ↓ (renders)
engine/world/overworld_renderer.py (OverworldRenderer)
```

- `World` holds map data, flags, runtime state
- `WorldScene` coordinates rendering and input
- `OverworldRenderer` draws tiles, entities, UI

#### Combat System Flow
```
core/combat/__init__.py (BattleSystem)
    ↓ (used by)
engine/battle_scene.py (BattleScene)
    ↓ (renders)
UI components (HP bars, action menus, messages)
```

- `BattleSystem` handles turn order, action execution, AI
- `BattleScene` provides UI for player input and displays battle state
- Battle scene queries battle system for current state and sends commands

#### Quest System Flow
```
core/quests.py (QuestManager)
    ↓ (accessed via)
engine/world_scene.py (WorldScene)
engine/quest_journal_scene.py (QuestJournalScene)
engine/battle_scene.py (BattleScene)
```

- `QuestManager` tracks quest state, objectives, prerequisites
- Multiple engine scenes read/write quest state:
  - `WorldScene`: Updates objectives from triggers, NPCs, items
  - `QuestJournalScene`: Displays quest list and details
  - `BattleScene`: Updates kill objectives, awards quest rewards

#### Save/Load Flow
```
core/save_load.py (SaveManager)
    ↔ (serialize/deserialize)
engine/save_slot_scene.py (SaveSlotScene)
engine/world_scene.py (WorldScene - auto-save)
engine/ending_scene.py (EndingScene - NG+ save)
```

- `SaveManager` serializes core state (World, Player, QuestManager, etc.)
- Engine scenes trigger save/load operations
- Save system is versioned with migration support

### Data Loading Architecture (`core.loaders`)

Domain-specific JSON loading has been decomposed into focused loader modules under `core/loaders/` to reduce the size of `core/data_loader.py` and keep each system’s loading logic localized:

- `core/loaders/base.py` – shared helpers (reserved for future shared utilities; generic `load_json_file` currently lives in `core/data_loader.py`).
- `core/loaders/bestiary_loader.py` – `build_bestiary_metadata(encounters_data)` aggregates encounter JSON into normalized bestiary metadata used by `Bestiary`.
- `core/loaders/fishing_loader.py` – `load_fishing_data(path)` parses `data/fishing.json` into `Fish` and `FishingSpot` definitions used by `FishingSystem`.
- `core/loaders/puzzle_loader.py` – `load_puzzles_from_json(path)` loads `DungeonPuzzle` and `SequencePuzzle` definitions from `data/puzzles.json`.
- `core/loaders/brain_teaser_loader.py` – `load_brain_teasers(path)` loads teaser definitions (`Riddle`, `WordScramble`, etc.) from `data/brain_teasers.json`.
- `core/loaders/arena_loader.py` – `load_arena_data(path)` loads arena fighter definitions and schedule from `data/arena.json`.
- `core/loaders/challenge_loader.py` – `load_challenge_dungeons(path)` loads challenge dungeon and modifier definitions from `data/challenge_dungeons.json`.
- `core/loaders/secret_boss_loader.py` – `load_secret_bosses(path)` and `load_secret_boss_hints(path)` load secret boss definitions and hint data from their respective JSON files.
- `core/loaders/tutorial_loader.py` – `load_tutorial_data(path)` and `load_tutorial_tips(path)` load tutorial tips/help entries from `data/tutorial_tips.json`.
- `core/loaders/npc_schedule_loader.py` – `load_npc_schedules(path)` loads NPC schedule definitions from `data/npc_schedules.json` and constructs a `ScheduleManager` used by the NPC schedule system.

Engine code that needs domain data imports these functions from `core.loaders` (or the specific submodule), while legacy imports from `core.data_loader` are preserved via thin wrapper functions to ease incremental refactoring.

### Dependency Direction

**Critical Rule**: Engine depends on Core, Core never depends on Engine

- ✅ `engine/world_scene.py` imports `from core.world import World`
- ✅ `engine/battle_scene.py` imports `from core.combat import BattleSystem`
- ❌ `core/world.py` does NOT import from `engine/`
- ❌ `core/combat/` does NOT import from `engine/`

This ensures:
- Core logic is testable without pygame
- Core can be reused in different UI frameworks
- Clear separation of concerns

### Data Serialization

Core modules define serialization methods that engine uses:

```python
# core/save_load.py
class SaveManager:
    def serialize_state(self, world: World, player: Player, ...) -> Dict[str, Any]:
        # Core defines serialization format
        return {
            "world": {...},
            "player": {...},
            # ...
        }

    def deserialize_state(self, data: Dict[str, Any], ...) -> Player:
        # Core defines deserialization logic
        # Reconstructs World, Player, QuestManager from JSON
```

Engine scenes call these methods but don't define the format.

---

## Save File Format Specification

The game uses a JSON-based save file format with versioning, validation, and migration support. Save files are stored in the `saves/` directory as `save_N.json` where N is the slot number.

### File Structure

Save files have the following top-level structure:

```json
{
  "meta": { ... },
  "world": { ... },
  "player": { ... },
  "quests": { ... },        // Optional
  "achievements": { ... },   // Optional
  "day_night": { ... },     // Optional
  "weather": { ... }        // Optional
}
```

### Version System

The save file format is versioned to support migration as the game evolves:

- **Current Version**: `1` (defined in `core/save_load.py` as `SAVE_FILE_VERSION`)
- **Version 0**: Legacy format (no version field, automatically migrated on load)

The version is stored in `meta.version`. When loading a save file:
1. System detects version (defaults to 0 if missing)
2. If version < current, migration is performed
3. Migrated data is validated before use

### Field Specifications

#### `meta` Section

Metadata about the save file:

```json
{
  "version": 1,                    // Save file format version
  "timestamp": "2025-11-30T11:27:41.128505",  // ISO format timestamp
  "play_time_seconds": 452.914     // Total playtime in seconds
}
```

- **`version`** (int, required): Save file format version
- **`timestamp`** (string, required): ISO format datetime when save was created
- **`play_time_seconds`** (float, required): Total playtime accumulated

#### `world` Section

World state and flags:

```json
{
  "current_map_id": "sunharbor_city",  // Current map identifier
  "flags": {                           // World flags (quest states, progression, etc.)
    "gold": 1084,
    "tutorial_completed": true,
    "forest_wolves_cleared": true,
    "luna_recruited": true,
    // ... arbitrary key-value pairs
  },
  "runtime_state": {
    "trigger_states": {},              // Per-map trigger activation states
    "enemy_states": {                  // Per-map enemy defeat states
      "desert_oasis": {
        "bandit_3": true,
        "mimic_1": true
      },
      "forest_path": {
        "slime_patrol_1": true
      }
    }
  }
}
```

- **`current_map_id`** (string, required): ID of the map the player is on
- **`flags`** (dict, required): World flags dictionary (arbitrary key-value pairs)
  - Common flags: `gold`, `tutorial_completed`, quest completion flags, recruitment flags
- **`runtime_state`** (dict, required): Runtime-only state that doesn't persist in World.flags
  - **`trigger_states`**: Per-map trigger activation (one-time triggers)
  - **`enemy_states`**: Per-map enemy defeat tracking (overworld enemies)

**Runtime State Schema:**
```json
{
  "runtime_state": {
    "trigger_states": {
      "<map_id>": {
        "<trigger_id>": true    // true = trigger has fired
      }
    },
    "enemy_states": {
      "<map_id>": {
        "<enemy_entity_id>": true  // true = enemy defeated
      }
    }
  }
}
```

Example:
```json
{
  "runtime_state": {
    "trigger_states": {
      "forest_path": {
        "forest_health_potion": true
      }
    },
    "enemy_states": {
      "forest_path": {
        "slime_patrol_1": true,
        "wolf_patrol_1": true
      },
      "desert_oasis": {
        "bandit_3": true
      }
    }
  }
}
```

#### `player` Section

Complete player state:

```json
{
  "entity_id": "player",
  "name": "Hero",
  "x": 10,                          // World position X
  "y": 0,                           // World position Y
  "inventory": {                     // Item ID -> quantity mapping
    "health_potion": 11,
    "starter_sword": 1
  },
  "hotbar_slots": {                 // Hotbar slot -> item ID mapping (can be empty)
    "1": "health_potion",
    "2": "magic_crystal"
  },
  "equipment": {                     // Equipment slot -> item ID mapping
    "weapon": "starter_sword",
    "armor": null,
    "accessory": null
  },
  "skills": ["power_strike", "arcane_blast"],  // Available skills
  "learned_moves": ["slash", "tackle"],       // Learned combat moves
  "stats": {
    "max_hp": 180,
    "hp": 167,
    "max_sp": 75,
    "sp": 75,
    "attack": 26,
    "defense": 22,
    "magic": 19,
    "speed": 14,
    "luck": 10,
    "level": 7,
    "exp": 1882,
    "status_effects": {}             // Status effect ID -> {duration, stacks}
  },
  "memory_value": 0,                 // Calculator-style memory value (always serialized)
  "memory_stat_type": null,          // Stat type stored in memory (always serialized)
  "party": [                         // Recruited party members
    {
      "entity_id": "luna",
      "name": "Luna",
      "x": 0,
      "y": 0,
      "sprite_id": "party_luna",
      "equipment": {...},
      "base_skills": [...],
      "skills": [...],
      "learned_moves": [...],
      "role": "mage",
      "portrait_id": "portrait_luna",
      "stats": {...},
      "memory_value": 0,             // Party members also have memory
      "memory_stat_type": null,
      "skill_tree_progress": {...},
      "formation_position": "middle"
    }
  ],
  "party_formation": {               // Party formation layout (member_id -> position)
    "luna": "back"
  },
  "formation_position": "front",    // Player's formation position
  "skill_tree_progress": {          // Skill tree unlock state
    "skill_points": 6,
    "skill_points_total": 6,
    "unlocked_nodes": {}
  },
  "player_class": "warrior",        // Primary class
  "player_subclass": "mage",        // Subclass
  "crafting_progress": null,        // Crafting XP and level (or null if not started)
  "bestiary": {                     // Bestiary discovery state
    "entries": {
      "<enemy_type>": {
        "enemy_type": "slime",
        "name": "Practice Slime",
        "sprite_id": "slime",
        "times_encountered": 2,
        "times_defeated": 2,
        "discovery_level": 2,
        "base_hp": 50,
        "base_sp": 10,
        "base_attack": 3,
        "base_defense": 1
      }
    }
  }
}
```

**Required Fields:**
- `entity_id`, `name`, `x`, `y`, `inventory`, `stats`

**Optional Fields:**
- `hotbar_slots`, `equipment`, `skills`, `learned_moves`, `memory_value`, `memory_stat_type`
- `party`, `party_formation`, `formation_position`
- `skill_tree_progress`, `player_class`, `player_subclass`
- `crafting_progress`, `bestiary`

#### `quests` Section (Optional)

Quest manager state:

```json
{
  "active_quests": {
    "quest_id": {
      "objectives": [
        {
          "type": "KILL",
          "target": "slime",
          "current": 3,
          "required": 5
        }
      ],
      "started_at": "2025-11-30T10:00:00"
    }
  },
  "completed_quests": ["tutorial_quest", "cave_exploration"],
  "failed_quests": []
}
```

#### `achievements` Section (Optional)

Achievement manager state:

```json
{
  "unlocked_achievements": ["first_victory", "explorer"],
  "progress": {
    "enemies_defeated": 15,
    "gold_earned": 1084
  }
}
```

#### `day_night` Section (Optional)

Day/night cycle state:

```json
{
  "current_time": 0.5,              // 0.0 = midnight, 0.5 = noon, 1.0 = midnight
  "day_count": 3
}
```

#### `weather` Section (Optional)

Weather system state:

```json
{
  "current_weather": "clear",
  "weather_timer": 120.5
}
```

### Migration System

The save system supports automatic migration between versions:

**Version 0 → 1 Migration:**
- Adds `meta.version = 1` if missing
- Adds `meta.timestamp` with current time if missing
- Ensures all required fields exist with defaults
- Preserves all existing data

Migration is performed automatically on load via `SaveManager._migrate_save_data()`.

### Validation Rules

Before loading, save files are validated via `SaveManager.validate_save_data()`:

**Required Top-Level Keys:**
- `meta`, `world`, `player`

**Required `meta` Fields:**
- `timestamp` (string)
- `play_time_seconds` (number)

**Required `world` Fields:**
- `current_map_id` (string)
- `flags` (dict)

**Required `player` Fields:**
- `entity_id` (string)
- `name` (string)
- `x`, `y` (numbers)
- `inventory` (dict)
- `stats` (dict with required stat fields)

**Required `stats` Fields:**
- `max_hp`, `hp`, `max_sp`, `sp`, `attack`, `defense`, `magic`, `speed`, `luck` (all numbers)

Validation returns `(is_valid, errors)` tuple. Invalid saves trigger recovery mode with default values.

### Example Save File

See `saves/save_1.json` for a complete example of a version 1 save file with all sections populated.

---

## AI Profile Structure

The game uses a data-driven AI system where enemy behavior is defined by JSON profiles. AI profiles support simple rule-based behavior, multi-phase combat, behavior type modifications, and integration with learning AI and coordinated tactics.

### Overview

AI profiles are defined in `data/encounters.json` as part of enemy definitions. Each enemy can have an `ai_profile` field that specifies how it behaves in combat.

### Profile Structure

AI profiles can use two structures:

#### 1. Simple Rules Structure

Flat list of rules evaluated each turn:

```json
{
  "ai_profile": {
    "rules": [
      {
        "conditions": { ... },
        "action": { ... },
        "weight": 10
      }
    ],
    "fallback_action": {
      "type": "attack",
      "target_strategy": "random_enemy"
    }
  }
}
```

#### 2. Multi-Phase Structure

Phases with HP thresholds, each with their own rules:

```json
{
  "ai_profile": {
    "behavior_type": "aggressive",
    "phases": [
      {
        "name": "phase_1",
        "hp_threshold": 70,
        "rules": [ ... ]
      },
      {
        "name": "phase_2",
        "hp_threshold": 40,
        "rules": [ ... ]
      }
    ],
    "fallback_action": { ... }
  }
}
```

### Rule Structure

Each rule has three components:

#### Conditions

Conditions determine when a rule is valid. All conditions must pass for the rule to be selected:

```json
{
  "conditions": {
    "hp_percent": {"min": 0, "max": 50},        // HP between 0-50%
    "sp_percent": {"min": 30, "max": 100},      // SP between 30-100%
    "turn_number": {"min": 1, "max": 3},        // Turns 1-3
    "morale": {"min": 0, "max": 3},             // Morale level (for spare mechanics)
    "allies_alive": {"min": 1},                 // At least 1 ally alive
    "enemies_alive": {"min": 1, "max": 2},      // 1-2 player characters alive
    "status_effects": ["has_poison", "no_stun"], // Enemy status requirements (list format)
    "enemy_status_effects": {"has": ["bleed"]}, // Player status requirements (dict format)
    "ally_status_effects": {"none": ["stun"]}   // Ally status requirements (dict format)
  }
}
```

**Supported Conditions:**
- **`hp_percent`**: Enemy HP percentage range (`min`, `max`)
- **`sp_percent`**: Enemy SP percentage range (`min`, `max`)
- **`morale`**: Enemy morale level for spare mechanics (`min`, `max`)
- **`turn_number`**: Current turn number range (`min`, `max`)
- **`allies_alive`**: Number of alive enemy allies (`min`, `max`)
- **`enemies_alive`**: Number of alive player characters (`min`, `max`)
- **`status_effects`**: Enemy status requirements (see formats below)
- **`ally_status_effects`**: Ally status requirements (see formats below)
- **`enemy_status_effects`**: Player status requirements (see formats below)

**Status Effect Condition Formats:**

The status effect conditions support two formats:

1. **List format** (for `status_effects` on self):
   ```json
   "status_effects": ["has_poison", "no_stun"]
   ```
   - `"has_X"`: Enemy must have status X
   - `"no_X"`: Enemy must NOT have status X

2. **Dict format** (for `ally_status_effects` and `enemy_status_effects`):
   ```json
   "enemy_status_effects": {
     "has": ["poison", "bleed"],   // ALL listed statuses must be present on at least one target
     "any": ["burn", "freeze"],    // ANY of these statuses must be present
     "none": ["shield"],           // NONE of these statuses may be present
     "not": ["invincible"]         // Alias for "none"
   }
   ```

#### Actions

Actions specify what the enemy does when the rule is selected:

```json
{
  "action": {
    "type": "skill",                    // Action type
    "skill_id": "fire_bolt",            // Skill ID (for skill actions)
    "target_strategy": "highest_hp_enemy"  // Target selection strategy
  }
}
```

**Action Types:**
- **`attack`**: Basic physical attack
- **`skill`**: Use a skill (requires `skill_id`)
- **`guard`**: Defend, reducing incoming damage
- **`item`**: Use an item (requires `item_id`)
- **`talk`**: Undertale-style "Act" action (for spare mechanics)

**Target Strategies:**
- **`random_enemy`**: Random player character
- **`weakest_enemy`**: Player with lowest HP
- **`highest_hp_enemy`**: Player with highest HP
- **`random_ally`**: Random enemy ally
- **`weakest_ally`**: Ally with lowest HP
- **`self`**: Target self

#### Weights

Weights determine selection probability when multiple rules are valid:

```json
{
  "weight": 8  // Higher weight = more likely to be selected
}
```

Rules are selected using weighted random selection from all valid rules. If no rules are valid, the `fallback_action` is used.

### Phase System

Multi-phase AI profiles allow enemies to change behavior based on HP thresholds:

**HP Threshold Meaning:**
- `hp_threshold` represents the **minimum HP percentage** required to be in that phase
- Example: `hp_threshold: 50` means "this phase is active when HP >= 50%"
- Phases are checked from highest threshold to lowest
- The first phase where `current_hp_percent >= hp_threshold` is selected

**Phase Selection Logic:**
1. Phases are sorted by `hp_threshold` descending (highest first)
2. First phase where `current_hp_percent >= hp_threshold` is selected
3. If no phase matches, lowest threshold phase is used as fallback

**Example:**
```json
{
  "phases": [
    {
      "name": "aggressive",
      "hp_threshold": 70,    // Active when HP >= 70%
      "rules": [ ... ]
    },
    {
      "name": "desperate",
      "hp_threshold": 25,     // Active when 25% <= HP < 70%
      "rules": [ ... ]
    },
    {
      "name": "last_stand",
      "hp_threshold": 0,      // Active when HP < 25%
      "rules": [ ... ]
    }
  ]
}
```

**How it works with example HP values:**
- Enemy at 80% HP: Uses "aggressive" phase (80 >= 70)
- Enemy at 50% HP: Uses "desperate" phase (50 >= 25, but 50 < 70)
- Enemy at 20% HP: Uses "last_stand" phase (20 >= 0, but 20 < 25)

**Phase Transition Feedback:**
- Bosses and "alpha" enemies show phase transition messages
- Messages appear when phase changes: `"⚡ Enemy shifts tactics to phase_name at X% HP!"`
- Controlled by `phase_feedback` flag in battle system

### Behavior Types

Behavior types modify rule weights to emphasize certain action patterns:

**Supported Types:**
- **`aggressive`**: Boosts attack and damage skill weights (×2 for attacks, ×1.5 for fire/physical skills)
- **`defensive`**: Boosts guard and self-targeting weights (×2 for guard/self, ×1.5 for holy skills)
- **`support`**: Boosts item usage and ally-targeting weights (×2 for items/ally-targeting, ×1.5 for ally skills)
- **`balanced`**: No weight modifications (default)

Behavior type is specified in the AI profile:
```json
{
  "behavior_type": "aggressive",
  "rules": [ ... ]
}
```

### Fallback Actions

When no rules pass their conditions, the `fallback_action` is used:

```json
{
  "fallback_action": {
    "type": "attack",
    "target_strategy": "random_enemy"
  }
}
```

Fallback actions ensure enemies always have a valid action even if all rules fail.

### Example AI Profiles

#### Simple Profile (Tutorial Slime)
```json
{
  "ai_profile": {
    "behavior_type": "balanced",
    "rules": [
      {
        "conditions": {
          "hp_percent": {"min": 0, "max": 100}
        },
        "action": {
          "type": "attack",
          "target_strategy": "random_enemy"
        },
        "weight": 10
      }
    ],
    "fallback_action": {
      "type": "attack",
      "target_strategy": "random_enemy"
    }
  }
}
```

#### Multi-Phase Profile (Ancient Guardian)
```json
{
  "ai_profile": {
    "behavior_type": "aggressive",
    "phases": [
      {
        "name": "phase_1",
        "hp_threshold": 70,
        "rules": [
          {
            "conditions": {
              "hp_percent": {"min": 0, "max": 100},
              "sp_percent": {"min": 50, "max": 100}
            },
            "action": {
              "type": "skill",
              "skill_id": "fire_bolt",
              "target_strategy": "highest_hp_enemy"
            },
            "weight": 8
          }
        ]
      },
      {
        "name": "phase_2",
        "hp_threshold": 40,
        "rules": [
          {
            "conditions": {
              "hp_percent": {"min": 0, "max": 50}
            },
            "action": {
              "type": "item",
              "item_id": "health_potion",
              "target_strategy": "self"
            },
            "weight": 5
          }
        ]
      }
    ],
    "fallback_action": {
      "type": "attack",
      "target_strategy": "weakest_enemy"
    }
  }
}
```

### Integration with Learning AI

The learning AI system (`core/combat_modules/learning_ai.py`) can modify AI profile behavior:

- **Counter-Strategies**: Learning AI detects player patterns and generates counter-strategies
- **Weight Modifiers**: Counter-strategies adjust rule weights to favor actions that counter player behavior
- **Priority Actions**: Counter-strategies can prioritize specific action types

Counter-strategies are applied during rule evaluation via `_apply_counter_strategy()` in `core/combat_modules/ai.py`.

### Integration with Coordinated Tactics

The coordinated tactics system (`core/combat_modules/tactics.py`) allows multiple enemies to coordinate:

- **Tactic Roles**: Enemies can have roles (initiator, supporter, finisher)
- **Coordination Triggers**: Enemies can trigger coordinated attacks when conditions are met
- **AI Profile Integration**: Coordination is separate from AI profiles but can influence action selection

---

## References

- `engine/scene.py` - SceneManager and Scene base class
- `engine/game.py` - Main game loop and scene transitions
- `engine/world_scene.py` - World scene implementation
- `engine/battle_scene.py` - Battle scene implementation
- `engine/ui.py` - TransitionManager for fade effects
- `core/save_load.py` - Save file serialization/deserialization
- `core/combat_modules/ai.py` - AI profile evaluation and phase system
- `core/combat_modules/learning_ai.py` - Learning AI integration
- `core/combat_modules/tactics.py` - Coordinated tactics system
- `data/encounters.json` - Example AI profiles
- `saves/save_1.json` - Example save file structure

---

## Advanced Systems Reference

High‑level combat, saving, and scene architecture are described in this file. For **domain‑specific systems** like fishing, gambling, the monster arena, NPC scheduling, and the tutorial/help framework (including how they hook into time of day, world flags, achievements, and scenes), see `SYSTEMS.md`.

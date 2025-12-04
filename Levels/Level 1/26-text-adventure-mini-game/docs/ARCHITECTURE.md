# Architecture

Current snapshot of how the game is put together: how the runtime boots, how scenes share state, how data flows between the core logic and the pygame layer, and what the save format looks like right now.

For system-specific behavior (fishing, arena, scheduling, tutorial/help, etc.) see `docs/SYSTEMS.md`.

## Runtime Overview
- Entry point `text_adventure_mini_game.py` creates `engine.game.RpgGame`.
- `RpgGame` loads config (`engine/config_loader.py`), initializes display/clock, input manager, mod loader, and optional replay recording.
- Domain data is loaded via `engine/game_loaders.py`: world, dialogue, items, encounters (with optional mod overrides), bestiary metadata, and the default player via `engine/player_factory.py`.
- Core managers are created once: `SaveManager`, `SaveCoordinator`, quest manager, day/night, weather, achievements, NPC schedules, tutorial manager, fishing, brain teasers, gambling, arena, challenge dungeons, post-game, secret bosses/hints. A shared `EventBus` is also created.
- A `SceneManager` is built with the initial `TitleScene` and the managers above so every scene can access them through the manager.
- Main loop (in `engine/game.py`): tick time/weather, process translated input events, run scene transitions for the title/name/class flow, update/draw the active scene, and render toast notifications. F12 captures a screenshot. On exit, any pending replay is flushed.

## Scene System
- `engine/scene.py` defines `Scene` and `SceneManager`. `SceneManager` keeps a stack (`current`, `push`, `pop`, `replace`, `get_scene_of_type`) plus shared managers (`save_manager`, `quest_manager`, `achievement_manager`, `day_night_cycle`, `weather_system`, `schedule_manager`, `tutorial_manager`, `fishing_system`, `brain_teaser_manager`, `gambling_manager`, `arena_manager`, `challenge_dungeon_manager`, `secret_boss_manager`, `hint_manager`, `post_game_manager`, `party_prototypes`, `items_db`, `encounters_data`, `event_bus`). Scenes call `get_manager_attr` for safe access.
- Fade effects come from `engine/ui/transitions.py` (exported via `engine/ui/__init__.py`).
- Key flows:
  - New game: `TitleScene` → `NameEntryScene` → `ClassSelectionScene` → `SubclassSelectionScene` → `_start_tutorial_battle()` → `TutorialBattleScene` → `WorldScene`.
  - Continue: `TitleScene` → `SaveSlotScene` (via `SaveCoordinator.open_load_slot_selection`) → load → `WorldScene`.
  - In-world: `WorldScene` pushes `DialogueScene`, `ShopScene`, `QuestJournalScene`, `InventoryScene`, `EquipmentScene`, `SkillTreeScene`, `PartyMenuScene`, `BestiaryScene`, `ArenaScene`, `ChallengeSelectScene`, `BrainTeaserScene`, etc. Pause/options use the same push/pop stack so world rendering stays beneath menus.
  - Battles are created from encounters and pushed, then popped back to world after rewards/endings.

## Engine ↔ Core Data Flow
- Separation is strict: `core/` holds domain logic (world, entities, stats, combat, quests, items, achievements, schedules, weather, tutorials, save system). `engine/` is pygame UI/rendering/input. Core never imports engine.
- Content is JSON-driven under `data/`. `engine/game_loaders.py` uses `core.loaders` (exposed via `core/data_loader`) to load world, dialogue, items, encounters, quests, tutorial tips, fishing, brain teasers, arena, challenge dungeons, post-game unlocks, secret bosses/hints, and NPC schedules. Mod overrides are merged through `core/mod_loader.ModLoader`.
- `encounters_data` feeds both the overworld and battles (`core.encounters.create_encounter_from_data`). Bestiary metadata is built from encounter JSON (`core.loaders.bestiary_loader.build_bestiary_metadata`) for UI displays.
- `engine/event_bus.EventBus` is a simple pub/sub used by achievements and other listeners; managers can be passed the bus from `RpgGame`.

## Save/Load Architecture
- `core/save_load.SaveManager` handles slots and delegates serialization/deserialization/migration/validation to `core/save/*`. `core/save/context.SaveContext` bundles world, player, and any saveable managers (checked by `save_key` and serialize/deserialize methods).
- `engine/save_coordinator.SaveCoordinator` owns save/load UI flow. It builds a `SaveContext` from the running `RpgGame`, calls `save_to_slot_with_context`/`load_from_slot_with_context`, and swaps to `SaveSlotScene` for selection. After loading it rechecks quest prerequisites and seeds the bestiary before replacing the scene with `WorldScene`.
- Save files live in `saves/save_<slot>.json`, current `SAVE_FILE_VERSION = 1`. Version/migration logic sits in `core/save/migration.py`; validation/recovery in `core/save/validation.py`; deserialization caches shared assets via `DeserializationResources`.
- Top-level structure:
  - `meta`: `version`, ISO `timestamp`, `play_time_seconds` (tracked in `RpgGame._update_time_systems`).
  - `world`: `current_map_id`, `flags`, `visited_maps`, `runtime_state.trigger_states`, `runtime_state.enemy_states`.
  - `player`: id/name/position, inventory + hotbar, equipment, base skills/learned moves, stats, memory fields, party roster and formation, skill tree progress, class/subclass, crafting progress, bestiary.
  - Optional manager blocks when present and saveable: `quests`, `day_night`, `achievements`, `weather`, `fishing`, `puzzles`, `brain_teasers`, `gambling`, `arena`, `challenge_dungeons`, `secret_bosses`, `hints`, `post_game`, `tutorial`, `npc_schedules`. Missing blocks are tolerated for backward compatibility.

## World and Battle Flow
- `engine/world_scene.py` runs the overworld: camera/movement, interaction, quest checks, inline dialogue, shops, hint buttons, minimap, weather overlays, and enemy/boss triggers. Rendering/logic helpers live in `engine/world` (`WorldRenderer`, `OverworldController`, `TriggerHandler`, `EnemySpawnManager`, and `world_logic.py` utilities for quests, shops, warps, achievements, and weather gating).
- Encounters are resolved through `world_logic.start_battle`, which calls `core.encounters.create_encounter_from_data` to build `BattleSystem` inputs, then pushes `BattleScene` with rewards/backdrop info. Rewards/flags/quests are applied via `engine/battle.BattleRewardsHandler`.
- `BattleScene` composes many mixins in `engine/battle` for menus, HUD, animations, AI notifications, outcomes, and layout; `BattlePhaseManager` drives the per-frame update phases.

## AI and Encounters
- Enemy AI is defined in `data/encounters.json` and evaluated by `core/combat_modules` (rule/phase-based profiles with behavior types, fallback actions, optional coordinated tactics and learning AI). Validation helpers in `core/combat/ai_validation` run at `WorldScene` init if enabled.
- Encounter metadata is reused for bestiary seeding and for validating AI assets before a battle starts.

## References
- Core/engine boundaries: `engine/game.py`, `engine/scene.py`, `engine/game_loaders.py`.
- Overworld: `engine/world_scene.py` and `engine/world/*`.
- Combat: `engine/battle_scene.py`, `engine/battle/*`, `core/combat_modules/*`.
- Saving: `core/save_load.py`, `core/save/context.py`, `core/save/serializer.py`, `core/save/deserializer.py`, `engine/save_coordinator.py`.
- Event bus: `engine/event_bus.py`.
- UI transitions: `engine/ui/transitions.py`.
- Data: `data/encounters.json`, `data/quests.json`, `data/items.json`, `data/maps/*`, `data/tutorial_tips.json`.
- Example save shape: `saves/save_1.json`.

For deeper, system-specific behavior see `docs/SYSTEMS.md`.

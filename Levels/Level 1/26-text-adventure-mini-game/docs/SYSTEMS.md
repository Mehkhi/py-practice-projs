## Advanced Systems Architecture

This document describes the game’s **advanced / side systems** and how they integrate with the core engine:

- **Fishing system**
- **Gambling / tavern mini‑games**
- **Monster arena**
- **NPC schedule system**
- **Tutorial and help system**

It complements `ARCHITECTURE.md`, which focuses on the scene stack, core↔engine data flow, save files, and AI. This file documents the **domain‑specific systems** that sit on top of those foundations.

- **Core logic** for each system lives in `core/` and is pygame‑free.
- **Presentation and input** live in `engine/` scenes.
- **Persistence** uses a `save_key` and the Saveable protocol so `SaveManager` can serialize/deserialize automatically.
- **Integration glue** uses:
  - `World` flags for gold, progression, and one‑shot events.
  - `TimeOfDay` from the time system where needed.
  - The global `TutorialManager` and `AchievementManager` passed via `SceneManager`.

---

## Data Loading & Schema Policy

- Loaders share helpers in `core/loaders/base.py` for type checks and required key validation. Messages flow through `[SCHEMA]` logs so issues are easy to spot.
- Default behavior is **tolerant**: malformed sections are logged and skipped while returning usable defaults.
- Set `STRICT_SCHEMA=1` in the environment to raise `ValueError` on schema violations (useful in development or CI).

---

## Fishing System

### Core Logic (`core/fishing.py`)

- **Types**
  - `FishRarity` and `WaterType` are `Enum` classes defining rarity tiers and water categories.
  - `Fish` models a species:
    - Identity: `fish_id`, `name`, `description`, `item_id` (inventory item when caught).
    - Economy: `rarity: FishRarity`, `base_value`.
    - Habitat & timing: `water_types: List[WaterType]`, `time_periods: List[str]` (values from `TimeOfDay.value`, empty = any time).
    - Mechanics: `min_size`, `max_size`, `catch_difficulty` (1–10, used to scale the mini‑game).
  - `FishingSpot` describes a fishable location:
    - Map position: `map_id`, `x`, `y`, `water_type`.
    - Tuning: `is_premium`, `fish_pool: List[str]` (fish IDs), `rarity_modifiers: Dict[str, float]` keyed by rarity string (`"common"`, `"rare"`, etc.).
  - `CaughtFish` wraps a specific catch:
    - `fish: Fish`, `size: float`.
    - `value` property derives gold reward from size:
      - Computes `size_ratio = size / max_size`.
      - Applies a 0.5x–1.5x multiplier to `base_value`.
    - `size_category` buckets (“tiny”, “small”, “medium”, “large”, “enormous”) based on where size falls between `min_size` and `max_size`.

- **FishingSystem**
  - Holds **static definitions** and **player progress**:
    - `fish_db: Dict[str, Fish]`, `spots: Dict[str, FishingSpot]`.
    - `player_records: Dict[str, CaughtFish]` – best catch per fish species.
    - `total_catches: int`.
    - `catches_per_spot: Dict[str, int]`.
  - Lookup helpers:
    - `get_spot_at(map_id, x, y) -> Optional[FishingSpot]` finds a spot at a world tile.
    - `get_available_fish(spot, time_of_day) -> List[Fish]` filters by:
      - Spot’s `fish_pool`.
      - Matching `WaterType`.
      - Time period, if the fish restricts `time_periods`.
  - Probability model:
    - `calculate_catch_chance(fish, spot, has_bait=False, rod_quality=1) -> float`:
      - Starts from rarity base chances (`common` ≈ easy, `legendary` hard).
      - Multiplies by `spot.rarity_modifiers[rarity]` if present.
      - Adds flat bonuses for bait and rod quality (capped).
      - Clamps to \[0.0, 1.0].
    - `roll_for_fish(spot, time_of_day, has_bait=False, rod_quality=1) -> Optional[Fish]`:
      - Applies a **global “bite” roll** (70% chance any fish bites).
      - For available fish, computes per‑fish chance via `calculate_catch_chance`.
      - Uses weighted random selection across fish, normalizing their chances.
      - Returns `None` if no bite or total weight is 0.
  - Results and tracking:
    - `generate_fish_size(fish) -> float` picks a random size between `min_size` and `max_size`.
    - `record_catch(caught: CaughtFish, spot_id: Optional[str]) -> bool`:
      - Increments `total_catches` and `catches_per_spot[spot_id]`.
      - Compares against existing `player_records[fish_id]`, replacing if bigger.
      - Returns `True` if this is a new personal record.
    - `get_fishing_stats() -> Dict` exposes aggregate stats for UI or analytics.

- **Save Integration**
  - `FishingSystem` participates in the generic Saveable pipeline:
    - Class attribute `save_key = "fishing"`.
    - `serialize() -> Dict` returns:
      - `player_records` as `fish_id` → dict with `fish_id` + `size`.
      - `total_catches`.
      - `catches_per_spot`.
    - `@classmethod deserialize(data, fish_db, spots) -> FishingSystem`:
      - Re‑constructs a new system instance using static definitions + saved stats.
    - `deserialize_into(data)`:
      - Clears and re‑fills `player_records`, `total_catches`, `catches_per_spot` **in place**, allowing the same object to be reused across loads.

### Engine Integration (`engine/fishing_scene.py`)

- **Scene Responsibilities**
  - `FishingScene(Scene)` is the interactive UI wrapper around `FishingSystem`:
    - Takes `fishing_system`, `FishingSpot`, `Player`, and `World` at construction.
    - Keeps a reference to the global `SceneManager` through `Scene`.
    - Controls visual phases and input while delegating catch logic to core.

- **Phase Flow**
  - The scene runs a finite‑state loop:
    - `WAITING` – random wait (`3–15s`); animates bobber; when timer expires, calls `_fish_bites()`.
    - `HOOKING` – a fish is biting; the player must react during `hook_window` (0.5s). A successful input transitions to `REELING`, otherwise the fish escapes.
    - `REELING` – timing/position mini‑game:
      - The fish moves erratically along a vertical bar (`fish_position`).
      - The player controls `reel_position` via actions (SPACE, confirm, or UP).
      - Tension and catch progress bars track risk vs progress.
      - On success, `_complete_catch()` is called; on failure, the fish escapes.
    - `CAUGHT` / `ESCAPED` / `CANCELLED` – result screens; ESC or confirm exits back to the previous scene via `manager.pop()`.

- **Using FishingSystem**
  - `_fish_bites()`:
    - Reads `time_of_day` from `manager.day_night_cycle` (defaulting to `"DAY"` if missing).
    - Calls `fishing_system.roll_for_fish(spot, time_of_day, has_bait, rod_quality)`.
    - On success, sets `current_fish` and enters `HOOKING`; on failure, restarts `WAITING`.
  - `_complete_catch()`:
    - Uses `fishing_system.generate_fish_size(current_fish)` and wraps in `CaughtFish`.
    - Records the catch via `fishing_system.record_catch(caught_fish, spot_id)`.
    - Adds the fish’s `item_id` to the player’s inventory.
    - Consumes `premium_bait` or `fishing_bait` when appropriate.

- **Equipment and Items**
  - `_check_equipment()`:
    - Uses `player.get_equipped_item_id("accessory")` and `items_db` from the `SceneManager` to determine rod quality.
    - Inspects the equipped item for a `rod_quality` attribute; falls back to `1` if missing.
    - Checks the player’s inventory for bait items and sets `has_bait` accordingly.

- **Achievements, Popups, and Tutorials**
  - `_complete_catch()`:
    - Fetches `day_night_cycle` and uses the shared `event_bus` from the `SceneManager`.
    - Publishes `fish_caught` with fish ID, rarity, size category, time of day, and unique species count for the Achievement system to consume.
    - If any achievements unlock, and if the current scene exposes `achievement_popup_manager`, it shows corresponding popups.
  - `_trigger_fishing_tutorials()`:
    - Obtains `tutorial_manager` from the `SceneManager`.
    - Uses `World` flags to ensure one‑time triggers:
      - On first catch: sets `_tutorial_first_fish_caught` and triggers `TipTrigger.FIRST_FISH_CAUGHT`.
      - On first legendary catch: sets `_tutorial_first_legendary_fish` and triggers `TipTrigger.FIRST_LEGENDARY_FISH`.

---

## Gambling System

### Core Logic (`core/gambling.py`)

- **Game Types and Statistics**
  - `GamblingGameType` enum defines supported tavern mini‑games: blackjack, high/low dice, slots, coin flip, cups.
  - `GamblingStats` tracks aggregate player behavior:
    - Totals: `total_wagered`, `total_won`, `total_lost`, `games_played`.
    - Extremes: `biggest_win`, `biggest_loss`.
    - Streaks: `current_streak`, `best_streak`, `worst_streak`.
    - Per‑game counters: `blackjack_wins`, `dice_wins`, `slots_wins`, `cups_wins`.

- **Mini‑Game Implementations**
  - `DiceGame`:
    - Rolls `num_dice` (default 2) and stores `last_roll`.
    - `get_total()` sums the dice.
    - `check_high_low("high"|"low")` implements a high/low rule with 7 as a push.
  - `BlackjackGame`:
    - Manages a shuffled deck, player and dealer hands, and player standing state.
    - `get_hand_value` handles face cards and flexible aces (11 or 1).
    - `dealer_play()` runs the standard “hit until 17+” dealer AI.
    - `determine_winner()` returns `"player"`, `"dealer"`, or `"push"`.
  - `SlotsGame`:
    - Represents three reels with symbolic results.
    - Uses weighted random selection for each spin (e.g., sevens are rare).
    - `get_payout_multiplier()` encodes pay lines (jackpot, triple bar, cherry patterns).
    - `is_jackpot()` detects triple sevens for special achievements.
  - `CupsGame`:
    - Shell‑game style “find the ball” mini‑game.
    - `start_game()` randomly places the ball; `generate_shuffles()` creates a swap sequence and tracks the ball position.
    - `guess(cup_index)` returns whether the player picked correctly.

- **GamblingManager**
  - Central orchestration for betting and stats:
    - Fields: `stats: GamblingStats`, `current_game`, `current_bet`.
    - `save_key = "gambling"` for Saveable integration.
  - Economy interaction:
    - All gold is stored in `World` via the `"gold"` flag.
    - `can_afford(amount, world)` safely reads and normalizes gold before comparison.
    - `place_bet(amount, world)`:
      - Validates affordability, decrements `gold`, records `current_bet`, and increments `total_wagered`.
    - `win(multiplier, world) -> int`:
      - Computes `winnings = current_bet * multiplier`, adds it to world gold, records `total_won`, increments `games_played`, updates best win and positive streak, then clears `current_bet`.
    - `lose()`:
      - Updates `total_lost`, `games_played`, worst loss, and negative streak, then clears `current_bet`.
    - `push(world)`:
      - Returns the bet to the player’s gold and increments `games_played`.
  - Game‑specific win tracking:
    - `track_game_win(game_type)` updates per‑game win counters (e.g., blackjack vs dice).
  - Persistence:
    - `serialize()` and `deserialize()` map all `GamblingStats` fields into/from a flat dict.
    - `deserialize_into()` updates an existing manager’s stats in place.

### Engine Integration (`engine/gambling_scene.py`)

- **Scene Responsibilities**
  - `GamblingScene(BaseMenuScene)` wraps an individual gambling session:
    - Constructed with a `GamblingGameType`, `GamblingManager`, and `World`.
    - Exposes a simple phase machine:
      - `betting` – choose bet amount and place a bet.
      - `playing` – interact with the chosen mini‑game.
      - `result` – show outcome and let the player replay.

- **Betting Phase**
  - Input:
    - UP/DOWN adjust `bet_amount` between `min_bet` and `max_bet`.
    - ENTER calls `gambling_manager.place_bet(bet_amount, world)`.
  - On success:
    - `_start_game()` constructs or resets the mini‑game (`DiceGame`, `BlackjackGame`, etc.).
    - Phase switches to `playing`.
  - On failure:
    - Displays a “Not enough gold!” message in the `MessageBox`.

- **Playing Phase**
  - The scene delegates rules to the mini‑game, but translates **input and results**:
    - Dice:
      - Player chooses `"high"` or `"low"`, then `_play_dice()` rolls and determines win/lose/push.
    - Blackjack:
      - Player chooses `"hit"` / `"stand"`; scene calls `hit()`, `dealer_play()`, and `_finish_blackjack()` to resolve.
    - Slots:
      - SPACE triggers `_play_slots()`, which spins, computes multiplier, and detects jackpots.
    - Cups:
      - Player presses 1–3 to pick a cup; `_play_cups()` compares against the internal ball position.
  - After each sub‑game:
    - Calls appropriate `GamblingManager` methods (`win`, `lose`, `push`) to mutate gold and stats.
    - Sets `result_type` and `result_message`, then moves to `result` phase.
    - Triggers achievements and tutorial tips (described below).

- **Result and Replay**
  - In the `result` phase:
    - Pressing SPACE/ENTER returns to `betting` via `_show_result()`:
      - Resets `bet_amount`, per‑game choices, and `game_instance`.
  - ESC from `betting` exits back to the previous scene via `manager.pop()`.

- **Achievements and Flags**
  - `_check_achievements()`:
    - Updates world flags based on `GamblingManager.stats`:
      - `gambling_total_won`, `gambling_best_streak`, `blackjack_wins`.
    - Calls `achievement_manager.check_stat_achievements(stats)` to let the achievement system inspect these values.
  - Slots jackpot:
    - On triple sevens, sets `slots_jackpot` in `World` and publishes `flag_set` on the `event_bus` so achievements can react.

- **Tutorial Integration**
  - `_trigger_gambling_entry_tip()`:
    - On the first time entering the gambling scene, if `_tutorial_first_gambling_shown` is not set:
      - Triggers `TipTrigger.FIRST_GAMBLING` and sets the flag, ensuring one‑shot behavior.
  - `_trigger_result_tip(result)`:
    - On the first gambling win, triggers `TipTrigger.FIRST_GAMBLING_WIN` and sets `_tutorial_first_gambling_win_shown`.
    - On the first loss, triggers `TipTrigger.FIRST_GAMBLING_LOSS` and sets `_tutorial_first_gambling_loss_shown`.

---

## Arena System

### Core Logic (`core/arena.py`)

- **Data Structures**
  - `ArenaFighter`:
    - Identity and visuals: `fighter_id`, `name`, `sprite_id`.
    - Combat stats: `stats` dict (hp, attack, defense, speed), `skills`.
    - Betting: `odds` (e.g., 2.0 for 2:1 payout), `wins`, `losses`.
    - `win_rate` property computes dynamic performance: wins / (wins + losses), default 0.5.
  - `ArenaMatch`:
    - Match ID, `fighter_a`, `fighter_b`, and optional `scheduled_time` (string form of `TimeOfDay`).
  - `ArenaBet`:
    - Links a player bet to `match_id` and chosen `fighter_id`, plus `amount` and `odds_at_bet`.

- **ArenaManager**
  - Central controller for:
    - Fighter roster (`fighters` dict).
    - Match schedule (`arena_schedule`, `current_matches`).
    - Active bets and persistent `match_history`.
  - Match generation:
    - `generate_matches(count=3) -> List[ArenaMatch]`:
      - Shuffles available fighters and pairs them.
      - Uses `arena_schedule["match_times"]` to assign time slots where present.
      - Stores generated matches in `current_matches`.
  - Betting and economy:
    - `place_bet(match, fighter_id, amount, world) -> Optional[ArenaBet]`:
      - Reads `gold` from `World` and ensures the player can afford the bet.
      - Validates that `fighter_id` participates in the specified match.
      - Deducts gold and records an `ArenaBet` in `active_bets`.
  - Match simulation:
    - `simulate_match(match) -> (winner_id, battle_log)`:
      - Runs a turn‑based, enemy‑vs‑enemy fight:
        - Each loop, A attacks B, then B attacks A (if still alive).
        - Uses `_calculate_damage(attacker, defender)` with simple attack vs defense and some random variance.
        - Logs each hit (turn, attacker, defender, damage, defender_hp).
      - Sets winner based on who still has HP.
      - Updates both fighters’ `wins`/`losses`.
      - Recalculates odds using `_update_odds(fighter)`:
        - Odds are inversely related to `win_rate` (bounded between 1.1 and 10.0).
  - Bet resolution and history:
    - `resolve_bets(match, winner_id, world)`:
      - Iterates `active_bets` for the match:
        - Winning bets pay out `amount * odds_at_bet` to world gold.
        - Losing bets yield 0.
      - Builds a `results` list of `(bet, winnings)` and appends a summary entry to `match_history`.
      - Removes resolved bets from `active_bets`.
  - Time‑based utility:
    - `get_current_match(time_of_day: TimeOfDay) -> Optional[ArenaMatch]`:
      - Uses `arena_schedule["match_times"]` to find which match is currently active at a given time period.

- **Save Integration**
  - `save_key = "arena"`.
  - `serialize()` returns:
    - Per‑fighter `wins`, `losses`, and `odds`.
    - A lightweight description of `current_matches` (IDs and fighter IDs).
    - Active bets and complete `match_history`.
  - `deserialize(data, fighter_defs)`:
    - Rebuilds fighters from static definitions plus saved stats.
    - Reconstructs `current_matches` and `active_bets`.
  - `deserialize_into(data)`:
    - Applies saved stats and match/bet state to an existing manager instance.

### Engine Integration (`engine/arena_scene.py`)

- **Scene Responsibilities**
  - `ArenaScene(BaseMenuScene)` presents the monster arena to the player:
    - Handles match browsing, bet placement, watching simulated battles, and viewing results.
    - Shares responsibilities with `GamblingScene` but specifically for **monster vs monster** betting.

- **Phases and Flow**
  - `LOBBY`:
    - Shows a list of today’s `current_matches` and their fighters.
    - Lets the player:
      - Move between matches with UP/DOWN.
      - Toggle selected fighter (A/B) with LEFT/RIGHT.
      - Adjust bet amount with PAGEUP/PAGEDOWN, clamped by available gold.
      - Place a bet with **B**, calling `ArenaManager.place_bet`.
      - Begin watching the selected match with **W**, which calls `simulate_match`.
  - `BATTLE`:
    - After `_watch_match()`:
      - Stores `current_match`, `battle_log`, and `winner_id`.
      - Plays back the battle log at `log_speed` seconds per entry:
        - `update(dt)` advances `log_timer`, increments `log_index`, and updates the message box with the current turn’s action.
        - Pressing SPACE reduces `log_speed` to speed up playback.
      - When the log ends, `_end_battle()` resolves bets and transitions to `RESULT`.
  - `RESULT`:
    - Displays the match winner, total winnings, and a breakdown of each bet’s outcome.
    - ESC returns to `LOBBY`.

- **World Flags and Achievements**
  - `_check_achievements()`:
    - Increments `arena_matches_watched` after each completed battle.
    - Aggregates `arena_gold_won` across winning bets.
    - Detects **underdog wins**:
      - If any winning bet used `odds_at_bet >= 5.0`, sets `arena_underdog_win` and publishes `flag_set` on the `event_bus`.
    - Maintains an `arena_streak` flag based on successive wins/losses.
    - Passes these stats into `achievement_manager.check_stat_achievements(stats)`.

- **Tutorial Integration**
  - `_trigger_first_visit_tip()`:
    - On first entry into the arena scene (no prior `_tutorial_first_arena_visit` flag):
      - Triggers `TipTrigger.FIRST_ARENA_VISIT` and sets the world flag.
  - `_trigger_first_bet_tip()`:
    - On first successful bet (`_place_bet()`):
      - Triggers `TipTrigger.FIRST_ARENA_BET` and marks `_tutorial_first_arena_bet` in `World`.

---

## NPC Schedule System

### Core Logic (`core/npc_schedules.py`)

- **Schedule Data**
  - `ScheduleEntry`:
    - `time_periods: List[TimeOfDay]` – time segments when the entry is active.
    - Target position: `map_id`, `x`, `y`.
    - Optional metadata:
      - `activity` (e.g., `"sleeping"`, `"working"`).
      - `shop_available: bool` (open/closed).
      - `alternative_dialogue_id` for closed‑shop or off‑duty states.
  - `NPCSchedule`:
    - Anchors an NPC’s schedule to an `npc_id`.
    - Defines fallback `default_map_id`, `default_x`, `default_y`.
    - Holds an ordered list of `entries`.

- **ScheduleManager**
  - Construction:
    - Accepts an optional `schedules` dict mapping NPC IDs to `NPCSchedule`.
    - Tracks internal state:
      - `_last_time_period: Optional[TimeOfDay]`.
      - `_npc_positions: Dict[npc_id, (map_id, x, y)]` for last known coordinates.
      - `_pending_position_restore` and `_force_schedule_refresh` for save compatibility.
  - Queries:
    - `get_npc_location(npc_id, time_of_day) -> (map_id, x, y)`:
      - Finds the first `ScheduleEntry` matching the current time.
      - Falls back to schedule defaults if no entry matches.
      - Returns `("", 0, 0)` when there is no schedule at all (meaning the schedule system won’t move that NPC).
    - `get_npc_activity(npc_id, time_of_day) -> Optional[str]`:
      - Returns `entry.activity` for the first matching time period, or `None`.
    - `is_shop_available(npc_id, time_of_day) -> bool`:
      - Returns `entry.shop_available` for the matching time period, defaulting to `True` when there is no schedule or no matching entry.
    - `get_alternative_dialogue(npc_id, time_of_day) -> Optional[str]`:
      - Returns `alternative_dialogue_id` **only when** `shop_available` is `False`.
    - `get_npcs_on_map(map_id, time_of_day) -> List[str]`:
      - Lists NPC IDs whose scheduled or default location is the specified map for the given time.
    - `is_npc_available_for_quest(npc_id, time_of_day) -> bool`:
      - Uses `get_npc_activity` and an “unavailable” set (`{"sleeping", "away", "busy"}`) to decide if the NPC should be allowed to give or progress quests.

- **Update Loop and World Integration**
  - `update(world, time_of_day) -> List[str]` is called when the world’s time period may have changed.
  - Guard logic:
    - Skips work if:
      - The time period is unchanged **and** there is no pending restore or forced refresh.
      - Or `world.npc_interaction_active` is true – avoiding teleporting an NPC mid‑conversation.
  - Movement:
    - For each scheduled NPC:
      - Uses `world.get_entity_by_id(npc_id)` to find the entity and its current map.
      - Computes the target location via `get_npc_location`.
      - If the NPC needs to move:
        - Calls `world.move_entity_to_map(npc_id, current_map_id, target_map_id, x, y)`.
        - On success, records the new position in `_npc_positions` and collects the NPC ID in the return list.
  - Saved positions:
    - `_npc_positions` tracks the last known map and tile for each NPC which was moved by the schedule system.

- **Save Integration**
  - `save_key = "npc_schedules"`.
  - `serialize()` stores:
    - `last_time_period` as `TimeOfDay.value` (or `None`).
    - `npc_positions` as `{npc_id: {"map_id": str, "x": int, "y": int}}`.
  - `deserialize_into(data)`:
    - Validates `data` structure and reconstructs `_last_time_period` from either:
      - The exact enum value string, or
      - The enum name (upper‑cased), for backwards compatibility.
    - Rebuilds `_npc_positions` if present, and:
      - Sets `_pending_position_restore = True` when there are saved positions.
      - Otherwise, sets `_force_schedule_refresh` if a valid time period exists, so that schedules will re‑apply on the next update.
  - `_apply_saved_positions(world)`:
    - When `_pending_position_restore` is set, moves each NPC back to its saved map/coordinates using `world.move_entity_to_map`.
    - Updates `_npc_positions` to the actual positions used after moves succeed or fail.

---

## Tutorial and Help System

### Core Tutorial Manager (`core/tutorial_system.py`)

- **Triggers and Types**
  - `TipTrigger` is a large enum of **named game events**, such as:
    - Progression: `FIRST_BATTLE`, `FIRST_LEVEL_UP`, `FIRST_QUEST_ACCEPTED`, `POST_GAME_START`, `NEAR_COMPLETION`.
    - Systems: `FIRST_FISHING_SPOT`, `FIRST_FISH_CAUGHT`, `FIRST_LEGENDARY_FISH`, `FIRST_GAMBLING`, `FIRST_GAMBLING_WIN`, `FIRST_GAMBLING_LOSS`, `FIRST_ARENA_VISIT`, `FIRST_ARENA_BET`, `FIRST_CRAFTING`, etc.
    - Context: `ENTERED_DUNGEON`, `ENTERED_TOWN`, `NIGHT_TIME_FIRST`, `SHOP_CLOSED`, `LOW_HP_WARNING`, `LOW_SP_WARNING`.
  - `TutorialTip`:
    - Identified by a string `tip_id`.
    - Bound to a `TipTrigger`.
    - Contains `title`, `content`, `priority`, `category`, and `requires_tips` prerequisites.
  - `HelpEntry`:
    - Always‑available reference entry for the help overlay, grouped by `category` and ordered with `order`.

- **TutorialManager**
  - Holds:
    - `tips: Dict[str, TutorialTip]`.
    - `help_entries: Dict[str, HelpEntry]`.
    - `dismissed_tips: Set[str]`.
    - `seen_tips: Set[str]`.
    - `pending_tips: List[str]` sorted by priority (descending).
    - `tips_enabled: bool` toggle.
  - Registration:
    - `register_tip(tip)` and `register_help_entry(entry)` are called during initialization to populate the catalog.
  - Triggering:
    - `trigger_tip(trigger: TipTrigger) -> Optional[TutorialTip]`:
      - Looks up all tips matching the trigger.
      - Filters out tips that cannot be shown (dismissed or unmet prerequisites).
      - Picks the highest‑priority remaining tip.
      - Enqueues its `tip_id` into `pending_tips`, kept sorted by priority.
      - Returns the chosen `TutorialTip` (or `None` if nothing qualifies).
  - Dismissal and retrieval:
    - `dismiss_tip(tip_id, permanently=False)`:
      - Adds the tip to `seen_tips` and optionally to `dismissed_tips`.
      - Removes it from `pending_tips` if present.
    - `get_pending_tip() -> Optional[TutorialTip]`:
      - Pops the next `tip_id` from `pending_tips` and returns the associated `TutorialTip`.
    - `get_help_entries_by_category()` groups help entries, ordered within each category.
    - `can_show_tip(tip_id)` enforces the “not dismissed, prerequisites met” rules.
  - Save integration:
    - `save_key = "tutorial"`.
    - `serialize()` stores `dismissed_tips`, `seen_tips`, and `tips_enabled`.
    - `deserialize()` and `deserialize_into()` restore these sets and flags, leaving the static tip/help definitions untouched.

### Tutorial Battle Flow (`engine/tutorial_battle_scene.py`)

- **Purpose**
  - `TutorialBattleScene` is a specialized subclass of `BattleScene` that **teaches combat mechanics step‑by‑step**.
  - It uses an internal `TutorialStep` enum to gate which actions the player should perform next.

- **Flow and State**
  - `TutorialStep` states include:
    - Intro and explanation states (`INTRO`, `ATTACK_EXPLAINED`, `SKILL_EXPLAINED`, etc.).
    - “Done” check‑points (`ATTACK_DONE`, `SKILL_DONE`, etc.).
    - `VICTORY_EXPLAINED` and final `COMPLETE`.
  - The scene holds:
    - `tutorial_step` – current step.
    - `_pending_action_type` – which action (attack/skill/item/guard/talk) we’re waiting to see completed.
    - `_last_battle_state` – last `BattleState` to detect transitions.
    - `_actions_taken` – flags indicating which action types the player has successfully executed.
    - A `tutorial_messages` dict mapping steps to on‑screen instructions.

- **Input and State Machine**
  - `handle_event`:
    - Intercepts ENTER while `_waiting_for_enter` is true to advance from intro and victory messages.
    - For all other combat input, delegates to the base `BattleScene.handle_event`.
  - `_handle_main_menu_selection`:
    - Wraps the parent implementation:
      - Reads the selected main menu action (e.g., `"Attack"`, `"Skill"`).
      - Normalizes to a lower‑case key and sets `_pending_action_type` if this action hasn’t been demonstrated yet.
      - Calls `super()._handle_main_menu_selection()` to perform the actual battle logic.
  - `update(dt)`:
    - First calls `super().update(dt)` to let the underlying battle system progress.
    - Then checks for transitions back to `BattleState.PLAYER_CHOOSE` while `_pending_action_type` is set:
      - If the action just executed was “attack”, it marks `"attack"` in `_actions_taken` and advances the tutorial to the next explanation step (`SKILL_EXPLAINED`), updating the message box.
      - Repeats similarly for `"skill"`, `"item"`, `"guard"`, and `"talk"`.
      - Clears `_pending_action_type`.
    - When all actions have been demonstrated and we’re back to `PLAYER_CHOOSE`, shows `VICTORY_EXPLAINED`.
    - When `BattleState.VICTORY` is reached and the tutorial isn’t marked complete, sets `TutorialStep.COMPLETE` and presents a final message guiding the player back to the overworld.
  - Victory and exit:
    - `_handle_victory()` calls `super()._handle_victory()` to apply XP, items, flags, etc., but then restores the tutorial’s custom victory message in the `MessageBox`.
    - `_transition_to_overworld()` constructs a new `WorldScene` using `SceneManager` resources (`save_manager`, `quest_manager`, `encounters_data`, config, etc.) and calls `manager.replace(overworld)`.

### System‑Wide Trigger Points

- **Where triggers are called**
  - Fishing:
    - `FishingScene` calls `tutorial_manager.trigger_tip` for `TipTrigger.FIRST_FISH_CAUGHT` and `TipTrigger.FIRST_LEGENDARY_FISH`.
  - Gambling:
    - `GamblingScene` triggers `FIRST_GAMBLING` on entry, and `FIRST_GAMBLING_WIN` / `FIRST_GAMBLING_LOSS` after results.
  - Arena:
    - `ArenaScene` triggers `FIRST_ARENA_VISIT` on entering the arena, and `FIRST_ARENA_BET` on placing the first bet.
  - Other systems (shops, dungeons, crafting, puzzles, etc.) follow similar patterns in their respective scenes.

- **One‑shot behavior with World flags**
  - Scenes rely on `World` flags (e.g., `_tutorial_first_gambling_shown`) to ensure tips only trigger once.
  - The tutorial system itself handles “don’t show again” via `dismissed_tips`, which is separate from per‑save one‑shot world flags.

- **Adding new tutorial content**
  - Choose or add a `TipTrigger` for the new event.
  - Register a `TutorialTip` instance tied to that trigger.
  - Optionally add a `HelpEntry` for the general help overlay.
  - In the relevant scene or system:
    - Use `tutorial_manager.trigger_tip(trigger)` at the right moment.
    - Use a `World` flag if you want the event to be strictly once per save, even if the player hasn’t dismissed the tip.

---

## Integration Patterns and Examples

### Common Integration Pattern

When adding a new advanced system, follow the existing design:

- **1. Core module in `core/`**
  - Define pure‑logic types, enums, and manager classes (no pygame).
  - Decide on a `save_key` string for use by the save system.
  - Implement `serialize()`, `deserialize()` (if constructing) and/or `deserialize_into()` (if mutating in place).
  - Use `World` and other core modules only through pure Python APIs.

- **2. Engine scene in `engine/`**
  - Create a scene subclass (`Scene` or `BaseMenuScene`) responsible for:
    - Input handling (keyboard/controller mapping via `InputManager`).
    - Calling into your core module for simulation and rules.
    - Rendering a focused UI for the system.
  - Obtain shared managers from `SceneManager`:
    - `save_manager`, `quest_manager`, `achievement_manager`, `tutorial_manager`, `day_night_cycle`, `items_db`, etc.
  - Use `World` flags for:
    - Economy (`gold`, or other currencies).
    - One‑shot events and progression flags.
    - Stats that achievements will read.

- **3. Save and time integration**
  - Register your system’s manager with the global **save context** using its `save_key`.
  - If your system is time‑sensitive:
    - Accept `TimeOfDay` or its string value from the owning scene.
    - Keep all scheduling/time calculations in your core module where possible.

- **4. Achievements and tutorials**
  - For achievements:
    - Expose counters and flags through `World` or dedicated manager stats.
    - Publish event-based milestones on the shared `event_bus` (e.g., `flag_set`, `battle_won`, `fish_caught`) so `AchievementManager` can react, and call `achievement_manager.check_stat_achievements(stats)` for stat-style checks.
  - For tutorials:
    - Decide whether the new feature needs one‑shot or context tips.
    - Add new `TipTrigger` values and `TutorialTip` definitions as needed.
    - Call `tutorial_manager.trigger_tip(...)` from your scene, using `World` flags to prevent redundant prompts.

### Example Flow: Fishing at a Spot

- Player interacts with a fishing tile in the overworld:
  - `WorldScene` locates a `FishingSpot` via `FishingSystem.get_spot_at(map_id, x, y)`.
  - `WorldScene` constructs a `FishingScene` with the shared `FishingSystem`, `World`, and `Player`, then `SceneManager.push(fishing_scene)`.
- In `FishingScene`:
  - Phase `WAITING` runs until `_fish_bites()`:
    - Gets `time_of_day` from `day_night_cycle`.
    - Calls `FishingSystem.roll_for_fish`.
  - Successful bite:
    - Player completes `HOOKING` and `REELING`.
    - `_complete_catch()`:
      - Calls `FishingSystem.generate_fish_size` and `record_catch`.
      - Adds the fish’s `item_id` to the inventory, handles bait, and notifies `AchievementManager`.
      - Triggers fishing tutorial tips via `TutorialManager` and world flags.
  - On exit, control returns to `WorldScene`; fishing state persists via the `FishingSystem`’s Saveable integration.

### Example Flow: Betting and Watching an Arena Match

- Player enters the arena:
  - The game constructs `ArenaScene` with a shared `ArenaManager` and `World` and pushes it via `SceneManager`.
  - On first visit, `_trigger_first_visit_tip()` calls `TutorialManager` with `TipTrigger.FIRST_ARENA_VISIT`.
- In `ArenaScene` lobby:
  - If `ArenaManager.current_matches` is empty, `generate_matches()` is called to create today’s fights.
  - Player selects a match and fighter, adjusts `bet_amount`, and presses **B**:
    - `ArenaManager.place_bet` decrements world `gold` and records an `ArenaBet`.
    - On first bet, `_trigger_first_bet_tip()` triggers `TipTrigger.FIRST_ARENA_BET`.
- Watching the match:
  - Pressing **W**:
    - Calls `ArenaManager.simulate_match()` to produce `winner_id` and `battle_log`.
    - Enters `BATTLE` phase to replay log entries over time.
  - When the log ends:
    - `_end_battle()` calls `ArenaManager.resolve_bets()` to calculate winnings, update world gold, and store results.
    - `_check_achievements()` updates arena‑related stats/flags and delegates to `AchievementManager`.
    - Scene transitions to `RESULT`, then back to `LOBBY` when the player presses ESC.

These patterns keep each system **modular, testable, and well‑integrated** with saves, time, achievements, and tutorials while maintaining the core↔engine separation described in `ARCHITECTURE.md`.

## Content Creation Guide

This guide explains how to add or tweak advanced content in the game **without writing Python**, by editing JSON files and reusing existing systems.

- Most content lives in `data/*.json`
- The game logic that uses this data lives under `core/` and `engine/`
- After editing JSON, you should always:
  - Validate the JSON (no missing commas or quotes)
  - Run the game and try your changes in-game

For a high-level view of how systems fit together, see `SYSTEMS.md`, `ARCHITECTURE.md`, and the per-system analysis docs in the repo.

---

## Fishing Content

### Files involved

- `data/fishing.json` – defines **fish types** and **fishing spots**
- `core/fishing.py` – code that reads this data and runs the fishing system
- `data/maps/*.json` – map IDs and coordinates (for deciding where to place spots)

You can safely add **new fish** and **new fishing spots** by editing `data/fishing.json`.

### Fish definitions (`fish` array)

At the top of `data/fishing.json` you will see:

- **`fish`**: a list of all fish that can ever be caught
- **`spots`**: a list of world locations where you can fish

A fish entry looks like this:

```json
{
  "fish_id": "common_carp",
  "name": "Common Carp",
  "rarity": "common",
  "base_value": 15,
  "water_types": ["freshwater"],
  "time_periods": [],
  "min_size": 0.5,
  "max_size": 2.0,
  "catch_difficulty": 2,
  "description": "A hardy fish found in most freshwater.",
  "item_id": "fish_common_carp"
}
```

#### Fields and allowed values

- **`fish_id`**: unique identifier used by the system
  - Must be **unique** across all fish
  - Used in `fish_pool` for spots and in save data
- **`name`**: friendly name shown to the player
- **`rarity`**: affects base catch chance and value
  - Allowed values (from `FishRarity`): `common`, `uncommon`, `rare`, `legendary`
- **`base_value`**: base gold value when sold; actual value is scaled by size
- **`water_types`**: list of water types where this fish can appear
  - Allowed values (from `WaterType`): `freshwater`, `saltwater`, `swamp`, `magical`
- **`time_periods`**: list of time-of-day strings; empty list means **any time**
  - Strings must match `TimeOfDay` values, such as:
    - `DAWN`, `DAY`, `MORNING`, `NOON`, `AFTERNOON`, `DUSK`, `EVENING`, `NIGHT`, `MIDNIGHT`
  - If non-empty, the fish is only available during those periods
- **`min_size` / `max_size`**: size range used for random size generation and value scaling
- **`catch_difficulty`**: 1–10, affects mini-game difficulty
- **`description`**: flavor text
- **`item_id`**: ID of the **item** this fish becomes in inventory
  - Must match an entry in `data/items.json`

#### Template for adding a new fish

Add a new object to the `fish` array (remember commas between entries):

```json
{
  "fish_id": "silver_perch",
  "name": "Silver Perch",
  "rarity": "uncommon",
  "base_value": 40,
  "water_types": ["freshwater"],
  "time_periods": ["MORNING", "AFTERNOON"],
  "min_size": 0.4,
  "max_size": 1.6,
  "catch_difficulty": 4,
  "description": "A shimmering perch that prefers bright daylight.",
  "item_id": "fish_silver_perch"
}
```

Checklist when adding a fish:

- **`fish_id`** is new and not used by any other fish
- **`item_id`** exists in `data/items.json` (or you add a matching item there)
- `rarity`, `water_types`, and `time_periods` use allowed values

### Fishing spots (`spots` array)

Further down in `data/fishing.json`, `spots` defines each fishing location:

```json
{
  "spot_id": "village_pond",
  "name": "Village Pond",
  "map_id": "riverside_town",
  "x": 8,
  "y": 6,
  "water_type": "freshwater",
  "is_premium": false,
  "fish_pool": [
    "common_carp",
    "small_bass",
    "pond_perch"
  ],
  "rarity_modifiers": {}
}
```

#### Fields

- **`spot_id`**: unique ID for the spot (used in saves and stats)
- **`name`**: label for the spot (used in UI)
- **`map_id`**: which map this spot is on
  - Must match a `map_id` from `data/maps/*.json`
- **`x`, `y`**: tile coordinates on that map
  - Use existing spots as a reference (copy `map_id`, `x`, `y` and adjust)
- **`water_type`**: one of `freshwater`, `saltwater`, `swamp`, `magical`
- **`is_premium`**: `true` or `false`
  - Premium spots tend to have better rarity modifiers and pools
- **`fish_pool`**: list of `fish_id`s that can appear at this spot
  - Each ID must exist in the `fish` array
- **`rarity_modifiers`**: optional tuning for rarity probabilities
  - Keys are rarity strings such as `"uncommon"`, `"rare"`, `"legendary"`
  - Values are multipliers; >1.0 increases that rarity’s chance

#### Example: adding a new pond on an existing map

Suppose you want a new pond in `riverside_town` that features your new `silver_perch` and some common fish:

```json
{
  "spot_id": "riverside_garden_pond",
  "name": "Riverside Garden Pond",
  "map_id": "riverside_town",
  "x": 9,
  "y": 9,
  "water_type": "freshwater",
  "is_premium": false,
  "fish_pool": [
    "common_carp",
    "sunfish",
    "silver_perch"
  ],
  "rarity_modifiers": {
    "uncommon": 1.2
  }
}
```

Checklist when adding a spot:

- `spot_id` is unique
- `map_id`, `x`, `y` point to a water tile on that map
- Every entry in `fish_pool` exists in `fish`
- `rarity_modifiers` keys match rarity strings (`common`, `uncommon`, `rare`, `legendary`)

---

## Gambling Games via Dialogue

### Files involved

- `core/gambling.py` – defines available gambling game types and logic
- `data/dialogue.json` – defines NPC dialogue and special flags that start gambling
- `data/tutorial_tips.json` – contains gambling tips (optional reading)

You **do not** need to modify Python code to hook existing gambling games into new NPCs. You only edit `data/dialogue.json`.

### Available gambling games

From `GamblingGameType` in `core/gambling.py`, the supported game types are:

- `blackjack`
- `dice_roll`
- `slots`
- `coin_flip`
- `cups_game`

Adding **brand new mechanics** requires code changes, but reusing one of these games is data-only.

### How dialogue hooks start games

In `data/dialogue.json`, look at the `gambler_intro` node:

- It presents choices like **"Blackjack (Min 50g)"**, **"Dice (Min 20g)"**, etc.
- Each choice uses a special **`set_flag`** value:
  - `_start_blackjack`
  - `_start_dice`
  - `_start_slots`
  - `_start_cups`

These internal flags are interpreted by the game to open the corresponding mini-game.

Key points:

- To offer a gambling game from **any** NPC:
  - Add a dialogue node or choice
  - Set the choice’s `set_flag` to one of the `_start_*` values
- Typically, `next_id` is left `null` so the game can transition into the mini-game instead of another dialogue node.

### Example: adding dice gambling to a tavern NPC

Here is a new dialogue node for a tavern gambler who offers a dice game:

```json
{
  "id": "mountain_tavern_gambler",
  "text": "Fancy a little game of chance? Dice never lie... only the players do.",
  "speaker": "Grin the Gambler",
  "portrait_id": "portrait_gambler",
  "choices": [
    {
      "text": "Play Dice (Min 20g)",
      "next_id": null,
      "set_flag": "_start_dice"
    },
    {
      "text": "Maybe later.",
      "next_id": null,
      "set_flag": null
    }
  ]
}
```

Once this node is wired into an NPC (via the map/entity setup), selecting **Play Dice** will launch the dice mini-game.

### Tutorial tip tie-in

The tutorial system includes triggers like:

- `FIRST_GAMBLING`
- `FIRST_GAMBLING_WIN`
- `FIRST_GAMBLING_LOSS`

These live in `core/tutorial_system.py` (`TipTrigger`) and are wired by code based on gameplay events. As a content author:

- You normally **do not** have to change code for these to work
- You can add or adjust the **text** for the relevant tips in `data/tutorial_tips.json` if needed (see the Tutorial section below)

---

## Arena Fighters and Matches

### Files involved

- `data/arena.json` – defines arena fighters and the arena schedule
- `core/arena.py` – code that:
  - Loads fighters and schedule
  - Generates matches
  - Simulates battles and resolves bets
- `data/dialogue.json` – arena dialogue and the `_open_arena` hook

### Fighter definitions (`fighters` object)

At the top of `data/arena.json`, you’ll see:

- **`fighters`**: an object whose keys are fighter IDs, with fighter definitions as values

A fighter entry looks like this:

```json
"iron_golem": {
  "fighter_id": "iron_golem",
  "name": "Iron Golem",
  "sprite_id": "golem",
  "stats": {
    "hp": 150,
    "attack": 25,
    "defense": 30,
    "speed": 5
  },
  "skills": ["smash", "iron_defense"],
  "odds": 1.8
}
```

#### Fields and expectations

- **Top-level key** (e.g. `"iron_golem"`):
  - Should match `fighter_id`
- **`fighter_id`**: internal ID, must be unique across fighters
- **`name`**: shown in the arena UI
- **`sprite_id`**:
  - Must match a sprite in `data/sprite_manifest.json`
- **`stats`**:
  - `hp`: starting hit points
  - `attack`, `defense`, `speed`: used by `ArenaManager._calculate_damage` and turn order
  - You can copy rough ranges from existing fighters for balance
- **`skills`**:
  - List of move IDs, typically defined in `data/moves.json`
  - They are mostly for flavor in logs/UI; the arena simulation uses simplified damage logic
- **`odds`**:
  - Starting betting odds (e.g. `2.0` = 2:1)
  - The arena system updates odds over time based on **win rate**, so this is just the starting value

#### Template for adding a new fighter

Add a new key/value pair inside `fighters`:

```json
"frost_wyvern": {
  "fighter_id": "frost_wyvern",
  "name": "Frost Wyvern",
  "sprite_id": "wyvern_ice",
  "stats": {
    "hp": 110,
    "attack": 38,
    "defense": 18,
    "speed": 20
  },
  "skills": ["ice_breath", "wing_slash"],
  "odds": 2.0
}
```

Checklist:

- Fighter key (`"frost_wyvern"`) matches `"fighter_id"`
- `sprite_id` exists in `data/sprite_manifest.json`
- `skills` are valid move IDs from `data/moves.json` (or are added there)
- `odds` around `1.5–3.0` is a good starting point; extremes (`1.1` or `5.0+`) are for very strong/weak fighters

### Arena schedule (`arena_schedule`)

In `data/arena.json`:

```json
"arena_schedule": {
  "match_times": ["MORNING", "AFTERNOON", "EVENING"],
  "matches_per_day": 3
}
```

- **`match_times`**:
  - List of time-of-day strings used to align matches with the world’s `TimeOfDay`
  - Strings must match values like: `MORNING`, `AFTERNOON`, `EVENING`, etc.
- **`matches_per_day`**:
  - How many matches `ArenaManager.generate_matches` should create

How matches are generated:

- `ArenaManager.generate_matches` shuffles the fighter list and pairs them up
- It assigns each match a time slot from `match_times` (if available)
- Content authors usually **only** adjust:
  - Which fighters exist
  - How many matches per day
  - Which times of day have matches

### Dialogue hook: opening the arena

In `data/dialogue.json`, the `arena_intro` node includes a choice:

- `"set_flag": "_open_arena"`

This special flag tells the game to open the arena UI. You can:

- Reuse this same `id` where needed, or
- Create new nodes that include a choice with `set_flag: "_open_arena"` to open the arena from different NPCs or locations

---

## NPC Schedules

### Files involved

- `data/npc_schedules.json` – defines where NPCs are and when
- `core/npc_schedules.py` – code that:
  - Picks the correct schedule entry for the current time
  - Moves NPCs between maps
  - Controls shop availability and alternative dialogue IDs
- `data/dialogue.json` – contains alternative dialogues for when shops are closed (by `id`)

You can add or modify **where NPCs are at different times of day** and **whether their shops are open** by editing `data/npc_schedules.json`.

### Schedule structure (`schedules` object)

Top level:

- **`schedules`**: object whose keys are NPC IDs, values are each NPC’s schedule

Example entry:

```json
"forest_merchant": {
  "default_map_id": "forest_path",
  "default_x": 3,
  "default_y": 4,
  "entries": [
    {
      "time_periods": ["MORNING", "NOON", "AFTERNOON"],
      "map_id": "forest_path",
      "x": 3,
      "y": 4,
      "activity": "tending shop",
      "shop_available": true
    },
    {
      "time_periods": ["DUSK", "EVENING"],
      "map_id": "riverside_inn",
      "x": 4,
      "y": 5,
      "activity": "relaxing",
      "shop_available": false,
      "alternative_dialogue_id": "merchant_off_duty"
    }
  ]
}
```

#### Fields

- **NPC key** (e.g. `"forest_merchant"`):
  - Must match the NPC’s **entity ID** defined in `data/entities.json` / entity setup
- **`default_map_id`, `default_x`, `default_y`**:
  - Fallback location if no time-based entry matches
- **`entries`**: list of schedule entries

Each **schedule entry**:

- **`time_periods`**:
  - List of `TimeOfDay` strings; if current time is in this list, the entry is active
- **`map_id`, `x`, `y`**:
  - Where the NPC should be during those time periods
- **`activity`** (optional string):
  - Description of what the NPC is doing (used by some systems and for logic)
- **`shop_available`** (optional, default `true` in code if not present):
  - If `false`, the NPC’s shop interaction is considered **closed**
- **`alternative_dialogue_id`** (optional):
  - If `shop_available` is `false`, this dialogue ID can be used to show a “closed” message
  - Must match an `id` in `data/dialogue.json` (e.g. `"shop_closed_sleeping"`)

### Time-of-day and activities

`time_periods` values must match the `TimeOfDay` enum, such as:

- `DAWN`, `MORNING`, `NOON`, `AFTERNOON`, `DUSK`, `EVENING`, `NIGHT`, `MIDNIGHT`

`ScheduleManager.is_npc_available_for_quest` treats certain activities as **unavailable**:

- `"sleeping"`
- `"away"`
- `"busy"`

So, if you set an entry’s `activity` to one of these, quests may not progress with that NPC during that time.

### Shop behavior and alternative dialogue

When a player interacts with a shop NPC:

- `shop_available` determines if the shop UI is accessible
- If `shop_available` is `false` and `alternative_dialogue_id` is set:
  - That dialogue node is shown instead (e.g., “Shop’s closed, come back tomorrow”)

Common alternative dialogue IDs (from `data/dialogue.json`) include:

- `"shop_closed_generic"`
- `"shop_closed_sleeping"`
- `"shop_closed_evening"`
- `"merchant_off_duty"`
- `"innkeeper_off_duty"`
- `"black_market_closed"`
- and others for specific merchants

### Example: adding a day/evening/night schedule for a new shop NPC

Imagine a new NPC `mountain_apothecary` in `mountain_town`:

```json
"mountain_apothecary": {
  "default_map_id": "mountain_town",
  "default_x": 6,
  "default_y": 4,
  "entries": [
    {
      "time_periods": ["MORNING", "NOON", "AFTERNOON"],
      "map_id": "mountain_town",
      "x": 6,
      "y": 4,
      "activity": "mixing potions at the stall",
      "shop_available": true
    },
    {
      "time_periods": ["DUSK", "EVENING"],
      "map_id": "mountain_inn",
      "x": 3,
      "y": 3,
      "activity": "sharing remedies with travelers",
      "shop_available": false,
      "alternative_dialogue_id": "shop_closed_evening"
    },
    {
      "time_periods": ["NIGHT", "MIDNIGHT", "DAWN"],
      "map_id": "mountain_town",
      "x": 5,
      "y": 2,
      "activity": "sleeping",
      "shop_available": false,
      "alternative_dialogue_id": "shop_closed_sleeping"
    }
  ]
}
```

Checklist:

- NPC ID (`"mountain_apothecary"`) matches the entity’s ID
- `alternative_dialogue_id` values exist in `data/dialogue.json`
- Time ranges cover the full day without overlap (for easier reasoning)

---

## Tutorial Tips & Help Entries

### Files involved

- `data/tutorial_tips.json` – defines tutorial tips and help entries
- `core/tutorial_system.py` – defines:
  - `TipTrigger` enum (events that can fire a tip)
  - `TutorialTip` and `HelpEntry` models
  - `TutorialManager` logic

You can safely add **new tutorial tips** and **help entries** by editing `data/tutorial_tips.json`. No Python changes are needed as long as you only use existing triggers.

### Tip triggers (`TipTrigger`)

In `core/tutorial_system.py`, `TipTrigger` includes (among others):

- `FIRST_BATTLE`
- `FIRST_SHOP_VISIT`
- `FIRST_LEVEL_UP`
- `FIRST_STATUS_EFFECT`
- `FIRST_PARTY_MEMBER`
- `FIRST_QUEST_ACCEPTED`
- `FIRST_ITEM_PICKUP`
- `FIRST_EQUIPMENT_CHANGE`
- `FIRST_SKILL_UNLOCK`
- `FIRST_CRAFTING`
- `FIRST_SAVE`
- `FIRST_DEATH`
- `LOW_HP_WARNING`
- `LOW_SP_WARNING`
- `ENTERED_DUNGEON`
- `ENTERED_TOWN`
- `NIGHT_TIME_FIRST`
- `SHOP_CLOSED`
- `FIRST_FISHING_SPOT`
- `FIRST_FISH_CAUGHT`
- `FIRST_LEGENDARY_FISH`
- `FIRST_GAMBLING`
- `FIRST_GAMBLING_WIN`
- `FIRST_GAMBLING_LOSS`
- `FIRST_ARENA_VISIT`
- `FIRST_ARENA_BET`
- `FIRST_DUNGEON_PUZZLE`
- `FIRST_PUZZLE_SOLVED`
- `FIRST_BRAIN_TEASER`
- `POST_GAME_START`
- `NEAR_COMPLETION`

In `data/tutorial_tips.json`, each tip’s `trigger` field must be one of these names **exactly** (as a string).

### Tutorial tips (`tips` array)

Each tip entry in `data/tutorial_tips.json` looks like:

```json
{
  "tip_id": "fishing_intro",
  "trigger": "FIRST_FISHING_SPOT",
  "title": "Fishing Available",
  "content": "You found a fishing spot! Press ENTER to cast your line...",
  "priority": 7,
  "category": "activities",
  "requires_tips": []
}
```

#### Fields

- **`tip_id`**:
  - Unique ID for this tip
- **`trigger`**:
  - One of the `TipTrigger` names (string)
- **`title`**:
  - Shown in the tip popup
- **`content`**:
  - The text body of the tip
- **`priority`** (optional, default 5):
  - 1–10; higher shows before lower if multiple tips are pending
- **`category`** (optional, default `"general"`):
  - Used to group tips in the help overlay
- **`requires_tips`** (optional, list of `tip_id`s):
  - This tip will only be shown if all listed tips have already been seen

#### Example: adding a new fishing-related tip

Suppose you want an extra tip that only appears after the basic fishing intro:

```json
{
  "tip_id": "fishing_spot_variants",
  "trigger": "FIRST_FISH_CAUGHT",
  "title": "Try Different Fishing Spots",
  "content": "Different fishing spots have different fish pools and rarities. Try ponds, streams, and magical springs to discover them all.",
  "priority": 5,
  "category": "activities",
  "requires_tips": ["fishing_intro"]
}
```

Checklist:

- `tip_id` is unique
- `trigger` matches a `TipTrigger` name exactly
- `requires_tips` entries are existing `tip_id`s

### Help entries (`help_entries` array)

Below the tips, `help_entries` define static help pages shown in the Help/Controls menus.

Example:

```json
{
  "entry_id": "help_gambling",
  "title": "Gambling Guide",
  "content": "Blackjack: Get close to 21 without going over. Dice: Guess high (8+) or low (6-)...",
  "category": "Activities",
  "order": 3
}
```

#### Fields

- **`entry_id`**:
  - Unique ID for the help entry
- **`title`**:
  - Shown in the help list
- **`content`**:
  - Multi-line text body; `\n` creates new lines
- **`category`**:
  - Group name in the help menu (e.g., `Controls`, `Activities`, `Combat`, `Gameplay`)
- **`order`**:
  - Integer; entries within a category are sorted by this

#### Example: adding a detailed gambling help entry

```json
{
  "entry_id": "help_gambling_advanced",
  "title": "Gambling – Advanced Tips",
  "content": "Blackjack: Stand on strong hands and avoid chasing losses.\nDice: Remember that totals around 7 are most common.\nSlots: Higher payouts come with lower odds.\nCups: Watch the shuffles carefully before guessing.",
  "category": "Activities",
  "order": 5
}
```

Checklist:

- `entry_id` is unique
- `category` groups entries logically
- `order` places the new entry where you want it within that category

---

## Testing & Troubleshooting

### Quick checklist after content changes

1. **Validate JSON syntax**
   - A single missing comma or quote will break loading
   - You can run:
     - `python -m json.tool data/fishing.json` (or another file)
   - Or use any online JSON validator
2. **Run the game**
   - Use the project’s virtual environment:
     - `.venv/bin/python3 text_adventure_mini_game.py`
   - Go to the relevant area/NPC:
     - Fishing: visit the map with your new spot
     - Gambling: talk to your gambler NPC and pick the new choice
     - Arena: visit the arena and check fighters/matches
     - NPC schedules: rest or advance time and verify NPC positions and shop hours
     - Tutorial tips: perform the action (e.g., first fishing spot) and confirm the new tip appears

### Common problems and how to fix them

- **Game crashes or logs an error about JSON**
  - Likely a syntax error (missing comma, extra comma, unquoted string)
  - Validate the JSON file you just edited

- **New fish never appears**
  - Check:
    - `fish_id` is listed in at least one spot’s `fish_pool`
    - `water_types` includes the spot’s `water_type`
    - `time_periods` includes the current time-of-day (or is empty)
    - `rarity_modifiers` aren’t accidentally zeroing out its rarity

- **Fishing spot can’t be used**
  - Confirm:
    - `map_id`, `x`, `y` line up with a water tile
    - There is at least one valid fish in `fish_pool` for that time and water type

- **Gambling choice does nothing**
  - Check:
    - `set_flag` matches one of `_start_blackjack`, `_start_dice`, `_start_slots`, `_start_cups`
    - There are no typos
    - `next_id` is `null` if the game expects to transition directly into the mini-game

- **Arena fighter never appears**
  - Confirm:
    - Fighter is listed under `fighters` with a unique `fighter_id`
    - There are at least two fighters so `generate_matches` can pair them
    - The arena is being opened (dialogue with `_open_arena`)

- **NPC never moves to new location**
  - Check:
    - `npc_id` in `data/npc_schedules.json` matches the entity’s ID
    - `time_periods` strings are valid and include the current world time
    - `map_id` is valid and the coordinates are inside the map

- **Shop appears closed at the wrong times**
  - Confirm:
    - `shop_available` is set to `true` for the times you want the shop open
    - `alternative_dialogue_id` is only set on entries where the shop is closed
    - The alternative dialogue ID exists in `data/dialogue.json`

- **Tutorial tip doesn’t show**
  - Check:
    - `tip_id` is unique
    - `trigger` string exactly matches a `TipTrigger` name
    - Any `requires_tips` entries are `tip_id`s that the player has actually seen before
    - Global tips are not disabled in saves (this is usually only a problem for existing save files)

By following this guide and the examples above, you can safely create new fishing spots and fish, add gambling hooks to dialogue, expand the arena roster, design NPC schedules, and write new tutorial tips and help pages without touching Python code. Always make small changes, test them, and iterate.

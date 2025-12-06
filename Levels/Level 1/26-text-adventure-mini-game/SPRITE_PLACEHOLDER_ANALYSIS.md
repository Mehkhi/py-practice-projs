# Sprite Placeholder Analysis

## Summary

This document identifies all sprites that are currently using the character-shaped placeholder system when they should have proper icon/UI sprites instead.

## The Problem

The placeholder system (`make_placeholder()` in `engine/assets/cache_utils.py`) generates **character-shaped sprites** (oval body + circular head) for any missing sprite. This is appropriate for missing character/enemy sprites, but **inappropriate** for UI elements, icons, and other non-character sprites.

## Fixed Sprites

### ✅ `hint_button` / `help_icon` / `question_mark`
- **Location**: `engine/ui/hint_button.py` (lines 52-54)
- **Status**: ✅ **FIXED** - Now has proper gold question mark icon sprite
- **What was there**: Character placeholder (oval body + head)
- **What should be there**: Question mark icon (now implemented)

### ✅ Puzzle Tiles (CRITICAL FIX)
- **Location**: `data/puzzles.json` - Used in cave/castle puzzle mini-games
- **Status**: ✅ **FIXED** - All puzzle tiles now have proper sprites
- **What was there**: Character placeholders making puzzles unplayable
- **What should be there**: Proper tile sprites (now implemented)

#### Fixed Puzzle Sprites:
1. **`puzzle_block`** - Pushable stone blocks
   - **Appearance**: Stone block with 3D depth and texture lines
   - **Used in**: Block pushing puzzles

2. **`pressure_plate`** - Floor plates that activate when stepped on
   - **Appearance**: Metal plate with gold center indicator
   - **Used in**: Block puzzles (blocks activate plates to open doors)

3. **`switch`** - Toggle switches/buttons
   - **Appearance**: Gold circular button on stone base
   - **Used in**: Sequence puzzles (activate switches in order)

4. **`reset_switch`** - Reset switches for puzzles
   - **Appearance**: Red circular button with white X symbol
   - **Used in**: All puzzles (resets puzzle to starting state)

5. **`teleporter`** - Teleport pads/portals
   - **Appearance**: Cyan energy portal with swirl pattern
   - **Used in**: Teleporter puzzles (move blocks through portals)

6. **`torch_holder`** - Torch holders
   - **Appearance**: Metal holder with U-shaped top
   - **Used in**: Torch lighting puzzles

## Summary of All Fixes

### Critical Puzzle Sprites (FIXED ✅)
All puzzle tiles in caves/castles were showing character placeholders, making puzzles completely unplayable. All 6 puzzle sprites have been created:

- ✅ `puzzle_block` - Stone pushable blocks
- ✅ `pressure_plate` - Floor activation plates
- ✅ `switch` - Gold toggle switches
- ✅ `reset_switch` - Red reset switches with X symbol
- ✅ `teleporter` - Cyan energy portal pads
- ✅ `torch_holder` - Metal torch holders

**Impact**: Puzzles in caves and castles are now playable with proper visual tiles!

## Sprites That Need Proper Icons (Remaining)

### 1. Achievement Category Icons
**Location**: `data/achievements.json` (category definitions)

These are referenced in the JSON but may not be actively loaded. If they are loaded, they would show character placeholders:

- `achievement_story` - Should be: Story/book icon
- `achievement_combat` - Should be: Sword/crossed swords icon
- `achievement_explore` - Should be: Map/compass icon
- `achievement_activity` - Should be: Activity/game controller icon
- `achievement_challenge` - Should be: Trophy/challenge icon
- `achievement_secret` - Should be: Lock/key/secret icon

**Note**: These may not be actively used. The achievement popup (`engine/achievement_popup.py`) draws trophy symbols procedurally rather than loading sprites. However, if any code tries to load these category icons, they would show character placeholders.

### 2. Item Icons (Mostly OK)
**Location**: `data/items.json`

- Most items use `item_default` which **exists** ✅
- One item uses `icon_health_potion` which **exists** ✅
- **Status**: No issues found here

### 3. Other Potential Issues

Based on the sprite manifest, these sprites are **requested but missing** (would use character placeholders):

#### UI/Icon Category (Priority: High)
- None currently identified (all UI sprites exist: `ui_panel`, `ui_cursor`, `icon_health_potion`)

#### Other Category (May need icons instead of character placeholders)
- `icon_health_potion` - ✅ **EXISTS** (proper icon)
- Other "other" category sprites are tiles/environmental, not icons

## Recommendations

### High Priority
1. **Verify achievement category icons**: Check if `achievement_story`, `achievement_combat`, etc. are actually loaded anywhere. If they are, create proper icon sprites for them.

### Medium Priority
2. **Audit sprite loading**: Search codebase for any other `get_image()` calls that might be loading UI/icon sprites that don't exist.

### Low Priority
3. **Consider placeholder variants**: The placeholder system could be enhanced to detect sprite naming patterns (e.g., `icon_*`, `ui_*`, `achievement_*`) and generate appropriate icon placeholders instead of character shapes.

## How to Check for More Issues

Run this command to find all `get_image()` calls:
```bash
grep -r "get_image" engine/ --include="*.py" | grep -E "(icon|ui|achievement|hint|help)"
```

## Files Modified

- `tools/generate_sprites.py` - Added `hint_button` and `help_icon` sprite generation
- `assets/sprites/hint_button.png` - Created (gold question mark icon)
- `assets/sprites/help_icon.png` - Created (gold question mark icon)

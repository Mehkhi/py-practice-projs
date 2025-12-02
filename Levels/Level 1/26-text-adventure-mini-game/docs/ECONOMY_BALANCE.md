# Economy Balance Documentation

This document describes the game's economic design, progression pacing, and balance guidelines.

## Overview

The economy is designed around a smooth progression curve where:
1. **Starter equipment** is immediately affordable or provided
2. **Early-game upgrades** become available after completing initial quests
3. **Mid-tier equipment** is attainable by mid-game (after ~3 main quests)
4. **Legendary items** are achievable endgame rewards

## Gold Sources

### Main Quest Chain (2,100g total)
| Quest | Reward | Cumulative |
|-------|--------|------------|
| A Hero's Beginning | 50g | 50g |
| Into the Darkness | 150g | 200g |
| Secrets of the Garden | 200g | 400g |
| Echoes of the Ancients | 300g | 700g |
| The Heart of Darkness | 400g | 1,100g |
| The Final Confrontation | 1,000g | 2,100g |

### Side Quests (~3,265g total)
- 21 side quests available
- Categories: side (3,190g), bounty (75g)
- Average reward: ~155g per quest

### Encounters (~2,385g total)
| Difficulty | Count | Total Gold | Avg/Encounter |
|------------|-------|------------|---------------|
| Easy | 1 | 10g | 10g |
| Normal | 6 | 190g | ~32g |
| Hard | 13 | 805g | ~62g |
| Elite | 7 | 670g | ~96g |
| Boss | 4 | 710g | ~178g |

### Total Available Gold: ~7,750g

## Equipment Tiers

### Starter Tier (0-15g)
Class-specific starting weapons at 5g each:
- Rusty Sword, Apprentice Wand, Worn Dagger, Holy Mace
- Hunter's Shortbow, Brutal Hatchet, Blessed Blade, Bone Staff
- Wrapped Fists, Traveler's Lute, Spirit Orb, Iron Lance
- Basic Sword (10g) - generic upgrade

### Early Tier (15-50g)
- Leather Armor (15g) - +3 defense
- Ring of Swiftness (30g) - +2 speed, +1 luck
- Apprentice Staff (40g) - +4 magic

### Mid Tier (50-200g)
Primary upgrades available after 3 main quests (~400g):
- Iron Sword (50g) - +4 attack
- Class-specific weapons at 75g:
  - Warrior's Blade, Shadow Dagger, Hunter's Bow
  - Berserker Axe, Arcane Focus, Holy Symbol
  - Necromancer's Tome, Monk's Wraps, Bard's Lyre, Summoner's Crystal
- Knight's Armor (75g), Paladin's Shield (75g)

### Legendary Tier (500g+)
- Legendary Blade (1,000g) - +15 attack, +5 defense, +5 magic, +3 speed

## Shop Distribution

| Location | Type | Notable Stock |
|----------|------|---------------|
| Village General | General | Health/SP potions, Torch |
| Village Blacksmith | Blacksmith | Basic Sword, Leather Armor, Starter weapons |
| Steel & Edge (City) | Weapon | Mid-tier weapons (75g each) |
| Guardian's Armory (City) | Armor | Mid-tier armor, accessories |
| Mystic Brews (City) | Potion | Potions, Elixirs |
| Arcane Emporium (Mage Tower) | Magic | Staves, magic weapons |
| Wanderer's Wares | Traveling | Mixed stock, Ring of Swiftness |
| Helena's (Ironhold) | General | Hi-Potions, Phoenix Down |
| Black Market (Nighthaven) | Special | Shadow Dagger, tonics, Smoke Bombs |

## Crafting Economy

Crafting provides an alternative path to equipment. Categories:
- **Basic** (Level 1): Torch, Smoke Bomb, Bowstring
- **Alchemy** (Level 1-4): Health/SP potions, status cures, tonics
- **Smithing** (Level 1-5): Weapons, armor from ore/materials
- **Enchanting** (Level 2-5): Magic items, accessories

### Cost Comparison (Buy vs Craft)
| Item | Buy Price | Craft Materials |
|------|-----------|-----------------|
| Health Potion | 20g | 2 Herb (10g) + 1 Vial (3g) = 13g |
| Iron Sword | 50g | 4 Iron Ore (40g) + materials = ~50g |
| Warrior's Blade | 75g | 5 Iron Ore + 2 Steel + 2 Leather |

Crafting is generally cost-neutral but requires gathering materials from exploration.

## Progression Checkpoints

### After Tutorial (~50g)
- Can afford: All starter weapons, some potions
- Cannot afford: Leather Armor (15g) - requires additional encounters

### After 3 Main Quests (~400g)
- Can afford: All starter/early items, most mid-tier equipment
- Recommended: One mid-tier weapon + Leather Armor

### After All Main Quests (~2,100g)
- Can afford: All mid-tier equipment, Legendary Blade (with savings)
- Should have: Full mid-tier loadout minimum

### 100% Completion (~7,750g)
- Can afford: Multiple Legendary items, full party equipped
- Excess gold for consumables

## Balance Guidelines

### Gold Rewards
- **Easy encounters**: 10-25g (enough for 1-2 potions)
- **Normal encounters**: 25-50g (partial equipment upgrade)
- **Hard encounters**: 50-75g (contributes to mid-tier gear)
- **Elite encounters**: 75-125g (significant progress)
- **Boss encounters**: 150-250g (major milestone reward)

### Quest Rewards
- **Tutorial/Early quests**: 25-75g (starter equipment range)
- **Mid-game quests**: 100-200g (mid-tier equipment)
- **Late-game quests**: 250-500g (legendary tier contribution)
- **Final quest**: 500-1000g (celebration reward)

### Item Pricing
- Price should reflect stat total and granted skills
- Rule of thumb: ~10g per stat point for equipment
- Consumables: ~0.4g per HP healed, ~0.5g per SP restored
- Status cures: 15-25g (accessible emergency items)
- Revival items: 150-300g (significant but not prohibitive)

## Known Issues

### Addressed
- Basic Sword renamed from "Iron Sword" to avoid confusion with the 50g Iron Sword

### Monitoring
- Side quest gold may exceed main quest gold (intentional for completionists)
- Crafting costs roughly equal shop prices (intentional balance)

## Running Analysis Tools

Generate fresh economy analysis:
```bash
.venv/bin/python3 tools/analyze_economy.py
```

Generate difficulty curve analysis:
```bash
.venv/bin/python3 tools/analyze_difficulty_curve.py
```

Reports are saved to `ECONOMY_ANALYSIS.md` and `DIFFICULTY_CURVE_ANALYSIS.md`.

================================================================================
DIFFICULTY CURVE ANALYSIS REPORT
================================================================================

ENCOUNTER DIFFICULTY DISTRIBUTION
--------------------------------------------------------------------------------
Total Encounters: 31

By Average Enemy Level:
  Level 1: 2 encounters
    - tutorial_battle: 1 enemies, difficulty easy
    - forest_slimes: 1 enemies, difficulty normal
  Level 2: 2 encounters
    - forest_wolves: 2 enemies, difficulty hard
    - werewolf_pack: 2 enemies, difficulty normal
  Level 3: 3 encounters
    - cave_goblins: 1 enemies, difficulty normal
    - poison_mushrooms: 1 enemies, difficulty normal
    - mountain_bats: 3 enemies, difficulty hard
  Level 4: 5 encounters
    - goblin_warband: 4 enemies, difficulty elite
    - bandit_ambush: 2 enemies, difficulty hard
    - swamp_spiders: 2 enemies, difficulty hard
    - harpy_flock: 2 enemies, difficulty normal
    - river_creature: 1 enemies, difficulty hard
  Level 5: 4 encounters
    - ice_elementals: 1 enemies, difficulty hard
    - ruins_skeletons: 2 enemies, difficulty normal
    - orc_raiders: 2 enemies, difficulty hard
    - lizardman_tribe: 2 enemies, difficulty hard
  Level 6: 7 encounters
    - swamp_witch: 1 enemies, difficulty elite
    - haunted_spirits: 1 enemies, difficulty hard
    - fire_elementals: 1 enemies, difficulty hard
    - mimic_trap: 1 enemies, difficulty hard
    - demon_invasion: 2 enemies, difficulty elite
    ... and 2 more
  Level 7: 3 encounters
    - mountain_troll: 1 enemies, difficulty elite
    - stone_golems: 1 enemies, difficulty elite
    - wraith_haunting: 1 enemies, difficulty hard
  Level 8: 2 encounters
    - final_boss: 1 enemies, difficulty boss
    - vampire_coven: 1 enemies, difficulty elite
  Level 9: 3 encounters
    - ruins_guardian: 1 enemies, difficulty boss
    - cyclops_den: 1 enemies, difficulty boss
    - dark_knight_duel: 1 enemies, difficulty boss

By Difficulty Tier:
  easy: 1 encounters
  normal: 6 encounters
  hard: 13 encounters
  elite: 7 encounters
  boss: 4 encounters

MAP GATING FLAGS
--------------------------------------------------------------------------------
ancient_ruins:
  Requires: ruins_guardian_defeated, dark_knight_defeated
dark_cave:
  Requires: cave_cleared
demon_fortress:
  Requires: demon_lord_defeated
desert_oasis:
  Requires: desert_bandits_cleared
forest_path:
  Requires: werewolves_defeated, forest_slimes_cleared, cave_cleared, forest_wolves_cleared
frozen_tundra:
  Requires: ice_queen_defeated
haunted_crypt:
  Requires: crypt_cleared
mountain_pass:
  Requires: cyclops_defeated, troll_defeated
murky_swamp:
  Requires: swamp_witch_defeated
secret_garden:
  Requires: magic_crystal_found
volcanic_crater:
  Requires: fire_lord_defeated

MAIN QUEST PROGRESSION PATH
--------------------------------------------------------------------------------
A Hero's Beginning:
Into the Darkness:
  Recommended Level: 7
  Related Encounters: goblin_warband, cave_goblins
Secrets of the Garden:
Echoes of the Ancients:
The Heart of Darkness:
The Final Confrontation:

RECOMMENDED LEVEL BY AREA
--------------------------------------------------------------------------------
ancient_ruins: Level 5-10 (avg: 8)
dark_cave: Level 3-7 (avg: 5)
demon_fortress: Level 8-10 (avg: 8)
desert_oasis: Level 5-7 (avg: 5)
forest_path: Level 1-3 (avg: 2)
frozen_tundra: Level 2-9 (avg: 5)
haunted_crypt: Level 5-10 (avg: 7)
mountain_pass: Level 4-10 (avg: 6)
murky_swamp: Level 3-8 (avg: 5)
sunharbor_city: Level 7-7 (avg: 7)
treasure_chamber: Level 5-10 (avg: 8)
volcanic_crater: Level 7-8 (avg: 7)

ISSUES FOUND
--------------------------------------------------------------------------------
⚠️  Map 'ancient_ruins' requires 'ruins_guardian_defeated' (set by level 9 encounter), but contains 'stone_golems' at level 7 (too easy for gated content)
⚠️  Map 'ancient_ruins' requires 'ruins_guardian_defeated' (set by level 9 encounter), but contains 'ruins_skeletons' at level 5 (too easy for gated content)
⚠️  Map 'ancient_ruins' requires 'ruins_guardian_defeated' (set by level 9 encounter), but contains 'haunted_spirits' at level 6 (too easy for gated content)
⚠️  Map 'ancient_ruins' requires 'ruins_guardian_defeated' (set by level 9 encounter), but contains 'fire_elementals' at level 6 (too easy for gated content)
⚠️  Map 'ancient_ruins' requires 'ruins_guardian_defeated' (set by level 9 encounter), but contains 'wraith_haunting' at level 7 (too easy for gated content)
⚠️  Map 'ancient_ruins' requires 'ruins_guardian_defeated' (set by level 9 encounter), but contains 'demon_invasion' at level 6 (too easy for gated content)
⚠️  Map 'ancient_ruins' requires 'ruins_guardian_defeated' (set by level 9 encounter), but contains 'necromancer_lair' at level 6 (too easy for gated content)
⚠️  Map 'ancient_ruins' requires 'dark_knight_defeated' (set by level 9 encounter), but contains 'stone_golems' at level 7 (too easy for gated content)
⚠️  Map 'ancient_ruins' requires 'dark_knight_defeated' (set by level 9 encounter), but contains 'ruins_skeletons' at level 5 (too easy for gated content)
⚠️  Map 'ancient_ruins' requires 'dark_knight_defeated' (set by level 9 encounter), but contains 'haunted_spirits' at level 6 (too easy for gated content)
⚠️  Map 'ancient_ruins' requires 'dark_knight_defeated' (set by level 9 encounter), but contains 'fire_elementals' at level 6 (too easy for gated content)
⚠️  Map 'ancient_ruins' requires 'dark_knight_defeated' (set by level 9 encounter), but contains 'wraith_haunting' at level 7 (too easy for gated content)
⚠️  Map 'ancient_ruins' requires 'dark_knight_defeated' (set by level 9 encounter), but contains 'demon_invasion' at level 6 (too easy for gated content)
⚠️  Map 'ancient_ruins' requires 'dark_knight_defeated' (set by level 9 encounter), but contains 'necromancer_lair' at level 6 (too easy for gated content)
⚠️  Map 'forest_path' requires 'cave_cleared' (set by level 3 encounter), but contains 'forest_slimes' at level 1 (too easy for gated content)
⚠️  Map 'mountain_pass' requires 'cyclops_defeated' (set by level 9 encounter), but contains 'ice_elementals' at level 5 (too easy for gated content)
⚠️  Map 'mountain_pass' requires 'cyclops_defeated' (set by level 9 encounter), but contains 'mountain_bats' at level 3 (too easy for gated content)
⚠️  Map 'mountain_pass' requires 'cyclops_defeated' (set by level 9 encounter), but contains 'mountain_troll' at level 7 (too easy for gated content)
⚠️  Map 'mountain_pass' requires 'cyclops_defeated' (set by level 9 encounter), but contains 'orc_raiders' at level 5 (too easy for gated content)
⚠️  Map 'mountain_pass' requires 'cyclops_defeated' (set by level 9 encounter), but contains 'harpy_flock' at level 4 (too easy for gated content)
⚠️  Map 'mountain_pass' requires 'troll_defeated' (set by level 7 encounter), but contains 'ice_elementals' at level 5 (too easy for gated content)
⚠️  Map 'mountain_pass' requires 'troll_defeated' (set by level 7 encounter), but contains 'mountain_bats' at level 3 (too easy for gated content)
⚠️  Map 'mountain_pass' requires 'troll_defeated' (set by level 7 encounter), but contains 'orc_raiders' at level 5 (too easy for gated content)
⚠️  Map 'mountain_pass' requires 'troll_defeated' (set by level 7 encounter), but contains 'harpy_flock' at level 4 (too easy for gated content)
⚠️  Map 'murky_swamp' requires 'swamp_witch_defeated' (set by level 6 encounter), but contains 'swamp_spiders' at level 4 (too easy for gated content)
⚠️  Map 'murky_swamp' requires 'swamp_witch_defeated' (set by level 6 encounter), but contains 'poison_mushrooms' at level 3 (too easy for gated content)

RECOMMENDATIONS
--------------------------------------------------------------------------------

================================================================================

import unittest

from core.items import Inventory
from core.gambling import GamblingManager
from core.arena import ArenaManager, ArenaFighter, ArenaMatch
from core.challenge_dungeons import (
    ChallengeDungeon,
    ChallengeDungeonManager,
    ChallengeModifier,
    ChallengeTier,
)


class WorldStub:
    def __init__(self, gold: int = 0):
        self.flags = {"gold": gold}

    def get_flag(self, name: str, default=0):
        return self.flags.get(name, default)

    def set_flag(self, name: str, value):
        self.flags[name] = value


class TestInventoryValidation(unittest.TestCase):
    def test_add_rejects_non_positive_or_invalid(self):
        inv = Inventory()
        self.assertEqual(inv.add("potion", -5), 0)
        self.assertEqual(inv.add("potion", 0), 0)
        self.assertEqual(inv.add("potion", "not-a-number"), 0)
        self.assertNotIn("potion", inv.items)

    def test_remove_rejects_non_positive_or_invalid(self):
        inv = Inventory()
        inv.items["potion"] = 3
        self.assertFalse(inv.remove("potion", 0))
        self.assertFalse(inv.remove("potion", -1))
        self.assertFalse(inv.remove("potion", "bad"))
        self.assertEqual(inv.items["potion"], 3)

    def test_has_rejects_non_positive_or_invalid(self):
        inv = Inventory()
        inv.items["potion"] = 3
        self.assertFalse(inv.has("potion", 0))
        self.assertFalse(inv.has("potion", -2))
        self.assertFalse(inv.has("potion", "bad"))
        self.assertTrue(inv.has("potion", 2))


class TestBettingGuards(unittest.TestCase):
    def test_gambling_rejects_non_positive_bets(self):
        manager = GamblingManager()
        world = WorldStub(100)
        self.assertFalse(manager.place_bet(-10, world))
        self.assertFalse(manager.place_bet(0, world))
        self.assertEqual(world.get_flag("gold"), 100)
        self.assertEqual(manager.current_bet, 0)

        self.assertTrue(manager.place_bet(10, world))
        self.assertEqual(world.get_flag("gold"), 90)
        self.assertEqual(manager.current_bet, 10)

    def test_arena_rejects_non_positive_bets(self):
        fighters = {
            "a": ArenaFighter("a", "A", "sprite_a", {"hp": 10, "attack": 5, "defense": 2, "speed": 3}, [], 2.0),
            "b": ArenaFighter("b", "B", "sprite_b", {"hp": 12, "attack": 4, "defense": 3, "speed": 2}, [], 2.0),
        }
        manager = ArenaManager(fighters, {})
        match = ArenaMatch("m1", fighters["a"], fighters["b"])
        world = WorldStub(50)

        self.assertIsNone(manager.place_bet(match, "a", -5, world))
        self.assertIsNone(manager.place_bet(match, "a", 0, world))
        self.assertEqual(world.get_flag("gold"), 50)

        bet = manager.place_bet(match, "a", 10, world)
        self.assertIsNotNone(bet)
        self.assertEqual(world.get_flag("gold"), 40)


class TestChallengeModifierMerging(unittest.TestCase):
    def test_modifiers_merge_multiplicatively_and_dedupe_hazards(self):
        modifiers = {
            "stat1": ChallengeModifier(
                modifier_id="stat1",
                name="Stat Boost",
                description="",
                effect_type="stat_mod",
                effect_data={
                    "enemy_stat_multiplier": 1.5,
                    "enemy_hp_multiplier": 2.0,
                    "enemy_lifesteal": 0.1,
                },
            ),
            "stat2": ChallengeModifier(
                modifier_id="stat2",
                name="More Stats",
                description="",
                effect_type="stat_mod",
                effect_data={
                    "enemy_stat_multiplier": 1.2,
                    "enemy_damage_multiplier": 1.3,
                    "enemy_speed_multiplier": 1.1,
                    "enemy_lifesteal": 0.2,
                },
            ),
            "rest": ChallengeModifier(
                modifier_id="rest",
                name="Restrictions",
                description="",
                effect_type="restriction",
                effect_data={"no_healing": True},
            ),
            "haz1": ChallengeModifier(
                modifier_id="haz1",
                name="Hazards",
                description="",
                effect_type="hazard",
                effect_data={"hazards": ["spikes", "poison"]},
            ),
            "haz2": ChallengeModifier(
                modifier_id="haz2",
                name="More Hazards",
                description="",
                effect_type="hazard",
                effect_data={"hazards": ["spikes", "ice"], "stat_scramble": True},
            ),
        }

        dungeons = {
            "trial": ChallengeDungeon(
                dungeon_id="trial",
                name="Trial",
                description="",
                tier=ChallengeTier.APPRENTICE,
                required_level=1,
                map_ids=["map"],
                entry_map_id="map",
                entry_x=0,
                entry_y=0,
                modifiers=["stat1", "stat2", "rest", "haz1", "haz2"],
                rewards={},
                first_clear_rewards={},
            )
        }

        manager = ChallengeDungeonManager(dungeons, modifiers)
        manager.active_dungeon_id = "trial"
        battle_ctx = {}

        result = manager.apply_modifiers_to_battle(battle_ctx)

        self.assertAlmostEqual(result["enemy_stat_multiplier"], 1.8)
        self.assertAlmostEqual(result["enemy_hp_multiplier"], 2.0)
        self.assertAlmostEqual(result["enemy_damage_multiplier"], 1.3)
        self.assertAlmostEqual(result["enemy_speed_multiplier"], 1.1)
        self.assertAlmostEqual(result["enemy_lifesteal"], 0.2)
        self.assertTrue(result["healing_disabled"])
        self.assertTrue(result["stat_scramble"])
        self.assertEqual(result.get("hazards"), ["spikes", "poison", "ice"])


if __name__ == "__main__":
    unittest.main()

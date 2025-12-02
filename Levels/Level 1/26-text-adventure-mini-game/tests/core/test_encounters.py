"""Unit tests for core/encounters.py - Encounter factory and loading."""

import unittest
import os
import json
import tempfile
from typing import Dict, Any

from core.encounters import create_encounter_from_data, load_encounters_from_json
from core.entities import Enemy
from core.stats import Stats


class TestLoadEncountersFromJson(unittest.TestCase):
    """Tests for load_encounters_from_json function."""

    def test_load_encounters_from_default_path(self):
        """Loading from default path returns encounter data."""
        encounters = load_encounters_from_json()
        self.assertIsInstance(encounters, dict)
        # Should have at least the tutorial encounter
        self.assertIn("tutorial_battle", encounters)

    def test_load_encounters_from_nonexistent_file(self):
        """Loading from nonexistent file returns empty dict."""
        encounters = load_encounters_from_json("nonexistent/path.json")
        self.assertEqual(encounters, {})

    def test_load_encounters_from_custom_path(self):
        """Loading from custom path with valid JSON works."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({
                "encounters": {
                    "test_encounter": {
                        "enemies": [{"id": "test", "name": "Test Enemy"}],
                        "rewards": {"exp": 10, "gold": 5}
                    }
                }
            }, f)
            temp_path = f.name

        try:
            encounters = load_encounters_from_json(temp_path)
            self.assertIn("test_encounter", encounters)
        finally:
            os.unlink(temp_path)

    def test_load_encounters_handles_missing_encounters_key(self):
        """Loading JSON without 'encounters' key returns empty dict."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"other_data": {}}, f)
            temp_path = f.name

        try:
            encounters = load_encounters_from_json(temp_path)
            self.assertEqual(encounters, {})
        finally:
            os.unlink(temp_path)


class TestCreateEncounterFromData(unittest.TestCase):
    """Tests for create_encounter_from_data factory function."""

    def test_returns_tuple_with_four_elements(self):
        """Factory returns (enemies, rewards, backdrop_id, ai_metadata) tuple."""
        encounters = {"test": {"enemies": [], "rewards": {}}}
        result = create_encounter_from_data("test", encounters)
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 4)

    def test_creates_enemy_from_encounter_data(self):
        """Factory creates Enemy instances from encounter data."""
        encounters = {
            "test": {
                "enemies": [{
                    "id": "goblin",
                    "name": "Goblin",
                    "sprite_id": "goblin",
                    "type": "humanoid",
                    "level": 2,
                    "difficulty": "normal",
                    "max_hp": 40,
                    "max_sp": 15,
                    "attack": 10,
                    "defense": 5,
                    "magic": 3,
                    "speed": 8,
                    "luck": 4
                }],
                "rewards": {"exp": 20, "gold": 10}
            }
        }
        enemies, rewards, backdrop_id, ai_metadata = create_encounter_from_data("test", encounters)

        self.assertEqual(len(enemies), 1)
        self.assertIsInstance(enemies[0], Enemy)
        self.assertEqual(enemies[0].entity_id, "goblin")
        self.assertEqual(enemies[0].name, "Goblin")

    def test_enemies_spawn_at_full_hp(self):
        """Enemies always spawn at full HP regardless of 'hp' field in JSON."""
        encounters = {
            "test": {
                "enemies": [{
                    "id": "test",
                    "name": "Test",
                    "level": 1,
                    "max_hp": 100,
                    "hp": 50,  # This should be ignored
                }],
                "rewards": {}
            }
        }
        enemies, _, _, _ = create_encounter_from_data("test", encounters)

        # HP should equal max_hp, not the 'hp' value from JSON
        self.assertEqual(enemies[0].stats.hp, enemies[0].stats.max_hp)

    def test_stat_scaling_by_level(self):
        """Enemy stats scale with level."""
        encounters = {
            "test_low": {
                "enemies": [{
                    "id": "e1", "name": "Low Level", "level": 1, "difficulty": "normal",
                    "max_hp": 100, "attack": 10
                }],
                "rewards": {}
            },
            "test_high": {
                "enemies": [{
                    "id": "e2", "name": "High Level", "level": 5, "difficulty": "normal",
                    "max_hp": 100, "attack": 10
                }],
                "rewards": {}
            }
        }
        enemies_low, _, _, _ = create_encounter_from_data("test_low", encounters)
        enemies_high, _, _, _ = create_encounter_from_data("test_high", encounters)

        # Higher level should have higher stats
        self.assertGreater(enemies_high[0].stats.max_hp, enemies_low[0].stats.max_hp)
        self.assertGreater(enemies_high[0].stats.attack, enemies_low[0].stats.attack)

    def test_stat_scaling_by_difficulty(self):
        """Enemy stats scale with difficulty."""
        encounters = {
            "test_easy": {
                "enemies": [{
                    "id": "e1", "name": "Easy", "level": 1, "difficulty": "easy",
                    "max_hp": 100, "attack": 10
                }],
                "rewards": {}
            },
            "test_boss": {
                "enemies": [{
                    "id": "e2", "name": "Boss", "level": 1, "difficulty": "boss",
                    "max_hp": 100, "attack": 10
                }],
                "rewards": {}
            }
        }
        enemies_easy, _, _, _ = create_encounter_from_data("test_easy", encounters)
        enemies_boss, _, _, _ = create_encounter_from_data("test_boss", encounters)

        # Boss difficulty should have higher stats
        self.assertGreater(enemies_boss[0].stats.max_hp, enemies_easy[0].stats.max_hp)
        self.assertGreater(enemies_boss[0].stats.attack, enemies_easy[0].stats.attack)

    def test_reward_calculation(self):
        """Rewards include exp and gold scaled by enemy level/difficulty."""
        encounters = {
            "test": {
                "enemies": [{
                    "id": "e1", "name": "Test", "level": 3, "difficulty": "hard"
                }],
                "rewards": {"exp": 50, "gold": 25, "items": {"potion": 1}, "flags": ["test_cleared"]}
            }
        }
        _, rewards, _, _ = create_encounter_from_data("test", encounters)

        self.assertIn("exp", rewards)
        self.assertIn("gold", rewards)
        self.assertIn("items", rewards)
        self.assertIn("flags", rewards)
        self.assertGreater(rewards["exp"], 0)
        self.assertGreater(rewards["gold"], 0)
        self.assertEqual(rewards["items"], {"potion": 1})
        self.assertEqual(rewards["flags"], ["test_cleared"])

    def test_backdrop_id_extraction(self):
        """Factory extracts backdrop_id from encounter data."""
        encounters = {
            "test": {
                "enemies": [{"id": "e1", "name": "Test"}],
                "rewards": {},
                "backdrop_id": "bg_dungeon"
            }
        }
        _, _, backdrop_id, _ = create_encounter_from_data("test", encounters)
        self.assertEqual(backdrop_id, "bg_dungeon")

    def test_backdrop_id_none_when_missing(self):
        """backdrop_id is None when not in encounter data."""
        encounters = {
            "test": {
                "enemies": [{"id": "e1", "name": "Test"}],
                "rewards": {}
            }
        }
        _, _, backdrop_id, _ = create_encounter_from_data("test", encounters)
        self.assertIsNone(backdrop_id)

    def test_ai_metadata_extraction(self):
        """Factory extracts AI metadata for post-BattleSystem setup."""
        ai_profile = {"rules": [{"action": {"type": "attack"}}]}
        encounters = {
            "test": {
                "enemies": [{
                    "id": "smart_enemy",
                    "name": "Smart Enemy",
                    "ai_profile": ai_profile,
                    "skills": ["fire_bolt", "heal"],
                    "items": {"health_potion": 2}
                }],
                "rewards": {}
            }
        }
        _, _, _, ai_metadata = create_encounter_from_data("test", encounters)

        self.assertEqual(len(ai_metadata), 1)
        self.assertEqual(ai_metadata[0]["enemy_index"], 0)
        self.assertEqual(ai_metadata[0]["ai_profile"], ai_profile)
        self.assertEqual(ai_metadata[0]["skills"], ["fire_bolt", "heal"])
        self.assertEqual(ai_metadata[0]["items"], {"health_potion": 2})
        self.assertEqual(ai_metadata[0]["enemy_id"], "smart_enemy")

    def test_multiple_enemies(self):
        """Factory handles encounters with multiple enemies."""
        encounters = {
            "test": {
                "enemies": [
                    {"id": "e1", "name": "Enemy 1", "level": 1},
                    {"id": "e2", "name": "Enemy 2", "level": 2},
                    {"id": "e3", "name": "Enemy 3", "level": 3}
                ],
                "rewards": {"exp": 30, "gold": 15}
            }
        }
        enemies, _, _, ai_metadata = create_encounter_from_data("test", encounters)

        self.assertEqual(len(enemies), 3)
        self.assertEqual(len(ai_metadata), 3)
        self.assertEqual(enemies[0].name, "Enemy 1")
        self.assertEqual(enemies[1].name, "Enemy 2")
        self.assertEqual(enemies[2].name, "Enemy 3")

    def test_spare_mechanics_propagation(self):
        """Factory propagates spare mechanics to Enemy instances."""
        spare_messages = {"low_hp": "The enemy looks tired...", "mercy": "You spared the enemy!"}
        encounters = {
            "test": {
                "enemies": [{
                    "id": "spareable_enemy",
                    "name": "Spareable",
                    "spareable": True,
                    "spare_threshold": 5,
                    "spare_hp_threshold": 25,
                    "spare_messages": spare_messages
                }],
                "rewards": {}
            }
        }
        enemies, _, _, _ = create_encounter_from_data("test", encounters)

        enemy = enemies[0]
        self.assertTrue(enemy.spareable)
        self.assertEqual(enemy.spare_threshold, 5)
        self.assertEqual(enemy.spare_hp_threshold, 25)
        self.assertEqual(enemy.spare_messages, spare_messages)

    def test_equipment_setup(self):
        """Factory sets up enemy equipment from data."""
        encounters = {
            "test": {
                "enemies": [{
                    "id": "armed_enemy",
                    "name": "Armed Enemy",
                    "equipment": {"weapon": "iron_sword", "armor": "leather_armor"}
                }],
                "rewards": {}
            }
        }
        enemies, _, _, _ = create_encounter_from_data("test", encounters)

        enemy = enemies[0]
        self.assertEqual(enemy.equipment.get("weapon"), "iron_sword")
        self.assertEqual(enemy.equipment.get("armor"), "leather_armor")
        self.assertIsNone(enemy.equipment.get("accessory"))

    def test_elemental_affinities(self):
        """Factory preserves weaknesses, resistances, immunities, and absorbs."""
        encounters = {
            "test": {
                "enemies": [{
                    "id": "elemental",
                    "name": "Elemental",
                    "weaknesses": ["ice"],
                    "resistances": ["fire"],
                    "immunities": ["poison"],
                    "absorbs": ["lightning"]
                }],
                "rewards": {}
            }
        }
        enemies, _, _, _ = create_encounter_from_data("test", encounters)

        stats = enemies[0].stats
        self.assertIn("ice", stats.weaknesses)
        self.assertIn("fire", stats.resistances)
        self.assertIn("poison", stats.immunities)
        self.assertIn("lightning", stats.absorbs)


class TestFallbackBehavior(unittest.TestCase):
    """Tests for fallback enemy creation when encounter is missing."""

    def test_fallback_enemy_on_missing_encounter_id(self):
        """Missing encounter ID creates a fallback enemy."""
        encounters = {}
        enemies, rewards, backdrop_id, ai_metadata = create_encounter_from_data("nonexistent", encounters)

        self.assertEqual(len(enemies), 1)
        self.assertEqual(enemies[0].name, "Slime")
        self.assertEqual(enemies[0].entity_id, "enemy_1")

    def test_fallback_enemy_on_none_encounters_data(self):
        """None encounters_data creates a fallback enemy."""
        enemies, _, _, _ = create_encounter_from_data("any_id", None)

        self.assertEqual(len(enemies), 1)
        self.assertEqual(enemies[0].name, "Slime")

    def test_tutorial_fallback_has_weaker_stats(self):
        """Tutorial fallback enemy has specifically weaker stats."""
        enemies_tutorial, _, _, _ = create_encounter_from_data("tutorial_battle", {})
        enemies_regular, _, _, _ = create_encounter_from_data("regular_battle", {})

        # Tutorial enemy should be weaker
        self.assertEqual(enemies_tutorial[0].name, "Practice Slime")
        self.assertEqual(enemies_regular[0].name, "Slime")
        self.assertLess(enemies_tutorial[0].stats.attack, enemies_regular[0].stats.attack)

    def test_fallback_rewards_empty_but_present(self):
        """Fallback returns empty but properly structured rewards."""
        _, rewards, _, _ = create_encounter_from_data("nonexistent", {})

        self.assertIn("items", rewards)
        self.assertIn("flags", rewards)
        self.assertEqual(rewards["items"], {})
        self.assertEqual(rewards["flags"], [])


class TestSkillsHandling(unittest.TestCase):
    """Tests for skills and base_skills handling."""

    def test_skills_list_copied(self):
        """Skills are copied to prevent mutation of source data."""
        encounters = {
            "test": {
                "enemies": [{
                    "id": "e1", "name": "Test",
                    "skills": ["skill1", "skill2"],
                    "base_skills": ["base1"]
                }],
                "rewards": {}
            }
        }
        enemies, _, _, _ = create_encounter_from_data("test", encounters)

        # Modify the enemy's skills
        enemies[0].skills.append("new_skill")

        # Re-create encounter - original should be unchanged
        enemies2, _, _, _ = create_encounter_from_data("test", encounters)
        self.assertNotIn("new_skill", enemies2[0].skills)

    def test_empty_skills_default(self):
        """Missing skills fields default to empty lists."""
        encounters = {
            "test": {
                "enemies": [{"id": "e1", "name": "Test"}],
                "rewards": {}
            }
        }
        enemies, _, _, _ = create_encounter_from_data("test", encounters)

        self.assertEqual(enemies[0].skills, [])
        self.assertEqual(enemies[0].base_skills, [])


class TestDefaultValues(unittest.TestCase):
    """Tests for default value handling."""

    def test_default_stat_values(self):
        """Enemy with missing stats gets default values."""
        encounters = {
            "test": {
                "enemies": [{"id": "minimal", "name": "Minimal Enemy"}],
                "rewards": {}
            }
        }
        enemies, _, _, _ = create_encounter_from_data("test", encounters)

        stats = enemies[0].stats
        # Check defaults are applied (scaled by level 1, normal difficulty = x1)
        self.assertEqual(stats.max_hp, 50)  # Default base
        self.assertEqual(stats.max_sp, 20)  # Default base
        self.assertEqual(stats.attack, 8)  # Default base
        self.assertEqual(stats.defense, 3)  # Default base
        self.assertEqual(stats.magic, 5)  # Default base
        self.assertEqual(stats.speed, 7)  # Default base
        self.assertEqual(stats.luck, 3)  # Default base

    def test_default_level_and_difficulty(self):
        """Enemy with missing level/difficulty gets defaults."""
        encounters = {
            "test": {
                "enemies": [{"id": "e1", "name": "Test", "max_hp": 100}],
                "rewards": {}
            }
        }
        enemies, _, _, _ = create_encounter_from_data("test", encounters)

        # Level 1, normal difficulty = base stats unchanged
        self.assertEqual(enemies[0].level, 1)
        self.assertEqual(enemies[0].difficulty, "normal")

    def test_default_enemy_type(self):
        """Enemy with missing type gets 'generic' default."""
        encounters = {
            "test": {
                "enemies": [{"id": "e1", "name": "Test"}],
                "rewards": {}
            }
        }
        enemies, _, _, _ = create_encounter_from_data("test", encounters)

        self.assertEqual(enemies[0].enemy_type, "generic")


if __name__ == "__main__":
    unittest.main()

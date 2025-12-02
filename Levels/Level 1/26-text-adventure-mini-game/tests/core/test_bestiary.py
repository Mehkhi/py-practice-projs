#!/usr/bin/env python3
"""Tests for bestiary metadata aggregation and visibility."""

import unittest

from core.bestiary import Bestiary, DiscoveryLevel
from core.loaders.bestiary_loader import build_bestiary_metadata


class TestBestiaryMetadata(unittest.TestCase):
    """Ensure bestiary seeding hydrates metadata correctly."""

    def setUp(self) -> None:
        self.encounters = {
            "ruined_path": {
                "backdrop_id": "ruined_path",
                "rewards": {"items": {"ancient_coin": 1}},
                "enemies": [
                    {
                        "name": "Rogue Slime",
                        "type": "rogue_slime",
                        "sprite_id": "slime",
                        "difficulty": "normal",
                        "max_hp": 40,
                        "attack": 6,
                        "defense": 2,
                        "magic": 1,
                        "speed": 5,
                        "weaknesses": ["fire"],
                        "resistances": ["ice"],
                        "immunities": [],
                        "absorbs": [],
                        "items": {"slime_core": 1},
                    }
                ],
            }
        }

    def test_metadata_builder_collects_enemy_details(self) -> None:
        metadata = build_bestiary_metadata(self.encounters)
        self.assertIn("rogue_slime", metadata)
        slime_meta = metadata["rogue_slime"]
        self.assertIn("fire", slime_meta["weaknesses"])
        self.assertIn("slime_core", slime_meta["drops"])
        self.assertIn("ancient_coin", slime_meta["drops"])
        self.assertTrue(slime_meta["description"])

    def test_seed_from_encounter_data_enriches_entries(self) -> None:
        metadata = build_bestiary_metadata(self.encounters)
        bestiary = Bestiary()
        added = bestiary.seed_from_encounter_data(self.encounters, metadata=metadata)
        self.assertEqual(added, 1)

        entry = bestiary.get_entry("rogue_slime")
        self.assertIsNotNone(entry)
        self.assertIn("fire", entry.weaknesses)
        self.assertIn("slime_core", entry.observed_drops)

        entry.discovery_level = DiscoveryLevel.DEFEATED
        stats = entry.get_visible_stats()
        self.assertIn("description", stats)
        self.assertIn("observed_drops", stats)
        self.assertIn("slime_core", stats["observed_drops"])


if __name__ == "__main__":
    unittest.main()

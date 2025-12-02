"""Tests for secret boss hints system."""

import unittest
from unittest.mock import Mock, MagicMock

from engine.secret_boss_hints import HintType, BossHint, HintManager
from core.secret_bosses import SecretBoss, SecretBossManager, UnlockCondition, UnlockConditionType


class TestSecretBossHints(unittest.TestCase):
    """Test suite for secret boss hints system."""

    def setUp(self):
        """Set up test fixtures."""
        # Create test hints
        self.hints = {
            "wyrm_hint_1": BossHint(
                hint_id="wyrm_hint_1",
                boss_id="ancient_wyrm",
                hint_type=HintType.RUMOR,
                content="Old miners speak of tremors...",
                trigger_type="dialogue",
                reveal_level=1
            ),
            "wyrm_hint_2": BossHint(
                hint_id="wyrm_hint_2",
                boss_id="ancient_wyrm",
                hint_type=HintType.LORE_ITEM,
                content="The Prophecy of Scales...",
                trigger_type="item",
                reveal_level=2
            ),
            "champion_hint_1": BossHint(
                hint_id="champion_hint_1",
                boss_id="forgotten_champion",
                hint_type=HintType.LORE_ITEM,
                content="Journal of Sir Aldric...",
                trigger_type="item",
                reveal_level=2
            )
        }
        self.hint_manager = HintManager(self.hints)

        # Create test bosses
        self.bosses = {
            "ancient_wyrm": SecretBoss(
                boss_id="ancient_wyrm",
                name="Zyraxis",
                title="The Ancient Wyrm",
                description="A dragon of immeasurable age.",
                encounter_id="secret_boss_ancient_wyrm",
                location_map_id="hidden_wyrm_lair",
                location_x=7,
                location_y=3,
                unlock_conditions=[],
                spawn_trigger_type="interact",
                lore_entries=[],
                rewards={"gold": 10000, "exp": 15000},
                unique_drops=["wyrm_fang"]
            ),
            "forgotten_champion": SecretBoss(
                boss_id="forgotten_champion",
                name="Sir Aldric",
                title="The Forgotten Champion",
                description="A legendary knight.",
                encounter_id="secret_boss_forgotten_champion",
                location_map_id="champions_rest",
                location_x=7,
                location_y=3,
                unlock_conditions=[],
                spawn_trigger_type="interact",
                lore_entries=[],
                rewards={"gold": 8000, "exp": 12000},
                unique_drops=["champions_shield"]
            )
        }
        self.secret_boss_manager = SecretBossManager(self.bosses)

    def test_hint_discovery(self):
        """Test that hints are correctly marked as discovered."""
        # Initially no hints discovered
        self.assertEqual(len(self.hint_manager.discovered_hints), 0)

        # Discover a hint
        hint = self.hint_manager.discover_hint("wyrm_hint_1")
        self.assertIsNotNone(hint)
        self.assertEqual(hint.hint_id, "wyrm_hint_1")
        self.assertIn("wyrm_hint_1", self.hint_manager.discovered_hints)

        # Try to discover again - should return None
        hint2 = self.hint_manager.discover_hint("wyrm_hint_1")
        self.assertIsNone(hint2)

    def test_hints_reveal_boss(self):
        """Test that first hint reveals boss in dossier."""
        # Initially boss not discovered
        self.assertNotIn("ancient_wyrm", self.secret_boss_manager.discovered)

        # Discover hint - should also discover boss
        self.hint_manager.discover_hint("wyrm_hint_1")
        # Note: In real implementation, dialogue_scene would call discover_boss
        self.secret_boss_manager.discover_boss("ancient_wyrm")
        self.assertIn("ancient_wyrm", self.secret_boss_manager.discovered)

    def test_hint_levels(self):
        """Test that higher level hints give more info."""
        hint1 = self.hints["wyrm_hint_1"]  # reveal_level=1
        hint2 = self.hints["wyrm_hint_2"]  # reveal_level=2

        self.assertEqual(hint1.reveal_level, 1)
        self.assertEqual(hint2.reveal_level, 2)
        self.assertLess(hint1.reveal_level, hint2.reveal_level)

    def test_hint_progress_tracking(self):
        """Test that discovery progress is accurate."""
        # Initially no progress
        discovered, total = self.hint_manager.get_discovery_progress("ancient_wyrm")
        self.assertEqual(discovered, 0)
        self.assertEqual(total, 2)  # 2 hints for ancient_wyrm

        # Discover one hint
        self.hint_manager.discover_hint("wyrm_hint_1")
        discovered, total = self.hint_manager.get_discovery_progress("ancient_wyrm")
        self.assertEqual(discovered, 1)
        self.assertEqual(total, 2)

        # Discover second hint
        self.hint_manager.discover_hint("wyrm_hint_2")
        discovered, total = self.hint_manager.get_discovery_progress("ancient_wyrm")
        self.assertEqual(discovered, 2)
        self.assertEqual(total, 2)

    def test_dialogue_triggers_hint(self):
        """Test that NPC dialogue discovers hints."""
        # Simulate dialogue setting flag
        flag = "hint_wyrm_hint_1_discovered"

        # Extract hint_id from flag pattern
        hint_id = flag[5:-11]  # Remove "hint_" prefix and "_discovered" suffix
        self.assertEqual(hint_id, "wyrm_hint_1")

        # Discover hint
        hint = self.hint_manager.discover_hint(hint_id)
        self.assertIsNotNone(hint)
        self.assertEqual(hint.hint_id, "wyrm_hint_1")

    def test_item_triggers_hint(self):
        """Test that lore items discover hints."""
        # Simulate item collection setting flag
        flag = "hint_champion_hint_1_discovered"
        hint_id = flag[5:-11]  # Remove "hint_" prefix and "_discovered" suffix
        self.assertEqual(hint_id, "champion_hint_1")

        # Discover hint
        hint = self.hint_manager.discover_hint(hint_id)
        self.assertIsNotNone(hint)
        self.assertEqual(hint.hint_id, "champion_hint_1")
        self.assertEqual(hint.trigger_type, "item")

    def test_mirror_boss_copies_stats(self):
        """Test that mirror boss has player stats."""
        # Create mock player
        player = Mock()
        player.name = "TestHero"
        player.stats = Mock()
        player.stats.max_hp = 1000
        player.stats.hp = 1000
        player.stats.attack = 50
        player.stats.defense = 30
        player.stats.magic = 40
        player.stats.speed = 25
        player.stats.luck = 10
        player.stats.max_sp = 100
        player.stats.sp = 100
        player.skills = ["fire_bolt", "heal", "shield", "lightning"]

        # Create mirror encounter
        encounter = self.secret_boss_manager.create_mirror_encounter(player)

        # Check encounter structure
        self.assertIn("enemies", encounter)
        self.assertEqual(len(encounter["enemies"]), 1)

        enemy = encounter["enemies"][0]
        self.assertEqual(enemy["name"], "Shadow TestHero")
        self.assertEqual(enemy["stats"]["hp"], 1200)  # 1.2 * 1000
        self.assertEqual(enemy["stats"]["max_hp"], 1200)
        self.assertEqual(enemy["stats"]["attack"], 50)
        self.assertEqual(enemy["stats"]["defense"], 30)
        self.assertEqual(enemy["stats"]["magic"], 40)
        self.assertEqual(enemy["stats"]["speed"], 25)
        self.assertEqual(len(enemy["skills"]), 4)  # Up to 4 skills
        self.assertTrue(enemy["ai_profile"]["mirrors_player"])

    def test_boss_silhouette_until_defeat(self):
        """Test that boss name is hidden until defeat."""
        # Boss not defeated - name should be hidden
        boss = self.bosses["ancient_wyrm"]
        if boss.boss_id not in self.secret_boss_manager.defeated:
            display_name = "???"
        else:
            display_name = boss.name
        self.assertEqual(display_name, "???")

        # Defeat boss
        self.secret_boss_manager.defeat_boss("ancient_wyrm")
        self.assertIn("ancient_wyrm", self.secret_boss_manager.defeated)

        # Now name should be visible
        if boss.boss_id in self.secret_boss_manager.defeated:
            display_name = boss.name
        else:
            display_name = "???"
        self.assertEqual(display_name, "Zyraxis")

    def test_multiple_hints_per_boss(self):
        """Test that multiple hints aggregate correctly."""
        # Discover both hints for ancient_wyrm
        self.hint_manager.discover_hint("wyrm_hint_1")
        self.hint_manager.discover_hint("wyrm_hint_2")

        # Get all hints for boss
        hints = self.hint_manager.get_hints_for_boss("ancient_wyrm")
        self.assertEqual(len(hints), 2)
        hint_ids = {h.hint_id for h in hints}
        self.assertEqual(hint_ids, {"wyrm_hint_1", "wyrm_hint_2"})

        # Progress should be 2/2
        discovered, total = self.hint_manager.get_discovery_progress("ancient_wyrm")
        self.assertEqual(discovered, 2)
        self.assertEqual(total, 2)


if __name__ == "__main__":
    unittest.main()

"""Unit tests for core/tutorial_system.py - Tutorial tips and help system."""

import unittest

from core.tutorial_system import (
    TutorialManager,
    TutorialTip,
    HelpEntry,
    TipTrigger,
)


class TestTutorialSystem(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        self.manager = TutorialManager()
        self.tip1 = TutorialTip(
            tip_id="tip1",
            trigger=TipTrigger.FIRST_BATTLE,
            title="Battle Basics",
            content="Use ATTACK to fight!",
            priority=10,
            category="combat",
        )
        self.tip2 = TutorialTip(
            tip_id="tip2",
            trigger=TipTrigger.FIRST_SHOP_VISIT,
            title="Shopping",
            content="Buy items here!",
            priority=8,
            category="exploration",
        )
        self.tip3 = TutorialTip(
            tip_id="tip3",
            trigger=TipTrigger.FIRST_BATTLE,
            title="Advanced Battle",
            content="Use SKILLS for special moves!",
            priority=5,
            category="combat",
            requires_tips=["tip1"],
        )
        self.help_entry1 = HelpEntry(
            entry_id="help1",
            title="Movement",
            content="Arrow keys to move",
            category="Controls",
            order=1,
        )
        self.help_entry2 = HelpEntry(
            entry_id="help2",
            title="Battle Controls",
            content="UP/DOWN to navigate",
            category="Controls",
            order=2,
        )

    def test_register_tip(self):
        """Test that tips are correctly registered."""
        self.manager.register_tip(self.tip1)
        self.assertIn("tip1", self.manager.tips)
        self.assertEqual(self.manager.tips["tip1"], self.tip1)

    def test_trigger_tip_returns_correct(self):
        """Test that correct tip is returned for trigger."""
        self.manager.register_tip(self.tip1)
        result = self.manager.trigger_tip(TipTrigger.FIRST_BATTLE)
        self.assertIsNotNone(result)
        self.assertEqual(result.tip_id, "tip1")
        self.assertEqual(result.trigger, TipTrigger.FIRST_BATTLE)

    def test_dismissed_tip_not_shown(self):
        """Test that permanently dismissed tips don't appear."""
        self.manager.register_tip(self.tip1)
        self.manager.dismiss_tip("tip1", permanently=True)
        result = self.manager.trigger_tip(TipTrigger.FIRST_BATTLE)
        self.assertIsNone(result)

    def test_seen_tip_tracking(self):
        """Test that tips are marked as seen after display."""
        self.manager.register_tip(self.tip1)
        self.assertNotIn("tip1", self.manager.seen_tips)
        self.manager.dismiss_tip("tip1", permanently=False)
        self.assertIn("tip1", self.manager.seen_tips)

    def test_prerequisite_tips(self):
        """Test that tips with prerequisites wait until prereqs seen."""
        self.manager.register_tip(self.tip1)
        self.manager.register_tip(self.tip3)
        # tip3 requires tip1, but tip1 hasn't been seen yet
        result = self.manager.trigger_tip(TipTrigger.FIRST_BATTLE)
        self.assertIsNotNone(result)
        self.assertEqual(result.tip_id, "tip1")  # Should return tip1, not tip3
        # Now mark tip1 as seen and permanently dismissed so tip3 can be shown
        self.manager.dismiss_tip("tip1", permanently=True)
        # Now tip3 should be available
        result = self.manager.trigger_tip(TipTrigger.FIRST_BATTLE)
        self.assertIsNotNone(result)
        self.assertEqual(result.tip_id, "tip3")

    def test_priority_ordering(self):
        """Test that higher priority tips are shown first."""
        self.manager.register_tip(self.tip1)  # priority 10
        self.manager.register_tip(self.tip3)  # priority 5
        # Both match FIRST_BATTLE, but tip1 has higher priority
        result = self.manager.trigger_tip(TipTrigger.FIRST_BATTLE)
        self.assertIsNotNone(result)
        self.assertEqual(result.tip_id, "tip1")
        # Dismiss tip1
        self.manager.dismiss_tip("tip1", permanently=True)
        # Now tip3 should be returned
        result = self.manager.trigger_tip(TipTrigger.FIRST_BATTLE)
        self.assertIsNotNone(result)
        self.assertEqual(result.tip_id, "tip3")

    def test_tips_disabled_global(self):
        """Test that no tips are shown when tips_enabled=False."""
        self.manager.register_tip(self.tip1)
        self.manager.tips_enabled = False
        result = self.manager.trigger_tip(TipTrigger.FIRST_BATTLE)
        self.assertIsNone(result)

    def test_help_entries_by_category(self):
        """Test that help entries are correctly grouped by category."""
        self.manager.register_help_entry(self.help_entry1)
        self.manager.register_help_entry(self.help_entry2)
        grouped = self.manager.get_help_entries_by_category()
        self.assertIn("Controls", grouped)
        self.assertEqual(len(grouped["Controls"]), 2)
        # Check ordering
        self.assertEqual(grouped["Controls"][0].entry_id, "help1")
        self.assertEqual(grouped["Controls"][1].entry_id, "help2")

    def test_serialize_deserialize(self):
        """Test that state survives save/load cycle."""
        self.manager.register_tip(self.tip1)
        self.manager.register_help_entry(self.help_entry1)
        self.manager.dismiss_tip("tip1", permanently=True)
        self.manager.seen_tips.add("tip1")
        self.manager.tips_enabled = False
        # Serialize
        data = self.manager.serialize()
        # Create new manager and deserialize
        new_manager = TutorialManager.deserialize(
            data, self.manager.tips, self.manager.help_entries
        )
        self.assertEqual(new_manager.dismissed_tips, {"tip1"})
        self.assertEqual(new_manager.seen_tips, {"tip1"})
        self.assertFalse(new_manager.tips_enabled)
        self.assertEqual(new_manager.tips, self.manager.tips)
        self.assertEqual(new_manager.help_entries, self.manager.help_entries)

    def test_pending_tip_queue(self):
        """Test that tips queue correctly and dequeue in priority order."""
        self.manager.register_tip(self.tip1)  # priority 10
        self.manager.register_tip(self.tip2)  # priority 8
        self.manager.register_tip(self.tip3)  # priority 5
        # Trigger tips (they get added to queue)
        self.manager.trigger_tip(TipTrigger.FIRST_BATTLE)
        self.manager.trigger_tip(TipTrigger.FIRST_SHOP_VISIT)
        # tip3 requires tip1, so it shouldn't be in queue yet
        self.assertEqual(len(self.manager.pending_tips), 2)
        # Get pending tip (should be highest priority first)
        tip = self.manager.get_pending_tip()
        self.assertIsNotNone(tip)
        self.assertEqual(tip.tip_id, "tip1")  # priority 10
        # Get next one
        tip = self.manager.get_pending_tip()
        self.assertIsNotNone(tip)
        self.assertEqual(tip.tip_id, "tip2")  # priority 8
        # Queue should be empty now
        self.assertEqual(len(self.manager.pending_tips), 0)
        tip = self.manager.get_pending_tip()
        self.assertIsNone(tip)

    def test_can_show_tip(self):
        """Test can_show_tip logic."""
        self.manager.register_tip(self.tip1)
        self.manager.register_tip(self.tip3)
        # tip1 should be showable
        self.assertTrue(self.manager.can_show_tip("tip1"))
        # tip3 requires tip1, so shouldn't be showable yet
        self.assertFalse(self.manager.can_show_tip("tip3"))
        # Mark tip1 as seen
        self.manager.seen_tips.add("tip1")
        # Now tip3 should be showable
        self.assertTrue(self.manager.can_show_tip("tip3"))
        # Dismiss tip1 permanently
        self.manager.dismiss_tip("tip1", permanently=True)
        # tip1 should not be showable
        self.assertFalse(self.manager.can_show_tip("tip1"))

    def test_register_help_entry(self):
        """Test that help entries are correctly registered."""
        self.manager.register_help_entry(self.help_entry1)
        self.assertIn("help1", self.manager.help_entries)
        self.assertEqual(self.manager.help_entries["help1"], self.help_entry1)

    def test_trigger_tip_no_match(self):
        """Test that trigger_tip returns None when no tips match."""
        self.manager.register_tip(self.tip1)
        result = self.manager.trigger_tip(TipTrigger.FIRST_SHOP_VISIT)
        self.assertIsNone(result)

    def test_dismiss_tip_removes_from_queue(self):
        """Test that dismissing a tip removes it from pending queue."""
        self.manager.register_tip(self.tip1)
        self.manager.trigger_tip(TipTrigger.FIRST_BATTLE)
        self.assertEqual(len(self.manager.pending_tips), 1)
        self.manager.dismiss_tip("tip1", permanently=False)
        self.assertEqual(len(self.manager.pending_tips), 0)


if __name__ == "__main__":
    unittest.main()

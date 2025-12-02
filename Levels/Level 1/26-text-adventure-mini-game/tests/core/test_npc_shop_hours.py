"""Unit tests for NPC shop hours system - shop availability and schedule queries."""

import unittest
from unittest.mock import Mock, MagicMock

from core.npc_schedules import ScheduleEntry, NPCSchedule, ScheduleManager
from core.time_system import TimeOfDay


class TestShopAvailability(unittest.TestCase):
    """Test shop availability checking functionality."""

    def setUp(self):
        """Set up test fixtures with shop schedule."""
        # Create schedule with shop open during work hours, closed in evening
        entry1 = ScheduleEntry(
            time_periods=[TimeOfDay.MORNING, TimeOfDay.NOON, TimeOfDay.AFTERNOON],
            map_id="shop",
            x=5,
            y=7,
            activity="tending shop",
            shop_available=True,
        )
        entry2 = ScheduleEntry(
            time_periods=[TimeOfDay.EVENING, TimeOfDay.NIGHT],
            map_id="tavern",
            x=3,
            y=4,
            activity="relaxing",
            shop_available=False,
            alternative_dialogue_id="merchant_off_duty",
        )
        entry3 = ScheduleEntry(
            time_periods=[TimeOfDay.MIDNIGHT, TimeOfDay.DAWN],
            map_id="home",
            x=1,
            y=1,
            activity="sleeping",
            shop_available=False,
            alternative_dialogue_id="shop_closed_sleeping",
        )
        schedule = NPCSchedule(
            npc_id="merchant_tom",
            default_map_id="shop",
            default_x=5,
            default_y=7,
            entries=[entry1, entry2, entry3],
        )
        self.manager = ScheduleManager(schedules={"merchant_tom": schedule})

    def test_shop_available_during_hours(self):
        """Shop returns available during work hours."""
        self.assertTrue(self.manager.is_shop_available("merchant_tom", TimeOfDay.MORNING))
        self.assertTrue(self.manager.is_shop_available("merchant_tom", TimeOfDay.NOON))
        self.assertTrue(self.manager.is_shop_available("merchant_tom", TimeOfDay.AFTERNOON))

    def test_shop_unavailable_off_hours(self):
        """Shop returns unavailable during off hours."""
        self.assertFalse(self.manager.is_shop_available("merchant_tom", TimeOfDay.EVENING))
        self.assertFalse(self.manager.is_shop_available("merchant_tom", TimeOfDay.NIGHT))
        self.assertFalse(self.manager.is_shop_available("merchant_tom", TimeOfDay.MIDNIGHT))

    def test_alternative_dialogue_returned(self):
        """Correct alt dialogue ID returned when shop is closed."""
        # Should return dialogue when shop is closed
        dialogue = self.manager.get_alternative_dialogue("merchant_tom", TimeOfDay.EVENING)
        self.assertEqual(dialogue, "merchant_off_duty")

        dialogue = self.manager.get_alternative_dialogue("merchant_tom", TimeOfDay.MIDNIGHT)
        self.assertEqual(dialogue, "shop_closed_sleeping")

        # Should return None when shop is open
        dialogue = self.manager.get_alternative_dialogue("merchant_tom", TimeOfDay.MORNING)
        self.assertIsNone(dialogue)

    def test_default_shop_available(self):
        """Missing schedule entry defaults to available."""
        # NPC without schedule should default to available
        self.assertTrue(self.manager.is_shop_available("nonexistent_npc", TimeOfDay.MORNING))

        # NPC with schedule but no matching entry should default to available
        # (uses default location which has shop_available=True by default)
        self.assertTrue(self.manager.is_shop_available("merchant_tom", TimeOfDay.DUSK))

    def test_alternative_dialogue_only_when_closed(self):
        """Alternative dialogue only returned when shop is actually closed."""
        # Shop is open, should return None
        dialogue = self.manager.get_alternative_dialogue("merchant_tom", TimeOfDay.MORNING)
        self.assertIsNone(dialogue)

        # Shop is closed, should return dialogue
        dialogue = self.manager.get_alternative_dialogue("merchant_tom", TimeOfDay.EVENING)
        self.assertEqual(dialogue, "merchant_off_duty")


class TestNPCSOnMapQuery(unittest.TestCase):
    """Test querying NPCs on a specific map."""

    def setUp(self):
        """Set up test fixtures with multiple NPCs."""
        # NPC 1: On shop map during morning
        entry1 = ScheduleEntry(
            time_periods=[TimeOfDay.MORNING, TimeOfDay.NOON],
            map_id="shop",
            x=5,
            y=7,
        )
        schedule1 = NPCSchedule(
            npc_id="merchant_1",
            default_map_id="home",
            default_x=1,
            default_y=1,
            entries=[entry1],
        )

        # NPC 2: On shop map during afternoon
        entry2 = ScheduleEntry(
            time_periods=[TimeOfDay.AFTERNOON, TimeOfDay.DUSK],
            map_id="shop",
            x=6,
            y=8,
        )
        schedule2 = NPCSchedule(
            npc_id="merchant_2",
            default_map_id="home",
            default_x=1,
            default_y=1,
            entries=[entry2],
        )

        # NPC 3: Never on shop map
        entry3 = ScheduleEntry(
            time_periods=[TimeOfDay.MORNING],
            map_id="tavern",
            x=3,
            y=4,
        )
        schedule3 = NPCSchedule(
            npc_id="npc_3",
            default_map_id="home",
            default_x=1,
            default_y=1,
            entries=[entry3],
        )

        self.manager = ScheduleManager(
            schedules={
                "merchant_1": schedule1,
                "merchant_2": schedule2,
                "npc_3": schedule3,
            }
        )

    def test_npcs_on_map_query(self):
        """Correctly lists NPCs scheduled for a map."""
        # During MORNING, only merchant_1 should be on shop map
        npcs = self.manager.get_npcs_on_map("shop", TimeOfDay.MORNING)
        self.assertIn("merchant_1", npcs)
        self.assertNotIn("merchant_2", npcs)
        self.assertNotIn("npc_3", npcs)

        # During AFTERNOON, only merchant_2 should be on shop map
        npcs = self.manager.get_npcs_on_map("shop", TimeOfDay.AFTERNOON)
        self.assertNotIn("merchant_1", npcs)
        self.assertIn("merchant_2", npcs)
        self.assertNotIn("npc_3", npcs)

        # During NOON, merchant_1 should still be on shop map
        npcs = self.manager.get_npcs_on_map("shop", TimeOfDay.NOON)
        self.assertIn("merchant_1", npcs)

    def test_npcs_on_map_empty_result(self):
        """Returns empty list when no NPCs are on the map."""
        npcs = self.manager.get_npcs_on_map("nonexistent_map", TimeOfDay.MORNING)
        self.assertEqual(npcs, [])

    def test_npcs_on_map_default_location(self):
        """Includes NPCs using default location when no entry matches."""
        # Create NPC with default location on shop map
        schedule = NPCSchedule(
            npc_id="default_npc",
            default_map_id="shop",
            default_x=10,
            default_y=10,
            entries=[],  # No entries, always uses default
        )
        manager = ScheduleManager(schedules={"default_npc": schedule})

        npcs = manager.get_npcs_on_map("shop", TimeOfDay.MORNING)
        self.assertIn("default_npc", npcs)


class TestQuestAvailability(unittest.TestCase):
    """Test NPC availability for quests."""

    def setUp(self):
        """Set up test fixtures with different activities."""
        # NPC available for quests
        entry1 = ScheduleEntry(
            time_periods=[TimeOfDay.MORNING],
            map_id="shop",
            x=5,
            y=7,
            activity="working",
        )

        # NPC unavailable (sleeping)
        entry2 = ScheduleEntry(
            time_periods=[TimeOfDay.NIGHT],
            map_id="home",
            x=1,
            y=1,
            activity="sleeping",
        )

        # NPC unavailable (away)
        entry3 = ScheduleEntry(
            time_periods=[TimeOfDay.AFTERNOON],
            map_id="away",
            x=0,
            y=0,
            activity="away",
        )

        # NPC unavailable (busy)
        entry4 = ScheduleEntry(
            time_periods=[TimeOfDay.EVENING],
            map_id="workshop",
            x=2,
            y=2,
            activity="busy",
        )

        schedule = NPCSchedule(
            npc_id="quest_giver",
            default_map_id="shop",
            default_x=5,
            default_y=7,
            entries=[entry1, entry2, entry3, entry4],
        )
        self.manager = ScheduleManager(schedules={"quest_giver": schedule})

    def test_quest_availability_sleeping(self):
        """Sleeping NPCs unavailable for quests."""
        self.assertFalse(self.manager.is_npc_available_for_quest("quest_giver", TimeOfDay.NIGHT))

    def test_quest_availability_away(self):
        """NPCs marked as 'away' are unavailable for quests."""
        self.assertFalse(self.manager.is_npc_available_for_quest("quest_giver", TimeOfDay.AFTERNOON))

    def test_quest_availability_busy(self):
        """NPCs marked as 'busy' are unavailable for quests."""
        self.assertFalse(self.manager.is_npc_available_for_quest("quest_giver", TimeOfDay.EVENING))

    def test_quest_availability_working(self):
        """NPCs with normal activities are available for quests."""
        self.assertTrue(self.manager.is_npc_available_for_quest("quest_giver", TimeOfDay.MORNING))

    def test_quest_availability_no_activity(self):
        """NPCs with no activity are available for quests."""
        # Create NPC with no activity
        entry = ScheduleEntry(
            time_periods=[TimeOfDay.MORNING],
            map_id="shop",
            x=5,
            y=7,
            activity=None,
        )
        schedule = NPCSchedule(
            npc_id="simple_npc",
            default_map_id="shop",
            default_x=5,
            default_y=7,
            entries=[entry],
        )
        manager = ScheduleManager(schedules={"simple_npc": schedule})

        self.assertTrue(manager.is_npc_available_for_quest("simple_npc", TimeOfDay.MORNING))

    def test_quest_availability_missing_npc(self):
        """Missing NPC defaults to available."""
        self.assertTrue(self.manager.is_npc_available_for_quest("nonexistent", TimeOfDay.MORNING))


class TestScheduleEntryDefaults(unittest.TestCase):
    """Test ScheduleEntry default values for shop fields."""

    def test_schedule_entry_defaults(self):
        """ScheduleEntry defaults shop_available to True and alternative_dialogue_id to None."""
        entry = ScheduleEntry(
            time_periods=[TimeOfDay.MORNING],
            map_id="shop",
            x=5,
            y=7,
        )
        self.assertTrue(entry.shop_available)
        self.assertIsNone(entry.alternative_dialogue_id)

    def test_schedule_entry_explicit_values(self):
        """ScheduleEntry can have explicit shop_available and alternative_dialogue_id values."""
        entry = ScheduleEntry(
            time_periods=[TimeOfDay.EVENING],
            map_id="tavern",
            x=3,
            y=4,
            shop_available=False,
            alternative_dialogue_id="shop_closed",
        )
        self.assertFalse(entry.shop_available)
        self.assertEqual(entry.alternative_dialogue_id, "shop_closed")


class TestBackwardCompatibility(unittest.TestCase):
    """Test backward compatibility with existing schedules."""

    def test_missing_shop_available_defaults_to_true(self):
        """Schedules without shop_available field default to True."""
        # Create entry without shop_available (simulating old data)
        entry = ScheduleEntry(
            time_periods=[TimeOfDay.MORNING],
            map_id="shop",
            x=5,
            y=7,
            # shop_available not specified, should default to True
        )
        schedule = NPCSchedule(
            npc_id="old_npc",
            default_map_id="shop",
            default_x=5,
            default_y=7,
            entries=[entry],
        )
        manager = ScheduleManager(schedules={"old_npc": schedule})

        # Should default to available
        self.assertTrue(manager.is_shop_available("old_npc", TimeOfDay.MORNING))

    def test_missing_alternative_dialogue_defaults_to_none(self):
        """Schedules without alternative_dialogue_id default to None."""
        entry = ScheduleEntry(
            time_periods=[TimeOfDay.EVENING],
            map_id="tavern",
            x=3,
            y=4,
            shop_available=False,
            # alternative_dialogue_id not specified
        )
        schedule = NPCSchedule(
            npc_id="npc_no_dialogue",
            default_map_id="shop",
            default_x=5,
            default_y=7,
            entries=[entry],
        )
        manager = ScheduleManager(schedules={"npc_no_dialogue": schedule})

        # Should return None when no alternative dialogue is set
        dialogue = manager.get_alternative_dialogue("npc_no_dialogue", TimeOfDay.EVENING)
        self.assertIsNone(dialogue)


if __name__ == "__main__":
    unittest.main()

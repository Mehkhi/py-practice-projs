#!/usr/bin/env python3
"""Tests for quest journal scene filtering and sorting helpers."""

import unittest
from typing import Optional

import pygame

from core.quests import Quest, QuestManager, QuestObjective, QuestStatus
from engine.quest_journal_scene import QuestJournalScene


class DummySceneManager:
    def pop(self) -> None:  # pragma: no cover - interface stub
        pass


class DummyAssets:
    """Minimal asset stub for menu scenes."""

    def get_font(
        self,
        font_name: str = "default",
        size: Optional[int] = None,
        apply_accessibility: bool = True,
    ) -> pygame.font.Font:
        return pygame.font.Font(None, size or 24)

    def get_image(self, sprite_id: str) -> pygame.Surface:
        surf = pygame.Surface((4, 4))
        surf.fill((255, 255, 255))
        return surf


class QuestJournalSceneTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        pygame.init()

    @classmethod
    def tearDownClass(cls) -> None:
        pygame.quit()

    def _build_manager(self) -> QuestManager:
        manager = QuestManager()
        quest_main = Quest(
            id="main",
            name="Main Quest",
            description="Restore balance.",
            status=QuestStatus.ACTIVE,
            category="main",
            difficulty="Easy",
            recommended_level=2,
            tags=["story"],
            reward_gold=50,
            reward_exp=100,
            objectives=[QuestObjective(id="obj", description="Do thing")],
        )
        quest_side = Quest(
            id="side",
            name="Side Quest",
            description="Optional task.",
            status=QuestStatus.ACTIVE,
            category="side",
            difficulty="Hard",
            recommended_level=5,
            tags=["side"],
            reward_gold=200,
            reward_exp=150,
            objectives=[QuestObjective(id="side_obj", description="Find item")],
        )
        manager.quests = {"main": quest_main, "side": quest_side}
        return manager

    def test_filter_restricts_visible_quests(self) -> None:
        manager = self._build_manager()
        scene = QuestJournalScene(DummySceneManager(), manager, assets=DummyAssets())
        self.assertIn("side", scene.filters)
        scene.filter_index = scene.filters.index("side")
        scene._clamp_selection()
        filtered = scene._get_current_quests()
        self.assertTrue(all(q.category == "side" or "side" in q.tags for q in filtered))

    def test_reward_sort_prioritizes_high_value(self) -> None:
        manager = self._build_manager()
        scene = QuestJournalScene(DummySceneManager(), manager, assets=DummyAssets())
        scene.sort_index = scene.sort_modes.index("Reward")
        quests = scene._get_current_quests()
        reward_values = [q.reward_gold + q.reward_exp for q in quests]
        self.assertGreaterEqual(reward_values[0], reward_values[1])


if __name__ == "__main__":
    unittest.main()

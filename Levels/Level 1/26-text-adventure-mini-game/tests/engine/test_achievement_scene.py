#!/usr/bin/env python3
"""Lightweight tests for the achievement scene controller logic."""

import unittest
from typing import Optional

import pygame

from core.achievements import (
    Achievement,
    AchievementCategory,
    AchievementManager,
    AchievementRarity,
)
from engine.achievement_scene import AchievementScene


class DummySceneManager:
    """Minimal manager stub to satisfy BaseMenuScene."""

    def __init__(self) -> None:
        self.pop_called = False

    def pop(self) -> None:
        self.pop_called = True


class DummyAssets:
    """Lightweight asset stub that returns simple pygame primitives."""

    def __init__(self) -> None:
        self._default_font = pygame.font.Font(None, 24)

    def get_font(
        self,
        font_name: str = "default",
        size: Optional[int] = None,
        apply_accessibility: bool = True,
    ) -> pygame.font.Font:
        return pygame.font.Font(None, size or 24)

    def get_image(self, sprite_id: str) -> pygame.Surface:
        surface = pygame.Surface((4, 4))
        surface.fill((255, 255, 255))
        return surface


class AchievementSceneTestCase(unittest.TestCase):
    """Verify focus toggling logic without rendering the full scene."""

    @classmethod
    def setUpClass(cls) -> None:
        pygame.init()

    @classmethod
    def tearDownClass(cls) -> None:
        pygame.quit()

    def _build_manager(self) -> AchievementManager:
        manager = AchievementManager()
        for idx in range(2):
            achievement = Achievement(
                id=f"ach_{idx}",
                name=f"Achievement {idx}",
                description="Do something notable.",
                category=AchievementCategory.COMBAT,
                rarity=AchievementRarity.COMMON,
                target_count=3,
            )
            achievement.current_count = idx
            manager.achievements[achievement.id] = achievement
        return manager

    def _make_scene(self) -> AchievementScene:
        manager = self._build_manager()
        return AchievementScene(
            manager=DummySceneManager(),
            achievement_manager=manager,
            assets=DummyAssets(),
        )

    def test_focus_toggle_and_scroll_reset(self) -> None:
        scene = self._make_scene()
        toggle_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
        scene.handle_event(toggle_event)
        self.assertFalse(scene.focus_on_list)

        scene._max_detail_scroll = 200
        scene.detail_scroll = 0
        down_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN)
        scene.handle_event(down_event)
        self.assertGreater(scene.detail_scroll, 0)

        scene.handle_event(toggle_event)
        self.assertTrue(scene.focus_on_list)
        self.assertEqual(scene.detail_scroll, 0)

    def test_list_navigation_resets_detail_scroll(self) -> None:
        scene = self._make_scene()
        scene.detail_scroll = 48
        down_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN)
        scene.handle_event(down_event)
        self.assertEqual(scene.detail_scroll, 0)


if __name__ == "__main__":
    unittest.main()

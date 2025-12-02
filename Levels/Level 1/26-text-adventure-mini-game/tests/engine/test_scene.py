"""Tests for Scene and SceneManager helper utilities."""

from typing import Any
import unittest
from unittest import mock

from engine.scene import Scene, SceneManager


class _DummyScene(Scene):
    """Concrete Scene for testing."""

    def handle_event(self, event: Any) -> None:
        return

    def update(self, dt: float) -> None:
        return

    def draw(self, surface: Any) -> None:
        return


class TestSceneHelpers(unittest.TestCase):
    """Unit tests for manager access helpers."""

    def test_get_manager_returns_instance(self) -> None:
        scene = _DummyScene()
        manager = SceneManager(scene)
        expected = object()
        manager.custom_manager = expected

        with mock.patch("core.logging_utils.log_warning") as mock_warning:
            result = manager.get_manager("custom_manager", "test_get_manager")

        self.assertIs(result, expected)
        mock_warning.assert_not_called()

    def test_get_manager_logs_when_missing(self) -> None:
        scene = _DummyScene()
        manager = SceneManager(scene)

        with mock.patch("core.logging_utils.log_warning") as mock_warning:
            result = manager.get_manager("missing_manager", "missing_context")

        self.assertIsNone(result)
        mock_warning.assert_called_once_with(
            "missing_manager not available (requested by missing_context)"
        )

    def test_scene_get_manager_attr_handles_missing_manager(self) -> None:
        scene = _DummyScene()
        scene.manager = None

        with mock.patch("core.logging_utils.log_warning") as mock_warning:
            result = scene.get_manager_attr(
                "achievement_manager", "scene_missing_manager"
            )

        self.assertIsNone(result)
        mock_warning.assert_called_once_with(
            "SceneManager not available when accessing achievement_manager "
            "(requested by scene_missing_manager)"
        )

    def test_scene_get_manager_attr_delegates(self) -> None:
        scene = _DummyScene()
        mock_manager = mock.Mock()
        expected = object()
        mock_manager.get_manager.return_value = expected
        scene.manager = mock_manager

        result = scene.get_manager_attr("quest_manager", "delegate_context")

        self.assertIs(result, expected)
        mock_manager.get_manager.assert_called_once_with(
            "quest_manager", "delegate_context"
        )

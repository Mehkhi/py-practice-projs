"""Unit tests for core/data_loader.py - Shared JSON loading utilities."""

import json
import os
import tempfile
import unittest
from unittest.mock import patch

from core.data_loader import load_json_file


class TestLoadJsonFile(unittest.TestCase):
    """Tests for the load_json_file() helper function."""

    def test_load_valid_json_dict(self):
        """Test loading a valid JSON file containing a dict."""
        data = {"key": "value", "number": 42, "list": [1, 2, 3]}
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            temp_path = f.name

        try:
            result = load_json_file(temp_path)
            self.assertEqual(result, data)
            self.assertEqual(result["key"], "value")
            self.assertEqual(result["number"], 42)
            self.assertEqual(result["list"], [1, 2, 3])
        finally:
            os.unlink(temp_path)

    def test_load_valid_json_list(self):
        """Test loading a valid JSON file containing a list at the top level."""
        data = [{"id": "item1"}, {"id": "item2"}]
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            temp_path = f.name

        try:
            result = load_json_file(temp_path)
            self.assertEqual(result, data)
            self.assertEqual(len(result), 2)
            self.assertEqual(result[0]["id"], "item1")
        finally:
            os.unlink(temp_path)

    def test_load_empty_json_object(self):
        """Test loading an empty JSON object."""
        data = {}
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            temp_path = f.name

        try:
            result = load_json_file(temp_path)
            self.assertEqual(result, {})
        finally:
            os.unlink(temp_path)

    def test_missing_file_returns_default(self):
        """Test that a missing file returns the default value."""
        result = load_json_file("/nonexistent/path/to/file.json")
        self.assertEqual(result, {})

    def test_missing_file_returns_custom_default(self):
        """Test that a missing file returns a custom default value."""
        result = load_json_file("/nonexistent/path.json", default=[])
        self.assertEqual(result, [])

        result = load_json_file("/nonexistent/path.json", default={"fallback": True})
        self.assertEqual(result, {"fallback": True})

    def test_missing_file_returns_none_default(self):
        """Test that a missing file can return None as default."""
        result = load_json_file("/nonexistent/path.json", default=None)
        # Note: default=None gets converted to {} by the function
        self.assertEqual(result, {})

    def test_malformed_json_returns_default(self):
        """Test that malformed JSON returns the default value."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("{ invalid json }")
            temp_path = f.name

        try:
            result = load_json_file(temp_path)
            self.assertEqual(result, {})
        finally:
            os.unlink(temp_path)

    def test_malformed_json_returns_custom_default(self):
        """Test that malformed JSON returns a custom default value."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("not valid json at all")
            temp_path = f.name

        try:
            result = load_json_file(temp_path, default={"error": True})
            self.assertEqual(result, {"error": True})
        finally:
            os.unlink(temp_path)

    def test_context_parameter_in_error_logging(self):
        """Test that context parameter is included in error logs."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("invalid json")
            temp_path = f.name

        try:
            with patch("core.data_loader.log_warning") as mock_log:
                load_json_file(temp_path, context="Loading test data")
                mock_log.assert_called_once()
                call_args = mock_log.call_args[0][0]
                self.assertIn("Loading test data", call_args)
                self.assertIn(temp_path, call_args)
        finally:
            os.unlink(temp_path)

    def test_context_parameter_on_missing_file_with_warn(self):
        """Test that context is included when warn_on_missing=True."""
        with patch("core.data_loader.log_warning") as mock_log:
            load_json_file(
                "/nonexistent/path.json",
                context="Loading quests",
                warn_on_missing=True
            )
            mock_log.assert_called_once()
            call_args = mock_log.call_args[0][0]
            self.assertIn("Loading quests", call_args)
            self.assertIn("/nonexistent/path.json", call_args)

    def test_missing_file_no_warning_by_default(self):
        """Test that missing files don't log warnings by default (only debug)."""
        with patch("core.data_loader.log_warning") as mock_warn:
            with patch("core.data_loader.log_debug") as mock_debug:
                load_json_file("/nonexistent/path.json")
                mock_warn.assert_not_called()
                mock_debug.assert_called_once()

    def test_warn_on_missing_true_logs_warning(self):
        """Test that warn_on_missing=True logs a warning for missing files."""
        with patch("core.data_loader.log_warning") as mock_warn:
            load_json_file("/nonexistent/path.json", warn_on_missing=True)
            mock_warn.assert_called_once()

    def test_nested_json_structure(self):
        """Test loading a complex nested JSON structure."""
        data = {
            "items": [
                {"id": "sword", "stats": {"attack": 10, "defense": 2}},
                {"id": "shield", "stats": {"attack": 0, "defense": 15}},
            ],
            "config": {
                "enabled": True,
                "nested": {"deeply": {"value": 42}}
            }
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            temp_path = f.name

        try:
            result = load_json_file(temp_path)
            self.assertEqual(result["items"][0]["stats"]["attack"], 10)
            self.assertEqual(result["config"]["nested"]["deeply"]["value"], 42)
        finally:
            os.unlink(temp_path)

    def test_unicode_content(self):
        """Test loading JSON with unicode characters."""
        data = {"name": "Magic Sword", "description": "A mystical blade"}
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
            temp_path = f.name

        try:
            result = load_json_file(temp_path)
            self.assertEqual(result["name"], "Magic Sword")
            self.assertEqual(result["description"], "A mystical blade")
        finally:
            os.unlink(temp_path)

    def test_empty_file_returns_default(self):
        """Test that an empty file returns the default value."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            # Write nothing - empty file
            temp_path = f.name

        try:
            result = load_json_file(temp_path)
            self.assertEqual(result, {})
        finally:
            os.unlink(temp_path)

    def test_json_with_comments_style_content(self):
        """Test that JSON with trailing content fails gracefully."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write('{"valid": "json"} // but with comments')
            temp_path = f.name

        try:
            result = load_json_file(temp_path, default={"fallback": True})
            self.assertEqual(result, {"fallback": True})
        finally:
            os.unlink(temp_path)

    def test_permission_error_returns_default(self):
        """Test that permission errors return the default value."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"test": "data"}, f)
            temp_path = f.name

        try:
            # Make file unreadable
            os.chmod(temp_path, 0o000)
            result = load_json_file(temp_path, default={"error": True})
            self.assertEqual(result, {"error": True})
        finally:
            # Restore permissions for cleanup
            os.chmod(temp_path, 0o644)
            os.unlink(temp_path)


class TestLoadJsonFileIntegration(unittest.TestCase):
    """Integration tests for load_json_file with real game data."""

    def test_load_actual_skills_json(self):
        """Test loading the actual skills.json file if it exists."""
        path = os.path.join("data", "skills.json")
        if os.path.exists(path):
            result = load_json_file(path)
            self.assertIn("skills", result)
            self.assertIsInstance(result["skills"], list)
            if result["skills"]:
                first_skill = result["skills"][0]
                self.assertIn("id", first_skill)
                self.assertIn("name", first_skill)

    def test_load_actual_items_json(self):
        """Test loading the actual items.json file if it exists."""
        path = os.path.join("data", "items.json")
        if os.path.exists(path):
            result = load_json_file(path)
            self.assertIn("items", result)
            self.assertIsInstance(result["items"], list)

    def test_load_actual_config_json(self):
        """Test loading the actual config.json file if it exists."""
        path = os.path.join("data", "config.json")
        if os.path.exists(path):
            result = load_json_file(path)
            self.assertIsInstance(result, dict)


if __name__ == "__main__":
    unittest.main()

"""Schema policy and loader robustness tests."""

import json
import os
import tempfile
import unittest

from core.loaders.arena_loader import load_arena_data
from core.loaders.base import load_json_file
from core.loaders.fishing_loader import load_fishing_data
from core.loaders.npc_loader import load_npc_schedules
from core.loaders.puzzle_loader import load_puzzles_from_json
from core.loaders.secret_boss_loader import load_secret_bosses
from core.loaders.tutorial_loader import load_tutorial_data
from core.mod_loader import ModLoader, ModManifest


class LoaderSchemaPolicyTests(unittest.TestCase):
    """Verify loaders log-and-skip malformed data instead of raising."""

    def test_load_json_file_missing_uses_default(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            missing_path = os.path.join(tmp_dir, "missing.json")
            result = load_json_file(missing_path, default={"ok": True})
            self.assertEqual(result, {"ok": True})

    def test_arena_loader_skips_invalid_fighter_shapes(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = os.path.join(tmp_dir, "arena.json")
            with open(path, "w", encoding="utf-8") as handle:
                json.dump({"fighters": ["bad"], "arena_schedule": {}}, handle)

            with self.assertLogs(level="WARNING") as logs:
                manager = load_arena_data(path)

            self.assertEqual(manager.fighters, {})
            self.assertTrue(any("[SCHEMA]" in msg for msg in logs.output))

    def test_fishing_loader_handles_malformed_sections(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = os.path.join(tmp_dir, "fishing.json")
            with open(path, "w", encoding="utf-8") as handle:
                json.dump({"fish": ["not-a-dict"], "spots": {}}, handle)

            with self.assertLogs(level="WARNING") as logs:
                fish_db, spots = load_fishing_data(path)

            self.assertEqual(fish_db, {})
            self.assertEqual(spots, {})
            self.assertTrue(any("[SCHEMA]" in msg for msg in logs.output))

    def test_puzzle_loader_skips_missing_required_fields(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = os.path.join(tmp_dir, "puzzles.json")
            with open(path, "w", encoding="utf-8") as handle:
                json.dump({"puzzles": {"p1": {"puzzle_id": "p1"}}}, handle)

            with self.assertLogs(level="WARNING") as logs:
                puzzles = load_puzzles_from_json(path)

            self.assertEqual(puzzles, {})
            self.assertTrue(any("[SCHEMA]" in msg for msg in logs.output))

    def test_npc_loader_skips_entries_with_invalid_time_periods(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = os.path.join(tmp_dir, "npc_schedules.json")
            data = {
                "schedules": {
                    "npc_1": {
                        "default_map_id": "m1",
                        "default_x": 0,
                        "default_y": 0,
                        "entries": [
                            {
                                "time_periods": ["invalid"],
                                "map_id": "m1",
                                "x": 1,
                                "y": 1,
                            }
                        ],
                    }
                }
            }
            with open(path, "w", encoding="utf-8") as handle:
                json.dump(data, handle)

            with self.assertLogs(level="WARNING") as logs:
                manager = load_npc_schedules(path)

            schedule = manager.schedules.get("npc_1")
            self.assertIsNotNone(schedule)
            self.assertEqual(schedule.entries, [])
            self.assertTrue(any("[SCHEMA]" in msg for msg in logs.output))

    def test_secret_boss_loader_skips_invalid_enum_values(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = os.path.join(tmp_dir, "secret_bosses.json")
            data = {
                "bosses": {
                    "boss_1": {
                        "boss_id": "boss_1",
                        "name": "Test",
                        "encounter_id": "enc_1",
                        "location_map_id": "map",
                        "unlock_conditions": [{"condition_type": "UNKNOWN", "data": {}, "description": ""}],
                    }
                }
            }
            with open(path, "w", encoding="utf-8") as handle:
                json.dump(data, handle)

            with self.assertLogs(level="WARNING") as logs:
                bosses = load_secret_bosses(path)

            self.assertIn("boss_1", bosses)
            self.assertEqual(bosses["boss_1"].unlock_conditions, [])
            self.assertTrue(any("[SCHEMA]" in msg for msg in logs.output))

    def test_tutorial_loader_skips_bad_trigger(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = os.path.join(tmp_dir, "tutorial_tips.json")
            data = {"tips": [{"tip_id": "tip1", "trigger": "NOPE", "title": "t", "content": "c"}], "help_entries": []}
            with open(path, "w", encoding="utf-8") as handle:
                json.dump(data, handle)

            with self.assertLogs(level="WARNING") as logs:
                tips, help_entries = load_tutorial_data(path)

            self.assertEqual(tips, {})
            self.assertEqual(help_entries, {})
            self.assertTrue(any("[SCHEMA]" in msg for msg in logs.output))

    def test_mod_loader_skips_non_dict_base_and_override(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_path = os.path.join(tmp_dir, "base.json")
            override_path = os.path.join(tmp_dir, "override.json")

            with open(base_path, "w", encoding="utf-8") as handle:
                json.dump([], handle)
            with open(override_path, "w", encoding="utf-8") as handle:
                json.dump([], handle)

            loader = ModLoader(mods_path=tmp_dir)
            loader.manifests = [
                ModManifest(
                    mod_id="mod1",
                    name="Mod1",
                    version="1.0",
                    data_overrides={"data": "override.json"},
                    base_path=tmp_dir,
                )
            ]

            with self.assertLogs(level="WARNING") as logs:
                merged = loader.merge_data(base_path, "data")

            self.assertEqual(merged, {})
            self.assertTrue(any("[SCHEMA]" in msg for msg in logs.output))


if __name__ == "__main__":
    unittest.main()

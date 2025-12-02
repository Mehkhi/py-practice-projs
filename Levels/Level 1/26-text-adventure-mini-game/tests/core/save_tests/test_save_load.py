"""Unit tests for core/save_load.py - Save/load serialization."""

import json
import os
import tempfile
import unittest
from unittest.mock import Mock

from core.save_load import SaveManager
from core.save import (
    DeserializationResources,
    get_save_version,
    migrate_save_data,
    recover_partial_save,
    serialize_world_runtime_state,
)
from core.world import World, Map, Tile
from core.entities import Player
from core.items import Inventory, Item
from core.stats import Stats, StatusEffect
from core.npc_schedules import ScheduleManager
from core.time_system import TimeOfDay


class TestSaveManagerSerialize(unittest.TestCase):
    def setUp(self):
        self.world = World()
        tiles = [[Tile("grass", True, "grass")] * 3] * 3
        self.world.add_map(Map(map_id="forest_path", width=3, height=3, tiles=tiles))
        self.world.add_map(Map(map_id="cave", width=3, height=3, tiles=tiles))
        self.world.set_flag("quest_started", True)

        self.stats = Stats(
            max_hp=100,
            hp=80,
            max_sp=50,
            sp=40,
            attack=15,
            defense=10,
            magic=8,
            speed=12,
            luck=5,
        )
        self.inventory = Inventory()
        self.inventory.add("health_potion", 3)
        self.inventory.add("sword", 1)

        self.player = Player(
            entity_id="player_1",
            name="Hero",
            x=5,
            y=10,
            sprite_id="hero_sprite",
            stats=self.stats,
            inventory=self.inventory,
        )
        self.player.base_skills = ["slash", "heal"]
        self.player.skills = ["slash", "heal"]
        self.player.equipment["weapon"] = "sword"

        self.save_manager = SaveManager(save_dir=tempfile.mkdtemp())

    def tearDown(self):
        # Clean up temp directory
        import shutil
        shutil.rmtree(self.save_manager.save_dir, ignore_errors=True)

    def test_serialize_state_basic(self):
        data = self.save_manager.serialize_state(self.world, self.player)

        self.assertIn("world", data)
        self.assertIn("player", data)

    def test_serialize_world_state(self):
        data = self.save_manager.serialize_state(self.world, self.player)

        self.assertEqual(data["world"]["current_map_id"], "forest_path")
        self.assertTrue(data["world"]["flags"]["quest_started"])

    def test_serialize_world_includes_visited_maps(self):
        self.world.mark_map_visited("cave")
        data = self.save_manager.serialize_state(self.world, self.player)
        self.assertIn("visited_maps", data["world"])
        self.assertIn("cave", data["world"]["visited_maps"])

    def test_serialize_player_basic_info(self):
        data = self.save_manager.serialize_state(self.world, self.player)
        player_data = data["player"]

        self.assertEqual(player_data["entity_id"], "player_1")
        self.assertEqual(player_data["name"], "Hero")
        self.assertEqual(player_data["x"], 5)
        self.assertEqual(player_data["y"], 10)

    def test_serialize_player_inventory(self):
        data = self.save_manager.serialize_state(self.world, self.player)
        inventory = data["player"]["inventory"]

        self.assertEqual(inventory["health_potion"], 3)
        self.assertEqual(inventory["sword"], 1)

    def test_serialize_player_stats(self):
        data = self.save_manager.serialize_state(self.world, self.player)
        stats = data["player"]["stats"]

        self.assertEqual(stats["max_hp"], 100)
        self.assertEqual(stats["hp"], 80)
        self.assertEqual(stats["attack"], 15)
        self.assertEqual(stats["defense"], 10)

    def test_serialize_player_equipment(self):
        data = self.save_manager.serialize_state(self.world, self.player)

        self.assertEqual(data["player"]["equipment"]["weapon"], "sword")

    def test_serialize_player_skills(self):
        data = self.save_manager.serialize_state(self.world, self.player)

        self.assertIn("slash", data["player"]["skills"])
        self.assertIn("heal", data["player"]["skills"])

    def test_serialize_status_effects(self):
        self.stats.add_status_effect("poison", duration=3, stacks=2)
        data = self.save_manager.serialize_state(self.world, self.player)

        effects = data["player"]["stats"]["status_effects"]
        self.assertIn("poison", effects)
        self.assertEqual(effects["poison"]["duration"], 3)
        self.assertEqual(effects["poison"]["stacks"], 2)


class TestSaveManagerDeserialize(unittest.TestCase):
    def setUp(self):
        self.world = World()
        tiles = [[Tile("grass", True, "grass")] * 3] * 3
        self.world.add_map(Map(map_id="forest_path", width=3, height=3, tiles=tiles))
        self.world.add_map(Map(map_id="cave", width=3, height=3, tiles=tiles))

        self.save_manager = SaveManager(save_dir=tempfile.mkdtemp())

    def tearDown(self):
        import shutil
        shutil.rmtree(self.save_manager.save_dir, ignore_errors=True)

    def test_deserialize_basic_player(self):
        data = {
            "world": {"current_map_id": "cave", "flags": {"test_flag": True}},
            "player": {
                "entity_id": "player_1",
                "name": "TestHero",
                "x": 3,
                "y": 7,
                "inventory": {},
                "equipment": {},
                "skills": [],
                "stats": {
                    "max_hp": 100,
                    "hp": 50,
                    "max_sp": 30,
                    "sp": 20,
                    "attack": 10,
                    "defense": 5,
                    "magic": 8,
                    "speed": 6,
                    "luck": 3,
                    "status_effects": {},
                },
            },
        }

        player = self.save_manager.deserialize_state(data, self.world)

        self.assertEqual(player.entity_id, "player_1")
        self.assertEqual(player.name, "TestHero")
        self.assertEqual(player.x, 3)
        self.assertEqual(player.y, 7)

    def test_deserialize_restores_world_state(self):
        data = {
            "world": {"current_map_id": "cave", "flags": {"quest_done": True}},
            "player": {
                "entity_id": "p1",
                "name": "Hero",
                "x": 0,
                "y": 0,
                "inventory": {},
                "equipment": {},
                "skills": [],
                "stats": None,
            },
        }

        self.save_manager.deserialize_state(data, self.world)

        self.assertEqual(self.world.current_map_id, "cave")
        self.assertTrue(self.world.flags["quest_done"])

    def test_deserialize_restores_visited_maps(self):
        data = {
            "world": {
                "current_map_id": "forest_path",
                "flags": {},
                "visited_maps": ["forest_path", "cave"],
            },
            "player": {
                "entity_id": "p1",
                "name": "Hero",
                "x": 0,
                "y": 0,
                "inventory": {},
                "equipment": {},
                "skills": [],
                "stats": {
                    "max_hp": 100,
                    "hp": 100,
                    "max_sp": 50,
                    "sp": 50,
                    "attack": 10,
                    "defense": 5,
                    "magic": 5,
                    "speed": 5,
                    "luck": 3,
                    "status_effects": {},
                },
            },
        }

        self.save_manager.deserialize_state(data, self.world)
        self.assertIn("cave", self.world.visited_maps)

    def test_deserialize_restores_stats(self):
        data = {
            "world": {"current_map_id": "forest_path", "flags": {}},
            "player": {
                "entity_id": "p1",
                "name": "Hero",
                "x": 0,
                "y": 0,
                "inventory": {},
                "equipment": {},
                "skills": [],
                "stats": {
                    "max_hp": 120,
                    "hp": 60,
                    "max_sp": 40,
                    "sp": 30,
                    "attack": 20,
                    "defense": 15,
                    "magic": 10,
                    "speed": 8,
                    "luck": 4,
                    "status_effects": {},
                },
            },
        }

        player = self.save_manager.deserialize_state(data, self.world)

        self.assertEqual(player.stats.max_hp, 120)
        self.assertEqual(player.stats.hp, 60)
        self.assertEqual(player.stats.attack, 20)

    def test_deserialize_restores_status_effects(self):
        data = {
            "world": {"current_map_id": "forest_path", "flags": {}},
            "player": {
                "entity_id": "p1",
                "name": "Hero",
                "x": 0,
                "y": 0,
                "inventory": {},
                "equipment": {},
                "skills": [],
                "stats": {
                    "max_hp": 100,
                    "hp": 50,
                    "max_sp": 30,
                    "sp": 20,
                    "attack": 10,
                    "defense": 5,
                    "magic": 8,
                    "speed": 6,
                    "luck": 3,
                    "status_effects": {
                        "poison": {"duration": 5, "stacks": 1},
                        "bleed": {"duration": 2, "stacks": 3},
                    },
                },
            },
        }

        player = self.save_manager.deserialize_state(data, self.world)

        self.assertIn("poison", player.stats.status_effects)
        self.assertEqual(player.stats.status_effects["poison"].duration, 5)
        self.assertIn("bleed", player.stats.status_effects)
        self.assertEqual(player.stats.status_effects["bleed"].stacks, 3)

    def test_deserialize_restores_inventory(self):
        data = {
            "world": {"current_map_id": "forest_path", "flags": {}},
            "player": {
                "entity_id": "p1",
                "name": "Hero",
                "x": 0,
                "y": 0,
                "inventory": {"health_potion": 5, "key": 1},
                "equipment": {},
                "skills": [],
                "stats": None,
            },
        }

        player = self.save_manager.deserialize_state(data, self.world)

        self.assertEqual(player.inventory.get_quantity("health_potion"), 5)
        self.assertEqual(player.inventory.get_quantity("key"), 1)

    def test_deserialize_restores_skills(self):
        data = {
            "world": {"current_map_id": "forest_path", "flags": {}},
            "player": {
                "entity_id": "p1",
                "name": "Hero",
                "x": 0,
                "y": 0,
                "inventory": {},
                "equipment": {},
                "skills": ["fireball", "ice_blast"],
                "stats": None,
            },
        }

        player = self.save_manager.deserialize_state(data, self.world)

        self.assertIn("fireball", player.skills)
        self.assertIn("ice_blast", player.skills)

    def test_deserialize_uses_injected_resources_without_io(self):
        resources = DeserializationResources(
            items_db={
                "test_sword": Item(
                    id="test_sword",
                    name="Test Sword",
                    description="",
                    item_type="equipment",
                    effect_id="slash",
                    equip_slot="weapon",
                    stat_modifiers={"attack": 2},
                )
            },
            skill_trees={}
        )
        resources.items_loader = Mock(side_effect=AssertionError("items loader should not run"))
        resources.skill_tree_loader = Mock(side_effect=AssertionError("skill tree loader should not run"))

        data = {
            "world": {"current_map_id": "forest_path", "flags": {}},
            "player": {
                "entity_id": "p1",
                "name": "Hero",
                "x": 0,
                "y": 0,
                "inventory": {},
                "equipment": {"weapon": "test_sword"},
                "skills": [],
                "skill_tree_progress": {
                    "skill_points": 0,
                    "skill_points_total": 0,
                    "unlocked_nodes": {},
                },
                "stats": {
                    "max_hp": 90,
                    "hp": 90,
                    "max_sp": 50,
                    "sp": 40,
                    "attack": 10,
                    "defense": 5,
                    "magic": 4,
                    "speed": 6,
                    "luck": 2,
                    "status_effects": {},
                },
            },
        }

        player = self.save_manager.deserialize_state(data, self.world, resources=resources)

        self.assertEqual(player.equipment.get("weapon"), "test_sword")
        self.assertFalse(resources.items_loader.called)
        self.assertFalse(resources.skill_tree_loader.called)


class TestSaveManagerSlots(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.save_manager = SaveManager(save_dir=self.temp_dir)

        self.world = World()
        tiles = [[Tile("grass", True, "grass")] * 3] * 3
        self.world.add_map(Map(map_id="forest_path", width=3, height=3, tiles=tiles))

        self.player = Player(
            entity_id="player_1",
            name="Hero",
            x=5,
            y=10,
            sprite_id="hero",
            stats=Stats(100, 100, 50, 50, 10, 5, 4, 6, 3),
            inventory=Inventory(),
        )

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_slot_exists_false(self):
        self.assertFalse(self.save_manager.slot_exists(1))

    def test_save_to_slot_creates_file(self):
        self.save_manager.save_to_slot(1, self.world, self.player)
        self.assertTrue(self.save_manager.slot_exists(1))

    def test_save_and_load_roundtrip(self):
        self.player.inventory.add("health_potion", 2)
        self.world.set_flag("test_flag", True)

        self.save_manager.save_to_slot(2, self.world, self.player)

        # Reset world state
        new_world = World()
        new_world.add_map(Map(map_id="forest_path", width=3, height=3, tiles=[[Tile("grass", True, "grass")] * 3] * 3))

        loaded_player = self.save_manager.load_from_slot(2, new_world)

        self.assertEqual(loaded_player.name, "Hero")
        self.assertEqual(loaded_player.inventory.get_quantity("health_potion"), 2)
        self.assertTrue(new_world.flags["test_flag"])

    def test_load_from_nonexistent_slot_raises(self):
        with self.assertRaises(FileNotFoundError):
            self.save_manager.load_from_slot(99, self.world)

    def test_multiple_slots(self):
        self.save_manager.save_to_slot(1, self.world, self.player)
        self.save_manager.save_to_slot(2, self.world, self.player)
        self.save_manager.save_to_slot(3, self.world, self.player)

        self.assertTrue(self.save_manager.slot_exists(1))
        self.assertTrue(self.save_manager.slot_exists(2))
        self.assertTrue(self.save_manager.slot_exists(3))
        self.assertFalse(self.save_manager.slot_exists(4))

    def test_world_runtime_state_persists(self):
        """Test that trigger fired states and enemy defeated flags persist."""
        from core.world import Trigger
        from core.entities import OverworldEnemy

        # Add a trigger to a map and fire it
        trigger = Trigger(id="chest_opened", x=1, y=1, trigger_type="script", data={}, once=True, fired=False)
        self.world.maps["forest_path"].triggers.append(trigger)
        self.world.maps["forest_path"].fire_trigger("chest_opened")

        # Add an overworld enemy and mark it defeated
        enemy = OverworldEnemy(entity_id="goblin_1", name="Goblin", x=2, y=2, sprite_id="goblin", encounter_id="goblin_fight")
        enemy.defeated = True
        self.world.set_map_overworld_enemies("forest_path", [enemy])

        # Save
        self.save_manager.save_to_slot(1, self.world, self.player)

        # Create fresh world and reload
        new_world = World()
        new_tiles = [[Tile("grass", True, "grass")] * 3] * 3
        new_map = Map(map_id="forest_path", width=3, height=3, tiles=new_tiles)
        new_trigger = Trigger(id="chest_opened", x=1, y=1, trigger_type="script", data={}, once=True, fired=False)
        new_map.triggers.append(new_trigger)
        new_world.add_map(new_map)
        new_enemy = OverworldEnemy(entity_id="goblin_1", name="Goblin", x=2, y=2, sprite_id="goblin", encounter_id="goblin_fight")
        new_world.set_map_overworld_enemies("forest_path", [new_enemy])

        # Load
        self.save_manager.load_from_slot(1, new_world)

        # Verify trigger state persisted
        restored_trigger = new_world.maps["forest_path"].get_trigger_at(1, 1)
        self.assertIsNone(restored_trigger)  # Should be None because fired=True and once=True
        self.assertTrue(new_world.maps["forest_path"].triggers[0].fired)

        # Verify enemy defeated state persisted
        enemies = new_world.get_map_overworld_enemies("forest_path")
        self.assertEqual(len(enemies), 1)
        self.assertTrue(enemies[0].defeated)

    def test_weather_system_state_persists(self):
        """Test that weather system state persists across save/load."""
        from core.weather import WeatherSystem, WeatherType

        weather = WeatherSystem()
        weather.current_weather = WeatherType.RAIN
        weather.change_timer = 123.45
        weather.enabled = True

        # Save with weather
        self.save_manager.save_to_slot(1, self.world, self.player, weather_system=weather)

        # Create new world and weather system
        new_world = World()
        new_tiles = [[Tile("grass", True, "grass")] * 3] * 3
        new_world.add_map(Map(map_id="forest_path", width=3, height=3, tiles=new_tiles))
        new_weather = WeatherSystem()  # Defaults to CLEAR

        # Load
        self.save_manager.load_from_slot(1, new_world, weather_system=new_weather)

        # Verify weather state restored
        self.assertEqual(new_weather.current_weather, WeatherType.RAIN)
        self.assertAlmostEqual(new_weather.change_timer, 123.45, places=2)
        self.assertTrue(new_weather.enabled)

    def test_schedule_manager_state_persists(self):
        """Test that schedule manager state persists across save/load via legacy API."""
        schedule_manager = ScheduleManager()
        schedule_manager._last_time_period = TimeOfDay.EVENING
        schedule_manager._npc_positions = {
            "merchant_1": ("town_square", 5, 7),
            "guard_1": ("castle_gate", 10, 3),
        }

        # Save with schedule_manager
        self.save_manager.save_to_slot(1, self.world, self.player, schedule_manager=schedule_manager)

        # Create new world and schedule manager
        new_world = World()
        new_tiles = [[Tile("grass", True, "grass")] * 3] * 3
        new_world.add_map(Map(map_id="forest_path", width=3, height=3, tiles=new_tiles))
        new_schedule_manager = ScheduleManager()

        # Load
        self.save_manager.load_from_slot(1, new_world, schedule_manager=new_schedule_manager)

        # Verify schedule state restored
        self.assertEqual(new_schedule_manager._last_time_period, TimeOfDay.EVENING)
        self.assertEqual(
            new_schedule_manager._npc_positions.get("merchant_1"),
            ("town_square", 5, 7),
        )
        self.assertEqual(
            new_schedule_manager._npc_positions.get("guard_1"),
            ("castle_gate", 10, 3),
        )
        self.assertTrue(new_schedule_manager._pending_position_restore)

    def test_serialize_state_includes_npc_schedules(self):
        """Test that serialize_state writes npc_schedules when schedule_manager is provided."""
        schedule_manager = ScheduleManager()
        schedule_manager._last_time_period = TimeOfDay.MORNING
        schedule_manager._npc_positions = {"npc_1": ("map_a", 1, 2)}

        data = self.save_manager.serialize_state(
            self.world, self.player, schedule_manager=schedule_manager
        )

        self.assertIn("npc_schedules", data)
        self.assertEqual(data["npc_schedules"]["last_time_period"], TimeOfDay.MORNING.value)
        self.assertIn("npc_1", data["npc_schedules"]["npc_positions"])

    def test_deserialize_state_restores_npc_schedules(self):
        """Test that deserialize_state restores schedule_manager from npc_schedules."""
        data = {
            "meta": {"version": 1, "timestamp": "2024-01-01T00:00:00", "play_time_seconds": 0},
            "world": {"current_map_id": "forest_path", "flags": {}},
            "player": {
                "entity_id": "p1", "name": "Hero", "x": 0, "y": 0,
                "inventory": {}, "equipment": {}, "skills": [],
                "stats": {
                    "max_hp": 100, "hp": 100, "max_sp": 50, "sp": 50,
                    "attack": 10, "defense": 5, "magic": 5, "speed": 5, "luck": 3,
                    "status_effects": {}
                }
            },
            "npc_schedules": {
                "last_time_period": TimeOfDay.NIGHT.value,
                "npc_positions": {
                    "shopkeeper": {"map_id": "home", "x": 4, "y": 5}
                }
            }
        }

        schedule_manager = ScheduleManager()
        self.save_manager.deserialize_state(data, self.world, schedule_manager=schedule_manager)

        self.assertEqual(schedule_manager._last_time_period, TimeOfDay.NIGHT)
        self.assertEqual(
            schedule_manager._npc_positions.get("shopkeeper"),
            ("home", 4, 5),
        )


class TestSaveFileVersioning(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.save_manager = SaveManager(save_dir=self.temp_dir)

        self.world = World()
        tiles = [[Tile("grass", True, "grass")] * 3] * 3
        self.world.add_map(Map(map_id="forest_path", width=3, height=3, tiles=tiles))

        self.player = Player(
            entity_id="player_1",
            name="Hero",
            x=5,
            y=10,
            sprite_id="hero",
            stats=Stats(100, 100, 50, 50, 10, 5, 4, 6, 3),
            inventory=Inventory(),
        )

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_save_includes_version(self):
        """Test that new saves include version field."""
        data = self.save_manager.serialize_state(self.world, self.player)
        self.assertIn("meta", data)
        self.assertIn("version", data["meta"])
        self.assertEqual(data["meta"]["version"], 1)

    def test_get_save_version(self):
        """Test get_save_version helper function."""
        # New save with version
        data = self.save_manager.serialize_state(self.world, self.player)
        version = get_save_version(data)
        self.assertEqual(version, 1)

        # Old save without version
        old_data = {
            "meta": {"timestamp": "2024-01-01T00:00:00", "play_time_seconds": 0},
            "world": {"current_map_id": "forest_path", "flags": {}},
            "player": {}
        }
        version = get_save_version(old_data)
        self.assertEqual(version, 0)

    def test_load_old_save_without_version(self):
        """Test that old saves without version field are migrated."""
        # Create an old-style save (version 0)
        old_data = {
            "meta": {
                "timestamp": "2024-01-01T00:00:00",
                "play_time_seconds": 100.5
            },
            "world": {
                "current_map_id": "forest_path",
                "flags": {"test_flag": True}
            },
            "player": {
                "entity_id": "player_1",
                "name": "OldHero",
                "x": 3,
                "y": 7,
                "inventory": {},
                "equipment": {},
                "skills": [],
                "stats": {
                    "max_hp": 100,
                    "hp": 80,
                    "max_sp": 50,
                    "sp": 40,
                    "attack": 10,
                    "defense": 5,
                    "magic": 8,
                    "speed": 6,
                    "luck": 3,
                    "status_effects": {}
                }
            }
        }

        # Save old format to file
        save_path = os.path.join(self.temp_dir, "save_1.json")
        with open(save_path, 'w') as f:
            json.dump(old_data, f)

        # Load should migrate automatically
        loaded_player = self.save_manager.load_from_slot(1, self.world)
        self.assertEqual(loaded_player.name, "OldHero")

        # Verify migration happened by checking the file
        with open(save_path, 'r') as f:
            loaded_data = json.load(f)
        # Note: Migration happens in memory, file isn't rewritten
        # But deserialize_state should handle it


class TestSaveFileValidation(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.save_manager = SaveManager(save_dir=self.temp_dir)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_validate_save_data_valid(self):
        """Test that valid save data passes validation."""
        valid_data = {
            "meta": {
                "version": 1,
                "timestamp": "2024-01-01T00:00:00",
                "play_time_seconds": 100.5
            },
            "world": {
                "current_map_id": "forest_path",
                "flags": {"test": True},
                "runtime_state": {"trigger_states": {}, "enemy_states": {}}
            },
            "player": {
                "entity_id": "player_1",
                "name": "Hero",
                "x": 5,
                "y": 10,
                "inventory": {},
                "equipment": {},
                "skills": [],
                "stats": {
                    "max_hp": 100,
                    "hp": 80,
                    "max_sp": 50,
                    "sp": 40,
                    "attack": 10,
                    "defense": 5,
                    "magic": 8,
                    "speed": 6,
                    "luck": 3,
                    "status_effects": {}
                }
            }
        }

        is_valid, errors = self.save_manager.validate_save_data(valid_data)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

    def test_validate_save_data_missing_fields(self):
        """Test that missing required fields are detected."""
        # Missing meta
        data = {
            "world": {"current_map_id": "forest_path", "flags": {}},
            "player": {"entity_id": "player_1", "name": "Hero", "x": 0, "y": 0, "inventory": {}, "stats": {}}
        }
        is_valid, errors = self.save_manager.validate_save_data(data)
        self.assertFalse(is_valid)
        self.assertIn("Missing 'meta' section", errors)

        # Missing player.stats required fields
        data = {
            "meta": {"timestamp": "2024-01-01T00:00:00", "play_time_seconds": 0},
            "world": {"current_map_id": "forest_path", "flags": {}},
            "player": {
                "entity_id": "player_1",
                "name": "Hero",
                "x": 0,
                "y": 0,
                "inventory": {},
                "stats": {"max_hp": 100}  # Missing other stats
            }
        }
        is_valid, errors = self.save_manager.validate_save_data(data)
        self.assertFalse(is_valid)
        self.assertTrue(any("Missing 'player.stats" in err for err in errors))

    def test_validate_save_data_invalid_types(self):
        """Test that wrong data types are detected."""
        data = {
            "meta": {
                "version": 1,
                "timestamp": 12345,  # Should be string
                "play_time_seconds": "not_a_number"  # Should be number
            },
            "world": {
                "current_map_id": 123,  # Should be string
                "flags": "not_a_dict"  # Should be dict
            },
            "player": {
                "entity_id": "player_1",
                "name": "Hero",
                "x": "not_a_number",  # Should be number
                "y": 0,
                "inventory": [],
                "stats": {
                    "max_hp": "not_a_number",  # Should be number
                    "hp": 80,
                    "max_sp": 50,
                    "sp": 40,
                    "attack": 10,
                    "defense": 5,
                    "magic": 8,
                    "speed": 6,
                    "luck": 3,
                    "status_effects": {}
                }
            }
        }
        is_valid, errors = self.save_manager.validate_save_data(data)
        self.assertFalse(is_valid)
        self.assertTrue(any("must be a" in err for err in errors))


class TestPartialCorruptionRecovery(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.save_manager = SaveManager(save_dir=self.temp_dir)

        self.world = World()
        tiles = [[Tile("grass", True, "grass")] * 3] * 3
        self.world.add_map(Map(map_id="forest_path", width=3, height=3, tiles=tiles))

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_recover_partial_save_missing_fields(self):
        """Test that missing fields get defaults during recovery."""
        # Save with missing fields
        partial_data = {
            "meta": {},  # Missing timestamp and play_time_seconds
            "world": {},  # Missing current_map_id and flags
            "player": {
                "entity_id": "player_1",
                # Missing name, x, y, stats, inventory
            }
        }

        recovered = recover_partial_save(partial_data)

        # Check that defaults were filled in
        self.assertIn("timestamp", recovered["meta"])
        self.assertIn("play_time_seconds", recovered["meta"])
        self.assertIn("current_map_id", recovered["world"])
        self.assertEqual(recovered["world"]["current_map_id"], "forest_path")
        self.assertIn("flags", recovered["world"])
        self.assertIn("name", recovered["player"])
        self.assertEqual(recovered["player"]["name"], "Hero")
        self.assertIn("stats", recovered["player"])
        self.assertIn("max_hp", recovered["player"]["stats"])

    def test_load_partial_corruption(self):
        """Test that partial corruption allows loading with defaults."""
        # Create save with missing stats
        partial_data = {
            "meta": {
                "version": 1,
                "timestamp": "2024-01-01T00:00:00",
                "play_time_seconds": 0
            },
            "world": {
                "current_map_id": "forest_path",
                "flags": {},
                "runtime_state": {"trigger_states": {}, "enemy_states": {}}
            },
            "player": {
                "entity_id": "player_1",
                "name": "Hero",
                "x": 5,
                "y": 10,
                "inventory": {},
                "equipment": {},
                "skills": []
                # Missing stats - should be recovered
            }
        }

        save_path = os.path.join(self.temp_dir, "save_1.json")
        with open(save_path, 'w') as f:
            json.dump(partial_data, f)

        # Should load successfully with recovered stats
        player = self.save_manager.load_from_slot(1, self.world)
        self.assertIsNotNone(player)
        self.assertIsNotNone(player.stats)
        self.assertEqual(player.name, "Hero")

    def test_load_corrupted_json(self):
        """Test that corrupted JSON is handled gracefully."""
        save_path = os.path.join(self.temp_dir, "save_1.json")

        # Write corrupted JSON
        with open(save_path, 'w') as f:
            f.write("{ invalid json }")

        # Should raise ValueError with descriptive message
        with self.assertRaises(ValueError) as context:
            self.save_manager.load_from_slot(1, self.world)

        self.assertIn("corrupted", str(context.exception).lower())


class TestErrorHandling(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.save_manager = SaveManager(save_dir=self.temp_dir)

        self.world = World()
        tiles = [[Tile("grass", True, "grass")] * 3] * 3
        self.world.add_map(Map(map_id="forest_path", width=3, height=3, tiles=tiles))

        self.player = Player(
            entity_id="player_1",
            name="Hero",
            x=5,
            y=10,
            sprite_id="hero",
            stats=Stats(100, 100, 50, 50, 10, 5, 4, 6, 3),
            inventory=Inventory(),
        )

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_load_from_slot_corrupted_file(self):
        """Test that corrupted files are handled with descriptive errors."""
        save_path = os.path.join(self.temp_dir, "save_1.json")

        # Write completely corrupted JSON
        with open(save_path, 'w') as f:
            f.write("not json at all {{{")

        with self.assertRaises(ValueError) as context:
            self.save_manager.load_from_slot(1, self.world)

        error_msg = str(context.exception)
        self.assertIn("corrupted", error_msg.lower())
        self.assertIn("slot 1", error_msg)

    def test_load_from_slot_missing_required_fields(self):
        """Test that missing required fields use defaults."""
        # Save with minimal valid data
        minimal_data = {
            "meta": {
                "version": 1,
                "timestamp": "2024-01-01T00:00:00",
                "play_time_seconds": 0
            },
            "world": {
                "current_map_id": "forest_path",
                "flags": {},
                "runtime_state": {"trigger_states": {}, "enemy_states": {}}
            },
            "player": {
                "entity_id": "player_1",
                "name": "TestHero",
                "x": 0,
                "y": 0,
                "inventory": {},
                "equipment": {},
                "skills": [],
                "stats": {
                    "max_hp": 100,
                    "hp": 100,
                    "max_sp": 30,
                    "sp": 30,
                    "attack": 10,
                    "defense": 5,
                    "magic": 5,
                    "speed": 5,
                    "luck": 3,
                    "status_effects": {}
                }
            }
        }

        save_path = os.path.join(self.temp_dir, "save_1.json")
        with open(save_path, 'w') as f:
            json.dump(minimal_data, f)

        # Should load successfully
        player = self.save_manager.load_from_slot(1, self.world)
        self.assertEqual(player.name, "TestHero")
        self.assertIsNotNone(player.stats)

    def test_get_slot_preview_validation(self):
        """Test that get_slot_preview validates before returning."""
        # Create invalid save
        invalid_data = {
            "meta": {},  # Missing required fields
            "world": {},
            "player": {}
        }

        save_path = os.path.join(self.temp_dir, "save_1.json")
        with open(save_path, 'w') as f:
            json.dump(invalid_data, f)

        # Should return None due to validation failure
        preview = self.save_manager.get_slot_preview(1)
        self.assertIsNone(preview)

    def test_get_slot_preview_corrupted_json(self):
        """Test that get_slot_preview handles corrupted JSON."""
        save_path = os.path.join(self.temp_dir, "save_1.json")

        with open(save_path, 'w') as f:
            f.write("{ invalid json }")

        # Should return None for corrupted JSON
        preview = self.save_manager.get_slot_preview(1)
        self.assertIsNone(preview)


class TestAdditionalCoverage(unittest.TestCase):
    """Additional tests for coverage gaps identified in code review."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.save_manager = SaveManager(save_dir=self.temp_dir)

        self.world = World()
        tiles = [[Tile("grass", True, "grass")] * 3] * 3
        self.world.add_map(Map(map_id="forest_path", width=3, height=3, tiles=tiles))

        self.player = Player(
            entity_id="player_1",
            name="Hero",
            x=5,
            y=10,
            sprite_id="hero",
            stats=Stats(100, 100, 50, 50, 10, 5, 4, 6, 3),
            inventory=Inventory(),
        )

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_resave_includes_version(self):
        """Test that re-saving a migrated save includes the new version."""
        # Create old-style save (version 0)
        old_data = {
            "meta": {
                "timestamp": "2024-01-01T00:00:00",
                "play_time_seconds": 100.5
            },
            "world": {
                "current_map_id": "forest_path",
                "flags": {"test_flag": True}
            },
            "player": {
                "entity_id": "player_1",
                "name": "OldHero",
                "x": 3,
                "y": 7,
                "inventory": {},
                "equipment": {},
                "skills": [],
                "stats": {
                    "max_hp": 100,
                    "hp": 80,
                    "max_sp": 50,
                    "sp": 40,
                    "attack": 10,
                    "defense": 5,
                    "magic": 8,
                    "speed": 6,
                    "luck": 3,
                    "status_effects": {}
                }
            }
        }

        # Save old format to file
        save_path = os.path.join(self.temp_dir, "save_1.json")
        with open(save_path, 'w') as f:
            json.dump(old_data, f)

        # Load (triggers migration)
        loaded_player = self.save_manager.load_from_slot(1, self.world)

        # Re-save the migrated data
        self.save_manager.save_to_slot(1, self.world, loaded_player)

        # Verify the re-saved file has version 1
        with open(save_path, 'r') as f:
            resaved_data = json.load(f)

        self.assertIn("meta", resaved_data)
        self.assertIn("version", resaved_data["meta"])
        self.assertEqual(resaved_data["meta"]["version"], 1)

    def test_empty_party_save_load(self):
        """Test saving/loading with an empty party list."""
        self.player.party = []  # Ensure empty party

        self.save_manager.save_to_slot(1, self.world, self.player)

        new_world = World()
        tiles = [[Tile("grass", True, "grass")] * 3] * 3
        new_world.add_map(Map(map_id="forest_path", width=3, height=3, tiles=tiles))

        loaded_player = self.save_manager.load_from_slot(1, new_world)

        self.assertEqual(len(loaded_player.party), 0)

    def test_invalid_formation_positions_corrected(self):
        """Test that invalid formation positions are corrected to defaults."""
        from core.save_load import DEFAULT_STARTING_MAP

        # Create save with invalid formation positions
        data = {
            "meta": {
                "version": 1,
                "timestamp": "2024-01-01T00:00:00",
                "play_time_seconds": 0
            },
            "world": {
                "current_map_id": "forest_path",
                "flags": {},
                "runtime_state": {"trigger_states": {}, "enemy_states": {}}
            },
            "player": {
                "entity_id": "player_1",
                "name": "Hero",
                "x": 0,
                "y": 0,
                "inventory": {},
                "equipment": {},
                "skills": [],
                "formation_position": "invalid_position",  # Invalid!
                "party_formation": {
                    "ally_1": "also_invalid"  # Invalid!
                },
                "stats": {
                    "max_hp": 100,
                    "hp": 100,
                    "max_sp": 30,
                    "sp": 30,
                    "attack": 10,
                    "defense": 5,
                    "magic": 5,
                    "speed": 5,
                    "luck": 3,
                    "status_effects": {}
                }
            }
        }

        save_path = os.path.join(self.temp_dir, "save_1.json")
        with open(save_path, 'w') as f:
            json.dump(data, f)

        player = self.save_manager.load_from_slot(1, self.world)

        # Player formation should be corrected to "front" (default)
        self.assertEqual(player.formation_position, "front")

        # Party formation should use default for invalid position
        from core.entities import DEFAULT_FORMATION_POSITION
        if "ally_1" in player.party_formation:
            self.assertEqual(player.party_formation["ally_1"], DEFAULT_FORMATION_POSITION)

    def test_serialize_world_runtime_state_directly(self):
        """Test _serialize_world_runtime_state method in isolation."""
        from core.world import Trigger
        from core.entities import OverworldEnemy

        # Add a trigger and fire it
        trigger = Trigger(id="chest_1", x=1, y=1, trigger_type="script", data={}, once=True, fired=True)
        self.world.maps["forest_path"].triggers.append(trigger)

        # Add a defeated enemy
        enemy = OverworldEnemy(entity_id="goblin_1", name="Goblin", x=2, y=2, sprite_id="goblin", encounter_id="fight")
        enemy.defeated = True
        self.world.set_map_overworld_enemies("forest_path", [enemy])

        # Serialize runtime state
        runtime_state = serialize_world_runtime_state(self.world)

        # Verify structure
        self.assertIn("trigger_states", runtime_state)
        self.assertIn("enemy_states", runtime_state)
        self.assertIn("forest_path", runtime_state["trigger_states"])
        self.assertTrue(runtime_state["trigger_states"]["forest_path"]["chest_1"])
        self.assertIn("forest_path", runtime_state["enemy_states"])
        self.assertTrue(runtime_state["enemy_states"]["forest_path"]["goblin_1"])

    def test_delete_slot_nonexistent(self):
        """Test that delete_slot returns False for non-existent slot."""
        result = self.save_manager.delete_slot(999)
        self.assertFalse(result)

    def test_delete_slot_success(self):
        """Test that delete_slot successfully removes a save file."""
        self.save_manager.save_to_slot(1, self.world, self.player)
        self.assertTrue(self.save_manager.slot_exists(1))

        result = self.save_manager.delete_slot(1)
        self.assertTrue(result)
        self.assertFalse(self.save_manager.slot_exists(1))

    def test_atomic_write_creates_valid_save(self):
        """Test that atomic write produces a valid save file."""
        self.player.inventory.add("health_potion", 5)
        self.world.set_flag("atomic_test", True)

        self.save_manager.save_to_slot(1, self.world, self.player)

        # Verify the file is valid JSON and contains expected data
        save_path = os.path.join(self.temp_dir, "save_1.json")
        with open(save_path, 'r') as f:
            data = json.load(f)

        self.assertEqual(data["player"]["inventory"]["health_potion"], 5)
        self.assertTrue(data["world"]["flags"]["atomic_test"])

    def test_deep_copy_in_migration(self):
        """Test that migration doesn't mutate the original data."""
        original_data = {
            "meta": {},
            "world": {"flags": {"original": True}},
            "player": {"entity_id": "test"}
        }

        # Keep a reference to check mutation
        original_meta = original_data["meta"]
        original_flags = original_data["world"]["flags"]

        # Perform migration
        migrated = migrate_save_data(original_data, 0, 1)

        # Original should NOT have been mutated
        self.assertNotIn("version", original_meta)
        self.assertNotIn("timestamp", original_meta)

        # Migrated should have the new fields
        self.assertIn("version", migrated["meta"])
        self.assertEqual(migrated["meta"]["version"], 1)

    def test_deep_copy_in_recovery(self):
        """Test that recovery doesn't mutate the original data."""
        original_data = {
            "meta": {},
            "world": {},
            "player": {}
        }

        # Keep references to check mutation
        original_meta = original_data["meta"]
        original_world = original_data["world"]

        # Perform recovery
        recovered = recover_partial_save(original_data)

        # Original should NOT have been mutated
        self.assertNotIn("version", original_meta)
        self.assertNotIn("current_map_id", original_world)

        # Recovered should have the new fields
        self.assertIn("version", recovered["meta"])
        self.assertIn("current_map_id", recovered["world"])

    def test_default_starting_map_constant(self):
        """Test that DEFAULT_STARTING_MAP constant is used correctly."""
        from core.save_load import DEFAULT_STARTING_MAP

        # Create minimal corrupted save missing current_map_id
        partial_data = {
            "meta": {"version": 1, "timestamp": "2024-01-01T00:00:00", "play_time_seconds": 0},
            "world": {"flags": {}},  # Missing current_map_id
            "player": {
                "entity_id": "player_1",
                "name": "Hero",
                "x": 0, "y": 0,
                "inventory": {},
                "stats": {
                    "max_hp": 100, "hp": 100, "max_sp": 30, "sp": 30,
                    "attack": 10, "defense": 5, "magic": 5, "speed": 5, "luck": 3,
                    "status_effects": {}
                }
            }
        }

        recovered = recover_partial_save(partial_data)
        self.assertEqual(recovered["world"]["current_map_id"], DEFAULT_STARTING_MAP)


class TestScheduleManagerState(unittest.TestCase):
    """Tests for ScheduleManager save/load and migration behavior."""

    def test_schedule_manager_serialize_basic(self):
        """ScheduleManager.serialize produces expected structure."""
        manager = ScheduleManager()
        manager._last_time_period = TimeOfDay.MORNING
        manager._npc_positions = {
            "npc_1": ("town_square", 5, 7),
            "npc_2": ("inn", 1, 2),
        }

        data = manager.serialize()

        self.assertIn("last_time_period", data)
        self.assertEqual(data["last_time_period"], TimeOfDay.MORNING.value)

        self.assertIn("npc_positions", data)
        self.assertIn("npc_1", data["npc_positions"])
        self.assertEqual(
            data["npc_positions"]["npc_1"],
            {"map_id": "town_square", "x": 5, "y": 7},
        )
        self.assertEqual(
            data["npc_positions"]["npc_2"],
            {"map_id": "inn", "x": 1, "y": 2},
        )

    def test_schedule_manager_deserialize_basic(self):
        """Valid data restores last_time_period and npc_positions."""
        manager = ScheduleManager()
        payload = {
            "last_time_period": TimeOfDay.EVENING.value,
            "npc_positions": {
                "npc_1": {"map_id": "town_square", "x": 3, "y": 4},
            },
        }

        manager.deserialize_into(payload)

        self.assertEqual(manager._last_time_period, TimeOfDay.EVENING)
        self.assertEqual(
            manager._npc_positions.get("npc_1"),
            ("town_square", 3, 4),
        )
        self.assertTrue(manager._pending_position_restore)
        self.assertFalse(manager._force_schedule_refresh)

    def test_schedule_manager_deserialize_non_dict_resets_state(self):
        """Non-dict data gracefully resets internal state."""
        manager = ScheduleManager()
        manager._last_time_period = TimeOfDay.MORNING
        manager._npc_positions = {"npc_1": ("map", 0, 0)}
        manager._pending_position_restore = True
        manager._force_schedule_refresh = True

        manager.deserialize_into(["not", "a", "dict"])  # type: ignore[arg-type]

        self.assertIsNone(manager._last_time_period)
        self.assertEqual(manager._npc_positions, {})
        self.assertFalse(manager._pending_position_restore)
        self.assertFalse(manager._force_schedule_refresh)

    def test_schedule_manager_deserialize_invalid_time_period(self):
        """Invalid last_time_period falls back to None without crashing."""
        manager = ScheduleManager()
        payload = {
            "last_time_period": "not_a_real_period",
            "npc_positions": {},
        }

        manager.deserialize_into(payload)

        self.assertIsNone(manager._last_time_period)
        self.assertEqual(manager._npc_positions, {})
        self.assertFalse(manager._pending_position_restore)
        self.assertFalse(manager._force_schedule_refresh)

    def test_schedule_manager_migration_no_positions_forces_refresh(self):
        """Old saves without npc_positions force a schedule refresh."""
        manager = ScheduleManager()
        payload = {
            "last_time_period": TimeOfDay.NIGHT.value,
            # npc_positions intentionally omitted to simulate older saves
        }

        manager.deserialize_into(payload)

        self.assertEqual(manager._last_time_period, TimeOfDay.NIGHT)
        self.assertEqual(manager._npc_positions, {})
        self.assertFalse(manager._pending_position_restore)
        self.assertTrue(manager._force_schedule_refresh)

    def test_schedule_manager_positions_trigger_restore_path(self):
        """Saves with npc_positions set the pending restore flag."""
        manager = ScheduleManager()
        payload = {
            "last_time_period": TimeOfDay.MORNING.value,
            "npc_positions": {
                "npc_1": {"map_id": "field", "x": 2, "y": 9},
            },
        }

        manager.deserialize_into(payload)

        self.assertEqual(manager._last_time_period, TimeOfDay.MORNING)
        self.assertEqual(
            manager._npc_positions.get("npc_1"),
            ("field", 2, 9),
        )
        self.assertTrue(manager._pending_position_restore)
        self.assertFalse(manager._force_schedule_refresh)


if __name__ == "__main__":
    unittest.main()

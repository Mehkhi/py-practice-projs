"""Unit tests for core/weather.py - WeatherSystem, WeatherType, weather effects."""

import unittest

from core.weather import (
    WeatherType,
    WeatherParticle,
    WeatherSystem,
    WEATHER_TINTS,
    WEATHER_AMBIENT,
    WEATHER_PARTICLE_DENSITY,
    WEATHER_COMBAT_EFFECTS,
    get_weather_for_map,
    get_biome_for_map,
)


class TestWeatherType(unittest.TestCase):
    def test_weather_types_exist(self):
        self.assertEqual(WeatherType.CLEAR.value, "clear")
        self.assertEqual(WeatherType.RAIN.value, "rain")
        self.assertEqual(WeatherType.THUNDERSTORM.value, "thunderstorm")
        self.assertEqual(WeatherType.SNOW.value, "snow")
        self.assertEqual(WeatherType.BLIZZARD.value, "blizzard")
        self.assertEqual(WeatherType.FOG.value, "fog")
        self.assertEqual(WeatherType.SANDSTORM.value, "sandstorm")

    def test_all_weather_types_have_tints(self):
        for weather in WeatherType:
            self.assertIn(weather, WEATHER_TINTS)

    def test_all_weather_types_have_ambient(self):
        for weather in WeatherType:
            self.assertIn(weather, WEATHER_AMBIENT)

    def test_all_weather_types_have_particle_density(self):
        for weather in WeatherType:
            self.assertIn(weather, WEATHER_PARTICLE_DENSITY)


class TestWeatherParticle(unittest.TestCase):
    def test_particle_creation(self):
        particle = WeatherParticle(
            x=100.0, y=50.0, vx=-10.0, vy=400.0, size=3, alpha=150
        )
        self.assertEqual(particle.x, 100.0)
        self.assertEqual(particle.y, 50.0)
        self.assertEqual(particle.vx, -10.0)
        self.assertEqual(particle.vy, 400.0)
        self.assertEqual(particle.size, 3)
        self.assertEqual(particle.alpha, 150)

    def test_particle_defaults(self):
        particle = WeatherParticle(x=0, y=0, vx=0, vy=0, size=1, alpha=100)
        self.assertEqual(particle.lifetime, 0.0)
        self.assertEqual(particle.max_lifetime, 2.0)


class TestWeatherSystem(unittest.TestCase):
    def setUp(self):
        self.weather = WeatherSystem()

    def test_default_state(self):
        self.assertEqual(self.weather.current_weather, WeatherType.CLEAR)
        self.assertIsNone(self.weather.transition_weather)
        self.assertEqual(self.weather.transition_progress, 0.0)
        self.assertTrue(self.weather.enabled)
        self.assertFalse(self.weather.paused)

    def test_set_weather(self):
        self.weather.set_weather(WeatherType.RAIN)
        self.assertEqual(self.weather.current_weather, WeatherType.RAIN)
        self.assertIsNone(self.weather.transition_weather)

    def test_set_weather_clears_particles(self):
        self.weather.particles = [WeatherParticle(0, 0, 0, 0, 1, 100)]
        self.weather.set_weather(WeatherType.SNOW)
        self.assertEqual(len(self.weather.particles), 0)

    def test_transition_to(self):
        self.weather.transition_to(WeatherType.RAIN, duration=5.0)
        self.assertEqual(self.weather.transition_weather, WeatherType.RAIN)
        self.assertEqual(self.weather.transition_duration, 5.0)
        self.assertEqual(self.weather.transition_progress, 0.0)

    def test_transition_to_same_weather(self):
        self.weather.set_weather(WeatherType.RAIN)
        self.weather.transition_to(WeatherType.RAIN)
        self.assertIsNone(self.weather.transition_weather)

    def test_update_advances_transition(self):
        self.weather.transition_to(WeatherType.RAIN, duration=2.0)
        self.weather.update(1.0, 640, 480)
        self.assertEqual(self.weather.transition_progress, 0.5)

    def test_update_completes_transition(self):
        self.weather.transition_to(WeatherType.RAIN, duration=1.0)
        self.weather.update(1.5, 640, 480)
        self.assertEqual(self.weather.current_weather, WeatherType.RAIN)
        self.assertIsNone(self.weather.transition_weather)

    def test_update_paused(self):
        self.weather.paused = True
        self.weather.transition_to(WeatherType.RAIN, duration=1.0)
        self.weather.update(1.0, 640, 480)
        self.assertEqual(self.weather.transition_progress, 0.0)

    def test_update_disabled(self):
        self.weather.enabled = False
        self.weather.transition_to(WeatherType.RAIN, duration=1.0)
        self.weather.update(1.0, 640, 480)
        self.assertEqual(self.weather.transition_progress, 0.0)

    def test_set_map_override(self):
        self.weather.set_map_override(WeatherType.SNOW)
        self.assertEqual(self.weather.map_weather_override, WeatherType.SNOW)

    def test_clear_map_override(self):
        self.weather.set_map_override(WeatherType.SNOW)
        self.weather.clear_map_override()
        self.assertIsNone(self.weather.map_weather_override)

    def test_set_biome_weights_forest(self):
        self.weather.set_biome_weights("forest")
        self.assertIn(WeatherType.RAIN, self.weather.weather_weights)
        self.assertIn(WeatherType.FOG, self.weather.weather_weights)

    def test_set_biome_weights_desert(self):
        self.weather.set_biome_weights("desert")
        self.assertIn(WeatherType.SANDSTORM, self.weather.weather_weights)
        self.assertGreater(self.weather.weather_weights[WeatherType.CLEAR], 0.5)

    def test_set_biome_weights_tundra(self):
        self.weather.set_biome_weights("tundra")
        self.assertIn(WeatherType.SNOW, self.weather.weather_weights)
        self.assertIn(WeatherType.BLIZZARD, self.weather.weather_weights)

    def test_get_tint_color(self):
        self.weather.set_weather(WeatherType.CLEAR)
        tint = self.weather.get_tint_color()
        self.assertEqual(len(tint), 4)
        self.assertEqual(tint, WEATHER_TINTS[WeatherType.CLEAR])

    def test_get_ambient_modifier(self):
        self.weather.set_weather(WeatherType.CLEAR)
        ambient = self.weather.get_ambient_modifier()
        self.assertEqual(ambient, 1.0)

    def test_get_ambient_modifier_stormy(self):
        self.weather.set_weather(WeatherType.THUNDERSTORM)
        ambient = self.weather.get_ambient_modifier()
        self.assertLess(ambient, 1.0)

    def test_get_combat_modifiers_clear(self):
        self.weather.set_weather(WeatherType.CLEAR)
        mods = self.weather.get_combat_modifiers()
        self.assertEqual(len(mods), 0)

    def test_get_combat_modifiers_rain(self):
        self.weather.set_weather(WeatherType.RAIN)
        mods = self.weather.get_combat_modifiers()
        self.assertIn("speed", mods)
        self.assertLess(mods["speed"], 0)

    def test_get_combat_modifiers_blizzard(self):
        self.weather.set_weather(WeatherType.BLIZZARD)
        mods = self.weather.get_combat_modifiers()
        self.assertIn("speed", mods)
        self.assertIn("attack", mods)

    def test_get_weather_name(self):
        self.weather.set_weather(WeatherType.THUNDERSTORM)
        name = self.weather.get_weather_name()
        self.assertEqual(name, "Thunderstorm")

    def test_serialize(self):
        self.weather.set_weather(WeatherType.RAIN)
        self.weather.paused = True
        data = self.weather.serialize()
        self.assertEqual(data["current_weather"], "rain")
        self.assertTrue(data["paused"])

    def test_deserialize(self):
        data = {
            "current_weather": "snow",
            "transition_weather": "blizzard",
            "transition_progress": 0.5,
            "change_timer": 100.0,
            "enabled": True,
            "paused": False,
        }
        weather = WeatherSystem.deserialize(data)
        self.assertEqual(weather.current_weather, WeatherType.SNOW)
        self.assertEqual(weather.transition_weather, WeatherType.BLIZZARD)
        self.assertEqual(weather.transition_progress, 0.5)

    def test_deserialize_defaults(self):
        weather = WeatherSystem.deserialize({})
        self.assertEqual(weather.current_weather, WeatherType.CLEAR)

    def test_map_override_affects_effective_weather(self):
        self.weather.set_weather(WeatherType.CLEAR)
        self.weather.set_map_override(WeatherType.SNOW)
        tint = self.weather.get_tint_color()
        self.assertEqual(tint, WEATHER_TINTS[WeatherType.SNOW])


class TestGetWeatherForMap(unittest.TestCase):
    def test_explicit_weather_in_map_data(self):
        map_data = {"weather": "rain"}
        result = get_weather_for_map("forest_path", map_data)
        self.assertEqual(result, WeatherType.RAIN)

    def test_tundra_map(self):
        result = get_weather_for_map("frozen_tundra")
        self.assertEqual(result, WeatherType.SNOW)

    def test_volcanic_map(self):
        result = get_weather_for_map("volcanic_crater")
        self.assertEqual(result, WeatherType.ASH)

    def test_swamp_map(self):
        result = get_weather_for_map("murky_swamp")
        self.assertEqual(result, WeatherType.FOG)

    def test_cave_map(self):
        result = get_weather_for_map("dark_cave")
        self.assertEqual(result, WeatherType.CLEAR)

    def test_desert_map(self):
        result = get_weather_for_map("sand_dunes")
        self.assertIsNone(result)

    def test_generic_map(self):
        result = get_weather_for_map("town_square")
        self.assertIsNone(result)


class TestGetBiomeForMap(unittest.TestCase):
    def test_explicit_biome_in_map_data(self):
        map_data = {"biome": "volcanic"}
        result = get_biome_for_map("random_map", map_data)
        self.assertEqual(result, "volcanic")

    def test_tundra_biome(self):
        result = get_biome_for_map("frozen_peaks")
        self.assertEqual(result, "tundra")

    def test_volcanic_biome(self):
        result = get_biome_for_map("volcano_summit")
        self.assertEqual(result, "volcanic")

    def test_desert_biome(self):
        result = get_biome_for_map("sand_oasis")
        self.assertEqual(result, "desert")

    def test_swamp_biome(self):
        result = get_biome_for_map("murky_marsh")
        self.assertEqual(result, "swamp")

    def test_mountain_biome(self):
        result = get_biome_for_map("mountain_pass")
        self.assertEqual(result, "mountain")

    def test_default_forest_biome(self):
        result = get_biome_for_map("village_road")
        self.assertEqual(result, "forest")


class TestWeatherConstants(unittest.TestCase):
    def test_tints_are_rgba(self):
        for weather, tint in WEATHER_TINTS.items():
            self.assertEqual(len(tint), 4)
            for value in tint:
                self.assertGreaterEqual(value, 0)
                self.assertLessEqual(value, 255)

    def test_ambient_in_range(self):
        for weather, ambient in WEATHER_AMBIENT.items():
            self.assertGreaterEqual(ambient, 0.0)
            self.assertLessEqual(ambient, 1.0)

    def test_particle_density_non_negative(self):
        for weather, density in WEATHER_PARTICLE_DENSITY.items():
            self.assertGreaterEqual(density, 0)


if __name__ == "__main__":
    unittest.main()

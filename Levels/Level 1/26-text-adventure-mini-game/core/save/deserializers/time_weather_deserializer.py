"""Day/night and weather deserialization."""

from typing import Any, Dict

from ...weather import WeatherSystem
from .base import DeserializationResources, DeserializerContext, DomainDeserializer


def _restore_day_night(data: Dict[str, Any], context: DeserializerContext) -> None:
    if not context.day_night_cycle or "day_night" not in data:
        return
    day_night_data = data["day_night"]
    context.day_night_cycle.current_time = day_night_data.get("current_time", 360.0)
    context.day_night_cycle.day_count = day_night_data.get("day_count", 1)
    context.day_night_cycle.time_scale = day_night_data.get("time_scale", 1.0)


def _restore_weather(data: Dict[str, Any], context: DeserializerContext) -> None:
    if not context.weather_system or "weather" not in data:
        return
    weather_data = data["weather"]
    restored_weather = WeatherSystem.deserialize(weather_data)
    context.weather_system.current_weather = restored_weather.current_weather
    context.weather_system.transition_weather = restored_weather.transition_weather
    context.weather_system.transition_progress = weather_data.get("transition_progress", 0.0)
    context.weather_system.change_timer = weather_data.get("change_timer", 300.0)
    context.weather_system.enabled = weather_data.get("enabled", True)
    context.weather_system.paused = weather_data.get("paused", False)


class TimeWeatherDeserializer(DomainDeserializer):
    """Deserialize time of day and weather systems."""

    def deserialize(self, data: Dict[str, Any], context: DeserializerContext, resources: DeserializationResources) -> None:
        _restore_day_night(data, context)
        _restore_weather(data, context)

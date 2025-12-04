"""Rendering for weather effects, overlays, and day/night cycle."""

from typing import TYPE_CHECKING, Dict, Optional, Tuple

import pygame

from core.weather import WeatherType

if TYPE_CHECKING:
    from engine.world_scene import WorldScene


class WeatherOverlayRenderer:
    """Handles rendering of weather particles, overlays, and day/night effects."""

    def __init__(self, scene: "WorldScene"):
        """Initialize renderer with reference to the world scene."""
        self.scene = scene
        self._overlay_surface_cache: Optional[pygame.Surface] = None
        self._overlay_surface_size: Optional[Tuple[int, int]] = None
        self._particle_surface_cache: Dict[Tuple[WeatherType, int], pygame.Surface] = {}

    def _get_overlay_surface(self, size: Tuple[int, int]) -> pygame.Surface:
        """Get or create a reusable full-screen surface for color overlays."""
        if (
            self._overlay_surface_cache is None
            or self._overlay_surface_size != size
            or self._overlay_surface_cache.get_size() != size
        ):
            self._overlay_surface_cache = pygame.Surface(size, pygame.SRCALPHA)
            self._overlay_surface_size = size
        return self._overlay_surface_cache

    def _get_particle_surface(self, weather_type: WeatherType, size: int, base_color: Tuple[int, int, int]) -> pygame.Surface:
        """Return a cached particle surface for snow/sand/ash to avoid per-particle allocations."""
        key = (weather_type, size)
        cached = self._particle_surface_cache.get(key)
        expected_size = size * 2

        if cached is None or cached.get_size() != (expected_size, expected_size):
            surf = pygame.Surface((expected_size, expected_size), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*base_color, 255), (size, size), size)
            self._particle_surface_cache[key] = surf
            cached = surf

        return cached

    def draw_day_night_overlay(self, surface: pygame.Surface) -> None:
        """Draw the day/night cycle color overlay."""
        day_night = self.scene.get_manager_attr(
            "day_night_cycle", "_draw_day_night_overlay"
        )
        if not day_night or day_night.paused:
            return

        # Get the current tint color with alpha
        tint = day_night.get_tint_color()
        r, g, b, a = tint

        # Skip if no tint needed
        if a <= 0:
            return

        # Create overlay surface (reuse cached surface)
        screen_width, screen_height = surface.get_size()
        overlay_surface = self._get_overlay_surface((screen_width, screen_height))
        overlay_surface.fill((r, g, b, a))

        # Apply overlay with blend mode
        surface.blit(overlay_surface, (0, 0))

    def draw_weather_overlay(self, surface: pygame.Surface) -> None:
        """Draw the weather color overlay."""
        weather = self.scene.get_manager_attr(
            "weather_system", "_draw_weather_overlay"
        )
        if not weather or not weather.enabled:
            return

        # Get the current tint color with alpha
        tint = weather.get_tint_color()
        r, g, b, a = tint

        # Skip if no tint needed
        if a <= 0:
            return

        # Create overlay surface
        screen_width, screen_height = surface.get_size()
        overlay = self._get_overlay_surface((screen_width, screen_height))
        overlay.fill((r, g, b, a))

        # Apply overlay
        surface.blit(overlay, (0, 0))

        # Draw lightning flash for thunderstorms
        if weather.lightning_flash > 0:
            flash_alpha = int(weather.lightning_flash * 200)
            flash_overlay = self._get_overlay_surface((screen_width, screen_height))
            flash_overlay.fill((255, 255, 255, flash_alpha))
            surface.blit(flash_overlay, (0, 0))

    def draw_weather_particles(self, surface: pygame.Surface) -> None:
        """Draw weather particles (rain, snow, etc.)."""
        weather = self.scene.get_manager_attr(
            "weather_system", "_draw_weather_particles"
        )
        if not weather or not weather.enabled:
            return

        if not weather.particles:
            return

        active_weather = weather._get_effective_weather()

        for particle in weather.particles:
            # Calculate alpha based on lifetime
            life_ratio = particle.lifetime / particle.max_lifetime
            alpha = int(particle.alpha * (1.0 - life_ratio * 0.5))
            if alpha <= 0:
                continue

            if active_weather in (WeatherType.RAIN, WeatherType.HEAVY_RAIN, WeatherType.THUNDERSTORM):
                # Draw rain as elongated lines
                end_x = particle.x + particle.vx * 0.02
                end_y = particle.y + particle.vy * 0.02
                color = (150, 180, 220, alpha)
                # Draw line for rain
                pygame.draw.line(
                    surface,
                    color[:3],
                    (int(particle.x), int(particle.y)),
                    (int(end_x), int(end_y)),
                    max(1, particle.size // 2)
                )
            elif active_weather in (WeatherType.SNOW, WeatherType.BLIZZARD):
                particle_surface = self._get_particle_surface(WeatherType.SNOW, particle.size, (255, 255, 255))
                particle_surface.set_alpha(alpha)
                surface.blit(particle_surface, (int(particle.x) - particle.size, int(particle.y) - particle.size))
            elif active_weather == WeatherType.SANDSTORM:
                particle_surface = self._get_particle_surface(WeatherType.SANDSTORM, particle.size, (210, 180, 130))
                particle_surface.set_alpha(alpha)
                surface.blit(particle_surface, (int(particle.x) - particle.size, int(particle.y) - particle.size))
            elif active_weather == WeatherType.ASH:
                particle_surface = self._get_particle_surface(WeatherType.ASH, particle.size, (80, 80, 80))
                particle_surface.set_alpha(alpha)
                surface.blit(particle_surface, (int(particle.x) - particle.size, int(particle.y) - particle.size))

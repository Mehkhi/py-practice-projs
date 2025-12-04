"""Coordinator for overworld rendering that orchestrates focused renderers."""

from typing import TYPE_CHECKING

import pygame

from .entity_renderer import EntityRenderer
from .hud_renderer import HUDRenderer
from .tile_prop_renderer import TilePropRenderer
from .weather_overlay_renderer import WeatherOverlayRenderer

if TYPE_CHECKING:
    from engine.world_scene import WorldScene


class OverworldRendererCoordinator:
    """Coordinates all overworld renderers in the correct order."""

    def __init__(self, scene: "WorldScene"):
        """Initialize coordinator with reference to the world scene."""
        self.scene = scene
        self.tile_prop_renderer = TilePropRenderer(scene)
        self.entity_renderer = EntityRenderer(scene)
        self.hud_renderer = HUDRenderer(scene)
        self.weather_overlay_renderer = WeatherOverlayRenderer(scene)

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the overworld by coordinating all renderers."""
        current_map, entities = self.scene.renderer.get_current_entities()
        if not current_map:
            return

        screen_width, screen_height = surface.get_size()

        # 1. Draw tiles (base layer)
        self.tile_prop_renderer.draw_tiles(surface, current_map)

        # 2. Draw puzzle elements (between tiles and entities)
        self.tile_prop_renderer.draw_puzzle_elements(surface, current_map)

        # 3. Draw entities (NPCs, etc.)
        self.entity_renderer.draw_entities(surface, entities)

        # 4. Draw decorative props (culled to viewport)
        visible_props = self.scene.renderer.get_visible_props(current_map, screen_width, screen_height)
        for prop in visible_props:
            self.tile_prop_renderer.draw_prop(surface, prop)

        # 5. Draw overworld enemies (culled to viewport)
        visible_enemies = self.scene.renderer.get_visible_enemies(current_map, screen_width, screen_height)
        for enemy in visible_enemies:
            self.entity_renderer.draw_overworld_enemy(surface, enemy)

        # 6. Draw player
        self.entity_renderer.draw_player(surface)

        # 7. Draw HUD elements
        font_small = self.scene.assets.get_font("small") or self.scene.assets.get_font("default")
        font_default = self.scene.assets.get_font("default")

        # Left HUD (player stats, map name, gold)
        left_hud_rect = self.hud_renderer.draw_left_hud(surface, current_map, font_small, font_default)

        # Reset right-side HUD stacking position
        self.hud_renderer.reset_right_hud_position(screen_height)

        # Right-side HUD elements in order (stacking vertically)
        # 1. Minimap
        self.hud_renderer.draw_minimap(surface, current_map, entities)

        # 2. Time display
        self.hud_renderer.draw_time_display(surface)

        # 3. Party member stats
        self.hud_renderer.draw_party_ui(surface)

        # Quest tracking HUD (bottom-left), respecting left HUD position
        self.hud_renderer.draw_quest_tracker(surface, left_hud_rect)

        # 8. Draw day/night overlay
        self.weather_overlay_renderer.draw_day_night_overlay(surface)

        # 9. Draw weather overlay and particles
        self.weather_overlay_renderer.draw_weather_overlay(surface)
        self.weather_overlay_renderer.draw_weather_particles(surface)

        # 10. Draw achievement popups (above everything except transitions)
        if self.scene.achievement_popup_manager:
            font = self.scene.assets.get_font("default")
            small_font = self.scene.assets.get_font("small")
            self.scene.achievement_popup_manager.draw(surface, font, small_font)

        # 11. Draw post-game indicator
        self.hud_renderer.draw_post_game_indicator(surface)

        # 12. Draw screen transition overlay (topmost)
        self.scene.transition.draw(surface)

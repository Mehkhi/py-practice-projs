"""Compatibility shim for overworld renderer.

This module provides backward compatibility by re-exporting utilities and
the coordinator. The actual rendering logic has been split into focused
renderers (tile_prop_renderer, entity_renderer, hud_renderer, weather_overlay_renderer)
coordinated by OverworldRendererCoordinator.
"""

# Re-export utilities for backward compatibility
from .entity_renderer import draw_direction_indicator
from .hud_renderer import (
    draw_text_shadow,
    format_location_name,
)
from ..ui.utils import draw_rounded_panel

from .entity_renderer import EntityRenderer
from .hud_renderer import HUDRenderer
from .overworld_renderer_coordinator import OverworldRendererCoordinator
from .tile_prop_renderer import TilePropRenderer
from .weather_overlay_renderer import WeatherOverlayRenderer

# Re-export the coordinator as OverworldRenderer for backward compatibility
OverworldRenderer = OverworldRendererCoordinator

__all__ = [
    "OverworldRenderer",
    "OverworldRendererCoordinator",
    "EntityRenderer",
    "HUDRenderer",
    "TilePropRenderer",
    "WeatherOverlayRenderer",
    "draw_rounded_panel",
    "draw_text_shadow",
    "draw_direction_indicator",
    "format_location_name",
]

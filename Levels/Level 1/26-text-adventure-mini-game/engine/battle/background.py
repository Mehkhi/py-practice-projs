import pygame
import random
from typing import Tuple, Optional
from engine.theme import Colors, Gradients

class BattleBackgroundRenderer:
    """
    Handles procedural generation of battle backgrounds based on biomes.
    """
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.surface = pygame.Surface((width, height))
        self.cache = {}

    def draw(self, biome: Optional[str], backdrop_id: Optional[str] = None) -> pygame.Surface:
        """
        Draw the battle background.

        Args:
            biome: The biome type (forest, cave, desert, etc.)
            backdrop_id: Optional specific backdrop ID (unused for now, but good for cache key)

        Returns:
            The generated background surface.
        """
        # Check cache
        cache_key = (biome, backdrop_id, self.width, self.height)
        if cache_key in self.cache:
            return self.cache[cache_key]

        # Reset surface
        self.surface.fill((0, 0, 0))

        # Draw based on biome (with fallback mappings)
        if biome in ("forest", "plains"):
            self._draw_forest()
        elif biome == "cave":
            self._draw_cave()
        elif biome in ("desert", "tundra"):  # tundra gets desert-like treatment for now
            self._draw_desert()
        elif biome in ("mountain", "volcanic"):  # volcanic maps to mountain style
            self._draw_mountain()
        elif biome == "ocean":
            self._draw_ocean()
        elif biome == "swamp":
            self._draw_swamp()
        elif biome == "ruins":
            self._draw_ruins()
        elif biome == "castle":
            self._draw_castle()
        else:
            # For unknown biomes or None, use default
            self._draw_default()

        # Cache the result
        result = self.surface.copy()
        self.cache[cache_key] = result
        return result

    def _draw_gradient_rect(self, top_color: Tuple[int, int, int], bottom_color: Tuple[int, int, int], rect: pygame.Rect):
        """Helper to draw a gradient within a specific rectangle."""
        temp_surface = pygame.Surface((rect.width, rect.height))
        Gradients.vertical(temp_surface, top_color, bottom_color)
        self.surface.blit(temp_surface, rect)

    def _draw_forest(self):
        # Sky
        sky_top = (100, 150, 230)
        sky_bottom = (180, 220, 250)
        sky_rect = pygame.Rect(0, 0, self.width, self.height // 2)
        self._draw_gradient_rect(sky_top, sky_bottom, sky_rect)

        # Ground
        ground_top = (50, 160, 60)
        ground_bottom = (20, 100, 30)
        ground_rect = pygame.Rect(0, self.height // 2, self.width, self.height // 2)
        self._draw_gradient_rect(ground_top, ground_bottom, ground_rect)

        # Distant trees (silhouettes)
        for i in range(0, self.width, 40):
            height = random.randint(60, 120)
            y = self.height // 2
            points = [
                (i, y),
                (i + 20, y - height),
                (i + 40, y)
            ]
            color = (30, 80, 40)
            pygame.draw.polygon(self.surface, color, points)

        # Grass details (foreground)
        for _ in range(150):
            x = random.randint(0, self.width)
            y = random.randint(self.height // 2, self.height)
            length = random.randint(5, 15)
            pygame.draw.line(self.surface, (60, 180, 70), (x, y), (x, y - length), 1)

    def _draw_cave(self):
        # Dark rocky background
        top = (20, 20, 25)
        bottom = (40, 40, 50)
        self._draw_gradient_rect(top, bottom, self.surface.get_rect())

        # Stalactites
        for i in range(0, self.width, 50):
            height = random.randint(50, 150)
            points = [
                (i, 0),
                (i + 25, height),
                (i + 50, 0)
            ]
            pygame.draw.polygon(self.surface, (15, 15, 20), points)

        # Stalagmites
        for i in range(0, self.width, 60):
            height = random.randint(50, 150)
            points = [
                (i, self.height),
                (i + 30, self.height - height),
                (i + 60, self.height)
            ]
            pygame.draw.polygon(self.surface, (15, 15, 20), points)

        # Rock debris
        for _ in range(30):
            x = random.randint(0, self.width)
            y = random.randint(self.height - 100, self.height)
            size = random.randint(5, 15)
            pygame.draw.circle(self.surface, (30, 30, 40), (x, y), size)

    def _draw_desert(self):
        # Sky
        sky_top = (50, 100, 200)
        sky_bottom = (200, 220, 255)
        sky_rect = pygame.Rect(0, 0, self.width, self.height // 2)
        self._draw_gradient_rect(sky_top, sky_bottom, sky_rect)

        # Sun
        pygame.draw.circle(self.surface, (255, 255, 100), (self.width - 100, 80), 40)

        # Sand dunes
        ground_top = (240, 200, 100)
        ground_bottom = (200, 150, 50)
        ground_rect = pygame.Rect(0, self.height // 2, self.width, self.height // 2)
        self._draw_gradient_rect(ground_top, ground_bottom, ground_rect)

        # Dune shapes
        for i in range(0, self.width, 150):
            rect = pygame.Rect(i - 75, self.height // 2 - 30, 200, 100)
            pygame.draw.ellipse(self.surface, (220, 180, 80), rect)

    def _draw_mountain(self):
        # Sky
        sky_top = (20, 40, 80)
        sky_bottom = (100, 120, 150)
        sky_rect = pygame.Rect(0, 0, self.width, self.height // 2)
        self._draw_gradient_rect(sky_top, sky_bottom, sky_rect)

        # Mountains
        for i in range(-50, self.width, 150):
            height = random.randint(150, 250)
            y = self.height // 2 + 50
            points = [
                (i, y),
                (i + 100, y - height),
                (i + 200, y)
            ]
            # Varying grey/blue shades
            shade = random.randint(50, 80)
            color = (shade, shade + 5, shade + 10)
            pygame.draw.polygon(self.surface, color, points)

            # Snow caps
            snow_height = height // 3
            snow_points = [
                (i + 100, y - height), # Peak
                (i + 75, y - height + snow_height),
                (i + 125, y - height + snow_height)
            ]
            pygame.draw.polygon(self.surface, (240, 240, 255), snow_points)

        # Ground
        ground_top = (50, 55, 60)
        ground_bottom = (30, 35, 40)
        ground_rect = pygame.Rect(0, self.height // 2, self.width, self.height // 2)
        self._draw_gradient_rect(ground_top, ground_bottom, ground_rect)

    def _draw_ocean(self):
        # Sky
        sky_top = (100, 150, 255)
        sky_bottom = (200, 220, 255)
        sky_rect = pygame.Rect(0, 0, self.width, self.height // 2)
        self._draw_gradient_rect(sky_top, sky_bottom, sky_rect)

        # Water
        water_top = (0, 100, 200)
        water_bottom = (0, 50, 100)
        water_rect = pygame.Rect(0, self.height // 2, self.width, self.height // 2)
        self._draw_gradient_rect(water_top, water_bottom, water_rect)

        # Waves
        for _ in range(100):
            x = random.randint(0, self.width)
            y = random.randint(self.height // 2, self.height)
            length = random.randint(10, 30)
            pygame.draw.line(self.surface, (100, 200, 255), (x, y), (x + length, y), 1)

    def _draw_swamp(self):
        # Murky sky
        sky_top = (40, 50, 40)
        sky_bottom = (60, 70, 60)
        sky_rect = pygame.Rect(0, 0, self.width, self.height // 2)
        self._draw_gradient_rect(sky_top, sky_bottom, sky_rect)

        # Murky water/ground
        ground_top = (30, 40, 30)
        ground_bottom = (10, 20, 10)
        ground_rect = pygame.Rect(0, self.height // 2, self.width, self.height // 2)
        self._draw_gradient_rect(ground_top, ground_bottom, ground_rect)

        # Dead trees
        for i in range(0, self.width, 80):
            height = random.randint(60, 100)
            y = self.height // 2 + random.randint(-20, 20)
            # Trunk
            pygame.draw.line(self.surface, (40, 30, 20), (i, y), (i, y - height), 4)
            # Branches
            pygame.draw.line(self.surface, (40, 30, 20), (i, y - height + 20), (i - 20, y - height - 10), 2)
            pygame.draw.line(self.surface, (40, 30, 20), (i, y - height + 30), (i + 20, y - height - 5), 2)

    def _draw_ruins(self):
        # Dark sky
        sky_top = (30, 25, 35)
        sky_bottom = (50, 45, 55)
        sky_rect = pygame.Rect(0, 0, self.width, self.height // 2)
        self._draw_gradient_rect(sky_top, sky_bottom, sky_rect)

        # Ground
        ground_top = (40, 35, 45)
        ground_bottom = (20, 15, 25)
        ground_rect = pygame.Rect(0, self.height // 2, self.width, self.height // 2)
        self._draw_gradient_rect(ground_top, ground_bottom, ground_rect)

        # Broken pillars
        for i in range(50, self.width, 100):
            if random.random() > 0.3:
                width = 30
                height = random.randint(40, 120)
                rect = pygame.Rect(i, self.height // 2 - height + 20, width, height)
                pygame.draw.rect(self.surface, (70, 65, 75), rect)
                # Cracks
                pygame.draw.line(self.surface, (40, 35, 45), (i + 5, rect.bottom - 10), (i + 20, rect.bottom - 40), 1)

    def _draw_castle(self):
        # Dark blue/purple sky
        sky_top = (25, 25, 40)
        sky_bottom = (45, 45, 60)
        sky_rect = pygame.Rect(0, 0, self.width, self.height // 2)
        self._draw_gradient_rect(sky_top, sky_bottom, sky_rect)

        # Floor (tiled pattern hint)
        ground_top = (50, 50, 60)
        ground_bottom = (30, 30, 40)
        ground_rect = pygame.Rect(0, self.height // 2, self.width, self.height // 2)
        self._draw_gradient_rect(ground_top, ground_bottom, ground_rect)

        # Grid lines for tiles
        for x in range(0, self.width, 60):
             # Perspective lines
             pygame.draw.line(self.surface, (60, 60, 70), (x, self.height // 2), (x - (x - self.width//2), self.height), 1)

        for y in range(self.height // 2, self.height, 40):
            pygame.draw.line(self.surface, (60, 60, 70), (0, y), (self.width, y), 1)

        # Pillars in background
        for i in range(20, self.width, 120):
            rect = pygame.Rect(i, self.height // 2 - 150, 40, 150)
            pygame.draw.rect(self.surface, (40, 40, 50), rect)
            # Capital
            pygame.draw.rect(self.surface, (50, 50, 60), (i - 5, self.height // 2 - 150, 50, 10))

    def _draw_default(self):
        """Default background with gradient and subtle pattern."""
        top = Colors.BG_DARK
        bottom = Colors.BG_MAIN
        self._draw_gradient_rect(top, bottom, self.surface.get_rect())

        # Add a subtle pattern overlay using a surface
        pattern_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        grid_color = (255, 255, 255, 8)  # RGBA for subtle transparency

        for x in range(0, self.width, 40):
            pygame.draw.line(pattern_surface, grid_color, (x, 0), (x, self.height))
        for y in range(0, self.height, 40):
            pygame.draw.line(pattern_surface, grid_color, (0, y), (self.width, y))

        # Blit the pattern onto the main surface
        self.surface.blit(pattern_surface, (0, 0))

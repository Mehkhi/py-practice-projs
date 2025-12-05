"""Name entry scene for capturing player name at startup."""

import math
import random
import pygame
from typing import Optional, List, TYPE_CHECKING

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    np = None  # type: ignore[assignment]
    HAS_NUMPY = False

from .base_menu_scene import BaseMenuScene
from .ui import MessageBox, NineSlicePanel
from .assets import AssetManager
from .theme import Colors
from .config_loader import load_config
from .onboarding_theme import generate_stars, generate_particles, update_particles
from core.constants import DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT

if TYPE_CHECKING:
    from .scene import SceneManager


class NameEntryScene(BaseMenuScene):
    """Scene for entering the player's name at game start."""

    def __init__(
        self,
        manager: Optional["SceneManager"],
        scale: int = 2,
        assets: Optional[AssetManager] = None,
    ):
        super().__init__(manager, assets, scale)

        # Load config for screen dimensions
        self.config = load_config()
        self.screen_width = self.config.get("window_width", DEFAULT_WINDOW_WIDTH)
        self.screen_height = self.config.get("window_height", DEFAULT_WINDOW_HEIGHT)

        self.player_name = ""
        self.name_confirmed = False
        self.blink_timer = 0.0  # Timer for cursor blink animation
        self.fade_in = 0.0  # Fade-in animation

        # Generate star field (same style as title)
        self.stars = generate_stars(60, self.screen_width, self.screen_height, seed=42)

        # Generate floating particles
        self.particles = generate_particles(20, self.screen_width, self.screen_height, seed=456)

        # Pre-render surfaces
        self._gradient_surface: Optional[pygame.Surface] = None
        self._vignette_surface: Optional[pygame.Surface] = None

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle input events."""
        if self.name_confirmed:
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if self.player_name.strip():
                    self.name_confirmed = True
            elif event.key == pygame.K_BACKSPACE:
                if self.player_name:
                    self.player_name = self.player_name[:-1]
            elif event.key == pygame.K_ESCAPE:
                # Allow clearing with Escape
                self.player_name = ""
            elif event.unicode and event.unicode.isprintable():
                # Add character if it's printable and name isn't too long
                if len(self.player_name) < 20:
                    self.player_name += event.unicode

    def update(self, dt: float) -> None:
        """Update scene state - manages cursor blink timer."""
        self.blink_timer += dt

        # Fade in animation
        if self.fade_in < 1.0:
            self.fade_in = min(1.0, self.fade_in + dt * 2.0)

        # Update particles using centralized function
        update_particles(self.particles, dt, self.screen_width, self.screen_height)

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the name entry scene."""
        width, height = surface.get_size()
        center_x = width // 2

        # Draw gradient background
        self._draw_gradient_background(surface)

        # Draw star field
        self._draw_stars(surface)

        # Draw floating particles
        self._draw_particles(surface)

        # Draw vignette
        self._draw_vignette(surface)

        # Draw decorative ornament
        self._draw_ornament(surface, center_x, 55)

        # Draw title with effects
        self._draw_title(surface, center_x, 100)

        # Draw subtitle
        self._draw_subtitle(surface, center_x, 155)

        # Draw divider
        self._draw_divider(surface, center_x, 190)

        # Draw prompt message
        self._draw_prompt(surface, center_x, 230)

        # Draw name input field
        self._draw_input_field(surface, center_x, 290)

        # Draw footer hints
        self._draw_footer(surface, center_x, height - 40)

    def _draw_gradient_background(self, surface: pygame.Surface) -> None:
        """Draw a smooth vertical gradient background using NumPy for performance."""
        width, height = surface.get_size()

        if self._gradient_surface is None or self._gradient_surface.get_size() != (width, height):
            self._gradient_surface = pygame.Surface((width, height))
            top = Colors.BG_ONBOARDING_TOP
            bottom = Colors.BG_ONBOARDING_BOTTOM

            if HAS_NUMPY:
                # Create gradient using NumPy for better performance
                y_indices = np.arange(height, dtype=np.float32) / height
                ratios = y_indices * y_indices * (3 - 2 * y_indices)  # Smoothstep

                r = (top[0] + (bottom[0] - top[0]) * ratios).astype(np.uint8)
                g = (top[1] + (bottom[1] - top[1]) * ratios).astype(np.uint8)
                b = (top[2] + (bottom[2] - top[2]) * ratios).astype(np.uint8)

                gradient_array = np.zeros((height, width, 3), dtype=np.uint8)
                gradient_array[:, :, 0] = r[:, np.newaxis]
                gradient_array[:, :, 1] = g[:, np.newaxis]
                gradient_array[:, :, 2] = b[:, np.newaxis]

                pygame.surfarray.blit_array(self._gradient_surface, gradient_array.swapaxes(0, 1))
            else:
                self._gradient_surface.lock()
                try:
                    for y in range(height):
                        ratio = y / height
                        ratio = ratio * ratio * (3 - 2 * ratio)  # Smoothstep
                        r = int(top[0] + (bottom[0] - top[0]) * ratio)
                        g = int(top[1] + (bottom[1] - top[1]) * ratio)
                        b = int(top[2] + (bottom[2] - top[2]) * ratio)
                        pygame.draw.line(self._gradient_surface, (r, g, b), (0, y), (width - 1, y))
                finally:
                    self._gradient_surface.unlock()

        surface.blit(self._gradient_surface, (0, 0))

    def _draw_vignette(self, surface: pygame.Surface) -> None:
        """Draw a subtle vignette effect using NumPy for performance."""
        width, height = surface.get_size()

        if self._vignette_surface is None or self._vignette_surface.get_size() != (width, height):
            self._vignette_surface = pygame.Surface((width, height), pygame.SRCALPHA)
            center_x, center_y = width // 2, height // 2
            max_dist = math.sqrt(center_x ** 2 + center_y ** 2)

            if HAS_NUMPY:
                x_coords = np.arange(width, dtype=np.float32)
                y_coords = np.arange(height, dtype=np.float32)
                xx, yy = np.meshgrid(x_coords, y_coords)

                distances = np.sqrt((xx - center_x) ** 2 + (yy - center_y) ** 2)
                alphas = np.minimum(80, (distances / max_dist) ** 2 * 120).astype(np.uint8)
                pygame.surfarray.pixels_alpha(self._vignette_surface)[:] = alphas.T
            else:
                self._vignette_surface.lock()
                try:
                    for y in range(height):
                        dy = y - center_y
                        for x in range(width):
                            dx = x - center_x
                            distance = math.sqrt(dx * dx + dy * dy)
                            alpha = min(80, (distance / max_dist) ** 2 * 120)
                            self._vignette_surface.set_at((x, y), (0, 0, 0, int(alpha)))
                finally:
                    self._vignette_surface.unlock()

        surface.blit(self._vignette_surface, (0, 0))

    def _draw_stars(self, surface: pygame.Surface) -> None:
        """Draw layered star field with twinkling."""
        for star in self.stars:
            twinkle = math.sin(self.blink_timer * star["twinkle_speed"] + star["twinkle_offset"])
            brightness = int(star["base_brightness"] + 60 * twinkle)
            brightness = max(40, min(255, brightness))

            if star["layer"] == 0:
                color = (brightness, brightness, int(brightness * 1.1))
            elif star["layer"] == 1:
                color = (brightness, int(brightness * 0.95), brightness)
            else:
                color = (int(brightness * 1.1), int(brightness * 1.05), brightness)

            x, y = int(star["x"]), int(star["y"])
            size = star["size"]

            if size > 1.5:
                glow_color = (color[0] // 4, color[1] // 4, color[2] // 4)
                pygame.draw.circle(surface, glow_color, (x, y), int(size + 2))

            pygame.draw.circle(surface, color, (x, y), max(1, int(size)))

    def _draw_particles(self, surface: pygame.Surface) -> None:
        """Draw floating ambient particles."""
        width, height = surface.get_size()
        for p in self.particles:
            x, y = int(p["x"]), int(p["y"])
            if 0 <= x < width and 0 <= y < height:
                size = int(p["size"])
                alpha = int(p["alpha"] * (0.5 + 0.5 * math.sin(self.blink_timer * 2 + x * 0.1)))
                color = (*p["color"], max(20, min(255, alpha)))

                particle_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                pygame.draw.circle(particle_surf, color, (size, size), size)
                surface.blit(particle_surf, (x - size, y - size))

    def _draw_ornament(self, surface: pygame.Surface, center_x: int, y: int) -> None:
        """Draw decorative ornament."""
        accent = Colors.ACCENT
        accent_dim = Colors.ACCENT_DIM

        diamond_size = 6
        points = [
            (center_x, y - diamond_size),
            (center_x + diamond_size, y),
            (center_x, y + diamond_size),
            (center_x - diamond_size, y),
        ]
        pygame.draw.polygon(surface, accent, points)

        line_length = 80
        for i in range(line_length):
            alpha_ratio = 1.0 - (i / line_length)
            color = (
                int(accent_dim[0] * alpha_ratio),
                int(accent_dim[1] * alpha_ratio),
                int(accent_dim[2] * alpha_ratio),
            )
            pygame.draw.line(surface, color,
                           (center_x - diamond_size - 8 - i, y),
                           (center_x - diamond_size - 9 - i, y))
            pygame.draw.line(surface, color,
                           (center_x + diamond_size + 8 + i, y),
                           (center_x + diamond_size + 9 + i, y))

        pygame.draw.circle(surface, accent_dim, (center_x - diamond_size - 8, y), 2)
        pygame.draw.circle(surface, accent_dim, (center_x + diamond_size + 8, y), 2)

    def _draw_title(self, surface: pygame.Surface, center_x: int, y: int) -> None:
        """Draw the title with glow and shadow effects."""
        font_large = self.assets.get_font("large", 44) or pygame.font.Font(None, 44)
        title_text = "Begin Your Journey"

        shadow = font_large.render(title_text, True, Colors.TITLE_SHADOW)
        shadow_rect = shadow.get_rect(center=(center_x + 3, y + 3))
        surface.blit(shadow, shadow_rect)

        glow = font_large.render(title_text, True, Colors.TITLE_GLOW)
        for offset in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            glow_rect = glow.get_rect(center=(center_x + offset[0], y + offset[1]))
            surface.blit(glow, glow_rect)

        main = font_large.render(title_text, True, Colors.TITLE_MAIN)
        main_rect = main.get_rect(center=(center_x, y))
        surface.blit(main, main_rect)

    def _draw_subtitle(self, surface: pygame.Surface, center_x: int, y: int) -> None:
        """Draw the subtitle."""
        font_medium = self.assets.get_font("default", 20) or pygame.font.Font(None, 20)
        subtitle = font_medium.render("Every legend begins with a name...", True, Colors.SUBTITLE)
        subtitle_rect = subtitle.get_rect(center=(center_x, y))
        surface.blit(subtitle, subtitle_rect)

    def _draw_divider(self, surface: pygame.Surface, center_x: int, y: int) -> None:
        """Draw a decorative divider line."""
        divider_color = Colors.DIVIDER
        half_width = 100

        for i in range(half_width):
            alpha_ratio = 1.0 - (i / half_width)
            color = (
                int(divider_color[0] * alpha_ratio),
                int(divider_color[1] * alpha_ratio),
                int(divider_color[2] * alpha_ratio),
            )
            pygame.draw.line(surface, color, (center_x - i, y), (center_x - i - 1, y))
            pygame.draw.line(surface, color, (center_x + i, y), (center_x + i + 1, y))

        pygame.draw.circle(surface, Colors.ACCENT, (center_x, y), 3)

    def _draw_prompt(self, surface: pygame.Surface, center_x: int, y: int) -> None:
        """Draw the prompt message."""
        font = self.assets.get_font("default", 22) or pygame.font.Font(None, 22)
        prompt = font.render("What shall we call you, adventurer?", True, Colors.WHITE)
        prompt_rect = prompt.get_rect(center=(center_x, y))

        # Apply fade-in
        prompt_surface = pygame.Surface(prompt.get_size(), pygame.SRCALPHA)
        prompt_surface.blit(prompt, (0, 0))
        prompt_surface.set_alpha(int(255 * self.fade_in))
        surface.blit(prompt_surface, prompt_rect)

    def _draw_input_field(self, surface: pygame.Surface, center_x: int, y: int) -> None:
        """Draw the name input field with polished styling."""
        input_width = 280
        input_height = 50
        input_rect = pygame.Rect(center_x - input_width // 2, y, input_width, input_height)

        # Draw input background
        bg_surface = pygame.Surface((input_width, input_height), pygame.SRCALPHA)
        pygame.draw.rect(bg_surface, (*Colors.INPUT_BG, int(220 * self.fade_in)),
                        (0, 0, input_width, input_height), border_radius=8)

        # Animated border glow
        glow_intensity = 0.5 + 0.5 * math.sin(self.blink_timer * 3)
        border_color = (
            int(Colors.INPUT_BORDER[0] + (Colors.INPUT_FOCUS[0] - Colors.INPUT_BORDER[0]) * glow_intensity),
            int(Colors.INPUT_BORDER[1] + (Colors.INPUT_FOCUS[1] - Colors.INPUT_BORDER[1]) * glow_intensity),
            int(Colors.INPUT_BORDER[2] + (Colors.INPUT_FOCUS[2] - Colors.INPUT_BORDER[2]) * glow_intensity),
            int(200 * self.fade_in)
        )
        pygame.draw.rect(bg_surface, border_color, (0, 0, input_width, input_height), width=2, border_radius=8)
        surface.blit(bg_surface, input_rect.topleft)

        # Draw name text with cursor
        font = self.assets.get_font("default", 28) or pygame.font.Font(None, 28)
        cursor = "|" if self.blink_timer % 1.0 < 0.5 else ""
        display_text = self.player_name + cursor

        name_text = font.render(display_text, True, Colors.WHITE)
        name_rect = name_text.get_rect(center=(center_x, y + input_height // 2))
        surface.blit(name_text, name_rect)

        # Draw character count
        font_small = self.assets.get_font("small", 14) or pygame.font.Font(None, 14)
        count_text = font_small.render(f"{len(self.player_name)}/20", True, Colors.TEXT_HINT)
        count_rect = count_text.get_rect(topright=(input_rect.right - 5, input_rect.bottom + 5))
        surface.blit(count_text, count_rect)

    def _draw_footer(self, surface: pygame.Surface, center_x: int, y: int) -> None:
        """Draw footer with controls hint."""
        font_small = self.assets.get_font("small", 16) or pygame.font.Font(None, 16)

        controls = font_small.render("Enter Confirm  •  Backspace Delete  •  Esc Clear", True, Colors.TEXT_HINT)
        controls_rect = controls.get_rect(center=(center_x, y))
        surface.blit(controls, controls_rect)

"""Title screen scene with main menu."""

import math
import random
import pygame
from typing import Optional, List, Tuple, TYPE_CHECKING

from .base_menu_scene import BaseMenuScene
from .ui import Menu, NineSlicePanel, TransitionManager
from .assets import AssetManager
from .theme import Colors, Fonts, Layout, Gradients
from .config_loader import load_config
from .onboarding_theme import generate_stars, generate_particles, update_particles
from core.constants import DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT
from core.save_load import SaveManager

if TYPE_CHECKING:
    from .scene import SceneManager


class TitleScene(BaseMenuScene):
    """Title screen with New Game / Continue / Options menu."""

    def __init__(
        self,
        manager: Optional["SceneManager"],
        save_manager: SaveManager,
        scale: int = 2,
        assets: Optional[AssetManager] = None,
    ):
        super().__init__(manager, assets, scale)
        self.save_manager = save_manager

        # Load config for screen dimensions
        self.config = load_config()
        self.screen_width = self.config.get("window_width", DEFAULT_WINDOW_WIDTH)
        self.screen_height = self.config.get("window_height", DEFAULT_WINDOW_HEIGHT)

        # Check for existing saves
        self.has_save = self._check_for_saves()

        # Build menu options
        menu_options = ["New Game", "Continue", "Options", "Quit"]
        disabled = [] if self.has_save else ["Continue"]

        self.menu = Menu(
            menu_options,
            position=(0, 0),  # Will be centered dynamically
            disabled=disabled
        )

        # Animation state
        self.title_offset = 0.0
        self.title_timer = 0.0
        self.menu_fade_in = 0.0  # For fade-in animation

        # Generate star field with depth layers using centralized generator
        self.stars = generate_stars(80, self.screen_width, self.screen_height, seed=42)

        # Generate floating particles using centralized generator
        # Title scene uses accent colors from theme
        particle_colors = [Colors.ACCENT_BRIGHT, Colors.TEXT_INFO, Colors.ACCENT]
        self.particles = generate_particles(
            25, self.screen_width, self.screen_height, seed=123, colors=particle_colors
        )

        # Selection state
        self.selection_made = False
        self.selected_action: Optional[str] = None

        # Pre-render surfaces
        self._gradient_surface: Optional[pygame.Surface] = None
        self._vignette_surface: Optional[pygame.Surface] = None

        # Screen transitions
        self.transition = TransitionManager(default_duration=0.5)
        self.transition.fade_in()  # Fade in when title screen appears

    def _check_for_saves(self) -> bool:
        """Check if any save slots exist."""
        if not self.save_manager:
            return False
        # Check slots 1-3
        for slot in range(1, 4):
            if self.save_manager.slot_exists(slot):
                return True
        return False

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle input events."""
        if self.selection_made:
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.menu.move_selection(-1)
                # Skip disabled options
                while self.menu.get_selected() in self.menu.disabled:
                    self.menu.move_selection(-1)
            elif event.key == pygame.K_DOWN:
                self.menu.move_selection(1)
                # Skip disabled options
                while self.menu.get_selected() in self.menu.disabled:
                    self.menu.move_selection(1)
            elif event.key == pygame.K_RETURN:
                selected = self.menu.get_selected()
                if selected and selected not in self.menu.disabled:
                    self._handle_selection(selected)
            elif event.key == pygame.K_ESCAPE:
                # ESC quits from title screen
                self._handle_selection("Quit")

    def _handle_selection(self, selection: str) -> None:
        """Handle menu selection."""
        self.selection_made = True
        self.selected_action = selection

    def update(self, dt: float) -> None:
        """Update scene state."""
        # Update transitions
        self.transition.update(dt)

        # Animate title with smooth floating
        self.title_timer += dt
        self.title_offset = 4.0 * math.sin(self.title_timer * 1.5)

        # Fade in menu
        if self.menu_fade_in < 1.0:
            self.menu_fade_in = min(1.0, self.menu_fade_in + dt * 1.5)

        # Update menu animations (cursor bounce) using dt-based path
        self.menu.update(dt)

        # Update particles using centralized function
        update_particles(self.particles, dt, self.screen_width, self.screen_height)

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the title screen."""
        width, height = surface.get_size()
        center_x = width // 2

        # Draw gradient background
        self._draw_gradient_background(surface)

        # Draw star field
        self._draw_stars(surface)

        # Draw floating particles
        self._draw_particles(surface)

        # Draw vignette overlay
        self._draw_vignette(surface)

        # Draw decorative top ornament
        self._draw_ornament(surface, center_x, 45)

        # Draw game title with glow effect
        self._draw_title(surface, center_x, 95 + self.title_offset)

        # Draw subtitle with fade
        self._draw_subtitle(surface, center_x, 155 + self.title_offset * 0.5)

        # Draw decorative divider
        self._draw_divider(surface, center_x, 195)

        # Draw menu with polished styling
        self._draw_menu(surface, center_x, 240)

        # Draw footer
        self._draw_footer(surface, center_x, height - 35)

        # Draw transition overlay
        self.transition.draw(surface)

    def _draw_gradient_background(self, surface: pygame.Surface) -> None:
        """Draw a smooth vertical gradient background."""
        width, height = surface.get_size()

        # Cache gradient surface
        if self._gradient_surface is None or self._gradient_surface.get_size() != (width, height):
            self._gradient_surface = pygame.Surface((width, height))
            Gradients.vertical(self._gradient_surface, Colors.BG_ONBOARDING_TOP, Colors.BG_ONBOARDING_BOTTOM)

        surface.blit(self._gradient_surface, (0, 0))

    def _draw_vignette(self, surface: pygame.Surface) -> None:
        """Draw a subtle vignette effect around the edges."""
        width, height = surface.get_size()

        if self._vignette_surface is None or self._vignette_surface.get_size() != (width, height):
            self._vignette_surface = pygame.Surface((width, height), pygame.SRCALPHA)
            center_x, center_y = width // 2, height // 2
            max_dist = math.sqrt(center_x ** 2 + center_y ** 2)

            for y in range(0, height, 4):
                for x in range(0, width, 4):
                    dist = math.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
                    ratio = dist / max_dist
                    alpha = int(min(80, ratio * ratio * 120))
                    pygame.draw.rect(self._vignette_surface, (0, 0, 0, alpha), (x, y, 4, 4))

        surface.blit(self._vignette_surface, (0, 0))

    def _draw_stars(self, surface: pygame.Surface) -> None:
        """Draw layered star field with twinkling effect."""
        for star in self.stars:
            # Calculate twinkle
            twinkle = math.sin(self.title_timer * star["twinkle_speed"] + star["twinkle_offset"])
            brightness = int(star["base_brightness"] + 60 * twinkle)
            brightness = max(40, min(255, brightness))

            # Distant stars are dimmer and bluer
            if star["layer"] == 0:
                color = (brightness, brightness, int(brightness * 1.1))
            elif star["layer"] == 1:
                color = (brightness, int(brightness * 0.95), brightness)
            else:
                color = (int(brightness * 1.1), int(brightness * 1.05), brightness)

            # Draw star with glow for larger ones
            x, y = int(star["x"]), int(star["y"])
            size = star["size"]

            if size > 1.5:
                # Draw subtle glow
                glow_color = (color[0] // 4, color[1] // 4, color[2] // 4)
                pygame.draw.circle(surface, glow_color, (x, y), int(size + 2))

            pygame.draw.circle(surface, color, (x, y), max(1, int(size)))

    def _draw_particles(self, surface: pygame.Surface) -> None:
        """Draw floating ambient particles."""
        width, height = surface.get_size()
        for p in self.particles:
            x, y = int(p["x"]), int(p["y"])
            if 0 <= x < width and 0 <= y < height:
                # Create a small surface for alpha blending
                size = int(p["size"])
                alpha = int(p["alpha"] * (0.5 + 0.5 * math.sin(self.title_timer * 2 + x * 0.1)))
                color = (*p["color"], max(20, min(255, alpha)))

                particle_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                pygame.draw.circle(particle_surf, color, (size, size), size)
                surface.blit(particle_surf, (x - size, y - size))

    def _draw_ornament(self, surface: pygame.Surface, center_x: int, y: int) -> None:
        """Draw decorative ornament above title."""
        accent = Colors.ACCENT
        accent_dim = Colors.ACCENT_DIM

        # Central diamond
        diamond_size = 6
        points = [
            (center_x, y - diamond_size),
            (center_x + diamond_size, y),
            (center_x, y + diamond_size),
            (center_x - diamond_size, y),
        ]
        pygame.draw.polygon(surface, accent, points)

        # Side lines with fade
        line_length = 80
        for i in range(line_length):
            alpha_ratio = 1.0 - (i / line_length)
            color = (
                int(accent_dim[0] * alpha_ratio),
                int(accent_dim[1] * alpha_ratio),
                int(accent_dim[2] * alpha_ratio),
            )
            # Left line
            pygame.draw.line(surface, color,
                           (center_x - diamond_size - 8 - i, y),
                           (center_x - diamond_size - 9 - i, y))
            # Right line
            pygame.draw.line(surface, color,
                           (center_x + diamond_size + 8 + i, y),
                           (center_x + diamond_size + 9 + i, y))

        # Small dots at ends
        pygame.draw.circle(surface, accent_dim, (center_x - diamond_size - 8, y), 2)
        pygame.draw.circle(surface, accent_dim, (center_x + diamond_size + 8, y), 2)

    def _draw_title(self, surface: pygame.Surface, center_x: int, y: int) -> None:
        """Draw the game title with glow and shadow effects."""
        font_large = self.assets.get_font(Fonts.LARGE, Fonts.SIZE_TITLE) or pygame.font.Font(None, Fonts.SIZE_TITLE)
        title_text = "JRPG Adventure"

        # Shadow (offset down-right)
        shadow = font_large.render(title_text, True, Colors.BG_DARK)
        shadow_rect = shadow.get_rect(center=(center_x + 3, y + 3))
        surface.blit(shadow, shadow_rect)

        # Glow layer (slightly larger, behind main text)
        glow = font_large.render(title_text, True, Colors.ACCENT_DIM)
        for offset in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            glow_rect = glow.get_rect(center=(center_x + offset[0], y + offset[1]))
            surface.blit(glow, glow_rect)

        # Main title
        main = font_large.render(title_text, True, Colors.ACCENT_BRIGHT)
        main_rect = main.get_rect(center=(center_x, y))
        surface.blit(main, main_rect)

    def _draw_subtitle(self, surface: pygame.Surface, center_x: int, y: int) -> None:
        """Draw the subtitle."""
        font_medium = self.assets.get_font(Fonts.DEFAULT, Fonts.SIZE_SUBHEADING) or pygame.font.Font(None, Fonts.SIZE_SUBHEADING)
        subtitle = font_medium.render("A Classic Fantasy Tale", True, Colors.TEXT_SECONDARY)
        subtitle_rect = subtitle.get_rect(center=(center_x, y))
        surface.blit(subtitle, subtitle_rect)

    def _draw_divider(self, surface: pygame.Surface, center_x: int, y: int) -> None:
        """Draw a decorative divider line."""
        divider_color = Colors.BORDER_FOCUS
        half_width = 100

        # Gradient line from center outward
        for i in range(half_width):
            alpha_ratio = 1.0 - (i / half_width)
            color = (
                int(divider_color[0] * alpha_ratio),
                int(divider_color[1] * alpha_ratio),
                int(divider_color[2] * alpha_ratio),
            )
            pygame.draw.line(surface, color, (center_x - i, y), (center_x - i - 1, y))
            pygame.draw.line(surface, color, (center_x + i, y), (center_x + i + 1, y))

        # Center dot
        pygame.draw.circle(surface, Colors.ACCENT, (center_x, y), 3)

    def _draw_menu(self, surface: pygame.Surface, center_x: int, start_y: int) -> None:
        """Draw the menu with polished styling."""
        font = self.assets.get_font(Fonts.DEFAULT, Fonts.SIZE_SUBHEADING) or pygame.font.Font(None, Fonts.SIZE_SUBHEADING)

        # Draw the menu using the component's draw method, but we can customize the container here
        menu_width = 220
        line_height = Layout.MENU_ITEM_HEIGHT + Layout.ELEMENT_GAP  # Extra spacing for title screen
        menu_height = len(self.menu.options) * line_height + Layout.PADDING_XL
        menu_x = center_x - menu_width // 2
        menu_y = start_y

        # Draw menu background panel with shadow
        shadow_rect = pygame.Rect(menu_x - Layout.PADDING_MD + 4, menu_y - Layout.PADDING_MD + 4,
                                  menu_width + Layout.PADDING_XL, menu_height + Layout.PADDING_MD)
        shadow_surface = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surface, (0, 0, 0, int(60 * self.menu_fade_in)),
                        (0, 0, shadow_rect.width, shadow_rect.height), border_radius=Layout.CORNER_RADIUS)
        surface.blit(shadow_surface, shadow_rect.topleft)

        # Main menu background
        menu_bg_rect = pygame.Rect(menu_x - Layout.PADDING_MD, menu_y - Layout.PADDING_MD,
                                   menu_width + Layout.PADDING_XL, menu_height + Layout.PADDING_MD)

        # Semi-transparent background
        bg_surface = pygame.Surface((menu_bg_rect.width, menu_bg_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(bg_surface, (*Colors.BG_PANEL, int(220 * self.menu_fade_in)),
                        (0, 0, menu_bg_rect.width, menu_bg_rect.height), border_radius=Layout.CORNER_RADIUS)
        pygame.draw.rect(bg_surface, (*Colors.BORDER, int(180 * self.menu_fade_in)),
                        (0, 0, menu_bg_rect.width, menu_bg_rect.height), width=Layout.BORDER_WIDTH, border_radius=Layout.CORNER_RADIUS)
        surface.blit(bg_surface, menu_bg_rect.topleft)

        # Update menu position
        self.menu.position = (menu_x, menu_y + Layout.PADDING_SM)

        # Draw menu items
        self.menu.draw(surface, font=font, line_height=line_height)

    def _draw_footer(self, surface: pygame.Surface, center_x: int, y: int) -> None:
        """Draw footer with version and controls hint."""
        font_small = self.assets.get_font(Fonts.SMALL, Fonts.SIZE_SMALL) or pygame.font.Font(None, Fonts.SIZE_SMALL)

        # Controls hint
        controls = font_small.render("↑↓ Navigate  •  Enter Select  •  Esc Quit", True, Colors.TEXT_DISABLED)
        controls_rect = controls.get_rect(center=(center_x, y))
        surface.blit(controls, controls_rect)

        # Version (smaller, below controls)
        version = font_small.render("v1.0", True, Colors.TEXT_DISABLED)
        version_rect = version.get_rect(center=(center_x, y + 18))
        surface.blit(version, version_rect)

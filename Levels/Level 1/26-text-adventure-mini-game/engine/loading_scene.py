"""Loading screen scene for background asset loading."""

import threading
import pygame
from typing import Callable, Optional, TYPE_CHECKING

from .scene import Scene
from .assets import AssetManager
from .theme import Colors, Fonts
from .onboarding_theme import generate_stars, update_particles, generate_particles
from core.constants import DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT
from core.logging_utils import log_debug

if TYPE_CHECKING:
    from .scene import SceneManager


class LoadingScene(Scene):
    """Scene that displays a loading screen while background assets are loaded."""

    def __init__(
        self,
        manager: Optional["SceneManager"],
        assets: AssetManager,
        next_scene_factory: Callable[["SceneManager"], Optional[Scene]],
        scale: int = 2,
    ):
        """Initialize the loading scene.

        Args:
            manager: Scene manager instance.
            assets: AssetManager instance that needs background loading.
            next_scene_factory: Callable that returns the next scene to transition to.
                               Will be called with (manager) when loading completes.
            scale: Display scale factor.
        """
        super().__init__(manager)
        self.assets = assets
        self.next_scene_factory = next_scene_factory
        self.scale = max(1, int(scale))

        # Load config for screen dimensions
        from .config_loader import load_config
        self.config = load_config()
        self.screen_width = self.config.get("window_width", DEFAULT_WINDOW_WIDTH)
        self.screen_height = self.config.get("window_height", DEFAULT_WINDOW_HEIGHT)

        # Loading state
        self.loading_complete = False
        self.loaded_count = 0
        self.total_count = 0
        self.progress = 0.0
        self.loading_thread: Optional[threading.Thread] = None

        # Animation state
        self.loading_timer = 0.0
        self.loading_dots = ""

        # Generate star field for visual appeal
        self.stars = generate_stars(60, self.screen_width, self.screen_height, seed=42)

        # Generate floating particles
        particle_colors = [Colors.ACCENT_BRIGHT, Colors.TEXT_INFO, Colors.ACCENT]
        self.particles = generate_particles(
            20, self.screen_width, self.screen_height, seed=789, colors=particle_colors
        )

        # Start background loading
        self._start_background_loading()

    def _start_background_loading(self) -> None:
        """Start the background loading process without blocking the render loop."""
        # Avoid starting multiple threads if the scene is re-used
        if self.loading_thread and self.loading_thread.is_alive():
            return

        # Count total sprites to load
        self.total_count = len(self.assets._pending_sprites)

        if self.total_count == 0:
            # Nothing to load, immediately mark as complete
            self.progress = 1.0
            self.loading_complete = True
            log_debug("No pending sprites to load; skipping background loading thread")
            return

        def progress_callback(loaded: int, total: int) -> None:
            """Update progress during loading."""
            self.loaded_count = loaded
            self.total_count = total
            if total > 0:
                self.progress = loaded / total
            else:
                self.progress = 1.0

        def load_assets() -> None:
            """Run heavy asset loading work off the main thread."""
            try:
                self.assets.complete_background_loading(progress_callback)
                log_debug(f"Background loading completed: {self.loaded_count} sprites loaded")
            except Exception as e:
                from core.logging_utils import log_error
                log_error(f"Background loading failed: {e}")
            finally:
                # Ensure progress reflects completion even if an error occurred
                if self.total_count > 0 and self.loaded_count < self.total_count:
                    self.loaded_count = self.total_count
                self.progress = 1.0
                self.loading_complete = True

        # Complete background loading asynchronously so the loading scene can render
        self.loading_thread = threading.Thread(target=load_assets, daemon=True)
        self.loading_thread.start()

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle input events (no-op during loading)."""
        # Loading scene doesn't respond to input
        pass

    def update(self, dt: float) -> None:
        """Update scene state."""
        # Update loading animation
        self.loading_timer += dt

        # Animate loading dots
        dot_count = int(self.loading_timer * 2) % 4
        self.loading_dots = "." * dot_count

        # Update particles
        update_particles(self.particles, dt, self.screen_width, self.screen_height)

        # Transition to next scene when loading is complete
        if self.loading_complete and self.manager:
            next_scene = self.next_scene_factory(self.manager)
            if next_scene:
                self.manager.replace(next_scene)

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the loading screen."""
        width, height = surface.get_size()
        center_x = width // 2
        center_y = height // 2

        # Draw gradient background
        self._draw_gradient_background(surface)

        # Draw star field
        self._draw_stars(surface)

        # Draw floating particles
        self._draw_particles(surface)

        # Draw loading text
        font = self.assets.get_font(Fonts.DEFAULT, Fonts.SIZE_TITLE)
        if font:
            loading_text = f"Loading{self.loading_dots}"
            text_surface = font.render(loading_text, True, Colors.TEXT_PRIMARY)
            text_rect = text_surface.get_rect(center=(center_x, center_y - 40))
            surface.blit(text_surface, text_rect)

        # Draw progress bar
        self._draw_progress_bar(surface, center_x, center_y + 20)

        # Draw progress text
        if font:
            progress_text = f"{self.loaded_count} / {self.total_count}"
            if self.total_count > 0:
                progress_text += f" ({int(self.progress * 100)}%)"
            progress_surface = font.render(progress_text, True, Colors.TEXT_SECONDARY)
            progress_rect = progress_surface.get_rect(center=(center_x, center_y + 60))
            surface.blit(progress_surface, progress_rect)

    def _draw_gradient_background(self, surface: pygame.Surface) -> None:
        """Draw a gradient background."""
        from .theme import Gradients
        width, height = surface.get_size()

        # Use a dark gradient for loading screen
        gradient = Gradients.DARK_BG
        for y in range(height):
            ratio = y / height
            color = (
                int(gradient[0][0] * (1 - ratio) + gradient[1][0] * ratio),
                int(gradient[0][1] * (1 - ratio) + gradient[1][1] * ratio),
                int(gradient[0][2] * (1 - ratio) + gradient[1][2] * ratio),
            )
            pygame.draw.line(surface, color, (0, y), (width, y))

    def _draw_stars(self, surface: pygame.Surface) -> None:
        """Draw the star field."""
        for star in self.stars:
            x, y, brightness = star
            # Scale brightness to 0-255 range
            color_value = int(brightness * 255)
            color = (color_value, color_value, color_value)
            pygame.draw.circle(surface, color, (int(x), int(y)), 1)

    def _draw_particles(self, surface: pygame.Surface) -> None:
        """Draw floating particles."""
        for particle in self.particles:
            x, y, color, size, _ = particle
            pygame.draw.circle(surface, color, (int(x), int(y)), int(size))

    def _draw_progress_bar(self, surface: pygame.Surface, center_x: int, center_y: int) -> None:
        """Draw a progress bar."""
        bar_width = 300
        bar_height = 20
        bar_x = center_x - bar_width // 2
        bar_y = center_y - bar_height // 2

        # Draw background
        pygame.draw.rect(surface, Colors.BG_SECONDARY, (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(surface, Colors.BORDER, (bar_x, bar_y, bar_width, bar_height), 2)

        # Draw progress fill
        if self.progress > 0:
            fill_width = int(bar_width * self.progress)
            pygame.draw.rect(surface, Colors.ACCENT, (bar_x + 2, bar_y + 2, fill_width - 4, bar_height - 4))

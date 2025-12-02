"""Base class for menu-style scenes with common UI patterns."""

from typing import Optional, Tuple, TYPE_CHECKING

import pygame

from .scene import Scene
from .assets import AssetManager
from .ui import NineSlicePanel

if TYPE_CHECKING:
    from .scene import SceneManager


class BaseMenuScene(Scene):
    """
    Base class for menu-style scenes that share common initialization patterns.

    Provides:
    - Asset manager initialization with optional param + fallback
    - NineSlicePanel loading with graceful degradation
    - Overlay surface caching for semi-transparent backgrounds

    Subclasses should call super().__init__(manager, assets, scale) and then
    set up their scene-specific state.
    """

    def __init__(
        self,
        manager: Optional["SceneManager"],
        assets: Optional[AssetManager] = None,
        scale: int = 2,
    ):
        """
        Initialize base menu scene.

        Args:
            manager: Scene manager for navigation
            assets: Optional asset manager (creates default if None)
            scale: Asset scale factor (default 2)
        """
        super().__init__(manager)
        self.scale = max(1, int(scale))
        self.assets = assets or AssetManager(scale=self.scale)
        self.panel: Optional[NineSlicePanel] = self._load_panel()
        self._overlay_cache: Optional[pygame.Surface] = None
        self._overlay_size: Optional[Tuple[int, int]] = None

    def _load_panel(self) -> Optional[NineSlicePanel]:
        """
        Load a reusable 9-slice panel from UI sprite.

        Returns:
            NineSlicePanel if loaded successfully, None otherwise
        """
        try:
            panel_surface = self.assets.get_image("ui_panel")
            return NineSlicePanel(panel_surface)
        except Exception:
            return None

    def _get_overlay(
        self,
        size: Tuple[int, int],
        color: Tuple[int, int, int] = (20, 20, 30),
        alpha: int = 200,
    ) -> pygame.Surface:
        """
        Get or create a cached overlay surface for semi-transparent backgrounds.

        Args:
            size: (width, height) of the overlay
            color: RGB color for the overlay (default dark blue-gray)
            alpha: Transparency value 0-255 (default 200)

        Returns:
            Cached or newly created overlay surface
        """
        if self._overlay_cache is None or self._overlay_size != size:
            self._overlay_cache = pygame.Surface(size)
            self._overlay_cache.set_alpha(alpha)
            self._overlay_cache.fill(color)
            self._overlay_size = size
        return self._overlay_cache

    def draw_overlay(self, surface: pygame.Surface) -> None:
        """
        Draw a semi-transparent overlay on the surface.

        Args:
            surface: Surface to draw the overlay on
        """
        overlay = self._get_overlay(surface.get_size())
        surface.blit(overlay, (0, 0))

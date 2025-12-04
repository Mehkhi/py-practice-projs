"""Post-game welcome scene shown after returning from credits."""

from typing import List, Optional, TYPE_CHECKING

import pygame

from .scene import Scene
from .assets import AssetManager
from core.post_game import PostGameUnlock
from core.tutorial_system import TipTrigger

if TYPE_CHECKING:
    from .scene import SceneManager


class PostGameWelcomeScene(Scene):
    """
    Shown after returning from credits to congratulate player
    and explain new unlocks.
    """

    def __init__(
        self,
        manager: Optional["SceneManager"],
        unlocks: List[PostGameUnlock],
        assets: Optional[AssetManager] = None,
        scale: int = 2,
    ):
        """
        Initialize post-game welcome scene.

        Args:
            manager: Scene manager
            unlocks: List of newly unlocked content
            assets: Asset manager
            scale: Display scale
        """
        super().__init__(manager)
        self.unlocks = unlocks
        self.assets = assets or AssetManager(scale=scale)
        self.scale = max(1, int(scale))
        self.current_page = 0
        self.unlocks_per_page = 5
        self._blink_timer = 0.0
        self._blink_visible = True
        if manager and hasattr(manager, 'tutorial_manager') and manager.tutorial_manager:
            manager.tutorial_manager.trigger_tip(TipTrigger.POST_GAME_START)

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle input events."""
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
                # Return to previous scene (world or title)
                if self.manager:
                    self.manager.pop()
            elif event.key == pygame.K_UP and self.current_page > 0:
                self.current_page -= 1
            elif event.key == pygame.K_DOWN:
                max_pages = max(0, (len(self.unlocks) - 1) // self.unlocks_per_page)
                if self.current_page < max_pages:
                    self.current_page += 1

    def update(self, dt: float) -> None:
        """Update scene state."""
        self._blink_timer += dt
        if self._blink_timer >= 0.8:
            self._blink_timer = 0.0
            self._blink_visible = not self._blink_visible

    def draw(self, surface: pygame.Surface) -> None:
        """
        Display:
        - "Congratulations!" header
        - "The following content is now unlocked:"
        - List of unlocks with descriptions
        - Page navigation if many unlocks
        - "Press ENTER to continue"
        """
        width, height = surface.get_size()
        center_x = width // 2

        # Draw background
        surface.fill((20, 25, 40))

        # Get fonts
        font_large = self.assets.get_font("large", 36) or pygame.font.Font(None, 36)
        font = self.assets.get_font("default", 22) or pygame.font.Font(None, 22)
        small_font = self.assets.get_font("small", 16) or pygame.font.Font(None, 16)

        y_offset = 50

        # Draw title
        title = font_large.render("Congratulations!", True, (255, 220, 100))
        title_rect = title.get_rect(center=(center_x, y_offset))
        surface.blit(title, title_rect)
        y_offset += 60

        # Draw subtitle
        subtitle_text = "The following content is now unlocked:"
        subtitle = font.render(subtitle_text, True, (255, 255, 255))
        subtitle_rect = subtitle.get_rect(center=(center_x, y_offset))
        surface.blit(subtitle, subtitle_rect)
        y_offset += 50

        # Draw unlocks list
        start_idx = self.current_page * self.unlocks_per_page
        end_idx = min(start_idx + self.unlocks_per_page, len(self.unlocks))

        panel_width = 600
        panel_height = min(400, (end_idx - start_idx) * 80 + 40)
        panel_x = center_x - panel_width // 2
        panel_y = y_offset

        # Draw panel background
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(surface, (35, 40, 60), panel_rect, border_radius=8)
        pygame.draw.rect(surface, (80, 90, 120), panel_rect, width=2, border_radius=8)

        # Draw unlocks
        current_y = panel_y + 20
        for i in range(start_idx, end_idx):
            unlock = self.unlocks[i]

            # Unlock name
            name_text = font.render(f"• {unlock.name}", True, (255, 200, 100))
            surface.blit(name_text, (panel_x + 20, current_y))
            current_y += 25

            # Unlock description
            desc_lines = self._wrap_text(unlock.description, small_font, panel_width - 40)
            for line in desc_lines:
                desc_surf = small_font.render(line, True, (200, 200, 200))
                surface.blit(desc_surf, (panel_x + 30, current_y))
                current_y += 18

            current_y += 10

        # Draw page indicator if multiple pages
        max_pages = max(1, (len(self.unlocks) + self.unlocks_per_page - 1) // self.unlocks_per_page)
        if max_pages > 1:
            page_text = f"Page {self.current_page + 1}/{max_pages}"
            page_surf = small_font.render(page_text, True, (150, 150, 150))
            surface.blit(page_surf, (center_x - page_surf.get_width() // 2, panel_y + panel_height + 10))

        # Draw continue prompt
        continue_y = height - 50
        continue_text = "Press ENTER to continue"
        continue_color = (200, 200, 200) if self._blink_visible else (120, 120, 120)
        continue_surf = small_font.render(continue_text, True, continue_color)
        continue_rect = continue_surf.get_rect(center=(center_x, continue_y))
        surface.blit(continue_surf, continue_rect)

    def _wrap_text(self, text: str, font: pygame.font.Font, max_width: int) -> List[str]:
        """Wrap text to fit within max_width."""
        words = text.split()
        lines = []
        current_line = []

        for word in words:
            test_line = " ".join(current_line + [word])
            test_surf = font.render(test_line, True, (255, 255, 255))
            if test_surf.get_width() <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]

        if current_line:
            lines.append(" ".join(current_line))

        return lines

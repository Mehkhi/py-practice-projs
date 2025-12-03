"""Boss dossier scene for viewing discovered secret bosses and hints."""

import pygame
from typing import List, Optional, TYPE_CHECKING

from .base_menu_scene import BaseMenuScene
from .assets import AssetManager
from .theme import Colors, Fonts, Layout
from core.secret_bosses import SecretBoss, SecretBossManager
from .secret_boss_hints import HintManager

if TYPE_CHECKING:
    from .scene import SceneManager


class BossDossierScene(BaseMenuScene):
    """Shows discovered information about secret bosses.

    Accessible from pause menu after first hint discovered.
    """

    def __init__(
        self,
        manager: Optional["SceneManager"],
        secret_boss_manager: SecretBossManager,
        hint_manager: HintManager,
        assets: Optional[AssetManager] = None,
        scale: int = 2,
    ):
        super().__init__(manager, assets, scale)
        self.sbm = secret_boss_manager
        self.hm = hint_manager
        self.selected_boss_index = 0

    def get_displayable_bosses(self) -> List[SecretBoss]:
        """Get bosses that player has discovered at least one hint for."""
        discovered_boss_ids = set()
        for hint_id in self.hm.discovered_hints:
            hint = self.hm.hints.get(hint_id)
            if hint:
                discovered_boss_ids.add(hint.boss_id)

        bosses = [
            self.sbm.bosses[bid]
            for bid in discovered_boss_ids
            if bid in self.sbm.bosses
        ]
        bosses.sort(key=lambda boss: boss.boss_id)
        return bosses

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle input events."""
        if event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_ESCAPE:
            self.manager.pop()
        elif event.key == pygame.K_UP:
            bosses = self.get_displayable_bosses()
            if bosses:
                self.selected_boss_index = (self.selected_boss_index - 1) % len(bosses)
        elif event.key == pygame.K_DOWN:
            bosses = self.get_displayable_bosses()
            if bosses:
                self.selected_boss_index = (self.selected_boss_index + 1) % len(bosses)

    def draw(self, surface: pygame.Surface) -> None:
        """Draw boss dossier.

        LEFT PANEL:
        - List of discovered bosses (name hidden until defeated: "???")
        - Status icons: Unknown, Discovered, Available, Defeated

        RIGHT PANEL:
        - Boss silhouette (full image if defeated)
        - Title (if discovered)
        - Discovered hints (revealed progressively)
        - Unlock progress bar
        - "Conditions met!" if available
        - Stats preview (if defeated)
        - Unique drops (if defeated)
        """
        # Draw semi-transparent background
        self.draw_overlay(surface)

        width, height = surface.get_size()

        # Get fonts
        font = self.assets.get_font(Fonts.DEFAULT, Fonts.SIZE_BODY)
        small_font = self.assets.get_font(Fonts.SMALL, Fonts.SIZE_SMALL)
        title_font = self.assets.get_font(Fonts.LARGE, Fonts.SIZE_TITLE) or font

        # Draw title
        title_text = title_font.render("BOSS DOSSIER", True, Colors.TEXT_PRIMARY)
        title_rect = title_text.get_rect(center=(width // 2, 30))
        surface.blit(title_text, title_rect)

        # Get displayable bosses
        bosses = self.get_displayable_bosses()

        if not bosses:
            # No hints discovered yet
            no_hints_text = font.render(
                "No secret bosses discovered yet.", True, Colors.TEXT_SECONDARY
            )
            no_hints_rect = no_hints_text.get_rect(center=(width // 2, height // 2))
            surface.blit(no_hints_text, no_hints_rect)
            return

        # Ensure selected index is valid
        if self.selected_boss_index >= len(bosses):
            self.selected_boss_index = 0

        selected_boss = bosses[self.selected_boss_index] if bosses else None

        # LEFT PANEL: Boss list
        left_panel_x = Layout.SCREEN_MARGIN + 20
        left_panel_y = 70
        left_panel_width = 200
        left_panel_height = height - left_panel_y - Layout.SCREEN_MARGIN

        left_panel_rect = pygame.Rect(
            left_panel_x, left_panel_y, left_panel_width, left_panel_height
        )
        if self.panel:
            self.panel.draw(surface, left_panel_rect)
        else:
            pygame.draw.rect(surface, Colors.BG_PANEL, left_panel_rect)
            pygame.draw.rect(
                surface, Colors.BORDER, left_panel_rect, Layout.BORDER_WIDTH
            )

        # Draw boss list
        list_y = left_panel_y + 10
        for i, boss in enumerate(bosses):
            is_selected = i == self.selected_boss_index
            color = Colors.TEXT_HIGHLIGHT if is_selected else Colors.TEXT_PRIMARY

            # Determine boss name (hidden if not defeated)
            if boss.boss_id in self.sbm.defeated:
                boss_name = boss.name
            else:
                boss_name = "???"

            # Determine status
            if boss.boss_id in self.sbm.defeated:
                status = "[DEFEATED]"
                status_color = Colors.SUCCESS
            elif boss.boss_id in self.sbm.available:
                status = "[AVAILABLE]"
                status_color = Colors.WARNING
            elif boss.boss_id in self.sbm.discovered:
                status = "[DISCOVERED]"
                status_color = Colors.TEXT_SECONDARY
            else:
                status = "[UNKNOWN]"
                status_color = Colors.TEXT_DISABLED

            # Draw boss entry
            name_text = font.render(boss_name, True, color)
            surface.blit(name_text, (left_panel_x + 10, list_y))

            status_text = small_font.render(status, True, status_color)
            surface.blit(status_text, (left_panel_x + 10, list_y + 20))

            list_y += 50

        # RIGHT PANEL: Boss details
        right_panel_x = left_panel_x + left_panel_width + 20
        right_panel_y = 70
        right_panel_width = width - right_panel_x - Layout.SCREEN_MARGIN - 20
        right_panel_height = height - right_panel_y - Layout.SCREEN_MARGIN

        right_panel_rect = pygame.Rect(
            right_panel_x, right_panel_y, right_panel_width, right_panel_height
        )
        if self.panel:
            self.panel.draw(surface, right_panel_rect)
        else:
            pygame.draw.rect(surface, Colors.BG_PANEL, right_panel_rect)
            pygame.draw.rect(
                surface, Colors.BORDER, right_panel_rect, Layout.BORDER_WIDTH
            )

        if selected_boss:
            detail_y = right_panel_y + 10

            # Boss title (if discovered)
            if selected_boss.boss_id in self.sbm.discovered:
                title_text = font.render(
                    selected_boss.title, True, Colors.TEXT_PRIMARY
                )
                surface.blit(title_text, (right_panel_x + 10, detail_y))
                detail_y += 30

            # Description (if discovered)
            if selected_boss.boss_id in self.sbm.discovered:
                desc_text = small_font.render(
                    selected_boss.description, True, Colors.TEXT_SECONDARY
                )
                # Word wrap description if needed
                words = selected_boss.description.split()
                lines = []
                current_line = []
                for word in words:
                    test_line = " ".join(current_line + [word])
                    test_surface = small_font.render(test_line, True, Colors.TEXT_SECONDARY)
                    if test_surface.get_width() <= right_panel_width - 40:
                        current_line.append(word)
                    else:
                        if current_line:
                            lines.append(" ".join(current_line))
                        current_line = [word]
                if current_line:
                    lines.append(" ".join(current_line))

                for line in lines[:3]:  # Limit to 3 lines
                    line_surface = small_font.render(line, True, Colors.TEXT_SECONDARY)
                    surface.blit(line_surface, (right_panel_x + 10, detail_y))
                    detail_y += 18
                detail_y += 10

            # Discovered hints
            hints = self.hm.get_hints_for_boss(selected_boss.boss_id)
            if hints:
                hints_label = font.render("Discovered Hints:", True, Colors.TEXT_PRIMARY)
                surface.blit(hints_label, (right_panel_x + 10, detail_y))
                detail_y += 25

                for hint in hints:
                    hint_text = small_font.render(
                        f"- {hint.content}", True, Colors.TEXT_SECONDARY
                    )
                    # Word wrap
                    words = hint.content.split()
                    current_line = []
                    for word in words:
                        test_line = " ".join(current_line + [word])
                        test_surface = small_font.render(
                            test_line, True, Colors.TEXT_SECONDARY
                        )
                        if test_surface.get_width() <= right_panel_width - 50:
                            current_line.append(word)
                        else:
                            if current_line:
                                line_surface = small_font.render(
                                    " ".join(current_line), True, Colors.TEXT_SECONDARY
                                )
                                surface.blit(
                                    line_surface, (right_panel_x + 20, detail_y)
                                )
                                detail_y += 18
                            current_line = [word]
                    if current_line:
                        line_surface = small_font.render(
                            " ".join(current_line), True, Colors.TEXT_SECONDARY
                        )
                        surface.blit(line_surface, (right_panel_x + 20, detail_y))
                        detail_y += 18
                    detail_y += 5

            # Unlock progress
            discovered_count, total_count = self.hm.get_discovery_progress(
                selected_boss.boss_id
            )
            progress_text = small_font.render(
                f"Discovery Progress: {discovered_count}/{total_count}",
                True,
                Colors.TEXT_SECONDARY,
            )
            surface.blit(progress_text, (right_panel_x + 10, detail_y))
            detail_y += 20

            # Progress bar
            if total_count > 0:
                bar_width = right_panel_width - 40
                bar_height = 10
                bar_x = right_panel_x + 10
                bar_y = detail_y
                progress_ratio = discovered_count / total_count

                # Background
                bar_bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
                pygame.draw.rect(surface, Colors.BG_MAIN, bar_bg_rect)
                pygame.draw.rect(surface, Colors.BORDER, bar_bg_rect, 1)

                # Progress fill
                fill_width = int(bar_width * progress_ratio)
                if fill_width > 0:
                    fill_rect = pygame.Rect(bar_x, bar_y, fill_width, bar_height)
                    pygame.draw.rect(surface, Colors.SUCCESS, fill_rect)

                detail_y += 20

            # "Conditions met!" indicator
            if selected_boss.boss_id in self.sbm.available:
                available_text = font.render(
                    "Conditions met! Boss is available.", True, Colors.SUCCESS
                )
                surface.blit(available_text, (right_panel_x + 10, detail_y))
                detail_y += 30

            # Unique drops (if defeated)
            if selected_boss.boss_id in self.sbm.defeated and selected_boss.unique_drops:
                drops_label = font.render("Unique Drops:", True, Colors.TEXT_PRIMARY)
                surface.blit(drops_label, (right_panel_x + 10, detail_y))
                detail_y += 25

                for drop in selected_boss.unique_drops:
                    drop_text = small_font.render(f"- {drop}", True, Colors.TEXT_SECONDARY)
                    surface.blit(drop_text, (right_panel_x + 20, detail_y))
                    detail_y += 18

        # Draw help text
        help_text = "Up/Down: Navigate | ESC: Close"
        help_surface = small_font.render(help_text, True, Colors.TEXT_DISABLED)
        surface.blit(
            help_surface,
            (
                Layout.SCREEN_MARGIN,
                height - Layout.SCREEN_MARGIN - help_surface.get_height(),
            ),
        )

"""Bestiary scene for viewing discovered enemies."""

import pygame
from typing import Dict, List, Optional, TYPE_CHECKING

from .base_menu_scene import BaseMenuScene
from .assets import AssetManager
from .ui import NineSlicePanel
from .ui.utils import draw_themed_panel
from .theme import (
    Colors, Fonts, Layout,
    PANEL_TAB, PANEL_TAB_SELECTED, PANEL_ITEM_SELECTED, PANEL_SUBPANEL,
)
from core.bestiary import Bestiary, BestiaryEntry, DiscoveryLevel
from core.logging_utils import log_warning

if TYPE_CHECKING:
    from .scene import SceneManager


class BestiaryScene(BaseMenuScene):
    """Scene for viewing the enemy compendium/bestiary."""

    # Filter tabs
    TAB_ALL = 0
    TAB_DEFEATED = 1
    TAB_STUDIED = 2
    TAB_NAMES = ["All", "Defeated", "Studied"]

    def __init__(
        self,
        manager: Optional["SceneManager"],
        bestiary: Bestiary,
        assets: Optional[AssetManager] = None,
        scale: int = 2,
    ):
        super().__init__(manager, assets, scale)
        self.bestiary = bestiary

        # UI state
        self.current_tab = self.TAB_ALL
        self.selected_index = 0
        self.scroll_offset = 0
        self.max_visible_entries = 8
        self.detail_scroll = 0

        # Track sprites we've already warned about to avoid log spam in draw loop
        self._warned_sprite_ids: set[str] = set()

        # Cache filtered entries
        self._refresh_entries()

    def _refresh_entries(self) -> None:
        """Refresh the filtered entry list based on current tab."""
        all_entries = self.bestiary.get_discovered_entries()

        if self.current_tab == self.TAB_ALL:
            self.filtered_entries = all_entries
        elif self.current_tab == self.TAB_DEFEATED:
            self.filtered_entries = [
                e for e in all_entries
                if e.discovery_level.value >= DiscoveryLevel.DEFEATED.value
            ]
        elif self.current_tab == self.TAB_STUDIED:
            self.filtered_entries = [
                e for e in all_entries
                if e.discovery_level == DiscoveryLevel.STUDIED
            ]
        else:
            self.filtered_entries = all_entries

    def _get_selected_entry(self) -> Optional[BestiaryEntry]:
        """Get currently selected entry."""
        if 0 <= self.selected_index < len(self.filtered_entries):
            return self.filtered_entries[self.selected_index]
        return None

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle input events."""
        if event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_ESCAPE:
            self.manager.pop()

        elif event.key == pygame.K_LEFT:
            # Switch to previous tab
            self.current_tab = (self.current_tab - 1) % len(self.TAB_NAMES)
            self.selected_index = 0
            self.scroll_offset = 0
            self.detail_scroll = 0
            self._refresh_entries()

        elif event.key == pygame.K_RIGHT:
            # Switch to next tab
            self.current_tab = (self.current_tab + 1) % len(self.TAB_NAMES)
            self.selected_index = 0
            self.scroll_offset = 0
            self.detail_scroll = 0
            self._refresh_entries()

        elif event.key == pygame.K_UP:
            if self.filtered_entries:
                self.selected_index = (self.selected_index - 1) % len(self.filtered_entries)
                self._adjust_scroll()
                self.detail_scroll = 0

        elif event.key == pygame.K_DOWN:
            if self.filtered_entries:
                self.selected_index = (self.selected_index + 1) % len(self.filtered_entries)
                self._adjust_scroll()
                self.detail_scroll = 0

        elif event.key == pygame.K_PAGEUP:
            # Scroll details up
            self.detail_scroll = max(0, self.detail_scroll - 1)

        elif event.key == pygame.K_PAGEDOWN:
            # Scroll details down (clamped in update/draw)
            self.detail_scroll += 1

    def _adjust_scroll(self) -> None:
        """Adjust scroll offset to keep selected entry visible."""
        if self.selected_index < self.scroll_offset:
            self.scroll_offset = self.selected_index
        elif self.selected_index >= self.scroll_offset + self.max_visible_entries:
            self.scroll_offset = self.selected_index - self.max_visible_entries + 1

    def update(self, dt: float) -> None:
        """Update scene state."""
        # Clamp detail_scroll to valid range
        entry = self._get_selected_entry()
        if entry:
            # Estimate max scroll based on visible content lines
            # A rough estimate: header + stats + elements + locations + description
            max_lines = 20  # Conservative upper bound for content lines
            self.detail_scroll = max(0, min(self.detail_scroll, max(0, max_lines - 5)))
        else:
            self.detail_scroll = 0

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the bestiary."""
        # Draw semi-transparent background
        overlay = pygame.Surface(surface.get_size())
        overlay.set_alpha(200)
        overlay.fill(Colors.BG_MAIN)
        surface.blit(overlay, (0, 0))

        # Get fonts
        font = self.assets.get_font("default")
        small_font = self.assets.get_font("small")
        title_font = self.assets.get_font("large", 28) or font

        # Draw main panel background
        panel_rect = pygame.Rect(
            Layout.SCREEN_MARGIN + 10,
            Layout.SCREEN_MARGIN + 10,
            580,
            420
        )
        if self.panel:
            self.panel.draw(surface, panel_rect)
        else:
            draw_themed_panel(surface, panel_rect, panel=None)

        # Draw title with shadow
        title_shadow = title_font.render("Bestiary", True, Colors.BLACK)
        title = title_font.render("Bestiary", True, Colors.ACCENT)
        title_x = panel_rect.centerx - title.get_width() // 2
        surface.blit(title_shadow, (title_x + 1, 41))
        surface.blit(title, (title_x, 40))

        # Draw completion stats
        stats = self.bestiary.get_discovery_stats()
        if stats["total"] > 0:
            completion = f"Discovered: {stats['encountered']}/{stats['total']}"
            comp_text = small_font.render(completion, True, Colors.TEXT_SECONDARY)
            surface.blit(comp_text, (panel_rect.right - comp_text.get_width() - Layout.PADDING_LG, 45))

        # Draw tabs
        self._draw_tabs(surface, font, panel_rect)

        # Draw entry list (left side)
        self._draw_entry_list(surface, font, small_font, panel_rect)

        # Draw entry details (right side)
        self._draw_entry_details(surface, font, small_font, panel_rect)

        # Draw help text at bottom
        self._draw_help_text(surface, small_font)

    def _draw_tabs(self, surface: pygame.Surface, font: pygame.font.Font, panel_rect: pygame.Rect) -> None:
        """Draw tab buttons."""
        tab_y = 75
        tab_width = 90
        tab_spacing = Layout.ELEMENT_GAP
        total_width = len(self.TAB_NAMES) * tab_width + (len(self.TAB_NAMES) - 1) * tab_spacing
        start_x = panel_rect.centerx - total_width // 2

        for i, tab_name in enumerate(self.TAB_NAMES):
            tab_x = start_x + i * (tab_width + tab_spacing)
            tab_rect = pygame.Rect(tab_x, tab_y, tab_width, 26)

            # Draw tab background with rounded corners
            if i == self.current_tab:
                draw_themed_panel(surface, tab_rect, PANEL_TAB_SELECTED)
                color = Colors.TEXT_PRIMARY
            else:
                draw_themed_panel(surface, tab_rect, PANEL_TAB)
                color = Colors.TEXT_SECONDARY

            # Draw tab text
            tab_text = font.render(tab_name, True, color)
            text_x = tab_rect.centerx - tab_text.get_width() // 2
            text_y = tab_rect.centery - tab_text.get_height() // 2
            surface.blit(tab_text, (text_x, text_y))

    def _draw_entry_list(
        self,
        surface: pygame.Surface,
        font: pygame.font.Font,
        small_font: pygame.font.Font,
        panel_rect: pygame.Rect
    ) -> None:
        """Draw the list of bestiary entries on the left side."""
        list_rect = pygame.Rect(panel_rect.left + Layout.PADDING_MD, 110, 180, 290)

        # Draw list background with rounded corners
        draw_themed_panel(surface, list_rect, PANEL_SUBPANEL)

        if not self.filtered_entries:
            no_entries = small_font.render("No entries", True, Colors.TEXT_DISABLED)
            surface.blit(no_entries, (list_rect.centerx - no_entries.get_width() // 2, list_rect.top + Layout.PADDING_LG))
            return

        # Draw visible entries
        y = list_rect.top + Layout.PADDING_SM
        visible_entries = self.filtered_entries[self.scroll_offset:self.scroll_offset + self.max_visible_entries]

        for i, entry in enumerate(visible_entries):
            actual_index = self.scroll_offset + i
            is_selected = actual_index == self.selected_index

            # Draw selection highlight with rounded corners
            item_rect = pygame.Rect(list_rect.left + 3, y - 1, list_rect.width - 6, 34)
            if is_selected:
                draw_themed_panel(surface, item_rect, PANEL_ITEM_SELECTED)

            # Draw enemy sprite thumbnail (if available)
            sprite_x = list_rect.left + Layout.PADDING_SM
            try:
                sprite = self.assets.get_image(entry.sprite_id)
                if sprite:
                    # Scale down sprite for list
                    thumb_size = 28
                    scaled = pygame.transform.scale(sprite, (thumb_size, thumb_size))
                    surface.blit(scaled, (sprite_x, y + 2))
                    sprite_x += thumb_size + Layout.PADDING_SM
            except (pygame.error, ValueError, TypeError) as e:
                if entry.sprite_id not in self._warned_sprite_ids:
                    self._warned_sprite_ids.add(entry.sprite_id)
                    log_warning(f"Failed to load bestiary sprite '{entry.sprite_id}' for '{entry.name}': {e}")
                sprite_x += 34

            # Draw entry name
            color = Colors.TEXT_PRIMARY if is_selected else Colors.TEXT_SECONDARY
            name_text = font.render(entry.name[:12], True, color)
            surface.blit(name_text, (sprite_x, y + 2))

            # Draw discovery level indicator
            level_colors = {
                DiscoveryLevel.ENCOUNTERED: Colors.ACCENT_DIM,
                DiscoveryLevel.DEFEATED: Colors.TEXT_SUCCESS,
                DiscoveryLevel.STUDIED: Colors.TEXT_INFO,
            }
            level_color = level_colors.get(entry.discovery_level, Colors.TEXT_DISABLED)
            level_text = small_font.render(entry.discovery_level.name.title(), True, level_color)
            surface.blit(level_text, (sprite_x, y + 18))

            y += 36

        # Draw scroll indicators
        if self.scroll_offset > 0:
            up_arrow = font.render("▲", True, Colors.TEXT_SECONDARY)
            surface.blit(up_arrow, (list_rect.right - 18, list_rect.top + 4))

        if self.scroll_offset + self.max_visible_entries < len(self.filtered_entries):
            down_arrow = font.render("▼", True, Colors.TEXT_SECONDARY)
            surface.blit(down_arrow, (list_rect.right - 18, list_rect.bottom - 18))

    def _draw_entry_details(
        self,
        surface: pygame.Surface,
        font: pygame.font.Font,
        small_font: pygame.font.Font,
        panel_rect: pygame.Rect
    ) -> None:
        """Draw entry details on the right side."""
        details_rect = pygame.Rect(panel_rect.left + 200, 110, 370, 290)

        # Draw details background with rounded corners
        draw_themed_panel(surface, details_rect, PANEL_SUBPANEL)

        entry = self._get_selected_entry()
        if not entry:
            hint = small_font.render("Select an entry to view details", True, Colors.TEXT_DISABLED)
            surface.blit(hint, (details_rect.centerx - hint.get_width() // 2, details_rect.top + 50))
            return

        visible_stats = entry.get_visible_stats()
        y = details_rect.top + Layout.PADDING_MD
        padding = Layout.PADDING_MD
        line_height = Layout.LINE_HEIGHT_COMPACT

        # Build content lines
        lines = []

        # Header with sprite
        lines.append(("header", entry.name, entry.sprite_id))

        # Category
        if "category" in visible_stats:
            lines.append(("label", f"Type: {visible_stats['category'].title()}"))

        # Encounter stats
        lines.append(("stat", f"Encountered: {entry.times_encountered}  |  Defeated: {entry.times_defeated}"))
        lines.append(("spacer", ""))

        # Base stats (if revealed)
        if "base_hp" in visible_stats:
            lines.append(("section", "Base Stats"))
            lines.append(("stat", f"HP: {visible_stats['base_hp']}"))

            if "base_sp" in visible_stats:
                lines.append(("stat", f"SP: {visible_stats['base_sp']}"))
            if "base_attack" in visible_stats:
                lines.append(("stat", f"ATK: {visible_stats['base_attack']}  DEF: {visible_stats['base_defense']}"))
            if "base_magic" in visible_stats:
                lines.append(("stat", f"MAG: {visible_stats['base_magic']}  SPD: {visible_stats['base_speed']}"))
            lines.append(("spacer", ""))

        # Elemental properties
        if "weaknesses" in visible_stats and visible_stats["weaknesses"]:
            lines.append(("section", "Elemental Properties"))
            lines.append(("weakness", f"Weak: {', '.join(w.title() for w in visible_stats['weaknesses'])}"))

        if "resistances" in visible_stats and visible_stats["resistances"]:
            lines.append(("resist", f"Resist: {', '.join(r.title() for r in visible_stats['resistances'])}"))

        if "immunities" in visible_stats and visible_stats["immunities"]:
            lines.append(("immune", f"Immune: {', '.join(i.title() for i in visible_stats['immunities'])}"))

        if "absorbs" in visible_stats and visible_stats["absorbs"]:
            lines.append(("absorb", f"Absorb: {', '.join(a.title() for a in visible_stats['absorbs'])}"))

        # Locations
        if "locations" in visible_stats and visible_stats["locations"]:
            lines.append(("spacer", ""))
            lines.append(("section", "Locations"))
            for loc in visible_stats["locations"][:3]:
                loc_name = loc.replace("_", " ").title()
                lines.append(("location", f"• {loc_name}"))

        # Drops
        if "observed_drops" in visible_stats and visible_stats["observed_drops"]:
            lines.append(("spacer", ""))
            lines.append(("section", "Known Drops"))
            for drop in visible_stats["observed_drops"]:
                drop_name = drop.replace("_", " ").title()
                lines.append(("drop_item", f"{drop_name}"))

        # Description
        if "description" in visible_stats and visible_stats["description"]:
            lines.append(("spacer", ""))
            lines.append(("section", "Description"))
            # Word wrap description
            desc_lines = self._wrap_text(visible_stats["description"], small_font, details_rect.width - 2 * padding)
            for desc_line in desc_lines:
                lines.append(("desc", desc_line))

        if entry.discovery_level != DiscoveryLevel.STUDIED:
            lines.append(("spacer", ""))
            lines.append(("warning", "Defeat this foe more times to reveal full intel."))

        # Apply scroll offset
        scroll_lines = lines[self.detail_scroll:]

        # Draw lines
        for line_type, content, *extra in scroll_lines:
            if y > details_rect.bottom - 25:
                break

            if line_type == "header":
                # Draw sprite
                sprite_id = extra[0] if extra else "enemy"
                try:
                    sprite = self.assets.get_image(sprite_id)
                    if sprite:
                        sprite_size = 48
                        scaled = pygame.transform.scale(sprite, (sprite_size, sprite_size))
                        surface.blit(scaled, (details_rect.left + padding, y))
                except (pygame.error, ValueError, TypeError) as e:
                    if sprite_id not in self._warned_sprite_ids:
                        self._warned_sprite_ids.add(sprite_id)
                        log_warning(f"Failed to load bestiary detail sprite '{sprite_id}' for '{entry.name}': {e}")

                # Draw name with shadow
                name_shadow = font.render(content, True, Colors.BLACK)
                name_text = font.render(content, True, Colors.ACCENT)
                surface.blit(name_shadow, (details_rect.left + padding + 57, y + 9))
                surface.blit(name_text, (details_rect.left + padding + 56, y + 8))

                # Draw discovery level badge
                level_text = small_font.render(entry.discovery_level.name.title(), True, Colors.TEXT_INFO)
                surface.blit(level_text, (details_rect.left + padding + 56, y + 28))
                y += 55

            elif line_type == "section":
                section_text = font.render(content, True, Colors.TEXT_HIGHLIGHT)
                surface.blit(section_text, (details_rect.left + padding, y))
                y += line_height + 4

            elif line_type == "label":
                label_text = small_font.render(content, True, Colors.TEXT_SECONDARY)
                surface.blit(label_text, (details_rect.left + padding, y))
                y += line_height

            elif line_type == "stat":
                stat_text = small_font.render(content, True, Colors.TEXT_PRIMARY)
                surface.blit(stat_text, (details_rect.left + padding, y))
                y += line_height

            elif line_type == "weakness":
                weak_text = small_font.render(content, True, Colors.TEXT_ERROR)
                surface.blit(weak_text, (details_rect.left + padding, y))
                y += line_height

            elif line_type == "resist":
                resist_text = small_font.render(content, True, Colors.TEXT_SUCCESS)
                surface.blit(resist_text, (details_rect.left + padding, y))
                y += line_height

            elif line_type == "immune":
                immune_text = small_font.render(content, True, Colors.ACCENT_DIM)
                surface.blit(immune_text, (details_rect.left + padding, y))
                y += line_height

            elif line_type == "absorb":
                absorb_text = small_font.render(content, True, Colors.TEXT_INFO)
                surface.blit(absorb_text, (details_rect.left + padding, y))
                y += line_height

            elif line_type == "location":
                loc_text = small_font.render(content, True, Colors.TEXT_SECONDARY)
                surface.blit(loc_text, (details_rect.left + padding, y))
                y += line_height

            elif line_type == "drop_item":
                drop_text = small_font.render(f"• {content}", True, Colors.TEXT_PRIMARY)
                surface.blit(drop_text, (details_rect.left + padding + Layout.PADDING_SM, y))
                y += line_height
            elif line_type == "warning":
                warn_text = small_font.render(content, True, Colors.TEXT_SECONDARY)
                surface.blit(warn_text, (details_rect.left + padding, y))
                y += line_height

            elif line_type == "desc":
                desc_text = small_font.render(content, True, Colors.TEXT_SECONDARY)
                surface.blit(desc_text, (details_rect.left + padding, y))
                y += line_height

            elif line_type == "spacer":
                y += Layout.ELEMENT_GAP

    def _wrap_text(self, text: str, font: pygame.font.Font, max_width: int) -> List[str]:
        """Wrap text to fit within max_width."""
        words = text.split()
        lines = []
        current_line = []

        for word in words:
            test_line = " ".join(current_line + [word])
            if font.size(test_line)[0] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]

        if current_line:
            lines.append(" ".join(current_line))

        return lines

    def _draw_help_text(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        """Draw standardized help text at the bottom of the screen."""
        width, height = surface.get_size()

        help_text = "←/→: Tab  •  ↑/↓: Select  •  PgUp/PgDn: Scroll Details  •  ESC: Close"

        # Draw subtle background for help text
        help_surface = font.render(help_text, True, Colors.TEXT_SECONDARY)
        help_rect = help_surface.get_rect(center=(width // 2, height - Layout.SCREEN_MARGIN))

        bg_rect = help_rect.inflate(Layout.PADDING_MD * 2, Layout.PADDING_SM)
        pygame.draw.rect(surface, Colors.BG_DARK, bg_rect, border_radius=Layout.CORNER_RADIUS_SMALL)

        surface.blit(help_surface, help_rect)

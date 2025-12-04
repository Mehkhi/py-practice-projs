"""Rendering for HUD elements (panels, quest tracker, time, party stats)."""

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

import pygame

from ..ui import draw_hp_bar, draw_sp_bar, Minimap, NineSlicePanel
from ..ui.utils import draw_rounded_panel
from ..theme import Colors, Layout

if TYPE_CHECKING:
    from engine.world_scene import WorldScene
    from core.world import Map


def format_location_name(map_id: str) -> str:
    """Format a map ID into a nice display name.

    Converts 'forest_path' to 'Forest Path', etc.

    Args:
        map_id: The map identifier (e.g., 'forest_path')

    Returns:
        Formatted display name (e.g., 'Forest Path')
    """
    return map_id.replace('_', ' ').title()


def draw_text_shadow(
    surface: pygame.Surface,
    font: pygame.font.Font,
    text: str,
    pos: tuple,
    color: tuple,
    shadow_color: tuple = Colors.BLACK,
    offset: int = Layout.TEXT_SHADOW_OFFSET
) -> None:
    """Draw text with a shadow for better readability."""
    shadow = font.render(text, True, shadow_color)
    main = font.render(text, True, color)
    surface.blit(shadow, (pos[0] + offset, pos[1] + offset))
    surface.blit(main, pos)


class HUDRenderer:
    """Handles rendering of all HUD elements."""

    # Panel background and border colors (consistent theme)
    PANEL_BG = (20, 25, 40, 180)
    PANEL_BORDER = Colors.BORDER

    def __init__(self, scene: "WorldScene"):
        """Initialize renderer with reference to the world scene."""
        self.scene = scene
        # Track right-side HUD vertical position for stacking
        self._right_hud_y = 0
        self._right_hud_max_y = 0

        # Shared gold-bordered, textured panel used for overworld HUD text boxes.
        # Falls back to procedural rounded panels if the sprite is unavailable.
        self.panel: Optional[NineSlicePanel] = None
        try:
            panel_surface = self.scene.assets.get_image("ui_panel")
            if panel_surface:
                self.panel = NineSlicePanel(panel_surface)
        except Exception:
            self.panel = None

        # Caching for expensive text rendering
        self._time_display_cache: Dict[str, Any] = {}
        self._quest_tracker_cache: Dict[str, Any] = {}
        self._party_ui_cache: Dict[str, Any] = {}

    def _render_text_with_shadow_surface(
        self,
        font: pygame.font.Font,
        text: str,
        color: tuple,
        shadow_color: tuple = Colors.BLACK,
        offset: int = Layout.TEXT_SHADOW_OFFSET
    ) -> Tuple[pygame.Surface, int]:
        """Render text with shadow to a reusable surface and return it with raw text width."""
        main = font.render(text, True, color)
        shadow = font.render(text, True, shadow_color)
        width = main.get_width()
        height = main.get_height()
        surface = pygame.Surface((width + offset, height + offset), pygame.SRCALPHA)
        surface.blit(shadow, (offset, offset))
        surface.blit(main, (0, 0))
        return surface, width

    def _build_time_display_cache(
        self,
        day_night: Any,
        font: pygame.font.Font
    ) -> Dict[str, Any]:
        """Build or reuse cached time display text surfaces."""
        time_str = day_night.get_12hour_time()
        time_of_day = day_night.get_time_of_day().value
        day_count = day_night.day_count
        if day_night.is_daytime():
            time_color = (255, 255, 200)
        else:
            time_color = (180, 200, 255)

        cache_key = (time_str, time_of_day, day_count, time_color, font)
        if self._time_display_cache.get("key") == cache_key:
            return self._time_display_cache

        time_surface, time_width = self._render_text_with_shadow_surface(font, time_str, time_color)
        period_surface, period_width = self._render_text_with_shadow_surface(
            font, time_of_day.title(), Colors.TEXT_DISABLED
        )
        day_surface, day_width = self._render_text_with_shadow_surface(
            font, f"Day {day_count}", Colors.TEXT_SECONDARY
        )

        self._time_display_cache = {
            "key": cache_key,
            "time": {"surface": time_surface, "width": time_width},
            "period": {"surface": period_surface, "width": period_width},
            "day": {"surface": day_surface, "width": day_width},
        }
        return self._time_display_cache

    def _build_quest_tracker_cache(
        self,
        active_quests: List[Any],
        font: pygame.font.Font,
        max_quests: int,
        max_objectives: int
    ) -> Dict[str, Any]:
        """Cache rendered quest tracker lines until quest data changes."""
        key_data = []
        for quest in active_quests[:max_quests]:
            obj_data = tuple(
                (obj.id, obj.description, obj.completed, obj.get_progress_text())
                for obj in quest.objectives[:max_objectives]
            )
            key_data.append((quest.id, quest.name, quest.is_complete(), obj_data, len(quest.objectives)))

        cache_key = (tuple(key_data), len(active_quests), font)
        if self._quest_tracker_cache.get("key") == cache_key:
            return self._quest_tracker_cache

        header_surface, _ = self._render_text_with_shadow_surface(font, "Active Quests", Colors.TEXT_HIGHLIGHT)
        quest_entries = []
        for quest in active_quests[:max_quests]:
            quest_color = Colors.TEXT_SUCCESS if quest.is_complete() else Colors.TEXT_PRIMARY
            quest_surface, _ = self._render_text_with_shadow_surface(
                font, f"* {quest.name[:25]}", quest_color
            )

            objective_surfaces = []
            for obj in quest.objectives[:max_objectives]:
                if obj.completed:
                    obj_color = Colors.TEXT_SUCCESS
                    status = "v"
                else:
                    obj_color = Colors.TEXT_SECONDARY
                    status = obj.get_progress_text()
                obj_surface, _ = self._render_text_with_shadow_surface(
                    font, f"  {status} {obj.description[:22]}", obj_color
                )
                objective_surfaces.append(obj_surface)

            more_obj_surface = None
            if len(quest.objectives) > max_objectives:
                more_obj_surface, _ = self._render_text_with_shadow_surface(
                    font,
                    f"  ... +{len(quest.objectives) - max_objectives} more",
                    Colors.TEXT_DISABLED
                )

            quest_entries.append(
                {
                    "name": quest_surface,
                    "objectives": objective_surfaces,
                    "more_objectives": more_obj_surface,
                }
            )

        more_quests_surface = None
        if len(active_quests) > max_quests:
            more_quests_surface, _ = self._render_text_with_shadow_surface(
                font,
                f"+{len(active_quests) - max_quests} more quests (J: Journal)",
                Colors.TEXT_DISABLED
            )

        self._quest_tracker_cache = {
            "key": cache_key,
            "header": header_surface,
            "quests": quest_entries,
            "more_quests": more_quests_surface,
        }
        return self._quest_tracker_cache

    def _build_party_panel_cache(
        self,
        font_small: Optional[pygame.font.Font],
        bar_width: int,
        bar_height: int,
        padding: int,
        panel_padding: int,
        member_height: int,
        panel_width: int,
        panel_height: int
    ) -> Optional[pygame.Surface]:
        """Cache party HUD contents until HP/SP or membership changes."""
        members = [m for m in self.scene.player.party if m.stats]
        party_signature = tuple(
            (m.name, m.stats.hp, m.stats.max_hp, m.stats.sp, m.stats.max_sp, m.is_alive())
            for m in members
        )
        cache_key = (party_signature, font_small, bar_width, bar_height, member_height)
        cached = self._party_ui_cache.get("surface")
        if (
            cached
            and self._party_ui_cache.get("key") == cache_key
            and self._party_ui_cache.get("panel_size") == (panel_width, panel_height)
        ):
            return cached

        if not members:
            self._party_ui_cache = {}
            return None

        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        content_x = panel_padding
        content_y = panel_padding

        for i, member in enumerate(members):
            y_offset = i * member_height
            if font_small:
                name_color = Colors.TEXT_PRIMARY if member.is_alive() else Colors.TEXT_DISABLED
                name_surface, _ = self._render_text_with_shadow_surface(font_small, member.name, name_color)
                panel_surface.blit(name_surface, (content_x, content_y + y_offset))

            hp_y = content_y + y_offset + Layout.HUD_NAME_HEIGHT
            draw_hp_bar(
                panel_surface,
                content_x,
                hp_y,
                bar_width,
                bar_height,
                member.stats.hp,
                member.stats.max_hp,
                "",
                font=font_small
            )

            sp_y = hp_y + bar_height + padding
            draw_sp_bar(
                panel_surface,
                content_x,
                sp_y,
                bar_width,
                bar_height,
                member.stats.sp,
                member.stats.max_sp,
                "",
                font=font_small
            )

        self._party_ui_cache = {
            "key": cache_key,
            "panel_size": (panel_width, panel_height),
            "surface": panel_surface,
        }
        return panel_surface

    def draw_left_hud(
        self,
        surface: pygame.Surface,
        current_map: "Map",
        font_small: pygame.font.Font,
        font_default: pygame.font.Font
    ) -> Optional[pygame.Rect]:
        """Draw the left-side HUD (player HP/SP, map name, gold). Returns the bounding rect."""
        # Guard against missing fonts - cannot render HUD without them
        if not font_default:
            return None
        if not font_small:
            font_small = font_default  # Fallback to default font

        # --- Layout constants for a clean, spacious HUD panel ---
        hud_x = Layout.SCREEN_MARGIN_SMALL
        hud_y = Layout.SCREEN_MARGIN_SMALL
        hud_padding = Layout.PADDING_MD

        bar_width = 200
        bar_height = Layout.BAR_HEIGHT_LARGE
        vertical_gap = Layout.ELEMENT_GAP

        # Measure text to size the panel based on content instead of magic numbers
        map_name_text = format_location_name(current_map.map_id)
        gold_amount = 0
        try:
            gold_amount = int(self.scene.world.get_flag("gold", 0))
        except Exception:
            gold_amount = 0
        gold_text = f"Gold: {gold_amount}"

        # Use default font for all HUD labels to keep things consistent
        label_font = font_default
        map_name_width, map_name_height = label_font.size(map_name_text)
        gold_width, gold_height = label_font.size(gold_text)

        # Bars have labels rendered by the bar helpers; approximate their text height
        bar_label_height = label_font.get_linesize()

        content_width = max(
            bar_width,
            map_name_width,
            gold_width,
        )

        # Content is stacked vertically:
        # line 1: map name
        # line 2: HP bar
        # line 3: SP bar
        # line 4: gold
        content_height = (
            map_name_height
            + vertical_gap
            + bar_height
            + vertical_gap
            + bar_height
            + vertical_gap
            + gold_height
        )

        panel_width = content_width + hud_padding * 2
        panel_height = content_height + hud_padding * 2
        panel_rect = pygame.Rect(hud_x, hud_y, panel_width, panel_height)

        # Draw background using shared gold-bordered panel when available
        if self.panel:
            self.panel.draw(surface, panel_rect)
        else:
            # Fallback rounded panel styling
            draw_rounded_panel(
                surface,
                panel_rect,
                self.PANEL_BG,
                self.PANEL_BORDER,
                radius=Layout.CORNER_RADIUS
            )
            # Inner bevel for fanciness
            inner_rect = panel_rect.inflate(-2, -2)
            pygame.draw.rect(surface, Colors.BORDER, inner_rect, 1, border_radius=Layout.CORNER_RADIUS)

        # Start drawing content inside the panel using consistent padding and gaps
        content_x = hud_x + hud_padding
        content_y = hud_y + hud_padding

        # Map name (top line)
        draw_text_shadow(
            surface,
            label_font,
            map_name_text,
            (content_x, content_y),
            Colors.TEXT_PRIMARY,
        )
        content_y += map_name_height + vertical_gap

        # Draw HP/SP bars stacked with clean spacing
        if self.scene.player.stats:
            draw_hp_bar(
                surface,
                content_x,
                content_y,
                bar_width,
                bar_height,
                self.scene.player.stats.hp,
                self.scene.player.stats.max_hp,
                "HP",
                font=label_font,
            )
            content_y += bar_height + vertical_gap

            draw_sp_bar(
                surface,
                content_x,
                content_y,
                bar_width,
                bar_height,
                self.scene.player.stats.sp,
                self.scene.player.stats.max_sp,
                "SP",
                font=label_font,
            )
            content_y += bar_height + vertical_gap

        # Gold (bottom line)
        draw_text_shadow(
            surface,
            label_font,
            gold_text,
            (content_x, content_y),
            Colors.ACCENT,
        )

        return panel_rect

    def draw_party_ui(self, surface: pygame.Surface) -> None:
        """Draw party member HP/SP bars in the HUD."""
        if not self.scene.player.party:
            return

        font_small = self.scene.assets.get_font("small") or self.scene.assets.get_font("default")
        screen_width = surface.get_width()
        members = [m for m in self.scene.player.party if m.stats]
        if not members:
            return

        # Use layout constants for consistent spacing
        bar_width = 150
        bar_height = Layout.BAR_HEIGHT_SMALL
        padding = Layout.PADDING_XS
        panel_padding = Layout.PADDING_SM

        # Calculate panel dimensions based on party size
        member_height = Layout.HUD_NAME_HEIGHT + bar_height * 2 + padding * 2
        num_members = len(members)

        panel_width = bar_width + panel_padding * 2
        panel_height = num_members * member_height + panel_padding * 2

        # Check if panel would go off-screen
        max_y = getattr(self, '_right_hud_max_y', surface.get_height() - Layout.SCREEN_MARGIN_SMALL)
        if self._right_hud_y + panel_height > max_y:
            # Don't draw if it would overflow
            return

        # Position using the stacking tracker
        panel_x = screen_width - panel_width - Layout.SCREEN_MARGIN_SMALL
        panel_y = self._right_hud_y

        # Draw rounded panel background
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        if self.panel:
            self.panel.draw(surface, panel_rect)
        else:
            draw_rounded_panel(
                surface,
                panel_rect,
                self.PANEL_BG,
                self.PANEL_BORDER,
                radius=Layout.CORNER_RADIUS
            )

        content_surface = self._build_party_panel_cache(
            font_small,
            bar_width,
            bar_height,
            padding,
            panel_padding,
            member_height,
            panel_width,
            panel_height
        )
        if content_surface:
            surface.blit(content_surface, (panel_x, panel_y))

        # Update stacking position for next element (only if drawn)
        self._right_hud_y += panel_height + Layout.ELEMENT_GAP

    def draw_quest_tracker(
        self,
        surface: pygame.Surface,
        left_hud_rect: Optional[pygame.Rect] = None
    ) -> None:
        """Draw active quest tracking HUD in the corner of the screen."""
        if not self.scene.quest_manager:
            return

        active_quests = self.scene.quest_manager.get_active_quests()
        if not active_quests:
            return

        font = self.scene.assets.get_font("small") or self.scene.assets.get_font("default")
        if not font:
            return

        # Position in bottom-left corner, avoiding overlap with left HUD
        padding = Layout.SCREEN_MARGIN_SMALL
        line_height = Layout.LINE_HEIGHT_COMPACT
        max_quests = 2  # Show at most 2 active quests
        max_objectives = 3  # Show at most 3 objectives per quest
        quest_cache = self._build_quest_tracker_cache(active_quests, font, max_quests, max_objectives)

        # Calculate panel dimensions
        panel_width = 220
        panel_padding = Layout.PADDING_SM
        panel_height = panel_padding * 2 + 20  # Header
        for quest in active_quests[:max_quests]:
            panel_height += line_height  # Quest name
            panel_height += min(len(quest.objectives), max_objectives) * line_height
            panel_height += Layout.PADDING_XS  # Spacing between quests

        screen_height = surface.get_height()
        screen_width = surface.get_width()

        # Determine left HUD bottom position
        left_hud_bottom = padding
        if left_hud_rect:
            left_hud_bottom = left_hud_rect.bottom

        # Calculate available space below left HUD
        space_below_left_hud = screen_height - (left_hud_bottom + Layout.ELEMENT_GAP)

        # Determine best position using priority: fit on screen > avoid overlap > clip if necessary
        panel_x = padding

        # Option 1: Try to position at bottom of screen (preferred)
        bottom_position = screen_height - panel_height - padding

        # Check if bottom position would overlap with left HUD
        would_overlap = bottom_position < left_hud_bottom + Layout.ELEMENT_GAP

        # Check if panel fits on screen at all
        fits_on_screen = panel_height <= screen_height - padding * 2

        if not fits_on_screen:
            # Panel is too tall to fit anywhere - position at bottom and clip
            panel_y = screen_height - panel_height - padding
        elif not would_overlap:
            # Bottom position doesn't overlap - use it
            panel_y = bottom_position
        elif space_below_left_hud >= panel_height:
            # Panel fits below left HUD - position it there
            panel_y = left_hud_bottom + Layout.ELEMENT_GAP
        else:
            # Panel doesn't fit below left HUD but fits on screen
            # Choose the position that minimizes overlap
            # Prefer bottom position (closer to expected location) even if it slightly overlaps
            if space_below_left_hud >= panel_height * 0.7:  # At least 70% fits
                panel_y = left_hud_bottom + Layout.ELEMENT_GAP
            else:
                panel_y = bottom_position

        # Final bounds check: ensure panel doesn't go completely off-screen
        if panel_y < padding:
            panel_y = padding

        # Clip panel to screen bounds if it extends off-screen
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        screen_rect = pygame.Rect(0, 0, screen_width, screen_height)
        clipped_panel_rect = panel_rect.clip(screen_rect)

        # Only draw if panel has valid dimensions
        if clipped_panel_rect.width > 0 and clipped_panel_rect.height > 0:
            # Draw background using shared gold-bordered panel when available.
            # Note: Nine-slice cannot easily be clipped, so fall back to rounded
            # panels when the quest tracker would extend off-screen.
            if self.panel and clipped_panel_rect == panel_rect:
                self.panel.draw(surface, panel_rect)
            else:
                draw_rounded_panel(
                    surface,
                    clipped_panel_rect,
                    self.PANEL_BG,
                    self.PANEL_BORDER,
                    radius=Layout.CORNER_RADIUS
                )

                # Inner bevel for fanciness
                inner_rect = clipped_panel_rect.inflate(-2, -2)
                pygame.draw.rect(surface, Colors.BORDER, inner_rect, 1, border_radius=Layout.CORNER_RADIUS)

            # Set clipping region to prevent drawing outside panel bounds
            old_clip = surface.get_clip()
            surface.set_clip(clipped_panel_rect)

            try:
                # Draw header with shadow
                header_y = panel_y + Layout.PADDING_XS
                if header_y >= 0 and header_y < screen_height:
                    header_surface = quest_cache.get("header")
                    if header_surface:
                        surface.blit(header_surface, (panel_x + panel_padding, header_y))

                y = panel_y + 25

                for quest_entry in quest_cache.get("quests", []):
                    # Skip drawing if we're past the visible area
                    if y > screen_height - padding:
                        break

                    # Quest name
                    if y >= 0:
                        surface.blit(quest_entry["name"], (panel_x + panel_padding, y))
                    y += line_height

                    # Objectives
                    for obj_surface in quest_entry["objectives"]:
                        if y > screen_height - padding:
                            break
                        if y >= 0:
                            surface.blit(obj_surface, (panel_x + panel_padding, y))
                        y += line_height

                    # Show if more objectives exist
                    if quest_entry.get("more_objectives"):
                        if y <= screen_height - padding and y >= 0:
                            surface.blit(quest_entry["more_objectives"], (panel_x + panel_padding, y))
                        y += line_height

                    y += Layout.PADDING_XS  # Spacing between quests

                # Show if more quests exist
                if quest_cache.get("more_quests") and len(active_quests) > max_quests:
                    if y <= screen_height - padding and y >= 0:
                        surface.blit(quest_cache["more_quests"], (panel_x + panel_padding, y))
            finally:
                # Restore original clipping region
                surface.set_clip(old_clip)

    def draw_time_display(self, surface: pygame.Surface) -> None:
        """Draw the current time in the HUD."""
        day_night = self.scene.get_manager_attr(
            "day_night_cycle", "_draw_time_display"
        )
        if not day_night:
            return

        # Check if clock display is enabled
        show_clock = self.scene.config.get("day_night_show_clock", True)
        if not show_clock:
            return

        font = self.scene.assets.get_font("small") or self.scene.assets.get_font("default")
        if not font:
            return

        screen_width, _ = surface.get_size()
        time_cache = self._build_time_display_cache(day_night, font)
        time_entry = time_cache["time"]
        period_entry = time_cache["period"]
        day_entry = time_cache["day"]

        # Calculate panel dimensions
        text_widths = [time_entry["width"], day_entry["width"], period_entry["width"]]
        panel_width = max(text_widths) + Layout.PADDING_MD * 2
        # Panel height: 3 lines of compact text + vertical padding
        panel_height = Layout.LINE_HEIGHT_COMPACT * 3 + Layout.PADDING_SM

        # Check if panel would go off-screen
        max_y = getattr(self, '_right_hud_max_y', surface.get_height() - Layout.SCREEN_MARGIN_SMALL)
        if self._right_hud_y + panel_height > max_y:
            # Don't draw if it would overflow
            return

        # Position using the stacking tracker
        panel_x = screen_width - panel_width - Layout.SCREEN_MARGIN_SMALL
        panel_y = self._right_hud_y

        # Draw panel background using gold-bordered panel when available
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        if self.panel:
            self.panel.draw(surface, panel_rect)
        else:
            draw_rounded_panel(
                surface,
                panel_rect,
                self.PANEL_BG,
                self.PANEL_BORDER,
                radius=Layout.CORNER_RADIUS
            )

        # Draw text with shadows, right-aligned inside panel
        # Use compact line height for consistent vertical spacing
        text_x = panel_x + panel_width - Layout.PADDING_SM
        line_y = panel_y + Layout.PADDING_XS
        surface.blit(time_entry["surface"], (text_x - time_entry["width"], line_y))
        line_y += Layout.LINE_HEIGHT_COMPACT
        surface.blit(period_entry["surface"], (text_x - period_entry["width"], line_y))
        line_y += Layout.LINE_HEIGHT_COMPACT
        surface.blit(day_entry["surface"], (text_x - day_entry["width"], line_y))

        # Update stacking position for next element (only if drawn)
        self._right_hud_y += panel_height + Layout.ELEMENT_GAP

    def draw_minimap(self, surface: pygame.Surface, current_map: "Map", entities: List) -> None:
        """Draw the minimap if enabled."""
        if not self.scene.minimap:
            return

        self.scene.minimap.draw(
            surface,
            current_map,
            self.scene.player.x,
            self.scene.player.y,
            entities=entities,
            triggers=current_map.triggers,
        )
        if self.scene.minimap_enabled:
            minimap_size = self.scene.config.get("minimap_size", 120)
            # Account for minimap + legend below it (2 rows of compact text + padding + gap)
            legend_height = Layout.LINE_HEIGHT_COMPACT * 2 + Layout.PADDING_XS
            minimap_total_height = minimap_size + legend_height + Layout.ELEMENT_GAP
            next_y = self._right_hud_y + minimap_total_height
            # Always advance stacking; clamp so later HUD elements don't overlap if minimap overflows
            self._right_hud_y = min(next_y, self._right_hud_max_y)

    def draw_post_game_indicator(self, surface: pygame.Surface) -> None:
        """Draw a small badge when post-game content is active."""
        post_game_manager = self.scene.get_manager_attr(
            "post_game_manager", "_draw_post_game_indicator"
        )
        state = getattr(post_game_manager, "state", None) if post_game_manager else None
        if not state or not getattr(state, "final_boss_defeated", False):
            return

        font = self.scene.assets.get_font("small") or self.scene.assets.get_font("default")
        if not font:
            return

        screen_width, _ = surface.get_size()
        unlock_count = len(getattr(post_game_manager, "active_unlocks", [])) if post_game_manager else 0

        title_text = "Post-Game"
        status_text = f"{unlock_count} unlocks" if unlock_count else "New challenges"

        title_surface = font.render(title_text, True, Colors.TEXT_HIGHLIGHT)
        status_surface = font.render(status_text, True, Colors.TEXT_SUCCESS)

        panel_width = max(title_surface.get_width(), status_surface.get_width()) + Layout.PADDING_MD * 2
        panel_height = Layout.LINE_HEIGHT_COMPACT * 2 + Layout.PADDING_SM

        # Check if panel would go off-screen
        max_y = getattr(self, '_right_hud_max_y', surface.get_height() - Layout.SCREEN_MARGIN_SMALL)
        if self._right_hud_y + panel_height > max_y:
            # Don't draw if it would overflow
            return

        panel_x = screen_width - panel_width - Layout.SCREEN_MARGIN_SMALL
        panel_y = self._right_hud_y

        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        if self.panel:
            self.panel.draw(surface, panel_rect)
        else:
            draw_rounded_panel(
                surface,
                panel_rect,
                self.PANEL_BG,
                self.PANEL_BORDER,
                radius=Layout.CORNER_RADIUS_SMALL
            )

        text_x = panel_x + Layout.PADDING_MD
        line_y = panel_y + Layout.PADDING_XS
        draw_text_shadow(surface, font, title_text, (text_x, line_y), Colors.TEXT_HIGHLIGHT)
        line_y += Layout.LINE_HEIGHT_COMPACT
        draw_text_shadow(surface, font, status_text, (text_x, line_y), Colors.TEXT_SUCCESS)

        # Update stacking position for next element (only if drawn)
        self._right_hud_y += panel_height + Layout.ELEMENT_GAP

    def reset_right_hud_position(self, screen_height: int) -> None:
        """Reset the right-side HUD stacking position for a new frame."""
        self._right_hud_y = Layout.SCREEN_MARGIN_SMALL
        self._right_hud_max_y = screen_height - Layout.SCREEN_MARGIN_SMALL

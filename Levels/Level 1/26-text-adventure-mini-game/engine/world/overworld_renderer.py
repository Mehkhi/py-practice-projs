"""Rendering logic for the overworld scene.

This module handles all rendering for the overworld exploration scene.
It draws tiles, entities, player, enemies, HUD elements, weather effects,
and screen transitions.

Dependencies on WorldScene:
    - scene.player: Player entity with position, stats, sprite_id, party
    - scene.world: World state for flags, current map, active enemies
    - scene.assets: AssetManager for sprites and fonts
    - scene.config: Configuration dict for display settings
    - scene.manager: SceneManager for day/night, weather, achievements
    - scene.camera_offset: Tuple[int, int] for view position
    - scene.draw_tile: int for scaled tile size
    - scene.tile_size: int for base tile size
    - scene.scale: int for display scale factor
    - scene.projection: str for coordinate projection type
    - scene.minimap: Optional[Minimap] for minimap rendering
    - scene.minimap_enabled: bool for minimap toggle
    - scene.quest_manager: Optional[QuestManager] for quest tracking
    - scene.transition: TransitionManager for fade effects
    - scene.achievement_popup_manager: Optional popup manager
    - scene.player_facing: str for player direction ("up", "down", "left", "right")
    - scene.is_walking: bool for walking animation state
    - scene.walk_frame: int for current walk animation frame
    - scene.walk_anim_time: float for walk animation timing
    - scene.anim_time: float for idle animation timing
    - scene.bob_height: int for bobbing animation height
"""

import math
from typing import TYPE_CHECKING, Tuple, List, Optional

import pygame

from ..ui import draw_hp_bar, draw_sp_bar, Minimap, NineSlicePanel
from ..theme import Colors, Layout
from core.weather import WeatherType

if TYPE_CHECKING:
    from ..world_scene import WorldScene
    from core.world import Map, Prop
    from core.entities import OverworldEnemy


def draw_rounded_panel(
    surface: pygame.Surface,
    rect: pygame.Rect,
    bg_color: tuple,
    border_color: tuple,
    border_width: int = Layout.BORDER_WIDTH_THIN,
    radius: int = Layout.CORNER_RADIUS_SMALL
) -> None:
    """Draw a rounded panel with background and border."""
    # Draw background
    panel_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(panel_surf, bg_color, panel_surf.get_rect(), border_radius=radius)
    surface.blit(panel_surf, rect.topleft)
    # Draw border
    pygame.draw.rect(surface, border_color, rect, border_width, border_radius=radius)


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


def draw_direction_indicator(
    surface: pygame.Surface,
    screen_x: int,
    screen_y: int,
    tile_size: int,
    facing: str,
    indicator_size: int,
    fill_color: Tuple[int, int, int],
    border_color: Tuple[int, int, int],
    indicator_gap: int = 2,
) -> None:
    """Draw a triangle indicator showing facing direction.

    Args:
        surface: Pygame surface to draw on
        screen_x: Screen x position of the entity
        screen_y: Screen y position of the entity
        tile_size: Size of the entity tile in pixels
        facing: Direction the entity is facing ("up", "down", "left", "right")
        indicator_size: Size of the indicator triangle
        fill_color: RGB tuple for the indicator fill
        border_color: RGB tuple for the indicator border
        indicator_gap: Gap between entity edge and indicator (default 2)
    """
    center_x = screen_x + tile_size // 2
    center_y = screen_y + tile_size // 2

    # Calculate indicator position based on facing direction
    facing_offsets = {
        "up": (0, -tile_size // 2 - indicator_size - indicator_gap),
        "down": (0, tile_size // 2 + indicator_gap),
        "left": (-tile_size // 2 - indicator_size - indicator_gap, 0),
        "right": (tile_size // 2 + indicator_gap, 0),
    }
    offset_x, offset_y = facing_offsets.get(facing, (0, tile_size // 2))
    indicator_x = center_x + offset_x
    indicator_y = center_y + offset_y

    # Calculate triangle points based on facing direction
    if facing == "up":
        points = [
            (indicator_x, indicator_y),
            (indicator_x - indicator_size // 2, indicator_y + indicator_size),
            (indicator_x + indicator_size // 2, indicator_y + indicator_size),
        ]
    elif facing == "down":
        points = [
            (indicator_x, indicator_y + indicator_size),
            (indicator_x - indicator_size // 2, indicator_y),
            (indicator_x + indicator_size // 2, indicator_y),
        ]
    elif facing == "left":
        points = [
            (indicator_x, indicator_y),
            (indicator_x + indicator_size, indicator_y - indicator_size // 2),
            (indicator_x + indicator_size, indicator_y + indicator_size // 2),
        ]
    else:  # right
        points = [
            (indicator_x + indicator_size, indicator_y),
            (indicator_x, indicator_y - indicator_size // 2),
            (indicator_x, indicator_y + indicator_size // 2),
        ]

    # Draw the triangle with fill and border
    pygame.draw.polygon(surface, fill_color, points)
    pygame.draw.polygon(surface, border_color, points, 1)


class OverworldRenderer:
    """Handles all rendering for the overworld scene."""

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

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the overworld."""
        current_map, entities = self.scene.renderer.get_current_entities()
        screen_width, screen_height = surface.get_size()
        map_height = len(current_map.tiles)
        map_width = len(current_map.tiles[0]) if current_map.tiles else 0

        start_tile_x = max(0, self.scene.camera_offset[0] // self.scene.draw_tile)
        start_tile_y = max(0, self.scene.camera_offset[1] // self.scene.draw_tile)
        end_tile_x = min(map_width, (self.scene.camera_offset[0] + screen_width) // self.scene.draw_tile + 2)
        end_tile_y = min(map_height, (self.scene.camera_offset[1] + screen_height) // self.scene.draw_tile + 2)

        for y in range(start_tile_y, end_tile_y):
            row = current_map.tiles[y]
            for x in range(start_tile_x, end_tile_x):
                tile = row[x]

                # ------------------------------------------------------------------
                # Tile sprite overrides for small aesthetic tweaks.
                #
                # The base map data uses a darker grass variant with black speckles
                # (`grass_dark`) to add variety. In practice it can look noisy and
                # out‑of‑place compared to the softer grass tiles, especially on the
                # early "forest_path" map you see first in the game.
                #
                # Instead of editing the JSON map data everywhere, we can do a
                # lightweight visual override here at render time: whenever we're
                # on the "forest_path" map, draw `grass_dark` tiles using the
                # regular `grass` sprite. This keeps the code beginner‑friendly
                # and easy to change later.
                # ------------------------------------------------------------------
                sprite_id = tile.sprite_id
                if current_map.map_id == "forest_path" and sprite_id == "grass_dark":
                    sprite_id = "grass"

                tile_surface = self.scene.assets.get_tile_surface(sprite_id, self.scene.tile_size)

                screen_x, screen_y = self.scene.renderer.project(x, y)
                surface.blit(tile_surface, (screen_x, screen_y))

        # Draw puzzle elements (between tiles and entities)
        self._draw_puzzle_elements(surface, current_map)

        for entity in entities:
            sprite = self.scene.assets.get_image(entity.sprite_id, (self.scene.tile_size, self.scene.tile_size))
            screen_x, screen_y = self.scene.renderer.project(entity.x, entity.y)
            surface.blit(sprite, (screen_x, screen_y))

        # Draw decorative props
        for prop in current_map.props:
            self._draw_prop(surface, prop)

        # Draw overworld enemies
        active_enemies = self.scene.world.get_active_overworld_enemies(current_map.map_id)
        for enemy in active_enemies:
            self._draw_overworld_enemy(surface, enemy)

        # Draw player with improved walking animation
        player_screen_x, player_screen_y = self.scene.renderer.project(self.scene.player.x, self.scene.player.y)
        self._draw_player(surface, player_screen_x, player_screen_y)

        # Draw highlight on current tile
        highlight_rect = pygame.Rect(player_screen_x, player_screen_y, self.scene.draw_tile, self.scene.draw_tile)
        pygame.draw.rect(surface, Colors.WHITE, highlight_rect, 1)

        font_small = self.scene.assets.get_font("small") or self.scene.assets.get_font("default")
        font_default = self.scene.assets.get_font("default")

        # Draw left HUD (player stats, map name, gold)
        left_hud_rect = self._draw_left_hud(surface, current_map, font_small, font_default)

        # Reset right-side HUD stacking position
        screen_height = surface.get_height()
        self._right_hud_y = Layout.SCREEN_MARGIN_SMALL
        self._right_hud_max_y = screen_height - Layout.SCREEN_MARGIN_SMALL  # Maximum y before going off-screen

        # Draw right-side HUD elements in order (stacking vertically)
        # 1. Minimap
        if self.scene.minimap:
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

        # 2. Time display
        self._draw_time_display(surface)

        # 3. Party member stats (weather HUD panel removed)
        self._draw_party_ui(surface)

        # Draw quest tracking HUD (bottom-left), respecting left HUD position
        self._draw_quest_tracker(surface, left_hud_rect)

        # Draw day/night overlay
        self._draw_day_night_overlay(surface)

        # Draw weather overlay and particles
        self._draw_weather_overlay(surface)
        self._draw_weather_particles(surface)

        # Draw achievement popups (above everything except transitions)
        if self.scene.achievement_popup_manager:
            font = self.scene.assets.get_font("default")
            small_font = self.scene.assets.get_font("small")
            self.scene.achievement_popup_manager.draw(surface, font, small_font)

        # Draw post-game indicator
        self._draw_post_game_indicator(surface)

        # Draw screen transition overlay
        self.scene.transition.draw(surface)

    def _draw_left_hud(
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
        bar_height = Layout.BAR_HEIGHT
        vertical_gap = Layout.ELEMENT_GAP_SMALL

        # Measure text to size the panel based on content instead of magic numbers
        map_name_text = current_map.map_id
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

    def _draw_player(self, surface: pygame.Surface, screen_x: int, screen_y: int) -> None:
        """Draw the player with improved walking animation."""
        # Get base player sprite
        player_surface = self.scene.assets.get_image(self.scene.player.sprite_id, (self.scene.tile_size, self.scene.tile_size))

        # Calculate animation offsets
        if self.scene.is_walking:
            # Walking animation: bob up and down more pronounced, with horizontal sway
            walk_bob = int(self.scene.bob_height * 1.5 * abs(math.sin(self.scene.walk_frame * math.pi / 2)))
            # Slight horizontal sway for more natural movement
            walk_sway = int(self.scene.scale * math.sin(self.scene.walk_frame * math.pi / 2))

            # Apply walking offsets
            draw_x = screen_x + walk_sway
            draw_y = screen_y - walk_bob

            # Draw walking "dust" effect (small particles behind player)
            self._draw_walk_dust(surface, screen_x, screen_y)
        else:
            # Idle animation: gentle breathing bob
            idle_bob = int(self.scene.bob_height * 0.5 * abs(math.sin(self.scene.anim_time * 2)))
            draw_x = screen_x
            draw_y = screen_y - idle_bob

        # Apply directional flip for left/right facing
        if self.scene.player_facing == "left":
            player_surface = pygame.transform.flip(player_surface, True, False)

        # Draw shadow under player
        shadow_rect = pygame.Rect(
            screen_x + self.scene.draw_tile // 4,
            screen_y + self.scene.draw_tile - 4 * self.scene.scale,
            self.scene.draw_tile // 2,
            4 * self.scene.scale
        )
        shadow_surface = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surface, (0, 0, 0, 60), shadow_surface.get_rect())
        surface.blit(shadow_surface, shadow_rect)

        # Draw the player sprite
        surface.blit(player_surface, (draw_x, draw_y))

        # Draw direction indicator (small arrow showing facing direction)
        self._draw_facing_indicator(surface, screen_x, screen_y)

    def _draw_walk_dust(self, surface: pygame.Surface, screen_x: int, screen_y: int) -> None:
        """Draw dust particles when walking."""
        if self.scene.walk_frame in (1, 3):  # Only show dust on certain frames
            dust_size = 3 * self.scene.scale
            dust_alpha = 100 - int(self.scene.walk_anim_time * 300)
            if dust_alpha > 0:
                # Position dust behind the player based on facing direction
                offsets = {
                    "up": (self.scene.draw_tile // 2, self.scene.draw_tile + dust_size),
                    "down": (self.scene.draw_tile // 2, -dust_size),
                    "left": (self.scene.draw_tile + dust_size, self.scene.draw_tile // 2),
                    "right": (-dust_size, self.scene.draw_tile // 2),
                }
                offset_x, offset_y = offsets.get(self.scene.player_facing, (0, self.scene.draw_tile))
                dust_x = screen_x + offset_x - dust_size // 2
                dust_y = screen_y + offset_y - dust_size // 2

                dust_surface = pygame.Surface((dust_size * 2, dust_size * 2), pygame.SRCALPHA)
                pygame.draw.circle(dust_surface, (180, 160, 140, dust_alpha), (dust_size, dust_size), dust_size)
                surface.blit(dust_surface, (dust_x, dust_y))

    def _draw_facing_indicator(self, surface: pygame.Surface, screen_x: int, screen_y: int) -> None:
        """Draw a small indicator showing which direction the player is facing."""
        # Player indicator: subtle blue, smaller size
        draw_direction_indicator(
            surface=surface,
            screen_x=screen_x,
            screen_y=screen_y,
            tile_size=self.scene.draw_tile,
            facing=self.scene.player_facing,
            indicator_size=4 * self.scene.scale,
            fill_color=(100, 150, 255),
            border_color=(60, 100, 200),
            indicator_gap=2,
        )

    def _draw_puzzle_elements(self, surface: pygame.Surface, current_map: "Map") -> None:
        """Draw puzzle elements on the map."""
        if not hasattr(self.scene, 'puzzle_manager') or not self.scene.puzzle_manager:
            return

        puzzle = self.scene.puzzle_manager.get_puzzle_for_map(current_map.map_id)
        if not puzzle:
            return

        from core.puzzles import PuzzleElementType

        for element in puzzle.elements.values():
            screen_x, screen_y = self.scene.renderer.project(element.x, element.y)

            # Get sprite based on element type and state
            sprite_id = element.sprite_id
            if element.element_type == PuzzleElementType.DOOR:
                # Use open/closed sprite based on state
                if element.state == "open" and "data" in element.__dict__:
                    sprite_id = element.data.get("open_sprite", sprite_id)
                elif element.state == "closed":
                    sprite_id = element.sprite_id
            elif element.element_type == PuzzleElementType.PRESSURE_PLATE:
                # Use pressed sprite if activated
                if element.state == "activated":
                    sprite_id = element.data.get("pressed_sprite", sprite_id)

            if sprite_id:
                sprite = self.scene.assets.get_image(
                    sprite_id, (self.scene.tile_size, self.scene.tile_size)
                )

                # Apply visual feedback based on visual_state
                visual_state = getattr(element, 'visual_state', 'normal')
                if visual_state == "flashing":
                    # Flash effect - alternate between normal and bright
                    flash_cycle = int(self.scene.anim_time * 5) % 2
                    if flash_cycle == 0:
                        # Bright flash
                        flash_surface = pygame.Surface(sprite.get_size(), pygame.SRCALPHA)
                        flash_surface.fill((255, 255, 255, 100))
                        sprite = sprite.copy()
                        sprite.blit(flash_surface, (0, 0), special_flags=pygame.BLEND_ADD)
                elif visual_state == "glowing":
                    # Glow effect - add yellow glow
                    glow_surface = pygame.Surface(sprite.get_size(), pygame.SRCALPHA)
                    glow_surface.fill((255, 255, 0, 80))
                    sprite = sprite.copy()
                    sprite.blit(glow_surface, (0, 0), special_flags=pygame.BLEND_ADD)
                elif visual_state == "animating":
                    # Animation effect - slight pulsing
                    pulse = int(self.scene.anim_time * 3) % 2
                    if pulse == 0:
                        pulse_surface = pygame.Surface(sprite.get_size(), pygame.SRCALPHA)
                        pulse_surface.fill((255, 255, 255, 50))
                        sprite = sprite.copy()
                        sprite.blit(pulse_surface, (0, 0), special_flags=pygame.BLEND_ADD)
                elif visual_state == "error":
                    # Error effect - red flash
                    error_surface = pygame.Surface(sprite.get_size(), pygame.SRCALPHA)
                    error_surface.fill((255, 0, 0, 150))
                    sprite = sprite.copy()
                    sprite.blit(error_surface, (0, 0), special_flags=pygame.BLEND_ADD)
                    # Reset error state after brief display
                    if hasattr(self.scene, 'anim_time') and int(self.scene.anim_time * 2) % 2 == 0:
                        element.visual_state = "normal"

                surface.blit(sprite, (screen_x, screen_y))

            # Draw subtle highlight for target positions (pressure plates)
            if element.element_type == PuzzleElementType.PRESSURE_PLATE:
                if element.state == "default":
                    # Draw subtle target indicator
                    highlight_rect = pygame.Rect(
                        screen_x, screen_y, self.scene.draw_tile, self.scene.draw_tile
                    )
                    highlight_surface = pygame.Surface(
                        (self.scene.draw_tile, self.scene.draw_tile), pygame.SRCALPHA
                    )
                    pygame.draw.rect(
                        highlight_surface, (255, 255, 0, 30), highlight_surface.get_rect()
                    )
                    surface.blit(highlight_surface, highlight_rect)

    def _draw_prop(self, surface: pygame.Surface, prop: "Prop") -> None:
        """Draw a decorative prop on the map."""
        screen_x, screen_y = self.scene.renderer.project(prop.x, prop.y)

        # Get the prop sprite
        sprite = self.scene.assets.get_image(prop.sprite_id, (self.scene.tile_size, self.scene.tile_size))

        # Draw shadow under solid props for depth
        if prop.solid:
            shadow_rect = pygame.Rect(
                screen_x + self.scene.draw_tile // 4,
                screen_y + self.scene.draw_tile - 3 * self.scene.scale,
                self.scene.draw_tile // 2,
                3 * self.scene.scale
            )
            shadow_surface = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow_surface, (0, 0, 0, 40), shadow_surface.get_rect())
            surface.blit(shadow_surface, shadow_rect)

        # Draw the prop sprite
        surface.blit(sprite, (screen_x, screen_y))

    def _draw_overworld_enemy(self, surface: pygame.Surface, enemy: "OverworldEnemy") -> None:
        """Draw an overworld enemy with a direction indicator."""
        screen_x, screen_y = self.scene.renderer.project(enemy.x, enemy.y)

        # Draw the enemy sprite
        sprite = self.scene.assets.get_image(enemy.sprite_id, (self.scene.tile_size, self.scene.tile_size))
        surface.blit(sprite, (screen_x, screen_y))

        # Draw a direction indicator (red triangle showing danger direction)
        draw_direction_indicator(
            surface=surface,
            screen_x=screen_x,
            screen_y=screen_y,
            tile_size=self.scene.draw_tile,
            facing=enemy.facing,
            indicator_size=6 * self.scene.scale,
            fill_color=(255, 80, 80),
            border_color=(180, 40, 40),
            indicator_gap=0,
        )

        # Draw detection range visualization (optional - shows line of sight)
        dx, dy = enemy.get_facing_offset()
        for dist in range(1, enemy.detection_range + 1):
            check_x = enemy.x + dx * dist
            check_y = enemy.y + dy * dist
            tile_screen_x, tile_screen_y = self.scene.renderer.project(check_x, check_y)
            # Draw a subtle red tint on tiles in detection range
            detection_rect = pygame.Rect(tile_screen_x, tile_screen_y, self.scene.draw_tile, self.scene.draw_tile)
            detection_surface = pygame.Surface((self.scene.draw_tile, self.scene.draw_tile), pygame.SRCALPHA)
            detection_surface.fill((255, 0, 0, 30))  # Semi-transparent red
            surface.blit(detection_surface, detection_rect)

    def _draw_party_ui(self, surface: pygame.Surface) -> None:
        """Draw party member HP/SP bars in the HUD."""
        if not self.scene.player.party:
            return

        font_small = self.scene.assets.get_font("small") or self.scene.assets.get_font("default")
        screen_width = surface.get_width()

        # Use layout constants for consistent spacing
        bar_width = 150
        bar_height = Layout.BAR_HEIGHT_SMALL
        padding = Layout.PADDING_XS
        panel_padding = Layout.PADDING_SM

        # Calculate panel dimensions based on party size
        member_height = Layout.HUD_NAME_HEIGHT + bar_height * 2 + padding * 2
        num_members = sum(1 for m in self.scene.player.party if m.stats)
        if num_members == 0:
            return

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

        # Draw each party member's stats
        content_x = panel_x + panel_padding
        content_y = panel_y + panel_padding

        for i, member in enumerate(self.scene.player.party):
            if not member.stats:
                continue

            y_offset = i * member_height

            # Draw member name with shadow
            if font_small:
                name_color = Colors.TEXT_PRIMARY if member.is_alive() else Colors.TEXT_DISABLED
                draw_text_shadow(
                    surface, font_small, member.name,
                    (content_x, content_y + y_offset),
                    name_color
                )

            # Draw HP bar
            hp_y = content_y + y_offset + Layout.HUD_NAME_HEIGHT
            draw_hp_bar(
                surface, content_x, hp_y, bar_width, bar_height,
                member.stats.hp, member.stats.max_hp, "", font=font_small
            )

            # Draw SP bar
            sp_y = hp_y + bar_height + padding
            draw_sp_bar(
                surface, content_x, sp_y, bar_width, bar_height,
                member.stats.sp, member.stats.max_sp, "", font=font_small
            )

        # Update stacking position for next element (only if drawn)
        self._right_hud_y += panel_height + Layout.ELEMENT_GAP

    def _draw_quest_tracker(
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
                    draw_text_shadow(
                        surface, font, "Active Quests",
                        (panel_x + panel_padding, header_y),
                        Colors.TEXT_HIGHLIGHT
                    )

                y = panel_y + 25

                for quest in active_quests[:max_quests]:
                    # Skip drawing if we're past the visible area
                    if y > screen_height - padding:
                        break

                    # Quest name
                    if y >= 0:
                        quest_color = Colors.TEXT_SUCCESS if quest.is_complete() else Colors.TEXT_PRIMARY
                        draw_text_shadow(
                            surface, font, f"* {quest.name[:25]}",
                            (panel_x + panel_padding, y),
                            quest_color
                        )
                    y += line_height

                    # Objectives
                    for obj in quest.objectives[:max_objectives]:
                        if y > screen_height - padding:
                            break
                        if y >= 0:
                            if obj.completed:
                                obj_color = Colors.TEXT_SUCCESS
                                status = "v"
                            else:
                                obj_color = Colors.TEXT_SECONDARY
                                status = obj.get_progress_text()

                            draw_text_shadow(
                                surface, font, f"  {status} {obj.description[:22]}",
                                (panel_x + panel_padding, y),
                                obj_color
                            )
                        y += line_height

                    # Show if more objectives exist
                    if len(quest.objectives) > max_objectives:
                        if y <= screen_height - padding and y >= 0:
                            more_text = f"  ... +{len(quest.objectives) - max_objectives} more"
                            draw_text_shadow(
                                surface, font, more_text,
                                (panel_x + panel_padding, y),
                                Colors.TEXT_DISABLED
                            )
                        y += line_height

                    y += Layout.PADDING_XS  # Spacing between quests

                # Show if more quests exist
                if len(active_quests) > max_quests:
                    if y <= screen_height - padding and y >= 0:
                        more_quests = f"+{len(active_quests) - max_quests} more quests (J: Journal)"
                        draw_text_shadow(
                            surface, font, more_quests,
                            (panel_x + panel_padding, y),
                            Colors.TEXT_DISABLED
                        )
            finally:
                # Restore original clipping region
                surface.set_clip(old_clip)

    def _draw_day_night_overlay(self, surface: pygame.Surface) -> None:
        """Draw the day/night cycle color overlay."""
        day_night = self.scene.get_manager_attr(
            "day_night_cycle", "_draw_day_night_overlay"
        )
        if not day_night or day_night.paused:
            return

        # Get the current tint color with alpha
        tint = day_night.get_tint_color()
        r, g, b, a = tint

        # Skip if no tint needed
        if a <= 0:
            return

        # Create overlay surface
        screen_width, screen_height = surface.get_size()
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((r, g, b, a))

        # Apply overlay with blend mode
        surface.blit(overlay, (0, 0))

    def _draw_time_display(self, surface: pygame.Surface) -> None:
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

        # Get time info
        time_str = day_night.get_12hour_time()
        time_of_day = day_night.get_time_of_day()
        day_count = day_night.day_count

        # Choose color based on time of day
        if day_night.is_daytime():
            time_color = (255, 255, 200)  # Warm yellow for day
        else:
            time_color = (180, 200, 255)  # Cool blue for night

        # Render text to measure dimensions
        time_text = font.render(time_str, True, time_color)
        day_text = font.render(f"Day {day_count}", True, Colors.TEXT_SECONDARY)
        period_text = font.render(time_of_day.value.title(), True, Colors.TEXT_DISABLED)

        # Calculate panel dimensions
        text_widths = [time_text.get_width(), day_text.get_width(), period_text.get_width()]
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
        draw_text_shadow(
            surface, font, time_str,
            (text_x - time_text.get_width(), line_y),
            time_color
        )
        line_y += Layout.LINE_HEIGHT_COMPACT
        draw_text_shadow(
            surface, font, time_of_day.value.title(),
            (text_x - period_text.get_width(), line_y),
            Colors.TEXT_DISABLED
        )
        line_y += Layout.LINE_HEIGHT_COMPACT
        draw_text_shadow(
            surface, font, f"Day {day_count}",
            (text_x - day_text.get_width(), line_y),
            Colors.TEXT_SECONDARY
        )

        # Update stacking position for next element (only if drawn)
        self._right_hud_y += panel_height + Layout.ELEMENT_GAP

    def _draw_weather_overlay(self, surface: pygame.Surface) -> None:
        """Draw the weather color overlay."""
        weather = self.scene.get_manager_attr(
            "weather_system", "_draw_weather_overlay"
        )
        if not weather or not weather.enabled:
            return

        # Get the current tint color with alpha
        tint = weather.get_tint_color()
        r, g, b, a = tint

        # Skip if no tint needed
        if a <= 0:
            return

        # Create overlay surface
        screen_width, screen_height = surface.get_size()
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((r, g, b, a))

        # Apply overlay
        surface.blit(overlay, (0, 0))

        # Draw lightning flash for thunderstorms
        if weather.lightning_flash > 0:
            flash_alpha = int(weather.lightning_flash * 200)
            flash_overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
            flash_overlay.fill((255, 255, 255, flash_alpha))
            surface.blit(flash_overlay, (0, 0))

    def _draw_weather_particles(self, surface: pygame.Surface) -> None:
        """Draw weather particles (rain, snow, etc.)."""
        weather = self.scene.get_manager_attr(
            "weather_system", "_draw_weather_particles"
        )
        if not weather or not weather.enabled:
            return

        if not weather.particles:
            return

        active_weather = weather._get_effective_weather()

        for particle in weather.particles:
            # Calculate alpha based on lifetime
            life_ratio = particle.lifetime / particle.max_lifetime
            alpha = int(particle.alpha * (1.0 - life_ratio * 0.5))

            if active_weather in (WeatherType.RAIN, WeatherType.HEAVY_RAIN, WeatherType.THUNDERSTORM):
                # Draw rain as elongated lines
                end_x = particle.x + particle.vx * 0.02
                end_y = particle.y + particle.vy * 0.02
                color = (150, 180, 220, alpha)
                # Draw line for rain
                pygame.draw.line(
                    surface,
                    color[:3],
                    (int(particle.x), int(particle.y)),
                    (int(end_x), int(end_y)),
                    max(1, particle.size // 2)
                )
            elif active_weather in (WeatherType.SNOW, WeatherType.BLIZZARD):
                # Draw snow as circles
                color = (255, 255, 255, alpha)
                snow_surface = pygame.Surface((particle.size * 2, particle.size * 2), pygame.SRCALPHA)
                pygame.draw.circle(snow_surface, color, (particle.size, particle.size), particle.size)
                surface.blit(snow_surface, (int(particle.x) - particle.size, int(particle.y) - particle.size))
            elif active_weather == WeatherType.SANDSTORM:
                # Draw sand as small tan particles
                color = (210, 180, 130, alpha)
                sand_surface = pygame.Surface((particle.size * 2, particle.size * 2), pygame.SRCALPHA)
                pygame.draw.circle(sand_surface, color, (particle.size, particle.size), particle.size)
                surface.blit(sand_surface, (int(particle.x) - particle.size, int(particle.y) - particle.size))
            elif active_weather == WeatherType.ASH:
                # Draw ash as dark gray particles
                color = (80, 80, 80, alpha)
                ash_surface = pygame.Surface((particle.size * 2, particle.size * 2), pygame.SRCALPHA)
                pygame.draw.circle(ash_surface, color, (particle.size, particle.size), particle.size)
                surface.blit(ash_surface, (int(particle.x) - particle.size, int(particle.y) - particle.size))

    def _draw_weather_indicator(self, surface: pygame.Surface) -> None:
        """Draw weather indicator in the HUD."""
        weather = self.scene.get_manager_attr(
            "weather_system", "_draw_weather_indicator"
        )
        if not weather or not weather.enabled:
            return

        # Check if weather indicator is enabled
        show_indicator = self.scene.config.get("weather_show_indicator", True)
        if not show_indicator:
            return

        font = self.scene.assets.get_font("small") or self.scene.assets.get_font("default")
        if not font:
            return

        screen_width, _ = surface.get_size()

        # Get weather info
        weather_name = weather.get_weather_name()
        active_weather = weather._get_effective_weather()

        # Choose icon/color based on weather
        weather_colors = {
            WeatherType.CLEAR: (255, 255, 150),      # Sunny yellow
            WeatherType.CLOUDY: (180, 180, 190),     # Gray
            WeatherType.RAIN: (100, 150, 200),       # Blue
            WeatherType.HEAVY_RAIN: (80, 120, 180),  # Darker blue
            WeatherType.THUNDERSTORM: (150, 100, 180),  # Purple
            WeatherType.SNOW: (220, 240, 255),       # Light blue-white
            WeatherType.BLIZZARD: (200, 220, 255),   # Blue-white
            WeatherType.FOG: (180, 180, 180),        # Gray
            WeatherType.SANDSTORM: (210, 180, 130),  # Tan
            WeatherType.ASH: (120, 110, 110),        # Dark gray
        }
        weather_color = weather_colors.get(active_weather, Colors.TEXT_SECONDARY)

        # Render weather text to measure
        weather_text = font.render(weather_name, True, weather_color)

        # Calculate panel dimensions
        panel_width = weather_text.get_width() + Layout.PADDING_MD * 2
        panel_height = 28

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
                radius=Layout.CORNER_RADIUS_SMALL
            )

        # Draw weather text with shadow
        text_x = panel_x + Layout.PADDING_MD
        text_y = panel_y + (panel_height - weather_text.get_height()) // 2
        draw_text_shadow(surface, font, weather_name, (text_x, text_y), weather_color)

        # Update stacking position for next element (only if drawn)
        self._right_hud_y += panel_height + Layout.ELEMENT_GAP

    def _draw_post_game_indicator(self, surface: pygame.Surface) -> None:
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

"""Class selection scene for choosing player class and subclass."""

import json
import math
import os
import sys
import pygame
from typing import Any, Callable, Dict, List, Optional, Tuple, TYPE_CHECKING

from .base_menu_scene import BaseMenuScene
from .assets import AssetManager
from .theme import Colors
from .onboarding_theme import generate_stars, generate_particles, update_particles
from .config_loader import load_config
from core.constants import DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT
from core.logging_utils import log_warning

if TYPE_CHECKING:
    from .scene import SceneManager

# Import sprite generation for dynamic class sprite creation
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))
try:
    from generate_sprites import generate_class_sprite, SUBCLASS_COLORS
    HAS_SPRITE_GENERATOR = True
except ImportError:
    HAS_SPRITE_GENERATOR = False
    SUBCLASS_COLORS = {}


def load_classes_data(path: str = os.path.join("data", "classes.json")) -> Dict[str, Any]:
    """Load class definitions from JSON."""
    if not os.path.exists(path):
        return {"classes": {}, "subclass_bonuses": {}}
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception as e:
        log_warning(f"Failed to load classes data from {path}: {e}")
        return {"classes": {}, "subclass_bonuses": {}}


def draw_onboarding_background(surface: pygame.Surface, cache: dict, anim_timer: float,
                                stars: List[dict], particles: List[dict]) -> None:
    """Draw the shared onboarding background with gradient, stars, particles, vignette."""
    width, height = surface.get_size()

    # Gradient background (cached)
    if cache.get("gradient") is None or cache["gradient"].get_size() != (width, height):
        grad = pygame.Surface((width, height))
        top, bottom = Colors.BG_ONBOARDING_TOP, Colors.BG_ONBOARDING_BOTTOM
        for y in range(height):
            ratio = y / height
            ratio = ratio * ratio * (3 - 2 * ratio)
            r = int(top[0] + (bottom[0] - top[0]) * ratio)
            g = int(top[1] + (bottom[1] - top[1]) * ratio)
            b = int(top[2] + (bottom[2] - top[2]) * ratio)
            pygame.draw.line(grad, (r, g, b), (0, y), (width, y))
        cache["gradient"] = grad
    surface.blit(cache["gradient"], (0, 0))

    # Stars
    for star in stars:
        twinkle = math.sin(anim_timer * star["twinkle_speed"] + star["twinkle_offset"])
        brightness = max(40, min(255, int(star["base_brightness"] + 60 * twinkle)))
        if star["layer"] == 0:
            color = (brightness, brightness, int(brightness * 1.1))
        elif star["layer"] == 1:
            color = (brightness, int(brightness * 0.95), brightness)
        else:
            color = (int(brightness * 1.1), int(brightness * 1.05), brightness)
        x, y = int(star["x"]), int(star["y"])
        size = star["size"]
        if size > 1.5:
            pygame.draw.circle(surface, (color[0]//4, color[1]//4, color[2]//4), (x, y), int(size + 2))
        pygame.draw.circle(surface, color, (x, y), max(1, int(size)))

    # Particles
    for p in particles:
        x, y = int(p["x"]), int(p["y"])
        if 0 <= x < width and 0 <= y < height:
            size = int(p["size"])
            alpha = int(p["alpha"] * (0.5 + 0.5 * math.sin(anim_timer * 2 + x * 0.1)))
            color = (*p["color"], max(20, min(255, alpha)))
            ps = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(ps, color, (size, size), size)
            surface.blit(ps, (x - size, y - size))

    # Vignette (cached)
    if cache.get("vignette") is None or cache["vignette"].get_size() != (width, height):
        vig = pygame.Surface((width, height), pygame.SRCALPHA)
        cx, cy = width // 2, height // 2
        max_dist = math.sqrt(cx ** 2 + cy ** 2)
        for vy in range(0, height, 4):
            for vx in range(0, width, 4):
                dist = math.sqrt((vx - cx) ** 2 + (vy - cy) ** 2)
                alpha = int(min(80, (dist / max_dist) ** 2 * 120))
                pygame.draw.rect(vig, (0, 0, 0, alpha), (vx, vy, 4, 4))
        cache["vignette"] = vig
    surface.blit(cache["vignette"], (0, 0))


def draw_title_text(surface: pygame.Surface, text: str, font: pygame.font.Font,
                    center_x: int, y: int) -> None:
    """Draw title text with glow and shadow effects."""
    shadow = font.render(text, True, Colors.TITLE_SHADOW)
    surface.blit(shadow, shadow.get_rect(center=(center_x + 2, y + 2)))
    glow = font.render(text, True, Colors.TITLE_GLOW)
    for off in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        surface.blit(glow, glow.get_rect(center=(center_x + off[0], y + off[1])))
    main = font.render(text, True, Colors.TITLE_MAIN)
    surface.blit(main, main.get_rect(center=(center_x, y)))


class SelectionSceneBase(BaseMenuScene):
    """Shared helpers for onboarding selection scenes."""

    LIST_ITEM_HEIGHT = 30
    MAX_VISIBLE_ITEMS = 10
    LIST_WIDTH = 155

    def __init__(
        self,
        manager: Optional["SceneManager"],
        player_name: str,
        scale: int,
        assets: Optional[AssetManager],
        star_seed: int,
        particle_seed: int,
    ):
        super().__init__(manager, assets, scale)
        self.player_name = player_name

        # Load config for screen dimensions
        self.config = load_config()
        self.screen_width = self.config.get("window_width", DEFAULT_WINDOW_WIDTH)
        self.screen_height = self.config.get("window_height", DEFAULT_WINDOW_HEIGHT)

        # Animation state
        self.anim_timer = 0.0
        self.fade_in = 0.0
        self.stars = generate_stars(50, self.screen_width, self.screen_height, seed=star_seed)
        self.particles = generate_particles(15, self.screen_width, self.screen_height, seed=particle_seed)
        self._bg_cache: Dict[str, pygame.Surface] = {}

    def update(self, dt: float) -> None:
        """Update shared animation state."""
        self.anim_timer += dt
        if self.fade_in < 1.0:
            self.fade_in = min(1.0, self.fade_in + dt * 2.0)
        update_particles(self.particles, dt, self.screen_width, self.screen_height)

    def _draw_selection_list(
        self,
        surface: pygame.Surface,
        width: int,
        height: int,
        item_ids: List[str],
        selected_index: int,
        name_lookup: Callable[[str], str],
    ) -> None:
        """Draw the scrollable selection list shared by class/subclass scenes."""
        x = int(width * 0.04)
        y = int(height * 0.22)

        item_height = self.LIST_ITEM_HEIGHT
        max_visible = self.MAX_VISIBLE_ITEMS
        list_width = self.LIST_WIDTH
        list_height = max_visible * item_height + 16

        font = self.assets.get_font("default", 20) or pygame.font.Font(None, 20)

        scroll_offset = selected_index - max_visible + 1 if selected_index >= max_visible else 0

        list_rect = pygame.Rect(x, y, list_width, list_height)
        bg_surface = pygame.Surface((list_width, list_height), pygame.SRCALPHA)
        pygame.draw.rect(
            bg_surface,
            (*Colors.LIST_BG, int(220 * self.fade_in)),
            (0, 0, list_width, list_height),
            border_radius=8,
        )
        pygame.draw.rect(
            bg_surface,
            (*Colors.PANEL_BORDER_ONBOARDING, int(180 * self.fade_in)),
            (0, 0, list_width, list_height),
            width=2,
            border_radius=8,
        )
        surface.blit(bg_surface, list_rect.topleft)

        font_arrow = self.assets.get_font("small", 14) or pygame.font.Font(None, 14)
        if scroll_offset > 0:
            arrow = font_arrow.render("▲ more", True, Colors.TEXT_HINT)
            surface.blit(arrow, (x + 45, y - 16))
        if scroll_offset + max_visible < len(item_ids):
            arrow = font_arrow.render("▼ more", True, Colors.TEXT_HINT)
            surface.blit(arrow, (x + 45, y + list_height + 2))

        for i in range(max_visible):
            actual_index = i + scroll_offset
            if actual_index >= len(item_ids):
                break

            item_id = item_ids[actual_index]
            item_name = name_lookup(item_id)

            is_selected = actual_index == selected_index
            item_y = y + 8 + i * item_height

            if is_selected:
                highlight_rect = pygame.Rect(x + 4, item_y - 2, list_width - 8, item_height - 2)
                highlight_surf = pygame.Surface((highlight_rect.width, highlight_rect.height), pygame.SRCALPHA)
                pygame.draw.rect(
                    highlight_surf,
                    (*Colors.LIST_SELECTED, int(200 * self.fade_in)),
                    (0, 0, highlight_rect.width, highlight_rect.height),
                    border_radius=4,
                )
                surface.blit(highlight_surf, highlight_rect.topleft)

                cursor_offset = 2 * math.sin(self.anim_timer * 5)
                cursor_x = x + 10 + cursor_offset
                arrow_points = [
                    (cursor_x, item_y + 3),
                    (cursor_x + 5, item_y + 8),
                    (cursor_x, item_y + 13),
                ]
                pygame.draw.polygon(surface, Colors.ACCENT, arrow_points)

            color = Colors.WHITE if is_selected else Colors.TEXT_SECONDARY
            name_text = font.render(item_name, True, color)
            surface.blit(name_text, (x + 22, item_y + 1))

    def _get_panel_rect(self, surface: pygame.Surface) -> pygame.Rect:
        """Return a responsive rect for the details panel."""
        width, height = surface.get_size()
        panel_x = int(width * 0.30)
        panel_y = int(height * 0.22)
        panel_width = int(width * 0.47)
        panel_height = int(height * 0.69)
        return pygame.Rect(panel_x, panel_y, panel_width, panel_height)

    def _draw_panel_background(self, surface: pygame.Surface) -> pygame.Rect:
        """Draw the shared details panel background and return its rect."""
        panel_rect = self._get_panel_rect(surface)
        bg_surface = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(
            bg_surface,
            (*Colors.PANEL_BG_ONBOARDING, int(230 * self.fade_in)),
            (0, 0, panel_rect.width, panel_rect.height),
            border_radius=10,
        )
        pygame.draw.rect(
            bg_surface,
            (*Colors.PANEL_BORDER_ONBOARDING, int(180 * self.fade_in)),
            (0, 0, panel_rect.width, panel_rect.height),
            width=2,
            border_radius=10,
        )
        surface.blit(bg_surface, panel_rect.topleft)
        return panel_rect

    def _draw_wrapped_text(
        self,
        surface: pygame.Surface,
        text: str,
        font: pygame.font.Font,
        pos: Tuple[int, int],
        max_width: int,
        color: Tuple[int, int, int],
    ) -> int:
        """Draw text wrapped to fit within max_width. Returns final y position."""
        words = text.split()
        lines: List[str] = []
        current_line: List[str] = []

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

        x, y = pos
        line_height = font.get_linesize()

        for line in lines:
            text_surface = font.render(line, True, color)
            surface.blit(text_surface, (x, y))
            y += line_height

        return y

    def _draw_preview_frame(self, surface: pygame.Surface) -> Tuple[int, int, int, int]:
        """Draw the shared sprite preview frame and return positioning info."""
        width, height = surface.get_size()
        sprite_x = int(width * 0.79)
        sprite_y = int(height * 0.27)
        frame_size = int(width * 0.19)

        frame_rect = pygame.Rect(sprite_x - 12, sprite_y - 12, frame_size, frame_size)
        frame_surf = pygame.Surface((frame_size, frame_size), pygame.SRCALPHA)
        pygame.draw.rect(
            frame_surf,
            (*Colors.PANEL_BG_ONBOARDING, int(230 * self.fade_in)),
            (0, 0, frame_size, frame_size),
            border_radius=8,
        )
        pygame.draw.rect(
            frame_surf,
            (*Colors.PANEL_BORDER_ONBOARDING, int(180 * self.fade_in)),
            (0, 0, frame_size, frame_size),
            width=2,
            border_radius=8,
        )
        surface.blit(frame_surf, frame_rect.topleft)

        font_label = self.assets.get_font("small", 14) or pygame.font.Font(None, 14)
        label = font_label.render("Preview", True, Colors.TEXT_HINT)
        sprite_center_x = sprite_x + frame_size // 2
        label_rect = label.get_rect(center=(sprite_center_x, sprite_y - 22))
        surface.blit(label, label_rect)

        sprite_size = int(width * 0.15)
        return sprite_x, sprite_y, sprite_size, sprite_center_x

    def _get_class_name(self, class_id: str) -> str:
        """Return the display name for a class id using loaded class data."""
        classes = getattr(self, "classes_data", {}).get("classes", {})
        class_data = classes.get(class_id, {}) if isinstance(classes, dict) else {}
        return class_data.get("name", class_id.title())


class ClassSelectionScene(SelectionSceneBase):
    """Scene for selecting player's primary class."""

    def __init__(
        self,
        manager: Optional["SceneManager"],
        player_name: str,
        scale: int = 2,
        assets: Optional[AssetManager] = None,
    ):
        super().__init__(
            manager=manager,
            player_name=player_name,
            scale=scale,
            assets=assets,
            star_seed=42,
            particle_seed=789,
        )

        # Load class data
        self.classes_data = load_classes_data()
        self.class_ids = list(self.classes_data.get("classes", {}).keys())

        # Selection state
        self.selected_index = 0
        self.selection_confirmed = False
        self.selected_class: Optional[str] = None

        # Class sprite cache
        self.class_sprites: Dict[str, pygame.Surface] = {}
        self._load_class_sprites()

    def _load_class_sprites(self) -> None:
        """Load or generate class sprites for preview."""
        for class_id in self.class_ids:
            # Try to load pre-generated sprite first
            sprite_name = f"class_{class_id}"
            try:
                sprite = self.assets.get_image(sprite_name)
                if sprite:
                    scaled = pygame.transform.scale(sprite, (96, 96))
                    self.class_sprites[class_id] = scaled
                    continue
            except Exception:
                pass

            # Fall back to dynamic generation
            if HAS_SPRITE_GENERATOR:
                try:
                    sprite = generate_class_sprite(class_id)
                    if sprite:
                        scaled = pygame.transform.scale(sprite, (96, 96))
                        self.class_sprites[class_id] = scaled
                except Exception as e:
                    log_warning(f"Failed to generate sprite for class {class_id}: {e}")

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle input events."""
        if self.selection_confirmed:
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_index = (self.selected_index - 1) % len(self.class_ids)
            elif event.key == pygame.K_DOWN:
                self.selected_index = (self.selected_index + 1) % len(self.class_ids)
            elif event.key == pygame.K_RETURN:
                self.selected_class = self.class_ids[self.selected_index]
                self.selection_confirmed = True

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the class selection scene."""
        width, height = surface.get_size()
        center_x = width // 2

        # Draw polished background
        draw_onboarding_background(surface, self._bg_cache, self.anim_timer, self.stars, self.particles)

        # Draw title with effects - proportional to height
        font_large = self.assets.get_font("large", 40) or pygame.font.Font(None, 40)
        title_y = int(height * 0.09)
        draw_title_text(surface, "Choose Your Class", font_large, center_x, title_y)

        # Draw subtitle with player name - proportional to height
        font_small = self.assets.get_font("default", 20) or pygame.font.Font(None, 20)
        subtitle = font_small.render(f"Welcome, {self.player_name}!", True, Colors.SUBTITLE)
        subtitle_y = int(height * 0.16)
        subtitle_rect = subtitle.get_rect(center=(center_x, subtitle_y))
        surface.blit(subtitle, subtitle_rect)

        # Draw class list on the left
        self._draw_class_list(surface, width, height)

        # Draw selected class details on the right
        self._draw_class_details(surface)

        # Draw class sprite preview
        self._draw_class_sprite(surface)

        # Draw controls hint
        font_hint = self.assets.get_font("small", 16) or pygame.font.Font(None, 16)
        hint_text = font_hint.render("↑↓ Select  •  Enter Confirm", True, Colors.TEXT_HINT)
        hint_rect = hint_text.get_rect(center=(center_x, height - 20))
        surface.blit(hint_text, hint_rect)

    def _draw_class_list(self, surface: pygame.Surface, width: int, height: int) -> None:
        """Draw the class list with the shared list renderer."""
        self._draw_selection_list(
            surface,
            width,
            height,
            self.class_ids,
            self.selected_index,
            self._get_class_name,
        )

    def _draw_class_details(self, surface: pygame.Surface) -> None:
        """Draw details panel for the selected class."""
        if not self.class_ids:
            return

        class_id = self.class_ids[self.selected_index]
        class_data = self.classes_data["classes"].get(class_id, {})

        panel_rect = self._draw_panel_background(surface)
        panel_x, panel_y = panel_rect.x, panel_rect.y

        # Draw class name with accent color
        font_medium = self.assets.get_font("default", 26) or pygame.font.Font(None, 26)
        class_name = self._get_class_name(class_id)
        name_text = font_medium.render(class_name, True, Colors.ACCENT)
        surface.blit(name_text, (panel_x + 15, panel_y + 12))

        # Draw description
        font_small = self.assets.get_font("small", 16) or pygame.font.Font(None, 16)
        description = class_data.get("description", "No description available.")
        self._draw_wrapped_text(surface, description, font_small, (panel_x + 15, panel_y + 42),
                               panel_rect.width - 30, Colors.TEXT_SECONDARY)

        # Draw stats section
        stats = class_data.get("stats", {})
        stats_y = panel_y + 105

        stat_names = [
            ("HP", "max_hp"), ("SP", "max_sp"), ("ATK", "attack"),
            ("DEF", "defense"), ("MAG", "magic"), ("SPD", "speed"), ("LCK", "luck")
        ]

        stats_label = font_small.render("Base Stats:", True, Colors.ACCENT_DIM)
        surface.blit(stats_label, (panel_x + 15, stats_y))
        stats_y += 20

        # Draw stats in two columns
        col1_x = panel_x + 15
        col2_x = panel_x + 160

        for i, (label, key) in enumerate(stat_names):
            value = stats.get(key, 0)
            x = col1_x if i < 4 else col2_x
            y = stats_y + (i % 4) * 20

            stat_color = self._get_stat_color(key, value)
            stat_text = font_small.render(f"{label}: {value}", True, stat_color)
            surface.blit(stat_text, (x, y))

        # Draw starting skills
        skills = class_data.get("base_skills", [])
        skills_y = stats_y + 95

        skills_label = font_small.render("Starting Skills:", True, Colors.ACCENT_DIM)
        surface.blit(skills_label, (panel_x + 15, skills_y))

        skills_text = ", ".join(s.replace("_", " ").title() for s in skills[:3]) if skills else "None"
        if len(skills) > 3:
            skills_text += f" (+{len(skills) - 3} more)"
        skills_value = font_small.render(skills_text, True, Colors.SKILL_TEXT)
        surface.blit(skills_value, (panel_x + 15, skills_y + 18))

    def _get_stat_color(self, stat_key: str, value: int) -> tuple:
        """Get color for stat based on its value (relative to average)."""
        # Average baseline values
        baselines = {
            "max_hp": 90, "max_sp": 50, "attack": 10, "defense": 6,
            "magic": 8, "speed": 10, "luck": 6
        }
        baseline = baselines.get(stat_key, 10)

        if value >= baseline * 1.3:
            return Colors.STAT_HIGH  # Green for high
        elif value <= baseline * 0.7:
            return Colors.STAT_LOW  # Red for low
        return Colors.STAT_NORMAL  # White for average

    def _draw_class_sprite(self, surface: pygame.Surface) -> None:
        """Draw the sprite preview for the currently selected class."""
        if not self.class_ids:
            return

        class_id = self.class_ids[self.selected_index]
        sprite = self.class_sprites.get(class_id)

        sprite_x, sprite_y, sprite_size, _ = self._draw_preview_frame(surface)

        if sprite:
            # Scale sprite to match proportional size
            scaled_sprite = pygame.transform.scale(sprite, (sprite_size, sprite_size))
            surface.blit(scaled_sprite, (sprite_x, sprite_y))
        else:
            # Draw placeholder with proportional size
            pygame.draw.rect(surface, Colors.PLACEHOLDER_BG, (sprite_x, sprite_y, sprite_size, sprite_size), border_radius=4)
            font = self.assets.get_font("small", 14) or pygame.font.Font(None, 14)
            text = font.render("No sprite", True, Colors.TEXT_HINT)
            text_rect = text.get_rect(center=(sprite_x + sprite_size // 2, sprite_y + sprite_size // 2))
            surface.blit(text, text_rect)


class SubclassSelectionScene(SelectionSceneBase):
    """Scene for selecting player's subclass (secondary class)."""

    def __init__(
        self,
        manager: Optional["SceneManager"],
        player_name: str,
        primary_class: str,
        scale: int = 2,
        assets: Optional[AssetManager] = None,
    ):
        super().__init__(
            manager=manager,
            player_name=player_name,
            scale=scale,
            assets=assets,
            star_seed=99,
            particle_seed=888,
        )
        self.primary_class = primary_class

        # Load class data
        self.classes_data = load_classes_data()

        # Get available subclasses (all classes except primary)
        all_classes = list(self.classes_data.get("classes", {}).keys())
        self.subclass_ids = [c for c in all_classes if c != primary_class]

        # Selection state
        self.selected_index = 0
        self.selection_confirmed = False
        self.selected_subclass: Optional[str] = None

        # Sprite cache for class+subclass combinations
        self.combo_sprites: Dict[str, pygame.Surface] = {}

    def _get_combo_sprite(self, subclass_id: str) -> Optional[pygame.Surface]:
        """Get or generate sprite for primary class with subclass coloring."""
        cache_key = f"{self.primary_class}_{subclass_id}"

        if cache_key in self.combo_sprites:
            return self.combo_sprites[cache_key]

        # Try to load pre-generated sprite
        sprite_name = f"player_{self.primary_class}_{subclass_id}"
        try:
            sprite = self.assets.get_image(sprite_name)
            if sprite:
                scaled = pygame.transform.scale(sprite, (96, 96))
                self.combo_sprites[cache_key] = scaled
                return scaled
        except Exception:
            pass

        # Fall back to dynamic generation
        if HAS_SPRITE_GENERATOR:
            try:
                sprite = generate_class_sprite(self.primary_class, subclass_id)
                if sprite:
                    scaled = pygame.transform.scale(sprite, (96, 96))
                    self.combo_sprites[cache_key] = scaled
                    return scaled
            except Exception as e:
                log_warning(f"Failed to generate combo sprite for {cache_key}: {e}")

        return None

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle input events."""
        if self.selection_confirmed:
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_index = (self.selected_index - 1) % len(self.subclass_ids)
            elif event.key == pygame.K_DOWN:
                self.selected_index = (self.selected_index + 1) % len(self.subclass_ids)
            elif event.key == pygame.K_RETURN:
                self.selected_subclass = self.subclass_ids[self.selected_index]
                self.selection_confirmed = True

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the subclass selection scene."""
        width, height = surface.get_size()
        center_x = width // 2

        # Draw polished background
        draw_onboarding_background(surface, self._bg_cache, self.anim_timer, self.stars, self.particles)

        # Draw title with effects - proportional to height
        font_large = self.assets.get_font("large", 40) or pygame.font.Font(None, 40)
        title_y = int(height * 0.09)
        draw_title_text(surface, "Choose Your Subclass", font_large, center_x, title_y)

        # Draw subtitle showing primary class - proportional to height
        font_small = self.assets.get_font("default", 20) or pygame.font.Font(None, 20)
        primary_name = self._get_class_name(self.primary_class)
        subtitle = font_small.render(f"Primary Class: {primary_name}", True, Colors.SKILL_TEXT)
        subtitle_y = int(height * 0.16)
        subtitle_rect = subtitle.get_rect(center=(center_x, subtitle_y))
        surface.blit(subtitle, subtitle_rect)

        # Draw subclass list on the left
        self._draw_subclass_list(surface, width, height)

        # Draw selected subclass bonus details on the right
        self._draw_subclass_details(surface)

        # Draw class sprite with subclass coloring
        self._draw_combo_sprite(surface)

        # Draw controls hint
        font_hint = self.assets.get_font("small", 16) or pygame.font.Font(None, 16)
        hint_text = font_hint.render("↑↓ Select  •  Enter Confirm", True, Colors.TEXT_HINT)
        hint_rect = hint_text.get_rect(center=(center_x, height - 20))
        surface.blit(hint_text, hint_rect)

    def _draw_subclass_list(self, surface: pygame.Surface, width: int, height: int) -> None:
        """Draw the subclass list with the shared list renderer."""
        self._draw_selection_list(
            surface,
            width,
            height,
            self.subclass_ids,
            self.selected_index,
            self._get_class_name,
        )

    def _draw_subclass_details(self, surface: pygame.Surface) -> None:
        """Draw details panel for the selected subclass."""
        if not self.subclass_ids:
            return

        subclass_id = self.subclass_ids[self.selected_index]
        class_data = self.classes_data["classes"].get(subclass_id, {})
        bonus_data = self.classes_data.get("subclass_bonuses", {}).get(subclass_id, {})
        subclass_name = self._get_class_name(subclass_id)

        panel_rect = self._draw_panel_background(surface)
        panel_x, panel_y = panel_rect.x, panel_rect.y

        # Draw subclass name with accent color
        font_medium = self.assets.get_font("default", 26) or pygame.font.Font(None, 26)
        name_text = font_medium.render(subclass_name, True, Colors.ACCENT)
        surface.blit(name_text, (panel_x + 15, panel_y + 12))

        # Draw description
        font_small = self.assets.get_font("small", 16) or pygame.font.Font(None, 16)
        description = class_data.get("description", "No description available.")
        y = self._draw_wrapped_text(surface, description, font_small, (panel_x + 15, panel_y + 42),
                                   panel_rect.width - 30, Colors.TEXT_SECONDARY)

        # Draw subclass bonuses
        y = max(y + 12, panel_y + 120)

        bonus_label = font_small.render("Subclass Bonuses:", True, Colors.ACCENT_DIM)
        surface.blit(bonus_label, (panel_x + 15, y))
        y += 20

        # Stat bonuses
        stat_bonuses = bonus_data.get("stats", {})
        if stat_bonuses:
            bonus_parts = []
            stat_labels = {
                "max_hp": "HP", "max_sp": "SP", "attack": "ATK",
                "defense": "DEF", "magic": "MAG", "speed": "SPD", "luck": "LCK"
            }
            for stat, value in stat_bonuses.items():
                label = stat_labels.get(stat, stat.upper())
                bonus_parts.append(f"+{value} {label}")

            bonus_text = font_small.render(", ".join(bonus_parts), True, Colors.STAT_HIGH)
            surface.blit(bonus_text, (panel_x + 15, y))
            y += 22

        # Skill bonuses
        skill_bonuses = bonus_data.get("skills", [])
        if skill_bonuses:
            skills_label = font_small.render("Bonus Skills:", True, Colors.ACCENT_DIM)
            surface.blit(skills_label, (panel_x + 15, y))
            y += 18

            skills_text = ", ".join(s.replace("_", " ").title() for s in skill_bonuses[:3])
            if len(skill_bonuses) > 3:
                skills_text += f" (+{len(skill_bonuses) - 3})"
            skills_value = font_small.render(skills_text, True, Colors.SKILL_TEXT)
            surface.blit(skills_value, (panel_x + 15, y))

    def _draw_combo_sprite(self, surface: pygame.Surface) -> None:
        """Draw the sprite preview for primary class with current subclass coloring."""
        if not self.subclass_ids:
            return

        subclass_id = self.subclass_ids[self.selected_index]
        sprite = self._get_combo_sprite(subclass_id)

        sprite_x, sprite_y, sprite_size, sprite_center_x = self._draw_preview_frame(surface)

        if sprite:
            # Scale sprite to match proportional size
            scaled_sprite = pygame.transform.scale(sprite, (sprite_size, sprite_size))
            surface.blit(scaled_sprite, (sprite_x, sprite_y))
        else:
            # Draw placeholder with proportional size
            pygame.draw.rect(surface, Colors.PLACEHOLDER_BG, (sprite_x, sprite_y, sprite_size, sprite_size), border_radius=4)
            font = self.assets.get_font("small", 14) or pygame.font.Font(None, 14)
            text = font.render("No sprite", True, Colors.TEXT_HINT)
            text_rect = text.get_rect(center=(sprite_x + sprite_size // 2, sprite_y + sprite_size // 2))
            surface.blit(text, text_rect)

        # Draw color scheme label below sprite - proportional offset
        font_small = self.assets.get_font("small", 14) or pygame.font.Font(None, 14)
        subclass_name = self._get_class_name(subclass_id)
        color_label = font_small.render(f"{subclass_name} Colors", True, Colors.TEXT_HINT)
        label_y = sprite_y + sprite_size + 12  # 12px below the sprite
        label_rect = color_label.get_rect(center=(sprite_center_x, label_y))
        surface.blit(color_label, label_rect)

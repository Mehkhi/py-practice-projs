"""
Base Sprite Class for Sprite Generation

Provides the foundational class for all sprite generators with
64x64 creation, scaling, and frame management capabilities.
"""

import os
import pygame
import json
from typing import Dict, List, Tuple, Optional
from abc import ABC, abstractmethod

from .utils import create_surface, scale_to_game_size


class BaseSprite(ABC):
    """
    Base class for all sprite generators.
    Handles 64x64 creation, scaling, and frame management.
    """

    def __init__(self, name: str, category: str):
        """
        Initialize the sprite generator.

        Args:
            name: Sprite name (used for file naming)
            category: Category ('enemy', 'npc', 'party', 'boss')
        """
        self.name = name
        self.category = category
        self.base_size = (64, 64)
        self.game_size = (32, 32)
        self.frames: Dict[str, List[pygame.Surface]] = {
            'idle': [],      # 4 frames
            'attack': [],    # 4 frames
            'hurt': [],      # 2 frames
            'death': [],     # 4 frames
        }
        self._base_surface: Optional[pygame.Surface] = None

    def generate_all_frames(self) -> None:
        """Generate all animation frames."""
        self.frames['idle'] = self._generate_idle_frames()
        self.frames['attack'] = self._generate_attack_frames()
        self.frames['hurt'] = self._generate_hurt_frames()
        self.frames['death'] = self._generate_death_frames()

    def generate_static(self) -> pygame.Surface:
        """
        Generate a single static sprite.

        Returns:
            The first idle frame
        """
        if not self.frames['idle']:
            self.frames['idle'] = self._generate_idle_frames()

        if self.frames['idle']:
            return self.frames['idle'][0]

        # Fallback: generate base sprite
        return self._generate_base_sprite()

    @abstractmethod
    def _generate_base_sprite(self) -> pygame.Surface:
        """
        Generate the base sprite design.
        Override in subclass to define the sprite's appearance.

        Returns:
            64x64 pygame Surface with the sprite
        """
        pass

    def _generate_idle_frames(self) -> List[pygame.Surface]:
        """
        Generate idle animation frames.
        Override in subclass for custom idle animation.
        Default: subtle breathing/movement.

        Returns:
            List of 4 pygame Surfaces
        """
        base = self._generate_base_sprite()
        frames = []

        for i in range(4):
            frame = create_surface(self.base_size)

            # Apply subtle vertical offset for breathing effect
            offset = [0, -1, 0, 1][i]
            frame.blit(base, (0, offset))

            frames.append(frame)

        return frames

    def _generate_attack_frames(self) -> List[pygame.Surface]:
        """
        Generate attack animation frames.
        Override in subclass for custom attack animation.

        Returns:
            List of 4 pygame Surfaces
        """
        base = self._generate_base_sprite()
        frames = []

        for i in range(4):
            frame = create_surface(self.base_size)

            # Attack motion: wind-up, strike, impact, recovery
            offsets = [(0, 0), (4, -2), (8, 0), (4, 0)]
            frame.blit(base, offsets[i])

            frames.append(frame)

        return frames

    def _generate_hurt_frames(self) -> List[pygame.Surface]:
        """
        Generate hurt reaction frames.
        Override in subclass for custom hurt animation.

        Returns:
            List of 2 pygame Surfaces
        """
        base = self._generate_base_sprite()
        frames = []

        for i in range(2):
            frame = create_surface(self.base_size)

            # Recoil effect
            offset = [(-4, 0), (-2, 0)][i]
            frame.blit(base, offset)

            # Add flash effect on first frame
            if i == 0:
                self._apply_flash_effect(frame)

            frames.append(frame)

        return frames

    def _generate_death_frames(self) -> List[pygame.Surface]:
        """
        Generate death animation frames.
        Override in subclass for custom death animation.

        Returns:
            List of 4 pygame Surfaces
        """
        base = self._generate_base_sprite()
        frames = []

        for i in range(4):
            frame = create_surface(self.base_size)

            # Death fall: initial hit, falling, hitting ground, rest
            offsets = [(0, 0), (0, 4), (0, 8), (0, 12)]
            alpha_values = [255, 200, 150, 100]

            # Copy and fade
            temp = base.copy()
            temp.set_alpha(alpha_values[i])
            frame.blit(temp, offsets[i])

            frames.append(frame)

        return frames

    def _apply_flash_effect(self, surface: pygame.Surface) -> None:
        """Apply a white flash effect to the surface."""
        w, h = surface.get_size()
        for y in range(h):
            for x in range(w):
                pixel = surface.get_at((x, y))
                if pixel.a > 0:
                    # Lighten the pixel
                    r = min(255, pixel.r + 100)
                    g = min(255, pixel.g + 100)
                    b = min(255, pixel.b + 100)
                    surface.set_at((x, y), (r, g, b, pixel.a))

    def save_sprites(self, output_dir: str, scale: bool = True) -> Dict[str, str]:
        """
        Save all frames to output directory.

        File naming convention:
        - Static: {name}.png (first idle frame, scaled to 32x32)
        - Animated: {name}_anim/{name}_{state}_{frame}.png
        - Sheet: {name}_sheet.png

        Args:
            output_dir: Base output directory
            scale: Whether to scale to game size (32x32)

        Returns:
            Dict mapping file types to paths
        """
        saved_files = {}

        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Generate frames if not already done
        if not any(self.frames.values()):
            self.generate_all_frames()

        # Save static sprite (first idle frame)
        static_path = os.path.join(output_dir, f"{self.name}.png")
        if self.frames['idle']:
            static = self.frames['idle'][0]
            if scale:
                static = scale_to_game_size(static, self.game_size)
            pygame.image.save(static, static_path)
            saved_files['static'] = static_path

        # Save animation frames
        anim_dir = os.path.join(output_dir, f"{self.name}_anim")
        os.makedirs(anim_dir, exist_ok=True)

        for state, frames in self.frames.items():
            for i, frame in enumerate(frames):
                frame_name = f"{self.name}_{state}_{i}.png"
                frame_path = os.path.join(anim_dir, frame_name)

                if scale:
                    frame = scale_to_game_size(frame, self.game_size)

                pygame.image.save(frame, frame_path)

        saved_files['anim_dir'] = anim_dir

        # Save sprite sheet
        sheet_path = os.path.join(output_dir, f"{self.name}_sheet.png")
        sheet = self._create_sprite_sheet(scale)
        if sheet:
            pygame.image.save(sheet, sheet_path)
            saved_files['sheet'] = sheet_path

        # Save metadata
        meta_path = os.path.join(output_dir, f"{self.name}_meta.json")
        meta = self._create_metadata()
        with open(meta_path, 'w') as f:
            json.dump(meta, f, indent=2)
        saved_files['meta'] = meta_path

        return saved_files

    def _create_sprite_sheet(self, scale: bool = True) -> Optional[pygame.Surface]:
        """
        Create a sprite sheet with all animation frames.

        Layout:
        - Rows: Animation states (idle, attack, hurt, death)
        - Columns: Frames (0, 1, 2, 3)

        Args:
            scale: Whether to scale to game size

        Returns:
            Sprite sheet surface or None if no frames
        """
        if not any(self.frames.values()):
            return None

        # Determine sheet dimensions
        frame_size = self.game_size if scale else self.base_size
        max_frames = max(len(frames) for frames in self.frames.values())
        num_states = len(self.frames)

        sheet_w = frame_size[0] * max_frames
        sheet_h = frame_size[1] * num_states

        sheet = create_surface((sheet_w, sheet_h))

        # State order
        state_order = ['idle', 'attack', 'hurt', 'death']

        for row, state in enumerate(state_order):
            frames = self.frames.get(state, [])
            for col, frame in enumerate(frames):
                if scale:
                    frame = scale_to_game_size(frame, self.game_size)

                x = col * frame_size[0]
                y = row * frame_size[1]
                sheet.blit(frame, (x, y))

        return sheet

    def _create_metadata(self) -> Dict:
        """
        Create metadata for the sprite.

        Returns:
            Dict containing sprite metadata
        """
        return {
            'name': self.name,
            'category': self.category,
            'base_size': list(self.base_size),
            'game_size': list(self.game_size),
            'animations': {
                state: len(frames) for state, frames in self.frames.items()
            },
            'frame_rate': 8,  # FPS for animations
        }

    def _scale_and_save(self, surface: pygame.Surface, filepath: str) -> None:
        """
        Scale 64x64 to 32x32 and save.

        Args:
            surface: 64x64 surface to scale
            filepath: Output file path
        """
        scaled = scale_to_game_size(surface, self.game_size)
        pygame.image.save(scaled, filepath)


class SimpleSprite(BaseSprite):
    """
    Simple sprite that doesn't require animation.
    Useful for static items, props, etc.
    """

    def __init__(self, name: str, category: str, draw_func: callable):
        """
        Initialize simple sprite with custom draw function.

        Args:
            name: Sprite name
            category: Category
            draw_func: Function that takes a surface and draws the sprite
        """
        super().__init__(name, category)
        self._draw_func = draw_func

    def _generate_base_sprite(self) -> pygame.Surface:
        surface = create_surface(self.base_size)
        self._draw_func(surface)
        return surface

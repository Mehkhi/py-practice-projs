"""Sound management for loading and playing audio."""

import os
from typing import Dict

import pygame

from core.logging_utils import log_warning


class SoundManager:
    """Manages loading and playback of sound effects."""

    def __init__(self, assets_dir: str = "assets"):
        self.assets_dir = assets_dir
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self._load_sounds()

    def _load_sounds(self) -> None:
        """Load sound effects/music."""
        audio_dir = os.path.join(self.assets_dir, "audio")
        if not os.path.exists(audio_dir):
            return
        for filename in os.listdir(audio_dir):
            if filename.lower().endswith((".wav", ".ogg", ".mp3")):
                sound_id = os.path.splitext(filename)[0]
                try:
                    sound = pygame.mixer.Sound(os.path.join(audio_dir, filename))
                    self.sounds[sound_id] = sound
                except Exception as e:
                    log_warning(f"Failed to load sound {filename} from {audio_dir}: {e}")

    def play_sound(self, sound_id: str) -> None:
        """Play a sound by ID."""
        if sound_id in self.sounds:
            try:
                self.sounds[sound_id].play()
            except Exception as e:
                log_warning(f"Failed to play sound {sound_id}: {e}")

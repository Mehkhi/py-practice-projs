"""Battle scene modular components.

This package contains extracted components from battle_scene.py for
better maintainability and separation of concerns.

Modules:
    constants: Biome backdrop mappings, gradient colors, animation timing constants
    state: BattleStateManager for centralized state management
    party_ai: AI logic for party member actions
    renderer: Battle scene rendering (flash effects, damage numbers, debug overlay)
    animations: Visual effects and animation system
    outcomes: Victory/defeat/escape handling
    menu: Menu input handling and state machine
    hud: HUD rendering (HP/SP bars, status icons, hotbar)
"""

from .constants import (
    BIOME_TO_BACKDROP,
    BIOME_GRADIENTS,
    FLASH_INITIAL_INTENSITY,
    FLASH_DECAY_RATE,
    AI_NOTIFICATION_DURATION,
)
from .state import BattleStateManager
from .party_ai import PartyAIMixin
from .renderer import BattleRendererMixin
from .animations import BattleAnimationsMixin
from .outcomes import BattleOutcomesMixin
from .rewards import BattleRewardsHandler
from .menu import BattleMenuMixin
from .hud import BattleHudMixin
from .targeting import BattleTargetingMixin
from .layout import BattleUILayoutMixin
from .initializer import BattleInitializer

__all__ = [
    # Constants
    "BIOME_TO_BACKDROP",
    "BIOME_GRADIENTS",
    "FLASH_INITIAL_INTENSITY",
    "FLASH_DECAY_RATE",
    "AI_NOTIFICATION_DURATION",
    # State management
    "BattleStateManager",
    # Mixins
    "PartyAIMixin",
    "BattleRendererMixin",
    "BattleAnimationsMixin",
    "BattleOutcomesMixin",
    "BattleRewardsHandler",
    "BattleMenuMixin",
    "BattleTargetingMixin",
    "BattleHudMixin",
    "BattleUILayoutMixin",
    "BattleInitializer",
]

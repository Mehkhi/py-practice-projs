"""UI components package.

This package contains modular UI components split by concern:
- toast: ToastNotification for temporary notifications
- nine_slice: NineSlicePanel for UI framing
- message_box: MessageBox for text display with pagination
- dialog: ConfirmationDialog for modal dialogs
- combat_log: CombatLog for battle action history
- bars: HP/SP bars and status icon drawing functions
- menus: Menu, Tooltip
- minimap: Minimap HUD component
- transitions: TransitionManager for screen transitions
- tutorial: HelpOverlay, TipPopup, HintButton
- comparison: EquipmentComparisonPanel for stat comparisons
- utils: Shared utility functions like draw_rounded_panel
"""

from .toast import ToastNotification
from .nine_slice import NineSlicePanel
from .message_box import MessageBox
from .dialog import ConfirmationDialog
from .combat_log import CombatLog
from .bars import (
    draw_hp_bar,
    draw_sp_bar,
    draw_status_icons,
    draw_help_text,
    draw_contextual_help,
    draw_section_header,
)
from .menus import Menu, Tooltip
from .minimap import Minimap
from .transitions import TransitionManager
from .help_overlay import HelpOverlay
from .tip_popup import TipPopup
from .hint_button import HintButton
from .comparison import EquipmentComparisonPanel, get_equipped_item_for_slot

__all__ = [
    # Panels
    "NineSlicePanel",
    "MessageBox",
    "ConfirmationDialog",
    "ToastNotification",
    "CombatLog",
    # Bars and drawing functions
    "draw_hp_bar",
    "draw_sp_bar",
    "draw_status_icons",
    "draw_help_text",
    "draw_contextual_help",
    "draw_section_header",
    # Menus
    "Menu",
    "Tooltip",
    # Minimap
    "Minimap",
    # Transitions
    "TransitionManager",
    # Tutorial UI
    "HelpOverlay",
    "TipPopup",
    "HintButton",
    # Comparison
    "EquipmentComparisonPanel",
    "get_equipped_item_for_slot",
]

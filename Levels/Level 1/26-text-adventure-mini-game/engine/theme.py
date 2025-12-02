"""
Unified theme system for the RPG.
Centralizes colors, fonts, and visual constants.
"""

from dataclasses import dataclass, field
from typing import Dict, Tuple, Optional, List
import pygame
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .accessibility import AccessibilityManager

# Load config for screen dimensions
try:
    from .config_loader import load_config
    from core.constants import DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT
    _config = load_config()
    _DEFAULT_SCREEN_WIDTH = _config.get("window_width", DEFAULT_WINDOW_WIDTH)
    _DEFAULT_SCREEN_HEIGHT = _config.get("window_height", DEFAULT_WINDOW_HEIGHT)
except Exception:
    from core.constants import DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT
    _DEFAULT_SCREEN_WIDTH = DEFAULT_WINDOW_WIDTH
    _DEFAULT_SCREEN_HEIGHT = DEFAULT_WINDOW_HEIGHT

# ==============================================
# COLOR PALETTE
# ==============================================

class Colors:
    # Base Colors
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    TRANSPARENT = (0, 0, 0, 0)

    # Theme: "Mystic Night"
    # Deep, rich backgrounds with warm gold accents

    # Backgrounds
    BG_DARK = (8, 10, 18)      # Deepest background
    BG_MAIN = (15, 20, 35)     # Main background color
    BG_PANEL = (25, 30, 45)    # UI Panel background
    BG_OVERLAY = (10, 12, 20, 200) # Semi-transparent overlay
    BG_TOOLTIP = (20, 25, 40, 230) # Tooltip background

    # UI Elements
    BORDER = (60, 70, 90)      # Subtle border
    BORDER_FOCUS = (100, 110, 140) # Active border
    BORDER_HIGHLIGHT = (200, 180, 100) # Highlight border

    ACCENT = (255, 200, 80)    # Gold accent
    ACCENT_DIM = (180, 140, 50) # Dim gold
    ACCENT_BRIGHT = (255, 240, 150) # Bright gold

    # Text
    TEXT_PRIMARY = (240, 240, 235)
    TEXT_SECONDARY = (160, 170, 190)
    TEXT_DISABLED = (80, 90, 110)
    TEXT_HIGHLIGHT = (255, 220, 100)
    TEXT_ERROR = (255, 80, 80)
    TEXT_SUCCESS = (100, 255, 120)
    TEXT_INFO = (100, 200, 255)

    # Status Bars
    HP_HIGH = (100, 255, 100)
    HP_MID = (255, 200, 50)
    HP_LOW = (255, 60, 60)
    SP_FILL = (60, 140, 255)
    XP_FILL = (200, 100, 255)
    BAR_BG = (40, 45, 60)

    # Rarity Colors
    COMMON = (200, 200, 200)
    UNCOMMON = (100, 255, 100)
    RARE = (100, 200, 255)
    EPIC = (200, 100, 255)
    LEGENDARY = (255, 200, 50)

    # Element Colors
    FIRE = (255, 80, 60)
    ICE = (100, 200, 255)
    LIGHTNING = (255, 240, 80)
    EARTH = (160, 120, 80)
    WIND = (150, 255, 200)
    WATER = (60, 100, 220)
    HOLY = (255, 255, 200)
    DARK = (140, 80, 180)
    POISON = (180, 60, 220)

    # Skill Tree Status Colors
    SKILL_UNLOCKED = (100, 255, 100)    # Green - skill is available
    SKILL_LOCKED = (255, 80, 80)        # Red - skill is locked
    SKILL_AVAILABLE = (255, 200, 80)    # Gold - can be unlocked

    # Onboarding/Startup Scene Colors
    # Used by: title_scene, name_entry_scene, class_selection_scene
    BG_ONBOARDING_TOP = (8, 12, 28)     # Top of gradient background
    BG_ONBOARDING_BOTTOM = (25, 35, 65) # Bottom of gradient background
    TITLE_MAIN = (255, 248, 220)        # Main title text color
    TITLE_GLOW = (180, 140, 80)         # Title glow effect color
    TITLE_SHADOW = (20, 15, 40)         # Title shadow color
    SUBTITLE = (160, 170, 200)         # Subtitle text color
    TEXT_HINT = (90, 100, 130)          # Hint/secondary text color

    # Onboarding UI Elements
    PANEL_BG_ONBOARDING = (20, 25, 45)  # Panel background for onboarding scenes
    PANEL_BORDER_ONBOARDING = (80, 90, 120) # Panel border for onboarding scenes
    LIST_BG = (15, 20, 38)              # List background color
    LIST_SELECTED = (60, 70, 110)       # Selected list item background

    # Input Field Colors
    INPUT_BG = (20, 25, 45)             # Input field background
    INPUT_BORDER = (80, 90, 120)        # Input field border
    INPUT_FOCUS = (255, 200, 100)       # Input field focus border

    # Stat Display Colors (for onboarding stat previews)
    STAT_HIGH = (100, 255, 100)         # High stat value (green)
    STAT_LOW = (255, 100, 100)          # Low stat value (red)
    STAT_NORMAL = (200, 200, 200)       # Normal stat value (gray)

    # Divider/Decoration
    DIVIDER = (100, 110, 140)           # Decorative divider line

    # Skill/Ability Text
    SKILL_TEXT = (150, 200, 255)        # Blue text for skill labels and values

    # Placeholder Elements
    PLACEHOLDER_BG = (60, 60, 80)       # Background for placeholder/empty elements

    @staticmethod
    def get_accessibility_color(color_key: str) -> Tuple[int, int, int]:
        """
        Get a color from the accessibility manager's colorblind palette.
        Falls back to default colors if accessibility manager is unavailable.

        Args:
            color_key: Key from accessibility color palette (e.g., "hp_high", "sp_bar", "positive", "negative")

        Returns:
            RGB tuple adjusted for current colorblind mode, or default color if unavailable
        """
        try:
            from .accessibility import get_accessibility_manager
            access_mgr = get_accessibility_manager()
            return access_mgr.get_color(color_key)
        except (ImportError, AttributeError):
            # Fallback to default colors if accessibility unavailable
            defaults = {
                "hp_high": Colors.HP_HIGH,
                "hp_medium": Colors.HP_MID,
                "hp_low": Colors.HP_LOW,
                "sp_bar": Colors.SP_FILL,
                "positive": Colors.TEXT_SUCCESS,
                "negative": Colors.TEXT_ERROR,
                "accent": Colors.ACCENT,
                "highlight": Colors.BORDER_HIGHLIGHT,
                "player_marker": (255, 255, 100),
                "enemy_marker": (255, 100, 100),
                "npc_marker": (200, 100, 255),
                "warp_marker": (100, 200, 255),
            }
            return defaults.get(color_key, Colors.WHITE)

    @staticmethod
    def get_hp_color(hp_ratio: float) -> Tuple[int, int, int]:
        """
        Get HP bar color based on HP ratio, adjusted for colorblind mode.

        Args:
            hp_ratio: Current HP / Max HP (0.0 to 1.0)

        Returns:
            RGB tuple for HP bar color
        """
        if hp_ratio > 0.6:
            return Colors.get_accessibility_color("hp_high")
        elif hp_ratio > 0.3:
            return Colors.get_accessibility_color("hp_medium")
        else:
            return Colors.get_accessibility_color("hp_low")

    @staticmethod
    def get_sp_color() -> Tuple[int, int, int]:
        """
        Get SP bar color adjusted for colorblind mode.

        Returns:
            RGB tuple for SP bar color
        """
        return Colors.get_accessibility_color("sp_bar")

class Gradients:
    """Helper for gradient definitions."""

    @staticmethod
    def vertical(surface: pygame.Surface, top_color: Tuple[int, int, int], bottom_color: Tuple[int, int, int]) -> None:
        """Fill a surface with a vertical gradient."""
        height = surface.get_height()
        width = surface.get_width()

        # Pre-calculate color steps to avoid float math in loop
        r1, g1, b1 = top_color
        r2, g2, b2 = bottom_color

        r_diff = r2 - r1
        g_diff = g2 - g1
        b_diff = b2 - b1

        for y in range(height):
            ratio = y / height
            r = int(r1 + r_diff * ratio)
            g = int(g1 + g_diff * ratio)
            b = int(b1 + b_diff * ratio)
            pygame.draw.line(surface, (r, g, b), (0, y), (width, y))

# ==============================================
# FONTS
# ==============================================

class Fonts:
    # Font sizes
    SIZE_TITLE = 48
    SIZE_HEADING = 32
    SIZE_SUBHEADING = 24
    SIZE_BODY = 20
    SIZE_SMALL = 16
    SIZE_TINY = 12

    # Font mapping keys (used in AssetManager)
    DEFAULT = "default"
    LARGE = "large"
    SMALL = "small"
    MONO = "mono" # For stats/numbers if needed


# ==============================================
# UI CONSTANTS
# ==============================================

class Layout:
    """
    Comprehensive layout system for consistent UI spacing.

    Naming conventions:
    - MARGIN: Space from screen edges or between major sections
    - PADDING: Space inside containers/panels
    - GAP: Space between related elements
    - SPACING: General-purpose spacing
    """

    # ==============================================
    # SCREEN MARGINS (breathing room from edges)
    # ==============================================
    SCREEN_MARGIN = 20          # Standard screen edge margin
    SCREEN_MARGIN_SMALL = 12    # Compact screen edge margin
    SCREEN_MARGIN_LARGE = 32    # Generous screen edge margin

    # ==============================================
    # CONTENT PADDING (inside panels/containers)
    # ==============================================
    PADDING_XS = 4              # Extra small - tight spaces
    PADDING_SM = 8              # Small - compact elements
    PADDING_MD = 12             # Medium - standard content
    PADDING_LG = 16             # Large - comfortable reading
    PADDING_XL = 24             # Extra large - major sections

    # Legacy aliases (for backwards compatibility)
    PADDING_SMALL = 4
    PADDING_MEDIUM = 8
    PADDING_LARGE = 16

    # ==============================================
    # SECTION SPACING (between major UI sections)
    # ==============================================
    SECTION_GAP = 20            # Between major UI sections
    SECTION_GAP_SMALL = 12      # Tighter section separation
    SECTION_GAP_LARGE = 32      # Generous section separation

    # ==============================================
    # ELEMENT SPACING (between related items)
    # ==============================================
    ELEMENT_GAP = 8             # Standard gap between elements
    ELEMENT_GAP_SMALL = 4       # Tight gap between elements
    ELEMENT_GAP_LARGE = 12      # Comfortable gap between elements

    # ==============================================
    # TEXT & LINE SPACING
    # ==============================================
    LINE_HEIGHT = 24            # Standard text line height
    LINE_HEIGHT_COMPACT = 20    # Compact text line height
    LINE_HEIGHT_RELAXED = 28    # Relaxed text line height
    TEXT_SHADOW_OFFSET = 1      # Shadow offset for text

    # ==============================================
    # MENU SYSTEM
    # ==============================================
    MENU_ITEM_HEIGHT = 36       # Height of menu items (increased from 32)
    MENU_ITEM_HEIGHT_COMPACT = 28  # Compact menu item height
    MENU_ITEM_PADDING_H = 16    # Horizontal padding inside menu items
    MENU_ITEM_PADDING_V = 6     # Vertical padding inside menu items
    MENU_CURSOR_WIDTH = 24      # Width reserved for cursor
    MENU_HIGHLIGHT_PADDING = 8  # Padding around highlight background
    MENU_GROUP_GAP = 16         # Gap between menu groups/sections

    # ==============================================
    # PANELS & CONTAINERS
    # ==============================================
    BORDER_WIDTH = 2            # Standard border width
    BORDER_WIDTH_THIN = 1       # Thin border width
    CORNER_RADIUS = 8           # Standard corner radius (increased from 6)
    CORNER_RADIUS_SMALL = 4     # Small corner radius
    CORNER_RADIUS_LARGE = 12    # Large corner radius

    PANEL_PADDING = 16          # Standard panel inner padding
    PANEL_HEADER_HEIGHT = 40    # Height for panel headers
    PANEL_MIN_WIDTH = 200       # Minimum panel width
    PANEL_MIN_HEIGHT = 100      # Minimum panel height

    # ==============================================
    # BARS (HP, SP, XP, etc.)
    # ==============================================
    BAR_HEIGHT = 18             # Standard bar height
    BAR_HEIGHT_SMALL = 14       # Small bar height
    BAR_HEIGHT_LARGE = 22       # Large bar height
    BAR_BORDER_RADIUS = 4       # Bar corner radius
    BAR_INNER_PADDING = 2       # Padding between bar border and fill
    BAR_GAP = 8                 # Gap between stacked bars
    BAR_LABEL_GAP = 4           # Gap between bar and its label
    BAR_LABEL_OFFSET_Y = -18    # Vertical offset for bar label

    # ==============================================
    # HUD ELEMENTS
    # ==============================================
    HUD_ROW_HEIGHT = 52         # Height per HUD row (player/party stats)
    HUD_NAME_HEIGHT = 16        # Height for name labels
    HUD_MARGIN = 16             # HUD margin from screen edges
    HUD_ELEMENT_GAP = 8         # Gap between HUD elements

    # ==============================================
    # MESSAGE BOX
    # ==============================================
    MESSAGE_BOX_PADDING = 16    # Inner padding for message boxes
    MESSAGE_BOX_LINE_GAP = 4    # Gap between message lines
    MESSAGE_BOX_MIN_HEIGHT = 80 # Minimum message box height
    MESSAGE_BOX_PORTRAIT_SIZE = 64  # Portrait image size
    MESSAGE_BOX_PORTRAIT_GAP = 16   # Gap after portrait

    # ==============================================
    # ICONS
    # ==============================================
    ICON_SIZE_XS = 12           # Extra small icons
    ICON_SIZE_SMALL = 16        # Small icons
    ICON_SIZE_MEDIUM = 24       # Medium icons
    ICON_SIZE_LARGE = 32        # Large icons
    ICON_SIZE_XL = 48           # Extra large icons
    ICON_GAP = 4                # Gap between icons

    # ==============================================
    # TOOLTIPS
    # ==============================================
    TOOLTIP_PADDING = 10        # Tooltip inner padding
    TOOLTIP_MAX_WIDTH = 280     # Maximum tooltip width
    TOOLTIP_OFFSET = 16         # Offset from cursor

    # ==============================================
    # OVERLAY SETTINGS
    # ==============================================
    OVERLAY_ALPHA = 200         # Standard overlay alpha for menus/panels

    # ==============================================
    # DIALOGS & MODALS
    # ==============================================
    DIALOG_PADDING = 24         # Dialog inner padding
    DIALOG_BUTTON_HEIGHT = 36   # Dialog button height
    DIALOG_BUTTON_GAP = 16      # Gap between dialog buttons
    DIALOG_BUTTON_MIN_WIDTH = 100  # Minimum button width

    # ==============================================
    # SCREEN DIMENSIONS (reference)
    # ==============================================
    SCREEN_WIDTH = _DEFAULT_SCREEN_WIDTH          # Default screen width from config
    SCREEN_HEIGHT = _DEFAULT_SCREEN_HEIGHT        # Default screen height from config

    # ==============================================
    # HELPER METHODS
    # ==============================================

    @staticmethod
    def center_x(element_width: int, container_width: Optional[int] = None) -> int:
        """Calculate x position to center an element horizontally."""
        if container_width is None:
            container_width = Layout.SCREEN_WIDTH
        return (container_width - element_width) // 2

    @staticmethod
    def center_y(element_height: int, container_height: Optional[int] = None) -> int:
        """Calculate y position to center an element vertically."""
        if container_height is None:
            container_height = Layout.SCREEN_HEIGHT
        return (container_height - element_height) // 2

    @staticmethod
    def bottom_aligned(element_height: int, margin: int = 20, container_height: Optional[int] = None) -> int:
        """Calculate y position to align element to bottom with margin."""
        if container_height is None:
            container_height = Layout.SCREEN_HEIGHT
        return container_height - element_height - margin

    @staticmethod
    def right_aligned(element_width: int, margin: int = 20, container_width: Optional[int] = None) -> int:
        """Calculate x position to align element to right with margin."""
        if container_width is None:
            container_width = Layout.SCREEN_WIDTH
        return container_width - element_width - margin


@dataclass
class UITheme:
    """Container for theme settings to pass to UI components."""
    primary_color: Tuple[int, int, int] = Colors.TEXT_PRIMARY
    secondary_color: Tuple[int, int, int] = Colors.TEXT_SECONDARY
    bg_color: Tuple[int, int, int] = Colors.BG_PANEL
    border_color: Tuple[int, int, int] = Colors.BORDER
    accent_color: Tuple[int, int, int] = Colors.ACCENT

    # Menu specific
    menu_active_color: Tuple[int, int, int] = Colors.TEXT_HIGHLIGHT
    menu_inactive_color: Tuple[int, int, int] = Colors.TEXT_SECONDARY
    menu_disabled_color: Tuple[int, int, int] = Colors.TEXT_DISABLED
    menu_highlight_bg: Tuple[int, int, int] = (50, 60, 80)

    font_size: int = Fonts.SIZE_BODY


# ==============================================
# SCENE LAYOUT PRESETS
# ==============================================

class SceneLayout:
    """
    Standard layout presets for menu scenes.

    These presets provide consistent positioning for common scene layouts,
    reducing duplication across similar scenes like inventory and equipment.
    """

    # Two-column layout with menu on left and details panel on right
    # Used by: inventory_scene, equipment_scene
    SIDE_PANEL = {
        "menu_x": Layout.SCREEN_MARGIN + 40,
        "menu_y": 120,
        "menu_bg_x": Layout.SCREEN_MARGIN + 20,
        "menu_bg_y": 100,
        "menu_bg_width": 280,
        "menu_bg_height": 280,
        "details_x": 340,
        "details_y": 100,
        "details_width": 280,
        "details_height": 280,
        "message_box_x": Layout.SCREEN_MARGIN,
        "message_box_y": 400,
        "message_box_width": 600,
        "message_box_height": 70,
        "title_y": 50,
    }

    # Centered menu layout for pause/title screens
    CENTERED = {
        "menu_width": 180,
        "menu_padding": 20,
        "title_y": 80,
        "menu_y": 130,
    }

    @staticmethod
    def get_menu_position(preset: dict) -> tuple:
        """Get menu position tuple from a preset."""
        return (preset.get("menu_x", 60), preset.get("menu_y", 120))

    @staticmethod
    def get_menu_bg_rect(preset: dict) -> tuple:
        """Get menu background rect tuple from a preset."""
        return (
            preset.get("menu_bg_x", Layout.SCREEN_MARGIN + 20),
            preset.get("menu_bg_y", 100),
            preset.get("menu_bg_width", 280),
            preset.get("menu_bg_height", 280),
        )

    @staticmethod
    def get_details_rect(preset: dict) -> tuple:
        """Get details/stats panel rect tuple from a preset."""
        return (
            preset.get("details_x", 340),
            preset.get("details_y", 100),
            preset.get("details_width", 280),
            preset.get("details_height", 280),
        )

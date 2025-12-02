"""Equipment comparison UI component for showing stat differences."""

from typing import Dict, List, Optional, Tuple

import pygame

from ..theme import Colors, Fonts, Layout
from core.items import Item


class EquipmentComparisonPanel:
    """
    Side-by-side equipment comparison showing stat differences.

    Displays current vs. new equipment with color-coded stat changes:
    - Green with up arrow for improvements
    - Red with down arrow for downgrades
    - Gray for unchanged stats
    """

    # Stats to compare (display name, stat key)
    STAT_LABELS = [
        ("ATK", "attack"),
        ("DEF", "defense"),
        ("MAG", "magic"),
        ("SPD", "speed"),
        ("LCK", "luck"),
    ]

    def __init__(
        self,
        width: int = 260,
        padding: int = 12,
    ):
        self.width = width
        self.padding = padding
        self.current_item: Optional[Item] = None
        self.new_item: Optional[Item] = None

    def set_items(self, current_item: Optional[Item], new_item: Optional[Item]) -> None:
        """Set the items to compare."""
        self.current_item = current_item
        self.new_item = new_item

    def _get_stat_modifier(self, item: Optional[Item], stat_key: str) -> int:
        """Get stat modifier value from an item."""
        if item is None:
            return 0
        return item.stat_modifiers.get(stat_key, 0)

    def _get_stat_diff_color(self, diff: int) -> Tuple[int, int, int]:
        """Get color based on stat difference."""
        if diff > 0:
            return Colors.TEXT_SUCCESS
        elif diff < 0:
            return Colors.TEXT_ERROR
        else:
            return Colors.TEXT_SECONDARY

    def _get_diff_indicator(self, diff: int) -> str:
        """Get arrow indicator for stat difference."""
        if diff > 0:
            return "+"
        elif diff < 0:
            return ""  # Negative sign is already included
        else:
            return "="

    def draw(
        self,
        surface: pygame.Surface,
        x: int,
        y: int,
        font: Optional[pygame.font.Font] = None,
    ) -> int:
        """
        Draw the comparison panel.

        Args:
            surface: Pygame surface to draw on
            x: X position
            y: Y position
            font: Font to use (defaults to body font)

        Returns:
            Height of the drawn panel
        """
        if self.new_item is None:
            return 0

        if font is None:
            font = pygame.font.Font(None, Fonts.SIZE_BODY)

        small_font = pygame.font.Font(None, Fonts.SIZE_SMALL)
        line_height = Layout.LINE_HEIGHT_COMPACT
        current_y = y

        # Panel background
        panel_height = self._calculate_height(font)
        panel_rect = pygame.Rect(x, y, self.width, panel_height)
        pygame.draw.rect(surface, Colors.BG_PANEL, panel_rect, border_radius=Layout.CORNER_RADIUS)
        pygame.draw.rect(surface, Colors.BORDER, panel_rect, Layout.BORDER_WIDTH, border_radius=Layout.CORNER_RADIUS)

        content_x = x + self.padding
        current_y = y + self.padding

        # Header
        header_text = "Equipment Comparison"
        header_surface = small_font.render(header_text, True, Colors.ACCENT)
        surface.blit(header_surface, (content_x, current_y))
        current_y += line_height + 4

        # Divider
        pygame.draw.line(
            surface, Colors.BORDER,
            (content_x, current_y), (x + self.width - self.padding, current_y)
        )
        current_y += 8

        # Current item label
        current_label = "Equipped:"
        current_name = self.current_item.name if self.current_item else "(None)"
        label_surf = small_font.render(current_label, True, Colors.TEXT_SECONDARY)
        surface.blit(label_surf, (content_x, current_y))
        name_surf = small_font.render(current_name, True, Colors.TEXT_PRIMARY)
        surface.blit(name_surf, (content_x + label_surf.get_width() + 4, current_y))
        current_y += line_height

        # New item label
        new_label = "New:"
        new_name = self.new_item.name
        label_surf = small_font.render(new_label, True, Colors.TEXT_SECONDARY)
        surface.blit(label_surf, (content_x, current_y))
        name_surf = small_font.render(new_name, True, Colors.TEXT_HIGHLIGHT)
        surface.blit(name_surf, (content_x + label_surf.get_width() + 4, current_y))
        current_y += line_height + 8

        # Divider
        pygame.draw.line(
            surface, Colors.BORDER,
            (content_x, current_y), (x + self.width - self.padding, current_y)
        )
        current_y += 8

        # Stat comparisons
        stat_col_x = content_x
        current_col_x = content_x + 50
        arrow_col_x = content_x + 90
        new_col_x = content_x + 115
        diff_col_x = content_x + 155

        for stat_label, stat_key in self.STAT_LABELS:
            current_val = self._get_stat_modifier(self.current_item, stat_key)
            new_val = self._get_stat_modifier(self.new_item, stat_key)
            diff = new_val - current_val

            # Skip if both are zero (stat not relevant for this equipment)
            if current_val == 0 and new_val == 0:
                continue

            diff_color = self._get_stat_diff_color(diff)

            # Stat label
            stat_surf = small_font.render(f"{stat_label}:", True, Colors.TEXT_SECONDARY)
            surface.blit(stat_surf, (stat_col_x, current_y))

            # Current value
            current_surf = small_font.render(f"{current_val:+d}" if current_val != 0 else "0", True, Colors.TEXT_PRIMARY)
            surface.blit(current_surf, (current_col_x, current_y))

            # Arrow
            arrow_surf = small_font.render("->", True, Colors.TEXT_SECONDARY)
            surface.blit(arrow_surf, (arrow_col_x, current_y))

            # New value
            new_surf = small_font.render(f"{new_val:+d}" if new_val != 0 else "0", True, Colors.TEXT_PRIMARY)
            surface.blit(new_surf, (new_col_x, current_y))

            # Difference
            if diff != 0:
                diff_text = f"({diff:+d})"
                diff_surf = small_font.render(diff_text, True, diff_color)
                surface.blit(diff_surf, (diff_col_x, current_y))

            current_y += line_height

        # Granted skills comparison
        current_skills = set(self.current_item.granted_skills) if self.current_item else set()
        new_skills = set(self.new_item.granted_skills) if self.new_item else set()

        gained_skills = new_skills - current_skills
        lost_skills = current_skills - new_skills

        if gained_skills or lost_skills:
            current_y += 4
            pygame.draw.line(
                surface, Colors.BORDER,
                (content_x, current_y), (x + self.width - self.padding, current_y)
            )
            current_y += 8

            # Skills header
            skills_header = small_font.render("Skills:", True, Colors.ACCENT)
            surface.blit(skills_header, (content_x, current_y))
            current_y += line_height

            # Gained skills
            for skill in gained_skills:
                skill_text = f"  + {skill.replace('_', ' ').title()}"
                skill_surf = small_font.render(skill_text, True, Colors.TEXT_SUCCESS)
                surface.blit(skill_surf, (content_x, current_y))
                current_y += line_height

            # Lost skills
            for skill in lost_skills:
                skill_text = f"  - {skill.replace('_', ' ').title()}"
                skill_surf = small_font.render(skill_text, True, Colors.TEXT_ERROR)
                surface.blit(skill_surf, (content_x, current_y))
                current_y += line_height

        return panel_height

    def _calculate_height(self, font: pygame.font.Font) -> int:
        """Calculate the total height needed for the panel."""
        line_height = Layout.LINE_HEIGHT_COMPACT
        height = self.padding * 2  # Top and bottom padding

        # Header + divider
        height += line_height + 4 + 8

        # Current and new item labels
        height += line_height * 2 + 8

        # Divider
        height += 8

        # Count non-zero stats
        stat_count = 0
        for _, stat_key in self.STAT_LABELS:
            current_val = self._get_stat_modifier(self.current_item, stat_key)
            new_val = self._get_stat_modifier(self.new_item, stat_key)
            if current_val != 0 or new_val != 0:
                stat_count += 1

        # At minimum show 3 stats even if zero
        stat_count = max(stat_count, 1)
        height += stat_count * line_height

        # Skills section
        current_skills = set(self.current_item.granted_skills) if self.current_item else set()
        new_skills = set(self.new_item.granted_skills) if self.new_item else set()
        gained_skills = new_skills - current_skills
        lost_skills = current_skills - new_skills

        if gained_skills or lost_skills:
            height += 4 + 8  # Divider
            height += line_height  # Skills header
            height += len(gained_skills) * line_height
            height += len(lost_skills) * line_height

        return height


def get_equipped_item_for_slot(player, slot: str, items_db: Dict[str, Item]) -> Optional[Item]:
    """
    Get the currently equipped item for a given slot.

    Args:
        player: Player entity with equipment dict
        slot: Equipment slot ("weapon", "armor", "accessory")
        items_db: Item database

    Returns:
        Item if equipped, None otherwise
    """
    if not hasattr(player, 'equipment') or not player.equipment:
        return None

    equipped_id = player.equipment.get(slot)
    if not equipped_id:
        return None

    return items_db.get(equipped_id)

"""Skill tree scene for viewing and unlocking skills."""

from typing import Dict, List, Optional, Tuple, TYPE_CHECKING

import pygame

from .base_menu_scene import BaseMenuScene
from .assets import AssetManager
from .ui import Menu, MessageBox, NineSlicePanel, draw_contextual_help
from .theme import Colors, Fonts, Layout
from core.entities import Player, PartyMember, Entity
from core.skill_tree import (
    SkillTree, SkillNode, SkillTreeProgress, SkillTreeManager,
    load_skill_trees_from_json
)
from core.tutorial_system import TipTrigger

if TYPE_CHECKING:
    from .scene import SceneManager


# Class to skill tree mapping
CLASS_TREE_MAP = {
    "warrior": "warrior",
    "mage": "mage",
    "healer": "healer",
    "rogue": "rogue",
    "fighter": "warrior",  # Alias
    "wizard": "mage",      # Alias
    "cleric": "healer",    # Alias
    "thief": "rogue",      # Alias
}


class SkillTreeScene(BaseMenuScene):
    """Scene for viewing and managing skill trees."""

    def __init__(
        self,
        manager: Optional["SceneManager"],
        entity: Entity,  # Player or PartyMember
        assets: Optional[AssetManager] = None,
        scale: int = 2,
    ):
        super().__init__(manager, assets, scale)
        self.entity = entity

        # Load skill trees
        self.skill_trees = load_skill_trees_from_json()
        self.tree_manager = SkillTreeManager(self.skill_trees)

        # Get entity's skill tree progress
        self.progress: SkillTreeProgress = getattr(entity, "skill_tree_progress", SkillTreeProgress())

        # Determine entity's class for tree recommendations
        self.entity_class = self._get_entity_class()
        self.recommended_tree_id = CLASS_TREE_MAP.get(self.entity_class.lower() if self.entity_class else "", None)

        # UI state - sort trees to put recommended first
        self.tree_ids = self._get_sorted_tree_ids()
        self.current_tree_index = 0
        self.selected_node_index = 0
        self.visible_nodes: List[SkillNode] = []

        # Scroll state for large trees
        self.scroll_offset = 0
        self.max_visible_nodes = 8

        # Visual mode: "list" or "graph"
        self.view_mode = "graph"

        # Message display
        self.message_box: Optional[MessageBox] = None
        self.showing_message = False
        self.message_timer = 0.0
        self.message_duration = 2.0
        self._pending_message_text: Optional[str] = None  # For deferred message box creation

        # Overlay for dimming background (using cached overlay from base class)

        # Build initial node list
        self._refresh_visible_nodes()

    def _get_entity_class(self) -> Optional[str]:
        """Get the entity's class for tree recommendations."""
        # Check player_class first (Player entity)
        if hasattr(self.entity, "player_class") and self.entity.player_class:
            return self.entity.player_class
        # Check role (PartyMember entity)
        if hasattr(self.entity, "role") and self.entity.role:
            return self.entity.role
        return None

    def _get_sorted_tree_ids(self) -> List[str]:
        """Get tree IDs sorted with recommended tree first."""
        tree_ids = list(self.skill_trees.keys())
        if self.recommended_tree_id and self.recommended_tree_id in tree_ids:
            # Move recommended tree to front
            tree_ids.remove(self.recommended_tree_id)
            tree_ids.insert(0, self.recommended_tree_id)
        return tree_ids

    def _is_recommended_tree(self, tree_id: str) -> bool:
        """Check if a tree is recommended for this entity's class."""
        return tree_id == self.recommended_tree_id

    def _refresh_visible_nodes(self) -> None:
        """Refresh the list of visible nodes for the current tree."""
        if not self.tree_ids:
            self.visible_nodes = []
            return

        tree_id = self.tree_ids[self.current_tree_index]
        tree = self.skill_trees.get(tree_id)
        if not tree:
            self.visible_nodes = []
            return

        # Get all nodes sorted by tier then by name
        nodes = list(tree.nodes.values())
        nodes.sort(key=lambda n: (n.tier, n.name))
        self.visible_nodes = nodes

        # Clamp selection
        if self.selected_node_index >= len(self.visible_nodes):
            self.selected_node_index = max(0, len(self.visible_nodes) - 1)

    def _get_current_tree(self) -> Optional[SkillTree]:
        """Get the currently selected skill tree."""
        if not self.tree_ids:
            return None
        tree_id = self.tree_ids[self.current_tree_index]
        return self.skill_trees.get(tree_id)

    def _get_selected_node(self) -> Optional[SkillNode]:
        """Get the currently selected node."""
        if not self.visible_nodes or self.selected_node_index >= len(self.visible_nodes):
            return None
        return self.visible_nodes[self.selected_node_index]

    def _get_node_status(self, node: SkillNode, tree: SkillTree) -> str:
        """Get the status of a node: 'unlocked', 'available', or 'locked'."""
        unlocked = self.progress.get_unlocked_for_tree(tree.id)

        if node.id in unlocked:
            return "unlocked"
        elif node.can_unlock(unlocked):
            return "available"
        else:
            return "locked"

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle input events."""
        if self.showing_message:
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_ESCAPE):
                self.showing_message = False
                self.message_box = None
                self._pending_message_text = None
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._exit_scene()
            elif event.key == pygame.K_UP:
                self._move_selection(-1)
            elif event.key == pygame.K_DOWN:
                self._move_selection(1)
            elif event.key == pygame.K_LEFT:
                self._switch_tree(-1)
            elif event.key == pygame.K_RIGHT:
                self._switch_tree(1)
            elif event.key == pygame.K_RETURN:
                self._try_unlock_node()
            elif event.key == pygame.K_TAB:
                # Toggle view mode
                self.view_mode = "list" if self.view_mode == "graph" else "graph"

    def _move_selection(self, delta: int) -> None:
        """Move node selection up or down."""
        if not self.visible_nodes:
            return
        self.selected_node_index = (self.selected_node_index + delta) % len(self.visible_nodes)

    def _switch_tree(self, delta: int) -> None:
        """Switch to a different skill tree."""
        if not self.tree_ids:
            return
        self.current_tree_index = (self.current_tree_index + delta) % len(self.tree_ids)
        self.selected_node_index = 0
        self.scroll_offset = 0
        self._refresh_visible_nodes()

    def _try_unlock_node(self) -> None:
        """Attempt to unlock the selected node."""
        tree = self._get_current_tree()
        node = self._get_selected_node()

        if not tree or not node:
            return

        total_unlocked_before = sum(len(nodes) for nodes in self.progress.unlocked_nodes.values())

        success, message, unlocked_node = self.progress.unlock_node(tree, node.id)

        if success and unlocked_node:
            # Apply stat bonuses to entity's stats
            if self.entity.stats and unlocked_node.stat_bonuses:
                self.tree_manager.apply_skill_tree_bonuses(self.entity.stats, self.progress)

            if total_unlocked_before == 0:
                tutorial_manager = self.get_manager_attr(
                    "tutorial_manager", "_try_unlock_node"
                )
                if tutorial_manager:
                    tutorial_manager.trigger_tip(TipTrigger.FIRST_SKILL_UNLOCK)

            # Add skill to entity if node grants one
            if unlocked_node.skill_id:
                if hasattr(self.entity, "base_skills"):
                    if unlocked_node.skill_id not in self.entity.base_skills:
                        self.entity.base_skills.append(unlocked_node.skill_id)
                if hasattr(self.entity, "skills"):
                    if unlocked_node.skill_id not in self.entity.skills:
                        self.entity.skills.append(unlocked_node.skill_id)

        # Show message
        self._show_message(message)

    def _show_message(self, text: str) -> None:
        """Show a temporary message. Position is calculated dynamically in draw()."""
        self._pending_message_text = text
        self.showing_message = True
        self.message_timer = 0.0

    def _exit_scene(self) -> None:
        """Exit the skill tree scene."""
        self.manager.pop()

    def update(self, dt: float) -> None:
        """Update scene state."""
        if self.showing_message:
            self.message_timer += dt
            if self.message_timer >= self.message_duration:
                self.showing_message = False
                self.message_box = None
                self._pending_message_text = None

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the skill tree scene."""
        size = surface.get_size()

        # Draw semi-transparent overlay
        if not self.overlay or self.overlay.get_size() != size:
            self.overlay = pygame.Surface(size)
            self.overlay.set_alpha(220)
            self.overlay.fill((20, 20, 30))
        surface.blit(self.overlay, (0, 0))

        font = self.assets.get_font("default")
        small_font = self.assets.get_font("small") or font
        large_font = self.assets.get_font("large", 24) or font

        # Draw title
        title_text = large_font.render("SKILL TREES", True, Colors.TEXT_PRIMARY)
        title_rect = title_text.get_rect(center=(size[0] // 2, 30))
        surface.blit(title_text, title_rect)

        # Draw entity name, class, and skill points
        entity_name = getattr(self.entity, "name", "Unknown")
        class_str = f" ({self.entity_class.title()})" if self.entity_class else ""
        sp_text = f"{entity_name}{class_str} - Skill Points: {self.progress.skill_points}"
        sp_surface = font.render(sp_text, True, Colors.ACCENT)
        surface.blit(sp_surface, (20, 60))

        # Draw tree tabs
        self._draw_tree_tabs(surface, font, 20, 90)

        # Draw current tree based on view mode
        tree = self._get_current_tree()
        if tree:
            if self.view_mode == "graph":
                self._draw_tree_graph(surface, tree, font, small_font, 20, 130)
            else:
                self._draw_tree(surface, tree, font, small_font, 20, 130)
        else:
            no_tree_text = font.render("No skill trees available", True, Colors.TEXT_SECONDARY)
            surface.blit(no_tree_text, (20, 130))

        # Draw selected node details
        self._draw_node_details(surface, font, small_font, 400, 130)

        # Draw message if showing (create MessageBox with dynamic position if needed)
        if self.showing_message:
            if self._pending_message_text and not self.message_box:
                # Create MessageBox centered horizontally, near bottom of screen
                msg_width = 340
                msg_height = 60
                msg_x = (size[0] - msg_width) // 2
                msg_y = size[1] - 120  # 120 pixels from bottom
                self.message_box = MessageBox(position=(msg_x, msg_y), width=msg_width, height=msg_height)
                self.message_box.set_text(self._pending_message_text)
                self._pending_message_text = None
            if self.message_box:
                self.message_box.draw(surface, small_font, panel=self.panel)

        # Draw help text at bottom
        self._draw_help_text(surface, small_font)

    def _draw_help_text(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        """Draw standardized help text at the bottom of the screen."""
        width, height = surface.get_size()

        mode_hint = "TAB: List View" if self.view_mode == "graph" else "TAB: Graph View"
        help_text = f"Up/Down: Select  |  Left/Right: Tree  |  Enter: Unlock  |  {mode_hint}  |  ESC: Back"

        draw_contextual_help(surface, help_text, font, margin_bottom=Layout.SCREEN_MARGIN)

    def _draw_tree_tabs(self, surface: pygame.Surface, font: pygame.font.Font, x: int, y: int) -> None:
        """Draw skill tree selection tabs."""
        tab_x = x
        for i, tree_id in enumerate(self.tree_ids):
            tree = self.skill_trees.get(tree_id)
            if not tree:
                continue

            is_selected = i == self.current_tree_index
            is_recommended = self._is_recommended_tree(tree_id)

            # Determine colors based on selection and recommendation
            if is_selected:
                text_color = Colors.TEXT_PRIMARY
                bg_color = Colors.BG_PANEL if not is_recommended else Colors.BG_DARK
                border_color = Colors.TEXT_INFO if is_recommended else Colors.ACCENT
            else:
                text_color = Colors.TEXT_INFO if is_recommended else Colors.TEXT_SECONDARY
                bg_color = Colors.BG_DARK
                border_color = Colors.TEXT_INFO if is_recommended else Colors.BORDER

            # Draw tab background
            tab_width = 100
            tab_height = 25
            tab_rect = pygame.Rect(tab_x, y, tab_width, tab_height)

            pygame.draw.rect(surface, bg_color, tab_rect)
            pygame.draw.rect(surface, border_color, tab_rect, 2 if is_selected else 1)

            # Draw recommended star indicator
            tab_label = tree.name
            if is_recommended:
                tab_label = f"★ {tree.name}"

            # Draw tab text
            tab_text = font.render(tab_label, True, text_color)
            text_rect = tab_text.get_rect(center=tab_rect.center)
            surface.blit(tab_text, text_rect)

            tab_x += tab_width + 5

    def _draw_tree(
        self,
        surface: pygame.Surface,
        tree: SkillTree,
        font: pygame.font.Font,
        small_font: pygame.font.Font,
        x: int,
        y: int
    ) -> None:
        """Draw the skill tree nodes."""
        unlocked = self.progress.get_unlocked_for_tree(tree.id)

        # Draw tree description
        desc_surface = small_font.render(tree.description, True, (180, 180, 180))
        surface.blit(desc_surface, (x, y))

        # Draw nodes list
        node_y = y + 30
        node_height = 28

        for i, node in enumerate(self.visible_nodes):
            is_selected = i == self.selected_node_index
            status = self._get_node_status(node, tree)

            # Determine colors
            if status == "unlocked":
                bg_color = Colors.BG_DARK
                text_color = Colors.SKILL_UNLOCKED
                status_text = "[UNLOCKED]"
            elif status == "available":
                bg_color = Colors.BG_DARK
                text_color = Colors.SKILL_AVAILABLE
                status_text = f"[{node.cost} SP]"
            else:
                bg_color = Colors.BG_DARK
                text_color = Colors.SKILL_LOCKED
                status_text = "[LOCKED]"

            # Draw selection highlight
            node_rect = pygame.Rect(x, node_y, 350, node_height - 2)
            if is_selected:
                pygame.draw.rect(surface, Colors.BG_PANEL, node_rect)
                pygame.draw.rect(surface, Colors.ACCENT, node_rect, 2)
            else:
                pygame.draw.rect(surface, bg_color, node_rect)

            # Draw tier indicator
            tier_text = small_font.render(f"T{node.tier}", True, Colors.TEXT_DISABLED)
            surface.blit(tier_text, (x + 5, node_y + 5))

            # Draw node name
            name_surface = font.render(node.name, True, text_color)
            surface.blit(name_surface, (x + 35, node_y + 3))

            # Draw status
            status_surface = small_font.render(status_text, True, text_color)
            surface.blit(status_surface, (x + 260, node_y + 5))

            node_y += node_height

            # Limit visible nodes
            if node_y > 380:
                more_text = small_font.render(f"... and {len(self.visible_nodes) - i - 1} more", True, Colors.TEXT_DISABLED)
                surface.blit(more_text, (x + 35, node_y))
                break

    def _draw_tree_graph(
        self,
        surface: pygame.Surface,
        tree: SkillTree,
        font: pygame.font.Font,
        small_font: pygame.font.Font,
        x: int,
        y: int
    ) -> None:
        """Draw the skill tree as a visual node graph with connections."""
        unlocked = self.progress.get_unlocked_for_tree(tree.id)

        # Draw tree description
        desc_surface = small_font.render(tree.description, True, (180, 180, 180))
        surface.blit(desc_surface, (x, y))

        # Layout configuration
        graph_y = y + 25
        graph_width = 360
        node_width = 100
        node_height = 32
        tier_spacing = 55

        # Group nodes by tier
        tiers = tree.get_nodes_by_tier()
        max_tier = max(tiers.keys()) if tiers else 1

        # Calculate node positions
        node_positions: Dict[str, Tuple[int, int]] = {}
        for tier_num in sorted(tiers.keys()):
            tier_nodes = tiers[tier_num]
            tier_y = graph_y + (tier_num - 1) * tier_spacing

            # Distribute nodes horizontally within tier
            num_nodes = len(tier_nodes)
            if num_nodes == 1:
                positions = [x + graph_width // 2 - node_width // 2]
            else:
                spacing = (graph_width - node_width) // (num_nodes - 1) if num_nodes > 1 else 0
                positions = [x + i * spacing for i in range(num_nodes)]

            for i, node in enumerate(tier_nodes):
                node_positions[node.id] = (positions[i], tier_y)

        # Draw connection lines first (behind nodes)
        for node in self.visible_nodes:
            if not node.prerequisites:
                continue
            node_pos = node_positions.get(node.id)
            if not node_pos:
                continue

            for prereq_id in node.prerequisites:
                prereq_pos = node_positions.get(prereq_id)
                if not prereq_pos:
                    continue

                # Determine line color based on unlock status
                prereq_unlocked = prereq_id in unlocked
                node_unlocked = node.id in unlocked
                if node_unlocked:
                    line_color = Colors.ACCENT_DIM
                elif prereq_unlocked:
                    line_color = Colors.SKILL_AVAILABLE
                else:
                    line_color = Colors.BORDER

                # Draw line from prereq bottom to node top
                start_x = prereq_pos[0] + node_width // 2
                start_y = prereq_pos[1] + node_height
                end_x = node_pos[0] + node_width // 2
                end_y = node_pos[1]

                pygame.draw.line(surface, line_color, (start_x, start_y), (end_x, end_y), 2)

        # Draw nodes
        for i, node in enumerate(self.visible_nodes):
            pos = node_positions.get(node.id)
            if not pos:
                continue

            is_selected = i == self.selected_node_index
            status = self._get_node_status(node, tree)

            # Determine colors
            if status == "unlocked":
                bg_color = Colors.BG_DARK
                border_color = Colors.SKILL_UNLOCKED
                text_color = Colors.SKILL_UNLOCKED
            elif status == "available":
                bg_color = Colors.BG_DARK
                border_color = Colors.SKILL_AVAILABLE
                text_color = Colors.SKILL_AVAILABLE
            else:
                bg_color = Colors.BG_DARK
                border_color = Colors.SKILL_LOCKED
                text_color = Colors.SKILL_LOCKED

            # Draw node box
            node_rect = pygame.Rect(pos[0], pos[1], node_width, node_height)
            pygame.draw.rect(surface, bg_color, node_rect, border_radius=4)

            # Selection highlight
            if is_selected:
                pygame.draw.rect(surface, Colors.ACCENT, node_rect, 3, border_radius=4)
            else:
                pygame.draw.rect(surface, border_color, node_rect, 1, border_radius=4)

            # Draw node name (truncate if needed)
            name = node.name
            if small_font.size(name)[0] > node_width - 8:
                while small_font.size(name + "...")[0] > node_width - 8 and len(name) > 3:
                    name = name[:-1]
                name += "..."

            name_surface = small_font.render(name, True, text_color)
            name_rect = name_surface.get_rect(center=(pos[0] + node_width // 2, pos[1] + node_height // 2))
            surface.blit(name_surface, name_rect)

            # Draw small status icon in corner
            if status == "unlocked":
                icon = "✓"
                icon_color = Colors.SKILL_UNLOCKED
            elif status == "available":
                icon = f"{node.cost}"
                icon_color = Colors.SKILL_AVAILABLE
            else:
                icon = "✗"
                icon_color = Colors.SKILL_LOCKED

            icon_surface = small_font.render(icon, True, icon_color)
            surface.blit(icon_surface, (pos[0] + node_width - 14, pos[1] + 2))

    def _draw_node_details(
        self,
        surface: pygame.Surface,
        font: pygame.font.Font,
        small_font: pygame.font.Font,
        x: int,
        y: int
    ) -> None:
        """Draw details for the selected node."""
        node = self._get_selected_node()
        tree = self._get_current_tree()

        if not node or not tree:
            return

        # Draw panel background
        panel_rect = pygame.Rect(x, y, 220, 250)
        if self.panel:
            self.panel.draw(surface, panel_rect)
        else:
            pygame.draw.rect(surface, Colors.BG_PANEL, panel_rect)
            pygame.draw.rect(surface, Colors.BORDER, panel_rect, 2)

        # Draw node name
        name_surface = font.render(node.name, True, Colors.TEXT_PRIMARY)
        surface.blit(name_surface, (x + 10, y + 10))

        # Draw description
        desc_y = y + 35
        words = node.description.split()
        line = ""
        for word in words:
            test_line = line + word + " "
            if small_font.size(test_line)[0] > 200:
                desc_surface = small_font.render(line, True, Colors.TEXT_SECONDARY)
                surface.blit(desc_surface, (x + 10, desc_y))
                desc_y += 18
                line = word + " "
            else:
                line = test_line
        if line:
            desc_surface = small_font.render(line, True, Colors.TEXT_SECONDARY)
            surface.blit(desc_surface, (x + 10, desc_y))
            desc_y += 18

        # Draw cost
        desc_y += 10
        cost_text = f"Cost: {node.cost} SP"
        cost_surface = small_font.render(cost_text, True, Colors.ACCENT)
        surface.blit(cost_surface, (x + 10, desc_y))
        desc_y += 20

        # Draw stat bonuses
        if node.stat_bonuses:
            bonus_title = small_font.render("Stat Bonuses:", True, Colors.TEXT_SUCCESS)
            surface.blit(bonus_title, (x + 10, desc_y))
            desc_y += 18

            for stat, value in node.stat_bonuses.items():
                sign = "+" if value > 0 else ""
                bonus_text = f"  {stat.replace('_', ' ').title()}: {sign}{value}"
                bonus_surface = small_font.render(bonus_text, True, Colors.TEXT_SUCCESS)
                surface.blit(bonus_surface, (x + 10, desc_y))
                desc_y += 16

        # Draw skill granted
        if node.skill_id:
            desc_y += 5
            skill_text = f"Grants: {node.skill_id.replace('_', ' ').title()}"
            skill_surface = small_font.render(skill_text, True, Colors.TEXT_INFO)
            surface.blit(skill_surface, (x + 10, desc_y))
            desc_y += 18

        # Draw prerequisites
        if node.prerequisites:
            desc_y += 5
            prereq_title = small_font.render("Requires:", True, Colors.TEXT_ERROR)
            surface.blit(prereq_title, (x + 10, desc_y))
            desc_y += 16

            unlocked = self.progress.get_unlocked_for_tree(tree.id)
            for prereq_id in node.prerequisites:
                prereq_node = tree.get_node(prereq_id)
                prereq_name = prereq_node.name if prereq_node else prereq_id
                is_met = prereq_id in unlocked
                color = Colors.TEXT_SUCCESS if is_met else Colors.TEXT_ERROR
                prefix = "✓ " if is_met else "✗ "
                prereq_text = f"  {prefix}{prereq_name}"
                prereq_surface = small_font.render(prereq_text, True, color)
                surface.blit(prereq_surface, (x + 10, desc_y))
                desc_y += 16

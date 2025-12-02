"""Challenge dungeon selection scene."""

import pygame
from typing import Optional, Dict, List, Any, TYPE_CHECKING

from .base_menu_scene import BaseMenuScene
from .assets import AssetManager
from .ui import Menu, MessageBox, NineSlicePanel
from .theme import Colors, Fonts
from core.challenge_dungeons import ChallengeDungeonManager, ChallengeTier
from core.entities import Player
from core.world import World

if TYPE_CHECKING:
    from .scene import SceneManager


class ChallengeSelectScene(BaseMenuScene):
    """Scene for selecting and viewing challenge dungeons."""

    COLORS = {
        "bg": (20, 25, 40),
        "panel_bg": (35, 40, 60),
        "panel_border": (80, 90, 120),
        "title": (255, 248, 220),
        "dungeon_active": (255, 255, 255),
        "dungeon_locked": (140, 150, 180),
        "highlight": (60, 70, 110),
        "accent": (255, 200, 100),
        "tier_apprentice": (150, 200, 255),
        "tier_adept": (100, 200, 150),
        "tier_expert": (255, 200, 100),
        "tier_master": (255, 150, 100),
        "tier_legendary": (200, 100, 255),
    }

    def __init__(
        self,
        manager: Optional["SceneManager"],
        challenge_manager: ChallengeDungeonManager,
        player: Player,
        world: World,
        assets: Optional[AssetManager] = None,
        scale: int = 2,
    ):
        """
        Initialize challenge selection scene.

        Args:
            manager: Scene manager
            challenge_manager: ChallengeDungeonManager instance
            player: Player instance
            world: World instance
            assets: Asset manager
            scale: Display scale
        """
        super().__init__(manager, assets, scale)
        self.challenge_manager = challenge_manager
        self.player = player
        self.world = world

        # Group dungeons by tier
        self.dungeons_by_tier: Dict[ChallengeTier, List[str]] = {}
        for dungeon_id, dungeon in challenge_manager.dungeons.items():
            tier = dungeon.tier
            if tier not in self.dungeons_by_tier:
                self.dungeons_by_tier[tier] = []
            self.dungeons_by_tier[tier].append(dungeon_id)

        # Flatten to list for selection
        self.dungeon_list: List[str] = []
        for tier in ChallengeTier:
            if tier in self.dungeons_by_tier:
                self.dungeon_list.extend(self.dungeons_by_tier[tier])

        self.selected_index = 0

        # UI state
        self.message_box: Optional[MessageBox] = None
        self.showing_message = False
        self.message_timer = 0.0
        self.message_duration = 2.0

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle input events."""
        if self.showing_message:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.showing_message = False
                self.message_box = None
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_index = (self.selected_index - 1) % len(self.dungeon_list)
            elif event.key == pygame.K_DOWN:
                self.selected_index = (self.selected_index + 1) % len(self.dungeon_list)
            elif event.key == pygame.K_RETURN:
                self._attempt_dungeon()
            elif event.key == pygame.K_ESCAPE:
                self.manager.pop()

    def _attempt_dungeon(self) -> None:
        """Attempt to enter the selected dungeon."""
        if not self.dungeon_list:
            return

        dungeon_id = self.dungeon_list[self.selected_index]
        dungeon = self.challenge_manager.dungeons.get(dungeon_id)
        if not dungeon:
            return

        # Get post-game manager
        post_game_manager = self.get_manager_attr(
            "post_game_manager", "_attempt_dungeon"
        )
        if not post_game_manager:
            self._show_message("Post-game system not available")
            return

        # Check access
        can_enter, reason = self.challenge_manager.can_enter(
            dungeon_id,
            self.player.stats.level,
            post_game_manager
        )

        if not can_enter:
            self._show_message(f"Cannot enter: {reason}")
            return

        # Enter dungeon and warp player
        self.challenge_manager.enter_dungeon(dungeon_id)

        # Warp player to dungeon entry
        from .world_scene import WorldScene
        world_scene = self.manager.get_scene_of_type(WorldScene)
        if world_scene:
            world_scene.world.set_current_map(dungeon.entry_map_id)
            world_scene.player.set_position(dungeon.entry_x, dungeon.entry_y)
            self.manager.pop()  # Return to world scene
        else:
            self._show_message("Cannot enter dungeon: world scene not found")

    def _show_message(self, text: str) -> None:
        """Show a temporary message."""
        self.message_box = MessageBox(position=(200, 350), width=400, height=60)
        self.message_box.set_text(text)
        self.showing_message = True
        self.message_timer = 0.0

    def update(self, dt: float) -> None:
        """Update scene state."""
        if self.showing_message:
            self.message_timer += dt
            if self.message_timer >= self.message_duration:
                self.showing_message = False
                self.message_box = None

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the challenge selection scene."""
        width, height = surface.get_size()

        # Draw background
        surface.fill(self.COLORS["bg"])

        # Draw title
        self._draw_title(surface, width // 2, 30)

        # Draw dungeon list (left side)
        list_x = 50
        list_y = 80
        self._draw_dungeon_list(surface, list_x, list_y, width // 2 - 100, height - 120)

        # Draw selected dungeon details (right side)
        detail_x = width // 2 + 50
        detail_y = 80
        self._draw_dungeon_details(surface, detail_x, detail_y, width - detail_x - 50, height - 120)

        # Draw instructions
        self._draw_instructions(surface, width // 2, height - 30)

        # Draw message box if showing
        if self.message_box:
            self.message_box.draw(surface, self.assets.get_font("small"), panel=self.panel)

    def _draw_title(self, surface: pygame.Surface, center_x: int, y: int) -> None:
        """Draw the scene title."""
        font = self.assets.get_font("large", 32) or pygame.font.Font(None, 32)
        title = font.render("Challenge Dungeons", True, self.COLORS["title"])
        title_rect = title.get_rect(center=(center_x, y))
        surface.blit(title, title_rect)

    def _draw_dungeon_list(
        self, surface: pygame.Surface, x: int, y: int, width: int, height: int
    ) -> None:
        """Draw the list of dungeons."""
        font = self.assets.get_font("default", 18) or pygame.font.Font(None, 18)
        small_font = self.assets.get_font("small", 14) or pygame.font.Font(None, 14)

        # Draw panel background
        panel_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(surface, self.COLORS["panel_bg"], panel_rect, border_radius=8)
        pygame.draw.rect(surface, self.COLORS["panel_border"], panel_rect, width=2, border_radius=8)

        # Draw dungeons
        item_height = 50
        max_items = (height - 20) // item_height
        start_index = max(0, self.selected_index - max_items + 1)
        end_index = min(len(self.dungeon_list), start_index + max_items)

        for i in range(start_index, end_index):
            dungeon_id = self.dungeon_list[i]
            dungeon = self.challenge_manager.dungeons.get(dungeon_id)
            if not dungeon:
                continue

            item_y = y + 10 + (i - start_index) * item_height
            is_selected = i == self.selected_index

            # Highlight selected
            if is_selected:
                highlight_rect = pygame.Rect(x + 5, item_y, width - 10, item_height - 5)
                pygame.draw.rect(surface, self.COLORS["highlight"], highlight_rect, border_radius=4)

            # Get post-game manager
            post_game_manager = self.get_manager_attr(
                "post_game_manager", "_draw_dungeon_list"
            )
            if post_game_manager:
                can_enter, _ = self.challenge_manager.can_enter(
                    dungeon_id, self.player.stats.level, post_game_manager
                )
            else:
                can_enter = False

            # Tier color
            tier_color = self.COLORS.get(f"tier_{dungeon.tier.value}", Colors.WHITE)
            text_color = self.COLORS["dungeon_active"] if can_enter else self.COLORS["dungeon_locked"]

            # Draw tier indicator
            tier_rect = pygame.Rect(x + 10, item_y + 5, 8, 40)
            pygame.draw.rect(surface, tier_color, tier_rect)

            # Draw dungeon name
            name_text = font.render(dungeon.name, True, text_color)
            surface.blit(name_text, (x + 25, item_y + 8))

            # Draw lock icon if locked
            if not can_enter:
                lock_text = small_font.render("🔒", True, self.COLORS["dungeon_locked"])
                surface.blit(lock_text, (x + width - 30, item_y + 15))

    def _draw_dungeon_details(
        self, surface: pygame.Surface, x: int, y: int, width: int, height: int
    ) -> None:
        """Draw details for the selected dungeon."""
        if not self.dungeon_list:
            return

        dungeon_id = self.dungeon_list[self.selected_index]
        dungeon = self.challenge_manager.dungeons.get(dungeon_id)
        if not dungeon:
            return

        # Draw panel
        panel_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(surface, self.COLORS["panel_bg"], panel_rect, border_radius=8)
        pygame.draw.rect(surface, self.COLORS["panel_border"], panel_rect, width=2, border_radius=8)

        font = self.assets.get_font("default", 20) or pygame.font.Font(None, 20)
        small_font = self.assets.get_font("small", 16) or pygame.font.Font(None, 16)

        current_y = y + 20

        # Dungeon name
        name_text = font.render(dungeon.name, True, self.COLORS["dungeon_active"])
        surface.blit(name_text, (x + 20, current_y))
        current_y += 35

        # Description
        desc_text = small_font.render(dungeon.description, True, Colors.TEXT_SECONDARY)
        # Word wrap description
        words = dungeon.description.split()
        lines = []
        current_line = ""
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            if small_font.size(test_line)[0] < width - 40:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)

        for line in lines:
            desc_surface = small_font.render(line, True, Colors.TEXT_SECONDARY)
            surface.blit(desc_surface, (x + 20, current_y))
            current_y += 20

        current_y += 10

        # Tier
        tier_text = small_font.render(f"Tier: {dungeon.tier.value.title()}", True, self.COLORS.get(f"tier_{dungeon.tier.value}", Colors.WHITE))
        surface.blit(tier_text, (x + 20, current_y))
        current_y += 25

        # Level requirement
        level_text = small_font.render(f"Required Level: {dungeon.required_level}", True, Colors.TEXT_SECONDARY)
        surface.blit(level_text, (x + 20, current_y))
        current_y += 25

        # Modifiers
        if dungeon.modifiers:
            mod_label = small_font.render("Modifiers:", True, Colors.TEXT_SECONDARY)
            surface.blit(mod_label, (x + 20, current_y))
            current_y += 20

            for mod_id in dungeon.modifiers:
                mod = self.challenge_manager.modifiers.get(mod_id)
                if mod:
                    mod_text = small_font.render(f"• {mod.name}: {mod.description}", True, Colors.TEXT_SECONDARY)
                    surface.blit(mod_text, (x + 30, current_y))
                    current_y += 18

        current_y += 10

        # Rewards
        rewards_label = small_font.render("Rewards:", True, Colors.TEXT_SECONDARY)
        surface.blit(rewards_label, (x + 20, current_y))
        current_y += 20

        if dungeon.rewards.get("gold"):
            gold_text = small_font.render(f"Gold: {dungeon.rewards['gold']}", True, self.COLORS["accent"])
            surface.blit(gold_text, (x + 30, current_y))
            current_y += 18

        if dungeon.rewards.get("exp"):
            exp_text = small_font.render(f"EXP: {dungeon.rewards['exp']}", True, self.COLORS["accent"])
            surface.blit(exp_text, (x + 30, current_y))
            current_y += 18

        # Progress
        progress = self.challenge_manager.progress.get(dungeon_id)
        if progress:
            current_y += 10
            if progress.cleared:
                cleared_text = small_font.render("Status: Cleared", True, self.COLORS["tier_adept"])
                surface.blit(cleared_text, (x + 20, current_y))
                current_y += 20

                if progress.best_time:
                    minutes = int(progress.best_time // 60)
                    seconds = int(progress.best_time % 60)
                    time_text = small_font.render(f"Best Time: {minutes}:{seconds:02d}", True, Colors.TEXT_SECONDARY)
                    surface.blit(time_text, (x + 20, current_y))
                    current_y += 20

                attempts_text = small_font.render(f"Attempts: {progress.attempts}", True, Colors.TEXT_SECONDARY)
                surface.blit(attempts_text, (x + 20, current_y))

    def _draw_instructions(self, surface: pygame.Surface, center_x: int, y: int) -> None:
        """Draw control instructions."""
        font = self.assets.get_font("small", 14) or pygame.font.Font(None, 14)
        instructions = "↑↓ Select  •  Enter Attempt  •  Esc Back"
        text = font.render(instructions, True, Colors.TEXT_SECONDARY)
        text_rect = text.get_rect(center=(center_x, y))
        surface.blit(text, text_rect)

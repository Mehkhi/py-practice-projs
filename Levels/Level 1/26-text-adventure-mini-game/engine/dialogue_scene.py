"""Dialogue scene for narrative choices."""

import copy
import os
from typing import Optional, Dict, List, TYPE_CHECKING

import pygame

from .base_menu_scene import BaseMenuScene
from .assets import AssetManager
from .ui import Menu, MessageBox, NineSlicePanel
from .theme import Colors, Fonts, Layout
from core.dialogue import load_dialogue_from_json, DialogueNode, DialogueTree
from core.world import World
from core.logging_utils import log_warning, log_info
from core.gambling import GamblingGameType
from core.tutorial_system import TipTrigger

if TYPE_CHECKING:
    from .scene import SceneManager
    from core.entities import Player, PartyMember


class DialogueScene(BaseMenuScene):
    """Presents a dialogue node with choices and optional flag setting."""

    def __init__(
        self,
        manager: Optional["SceneManager"],
        dialogue_id: str,
        world: Optional[World] = None,
        scale: int = 2,
        tree: Optional[DialogueTree] = None,
        assets: Optional[AssetManager] = None,
        player: Optional["Player"] = None,
    ):
        super().__init__(manager, assets, scale)
        self.world = world
        self.dialogue_id = dialogue_id
        self.player = player

        self.tree = tree or self._load_tree()
        self.current_node: Optional[DialogueNode] = self.tree.get_node(dialogue_id) if self.tree else None

        # Position message box at bottom
        self.message_box = MessageBox(
            position=(Layout.PADDING_LARGE, 320),
            width=Layout.SCREEN_WIDTH - Layout.PADDING_LARGE * 2,
            height=140
        )
        self.choice_menu: Optional[Menu] = None

        # Queued notifications to show after dialogue closes
        self._pending_notifications: List[str] = []

        self._refresh_ui()

    def _load_tree(self) -> Optional[DialogueTree]:
        """Load dialogue tree from data file."""
        path = os.path.join("data", "dialogue.json")
        if not os.path.exists(path):
            return None
        try:
            return load_dialogue_from_json(path)
        except Exception as e:
            log_warning(f"Failed to load dialogue from {path}: {e}")
            return None

    def _refresh_ui(self) -> None:
        """Update message box and choices based on current node."""
        if not self.current_node:
            return
        self.message_box.set_text(self.current_node.text)
        portrait_surface = None
        portrait_width = 0
        if self.current_node.portrait_id:
            portrait_surface = self.assets.get_image(self.current_node.portrait_id, (32, 32))
            if portrait_surface:
                portrait_width = portrait_surface.get_width()
        self.message_box.set_portrait(portrait_surface)
        choice_texts = [c.text for c in self.current_node.choices]
        if choice_texts:
            # Position menu to the right of the portrait to avoid overlap
            # Account for portrait width + padding when portrait is present
            menu_x = Layout.PADDING_LARGE + 20
            if portrait_width > 0:
                # Portrait is drawn at x + 10, with width portrait_width
                # Add extra padding after portrait
                menu_x = Layout.PADDING_LARGE + portrait_width + 30

            # Position menu below the dialogue text area
            # Message box is at y=320, with text starting around y=332
            # Leave room for ~2-3 lines of dialogue text before choices
            menu_y = self.message_box.position[1] + 60

            self.choice_menu = Menu(
                choice_texts,
                position=(menu_x, menu_y)
            )
        else:
            self.choice_menu = None

    def _apply_choice(self, index: int) -> None:
        """Handle choice selection."""
        if not self.current_node:
            return
        if index < 0 or index >= len(self.current_node.choices):
            return

        choice = self.current_node.choices[index]
        if choice.set_flag and self.world:
            self.world.set_flag(choice.set_flag, True)
            # Check for party member recruitment
            self._check_recruitment(choice.set_flag)
            # Check for hint discovery
            self._check_hint_discovery(choice.set_flag)

        # Set additional flags defined at the dialogue node level (for all choices)
        if hasattr(self.current_node, 'set_flags_after_choice') and self.current_node.set_flags_after_choice and self.world:
            for flag in self.current_node.set_flags_after_choice:
                self.world.set_flag(flag, True)
                self._check_recruitment(flag)
                # Check for hint discovery
                self._check_hint_discovery(flag)

        # Discover recipes from choice and node
        self._discover_recipes(choice.discover_recipes)
        self._discover_recipes(self.current_node.discover_recipes)

        if choice.next_id:
            self.current_node = self.tree.get_node(choice.next_id) if self.tree else None
            self._refresh_ui()
        else:
            self._close_dialogue()

    def _discover_recipes(self, recipe_ids: List[str]) -> None:
        """Handle recipe discovery and queue notification for display.

        Args:
            recipe_ids: List of recipe IDs to discover
        """
        if not recipe_ids or not self.player:
            return

        from core.crafting import discover_recipes_for_player, CraftingSystem
        newly_discovered = discover_recipes_for_player(self.player, recipe_ids)

        if not newly_discovered:
            return

        # Get crafting system to get recipe names
        crafting_system = self.get_manager_attr(
            "crafting_system", "_discover_recipes"
        )
        if not crafting_system:
            crafting_system = CraftingSystem()

        recipe_names = []
        for recipe_id in newly_discovered:
            recipe = crafting_system.get_recipe(recipe_id)
            if recipe:
                recipe_names.append(recipe.name)
            else:
                log_warning(f"Recipe ID '{recipe_id}' not found in crafting system")
                recipe_names.append(recipe_id)

        # Build notification message
        if len(recipe_names) == 1:
            notification = f"Recipe Discovered!\n\nYou learned how to craft: {recipe_names[0]}"
        else:
            recipes_text = ", ".join(recipe_names[:-1]) + f", and {recipe_names[-1]}"
            notification = f"Recipes Discovered!\n\nYou learned how to craft: {recipes_text}"

        # Queue notification for display after dialogue closes
        self._pending_notifications.append(notification)
        log_info(f"Recipe discovered: {', '.join(recipe_names)}")

    def _check_hint_discovery(self, flag: str) -> None:
        """Check if a flag matches hint discovery pattern and discover hint.

        Args:
            flag: The flag that was set
        """
        # Check if flag matches hint discovery pattern: hint_*_discovered
        if not flag.startswith("hint_") or not flag.endswith("_discovered"):
            return

        # Extract hint_id from flag (e.g., "hint_wyrm_hint_1_discovered" -> "wyrm_hint_1")
        hint_id = flag[5:-11]  # Remove "hint_" prefix and "_discovered" suffix

        hint_manager = self.get_manager_attr("hint_manager", "_check_hint_discovery")
        if not hint_manager:
            return

        # Discover the hint
        hint = hint_manager.discover_hint(hint_id)
        if hint:
            # Also discover the associated boss
            secret_boss_manager = self.get_manager_attr(
                "secret_boss_manager", "_check_hint_discovery"
            )
            if secret_boss_manager:
                secret_boss_manager.discover_boss(hint.boss_id)
            log_info(f"Hint discovered: {hint_id} for boss {hint.boss_id}")

    def _close_dialogue(self) -> None:
        """Close dialogue and show any pending notifications."""
        # Check for gambling flags before closing
        if self.world:
            gambling_manager = self.get_manager_attr(
                "gambling_manager", "_close_dialogue"
            )
            if gambling_manager:
                # Check for gambling game flags
                if self.world.get_flag("_start_blackjack"):
                    self.world.set_flag("_start_blackjack", False)
                    self._start_gambling("blackjack", 50, 1000)
                    return
                elif self.world.get_flag("_start_dice"):
                    self.world.set_flag("_start_dice", False)
                    self._start_gambling("dice_roll", 20, 1000)
                    return
                elif self.world.get_flag("_start_slots"):
                    self.world.set_flag("_start_slots", False)
                    self._start_gambling("slots", 10, 1000)
                    return
                elif self.world.get_flag("_start_cups"):
                    self.world.set_flag("_start_cups", False)
                    self._start_gambling("cups_game", 30, 1000)
                    return

            # Check for arena flag
            arena_manager = self.get_manager_attr("arena_manager", "_close_dialogue")
            if arena_manager:
                if self.world.get_flag("_open_arena"):
                    self.world.set_flag("_open_arena", False)
                    self._start_arena()
                    return

        if self._pending_notifications and self.manager:
            # Show notifications as inline dialogue messages
            self._show_pending_notifications()
        else:
            self.manager.pop()

    def _show_pending_notifications(self) -> None:
        """Show pending notifications as a dialogue sequence."""
        if not self._pending_notifications:
            self.manager.pop()
            return

        # Get the first notification
        notification = self._pending_notifications.pop(0)

        # Create a simple notification node
        from core.dialogue import DialogueChoice

        # Update the current node to show the notification
        self.current_node = DialogueNode(
            id="notification",
            text=notification,
            choices=[DialogueChoice(text="Continue", next_id=None, set_flag=None)],
            speaker=None,
            portrait_id=None
        )
        self._refresh_ui()

        # When this notification is dismissed, either show next or pop
        # This is handled by the modified flow - after showing notification,
        # the choice will have next_id=None, triggering _close_dialogue again

    def _start_gambling(self, game_type_str: str, min_bet: int, max_bet: int) -> None:
        """Start a gambling game scene."""
        gambling_manager = self.get_manager_attr(
            "gambling_manager", "_start_gambling"
        )
        if not gambling_manager:
            log_warning("Gambling manager not available")
            self.manager.pop()
            return

        try:
            game_type = GamblingGameType(game_type_str)
        except ValueError:
            log_warning(f"Invalid gambling game type: {game_type_str}")
            self.manager.pop()
            return

        from .gambling_scene import GamblingScene

        scene = GamblingScene(
            manager=self.manager,
            game_type=game_type,
            gambling_manager=gambling_manager,
            world=self.world,
            min_bet=min_bet,
            max_bet=max_bet,
            assets=self.assets,
            scale=self.scale,
        )
        self.manager.push(scene)

    def _start_arena(self) -> None:
        """Start the arena scene."""
        arena_manager = self.get_manager_attr("arena_manager", "_start_arena")
        if not arena_manager:
            log_warning("Arena manager not available")
            self.manager.pop()
            return

        from .arena_scene import ArenaScene

        scene = ArenaScene(
            manager=self.manager,
            arena_manager=arena_manager,
            world=self.world,
            assets=self.assets,
            scale=self.scale,
        )
        self.manager.push(scene)

    def _check_recruitment(self, flag: str) -> None:
        """
        Check if a flag triggers party member recruitment.

        Recruitment flags follow the pattern: {member_id}_recruited
        """
        if not flag.endswith("_recruited"):
            return

        # Extract member ID from flag (e.g., "luna_recruited" -> "luna")
        member_id = flag[:-len("_recruited")]

        # Get party prototypes from scene manager
        party_prototypes = self.get_manager_attr(
            "party_prototypes", "_check_recruitment"
        )
        if not party_prototypes:
            return

        # Check if this member exists in prototypes
        if member_id not in party_prototypes:
            return

        # Get player - try from scene, then look through scene stack for WorldScene
        player = self.player
        if not player and self.manager:
            for scene in reversed(self.manager.stack):
                if hasattr(scene, 'player'):
                    player = scene.player
                    break

        if not player:
            log_warning(f"Cannot recruit {member_id} - no player reference")
            return

        # Check if already in party
        if player.get_party_member(member_id):
            return

        had_party_members = len(player.party) > 0
        # Create a fresh copy of the party member prototype
        prototype = party_prototypes[member_id]
        new_member = self._clone_party_member(prototype)

        # Add to player's party
        added = player.add_party_member(new_member)
        if not added:
            return

        # Sync formation position to player's party_formation dict
        player.party_formation[new_member.entity_id] = new_member.formation_position

        # Recompute equipment if items_db available
        items_db = self.get_manager_attr("items_db", "_check_recruitment")
        if items_db:
            new_member.recompute_equipment(items_db)

        log_info(f"{new_member.name} has joined the party!")

        # Track recruitment achievement via event bus if available
        bus = getattr(self.manager, "event_bus", None) if self.manager else None
        if bus:
            bus.publish("party_member_recruited", member_id=member_id)

        tutorial_manager = self.get_manager_attr(
            "tutorial_manager", "_check_recruitment"
        )
        if not had_party_members and tutorial_manager:
            already_shown = self.world.get_flag("_tutorial_first_party_member", False) if self.world else False
            if self.world and not already_shown:
                self.world.set_flag("_tutorial_first_party_member", True)
            if not already_shown:
                tutorial_manager.trigger_tip(TipTrigger.FIRST_PARTY_MEMBER)

    def _clone_party_member(self, prototype: "PartyMember") -> "PartyMember":
        """Create a deep copy of a party member prototype."""
        from core.entities import PartyMember
        from core.stats import Stats
        from core.skill_tree import SkillTreeProgress

        # Clone stats
        new_stats = None
        if prototype.stats:
            new_stats = Stats(
                max_hp=prototype.stats.max_hp,
                hp=prototype.stats.hp,
                max_sp=prototype.stats.max_sp,
                sp=prototype.stats.sp,
                attack=prototype.stats.attack,
                defense=prototype.stats.defense,
                magic=prototype.stats.magic,
                speed=prototype.stats.speed,
                luck=prototype.stats.luck,
                level=prototype.stats.level,
                exp=prototype.stats.exp,
            )

        # Create new party member
        return PartyMember(
            entity_id=prototype.entity_id,
            name=prototype.name,
            x=prototype.x,
            y=prototype.y,
            sprite_id=prototype.sprite_id,
            stats=new_stats,
            faction=prototype.faction,
            equipment=dict(prototype.equipment),
            base_skills=list(prototype.base_skills),
            skills=list(prototype.skills),
            role=prototype.role,
            portrait_id=prototype.portrait_id,
            skill_tree_progress=SkillTreeProgress(),
            learned_moves=list(getattr(prototype, 'learned_moves', [])),
            formation_position=getattr(prototype, 'formation_position', 'middle'),
        )

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if self.choice_menu:
                if event.key == pygame.K_UP:
                    self.choice_menu.move_selection(-1)
                elif event.key == pygame.K_DOWN:
                    self.choice_menu.move_selection(1)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    idx = self.choice_menu.selected_index
                    self._apply_choice(idx)
            else:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
                    self.manager.pop()

    def update(self, dt: float) -> None:
        """Dialogue scene is mostly static; nothing to update per frame."""
        return

    def draw(self, surface: pygame.Surface) -> None:
        # Draw semi-transparent dark background
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill(Colors.BG_OVERLAY)
        surface.blit(overlay, (0, 0))

        if self.current_node and self.current_node.speaker:
            name_font = self.assets.get_font(Fonts.DEFAULT, Fonts.SIZE_SUBHEADING)
            if name_font:
                # Draw name with shadow
                name_text = self.current_node.speaker
                name_surface = name_font.render(name_text, True, Colors.ACCENT)
                shadow_surface = name_font.render(name_text, True, Colors.BLACK)

                name_x = self.message_box.position[0] + 10
                name_y = self.message_box.position[1] - 24

                surface.blit(shadow_surface, (name_x + 1, name_y + 1))
                surface.blit(name_surface, (name_x, name_y))

        self.message_box.draw(surface, self.assets.get_font(Fonts.DEFAULT, Fonts.SIZE_BODY), panel=self.panel)
        if self.choice_menu:
            self.choice_menu.draw(
                surface,
                self.assets.get_font(Fonts.DEFAULT, Fonts.SIZE_BODY),
                theme={
                    "active": Colors.TEXT_HIGHLIGHT,
                    "inactive": Colors.TEXT_SECONDARY,
                    "disabled": Colors.TEXT_DISABLED
                }
            )

        # Draw help text at bottom
        self._draw_help_text(surface, self.assets.get_font(Fonts.SMALL, Fonts.SIZE_SMALL))

    def _draw_help_text(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        """Draw standardized help text at the bottom of the screen."""
        if not font:
            return

        width, height = surface.get_size()

        if self.choice_menu:
            help_text = "↑/↓: Select Choice  •  Enter/Space: Confirm"
        else:
            help_text = "Enter/Space/ESC: Continue"

        # Draw subtle background for help text
        help_surface = font.render(help_text, True, Colors.TEXT_SECONDARY)
        help_rect = help_surface.get_rect(center=(width // 2, height - Layout.SCREEN_MARGIN))

        bg_rect = help_rect.inflate(Layout.PADDING_MD * 2, Layout.PADDING_SM)
        pygame.draw.rect(surface, Colors.BG_DARK, bg_rect, border_radius=Layout.CORNER_RADIUS_SMALL)

        surface.blit(help_surface, help_rect)

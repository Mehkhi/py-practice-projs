"""Overworld scene for top-down exploration."""

import math
import os
from typing import Any, Dict, List, Optional, Tuple, TYPE_CHECKING

import pygame

from .scene import Scene
from .assets import AssetManager
from .ui import draw_hp_bar, draw_sp_bar, Minimap, TransitionManager, HelpOverlay, TipPopup, HintButton
from .theme import Colors, Layout
from core.logging_utils import log_warning
from .config_loader import load_config
from .world.world_renderer import WorldRenderer
from .world.overworld_controller import OverworldController
from .world.trigger_handler import TriggerHandler
from .world.enemy_spawn_manager import EnemySpawnManager
from .world.world_logic import (
    init_achievement_popups,
    load_dialogue_tree,
    player_has_item,
    show_inline_message,
    show_dialogue_or_message,
    requirements_met,
    encounter_already_cleared,
    battle_available,
    can_use_warp,
    resolve_dialogue_for_npc,
    get_shop_stock,
    open_shop,
    award_quest_rewards,
    show_quest_notification,
    start_dialogue,
    start_battle,
    check_challenge_dungeon_timer,
    is_in_challenge_dungeon_with_restriction,
    update_map_weather,
)
from core.world import World
from core.entities import Player, OverworldEnemy, PartyMember
from core.stats import Stats
from core.encounters import load_encounters_from_json
from core.combat.ai_validation import (
    iter_ai_actions,
    validate_ai_profile_dict,
    warn_missing_profile,
)

if TYPE_CHECKING:
    from .scene import SceneManager
    from .battle_scene import BattleScene
    from .dialogue_scene import DialogueScene
    from core.dialogue import DialogueTree
    from core.entities import NPC, Entity
    from core.items import Item
    from core.quests import QuestManager
    from core.combat import Skill


FORMATION_SEQUENCE = ["front", "middle", "back"]


class WorldScene(Scene):
    """Top-down overworld exploration scene."""

    _iter_ai_actions = staticmethod(iter_ai_actions)
    _validate_ai_profile_dict = staticmethod(validate_ai_profile_dict)
    _warn_missing_profile = staticmethod(warn_missing_profile)
    _init_achievement_popups = init_achievement_popups
    _load_dialogue_tree = load_dialogue_tree
    _player_has_item = player_has_item
    _show_inline_message = show_inline_message
    _show_dialogue_or_message = show_dialogue_or_message
    _requirements_met = requirements_met
    _encounter_already_cleared = encounter_already_cleared
    _battle_available = battle_available
    _can_use_warp = can_use_warp
    _resolve_dialogue_for_npc = resolve_dialogue_for_npc
    _get_shop_stock = get_shop_stock
    _open_shop = open_shop
    _award_quest_rewards = award_quest_rewards
    _show_quest_notification = show_quest_notification
    _start_dialogue = start_dialogue
    _start_battle = start_battle
    _check_challenge_dungeon_timer = check_challenge_dungeon_timer
    _is_in_challenge_dungeon_with_restriction = is_in_challenge_dungeon_with_restriction
    _update_map_weather = update_map_weather

    def _preflight_validate_ai_assets(self) -> None:
        """Scan encounters for bad AI references and missing profiles."""
        if not self.config.get("ai_validation_enabled", True):
            return
        if not self.encounters_data:
            return
        for encounter_id, encounter in self.encounters_data.items():
            if not isinstance(encounter, dict):
                continue
            enemies = encounter.get("enemies", [])
            if not isinstance(enemies, list):
                continue
            for enemy_data in enemies:
                if not isinstance(enemy_data, dict):
                    continue
                ai_profile = enemy_data.get("ai_profile")
                enemy_id = enemy_data.get("id", "enemy")
                WorldScene._validate_ai_profile_dict(
                    ai_profile,
                    self.skills,
                    self.items_db,
                    encounter_id,
                    enemy_id,
                )
                if self.config.get("ai_profile_coverage_check", True):
                    WorldScene._warn_missing_profile(encounter_id, enemy_data)

    def __init__(
        self,
        manager: Optional["SceneManager"],
        world: World,
        player: Player,
        tile_size: int = 32,
        scale: int = 2,
        projection: str = "topdown",
        tileset_name: Optional[str] = None,
        dialogue_tree: Optional["DialogueTree"] = None,
        items_db: Optional[Dict[str, "Item"]] = None,
        save_manager: Optional[Any] = None,
        save_slot: int = 1,
        config: Optional[Dict[str, Any]] = None,
        quest_manager: Optional["QuestManager"] = None,
        encounters_data: Optional[Dict[str, Dict[str, Any]]] = None,
    ):
        super().__init__(manager)
        self.world = world
        self.player = player
        self.save_manager = save_manager
        self.save_slot = max(1, int(save_slot))
        self.tile_size = tile_size
        self.scale = max(1, int(scale))
        self.draw_tile = self.tile_size * self.scale
        self.projection = projection
        # Config is expected to already include env overrides (load_config handles this)
        self.config = config or load_config()
        # If tileset_name not provided, read from config with "default" fallback
        if tileset_name is None:
            tileset_name = self.config.get("tileset", "default")
        self.assets = AssetManager(
            scale=self.scale,
            tileset_name=tileset_name,
            tile_size=tile_size,
            sprite_size=tile_size,  # World scenes use tile_size for entities
        )
        # Warm cache for current tileset resolution to avoid per-frame scaling on first use
        self.assets.warm_cache_for_resolution(tile_size, tile_size)
        self.dialogue_tree = dialogue_tree
        self.items_db = items_db or {}
        if self.dialogue_tree is None:
            self.dialogue_tree = self._load_dialogue_tree()
        self.encounters_data = encounters_data or load_encounters_from_json()

        # Camera offset (top-left of view in pixel space)
        self.camera_offset: Tuple[int, int] = (0, 0)

        # Movement state
        self.move_timer = 0.0
        self.move_delay = 0.15  # Seconds between moves

        # Animation timers
        self.anim_time = 0.0
        self.bob_height = 2 * self.scale

        # Walking animation state
        self.player_facing = "down"  # "up", "down", "left", "right"
        self.is_walking = False
        self.walk_anim_time = 0.0
        self.walk_anim_speed = 8.0  # Frames per second for walk cycle
        self.walk_frame = 0  # Current walk animation frame (0-3)

        # Load skills for combat
        from core.combat import load_skills_from_json
        self.skills = load_skills_from_json()

        # Optional AI validation preflight
        self._preflight_validate_ai_assets()

        # Merchant/shop state
        self.shop_stock: Dict[str, Dict[str, int]] = {}
        self._pending_shop_for: Optional[str] = None
        self._pending_brain_teaser: Optional[str] = None
        self._last_blocked_trigger: Optional[str] = None
        # Load centralized shops database
        from .shop_scene import load_shops_from_json
        self.shops_db = load_shops_from_json()

        # Overworld enemy tracking
        self._pending_enemy_defeat: Optional[OverworldEnemy] = None

        # Quest system
        self.quest_manager = quest_manager

        # Initialize minimap if enabled
        self.minimap_enabled = self.config.get("minimap_enabled", True)
        if self.minimap_enabled:
            self.minimap = Minimap(
                size=self.config.get("minimap_size", 120),
                tile_size=self.config.get("minimap_tile_size", 4),
            )
        else:
            self.minimap = None

        # Screen transitions for map changes
        self.transition = TransitionManager(default_duration=0.4)
        self._pending_warp: Optional[Tuple[str, int, int]] = None
        # Track position we just warped to, to prevent immediate re-warp
        self._warp_cooldown_pos: Optional[Tuple[str, int, int]] = None  # (map_id, x, y)

        # Auto-save settings
        self.auto_save_enabled = self.config.get("auto_save_enabled", True)
        self.auto_save_on_map_change = self.config.get("auto_save_on_map_change", True)
        self._last_auto_save_map: Optional[str] = world.current_map_id

        # Start with fade-in if this is a fresh scene
        self.transition.fade_in(duration=0.3)

        # Initialize weather for starting map
        self._update_map_weather()

        # Initialize achievement popup manager
        self.achievement_popup_manager: Optional[Any] = None
        self._init_achievement_popups()

        # Initialize tutorial UI components
        tutorial_manager = self.get_manager_attr(
            "tutorial_manager", "world_scene_init_tutorial"
        )
        if tutorial_manager:
            self.help_overlay = HelpOverlay(tutorial_manager, theme=None)
            self.tip_popup = TipPopup(theme=None)
            self.hint_button = HintButton(tutorial_manager, theme=None, assets=self.assets)
            self.hint_button.set_context("world")

            # Reposition hint button to bottom-right to avoid overlap with HUD
            # Use Layout constants for consistent spacing, but with extra margin
            # to ensure tooltips don't clip off screen
            btn_w, btn_h = self.hint_button.size
            margin_right = Layout.SCREEN_MARGIN * 2
            margin_bottom = Layout.SCREEN_MARGIN
            self.hint_button.position = (
                Layout.SCREEN_WIDTH - btn_w - margin_right,
                Layout.SCREEN_HEIGHT - btn_h - margin_bottom
            )
        else:
            self.help_overlay = None
            self.tip_popup = None
            self.hint_button = None

        # Party overlay UI state
        self.party_overlay_visible = False
        self.party_overlay_selection = 0
        self.party_overlay_message: Optional[str] = None
        self.party_overlay_message_timer = 0.0

        # Initialize puzzle system
        from core.data_loader import load_puzzles_from_json
        from core.puzzles import PuzzleManager
        puzzles_data = load_puzzles_from_json()
        self.puzzle_manager = PuzzleManager(puzzles_data)

        # Initialize modular components
        self.renderer = WorldRenderer(self)
        self._get_current_entities = self.renderer.get_current_entities
        self._find_npc_by_id = self.renderer.find_npc_by_id
        self._find_nearby_npc = self.renderer.find_nearby_npc
        self._project = self.renderer.project
        self.controller = OverworldController(self)
        self.trigger_handler = TriggerHandler(self)
        self.enemy_manager = EnemySpawnManager(self)

        # Preload current map sprites
        self.renderer.preload_map_sprites()

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle input events."""
        if self.party_overlay_visible:
            if self._handle_party_overlay_event(event):
                return

        if event.type == pygame.KEYDOWN and event.key == pygame.K_f:
            self._toggle_party_overlay()
            return

        # Help overlay takes priority when visible
        if self.help_overlay and self.help_overlay.visible:
            if self.help_overlay.handle_event(event):
                return

        # Tip popup
        if self.tip_popup and self.tip_popup.visible:
            consumed, permanent = self.tip_popup.handle_event(event)
            if permanent and self.tip_popup.current_tip:
                tutorial_manager = self.get_manager_attr(
                    "tutorial_manager", "handle_event_tip_popup"
                )
                if tutorial_manager:
                    tutorial_manager.dismiss_tip(self.tip_popup.current_tip.tip_id, permanently=True)
            if consumed:
                return

        # H key toggles help
        if event.type == pygame.KEYDOWN and event.key == pygame.K_h:
            if self.help_overlay:
                self.help_overlay.toggle()
            return

        # Hint button click
        if self.hint_button and self.hint_button.handle_event(event):
            if self.help_overlay:
                self.help_overlay.toggle()
            return

        # Pass other events to controller
        self.controller.handle_event(event)

    def update(self, dt: float) -> None:
        """Update scene state."""
        if self.party_overlay_message and self.party_overlay_message_timer > 0:
            self.party_overlay_message_timer = max(0.0, self.party_overlay_message_timer - dt)
            if self.party_overlay_message_timer <= 0:
                self.party_overlay_message = None

        # Update screen transitions
        self.transition.update(dt)

        # Update achievement popups (always update, even during transitions)
        if self.achievement_popup_manager:
            self.achievement_popup_manager.update(dt)

        # Don't process input during transitions
        if self.transition.is_active():
            return

        # Check for party recruitment
        self._check_party_recruitment()

        # Check if we just returned from a battle and need to mark enemy as defeated
        if self._pending_enemy_defeat and self.manager and self.manager.current() is self:
            # Check if the encounter was cleared (victory)
            if self._encounter_already_cleared(self._pending_enemy_defeat.encounter_id):
                self._pending_enemy_defeat.defeated = True
            self._pending_enemy_defeat = None

        if self._pending_shop_for and self.manager and self.manager.current() is self:
            npc = self._find_npc_by_id(self._pending_shop_for)
            self._pending_shop_for = None
            if npc:
                self._open_shop(npc)

        if self._pending_brain_teaser and self.manager and self.manager.current() is self:
            teaser_id = self._pending_brain_teaser
            self._pending_brain_teaser = None
            self.trigger_handler._open_brain_teaser(teaser_id)

        if self.party_overlay_visible:
            return

        # Delegate movement and input handling to controller
        self.controller.update_movement(dt)

        # Check for puzzle step triggers (pressure plates) after movement
        if self.puzzle_manager:
            self.puzzle_manager._check_step_triggers(
                self.world.current_map_id,
                self.player.x,
                self.player.y,
                is_block=False,
                world=self.world
            )
            puzzle = self.puzzle_manager.get_puzzle_for_map(self.world.current_map_id)
            if puzzle and hasattr(self, 'trigger_handler'):
                self.trigger_handler._trigger_first_puzzle_tip()
                self.trigger_handler._trigger_puzzle_solved_tip(puzzle)

        # Update overworld enemies and check for detection
        self.enemy_manager.update(dt)

        # Update camera to follow player
        self.controller._update_camera()

        # Check for triggers
        self.trigger_handler.check_triggers()

        # Check time limit for challenge dungeon floors
        self._check_challenge_dungeon_timer(dt)

        # Check for pending tips and update tutorial UI
        if self.tip_popup and not self.tip_popup.visible:
            tutorial_manager = self.get_manager_attr(
                "tutorial_manager", "update_pending_tips"
            )
            if tutorial_manager:
                pending = tutorial_manager.get_pending_tip()
                if pending:
                    self.tip_popup.show_tip(pending, position="top")
                    tutorial_manager.dismiss_tip(pending.tip_id)

        # Update tutorial UI components
        if self.tip_popup:
            self.tip_popup.update(dt)
        if self.help_overlay:
            self.help_overlay.update(dt)
        if self.hint_button:
            self.hint_button.update(dt)

    def _check_party_recruitment(self) -> None:
        """Check world flags for recruited NPCs and add them to the party."""
        prototypes = self.get_manager_attr("party_prototypes", "_check_party_recruitment")
        if not prototypes:
            return

        for member_id, data in prototypes.items():
            recruited_flag = f"{member_id}_recruited"
            joined_flag = f"{member_id}_joined"

            # If recruited flag is set but they haven't joined yet
            if not (self.world.get_flag(recruited_flag) and not self.world.get_flag(joined_flag)):
                continue

            try:
                # Resolve prototype fields (PartyMember instance or legacy dict)
                if isinstance(data, PartyMember):
                    proto = data
                    proto_entity_id = proto.entity_id or member_id
                    name = proto.name or member_id.capitalize()
                    sprite_id = proto.sprite_id or "player"

                    # Clone stats so each recruited member has independent HP, etc.
                    if proto.stats:
                        stats = Stats(
                            max_hp=proto.stats.max_hp,
                            hp=proto.stats.hp,
                            max_sp=proto.stats.max_sp,
                            sp=proto.stats.sp,
                            attack=proto.stats.attack,
                            defense=proto.stats.defense,
                            magic=proto.stats.magic,
                            speed=proto.stats.speed,
                            luck=proto.stats.luck,
                        )
                    else:
                        stats = Stats(100, 100, 50, 50, 10, 10, 10, 10, 5)

                    base_skills = list(getattr(proto, "base_skills", []) or [])
                    role = getattr(proto, "role", "fighter") or "fighter"
                    portrait_id = getattr(proto, "portrait_id", None)
                    formation_position = getattr(proto, "formation_position", "middle") or "middle"
                    equipment_source = dict(getattr(proto, "equipment", {}) or {})
                else:
                    # Fallback: data is a raw dict (older save or alternate loader)
                    stats_data = data.get("stats", {})
                    stats = Stats(
                        max_hp=stats_data.get("max_hp", 100),
                        hp=stats_data.get("hp", 100),
                        max_sp=stats_data.get("max_sp", 50),
                        sp=stats_data.get("sp", 50),
                        attack=stats_data.get("attack", 10),
                        defense=stats_data.get("defense", 10),
                        magic=stats_data.get("magic", 10),
                        speed=stats_data.get("speed", 10),
                        luck=stats_data.get("luck", 5),
                    )
                    proto_entity_id = data.get("entity_id", member_id)
                    name = data.get("name", member_id.capitalize())
                    sprite_id = data.get("sprite_id", "player")
                    base_skills = list(data.get("base_skills", []) or [])
                    role = data.get("role", "fighter") or "fighter"
                    portrait_id = data.get("portrait_id")
                    formation_position = data.get("formation_position", "middle") or "middle"
                    equipment_source = dict(data.get("equipment", {}) or {})

                # Prevent duplicate addition (double safety) based on entity_id
                if any(m.entity_id == proto_entity_id for m in self.player.party):
                    self.world.set_flag(joined_flag, True)
                    continue

                # Create a fresh PartyMember instance for the recruited ally
                member = PartyMember(
                    entity_id=proto_entity_id,
                    name=name,
                    sprite_id=sprite_id,
                    x=0,
                    y=0,
                    stats=stats,
                    base_skills=base_skills,
                    role=role,
                    portrait_id=portrait_id,
                    formation_position=formation_position,
                )

                # Add to party
                if self.player.add_party_member(member):
                    self.world.set_flag(joined_flag, True)
                    self._show_inline_message(f"{member.name} joined the party!")

                    # Sync authoritative formation mapping on the player
                    self.player.party_formation[member.entity_id] = formation_position

                    achievement_manager = self.get_manager_attr(
                        "achievement_manager", "_check_party_recruitment"
                    )
                    if achievement_manager:
                        try:
                            achievement_manager.on_party_member_recruited(member.entity_id)
                        except Exception as exc:
                            log_warning(
                                f"Failed to trigger party_member_recruited for {member.entity_id}: {exc}"
                            )

                    # Equip default items if specified
                    if equipment_source and self.items_db:
                        for slot, item_id in equipment_source.items():
                            if item_id in self.items_db:
                                member.equip(self.items_db[item_id], slot)
                        member.recompute_equipment(self.items_db)

            except Exception as e:
                print(f"Failed to recruit party member {member_id}: {e}")

    def _party_overlay_members(self) -> List["Entity"]:
        members: List["Entity"] = [self.player]
        members.extend([ally for ally in getattr(self.player, "party", []) if ally])
        return members

    def _toggle_party_overlay(self, force_state: Optional[bool] = None) -> None:
        desired_state = (not self.party_overlay_visible) if force_state is None else bool(force_state)
        if desired_state == self.party_overlay_visible:
            return
        self.party_overlay_visible = desired_state
        if desired_state:
            members = self._party_overlay_members()
            if members:
                self.party_overlay_selection = min(self.party_overlay_selection, len(members) - 1)
            else:
                self.party_overlay_selection = 0
            self._party_overlay_show_message("Use Arrows to adjust formations.")
        else:
            self.party_overlay_message = None

    def _handle_party_overlay_event(self, event: pygame.event.Event) -> bool:
        if event.type != pygame.KEYDOWN:
            return True
        if event.key in (pygame.K_ESCAPE, pygame.K_f):
            self._toggle_party_overlay(False)
            return True
        if event.key == pygame.K_UP:
            self._move_party_overlay_selection(-1)
            return True
        if event.key == pygame.K_DOWN:
            self._move_party_overlay_selection(1)
            return True
        if event.key == pygame.K_LEFT:
            self._adjust_party_overlay_position(-1)
            return True
        if event.key == pygame.K_RIGHT:
            self._adjust_party_overlay_position(1)
            return True
        return True

    def _move_party_overlay_selection(self, delta: int) -> None:
        members = self._party_overlay_members()
        if not members:
            self.party_overlay_selection = 0
            return
        self.party_overlay_selection = (self.party_overlay_selection + delta) % len(members)

    def _adjust_party_overlay_position(self, direction: int) -> None:
        members = self._party_overlay_members()
        if not members:
            return
        index = self.party_overlay_selection % len(members)
        member = members[index]
        current_position = (
            getattr(self.player, "formation_position", FORMATION_SEQUENCE[0])
            if index == 0
            else self.player.get_member_formation(member.entity_id)
        )
        if current_position not in FORMATION_SEQUENCE:
            current_position = FORMATION_SEQUENCE[0]
        new_index = (FORMATION_SEQUENCE.index(current_position) + direction) % len(FORMATION_SEQUENCE)
        new_position = FORMATION_SEQUENCE[new_index]
        if index == 0:
            self.player.formation_position = new_position
            self._party_overlay_show_message(f"Leader moves to {new_position.capitalize()}.")
        else:
            if self.player.set_member_formation(member.entity_id, new_position):
                self._party_overlay_show_message(
                    f"{member.name} moves to {new_position.capitalize()}."
                )
            else:
                self._party_overlay_show_message(f"Can't move {member.name} there.")

    def _draw_party_overlay(self, surface: pygame.Surface) -> None:
        width, height = surface.get_size()
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        margin = Layout.SCREEN_MARGIN
        panel_rect = pygame.Rect(
            margin,
            margin,
            width - margin * 2,
            height - margin * 2,
        )
        pygame.draw.rect(surface, Colors.BG_PANEL, panel_rect)
        pygame.draw.rect(surface, Colors.BORDER, panel_rect, 2)

        title_font = self.assets.get_font("large", 28) or self.assets.get_font("default")
        font = self.assets.get_font("default")
        small_font = self.assets.get_font("small") or font

        if title_font:
            title_text = title_font.render("Party Formation", True, Colors.TEXT_PRIMARY)
            surface.blit(title_text, (panel_rect.centerx - title_text.get_width() // 2, panel_rect.top + 20))

        members = self._party_overlay_members()
        row_height = 60
        row_y = panel_rect.top + 80
        row_x = panel_rect.left + 40
        row_width = panel_rect.width - 80

        for idx, member in enumerate(members):
            card_rect = pygame.Rect(row_x, row_y + idx * (row_height + 10), row_width, row_height)
            pygame.draw.rect(
                surface,
                Colors.BG_DARK if idx != self.party_overlay_selection else Colors.BG_PANEL,
                card_rect,
            )
            pygame.draw.rect(
                surface,
                Colors.ACCENT if idx == self.party_overlay_selection else Colors.BORDER,
                card_rect,
                2,
            )

            if font:
                role_label = "Leader" if idx == 0 else getattr(member, "role", "Ally").title()
                formation = (
                    getattr(self.player, "formation_position", "front")
                    if idx == 0
                    else self.player.get_member_formation(member.entity_id)
                )
                name_text = font.render(
                    f"{member.name} - {role_label}",
                    True,
                    Colors.TEXT_PRIMARY,
                )
                surface.blit(name_text, (card_rect.x + 16, card_rect.y + 8))

                formation_text = small_font.render(
                    f"Position: {formation.capitalize()}",
                    True,
                    Colors.TEXT_SECONDARY,
                )
                surface.blit(formation_text, (card_rect.x + 16, card_rect.y + 30))

        instructions = "F/Esc: Close  |  Up/Down: Select  |  Left/Right: Cycle"
        if small_font:
            help_text = small_font.render(instructions, True, Colors.TEXT_SECONDARY)
            surface.blit(
                help_text,
                (
                    panel_rect.centerx - help_text.get_width() // 2,
                    panel_rect.bottom - 40,
                ),
            )

        if self.party_overlay_message and small_font:
            msg_text = small_font.render(self.party_overlay_message, True, Colors.TEXT_PRIMARY)
            surface.blit(
                msg_text,
                (
                    panel_rect.centerx - msg_text.get_width() // 2,
                    panel_rect.bottom - 70,
                ),
            )

    def _party_overlay_show_message(self, text: str) -> None:
        self.party_overlay_message = text
        self.party_overlay_message_timer = 2.0


    def _interact(self) -> None:
        """Handle interaction on the current tile or adjacent NPC."""
        self.trigger_handler.interact()

    def _preload_map_sprites(self) -> None:
        """Preload sprites for the active map after a warp."""
        if self.renderer:
            self.renderer.preload_map_sprites()

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the overworld."""
        self.renderer.draw(surface)

        # Draw tutorial UI last (on top)
        if self.hint_button:
            self.hint_button.draw(surface)
        if self.tip_popup:
            self.tip_popup.draw(surface)
        if self.help_overlay:
            self.help_overlay.draw(surface)  # Overlay on very top

        if self.party_overlay_visible:
            self._draw_party_overlay(surface)

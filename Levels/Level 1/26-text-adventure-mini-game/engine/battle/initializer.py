"""Battle initialization helpers for `BattleScene`.

This module pulls a large amount of setup logic out of `BattleScene.__init__`
to keep the scene class focused on high-level orchestration.
"""

from __future__ import annotations

from typing import Dict, Any, Optional, TYPE_CHECKING

import os

from core.data_loader import load_json_file
from core.logging_utils import log_warning
from core.tutorial_system import TipTrigger

from ..assets import AssetManager
from ..ui import Menu, MessageBox, CombatLog, NineSlicePanel
from ..theme import Colors

if TYPE_CHECKING:
    from . import BattleStateManager
    from .scene import SceneManager
    from .battle_scene import BattleScene  # type: ignore  # circular at runtime


class BattleInitializer:
    """Helper responsible for initializing a `BattleScene` instance.

    The public entry-point is `initialize(scene)`, which assumes the scene has
    basic dependencies already assigned (manager, battle_system, world,
    player, rewards, etc.) and fills in all remaining runtime fields.
    """

    def __init__(self) -> None:
        # Stateless helper; no configuration for now.
        pass

    def initialize(self, scene: "BattleScene") -> None:
        """Populate all runtime fields on `scene`.

        This mirrors the original `BattleScene.__init__` body so that behavior
        remains identical, but the code lives in a dedicated helper.
        """
        # Sizing and asset setup
        scene._init_battle_sizing()

        if not getattr(scene, "assets", None):
            scene.assets = AssetManager(
                scale=scene.scale,
                tile_size=32,  # Not used in battle, but needed for preload
                sprite_size=scene.sprite_size,
            )

        # Basic containers / flags
        scene.rewards = scene.rewards if scene.rewards is not None else scene._default_rewards()
        if scene.items_db is None:
            scene.items_db = {}

        scene.battle_context: Dict[str, Any] = {}

        # UI components - positioned relative to screen dimensions
        scene.main_menu = Menu(
            ["Attack", "Skill", "Item", "Guard", "Talk", "Memory", "Auto", "Flee"],
            position=scene._get_main_menu_position(),
            compact=True,
        )
        scene.skill_menu = None
        scene.item_menu = None
        scene.move_menu = None
        scene.memory_menu = None
        scene.memory_stat_menu = None

        scene.message_box = MessageBox(
            position=scene._get_message_box_position(),
            width=490,
            height=90,
        )

        scene.combat_log = CombatLog(
            position=scene._get_message_box_position(),
            width=490,
            collapsed_height=90,
            expanded_height=280,
        )

        # Moves database and mappings
        scene.moves_db = scene.moves_db if getattr(scene, "moves_db", None) else scene._get_moves_db()
        scene.move_menu_mapping = {}
        scene.pending_move_id = None

        # Animation state
        scene.current_animation = None
        scene.animation_timer = 0.0
        scene.animation_target_pos = None

        # Enhanced animation effects
        scene.screen_shake = 0.0
        scene.screen_shake_offset = (0, 0)
        scene.shake_offset = (0, 0)
        scene.shake_timer = 0.0
        scene.shake_intensity = 0.0
        scene.flash_timer = 0.0
        scene.flash_color = Colors.WHITE
        scene.damage_numbers = []

        # Background cache
        scene._bg_surface = None
        scene.combo_flash = 0.0
        scene.coordinated_tactic_flash = 0.0
        scene.phase_transition_flash = 0.0
        scene.show_ai_debug = False
        scene.last_adaptation_level = 0
        scene.ai_pattern_notification = None
        scene.ai_notification_timer = 0.0

        # Battle state
        scene.menu_mode = "main"
        scene.waiting_for_target = False
        scene.target_type = None
        scene.target_index = 0
        scene.pending_skill_id = None
        scene.pending_item_id = None
        scene.target_side = None
        scene.active_player_index = 0
        scene._player_phase_initialized = False

        scene.status_icon_map = self._load_status_icon_map()
        scene.item_menu_mapping = {}
        scene._pending_memory_op = None
        scene._rewards_applied = False
        scene._outcome_finalized = False
        scene._victory_spared = False
        scene._pending_move_learns = []
        scene._status_effect_triggered = False
        scene._low_hp_tip_triggered = False
        scene._low_sp_tip_triggered = False
        scene._defeat_tip_triggered = False
        if getattr(scene, "rewards_handler", None):
            scene._pending_move_learns = scene.rewards_handler._pending_move_learns

        # Auto-battle speed control
        scene.auto_battle = False
        scene.battle_speed = 1
        scene._speed_options = [1, 2, 4]

        # Cached surfaces
        scene._default_backdrop_surface = None

        # Panel / visual UI chrome
        self._load_panel(scene)

        # Set initial message/log
        if scene.battle_context.get("stat_scrambled"):
            scene.battle_system.message_log.append(
                "Reality warps! Enemy Attack and Magic stats have been swapped!"
            )
        scene.message_box.set_text("Battle begins!")
        scene.combat_log.add_message("Battle begins!")

        # Preload sprites and record bestiary data
        self._preload_battle_sprites(scene)
        self._record_enemy_encounters(scene)

        # Trigger FIRST_BATTLE tutorial tip
        tutorial_manager = scene.get_manager_attr("tutorial_manager", "battle_init")
        if tutorial_manager:
            tutorial_manager.trigger_tip(TipTrigger.FIRST_BATTLE)

    # --- Helpers mirrored from original `BattleScene` private methods ---

    def _load_panel(self, scene: "BattleScene") -> None:
        """Try to build a reusable 9-slice panel from UI sprite."""
        try:
            panel_surface = scene.assets.get_image("ui_panel")
            scene.panel = NineSlicePanel(panel_surface)
        except Exception:
            scene.panel = None

    def _load_status_icon_map(self) -> Dict[str, str]:
        """Load mapping of status effect IDs to sprite IDs."""
        path = os.path.join("data", "status_icons.json")
        return load_json_file(path, default={}, context="Loading status icon map")

    def _preload_battle_sprites(self, scene: "BattleScene") -> None:
        """Preload battle-specific sprites to prevent stuttering during combat."""
        battle_sprites: list[str] = []

        # Enemies
        for enemy in scene.battle_system.enemies:
            if enemy.entity and hasattr(enemy.entity, "sprite_id"):
                sprite_id = enemy.entity.sprite_id
                if sprite_id and sprite_id not in battle_sprites:
                    battle_sprites.append(sprite_id)

        # Player / party
        for ally in scene.battle_system.players:
            if ally.entity and hasattr(ally.entity, "sprite_id"):
                sprite_id = ally.entity.sprite_id
                if sprite_id and sprite_id not in battle_sprites:
                    battle_sprites.append(sprite_id)

        # Backdrop
        backdrop_id = scene._get_backdrop_id()
        if backdrop_id and backdrop_id not in battle_sprites:
            battle_sprites.append(backdrop_id)

        # Preload sprites at battle sprite size
        for sprite_id in battle_sprites:
            try:
                scene.assets.get_image(sprite_id, (scene.sprite_size, scene.sprite_size))
            except Exception as exc:
                log_warning(f"Failed to preload battle sprite {sprite_id}: {exc}")

        if backdrop_id:
            try:
                scene.assets.get_image(backdrop_id)
            except Exception as exc:
                log_warning(f"Failed to preload backdrop {backdrop_id}: {exc}")

    def _record_enemy_encounters(self, scene: "BattleScene") -> None:
        """Record all enemies in this battle to the player's bestiary."""
        player = scene.player
        if not hasattr(player, "bestiary") or not player.bestiary:
            return

        location = scene.world.current_map_id if scene.world else None

        for enemy_participant in scene.battle_system.enemies:
            enemy = enemy_participant.entity
            enemy_type = getattr(enemy, "enemy_type", enemy.entity_id)

            base_stats: Dict[str, Any] = {}
            if enemy_participant.stats:
                base_stats = {
                    "max_hp": enemy_participant.stats.max_hp,
                    "max_sp": enemy_participant.stats.max_sp,
                    "attack": enemy_participant.stats.attack,
                    "defense": enemy_participant.stats.defense,
                    "magic": enemy_participant.stats.magic,
                    "speed": enemy_participant.stats.speed,
                }

            weaknesses = (
                getattr(enemy_participant.stats, "weaknesses", [])
                if enemy_participant.stats
                else []
            )
            resistances = (
                getattr(enemy_participant.stats, "resistances", [])
                if enemy_participant.stats
                else []
            )
            immunities = (
                getattr(enemy_participant.stats, "immunities", [])
                if enemy_participant.stats
                else []
            )
            absorbs = (
                getattr(enemy_participant.stats, "absorbs", [])
                if enemy_participant.stats
                else []
            )

            player.bestiary.record_encounter(
                enemy_type=enemy_type,
                name=enemy.name,
                sprite_id=getattr(enemy, "sprite_id", "enemy"),
                category=enemy_type,
                location=location,
                base_stats=base_stats,
                weaknesses=list(weaknesses),
                resistances=list(resistances),
                immunities=list(immunities),
                absorbs=list(absorbs),
            )

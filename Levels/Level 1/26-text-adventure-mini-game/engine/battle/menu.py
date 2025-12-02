"""Battle menu handling logic.

This module contains menu input handling and state machine logic for battle scenes,
including main menu, skill/item/move/memory submenus, and target selection.
"""

from typing import Optional, Dict, List, Callable

import pygame

from .targeting import BattleTargetingMixin


class BattleMenuMixin(BattleTargetingMixin):
    """Mixin providing menu handling logic for BattleScene.

    This mixin handles:
    - Main menu input and selection
    - Skill/Item/Move/Memory submenu handling
    - Target selection mode
    - Party member turn management
    - Action queuing

    Attributes expected from host class:
        battle_system: BattleSystem instance
        player: Player entity
        main_menu, skill_menu, item_menu, etc.: Menu instances
        message_box: MessageBox for battle messages
        menu_mode: Current menu state string
        waiting_for_target: Target selection flag
        items_db: Item database
        moves_db: Moves database
    """

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle input events for battle menus."""
        from core.combat import BattleState

        if event.type != pygame.KEYDOWN:
            return

        # Handle combat log toggle/scroll (TAB key, always available)
        if hasattr(self, 'combat_log') and self.combat_log:
            if self.combat_log.handle_event(event):
                return  # Event consumed by combat log

        if self.waiting_for_target:
            self._handle_target_input(event)
        elif self.menu_mode == "main":
            self._handle_main_menu_input(event)
        elif self.menu_mode == "skill":
            self._handle_skill_menu_input(event)
        elif self.menu_mode == "item":
            self._handle_item_menu_input(event)
        elif self.menu_mode == "move":
            self._handle_move_menu_input(event)
        elif self.menu_mode == "memory":
            self._handle_memory_menu_input(event)
        elif self.menu_mode == "memory_stat":
            self._handle_memory_stat_menu_input(event)

        # Handle battle end states
        if self.battle_system.state in [BattleState.VICTORY, BattleState.ESCAPED, BattleState.DEFEAT]:
            if event.key == pygame.K_RETURN:
                self._handle_battle_end_input()

    def _handle_main_menu_input(self, event: pygame.event.Event) -> None:
        """Handle input for main battle menu."""
        # Check for hotbar shortcuts (1-9)
        if event.key >= pygame.K_1 and event.key <= pygame.K_9:
            slot = event.key - pygame.K_0
            self._use_hotbar_item(slot)
        elif event.key == pygame.K_l:
            # Toggle AI debug overlay
            self.show_ai_debug = not self.show_ai_debug
        elif event.key == pygame.K_a:
            # Toggle continuous auto-battle mode
            self._toggle_auto_battle()
        elif event.key in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS):
            # Increase battle speed (only during auto-battle)
            self._cycle_battle_speed(1)
        elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
            # Decrease battle speed (only during auto-battle)
            self._cycle_battle_speed(-1)
        elif event.key == pygame.K_UP:
            self.main_menu.move_selection(-1)
        elif event.key == pygame.K_DOWN:
            self.main_menu.move_selection(1)
        elif event.key == pygame.K_RETURN:
            self._handle_main_menu_selection()

    def _handle_submenu_input(
        self,
        event: pygame.event.Event,
        menu: Optional[object],
        on_select: Callable[[], None],
        on_cancel: Callable[[], None]
    ) -> None:
        """Generic handler for submenu input.

        Args:
            event: The pygame key event.
            menu: The menu object (must have move_selection method).
            on_select: Callback invoked when RETURN is pressed.
            on_cancel: Callback invoked when ESCAPE is pressed.
        """
        if not menu:
            return
        if event.key == pygame.K_UP:
            menu.move_selection(-1)
        elif event.key == pygame.K_DOWN:
            menu.move_selection(1)
        elif event.key == pygame.K_RETURN:
            on_select()
        elif event.key == pygame.K_ESCAPE:
            on_cancel()

    def _handle_skill_menu_input(self, event: pygame.event.Event) -> None:
        """Handle input for skill submenu."""
        def on_cancel() -> None:
            self.menu_mode = "main"
            self.skill_menu = None
        self._handle_submenu_input(event, self.skill_menu, self._handle_skill_selection, on_cancel)

    def _handle_item_menu_input(self, event: pygame.event.Event) -> None:
        """Handle input for item submenu."""
        def on_cancel() -> None:
            self.menu_mode = "main"
            self.item_menu = None
        self._handle_submenu_input(event, self.item_menu, self._handle_item_selection, on_cancel)

    def _handle_move_menu_input(self, event: pygame.event.Event) -> None:
        """Handle input for move submenu."""
        def on_cancel() -> None:
            self.menu_mode = "main"
            self.move_menu = None
            self.pending_move_id = None
        self._handle_submenu_input(event, self.move_menu, self._handle_move_selection, on_cancel)

    def _handle_memory_menu_input(self, event: pygame.event.Event) -> None:
        """Handle input for memory submenu."""
        def on_cancel() -> None:
            self.menu_mode = "main"
            self.memory_menu = None
        self._handle_submenu_input(event, self.memory_menu, self._handle_memory_selection, on_cancel)

    def _handle_memory_stat_menu_input(self, event: pygame.event.Event) -> None:
        """Handle input for memory stat submenu."""
        def on_cancel() -> None:
            self.menu_mode = "main"
            self.memory_stat_menu = None
            self._pending_memory_op = None
        self._handle_submenu_input(event, self.memory_stat_menu, self._handle_memory_stat_selection, on_cancel)

    def _handle_battle_end_input(self) -> None:
        """Handle input when battle has ended."""
        from core.combat import BattleState

        # Skip final boss - it transitions immediately in _handle_victory()
        if self.encounter_id == "final_boss" and self.battle_system.state == BattleState.VICTORY:
            return  # Already handled by immediate transition
        elif self.battle_system.state == BattleState.DEFEAT:
            # On defeat, return to title screen where player can continue from last save
            self._return_to_title_screen()
        else:
            # Check for pending move learns before exiting
            pending_move_learns = []
            if hasattr(self, "rewards_handler") and self.rewards_handler:
                pending_move_learns = getattr(self.rewards_handler, "_pending_move_learns", [])
            elif hasattr(self, "_pending_move_learns"):
                pending_move_learns = self._pending_move_learns

            if pending_move_learns:
                self._trigger_next_move_learn()
            else:
                self.manager.pop()

    def _handle_main_menu_selection(self) -> None:
        """Handle selection from main menu."""
        actor = self._current_actor()
        if not actor:
            self.message_box.set_text("No active ally to act.")
            return
        selection = self.main_menu.get_selected()
        if not selection:
            return

        if selection == "Attack":
            self._queue_attack()
        elif selection == "Skill":
            self._show_skill_menu()
        elif selection == "Item":
            self._show_item_menu()
        elif selection == "Guard":
            self._queue_guard()
        elif selection == "Talk":
            self._queue_talk()
        elif selection == "Memory":
            self._show_memory_menu()
        elif selection == "Auto":
            self._queue_auto_action()
        elif selection == "Flee":
            self._queue_flee()

    def _queue_attack(self) -> None:
        """Show move selection menu when Attack is selected."""
        from ..ui import Menu

        actor = self._current_actor()
        if not actor:
            self.message_box.set_text("No active ally to act.")
            return
        alive_enemies = self._alive_enemies()
        if not alive_enemies:
            self.message_box.set_text("No enemies to attack!")
            return

        # Get the entity's learned moves
        entity = actor.entity
        learned_moves = getattr(entity, "learned_moves", [])

        if not learned_moves:
            # No moves learned - use basic attack (fallback)
            self.pending_skill_id = None
            self.pending_item_id = None
            self.pending_move_id = None
            self._begin_target_selection("single_enemy")
            self.message_box.set_text("Choose a target.")
            return

        # Build move menu
        move_names = []
        self.move_menu_mapping.clear()
        for idx, move_id in enumerate(learned_moves):
            move = self.moves_db.get_move(move_id)
            if move:
                move_names.append(f"{move.name} (Pwr:{move.power})")
                self.move_menu_mapping[idx] = move_id
            else:
                move_names.append(move_id)
                self.move_menu_mapping[idx] = move_id

        self.move_menu = Menu(move_names, position=self._get_submenu_position(), compact=True)
        self.menu_mode = "move"
        self.message_box.set_text("Choose a move.")

    def _handle_move_selection(self) -> None:
        """Handle move selection from the move menu."""
        if not self.move_menu:
            return

        actor = self._current_actor()
        if not actor:
            self.message_box.set_text("No active ally to act.")
            self.menu_mode = "main"
            self.move_menu = None
            return

        selected_idx = self.move_menu.selected_index
        move_id = self.move_menu_mapping.get(selected_idx)
        if not move_id:
            return

        self.pending_move_id = move_id
        self.pending_skill_id = None
        self.pending_item_id = None
        self.move_menu = None

        move = self.moves_db.get_move(move_id)
        move_name = move.name if move else move_id
        self._begin_target_selection("single_enemy", message=f"Use {move_name} on which enemy?")

    def _show_skill_menu(self) -> None:
        """Show skill selection menu."""
        from ..ui import Menu

        actor = self._current_actor()
        if not actor or not actor.stats:
            self.message_box.set_text("No one can act right now.")
            return

        available_skills = []
        known_skills = getattr(actor.entity, "skills", None)
        for skill_id, skill in self.battle_system.skills.items():
            if known_skills is not None and skill_id not in known_skills:
                continue
            if actor.stats.sp >= skill.cost_sp:
                available_skills.append(skill.name)

        if not available_skills:
            self.message_box.set_text("No skills available!")
            return

        self.skill_menu = Menu(available_skills, position=self._get_submenu_position(), compact=True)
        self.menu_mode = "skill"

    def _handle_skill_selection(self) -> None:
        """Handle skill selection."""
        from core.combat import BattleCommand, ActionType

        if not self.skill_menu:
            return

        actor = self._current_actor()
        if not actor:
            self.message_box.set_text("No active ally to act.")
            self.skill_menu = None
            self.menu_mode = "main"
            return

        skill_name = self.skill_menu.get_selected()
        if not skill_name:
            return

        skill_id = None
        for sid, skill in self.battle_system.skills.items():
            if skill.name == skill_name:
                skill_id = sid
                break

        if not skill_id:
            return

        skill = self.battle_system.skills.get(skill_id)
        if not skill:
            return
        if actor.stats and actor.stats.sp < skill.cost_sp:
            self.message_box.set_text("Not enough SP!")
            self.menu_mode = "main"
            self.skill_menu = None
            return
        self.pending_item_id = None

        if skill.target_pattern in ("self", "all_enemies"):
            target_ids: list[str] = []
            if skill.target_pattern == "self":
                target_ids = [actor.entity.entity_id]
            cmd = BattleCommand(
                actor_id=actor.entity.entity_id,
                action_type=ActionType.SKILL,
                skill_id=skill_id,
                target_ids=target_ids
            )
            self.battle_system.queue_player_command(cmd)
            self.message_box.set_text(f"{actor.entity.name} uses {skill_name}!")
            self.menu_mode = "main"
            self.skill_menu = None
            self._advance_actor_after_command()
        elif skill.target_pattern in ("single_enemy", "single_ally"):
            self.pending_skill_id = skill_id
            self._begin_target_selection(skill.target_pattern, message=f"Choose a target for {skill.name}.")
            self.skill_menu = None
        else:
            self.message_box.set_text("No valid target for that skill.")

    def _show_item_menu(self) -> None:
        """Show item selection menu."""
        from ..ui import Menu

        actor = self._current_actor()
        if not actor:
            self.message_box.set_text("No active ally to act.")
            return
        if not self.player.inventory:
            self.message_box.set_text("No items available!")
            return

        items = self.player.inventory.get_all_items()
        if not items:
            self.message_box.set_text("Inventory is empty!")
            return

        options = []
        self.item_menu_mapping.clear()
        idx = 0
        for item_id, qty in items.items():
            item_def = self.items_db.get(item_id)
            if not item_def:
                continue
            if item_def.item_type != "consumable":
                continue
            item_name = item_def.name if item_def else item_id
            options.append(f"{item_name} x{qty}")
            self.item_menu_mapping[idx] = item_id
            idx += 1

        if not options:
            self.message_box.set_text("No usable items available!")
            return

        self.item_menu = Menu(options, position=self._get_submenu_position(), compact=True)
        self.menu_mode = "item"

    def _use_hotbar_item(self, slot: int) -> None:
        """Use an item from the hotbar slot (1-9)."""
        from core.combat import BattleCommand, ActionType

        if not self.player.inventory:
            self.message_box.set_text("No inventory available!")
            return

        item_id = self.player.inventory.get_hotbar_item(slot)
        if not item_id:
            self.message_box.set_text(f"Hotbar slot {slot} is empty!")
            return

        # Check if item exists and is consumable
        item = self.items_db.get(item_id)
        if not item:
            self.message_box.set_text(f"Item not found in database!")
            return

        if item.item_type != "consumable":
            self.message_box.set_text(f"{item.name} is not a consumable item!")
            return

        # Check if player has the item
        if not self.player.inventory.has(item_id, 1):
            self.message_box.set_text(f"No {item.name} available!")
            return

        actor = self._current_actor()
        if not actor:
            self.message_box.set_text("No active ally to act.")
            return

        target_pattern = item.target_pattern if item else "self"

        if target_pattern == "single_ally":
            self.pending_item_id = item_id
            self.pending_skill_id = None
            prompt = f"Use {item.name} on which ally?" if item else "Choose a target."
            self._begin_target_selection("single_ally", message=prompt)
            if self.waiting_for_target:
                self.menu_mode = "target"
            else:
                self.pending_item_id = None
            return

        cmd = BattleCommand(
            actor_id=actor.entity.entity_id,
            action_type=ActionType.ITEM,
            item_id=item_id,
            target_ids=[actor.entity.entity_id] if target_pattern == "self" else []
        )
        self.battle_system.queue_player_command(cmd)
        item_label = item.name if item else item_id
        self.message_box.set_text(f"{actor.entity.name} uses {item_label}!")
        self.menu_mode = "main"
        self._advance_actor_after_command()

    def _handle_item_selection(self) -> None:
        """Handle item selection."""
        from core.combat import BattleCommand, ActionType

        if not self.item_menu:
            return

        actor = self._current_actor()
        if not actor:
            self.message_box.set_text("No active ally to act.")
            self.menu_mode = "main"
            self.item_menu = None
            return

        selected_idx = self.item_menu.selected_index
        item_id = self.item_menu_mapping.get(selected_idx)
        if not item_id:
            return

        item = self.items_db.get(item_id)
        target_pattern = item.target_pattern if item else "self"

        if target_pattern == "single_ally":
            self.pending_item_id = item_id
            self.pending_skill_id = None
            prompt = f"Use {item.name} on which ally?" if item else "Choose a target."
            self._begin_target_selection("single_ally", message=prompt)
            if self.waiting_for_target:
                self.item_menu = None
                self.menu_mode = "target"
            else:
                self.pending_item_id = None
            return

        cmd = BattleCommand(
            actor_id=actor.entity.entity_id,
            action_type=ActionType.ITEM,
            item_id=item_id,
            target_ids=[actor.entity.entity_id] if target_pattern == "self" else []
        )
        self.battle_system.queue_player_command(cmd)
        item_label = item.name if item else item_id
        self.message_box.set_text(f"{actor.entity.name} uses {item_label}!")
        self.menu_mode = "main"
        self.item_menu = None
        self._advance_actor_after_command()

    def _queue_guard(self) -> None:
        """Queue a guard command."""
        from core.combat import BattleCommand, ActionType

        actor = self._current_actor()
        if not actor:
            self.message_box.set_text("No active ally to act.")
            return
        cmd = BattleCommand(
            actor_id=actor.entity.entity_id,
            action_type=ActionType.GUARD
        )
        self.battle_system.queue_player_command(cmd)
        self.message_box.set_text(f"{actor.entity.name} guards!")
        self._advance_actor_after_command()

    def _queue_talk(self) -> None:
        """Queue a talk command."""
        from core.combat import BattleCommand, ActionType

        actor = self._current_actor()
        if not actor:
            self.message_box.set_text("No active ally to act.")
            return
        alive_enemies = [e for e in self.battle_system.enemies if e.is_alive()]
        if alive_enemies:
            cmd = BattleCommand(
                actor_id=actor.entity.entity_id,
                action_type=ActionType.TALK,
                target_ids=[alive_enemies[0].entity.entity_id]
            )
            self.battle_system.queue_player_command(cmd)
            self.message_box.set_text(f"{actor.entity.name} tries to talk...")
            self._advance_actor_after_command()

    def _queue_flee(self) -> None:
        """Queue a flee command."""
        from core.combat import BattleCommand, ActionType

        actor = self._current_actor()
        if not actor:
            self.message_box.set_text("No active ally to act.")
            return
        cmd = BattleCommand(
            actor_id=actor.entity.entity_id,
            action_type=ActionType.FLEE
        )
        self.battle_system.queue_player_command(cmd)
        self.message_box.set_text(f"{actor.entity.name} tries to flee...")
        self._advance_actor_after_command()

    def _queue_auto_action(self) -> None:
        """Queue an AI-determined action for the current party member."""
        from core.combat import BattleCommand, ActionType

        actor = self._current_actor()
        if not actor:
            self.message_box.set_text("No active ally to act.")
            return

        cmd = self._select_party_ai_action(actor)
        if cmd:
            self.battle_system.queue_player_command(cmd)
            action_desc = self._describe_auto_action(cmd)
            self.message_box.set_text(f"{actor.entity.name} (Auto): {action_desc}")
            self._advance_actor_after_command()
        else:
            # Fallback to guard if AI can't decide
            cmd = BattleCommand(
                actor_id=actor.entity.entity_id,
                action_type=ActionType.GUARD
            )
            self.battle_system.queue_player_command(cmd)
            self.message_box.set_text(f"{actor.entity.name} (Auto): Guards!")
            self._advance_actor_after_command()

    def _show_memory_menu(self) -> None:
        """Show memory operation menu."""
        from ..ui import Menu

        actor = self._current_actor()
        if not actor:
            self.message_box.set_text("No active ally to act.")
            return

        mem_val = actor.memory_value
        mem_type = actor.memory_stat_type or "empty"
        options = [
            "M+ Store",
            "M- Subtract",
            "MR Recall",
            "MC Clear",
            f"[Memory: {mem_val} ({mem_type})]"
        ]
        self.memory_menu = Menu(options[:4], position=self._get_submenu_position(), compact=True)
        self.menu_mode = "memory"
        self.message_box.set_text(f"Memory: {mem_val} ({mem_type}). Choose operation.")

    def _handle_memory_selection(self) -> None:
        """Handle memory operation selection."""
        from core.combat import MemoryOperation

        if not self.memory_menu:
            return

        selection = self.memory_menu.get_selected()
        if selection == "MC Clear":
            self._queue_memory_operation(MemoryOperation.CLEAR, None)
        elif selection == "MR Recall":
            self._queue_memory_operation(MemoryOperation.RECALL, None)
        elif selection in ("M+ Store", "M- Subtract"):
            self._show_memory_stat_menu(selection)

        self.memory_menu = None

    def _show_memory_stat_menu(self, operation: str) -> None:
        """Show stat selection for memory store/subtract."""
        from ..ui import Menu
        from core.combat import MemoryOperation

        stat_options = [
            "Attack",
            "Defense",
            "Magic",
            "Speed",
            "Current HP",
            "Last Damage"
        ]
        self.memory_stat_menu = Menu(stat_options, position=self._get_submenu_position(), compact=True)
        self.menu_mode = "memory_stat"
        is_store = "Store" in operation
        self._pending_memory_op = MemoryOperation.STORE if is_store else MemoryOperation.SUBTRACT
        op_name = "store" if is_store else "subtract"
        self.message_box.set_text(f"Choose stat to {op_name}.")

    def _handle_memory_stat_selection(self) -> None:
        """Handle stat selection for memory operation."""
        from core.combat import MemoryOperation

        if not self.memory_stat_menu:
            return

        stat_map = {
            "Attack": "attack",
            "Defense": "defense",
            "Magic": "magic",
            "Speed": "speed",
            "Current HP": "current_hp",
            "Last Damage": "last_damage"
        }
        selection = self.memory_stat_menu.get_selected()
        stat_type = stat_map.get(selection)

        op = self._pending_memory_op or MemoryOperation.STORE
        self._queue_memory_operation(op, stat_type)
        self.memory_stat_menu = None
        self.menu_mode = "main"
        self._pending_memory_op = None

    def _queue_memory_operation(self, operation, stat_type: Optional[str]) -> None:
        """Queue a memory command."""
        from core.combat import BattleCommand, ActionType

        actor = self._current_actor()
        if not actor:
            return

        cmd = BattleCommand(
            actor_id=actor.entity.entity_id,
            action_type=ActionType.MEMORY,
            memory_operation=operation,
            memory_stat=stat_type
        )
        self.battle_system.queue_player_command(cmd)
        self._pending_memory_op = None
        self._advance_actor_after_command()

    def _describe_auto_action(self, cmd) -> str:
        """Generate a description of an auto action for the message box.

        Uses the ActionHandler pattern to generate descriptions, consolidating
        the logic previously scattered across multiple if/elif chains.
        """
        from core.combat_modules.action_handlers import describe_action

        # Build context with available databases
        context = {
            "skills": self.battle_system.skills,
            "items_db": self.items_db,
            "moves_db": self.moves_db,
        }

        # Get description from handler and format for message box
        description = describe_action(cmd, context)
        return f"{description.capitalize()}!"

    def _toggle_auto_battle(self) -> None:
        """Toggle continuous auto-battle mode."""
        self.auto_battle = not self.auto_battle
        if self.auto_battle:
            self.message_box.set_text("Auto-Battle ON! Press A to disable, +/- to change speed.")
            if hasattr(self, 'combat_log') and self.combat_log:
                self.combat_log.add_message("Auto-Battle enabled.")
        else:
            self.message_box.set_text("Auto-Battle OFF.")
            # Reset speed to 1x when disabling auto-battle
            self.battle_speed = 1
            if hasattr(self, 'combat_log') and self.combat_log:
                self.combat_log.add_message("Auto-Battle disabled.")

    def _cycle_battle_speed(self, direction: int) -> None:
        """Cycle battle speed up or down.

        Args:
            direction: 1 to increase speed, -1 to decrease speed
        """
        if not self.auto_battle:
            self.message_box.set_text("Enable Auto-Battle first (press A).")
            return

        current_idx = self._speed_options.index(self.battle_speed)
        new_idx = current_idx + direction

        # Clamp to valid range
        new_idx = max(0, min(new_idx, len(self._speed_options) - 1))
        self.battle_speed = self._speed_options[new_idx]

        speed_text = f"{self.battle_speed}x"
        self.message_box.set_text(f"Battle Speed: {speed_text}")
        if hasattr(self, 'combat_log') and self.combat_log:
            self.combat_log.add_message(f"Battle speed set to {speed_text}.")

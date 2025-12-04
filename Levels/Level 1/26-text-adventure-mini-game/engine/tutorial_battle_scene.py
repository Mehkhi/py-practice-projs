"""Tutorial battle scene with guided instructions for each battle function."""

import pygame
from typing import Optional, Dict, List, Any, TYPE_CHECKING
from enum import Enum

from .battle_scene import BattleScene
from .ui import MessageBox
from core.combat import BattleSystem, BattleState, ActionType
from core.entities import Player
from core.world import World
from core.items import Item

if TYPE_CHECKING:
    from .scene import SceneManager
    from core.world import Trigger


class TutorialStep(Enum):
    """Tracks which tutorial step we're on."""
    INTRO = "intro"
    ATTACK_EXPLAINED = "attack_explained"
    ATTACK_DONE = "attack_done"
    SKILL_EXPLAINED = "skill_explained"
    SKILL_DONE = "skill_done"
    ITEM_EXPLAINED = "item_explained"
    ITEM_DONE = "item_done"
    GUARD_EXPLAINED = "guard_explained"
    GUARD_DONE = "guard_done"
    TALK_EXPLAINED = "talk_explained"
    TALK_DONE = "talk_done"
    FLEE_EXPLAINED = "flee_explained"
    VICTORY_EXPLAINED = "victory_explained"
    COMPLETE = "complete"


class TutorialBattleScene(BattleScene):
    """Battle scene with step-by-step tutorial guidance."""

    def __init__(
        self,
        manager: "SceneManager",
        battle_system: BattleSystem,
        world: World,
        player: Player,
        assets: Optional[Any] = None,
        scale: int = 2,
        rewards: Optional[Dict[str, Any]] = None,
        items_db: Optional[Dict[str, Item]] = None,
        backdrop_id: Optional[str] = None,
        source_trigger: Optional["Trigger"] = None,
        encounter_id: Optional[str] = None,
    ):
        super().__init__(
            manager, battle_system, world, player, assets, scale,
            rewards, items_db, backdrop_id, source_trigger, encounter_id
        )

        # Tutorial state
        self.tutorial_step = TutorialStep.INTRO
        self._pending_action_type = None  # Track action being executed
        self._last_battle_state = BattleState.PLAYER_CHOOSE
        self.tutorial_messages = {
            TutorialStep.INTRO: (
                "Welcome to your first battle! This tutorial will teach you\n"
                "each battle function. Let's start with the basics.\n"
                "Press Enter to continue..."
            ),
            TutorialStep.ATTACK_EXPLAINED: (
                "ATTACK: Deal physical damage to enemies.\n"
                "Select 'Attack' from the menu, then choose a target.\n"
                "Try attacking the enemy now!"
            ),
            TutorialStep.SKILL_EXPLAINED: (
                "SKILL: Use special abilities that cost SP (Soul Points).\n"
                "Skills can deal more damage or have special effects.\n"
                "Select 'Skill' and try using Fire Bolt!"
            ),
            TutorialStep.ITEM_EXPLAINED: (
                "ITEM: Use consumable items from your inventory.\n"
                "Health Potions restore HP. Select 'Item' to use one!"
            ),
            TutorialStep.GUARD_EXPLAINED: (
                "GUARD: Reduce incoming damage this turn.\n"
                "Useful when you need to survive enemy attacks.\n"
                "Try selecting 'Guard' now!"
            ),
            TutorialStep.TALK_EXPLAINED: (
                "TALK: Attempt to spare enemies (Undertale-style).\n"
                "Repeatedly talking to enemies can make them spareable.\n"
                "Try selecting 'Talk' to see how it works!"
            ),
            TutorialStep.FLEE_EXPLAINED: (
                "FLEE: Try to escape from battle.\n"
                "Success depends on your speed vs enemy speed.\n"
                "For this tutorial, let's finish the battle instead!"
            ),
            TutorialStep.VICTORY_EXPLAINED: (
                "VICTORY CONDITIONS:\n"
                "• Defeat all enemies (reduce HP to 0)\n"
                "• OR spare all enemies (use Talk multiple times)\n"
                "You'll receive rewards when you win!\n"
                "Press Enter to continue..."
            ),
        }
        self._show_tutorial_message(TutorialStep.INTRO)
        self._waiting_for_enter = True
        self._actions_taken = {
            "attack": False,
            "skill": False,
            "item": False,
            "guard": False,
            "talk": False,
        }

    def _show_tutorial_message(self, step: TutorialStep) -> None:
        """Show a tutorial message for the current step."""
        if step in self.tutorial_messages:
            self.message_box.set_text(self.tutorial_messages[step])
        self.tutorial_step = step
        self._waiting_for_enter = step in [TutorialStep.INTRO, TutorialStep.VICTORY_EXPLAINED]

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle input events with tutorial guidance."""
        # Handle Enter key for tutorial messages
        if self._waiting_for_enter and event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            if self.tutorial_step == TutorialStep.INTRO:
                self._show_tutorial_message(TutorialStep.ATTACK_EXPLAINED)
                self._waiting_for_enter = False
                return
            elif self.tutorial_step == TutorialStep.VICTORY_EXPLAINED:
                self._waiting_for_enter = False
                # Let the battle continue normally
                return

        # Handle battle outcome Enter key
        if self.battle_system.state in [BattleState.VICTORY, BattleState.ESCAPED, BattleState.DEFEAT]:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                if self.battle_system.state == BattleState.DEFEAT:
                    # On defeat, return to title screen (uses parent method)
                    self._return_to_title_screen()
                    return
                if self.tutorial_step == TutorialStep.COMPLETE or (self._rewards_applied and self.battle_system.state == BattleState.VICTORY):
                    # Transition to overworld after tutorial
                    self._transition_to_overworld()
                    return

        # Delegate to parent for normal battle controls
        super().handle_event(event)

    def _handle_main_menu_selection(self) -> None:
        """Handle selection from main menu with tutorial guidance."""
        selection = self.main_menu.get_selected()
        if not selection:
            return

        # Track tutorial progress - only advance after action is completed
        action_key = selection.lower()

        # Track which action is being executed for completion detection
        if not self._actions_taken.get(action_key, False):
            self._pending_action_type = action_key

        # Call parent to handle the actual action
        super()._handle_main_menu_selection()

    def update(self, dt: float) -> None:
        """Update battle state and check tutorial progress."""
        # Update battle normally first
        super().update(dt)

        # Check for action completion by monitoring battle state transitions
        current_state = self.battle_system.state
        if (self._pending_action_type and
            self._last_battle_state != BattleState.PLAYER_CHOOSE and
            current_state == BattleState.PLAYER_CHOOSE):

            # Action completed - mark it as taken and advance tutorial
            if self._pending_action_type == "attack" and not self._actions_taken["attack"]:
                self._actions_taken["attack"] = True
                self.tutorial_step = TutorialStep.ATTACK_DONE
                self._show_tutorial_message(TutorialStep.SKILL_EXPLAINED)
            elif self._pending_action_type == "skill" and not self._actions_taken["skill"]:
                self._actions_taken["skill"] = True
                self.tutorial_step = TutorialStep.SKILL_DONE
                self._show_tutorial_message(TutorialStep.ITEM_EXPLAINED)
            elif self._pending_action_type == "item" and not self._actions_taken["item"]:
                self._actions_taken["item"] = True
                self.tutorial_step = TutorialStep.ITEM_DONE
                self._show_tutorial_message(TutorialStep.GUARD_EXPLAINED)
            elif self._pending_action_type == "guard" and not self._actions_taken["guard"]:
                self._actions_taken["guard"] = True
                self.tutorial_step = TutorialStep.GUARD_DONE
                self._show_tutorial_message(TutorialStep.TALK_EXPLAINED)
            elif self._pending_action_type == "talk" and not self._actions_taken["talk"]:
                self._actions_taken["talk"] = True
                self.tutorial_step = TutorialStep.TALK_DONE
                self._show_tutorial_message(TutorialStep.FLEE_EXPLAINED)

            self._pending_action_type = None

        self._last_battle_state = current_state

        # Check if we should advance to next tutorial step (after all actions demonstrated)
        if (self.tutorial_step == TutorialStep.TALK_DONE and
            self.battle_system.state == BattleState.PLAYER_CHOOSE and
            not self._waiting_for_enter and
            self.tutorial_step != TutorialStep.VICTORY_EXPLAINED):
            # Check if player has used all main actions
            if all(self._actions_taken.values()):
                self._show_tutorial_message(TutorialStep.VICTORY_EXPLAINED)

        # Check for victory to show final tutorial message
        if (self.battle_system.state == BattleState.VICTORY and
            self.tutorial_step != TutorialStep.COMPLETE):
            self.tutorial_step = TutorialStep.COMPLETE
            victory_msg = (
                "Excellent! You've completed the tutorial battle!\n"
                "You now know how to use all battle functions.\n"
                "Press Enter to return to the overworld..."
            )
            self.message_box.set_text(victory_msg)

    def _handle_victory(self) -> None:
        """
        Handle battle victory with tutorial completion message.

        This override ensures that the parent BattleScene's reward application logic
        runs (via super()._handle_victory()), while preserving the tutorial-specific
        victory message that was already set in update() when BattleState.VICTORY
        was detected.

        Flow:
        1. update() detects BattleState.VICTORY and sets tutorial_step to COMPLETE
        2. update() sets the tutorial-specific victory message in message_box
        3. update() calls _handle_victory() (inherited from BattleScene)
        4. This override calls super()._handle_victory() to apply rewards/flags
        5. The tutorial message remains displayed (already set in step 2)

        This pattern allows the tutorial to customize messaging while preserving
        all the reward application and flag setting logic from the base class.
        """
        tutorial_message = None
        if self.message_box and self.message_box.text:
            tutorial_message = self.message_box.text
        super()._handle_victory()
        if tutorial_message:
            self.message_box.set_text(tutorial_message)

    def _transition_to_overworld(self) -> None:
        """Transition from tutorial battle to overworld scene."""
        from .world_scene import WorldScene

        # Create overworld scene with the resources we have
        save_manager = self.get_manager_attr(
            "save_manager", "_transition_to_overworld"
        )
        save_slot = self.manager.save_slot if self.manager else 1
        quest_manager = self.get_manager_attr(
            "quest_manager", "_transition_to_overworld"
        )
        encounters_data = self.get_manager_attr(
            "encounters_data", "_transition_to_overworld"
        )
        overworld = WorldScene(
            self.manager,
            self.world,
            self.player,
            tile_size=32,
            scale=self.scale,
            projection="topdown",
            tileset_name=None,
            dialogue_tree=None,  # Will be loaded by WorldScene
            items_db=self.items_db,
            save_manager=save_manager,
            save_slot=save_slot,
            config=getattr(self, 'config', None),  # Pass config if available
            quest_manager=quest_manager,
            encounters_data=encounters_data,
        )
        self.manager.replace(overworld)

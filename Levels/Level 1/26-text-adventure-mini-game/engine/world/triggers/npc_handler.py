"""NPC interaction and item trigger handling."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List, TYPE_CHECKING

from core.logging_utils import log_warning

from .base import TriggerContext, TriggerHandlerStrategy
from .shop_handler import ShopInteractionHandler

if TYPE_CHECKING:
    from core.world import Trigger


@dataclass
class NpcInteractionHandler:
    """Handles NPC interactions including quests, shops, and dialogue."""

    shop_handler: ShopInteractionHandler

    def interact_with_npc(self, npc: Any, context: TriggerContext) -> None:
        scene = context.scene
        self._track_npc_talk_achievement(npc.entity_id, context)

        if self._try_turn_in_quest(npc.entity_id, context):
            dialogue_id = scene._resolve_dialogue_for_npc(npc) if getattr(npc, "dialogue_id", None) else None
            if dialogue_id:
                scene._start_dialogue(dialogue_id)
            return

        if self._try_give_quest(npc.entity_id, context):
            dialogue_id = scene._resolve_dialogue_for_npc(npc) if getattr(npc, "dialogue_id", None) else None
            if dialogue_id:
                scene._start_dialogue(dialogue_id)
            return

        if getattr(npc, "role", "") == "merchant" or getattr(npc, "shop_id", None):
            if self.shop_handler.handle(npc, context):
                return

        if getattr(npc, "dialogue_id", None):
            dialogue_id = scene._resolve_dialogue_for_npc(npc)
            if dialogue_id:
                scene._start_dialogue(dialogue_id)

    def _track_npc_talk_achievement(self, npc_id: str, context: TriggerContext) -> None:
        scene = context.scene
        if scene.manager and getattr(scene.manager, "event_bus", None):
            scene.manager.event_bus.publish("npc_talked", npc_id=npc_id)

        if scene.quest_manager:
            updated_quests = scene.quest_manager.on_npc_talked(npc_id)
            if updated_quests:
                for quest_id in updated_quests:
                    quest = scene.quest_manager.get_quest(quest_id)
                    if quest and quest.is_complete():
                        scene._show_quest_notification(
                            f"Quest Ready: {quest.name}",
                            "Return to the quest giver to claim your reward!",
                        )

    def _try_give_quest(self, npc_id: str, context: TriggerContext) -> bool:
        scene = context.scene
        if not scene.quest_manager:
            return False

        scene.quest_manager.check_prerequisites(scene.world.flags)
        available_quests = scene.quest_manager.get_available_quests()
        for quest in available_quests:
            if quest.giver_npc == npc_id:
                if scene.quest_manager.start_quest(quest.id):
                    scene._show_quest_notification(f"Quest started: {quest.name}", quest.description)
                    tutorial_manager = scene.get_manager_attr("tutorial_manager", "_try_give_quest")
                    if tutorial_manager:
                        from core.tutorial_system import TipTrigger

                        tutorial_manager.trigger_tip(TipTrigger.FIRST_QUEST_ACCEPTED)
                    return True
        return False

    def _try_turn_in_quest(self, npc_id: str, context: TriggerContext) -> bool:
        scene = context.scene
        if not scene.quest_manager:
            return False

        active_quests = scene.quest_manager.get_active_quests()
        for quest in active_quests:
            turn_in_npc = quest.turn_in_npc or quest.giver_npc
            if quest.is_complete() and turn_in_npc == npc_id:
                completed_quest = scene.quest_manager.complete_quest(quest.id)
                if completed_quest:
                    scene._award_quest_rewards(completed_quest)
                    scene._show_quest_notification(
                        f"Quest completed: {completed_quest.name}",
                        "Rewards received!",
                    )
                    return True
        return False


@dataclass
class ItemTriggerHandler(TriggerHandlerStrategy):
    """Adds items to inventory and sets optional flags."""

    trigger_type: str = "item"

    def handle(self, trigger: "Trigger", context: TriggerContext) -> None:
        scene = context.scene
        item_id = trigger.data.get("item_id")
        if item_id and scene.player.inventory:
            if not scene._player_has_item(item_id) or not trigger.data.get("unique", True):
                scene.player.inventory.add(item_id)
                tutorial_manager = scene.get_manager_attr("tutorial_manager", "handle_trigger_item_pickup")
                if tutorial_manager:
                    from core.tutorial_system import TipTrigger

                    tutorial_manager.trigger_tip(TipTrigger.FIRST_ITEM_PICKUP)
                if scene.quest_manager:
                    scene.quest_manager.on_item_collected(item_id, 1)
            flag_name = trigger.data.get("flag_name")
            flag_value = trigger.data.get("flag_value", True)
            if flag_name:
                scene.world.set_flag(flag_name, flag_value)
            trigger.fired = trigger.once

        discover_recipes = trigger.data.get("discover_recipes", [])
        if discover_recipes and scene.player:
            from core.crafting import CraftingSystem, discover_recipes_for_player

            newly_discovered = discover_recipes_for_player(scene.player, discover_recipes)
            if newly_discovered:
                crafting_system = getattr(scene, "crafting_system", None)
                if not crafting_system:
                    crafting_system = CraftingSystem()
                recipe_names: List[str] = []
                for recipe_id in newly_discovered:
                    recipe = crafting_system.get_recipe(recipe_id)
                    recipe_names.append(recipe.name if recipe else recipe_id)

                if len(recipe_names) == 1:
                    scene._show_quest_notification(
                        "Recipe Discovered!", f"You found a recipe: {recipe_names[0]}"
                    )
                else:
                    recipes_text = ", ".join(recipe_names[:-1]) + f", and {recipe_names[-1]}"
                    scene._show_quest_notification(
                        "Recipes Discovered!", f"You found recipes: {recipes_text}"
                    )
        else:
            if trigger.data.get("discover_recipes"):
                log_warning("discover_recipes provided but no player available to learn them")


__all__ = ["NpcInteractionHandler", "ItemTriggerHandler"]

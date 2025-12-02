"""Shop interaction handling."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .base import TriggerContext


@dataclass
class ShopInteractionHandler:
    """Handles merchant interaction flow and schedule-aware messaging."""

    def handle(self, npc: Any, context: TriggerContext) -> bool:
        scene = context.scene
        schedule_mgr = scene.get_manager_attr("schedule_manager", "interact_shop_schedule")
        day_night_cycle = (
            scene.get_manager_attr("day_night_cycle", "interact_shop_schedule") if schedule_mgr else None
        )

        if schedule_mgr and day_night_cycle:
            time_of_day = day_night_cycle.get_time_of_day()

            if not schedule_mgr.is_shop_available(npc.entity_id, time_of_day):
                tutorial_manager = scene.get_manager_attr("tutorial_manager", "interact_shop_schedule")
                if tutorial_manager:
                    from core.tutorial_system import TipTrigger

                    tutorial_manager.trigger_tip(TipTrigger.SHOP_CLOSED)

                alt_dialogue = schedule_mgr.get_alternative_dialogue(npc.entity_id, time_of_day)
                if alt_dialogue:
                    scene._start_dialogue(alt_dialogue)
                    return True

                npc_name = getattr(npc, "name", "The merchant")
                scene._show_inline_message(f"{npc_name}'s shop is closed right now.")
                return True

        if getattr(npc, "dialogue_id", None) and not scene.world.get_flag("met_forest_merchant"):
            scene._pending_shop_for = npc.entity_id
            dialogue_id = scene._resolve_dialogue_for_npc(npc)
            if dialogue_id:
                scene._start_dialogue(dialogue_id)
                return True

        scene._pending_shop_for = None
        scene._open_shop(npc)
        return True


__all__ = ["ShopInteractionHandler"]

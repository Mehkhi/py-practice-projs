"""WorldScene helper functions for dialogue, shops, battles, and weather."""

import os
import time
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from core.constants import DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT
from core.encounters import create_encounter_from_data
from core.logging_utils import log_warning
from core.weather import get_biome_for_map, get_weather_for_map

if TYPE_CHECKING:
    from engine.world_scene import WorldScene
    from core.dialogue import DialogueTree
    from core.entities import Entity, NPC
    from core.quests import Quest
    from core.world import Map


def init_achievement_popups(scene: "WorldScene") -> None:
    """Initialize achievement popup manager and register callback."""
    achievement_manager = scene.get_manager_attr(
        "achievement_manager", "_init_achievement_popups"
    )
    if not achievement_manager:
        return

    screen_width = scene.config.get("window_width", DEFAULT_WINDOW_WIDTH)
    screen_height = scene.config.get("window_height", DEFAULT_WINDOW_HEIGHT)

    from engine.achievement_popup import AchievementPopupManager

    scene.achievement_popup_manager = AchievementPopupManager(screen_width, screen_height)

    def on_achievement_unlocked(achievement):
        if scene.achievement_popup_manager:
            scene.achievement_popup_manager.add_popup(achievement)

    achievement_manager.register_callback(on_achievement_unlocked)


def load_dialogue_tree(scene: "WorldScene") -> Optional["DialogueTree"]:
    """Load dialogue tree from data."""
    path = os.path.join("data", "dialogue.json")
    try:
        from core.dialogue import load_dialogue_from_json

        if os.path.exists(path):
            return load_dialogue_from_json(path)
    except Exception as exc:
        log_warning(f"Failed to load dialogue tree from {path}: {exc}")
    return None


def player_has_item(scene: "WorldScene", item_id: str) -> bool:
    """Check if the player currently has a given item."""
    return bool(scene.player.inventory and scene.player.inventory.has(item_id))


def show_inline_message(scene: "WorldScene", text: str) -> None:
    """Push a lightweight one-off dialogue message."""
    try:
        from core.dialogue import DialogueNode, DialogueChoice, DialogueTree
        from engine.dialogue_scene import DialogueScene

        node = DialogueNode(
            id="inline",
            text=text,
            choices=[DialogueChoice(text="Continue", next_id=None, set_flag=None)]
        )
        tree = DialogueTree({"inline": node})
        dialogue_scene = DialogueScene(
            scene.manager,
            "inline",
            world=scene.world,
            scale=scene.scale,
            tree=tree,
            assets=scene.assets,
            player=scene.player
        )
        scene.manager.push(dialogue_scene)
    except Exception as exc:
        log_warning(f"Failed to show inline message (text: {text[:50] if text else 'None'}...): {exc}")


def show_dialogue_or_message(
    scene: "WorldScene",
    dialogue_id: Optional[str],
    fallback_text: Optional[str] = None
) -> None:
    """Show a dialogue node if available, otherwise fall back to inline text."""
    if dialogue_id and scene.dialogue_tree and scene.dialogue_tree.has_node(dialogue_id):
        start_dialogue(scene, dialogue_id)
    elif fallback_text:
        show_inline_message(scene, fallback_text)


def requirements_met(
    scene: "WorldScene",
    data: Dict[str, Any],
    fallback_text: Optional[str] = None,
    show_message: bool = True
) -> bool:
    """Check common requirement keys against world state and inventory."""
    requires_flag = data.get("requires_flag")
    requires_flags = data.get("requires_flags", [])
    requires_item = data.get("requires_item")
    blocked_by_flag = data.get("blocked_by_flag") or data.get("block_if_flag")
    skip_if_flag = data.get("skip_if_flag")
    fail_dialogue_id = data.get("fail_dialogue_id")

    flags_needed: List[str] = []
    if requires_flag:
        flags_needed.append(requires_flag)
    if isinstance(requires_flags, str):
        flags_needed.append(requires_flags)
    else:
        flags_needed.extend(requires_flags)

    for flag in flags_needed:
        if not scene.world.get_flag(flag):
            hint = fallback_text or f"You need {flag.replace('_', ' ')} first."
            if show_message:
                show_dialogue_or_message(scene, fail_dialogue_id, hint)
            return False

    if requires_item and not player_has_item(scene, requires_item):
        hint = fallback_text or f"You need {requires_item} to proceed."
        if show_message:
            show_dialogue_or_message(scene, fail_dialogue_id, hint)
        return False

    if blocked_by_flag and scene.world.get_flag(blocked_by_flag):
        hint = fallback_text or "Something blocks the way."
        if show_message:
            show_dialogue_or_message(scene, fail_dialogue_id, hint)
        return False

    if skip_if_flag and scene.world.get_flag(skip_if_flag):
        return False

    return True


def encounter_already_cleared(scene: "WorldScene", encounter_id: Optional[str]) -> bool:
    """Check reward flags to decide if an encounter was already beaten."""
    if not encounter_id or encounter_id not in scene.encounters_data:
        return False
    rewards = scene.encounters_data.get(encounter_id, {}).get("rewards", {})
    reward_flags = rewards.get("flags", [])
    return any(scene.world.get_flag(flag) for flag in reward_flags)


def battle_available(scene: "WorldScene", trigger) -> bool:
    """Evaluate gating and completion before starting a battle."""
    encounter_id = trigger.data.get("encounter_id", "default")
    show_message = trigger.id != scene._last_blocked_trigger
    if not requirements_met(scene, trigger.data, show_message=show_message):
        scene._last_blocked_trigger = trigger.id
        return False
    if trigger.once and encounter_already_cleared(scene, encounter_id):
        trigger.fired = True
        scene._last_blocked_trigger = trigger.id
        return False
    scene._last_blocked_trigger = None
    return True


def can_use_warp(scene: "WorldScene", warp, show_message: bool = True) -> bool:
    """Check warp requirements such as flags or key items."""
    if warp is None:
        return False
    req_data = {
        "requires_flag": getattr(warp, "requires_flag", None),
        "requires_flags": [],
        "requires_item": getattr(warp, "requires_item", None),
        "blocked_by_flag": getattr(warp, "blocked_by_flag", None),
        "fail_dialogue_id": getattr(warp, "fail_dialogue_id", None),
    }
    return requirements_met(scene, req_data, show_message=show_message)


def resolve_dialogue_for_npc(scene: "WorldScene", npc: "NPC") -> Optional[str]:
    """Pick a dialogue id based on world flags and NPC role."""
    if npc.dialogue_id == "garden_spirit":
        if scene.world.get_flag("spared_crystal"):
            return "garden_spirit_grateful"
        if scene.world.get_flag("took_crystal"):
            return "garden_spirit_displeased"
    if npc.dialogue_id == "forest_merchant_intro" and scene.world.get_flag("met_forest_merchant"):
        return "forest_merchant_return"
    return npc.dialogue_id


def get_shop_stock(scene: "WorldScene", npc: "NPC") -> Dict[str, int]:
    """Build or update stock for a merchant NPC from centralized shop or inline inventory."""
    npc_id = npc.entity_id
    if npc_id not in scene.shop_stock:
        base_stock: Dict[str, int] = {}

        if hasattr(npc, 'shop_id') and npc.shop_id:
            shop_config = scene.shops_db.get(npc.shop_id)
            if shop_config:
                base_stock = dict(shop_config.get("stock", {}))

        inline_inventory = dict(getattr(npc, "shop_inventory", {}) or {})
        for item_id, qty in inline_inventory.items():
            base_stock[item_id] = qty

        scene.shop_stock[npc_id] = base_stock

    stock = scene.shop_stock[npc_id]

    if scene.world.get_flag("forest_wolves_cleared"):
        stock.setdefault("torch", 1)
    if scene.world.get_flag("cave_cleared"):
        stock.setdefault("health_potion", 1)

    return stock


def open_shop(scene: "WorldScene", npc: "NPC") -> None:
    """Push the shop scene for a merchant NPC."""
    scene.world.set_flag("met_forest_merchant", True)
    try:
        from engine.shop_scene import ShopScene, create_shop_scene

        greeting_text: Optional[str] = None
        if scene.dialogue_tree and npc.dialogue_id:
            node_id = resolve_dialogue_for_npc(scene, npc)
            if node_id and scene.dialogue_tree.has_node(node_id):
                node = scene.dialogue_tree.get_node(node_id)
                if node:
                    greeting_text = node.text

        if hasattr(npc, 'shop_id') and npc.shop_id:
            shop_scene = create_shop_scene(
                manager=scene.manager,
                world=scene.world,
                player=scene.player,
                items_db=scene.items_db,
                shop_id=npc.shop_id,
                shops_db=scene.shops_db,
                assets=scene.assets,
                scale=scene.scale,
                quest_manager=scene.quest_manager,
            )
            if shop_scene:
                if greeting_text:
                    shop_scene.message_box.set_text(greeting_text)
                scene.manager.push(shop_scene)
                return
            log_warning(f"Shop ID '{npc.shop_id}' for NPC '{npc.entity_id}' not found in shops_db")

        stock = get_shop_stock(scene, npc)
        if not stock:
            show_inline_message(scene, "The merchant has nothing left to sell.")
            return

        legacy_shop_scene = ShopScene(
            scene.manager,
            scene.world,
            scene.player,
            scene.items_db,
            stock,
            assets=scene.assets,
            scale=scene.scale,
            title=f"{npc.name}'s shop",
            quest_manager=scene.quest_manager,
        )
        if greeting_text:
            legacy_shop_scene.message_box.set_text(greeting_text)
        scene.manager.push(legacy_shop_scene)
    except Exception as exc:
        log_warning(f"Failed to open shop for NPC {npc.entity_id if npc else 'unknown'}: {exc}")


def award_quest_rewards(scene: "WorldScene", quest: "Quest") -> None:
    """Award quest rewards to the player."""
    if not quest or not scene.player:
        return
    bus = getattr(scene.manager, "event_bus", None) if scene.manager else None

    if quest.reward_gold > 0:
        current_gold = scene.world.get_flag("gold")
        if current_gold is False or current_gold is True:
            current_gold = 0
        elif not isinstance(current_gold, (int, float)):
            current_gold = 0
        new_gold = int(current_gold) + quest.reward_gold
        scene.world.set_flag("gold", new_gold)
        if bus:
            bus.publish("gold_changed", total_gold=new_gold)

    if quest.reward_exp > 0 and hasattr(scene.player, 'add_experience'):
        scene.player.add_experience(quest.reward_exp)

    if quest.reward_items and scene.player.inventory:
        for item_id, quantity in quest.reward_items.items():
            for _ in range(quantity):
                scene.player.inventory.add(item_id)

    if hasattr(scene.player, 'class_id') and scene.player.class_id:
        class_rewards = quest.class_rewards.get(scene.player.class_id, {})
        for item_id, quantity in class_rewards.items():
            for _ in range(quantity):
                if scene.player.inventory:
                    scene.player.inventory.add(item_id)

    if hasattr(scene.player, 'subclass_id') and scene.player.subclass_id:
        subclass_rewards = quest.subclass_rewards.get(scene.player.subclass_id, {})
        for item_id, quantity in subclass_rewards.items():
            for _ in range(quantity):
                if scene.player.inventory:
                    scene.player.inventory.add(item_id)

    for flag in quest.reward_flags:
        scene.world.set_flag(flag, True)

    if quest.reward_recipes:
        from core.crafting import CraftingSystem, discover_recipes_for_player

        newly_discovered = discover_recipes_for_player(scene.player, quest.reward_recipes)
        if newly_discovered:
            recipe_names = []
            crafting_system = getattr(scene, 'crafting_system', None)
            if not crafting_system:
                crafting_system = CraftingSystem()

            for recipe_id in newly_discovered:
                recipe = crafting_system.get_recipe(recipe_id)
                if recipe:
                    recipe_names.append(recipe.name)
                else:
                    recipe_names.append(recipe_id)

            if len(recipe_names) == 1:
                show_quest_notification(
                    scene,
                    "Recipe Discovered!",
                    f"You learned how to craft: {recipe_names[0]}"
                )
            else:
                recipes_text = ", ".join(recipe_names[:-1]) + f", and {recipe_names[-1]}"
                show_quest_notification(
                    scene,
                    "Recipes Discovered!",
                    f"You learned how to craft: {recipes_text}"
                )


def show_quest_notification(scene: "WorldScene", title: str, message: str) -> None:
    """Show a quest notification message as an in-game popup."""
    notification_text = f"{title}\n\n{message}"
    show_inline_message(scene, notification_text)


def start_dialogue(scene: "WorldScene", dialogue_id: str) -> None:
    """Push a dialogue scene for a given dialogue node."""
    if not scene.dialogue_tree or not scene.dialogue_tree.has_node(dialogue_id):
        return
    try:
        from engine.dialogue_scene import DialogueScene

        dialogue_scene = DialogueScene(
            scene.manager,
            dialogue_id,
            world=scene.world,
            scale=scene.scale,
            tree=scene.dialogue_tree,
            assets=scene.assets,
            player=scene.player
        )
        scene.manager.push(dialogue_scene)
    except Exception as exc:
        log_warning(f"Failed to open dialogue scene for dialogue_id '{dialogue_id}': {exc}")


def start_battle(scene: "WorldScene", encounter_id: str, trigger: Optional[Any] = None) -> None:
    """Start a battle encounter."""
    if encounter_id == "secret_boss_mirror" and trigger and hasattr(trigger, 'data'):
        boss_id = trigger.data.get("boss_id")
        if boss_id == "mirror_self":
            secret_boss_manager = scene.get_manager_attr(
                "secret_boss_manager", "_start_battle_mirror"
            )
            if secret_boss_manager and scene.player:
                mirror_encounter = secret_boss_manager.create_mirror_encounter(scene.player)
                original_encounter = scene.encounters_data.get(encounter_id)
                scene.encounters_data[encounter_id] = mirror_encounter
                try:
                    enemies, rewards, backdrop_id, ai_metadata = create_encounter_from_data(
                        encounter_id=encounter_id,
                        encounters_data=scene.encounters_data,
                        items_db=scene.items_db,
                    )
                finally:
                    if original_encounter:
                        scene.encounters_data[encounter_id] = original_encounter
                    else:
                        scene.encounters_data.pop(encounter_id, None)
            else:
                enemies, rewards, backdrop_id, ai_metadata = create_encounter_from_data(
                    encounter_id=encounter_id,
                    encounters_data=scene.encounters_data,
                    items_db=scene.items_db,
                )
        else:
            enemies, rewards, backdrop_id, ai_metadata = create_encounter_from_data(
                encounter_id=encounter_id,
                encounters_data=scene.encounters_data,
                items_db=scene.items_db,
            )
    else:
        enemies, rewards, backdrop_id, ai_metadata = create_encounter_from_data(
            encounter_id=encounter_id,
            encounters_data=scene.encounters_data,
            items_db=scene.items_db,
        )

    battle_context: Dict[str, Any] = {}
    challenge_manager = scene.get_manager_attr(
        "challenge_dungeon_manager", "_start_battle_modifiers"
    )
    if challenge_manager and challenge_manager.active_dungeon_id:
        challenge_manager.apply_modifiers_to_battle(battle_context)

        for enemy in enemies:
            if hasattr(enemy, 'stats') and enemy.stats:
                if "enemy_hp_multiplier" in battle_context:
                    multiplier = battle_context["enemy_hp_multiplier"]
                    enemy.stats.max_hp = int(enemy.stats.max_hp * multiplier)
                    enemy.stats.hp = enemy.stats.max_hp

                if "enemy_damage_multiplier" in battle_context:
                    multiplier = battle_context["enemy_damage_multiplier"]
                    enemy.stats.attack = int(enemy.stats.attack * multiplier)
                    enemy.stats.magic = int(enemy.stats.magic * multiplier)

                if "enemy_speed_multiplier" in battle_context:
                    multiplier = battle_context["enemy_speed_multiplier"]
                    enemy.stats.speed = int(enemy.stats.speed * multiplier)

                if "enemy_stat_multiplier" in battle_context and "enemy_hp_multiplier" not in battle_context:
                    multiplier = battle_context["enemy_stat_multiplier"]
                    enemy.stats.max_hp = int(enemy.stats.max_hp * multiplier)
                    enemy.stats.hp = enemy.stats.max_hp
                    enemy.stats.attack = int(enemy.stats.attack * multiplier)
                    enemy.stats.defense = int(enemy.stats.defense * multiplier)
                    enemy.stats.magic = int(enemy.stats.magic * multiplier)
                    enemy.stats.speed = int(enemy.stats.speed * multiplier)

        if battle_context.get("stat_scramble"):
            import random

            should_swap = random.random() < 0.5
            if should_swap:
                for enemy in enemies:
                    if hasattr(enemy, 'stats') and enemy.stats:
                        temp_attack = enemy.stats.attack
                        enemy.stats.attack = enemy.stats.magic
                        enemy.stats.magic = temp_attack
                battle_context["stat_scrambled"] = True

    from core.combat import BattleSystem

    party_members = scene.player.get_battle_party()
    battle_system = BattleSystem(
        players=party_members,
        enemies=enemies,
        skills=scene.skills,
        items=scene.items_db,
        debug_ai=scene.config.get('debug_ai', False),
        phase_feedback=scene.config.get('ai_phase_feedback', False),
        battle_context=battle_context
    )

    for metadata in ai_metadata:
        enemy_index = metadata["enemy_index"]
        if enemy_index < len(battle_system.enemies):
            enemy_participant = battle_system.enemies[enemy_index]
            enemy_participant.ai_profile = metadata["ai_profile"]
            computed_skills = metadata["skills"] or getattr(enemy_participant.entity, "skills", [])
            enemy_participant.skills = list(dict.fromkeys(computed_skills))
            enemy_participant.items = metadata["items"]
            if scene.config.get("ai_validation_enabled", True):
                if scene.ai_validator:
                    scene.ai_validator.validate_single_ai_profile(
                        enemy_participant.ai_profile,
                        scene.skills,
                        scene.items_db,
                        encounter_id,
                        metadata["enemy_id"],
                    )
                else:
                    log_warning(
                        f"AI validation enabled but validator not available for "
                        f"encounter '{encounter_id}' enemy '{metadata['enemy_id']}'"
                    )

    from engine.battle_scene import BattleScene

    battle_scene = BattleScene(
        scene.manager,
        battle_system,
        scene.world,
        scene.player,
        scale=scene.scale,
        assets=scene.assets,
        rewards=rewards,
        items_db=scene.items_db,
        backdrop_id=backdrop_id,
        source_trigger=trigger,
        encounter_id=encounter_id
    )
    if battle_context:
        battle_scene.battle_context = battle_context
    scene.manager.push(battle_scene)


def check_challenge_dungeon_timer(scene: "WorldScene", dt: float) -> None:
    """Check time limit for challenge dungeon floors and reset if expired."""
    challenge_manager = scene.get_manager_attr(
        "challenge_dungeon_manager", "_check_challenge_dungeon_timer"
    )
    if not challenge_manager or not challenge_manager.active_dungeon_id:
        return

    dungeon = challenge_manager.dungeons.get(challenge_manager.active_dungeon_id)
    if not dungeon or not dungeon.time_limit:
        return

    if scene.world.current_map_id not in dungeon.map_ids:
        return

    elapsed = time.time() - challenge_manager.current_floor_start_time
    if challenge_manager.check_floor_timer(elapsed):
        entry_x = dungeon.entry_x
        entry_y = dungeon.entry_y
        entry_map_id = dungeon.entry_map_id
        scene.player.set_position(entry_x, entry_y)
        if scene.world.current_map_id != entry_map_id:
            scene.world.set_current_map(entry_map_id)
        challenge_manager.start_floor()
        show_inline_message(scene, "Time limit expired! Floor reset.")


def is_in_challenge_dungeon_with_restriction(scene: "WorldScene", restriction: str) -> bool:
    """Check if player is in a challenge dungeon with a specific restriction."""
    challenge_manager = scene.get_manager_attr(
        "challenge_dungeon_manager", "_is_in_challenge_dungeon_with_restriction"
    )
    if not challenge_manager or not challenge_manager.active_dungeon_id:
        return False

    dungeon = challenge_manager.dungeons.get(challenge_manager.active_dungeon_id)
    if not dungeon:
        return False

    if restriction == "no_save":
        return dungeon.no_save
    if restriction == "no_items":
        return dungeon.no_items

    return False


def update_map_weather(scene: "WorldScene") -> None:
    """Update weather system based on current map."""
    weather = scene.get_manager_attr("weather_system", "_update_map_weather")
    if not weather or not weather.enabled:
        return

    current_map = scene.world.get_current_map()
    if not current_map:
        return

    map_weather = get_weather_for_map(current_map.map_id)
    weather.set_map_override(map_weather)

    biome = get_biome_for_map(current_map.map_id)
    weather.set_biome_weights(biome)

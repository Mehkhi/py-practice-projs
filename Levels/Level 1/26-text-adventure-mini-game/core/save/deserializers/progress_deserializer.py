"""Progress-related deserialization: achievements, arena, gambling, etc."""

from typing import Any, Dict, Optional

from .base import DeserializationResources, DeserializerContext, DomainDeserializer


def deserialize_gambling_manager(data: Optional[Dict[str, Any]]) -> Optional[Any]:
    """Deserialize gambling manager from a dict."""
    if not data:
        return None

    from ...gambling import GamblingManager

    return GamblingManager.deserialize(data)


def deserialize_challenge_dungeon_manager(
    data: Optional[Dict[str, Any]],
    dungeons: Dict[str, Any],
    modifiers: Dict[str, Any],
) -> Optional[Any]:
    """Deserialize challenge dungeon manager from a dict."""
    if not data:
        return None
    from ...challenge_dungeons import ChallengeDungeonManager

    return ChallengeDungeonManager.deserialize(data, dungeons, modifiers)


def _restore_achievements(data: Dict[str, Any], context: DeserializerContext) -> None:
    if context.achievement_manager and "achievements" in data:
        context.achievement_manager.deserialize_state(data["achievements"])


def _restore_gambling(data: Dict[str, Any], context: DeserializerContext) -> None:
    if not context.gambling_manager or "gambling" not in data:
        return
    restored = deserialize_gambling_manager(data["gambling"])
    if restored:
        context.gambling_manager.stats = restored.stats


def _restore_arena(data: Dict[str, Any], context: DeserializerContext) -> None:
    if not context.arena_manager or "arena" not in data:
        return
    arena_data = data["arena"]
    fighters_data = arena_data.get("fighters", {})

    for fighter_id, record in fighters_data.items():
        fighter = context.arena_manager.fighters.get(fighter_id)
        if fighter:
            fighter.wins = record.get("wins", fighter.wins)
            fighter.losses = record.get("losses", fighter.losses)
            fighter.odds = record.get("odds", fighter.odds)

    from ...arena import ArenaBet, ArenaMatch

    context.arena_manager.current_matches = []
    for match_data in arena_data.get("current_matches", []):
        fighter_a = context.arena_manager.fighters.get(match_data.get("fighter_a_id"))
        fighter_b = context.arena_manager.fighters.get(match_data.get("fighter_b_id"))
        if fighter_a and fighter_b:
            context.arena_manager.current_matches.append(
                ArenaMatch(
                    match_id=match_data.get("match_id", ""),
                    fighter_a=fighter_a,
                    fighter_b=fighter_b,
                    scheduled_time=match_data.get("scheduled_time"),
                )
            )

    context.arena_manager.active_bets = [
        ArenaBet(
            match_id=bet_data.get("match_id", ""),
            fighter_id=bet_data.get("fighter_id", ""),
            amount=bet_data.get("amount", 0),
            odds_at_bet=bet_data.get("odds_at_bet", 1.0),
        )
        for bet_data in arena_data.get("active_bets", [])
    ]
    context.arena_manager.match_history = arena_data.get("match_history", [])


def _restore_challenge_dungeons(data: Dict[str, Any], context: DeserializerContext, resources: DeserializationResources) -> None:
    if not context.challenge_dungeon_manager or "challenge_dungeons" not in data:
        return
    challenge_data = data["challenge_dungeons"]
    dungeons, modifiers = resources.resolve_challenge_dungeons(context.challenge_dungeon_manager)
    restored = deserialize_challenge_dungeon_manager(challenge_data, dungeons, modifiers)
    if restored:
        context.challenge_dungeon_manager.progress = restored.progress
        context.challenge_dungeon_manager.active_dungeon_id = restored.active_dungeon_id
        context.challenge_dungeon_manager.dungeon_start_time = restored.dungeon_start_time


def _restore_secret_bosses(data: Dict[str, Any], context: DeserializerContext, resources: DeserializationResources) -> None:
    if not context.secret_boss_manager or "secret_bosses" not in data:
        return
    boss_definitions = resources.resolve_secret_bosses(context.secret_boss_manager)
    from ...secret_bosses import SecretBossManager

    restored_manager = SecretBossManager.deserialize(data["secret_bosses"], boss_definitions)
    if restored_manager:
        context.secret_boss_manager.discovered = restored_manager.discovered.copy()
        context.secret_boss_manager.defeated = restored_manager.defeated.copy()
        context.secret_boss_manager.available = restored_manager.available.copy()


def _restore_hints(data: Dict[str, Any], context: DeserializerContext, resources: DeserializationResources) -> None:
    if not context.hint_manager or "hints" not in data:
        return
    hint_definitions = resources.resolve_hint_definitions(context.hint_manager)
    from ...secret_boss_hints import HintManager

    restored_hint_manager = HintManager.deserialize(data["hints"], hint_definitions)
    if restored_hint_manager:
        context.hint_manager.discovered_hints = restored_hint_manager.discovered_hints.copy()


def _restore_post_game(data: Dict[str, Any], context: DeserializerContext, resources: DeserializationResources) -> None:
    if not context.post_game_manager or "post_game" not in data:
        return
    from ...post_game import PostGameManager

    unlock_definitions = resources.resolve_post_game_unlocks(context.post_game_manager)
    restored = PostGameManager.deserialize(data["post_game"], unlock_definitions)
    if restored:
        context.post_game_manager.state = restored.state
        context.post_game_manager.active_unlocks = restored.active_unlocks.copy()


def _restore_tutorial(data: Dict[str, Any], context: DeserializerContext, resources: DeserializationResources) -> None:
    if not context.tutorial_manager or "tutorial" not in data:
        return
    from ...tutorial_system import TutorialManager

    tips, help_entries = resources.resolve_tutorial_data(context.tutorial_manager)
    restored = TutorialManager.deserialize(data["tutorial"], tips, help_entries)
    if restored:
        context.tutorial_manager.dismissed_tips = restored.dismissed_tips.copy()
        context.tutorial_manager.seen_tips = restored.seen_tips.copy()
        context.tutorial_manager.tips_enabled = restored.tips_enabled


class ProgressDeserializer(DomainDeserializer):
    """Deserialize progression systems (achievements, arena, challenge, etc.)."""

    def deserialize(self, data: Dict[str, Any], context: DeserializerContext, resources: DeserializationResources) -> None:
        _restore_achievements(data, context)
        _restore_gambling(data, context)
        _restore_arena(data, context)
        _restore_challenge_dungeons(data, context, resources)
        _restore_secret_bosses(data, context, resources)
        _restore_hints(data, context, resources)
        _restore_post_game(data, context, resources)
        _restore_tutorial(data, context, resources)

from types import SimpleNamespace

import pytest

from engine.battle.targeting import BattleTargetingMixin
from engine.battle_scene import BattleScene
from core.combat import ActionType, BattleCommand
from core.moves import Move, MoveAnimation


class DummyMessageBox:
    def __init__(self) -> None:
        self.text = ""

    def set_text(self, text: str) -> None:
        self.text = text


class DummyParticipant:
    def __init__(self, entity_id: str, name: str, hp: int) -> None:
        self.entity = SimpleNamespace(entity_id=entity_id, name=name, sprite_id="ally")
        self.stats = SimpleNamespace(hp=hp, max_hp=10)

    def is_alive(self) -> bool:
        return self.stats.hp > 0 and not getattr(self, "spared", False)


class DummyBattleSystem:
    def __init__(self, players):
        self.players = players
        self.enemies = []
        self.queued_commands = []

    def queue_player_command(self, cmd: BattleCommand) -> None:
        self.queued_commands.append(cmd)


class DummyScene(BattleTargetingMixin):
    def __init__(self, players, items_db):
        self.battle_system = DummyBattleSystem(players)
        self.message_box = DummyMessageBox()
        self.items_db = items_db

        self.pending_skill_id = None
        self.pending_item_id = None
        self.pending_move_id = None
        self.waiting_for_target = False
        self.menu_mode = "main"
        self.target_side = None
        self.target_type = None
        self.item_menu_mapping = {}
        self.move_menu_mapping = {}
        self.skill_menu = None
        self.item_menu = None
        self.memory_menu = None
        self.memory_stat_menu = None
        self._pending_memory_op = None
        self._include_downed_allies = False

        self.active_player_index = 0
        self.main_menu = SimpleNamespace(selected_index=0)

    def _start_move_animation(self, move, target):
        # Not needed for tests
        pass


@pytest.fixture
def revive_item_db():
    return {
        "phoenix_down": SimpleNamespace(
            effect_id="revive_25", target_pattern="single_ally", name="Phoenix Down"
        ),
        "healing_herb": SimpleNamespace(
            effect_id="heal_small", target_pattern="single_ally", name="Healing Herb"
        ),
    }


def test_revive_item_targets_downed_allies(revive_item_db):
    players = [DummyParticipant("ally1", "Hero", 10), DummyParticipant("ally2", "Mage", 0)]
    scene = DummyScene(players, revive_item_db)
    scene.pending_item_id = "phoenix_down"

    scene._begin_target_selection("single_ally")
    assert scene.waiting_for_target is True
    assert scene.target_side == "ally"
    assert scene._include_downed_allies is True

    # Select the downed ally (index 1) and queue the command
    scene.target_index = 1
    scene._select_target()

    assert len(scene.battle_system.queued_commands) == 1
    cmd = scene.battle_system.queued_commands[0]
    assert cmd.action_type == ActionType.ITEM
    assert cmd.target_ids == ["ally2"]
    assert scene.waiting_for_target is False
    assert scene.menu_mode == "main"


def test_non_revive_item_excludes_downed_allies(revive_item_db):
    players = [DummyParticipant("ally1", "Hero", 0)]
    scene = DummyScene(players, revive_item_db)
    scene.pending_item_id = "healing_herb"

    scene._begin_target_selection("single_ally")

    assert scene.waiting_for_target is False
    assert scene.message_box.text == "No valid allies."
    assert not scene.battle_system.queued_commands


def test_run_move_learns_then_invokes_callback(monkeypatch):
    scene = BattleScene.__new__(BattleScene)
    scene.manager = SimpleNamespace()
    scene.manager.pushed = []
    scene.manager.push = scene.manager.pushed.append
    scene.scale = 2
    scene.assets = None

    move = Move(
        id="slash",
        name="Slash",
        description="",
        power=10,
        accuracy=100,
        element="physical",
        animation=MoveAnimation(type="impact", color=(255, 255, 255), duration=0.1, frames=2),
    )
    rewards_handler = SimpleNamespace(
        _pending_move_learns=[(SimpleNamespace(name="Hero"), move)]
    )
    scene.rewards_handler = rewards_handler

    called = []

    def fake_move_learn_scene(manager, entity, move_obj, on_complete, assets=None, scale=2):
        on_complete()
        return SimpleNamespace(entity=entity, move=move_obj)

    monkeypatch.setattr("engine.move_learn_scene.MoveLearnScene", fake_move_learn_scene)

    scene._run_move_learns_then(lambda: called.append("done"))

    assert called == ["done"]
    assert rewards_handler._pending_move_learns == []
    # Ensure a scene was pushed (even though our fake immediately completes)
    assert scene.manager.pushed

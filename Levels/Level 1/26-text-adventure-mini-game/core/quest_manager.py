"""QuestManager for managing all quests and their state."""

from typing import Any, Dict, List, Optional, Tuple

from .data_loader import load_json_file
from .logging_utils import log_warning
from .quest_models import (
    ObjectiveType,
    Quest,
    QuestObjective,
    QuestStatus,
)


class QuestManager:
    """Manages all quests and their state.

    Implements the Saveable protocol for automatic save/load via SaveContext.

    This class provides comprehensive quest management including:
    - Quest loading from JSON definitions
    - Quest lifecycle management (locked, available, active, completed, failed)
    - Objective tracking from multiple sources (combat, items, NPCs, maps, flags)
    - Prerequisite checking and quest unlocking
    - Failure condition monitoring
    - Quest tracking for UI display
    - Save/load state persistence

    Quest lifecycle:
    1. LOCKED: Quest exists but prerequisites not met
    2. AVAILABLE: Prerequisites met, can be started
    3. ACTIVE: Quest in progress, objectives being tracked
    4. COMPLETED: All objectives complete, rewards given
    5. FAILED: Failure conditions met (time limit, flag, NPC death)

    Objective tracking integration:
    - on_enemy_killed(): Called from battle scenes when enemies die
    - on_item_collected(): Called from world scenes when items collected
    - on_npc_talked(): Called from dialogue scenes when NPCs talked to
    - on_map_entered(): Called from world scenes when maps entered
    - check_flag_objectives(): Called periodically to check flag-based objectives

    Example usage:
        ```python
        manager = QuestManager()
        manager.load_quests("data/quests.json")

        # Check prerequisites and unlock quests
        newly_available = manager.check_prerequisites(world_flags)

        # Start a quest
        manager.start_quest("tutorial_quest")

        # Update objectives from game events
        manager.on_enemy_killed("wolf")
        manager.on_item_collected("ancient_key")

        # Complete quest when all objectives done
        completed_quest = manager.complete_quest("tutorial_quest")
        if completed_quest:
            # Award rewards
            pass
        ```

    Attributes:
        quests: Dictionary mapping quest_id to Quest instances
        _definitions: Original JSON definitions for quest reset/reload
        save_key: Key used for this manager in save data ('quests')
    """

    save_key: str = "quests"

    def __init__(self) -> None:
        self.quests: Dict[str, Quest] = {}
        self._definitions: Dict[str, Dict[str, Any]] = {}  # Original definitions for reset

        # Performance optimization: indexed lookups for objectives
        # Maps target -> [(quest_id, objective_id), ...]
        self._kill_objectives_by_target: Dict[str, List[Tuple[str, str]]] = {}
        self._talk_objectives_by_npc: Dict[str, List[Tuple[str, str]]] = {}
        self._collect_objectives_by_item: Dict[str, List[Tuple[str, str]]] = {}
        self._reach_objectives_by_map: Dict[str, List[Tuple[str, str]]] = {}
        self._flag_objectives_by_flag: Dict[str, List[Tuple[str, str]]] = {}

    def _rebuild_indexes(self) -> None:
        """Rebuild all objective indexes from active quests.

        This method clears and repopulates the index dictionaries to ensure
        they accurately reflect the current state of active quests. Should be
        called whenever quest status changes (start, complete, fail) or after
        loading quests/state.
        """
        # Clear all indexes
        self._kill_objectives_by_target.clear()
        self._talk_objectives_by_npc.clear()
        self._collect_objectives_by_item.clear()
        self._reach_objectives_by_map.clear()
        self._flag_objectives_by_flag.clear()

        # Rebuild from active quests
        for quest in self.get_active_quests():
            for obj in quest.objectives:
                if obj.completed:
                    continue  # Skip completed objectives

                quest_obj_pair = (quest.id, obj.id)

                if obj.objective_type == ObjectiveType.KILL:
                    if obj.target:
                        if obj.target not in self._kill_objectives_by_target:
                            self._kill_objectives_by_target[obj.target] = []
                        self._kill_objectives_by_target[obj.target].append(quest_obj_pair)

                elif obj.objective_type == ObjectiveType.TALK:
                    if obj.target:
                        if obj.target not in self._talk_objectives_by_npc:
                            self._talk_objectives_by_npc[obj.target] = []
                        self._talk_objectives_by_npc[obj.target].append(quest_obj_pair)

                elif obj.objective_type == ObjectiveType.COLLECT:
                    if obj.target:
                        if obj.target not in self._collect_objectives_by_item:
                            self._collect_objectives_by_item[obj.target] = []
                        self._collect_objectives_by_item[obj.target].append(quest_obj_pair)

                elif obj.objective_type == ObjectiveType.REACH:
                    if obj.target:
                        if obj.target not in self._reach_objectives_by_map:
                            self._reach_objectives_by_map[obj.target] = []
                        self._reach_objectives_by_map[obj.target].append(quest_obj_pair)

                elif obj.objective_type == ObjectiveType.FLAG:
                    if obj.target:
                        if obj.target not in self._flag_objectives_by_flag:
                            self._flag_objectives_by_flag[obj.target] = []
                        self._flag_objectives_by_flag[obj.target].append(quest_obj_pair)

    def load_quests(self, json_path: str) -> None:
        """Load quest definitions from JSON file."""
        data = load_json_file(
            json_path,
            default={},
            context="Loading quests",
            warn_on_missing=True
        )

        self._definitions = {}
        for quest_data in data.get("quests", []):
            quest_id = quest_data["id"]
            self._definitions[quest_id] = quest_data
            self.quests[quest_id] = Quest.from_definition(quest_data)

        # Rebuild indexes after loading
        self._rebuild_indexes()

    def add_quest(self, quest: Quest) -> None:
        """Add a quest and rebuild indexes.

        This method should be used when programmatically adding quests at runtime
        (e.g., in tests or dynamic quest generation). It ensures the objective
        indexes are properly updated.

        Args:
            quest: Quest instance to add
        """
        self.quests[quest.id] = quest
        self._rebuild_indexes()

    def get_quest(self, quest_id: str) -> Optional[Quest]:
        """Get a quest by ID."""
        return self.quests.get(quest_id)

    def get_quests_by_status(self, status: QuestStatus) -> List[Quest]:
        """Get all quests with a specific status."""
        return [q for q in self.quests.values() if q.status == status]

    def get_active_quests(self) -> List[Quest]:
        """Get all active quests."""
        return self.get_quests_by_status(QuestStatus.ACTIVE)

    def get_completed_quests(self) -> List[Quest]:
        """Get all completed quests."""
        return self.get_quests_by_status(QuestStatus.COMPLETED)

    def get_available_quests(self) -> List[Quest]:
        """Get all available (can be started) quests."""
        return self.get_quests_by_status(QuestStatus.AVAILABLE)

    def get_tracked_quest(self) -> Optional[Quest]:
        """Get the currently tracked quest, if any."""
        for quest in self.get_active_quests():
            if quest.tracked:
                return quest
        return None

    def set_tracked_quest(self, quest_id: str) -> bool:
        """Set a quest as tracked, untracking others. Returns True if successful."""
        target = self.quests.get(quest_id)
        if not target or target.status != QuestStatus.ACTIVE:
            return False
        for quest in self.quests.values():
            quest.tracked = (quest.id == quest_id)
        return True

    def untrack_all_quests(self) -> None:
        """Untrack all quests."""
        for quest in self.quests.values():
            quest.tracked = False

    def start_quest(self, quest_id: str) -> bool:
        """Start a quest, changing status from AVAILABLE/LOCKED to ACTIVE.

        This method activates a quest, making it trackable and allowing
        objectives to be updated. The quest must be in AVAILABLE or LOCKED
        status to be started.

        Args:
            quest_id: ID of the quest to start

        Returns:
            True if quest was successfully started, False if quest doesn't
            exist or is not in a startable state

        Note:
            Starting a LOCKED quest bypasses prerequisite checks. This is
            intentional for special cases (e.g., tutorial quests that start
            automatically). Normally, quests should be AVAILABLE before starting.
        """
        quest = self.quests.get(quest_id)
        if not quest:
            return False
        if quest.status not in (QuestStatus.AVAILABLE, QuestStatus.LOCKED):
            return False
        quest.status = QuestStatus.ACTIVE
        self._rebuild_indexes()  # Rebuild indexes when quest becomes active
        return True

    def complete_quest(self, quest_id: str) -> Optional[Quest]:
        """Mark a quest as completed and return it for reward processing.

        This method validates that a quest is complete (all non-optional
        objectives done) and changes status from ACTIVE to COMPLETED.

        Args:
            quest_id: ID of the quest to complete

        Returns:
            Quest instance if successfully completed, None if quest doesn't
            exist, isn't active, or isn't complete

        The returned quest can be used to:
        - Award rewards (gold, EXP, items, flags, recipes)
        - Check for class/subclass-specific rewards
        - Trigger quest completion events
        - Update quest tracking UI

        Note:
            This method only changes status. Reward distribution should be
            handled by the caller using the returned quest's reward fields.
        """
        quest = self.quests.get(quest_id)
        if not quest or quest.status != QuestStatus.ACTIVE:
            return None
        if not quest.is_complete():
            return None
        quest.status = QuestStatus.COMPLETED
        self._rebuild_indexes()  # Rebuild indexes when quest becomes inactive
        return quest

    def fail_quest(self, quest_id: str) -> bool:
        """Mark a quest as failed."""
        quest = self.quests.get(quest_id)
        if not quest or quest.status != QuestStatus.ACTIVE:
            return False
        quest.status = QuestStatus.FAILED
        self._rebuild_indexes()  # Rebuild indexes when quest becomes inactive
        return True

    def update_objective(self, quest_id: str, objective_id: str, amount: int = 1) -> bool:
        """Update a quest objective's progress.

        This method increments an objective's current_count and checks if
        it's complete. If the objective reaches required_count, it's marked
        as completed. The method then checks if the entire quest is complete.

        Args:
            quest_id: ID of the quest containing the objective
            objective_id: ID of the objective to update
            amount: Amount to increment progress (default 1)

        Returns:
            True if the quest is now complete (all non-optional objectives done),
            False otherwise

        This is a lower-level method. Higher-level methods like on_enemy_killed()
        and on_item_collected() use this internally. Direct use is typically
        only needed for custom objective types.
        """
        quest = self.quests.get(quest_id)
        if not quest or quest.status != QuestStatus.ACTIVE:
            return False
        return quest.update_objective(objective_id, amount)

    def check_prerequisites(self, world_flags: Dict[str, Any]) -> List[str]:
        """Check all locked quests for prerequisites and unlock if met.

        This method evaluates prerequisites for all locked quests and unlocks
        them when conditions are met. Prerequisites include:
        - Required flags: World flags that must be set
        - Required quests: Quest IDs that must be completed

        Both conditions must be met for a quest to unlock. When unlocked,
        quest status changes from LOCKED to AVAILABLE.

        Args:
            world_flags: Dictionary of world flags (flag_name -> value)

        Returns:
            List of quest IDs that were newly unlocked (changed from LOCKED
            to AVAILABLE)

        Example:
            If quest requires flags ["cave_cleared", "key_found"] and quest
            ["tutorial_quest"] to be completed:
            - All flags must be True in world_flags
            - "tutorial_quest" must be in completed quests
            - If both met, quest unlocks and ID added to return list

        This method should be called periodically (e.g., after quest completion,
        flag changes, or map transitions) to unlock new quests.
        """
        newly_available = []
        completed_ids = {q.id for q in self.get_completed_quests()}

        for quest in self.quests.values():
            if quest.status != QuestStatus.LOCKED:
                continue

            # Check required flags
            flags_met = all(world_flags.get(flag) for flag in quest.required_flags)

            # Check required quests
            quests_met = all(qid in completed_ids for qid in quest.required_quests)

            if flags_met and quests_met:
                quest.status = QuestStatus.AVAILABLE
                newly_available.append(quest.id)

        return newly_available

    def check_flag_objectives(self, world_flags: Dict[str, Any]) -> List[str]:
        """Check all active quests for flag-based objective completion.

        This method checks only flags that are set in world_flags and uses
        indexed lookups to find matching objectives. If a flag is set and matches
        an objective's target, the objective is marked as completed.

        Args:
            world_flags: Dictionary of world flags (flag_name -> value)

        Returns:
            List of quest IDs that had at least one objective updated
            (not necessarily completed - includes partial progress)

        Flag-based objectives are useful for:
        - Story progression flags (e.g., "boss_defeated")
        - Exploration flags (e.g., "ancient_ruins_discovered")
        - Choice flags (e.g., "spared_enemy", "killed_enemy")

        This method should be called on map transitions and when flags change,
        not every frame. Unlike other objective types that are event-driven,
        flag objectives require polling but are now optimized with indexes.
        """
        updated_quests = []
        # Only check flags that are actually set (truthy values)
        for flag_name, flag_value in world_flags.items():
            if not flag_value:
                continue  # Skip unset flags

            # Use indexed lookup instead of iterating all quests
            objectives = self._flag_objectives_by_flag.get(flag_name, [])
            for quest_id, obj_id in objectives:
                quest = self.quests.get(quest_id)
                if not quest or quest.status != QuestStatus.ACTIVE:
                    continue
                obj = quest.get_objective(obj_id)
                if obj and not obj.completed:
                    obj.set_completed()
                    if quest_id not in updated_quests:
                        updated_quests.append(quest_id)

        return updated_quests

    def on_enemy_killed(self, enemy_type: str, return_progress: bool = False) -> List[Any]:
        """
        Called when an enemy is killed. Updates relevant kill objectives.

        Args:
            enemy_type: The type/ID of the enemy that was killed.
            return_progress: If True, returns detailed progress info instead of just quest IDs.

        Returns:
            If return_progress is False (default):
                List of quest IDs where at least one objective was newly completed
                (not quests that were merely updated without completing an objective).
            If return_progress is True:
                List of dicts with keys: quest_name, objective_desc, current, required, completed
                for each objective that was updated (whether completed or not).
        """
        # Use indexed lookup instead of iterating all quests
        objectives = self._kill_objectives_by_target.get(enemy_type, [])

        if return_progress:
            progress_info = []
            for quest_id, obj_id in objectives:
                quest = self.quests.get(quest_id)
                if not quest or quest.status != QuestStatus.ACTIVE:
                    continue
                obj = quest.get_objective(obj_id)
                if not obj or obj.completed:
                    continue
                was_completed = obj.update_progress(1)
                progress_info.append({
                    "quest_name": quest.name,
                    "objective_desc": obj.description,
                    "current": obj.current_count,
                    "required": obj.required_count,
                    "completed": was_completed,
                })
            return progress_info
        else:
            updated = []
            for quest_id, obj_id in objectives:
                quest = self.quests.get(quest_id)
                if not quest or quest.status != QuestStatus.ACTIVE:
                    continue
                obj = quest.get_objective(obj_id)
                if obj and not obj.completed:
                    if obj.update_progress(1):
                        if quest_id not in updated:
                            updated.append(quest_id)
            return updated

    def on_item_collected(self, item_id: str, amount: int = 1) -> List[str]:
        """
        Called when an item is collected. Updates relevant collect objectives.

        Args:
            item_id: The ID of the item collected.
            amount: Number of items collected (default 1).

        Returns:
            List of quest IDs where at least one objective was newly completed
            (not quests that were merely updated without completing an objective).
        """
        # Use indexed lookup instead of iterating all quests
        objectives = self._collect_objectives_by_item.get(item_id, [])
        updated = []
        for quest_id, obj_id in objectives:
            quest = self.quests.get(quest_id)
            if not quest or quest.status != QuestStatus.ACTIVE:
                continue
            obj = quest.get_objective(obj_id)
            if obj and not obj.completed:
                if obj.update_progress(amount):
                    if quest_id not in updated:
                        updated.append(quest_id)
        return updated

    def on_npc_talked(self, npc_id: str) -> List[str]:
        """
        Called when player talks to an NPC. Updates relevant talk objectives.

        Args:
            npc_id: The ID of the NPC talked to.

        Returns:
            List of quest IDs where at least one objective was newly completed
            (not quests that were merely updated without completing an objective).
        """
        # Use indexed lookup instead of iterating all quests
        objectives = self._talk_objectives_by_npc.get(npc_id, [])
        updated = []
        for quest_id, obj_id in objectives:
            quest = self.quests.get(quest_id)
            if not quest or quest.status != QuestStatus.ACTIVE:
                continue
            obj = quest.get_objective(obj_id)
            if obj and not obj.completed:
                if obj.update_progress(1):
                    if quest_id not in updated:
                        updated.append(quest_id)
        return updated

    def on_map_entered(self, map_id: str) -> List[str]:
        """
        Called when player enters a map. Updates relevant reach objectives.

        Args:
            map_id: The ID of the map entered.

        Returns:
            List of quest IDs where at least one objective was newly completed
            (not quests that were merely updated without completing an objective).
        """
        # Use indexed lookup instead of iterating all quests
        objectives = self._reach_objectives_by_map.get(map_id, [])
        updated = []
        for quest_id, obj_id in objectives:
            quest = self.quests.get(quest_id)
            if not quest or quest.status != QuestStatus.ACTIVE:
                continue
            obj = quest.get_objective(obj_id)
            if obj and not obj.completed:
                if obj.update_progress(1):
                    if quest_id not in updated:
                        updated.append(quest_id)
        return updated

    def check_failure_conditions(self, world_flags: Dict[str, Any]) -> List[str]:
        """Check all active quests for failure conditions.

        This method evaluates failure conditions for all active quests and
        marks them as FAILED if conditions are met. Failure conditions include:
        - fail_on_flags: World flags that cause failure if set
        - time_limit_turns: Turn count exceeded (checked separately via increment_quest_turns)
        - fail_on_npc_death: NPC death (checked separately via on_npc_death)

        Args:
            world_flags: Dictionary of world flags to check against fail_on_flags

        Returns:
            List of quest IDs that have failed (status changed to FAILED)

        This method should be called periodically (e.g., after flag changes)
        to check for quest failures. Time-based failures are handled separately
        by increment_quest_turns().
        """
        failed_quests = []
        for quest in self.get_active_quests():
            if quest.check_failure_conditions(world_flags):
                quest.status = QuestStatus.FAILED
                failed_quests.append(quest.id)
        return failed_quests

    def on_npc_death(self, npc_id: str) -> List[str]:
        """
        Called when an NPC dies. Fails quests that depend on that NPC.
        Returns list of quest IDs that have failed.
        """
        failed_quests = []
        for quest in self.get_active_quests():
            if quest.fail_on_npc_death == npc_id:
                quest.status = QuestStatus.FAILED
                failed_quests.append(quest.id)
        return failed_quests

    def increment_quest_turns(self) -> List[str]:
        """
        Increment turn counters for all timed quests.
        Returns list of quest IDs that have failed due to time limit.
        """
        failed_quests = []
        for quest in self.get_active_quests():
            if quest.increment_turn():
                quest.status = QuestStatus.FAILED
                failed_quests.append(quest.id)
        return failed_quests

    def get_quests_from_npc(self, npc_id: str) -> List[Quest]:
        """Get all available quests that this NPC gives."""
        return [
            q for q in self.quests.values()
            if q.giver_npc == npc_id and q.status == QuestStatus.AVAILABLE
        ]

    def get_turn_in_quests_for_npc(self, npc_id: str) -> List[Quest]:
        """
        Get all active quests that can be turned in to this NPC.

        A quest can be turned in if:
        - It's active and all objectives are complete
        - The turn_in_npc matches (or giver_npc if turn_in_npc is None)
        """
        turn_in_quests = []
        for quest in self.get_active_quests():
            if not quest.is_complete():
                continue
            turn_in_target = quest.turn_in_npc or quest.giver_npc
            if turn_in_target == npc_id:
                turn_in_quests.append(quest)
        return turn_in_quests

    def can_turn_in_quest(self, quest_id: str, npc_id: str) -> bool:
        """Check if a quest can be turned in to a specific NPC."""
        quest = self.quests.get(quest_id)
        if not quest or quest.status != QuestStatus.ACTIVE:
            return False
        if not quest.is_complete():
            return False
        turn_in_target = quest.turn_in_npc or quest.giver_npc
        return turn_in_target == npc_id

    def turn_in_quest(self, quest_id: str, npc_id: str) -> Optional[Quest]:
        """
        Turn in a completed quest to an NPC.

        Returns the quest if successful (for reward processing), None otherwise.
        """
        if not self.can_turn_in_quest(quest_id, npc_id):
            return None
        return self.complete_quest(quest_id)

    def serialize_state(self) -> Dict[str, Any]:
        """Serialize all quest states for saving."""
        return {
            "quests": [quest.to_dict() for quest in self.quests.values()]
        }

    # Saveable protocol methods
    def serialize(self) -> Dict[str, Any]:
        """Serialize state (Saveable protocol)."""
        return self.serialize_state()

    def deserialize_into(self, data: Dict[str, Any]) -> None:
        """Restore state from saved data (Saveable protocol)."""
        self.deserialize_state(data)

    def deserialize_state(self, data: Dict[str, Any]) -> None:
        """Restore quest states from saved data."""
        quest_states = {q["id"]: q for q in data.get("quests", [])}

        for quest_id, quest in self.quests.items():
            if quest_id in quest_states:
                state = quest_states[quest_id]
                saved_status = state.get("status", quest.status.value)
                try:
                    quest.status = QuestStatus(saved_status)
                except ValueError:
                    log_warning(
                        f"Unknown quest status '{saved_status}' for quest {quest_id}, defaulting to locked"
                    )
                    quest.status = QuestStatus.LOCKED
                quest.tracked = state.get("tracked", False)
                quest.turns_elapsed = state.get("turns_elapsed", 0)

                # Restore objective progress
                obj_states = {o["id"]: o for o in state.get("objectives", [])}

                for obj in quest.objectives:
                    if obj.id in obj_states:
                        obj_state = obj_states[obj.id]
                        obj.current_count = obj_state.get("current_count", 0)
                        obj.completed = obj_state.get("completed", False)

        # Rebuild indexes after deserializing state
        self._rebuild_indexes()


def load_quest_manager(json_path: str = "data/quests.json") -> QuestManager:
    """Load and return a QuestManager with quests from JSON."""
    manager = QuestManager()
    manager.load_quests(json_path)
    return manager

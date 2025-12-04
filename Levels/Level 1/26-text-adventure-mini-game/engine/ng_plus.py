"""New Game+ data creation and persistence management.

This module handles the creation of New Game+ save data and the management
of NG+ state transitions, separating NG+ logic from the main scene.
"""

import json
import os
from typing import Dict, List, Optional, TYPE_CHECKING

from core.logging_utils import log_warning, log_error

if TYPE_CHECKING:
    from core.world import World
    from core.entities import Player
    from core.save_load import SaveManager


class NewGamePlusManager:
    """Manages New Game+ data creation and save operations.

    Handles:
    - NG+ data structure creation
    - Save file generation for NG+ cycles
    - Menu selection handling
    - Stat bonus calculations
    - Ending tracking across cycles
    """

    def __init__(
        self,
        world: "World",
        player: "Player",
        save_manager: Optional["SaveManager"] = None,
    ):
        """Initialize the NG+ manager.

        Args:
            world: World instance for flag access
            player: Player instance for stats and inventory
            save_manager: Save manager for file operations
        """
        self.world = world
        self.player = player
        self.save_manager = save_manager

        # Menu state
        self.selected_option = 0  # 0 = New Game+, 1 = Return to Title
        self.available = True

    def create_ng_plus_data(self) -> Dict:
        """Create New Game+ save data with carried over progress.

        Returns:
            Dictionary containing NG+ save data structure
        """
        current_cycle = self.world.get_flag("ng_plus_cycle")
        if not isinstance(current_cycle, int):
            current_cycle = 0
        new_cycle = current_cycle + 1

        carry_over = {
            "level": self.player.stats.level if self.player.stats else 1,
            "skills": list(getattr(self.player, "learned_moves", [])),
            "inventory": {},
            "equipment": dict(getattr(self.player, "equipment", {})),
            "endings_seen": [],
            "ng_plus_cycle": new_cycle,
            "ng_plus_stat_bonus": min(new_cycle * 5, 25),
        }

        # Carry over limited inventory items
        if self.player.inventory:
            for item_id, qty in self.player.inventory.get_all_items().items():
                carry_over["inventory"][item_id] = min(qty, 10)

        # Track seen endings
        for ending_type in ["good", "bad", "neutral"]:
            if self.world.get_flag(f"ending_{ending_type}_seen"):
                carry_over["endings_seen"].append(ending_type)

        return carry_over

    def save_ng_plus_state(self, slot: int, ng_plus_data: Dict) -> None:
        """Save New Game+ state to a slot.

        Args:
            slot: Save slot number
            ng_plus_data: NG+ data structure from create_ng_plus_data()

        Raises:
            Exception: If save file cannot be written
        """
        if not self.save_manager:
            raise Exception("No save manager available")

        save_path = os.path.join(self.save_manager.save_dir, f"save_{slot}.json")

        bonus = ng_plus_data["ng_plus_stat_bonus"]
        ng_save = {
            "world": {
                "current_map_id": "forest_path",
                "flags": {
                    "new_game_plus": True,
                    "ng_plus_cycle": ng_plus_data["ng_plus_cycle"],
                    "ng_plus_stat_bonus": bonus,
                    **{f"ending_{e}_seen": True for e in ng_plus_data["endings_seen"]},
                }
            },
            "player": {
                "entity_id": self.player.entity_id,
                "name": self.player.name,
                "x": 7,
                "y": 7,
                "inventory": ng_plus_data["inventory"],
                "equipment": ng_plus_data["equipment"],
                "skills": ng_plus_data["skills"],
                "learned_moves": ng_plus_data["skills"],
                "stats": {
                    "max_hp": 100 + bonus * 2,
                    "hp": 100 + bonus * 2,
                    "max_sp": 30 + bonus,
                    "sp": 30 + bonus,
                    "attack": 10 + bonus,
                    "defense": 8 + bonus,
                    "magic": 8 + bonus,
                    "speed": 10 + bonus // 2,
                    "luck": 5 + bonus // 2,
                    "level": 1,
                    "exp": 0,
                    "status_effects": {}
                },
                "party": [],
                "skill_tree_progress": None,
                "player_class": getattr(self.player, "player_class", None),
                "player_subclass": getattr(self.player, "player_subclass", None)
            }
        }

        try:
            with open(save_path, 'w') as f:
                json.dump(ng_save, f, indent=2)
        except Exception as e:
            log_error(f"Failed to write New Game+ save to {save_path}: {e}")
            raise

    def start_new_game_plus(self, slot: int) -> str:
        """Initialize New Game+ mode.

        Args:
            slot: Save slot to use for NG+ save

        Returns:
            Status message about the operation
        """
        if not self.save_manager:
            return "No save manager available"

        try:
            ng_plus_data = self.create_ng_plus_data()
            self.save_ng_plus_state(slot, ng_plus_data)
            self.world.set_flag("new_game_plus_pending", True)
            return f"New Game+ saved to slot {slot}"
        except Exception as e:
            log_warning(f"Failed to create New Game+ save: {e}")
            return "Failed to create New Game+"

    def handle_menu_navigation(self, direction: str) -> None:
        """Handle NG+ menu navigation.

        Args:
            direction: "up" or "down" for menu navigation
        """
        if direction == "up":
            self.selected_option = (self.selected_option - 1) % 2
        elif direction == "down":
            self.selected_option = (self.selected_option + 1) % 2

    def handle_menu_selection(self, slot: int) -> tuple[bool, str]:
        """Handle NG+ menu selection.

        Args:
            slot: Save slot to use if NG+ is selected

        Returns:
            Tuple of (should_quit, message)
        """
        if self.selected_option == 0:
            # New Game+ selected
            message = self.start_new_game_plus(slot)
            return True, message
        else:
            # Return to Title selected
            return True, "Returning to title"

    def get_current_cycle_info(self) -> str:
        """Get formatted current NG+ cycle information.

        Returns:
            Formatted string showing current cycle, or empty if not in NG+
        """
        ng_cycle = self.world.get_flag("ng_plus_cycle")
        if isinstance(ng_cycle, int) and ng_cycle > 0:
            return f"NG+ Cycle {ng_cycle}"
        return ""

    def get_menu_options(self) -> List[str]:
        """Get the menu options for NG+ selection.

        Returns:
            List of menu option strings
        """
        return ["New Game+", "Return to Title"]

    def is_new_game_plus_selected(self) -> bool:
        """Check if New Game+ option is currently selected.

        Returns:
            True if NG+ option is selected, False if Return to Title
        """
        return self.selected_option == 0

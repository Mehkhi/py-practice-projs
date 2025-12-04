"""Coordinate save/load operations for the RPG game."""

from typing import TYPE_CHECKING

from core.logging_utils import log_warning, log_error
from core.save import SaveContext

if TYPE_CHECKING:
    from engine.scene import SceneManager
    from core.save_load import SaveManager
    # Note: RpgGame is not imported to avoid circular dependency with engine.game
    # The string literal annotation "RpgGame" is sufficient for type checking


class SaveCoordinator:
    """Handles save slot selection, saving, and loading for the game."""

    def __init__(self, game: "RpgGame", save_manager: "SaveManager"):
        self.game = game
        self.save_manager = save_manager

    def open_load_slot_selection(self) -> None:
        """Open the save slot selection scene for loading."""
        from .save_slot_scene import SaveSlotScene
        from .assets import AssetManager

        current_scene = self.game.scene_manager.current() if self.game.scene_manager else None
        assets = getattr(current_scene, "assets", None)
        if assets is None:
            assets = AssetManager(
                scale=self.game.scale,
                tile_size=self.game.tile_size,
                sprite_size=self.game.sprite_size,
                preload_common=False,
            )

        def on_load_complete(slot: int) -> bool:
            return self.load_from_slot(slot)

        load_scene = SaveSlotScene(
            self.game.scene_manager,
            self.save_manager,
            mode="load",
            on_complete=on_load_complete,
            assets=assets,
            scale=self.game.scale,
        )
        self.game.scene_manager.push(load_scene)

    def save_current_slot(self) -> None:
        """Persist the current game state to the active save slot."""
        try:
            context = SaveContext.from_game(self.game)
            self.save_manager.save_to_slot_with_context(self.game.save_slot, context)
        except (OSError, ValueError, KeyError, AttributeError) as exc:
            log_warning(f"Failed to create save profile for slot {self.game.save_slot}: {exc}")
        except Exception as exc:
            log_error(f"Unexpected error saving to slot {self.game.save_slot}: {exc}")

    def load_from_slot(self, slot: int) -> bool:
        """Load saved game from a specific slot and transition to world scene."""
        from .world_scene import WorldScene

        try:
            context = SaveContext.from_game(self.game)
            self.game.player = self.save_manager.load_from_slot_with_context(slot, context)
            self.game.save_slot = slot

            if self.game.quest_manager:
                self.game.quest_manager.check_prerequisites(self.game.world.flags)

            if self.game.encounters_data and hasattr(self.game.player, 'bestiary'):
                self.game.player.bestiary.seed_from_encounter_data(
                    self.game.encounters_data,
                    metadata=self.game.bestiary_metadata,
                )

            world_scene = WorldScene(
                self.game.scene_manager,
                self.game.world,
                self.game.player,
                dialogue_tree=self.game.dialogue_tree,
                items_db=self.game.items_db,
                scale=self.game.scale,
                quest_manager=self.game.quest_manager,
                save_manager=self.save_manager,
                save_slot=slot,
                encounters_data=self.game.encounters_data,
            )
            self.game.scene_manager.replace(world_scene)
            return True
        except (OSError, ValueError, KeyError, AttributeError, FileNotFoundError) as exc:
            log_warning(f"Failed to load save from slot {slot}: {exc}")
            return False
        except Exception as exc:
            log_error(f"Unexpected error loading save from slot {slot}: {exc}")
            return False

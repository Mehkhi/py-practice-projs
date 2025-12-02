"""Shop scene for merchants with buy/sell functionality and shop types."""

import json
import os
from typing import Dict, List, Optional, Tuple

import pygame

from .base_menu_scene import BaseMenuScene
from .assets import AssetManager
from .ui import Menu, MessageBox, NineSlicePanel, draw_contextual_help, EquipmentComparisonPanel, get_equipped_item_for_slot
from .theme import Colors, Fonts, Layout
from core.world import World
from core.entities import Player
from core.items import Item
from core.logging_utils import log_warning
from core.tutorial_system import TipTrigger

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .scene import SceneManager
    from core.quests import QuestManager


# Shop type definitions - determines which item types are sold
SHOP_TYPES = {
    "general": ["consumable", "equipment", "key"],  # Sells everything
    "weapon": ["equipment"],  # Only equipment with equip_slot="weapon"
    "armor": ["equipment"],   # Only equipment with equip_slot="armor" or "accessory"
    "item": ["consumable"],   # Only consumables
    "blacksmith": ["equipment"],  # Weapons and armor
    "potion": ["consumable"],  # Potions and consumables
    "fishing": ["consumable", "equipment"],  # Fishing supplies (bait, rods, etc.)
}

# Sell price multiplier (items sell for this fraction of their value)
SELL_PRICE_MULTIPLIER = 0.5


class ShopScene(BaseMenuScene):
    """Allows buying and selling items from a merchant NPC."""

    # Shop modes
    MODE_MAIN = "main"
    MODE_BUY = "buy"
    MODE_SELL = "sell"

    def __init__(
        self,
        manager: Optional["SceneManager"],
        world: World,
        player: Player,
        items_db: Dict[str, Item],
        stock: Dict[str, int],
        assets: Optional[AssetManager] = None,
        scale: int = 2,
        title: str = "Shop",
        shop_type: str = "general",
        shop_id: Optional[str] = None,
        restock_interval: Optional[int] = None,  # In-game days until restock
        base_stock: Optional[Dict[str, int]] = None,  # Original stock for restocking
        quest_manager: Optional["QuestManager"] = None,
    ):
        super().__init__(manager, assets, scale)
        self.world = world
        self.player = player
        self.items_db = items_db
        self.stock: Dict[str, int] = stock
        self.title = title
        self.shop_type = shop_type
        self.shop_id = shop_id or title.lower().replace(" ", "_")
        self.restock_interval = restock_interval
        self.base_stock = base_stock or dict(stock)  # Copy for restocking
        self.quest_manager = quest_manager
        self.fish_buyer_bonus = 1.0  # Default no bonus

        # Mode management
        self.mode = self.MODE_MAIN
        self.menu_mapping: Dict[int, str] = {}
        self.menu: Optional[Menu] = None

        self.message_box = MessageBox(
            position=(Layout.PADDING_LARGE, 320),
            width=Layout.SCREEN_WIDTH - Layout.PADDING_LARGE * 2,
            height=140
        )

        # Equipment comparison panel for buy mode
        self.comparison_panel = EquipmentComparisonPanel(width=240)

        # Load persisted stock from world flags (if any)
        self._load_persisted_stock()

        # Check and apply restocking if needed
        self._check_restock()

        self.message_box.set_text("Welcome! What would you like to do?")
        self._refresh_main_menu()

        # Trigger FIRST_SHOP_VISIT tip
        tutorial_manager = self.get_manager_attr(
            "tutorial_manager", "__init__"
        )
        if tutorial_manager:
            tutorial_manager.trigger_tip(TipTrigger.FIRST_SHOP_VISIT)

    def _gold(self) -> int:
        """Get current gold from world flags."""
        value = self.world.get_flag("gold", 0)
        try:
            return int(value)
        except Exception:
            return 0

    def _set_gold(self, amount: int) -> None:
        """Persist gold amount back into world flags."""
        self.world.set_flag("gold", max(0, int(amount)))

    def _get_game_day(self) -> int:
        """Get current in-game day from world flags."""
        return int(self.world.get_flag("game_day", 0))

    def _get_stock_flag_key(self) -> str:
        """Get the world flag key for this shop's persisted stock."""
        return f"shop_{self.shop_id}_stock"

    def _load_persisted_stock(self) -> None:
        """Load persisted stock from world flags if available."""
        stock_key = self._get_stock_flag_key()
        persisted = self.world.get_flag(stock_key)
        if persisted and isinstance(persisted, dict):
            # Merge persisted stock into current stock (persisted values override)
            for item_id, qty in persisted.items():
                if item_id in self.stock:
                    self.stock[item_id] = qty

    def _save_persisted_stock(self) -> None:
        """Save current stock to world flags for persistence."""
        stock_key = self._get_stock_flag_key()
        # Only save items that differ from base stock or have been purchased
        self.world.set_flag(stock_key, dict(self.stock))

    def _check_restock(self) -> None:
        """Check if shop should restock and apply if needed."""
        if not self.restock_interval or self.restock_interval <= 0:
            return

        last_restock_key = f"shop_{self.shop_id}_last_restock"
        last_restock = int(self.world.get_flag(last_restock_key, 0))
        current_day = self._get_game_day()

        if current_day - last_restock >= self.restock_interval:
            # Restock: restore base stock quantities
            for item_id, base_qty in self.base_stock.items():
                current_qty = self.stock.get(item_id, 0)
                # Add back up to base quantity
                self.stock[item_id] = max(current_qty, base_qty)
            self.world.set_flag(last_restock_key, current_day)
            # Persist the restocked values
            self._save_persisted_stock()

    def _item_matches_shop_type(self, item: Item) -> bool:
        """Check if an item matches this shop's type for buying."""
        allowed_types = SHOP_TYPES.get(self.shop_type, SHOP_TYPES["general"])

        if item.item_type not in allowed_types:
            return False

        # Additional filtering for weapon/armor shops
        if self.shop_type == "weapon":
            return item.equip_slot == "weapon"
        elif self.shop_type == "armor":
            return item.equip_slot in ("armor", "accessory")

        return True

    def _get_sell_price(self, item: Item) -> int:
        """Calculate sell price for an item."""
        price = item.value * SELL_PRICE_MULTIPLIER
        if item.item_type == "fish":
            price *= self.fish_buyer_bonus
        return max(1, int(round(price)))

    def _refresh_main_menu(self) -> None:
        """Show the main Buy/Sell/Leave menu."""
        self.mode = self.MODE_MAIN
        self.menu_mapping.clear()
        options = ["Buy", "Sell", "Leave"]
        self.menu = Menu(options, position=(360, 200))
        self.message_box.set_text("Welcome! What would you like to do?")

    def _refresh_buy_menu(self) -> None:
        """Refresh menu options for buying based on remaining stock."""
        self.mode = self.MODE_BUY
        options = []
        self.menu_mapping.clear()
        idx = 0
        for item_id, qty in self.stock.items():
            if qty <= 0:
                continue
            item = self.items_db.get(item_id)
            if not item:
                continue
            # Filter by shop type
            if not self._item_matches_shop_type(item):
                continue
            label = item.name if item else item_id
            price = item.value if item else 0
            options.append(f"{label} ({price}g) x{qty}")
            self.menu_mapping[idx] = item_id
            idx += 1
        options.append("Back")
        self.menu = Menu(options, position=(360, 150))
        if len(options) == 1:  # Only "Back"
            self.message_box.set_text("Nothing available for purchase.")
        else:
            self.message_box.set_text("Select an item to buy. Press ESC to go back.")

        # Update comparison panel for initial selection
        self._update_comparison_panel()

    def _refresh_sell_menu(self) -> None:
        """Refresh menu options for selling based on player inventory."""
        self.mode = self.MODE_SELL
        options = []
        self.menu_mapping.clear()
        idx = 0

        if self.player.inventory:
            for item_id, qty in self.player.inventory.get_all_items().items():
                if qty <= 0:
                    continue
                item = self.items_db.get(item_id)
                if not item:
                    continue
                # Don't allow selling key items
                if item.item_type == "key":
                    continue
                sell_price = self._get_sell_price(item)
                options.append(f"{item.name} ({sell_price}g) x{qty}")
                self.menu_mapping[idx] = item_id
                idx += 1

        options.append("Back")
        self.menu = Menu(options, position=(360, 150))
        if len(options) == 1:  # Only "Back"
            self.message_box.set_text("You have nothing to sell.")
        else:
            self.message_box.set_text("Select an item to sell. Press ESC to go back.")

    def _handle_purchase(self, item_id: str) -> None:
        """Process a purchase attempt for a given item."""
        item = self.items_db.get(item_id)
        price = item.value if item else 0
        current_gold = self._gold()

        if self.stock.get(item_id, 0) <= 0:
            self.message_box.set_text("Sold out. This item is no longer available.")
            self._refresh_buy_menu()
            return

        if current_gold < price:
            self.message_box.set_text(f"Not enough gold. You need {price}g but only have {current_gold}g.")
            return

        self._set_gold(current_gold - price)
        # Notify achievement system of gold change (spending gold)
        if self.manager and getattr(self.manager, "event_bus", None):
            self.manager.event_bus.publish("gold_changed", total_gold=self._gold())
        if self.player.inventory:
            self.player.inventory.add(item_id, 1)
            # Update quest objectives for item collection (purchases count as collection)
            if self.quest_manager:
                self.quest_manager.on_item_collected(item_id, 1)
        self.stock[item_id] -= 1
        if self.stock[item_id] <= 0:
            self.stock[item_id] = 0
        # Persist stock changes to world flags
        self._save_persisted_stock()
        self._refresh_buy_menu()
        item_name = item.name if item else item_id
        self.message_box.set_text(f"Bought {item_name}! Gold remaining: {self._gold()}")

    def _handle_sale(self, item_id: str) -> None:
        """Process a sale attempt for a given item."""
        item = self.items_db.get(item_id)
        if not item:
            self.message_box.set_text("Unknown item.")
            return

        if not self.player.inventory or not self.player.inventory.has(item_id):
            self.message_box.set_text("You don't have that item in your inventory.")
            self._refresh_sell_menu()
            return

        sell_price = self._get_sell_price(item)

        # Remove from player inventory
        self.player.inventory.remove(item_id, 1)

        # Add gold to player
        self._set_gold(self._gold() + sell_price)
        # Notify achievement system of gold change (earning gold from sale)
        if self.manager and getattr(self.manager, "event_bus", None):
            self.manager.event_bus.publish("gold_changed", total_gold=self._gold())

        # Optionally add to shop stock (shop buys items from player)
        if item_id in self.stock:
            self.stock[item_id] += 1
        # Persist stock changes to world flags
        self._save_persisted_stock()

        self._refresh_sell_menu()

        # Show bonus message for fish at fisherman shop
        bonus_text = ""
        if item.item_type == "fish" and self.fish_buyer_bonus > 1.0:
            bonus_text = " (Fishing shop bonus!)"

        self.message_box.set_text(f"Sold {item.name} for {sell_price}g{bonus_text}! Gold: {self._gold()}")

    def _handle_selection(self) -> None:
        """Handle menu selection based on current mode."""
        if not self.menu:
            return

        selected_idx = self.menu.selected_index
        selected_option = self.menu.get_selected()

        if self.mode == self.MODE_MAIN:
            if selected_option == "Buy":
                self._refresh_buy_menu()
            elif selected_option == "Sell":
                self._refresh_sell_menu()
            elif selected_option == "Leave":
                self.manager.pop()

        elif self.mode == self.MODE_BUY:
            # Last option is always "Back"
            if selected_idx == len(self.menu.options) - 1:
                self._refresh_main_menu()
                return
            item_id = self.menu_mapping.get(selected_idx)
            if item_id:
                self._handle_purchase(item_id)

        elif self.mode == self.MODE_SELL:
            # Last option is always "Back"
            if selected_idx == len(self.menu.options) - 1:
                self._refresh_main_menu()
                return
            item_id = self.menu_mapping.get(selected_idx)
            if item_id:
                self._handle_sale(item_id)

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle input for menu navigation and buying/selling."""
        if event.type != pygame.KEYDOWN or not self.menu:
            return

        if event.key == pygame.K_UP:
            self.menu.move_selection(-1)
            self._update_comparison_panel()
        elif event.key == pygame.K_DOWN:
            self.menu.move_selection(1)
            self._update_comparison_panel()
        elif event.key == pygame.K_ESCAPE:
            if self.mode == self.MODE_MAIN:
                self.manager.pop()
            else:
                self._refresh_main_menu()
        elif event.key == pygame.K_RETURN:
            self._handle_selection()

    def _update_comparison_panel(self) -> None:
        """Update the comparison panel based on current selection."""
        if self.mode != self.MODE_BUY or not self.menu:
            self.comparison_panel.set_items(None, None)
            return

        selected_idx = self.menu.selected_index
        item_id = self.menu_mapping.get(selected_idx)

        if not item_id:
            self.comparison_panel.set_items(None, None)
            return

        new_item = self.items_db.get(item_id)
        if not new_item or new_item.item_type != "equipment":
            self.comparison_panel.set_items(None, None)
            return

        # Get currently equipped item for this slot
        current_item = get_equipped_item_for_slot(
            self.player, new_item.equip_slot, self.items_db
        )

        self.comparison_panel.set_items(current_item, new_item)

    def update(self, dt: float) -> None:
        """Shop scene has no per-frame logic."""
        return

    def draw(self, surface: pygame.Surface) -> None:
        """Render shop menu and info."""
        surface.fill(Colors.BG_MAIN)

        # Draw decorative header background
        header_rect = pygame.Rect(0, 0, surface.get_width(), 100)
        pygame.draw.rect(surface, Colors.BG_DARK, header_rect)
        pygame.draw.line(surface, Colors.BORDER, (0, 100), (surface.get_width(), 100), 2)

        font = self.assets.get_font(Fonts.DEFAULT, Fonts.SIZE_HEADING)
        small_font = self.assets.get_font(Fonts.SMALL, Fonts.SIZE_SMALL) or font

        if font:
            # Title with mode indicator
            mode_text = ""
            if self.mode == self.MODE_BUY:
                mode_text = " - Buy"
            elif self.mode == self.MODE_SELL:
                mode_text = " - Sell"

            # Draw title with shadow
            title_str = f"{self.title}{mode_text}"
            title_shadow = font.render(title_str, True, Colors.BLACK)
            title_surface = font.render(title_str, True, Colors.TEXT_PRIMARY)
            surface.blit(title_shadow, (22, 22))
            surface.blit(title_surface, (20, 20))

            # Gold display
            gold_surface = font.render(f"Gold: {self._gold()}", True, Colors.ACCENT)
            surface.blit(gold_surface, (20, 60))

            # Shop type indicator (for specialized shops)
            if self.shop_type != "general":
                type_label = self.shop_type.title() + " Shop"
                type_surface = small_font.render(type_label, True, Colors.TEXT_SECONDARY)
                surface.blit(type_surface, (surface.get_width() - type_surface.get_width() - 20, 20))

        if self.menu:
            self.menu.draw(
                surface,
                font or self.assets.get_font(),
                theme={
                    "active": Colors.TEXT_HIGHLIGHT,
                    "inactive": Colors.TEXT_SECONDARY,
                    "disabled": Colors.TEXT_DISABLED
            }
        )

        # Draw equipment comparison panel in buy mode
        if self.mode == self.MODE_BUY and self.comparison_panel.new_item:
            self.comparison_panel.draw(
                surface,
                x=20,
                y=110,
                font=small_font or self.assets.get_font(Fonts.DEFAULT)
            )

        self.message_box.draw(surface, small_font or self.assets.get_font(Fonts.DEFAULT), panel=getattr(self, 'panel', None))

        # Draw help text at bottom
        self._draw_help_text(surface, small_font or self.assets.get_font(Fonts.DEFAULT))

    def _draw_help_text(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        """Draw standardized help text at the bottom of the screen."""
        mode_labels = {
            self.MODE_MAIN: "Up/Down: Select | Enter: Confirm | ESC: Leave",
            self.MODE_BUY: "Up/Down: Select Item | Enter: Buy | ESC: Back",
            self.MODE_SELL: "Up/Down: Select Item | Enter: Sell | ESC: Back"
        }
        help_text = mode_labels.get(self.mode, "Up/Down: Navigate | Enter: Confirm | ESC: Back")
        draw_contextual_help(surface, help_text, font, margin_bottom=Layout.SCREEN_MARGIN)


def load_shops_from_json(path: str = os.path.join("data", "shops.json")) -> Dict[str, dict]:
    """
    Load shop definitions from JSON.

    Returns a dict mapping shop_id to shop config with keys:
        - name: Display name
        - shop_type: Type of shop (general, weapon, armor, item, etc.)
        - restock_interval: Days between restocks (optional)
        - stock: Dict of item_id -> quantity
    """
    shops: Dict[str, dict] = {}
    if not os.path.exists(path):
        return shops
    try:
        with open(path, "r") as f:
            data = json.load(f)
    except Exception as exc:
        log_warning(f"Failed to load shops from {path}: {exc}")
        return shops

    for shop_id, shop_data in data.get("shops", {}).items():
        shops[shop_id] = {
            "name": shop_data.get("name", shop_id),
            "shop_type": shop_data.get("shop_type", "general"),
            "restock_interval": shop_data.get("restock_interval"),
            "stock": shop_data.get("stock", {}),
            "fish_buyer_bonus": shop_data.get("fish_buyer_bonus", 1.0),
        }
    return shops


def validate_shop_items(shops_db: Dict[str, dict], items_db: Dict[str, Item]) -> List[str]:
    """
    Validate that all item IDs in shop stock exist in items database.

    Args:
        shops_db: Shop definitions from load_shops_from_json()
        items_db: Item database from load_items_from_json()

    Returns:
        List of warning messages for invalid item references (empty if all valid)
    """
    warnings = []
    for shop_id, shop_data in shops_db.items():
        for item_id in shop_data.get("stock", {}).keys():
            if item_id not in items_db:
                warnings.append(
                    f"Shop '{shop_id}' references unknown item_id: '{item_id}'"
                )
    return warnings


def create_shop_scene(
    manager,
    world: World,
    player: Player,
    items_db: Dict[str, Item],
    shop_id: str,
    shops_db: Optional[Dict[str, dict]] = None,
    assets: Optional[AssetManager] = None,
    scale: int = 2,
    quest_manager: Optional["QuestManager"] = None,
) -> Optional[ShopScene]:
    """
    Factory function to create a ShopScene from a shop_id.

    Args:
        manager: Scene manager
        world: World instance
        player: Player instance
        items_db: Item database
        shop_id: ID of the shop to create
        shops_db: Optional pre-loaded shops database
        assets: Optional asset manager
        scale: Display scale
        quest_manager: Optional quest manager for quest objective tracking

    Returns:
        ShopScene instance or None if shop_id not found
    """
    if shops_db is None:
        shops_db = load_shops_from_json()

    shop_config = shops_db.get(shop_id)
    if not shop_config:
        return None

    scene = ShopScene(
        manager=manager,
        world=world,
        player=player,
        items_db=items_db,
        stock=dict(shop_config["stock"]),  # Copy to avoid mutating original
        assets=assets,
        scale=scale,
        title=shop_config["name"],
        shop_type=shop_config["shop_type"],
        shop_id=shop_id,
        restock_interval=shop_config.get("restock_interval"),
        base_stock=dict(shop_config["stock"]),
        quest_manager=quest_manager,
    )
    # Set fish buyer bonus from shop config
    scene.fish_buyer_bonus = shop_config.get("fish_buyer_bonus", 1.0)
    return scene

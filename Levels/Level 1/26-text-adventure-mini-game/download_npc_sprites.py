# Download script for NPC Sprites
# Usage: Update the DOWNLOAD_URL variable and run this script

import os
import urllib.request

SPRITES_DIR = 'assets/sprites'
PORTRAITS_DIR = os.path.join(SPRITES_DIR, 'portraits')
os.makedirs(SPRITES_DIR, exist_ok=True)
os.makedirs(PORTRAITS_DIR, exist_ok=True)

# Update these with your download URL patterns
SPRITE_DOWNLOAD_URL = 'YOUR_SPRITE_URL_HERE/{filename}'
PORTRAIT_DOWNLOAD_URL = 'YOUR_PORTRAIT_URL_HERE/{filename}'

npcs = [
    {'name': 'Ancient Scholar', 'sprite_filename': 'npc_default.png', 'portrait_filename': 'portrait_ancient_scholar.png'},
    {'name': 'Archmage Seraphina', 'sprite_filename': 'npc_default.png', 'portrait_filename': 'portrait_archmage_seraphina.png'},
    {'name': 'Arena Bookkeeper', 'sprite_filename': 'npc_default.png', 'portrait_filename': 'portrait_arena_bookkeeper.png'},
    {'name': 'Arena Master Vex', 'sprite_filename': 'npc_default.png', 'portrait_filename': 'portrait_arena_master_vex.png'},
    {'name': 'Barnacle Bill', 'sprite_filename': 'npc_default.png', 'portrait_filename': 'portrait_barnacle_bill.png'},
    {'name': 'Bertha the Innkeeper', 'sprite_filename': 'npc_default.png', 'portrait_filename': 'portrait_bertha_the_innkeeper.png'},
    {'name': 'Bounty Board', 'sprite_filename': 'npc_default.png', 'portrait_filename': 'portrait_bounty_board.png'},
    {'name': 'Brock', 'sprite_filename': 'party_brock.png', 'portrait_filename': 'portrait_brock.png'},
    {'name': 'Bruno the Barkeep', 'sprite_filename': 'npc_default.png', 'portrait_filename': 'portrait_bruno_the_barkeep.png'},
    {'name': 'Brutus the Armorer', 'sprite_filename': 'npc_default.png', 'portrait_filename': 'portrait_brutus_the_armorer.png'},
    {'name': 'Captain Stormwind', 'sprite_filename': 'npc_default.png', 'portrait_filename': 'portrait_captain_stormwind.png'},
    {'name': 'Celeste the Hostess', 'sprite_filename': 'npc_default.png', 'portrait_filename': 'portrait_celeste_the_hostess.png'},
    {'name': 'Commander Steelheart', 'sprite_filename': 'npc_default.png', 'portrait_filename': 'portrait_commander_steelheart.png'},
    {'name': 'Desert Nomad', 'sprite_filename': 'npc_default.png', 'portrait_filename': 'portrait_desert_nomad.png'},
    {'name': 'Dusk the Barkeep', 'sprite_filename': 'npc_default.png', 'portrait_filename': 'portrait_dusk_the_barkeep.png'},
    {'name': 'Enchanter Rune', 'sprite_filename': 'npc_default.png', 'portrait_filename': 'portrait_enchanter_rune.png'},
    {'name': 'Forest Merchant', 'sprite_filename': 'npc_default.png', 'portrait_filename': 'portrait_forest_merchant.png'},
    {'name': 'Forge Master Grimm', 'sprite_filename': 'npc_default.png', 'portrait_filename': 'portrait_forge_master_grimm.png'},
    {'name': 'Garden Spirit', 'sprite_filename': 'npc_default.png', 'portrait_filename': 'portrait_garden_spirit.png'},
    {'name': 'Gerald the Trader', 'sprite_filename': 'npc_default.png', 'portrait_filename': 'portrait_gerald_the_trader.png'},
    {'name': 'Grimsby the Innkeeper', 'sprite_filename': 'npc_default.png', 'portrait_filename': 'portrait_grimsby_the_innkeeper.png'},
    {'name': 'Grizzled Miner', 'sprite_filename': 'npc_default.png', 'portrait_filename': 'portrait_grizzled_miner.png'},
    {'name': 'Gruff the Miner', 'sprite_filename': 'npc_default.png', 'portrait_filename': 'portrait_gruff_the_miner.png'},
    {'name': 'Helena the Shopkeeper', 'sprite_filename': 'npc_default.png', 'portrait_filename': 'portrait_helena_the_shopkeeper.png'},
    {'name': 'Hex the Potion Seller', 'sprite_filename': 'npc_default.png', 'portrait_filename': 'portrait_hex_the_potion_seller.png'},
    {'name': 'High Priest Solarius', 'sprite_filename': 'npc_default.png', 'portrait_filename': 'portrait_high_priest_solarius.png'},
    {'name': 'Keeper of Tomes', 'sprite_filename': 'npc_default.png', 'portrait_filename': 'portrait_keeper_of_tomes.png'},
    {'name': 'Lucky Lou', 'sprite_filename': 'npc_default.png', 'portrait_filename': 'portrait_lucky_lou.png'},
    {'name': 'Luna', 'sprite_filename': 'party_luna.png', 'portrait_filename': 'portrait_luna.png'},
    {'name': 'Marcus the Blacksmith', 'sprite_filename': 'npc_default.png', 'portrait_filename': 'portrait_marcus_the_blacksmith.png'},
    {'name': 'Marina the Hostess', 'sprite_filename': 'npc_default.png', 'portrait_filename': 'portrait_marina_the_hostess.png'},
    {'name': 'Martha the Innkeeper', 'sprite_filename': 'npc_default.png', 'portrait_filename': 'portrait_martha_the_innkeeper.png'},
    {'name': 'Master Angler', 'sprite_filename': 'npc_default.png', 'portrait_filename': 'portrait_master_angler.png'},
    {'name': 'Merchant Prince Aurelius', 'sprite_filename': 'npc_default.png', 'portrait_filename': 'portrait_merchant_prince_aurelius.png'},
    {'name': 'Mordecai the Alchemist', 'sprite_filename': 'npc_default.png', 'portrait_filename': 'portrait_mordecai_the_alchemist.png'},
    {'name': 'Mountain Traveler', 'sprite_filename': 'npc_default.png', 'portrait_filename': 'portrait_mountain_traveler.png'},
    {'name': 'Mysterious Wanderer', 'sprite_filename': 'npc_default.png', 'portrait_filename': 'portrait_mysterious_wanderer.png'},
    {'name': 'Mystica the Enchantress', 'sprite_filename': 'npc_default.png', 'portrait_filename': 'portrait_mystica_the_enchantress.png'},
    {'name': 'Old Fisher Tom', 'sprite_filename': 'npc_default.png', 'portrait_filename': 'portrait_old_fisher_tom.png'},
    {'name': 'Old Guide', 'sprite_filename': 'npc_old_guide.png', 'portrait_filename': 'portrait_old_guide.png'},
    {'name': 'Papyrus the Scribe', 'sprite_filename': 'npc_default.png', 'portrait_filename': 'portrait_papyrus_the_scribe.png'},
    {'name': 'Piper the Baker', 'sprite_filename': 'npc_default.png', 'portrait_filename': 'portrait_piper_the_baker.png'},
    {'name': 'Sage', 'sprite_filename': 'party_sage.png', 'portrait_filename': 'portrait_sage.png'},
    {'name': 'Shade the Hunter', 'sprite_filename': 'npc_default.png', 'portrait_filename': 'portrait_shade_the_hunter.png'},
    {'name': 'Silent Eye', 'sprite_filename': 'npc_default.png', 'portrait_filename': 'portrait_silent_eye.png'},
    {'name': 'The Shadow Broker', 'sprite_filename': 'npc_default.png', 'portrait_filename': 'portrait_the_shadow_broker.png'},
    {'name': 'Vex the Dealer', 'sprite_filename': 'npc_default.png', 'portrait_filename': 'portrait_vex_the_dealer.png'},
    {'name': 'Village Elder', 'sprite_filename': 'npc_default.png', 'portrait_filename': 'portrait_village_elder.png'},
    {'name': 'Village Healer', 'sprite_filename': 'npc_default.png', 'portrait_filename': 'portrait_village_healer.png'},
    {'name': 'Whisper the Fence', 'sprite_filename': 'npc_default.png', 'portrait_filename': 'portrait_whisper_the_fence.png'},
    {'name': 'Willow the Herbalist', 'sprite_filename': 'npc_default.png', 'portrait_filename': 'portrait_willow_the_herbalist.png'},
    {'name': 'Wise Hermit', 'sprite_filename': 'npc_default.png', 'portrait_filename': 'portrait_wise_hermit.png'},
    {'name': 'Zara the Exotic Trader', 'sprite_filename': 'npc_default.png', 'portrait_filename': 'portrait_zara_the_exotic_trader.png'},
]

for npc in npcs:
    # Download sprite
    sprite_url = SPRITE_DOWNLOAD_URL.format(filename=npc['sprite_filename'])
    sprite_filepath = os.path.join(SPRITES_DIR, npc['sprite_filename'])
    print(f'Downloading {npc["name"]} sprite...')
    try:
        urllib.request.urlretrieve(sprite_url, sprite_filepath)
        print(f'  ✓ Saved to {sprite_filepath}')
    except Exception as e:
        print(f'  ✗ Error: {e}')

    # Download portrait
    portrait_url = PORTRAIT_DOWNLOAD_URL.format(filename=npc['portrait_filename'])
    portrait_filepath = os.path.join(PORTRAITS_DIR, npc['portrait_filename'])
    print(f'Downloading {npc["name"]} portrait...')
    try:
        urllib.request.urlretrieve(portrait_url, portrait_filepath)
        print(f'  ✓ Saved to {portrait_filepath}')
    except Exception as e:
        print(f'  ✗ Error: {e}')

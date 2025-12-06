# Download script for Enemy Sprites
# Usage: Update the DOWNLOAD_URL variable and run this script

import os
import urllib.request

SPRITES_DIR = 'assets/sprites'
os.makedirs(SPRITES_DIR, exist_ok=True)

# Update this with your download URL pattern
# Example: DOWNLOAD_URL = 'https://example.com/sprites/{filename}'
DOWNLOAD_URL = 'YOUR_DOWNLOAD_URL_HERE/{filename}'

enemies = [
    {'name': '???', 'filename': 'boss_unknown.png'},
    {'name': 'Alpha Wolf', 'filename': 'wolf.png'},
    {'name': 'Ancient Guardian', 'filename': 'boss.png'},
    {'name': 'Bandit Leader', 'filename': 'bandit.png'},
    {'name': 'Cave Bat', 'filename': 'bat.png'},
    {'name': 'Cave Goblin', 'filename': 'goblin.png'},
    {'name': 'Cyclops', 'filename': 'cyclops.png'},
    {'name': 'Dark Knight', 'filename': 'dark_knight.png'},
    {'name': 'Fire Elemental', 'filename': 'fire_elemental.png'},
    {'name': 'Forest Wolf', 'filename': 'wolf.png'},
    {'name': 'Giant Spider', 'filename': 'spider.png'},
    {'name': 'Goblin Chief', 'filename': 'goblin.png'},
    {'name': 'Goblin Shaman', 'filename': 'goblin.png'},
    {'name': 'Goblin Warrior', 'filename': 'goblin.png'},
    {'name': 'Gorakk, The Primordial Beast', 'filename': 'boss_primordial.png'},
    {'name': 'Green Slime', 'filename': 'slime.png'},
    {'name': 'Harpy', 'filename': 'harpy.png'},
    {'name': 'Ice Elemental', 'filename': 'ice_elemental.png'},
    {'name': 'Imp', 'filename': 'imp.png'},
    {'name': 'Lesser Demon', 'filename': 'demon.png'},
    {'name': 'Lizardman Shaman', 'filename': 'lizardman.png'},
    {'name': 'Lizardman Warrior', 'filename': 'lizardman.png'},
    {'name': 'Mountain Troll', 'filename': 'troll.png'},
    {'name': 'Necromancer', 'filename': 'necromancer.png'},
    {'name': 'Nullix, Emperor of the Void', 'filename': 'boss_void.png'},
    {'name': 'Orc Berserker', 'filename': 'orc.png'},
    {'name': 'Orc Warrior', 'filename': 'orc.png'},
    {'name': 'Practice Slime', 'filename': 'slime.png'},
    {'name': 'Restless Spirit', 'filename': 'ghost.png'},
    {'name': 'River Lurker', 'filename': 'slime.png'},
    {'name': 'Sea Serpent', 'filename': 'snake.png'},
    {'name': 'Shadow [Player]', 'filename': 'mirror_player.png'},
    {'name': 'Sir Aldric, The Forgotten Champion', 'filename': 'boss_champion.png'},
    {'name': 'Skeleton Archer', 'filename': 'skeleton.png'},
    {'name': 'Skeleton Minion', 'filename': 'skeleton.png'},
    {'name': 'Skeleton Warrior', 'filename': 'skeleton.png'},
    {'name': 'Stone Golem', 'filename': 'golem.png'},
    {'name': 'Swamp Spider', 'filename': 'spider.png'},
    {'name': 'Swamp Witch', 'filename': 'witch.png'},
    {'name': 'Toxic Mushroom', 'filename': 'mushroom.png'},
    {'name': 'Treasure Mimic', 'filename': 'mimic.png'},
    {'name': 'Umbraxis, Shadow Sovereign', 'filename': 'boss_shadow.png'},
    {'name': 'Vampire Bat', 'filename': 'bat.png'},
    {'name': 'Vampire Lord', 'filename': 'vampire.png'},
    {'name': 'Venomous Spider', 'filename': 'spider.png'},
    {'name': 'Wraith', 'filename': 'wraith.png'},
    {'name': 'Young Werewolf', 'filename': 'werewolf.png'},
    {'name': 'Zyraxis, Ancient Wyrm', 'filename': 'boss_wyrm.png'},
]

for enemy in enemies:
    url = DOWNLOAD_URL.format(filename=enemy['filename'])
    filepath = os.path.join(SPRITES_DIR, enemy['filename'])
    print(f'Downloading {enemy["name"]}...')
    try:
        urllib.request.urlretrieve(url, filepath)
        print(f'  ✓ Saved to {filepath}')
    except Exception as e:
        print(f'  ✗ Error: {e}')

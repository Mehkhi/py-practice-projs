
# Tetris (Minimal Pygame Edition)

A clean, dependency-light Tetris built with Pygame. No linting rigs, no CI fairy dust—just code you can run and hack.

## Features
- 10×20 board, 7-bag piece randomizer
- Rotation with simple wall-kicks
- Line clearing, scoring, levels (gravity speeds up)
- Soft drop / hard drop, pause, restart
- Next-piece preview, ghost piece
- **4 visual themes**: NES (classic), Modern (flat), Neon (arcade), Minimal (high contrast)
- **Enhanced visuals**: Rounded blocks, gradients, shadows, outlines per theme
- **Smooth animations**: Spawn pop, lock thud, line-clear flash

## Controls
- **Left/Right or A/D**: move
- **Down or S**: soft drop
- **Up / X / W**: rotate clockwise
- **Z**: rotate counterclockwise
- **Space**: hard drop
- **P**: pause
- **R**: restart
- **Esc**: close the window (or click the X)
- **T**: cycle theme forward
- **Shift+T**: cycle theme backward
- **1-4**: select theme directly (1=NES, 2=Modern, 3=Neon, 4=Minimal)

## Setup
Requires Python 3.10+.

```bash
pip install -r requirements.txt
```

## Run
```bash
python -m tetris
```

### Headless note (optional)
For CI or servers without a display, you can run with a dummy SDL video driver:
```bash
SDL_VIDEODRIVER=dummy python -m tetris
```

## Project Layout
```text
tetris/
  __main__.py         # entrypoint: python -m tetris
  game.py             # orchestrates loop, input, state
  config.py           # sizes, colors
  core/
    board.py          # board grid, collision, line clear
    piece.py          # piece definitions and rotations
    bag.py            # 7-bag generator
    rules.py          # scoring and gravity
  ui/
    render.py         # drawing and HUD/panel
    theme.py          # theme system and visual styles
  assets/             # (optional) drop sounds/fonts here
```

## Game API

The `Game` class provides a clear API for integrating with different frontends:

### Recommended Usage

```python
game = Game()

while running:
    for event in pygame.event.get():
        game.handle_event(event)  # Forward events
    game.tick()  # Per-frame update (polls held keys for DAS/ARR)
    game.draw(screen, font)
```

- **`handle_event(event)`**: Processes pygame events (KEYDOWN, KEYUP, custom events). Also performs throttled held-key polling to ensure DAS/ARR works even when only forwarding events.
- **`tick()`**: Per-frame update that polls held keys for repeat movement. Should be called once per frame.

### Backwards Compatibility

The `update(event_or_none)` method remains available for backwards compatibility:
- `update(None)` → calls `tick()`
- `update(event)` → calls `handle_event(event)`

**Note**: `update()` is maintained for compatibility but may be deprecated in future versions. New code should use `handle_event()` and `tick()` directly.

## Themes

The game includes four distinct visual themes that can be switched at runtime:

- **NES**: Classic retro look with bright colors and square blocks
- **Modern**: Clean flat design with rounded corners, gradients, and shadows
- **Neon**: Dark arcade aesthetic with glowing colors and diagonal background patterns
- **Minimal**: High-contrast minimalist design with bold outlines

Each theme includes:
- Custom color palette for background, grid, text, and pieces
- Block styling (rounded corners, outlines, gradients, shadows)
- Ghost piece styling (solid or dotted outlines)
- Panel background and styling

## Make it yours
This is intentionally minimal so you can fork and riff:
- Add a hold piece, SRS wall-kick tables, T-spins, proper DAS/ARR
- High-score persistence (JSON/SQLite), music/sfx
- Additional themes or customization options

MIT licensed—go wild.

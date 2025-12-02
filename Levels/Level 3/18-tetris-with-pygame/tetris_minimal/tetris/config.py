
# Basic configuration values for the Tetris game.
CELL_SIZE = 30            # pixels per cell
COLUMNS = 10              # board width
ROWS = 20                 # board height
FPS = 60                  # frame cap
MARGIN = 20               # outer window padding in pixels
PANEL_WIDTH = 6           # side panel (columns worth of width)

# Derived window size
# Add extra 20px for panel gap and 10px padding on each side
WINDOW_WIDTH = (COLUMNS + PANEL_WIDTH) * CELL_SIZE + 2 * MARGIN + 20 + 20
WINDOW_HEIGHT = ROWS * CELL_SIZE + 2 * MARGIN

# Colors (R, G, B)
COLOR_BG = (18, 18, 18)
COLOR_GRID = (45, 45, 45)
COLOR_TEXT = (230, 230, 230)
COLOR_GHOST = (90, 90, 90)

# Piece colors
PIECE_COLORS = {
    "I": (0, 240, 240),     # cyan
    "O": (240, 240, 0),     # yellow
    "T": (160, 0, 240),     # purple
    "S": (0, 240, 0),       # green
    "Z": (240, 0, 0),       # red
    "J": (0, 0, 240),       # blue
    "L": (240, 160, 0),     # orange
}

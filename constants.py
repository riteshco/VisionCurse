WIN_WIDTH = 800
WIN_HEIGHT = 600

PLAYER_SIZE = 40

# Maze dimensions
PLAYER_SPEED = 6
CELL_SIZE = PLAYER_SIZE * 3  # Corridor size is 3x player size
WALL_THICKNESS = 3
COLS = 40  # Number of columns in the maze
ROWS = 30  # Number of rows in the maze

# Calculate total world size
WORLD_WIDTH = COLS * CELL_SIZE
WORLD_HEIGHT = ROWS * CELL_SIZE

FOV_ANGLE_DEGREES = 60
RAY_COUNT = 60
RAY_LENGTH = 300
AURA_RADIUS = 50

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)         # Exit
START_BLUE = (0, 0, 255)  # Start
PURPLE = (40, 0, 80)      # Floor
PLAYER_COLOR = (255, 100, 100) # Player

# Player dimensions
PLAYER_SIZE = 40
CELL_SIZE = PLAYER_SIZE * 3
WALL_THICKNESS = 3
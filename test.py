import pygame
import random

# --- Constants ---
# Screen dimensions
WIDTH = 800
HEIGHT = 600

# Maze dimensions (in cells)
CELL_SIZE = 20
COLS = 20
ROWS = 20

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)       # Current cell
RED = (255, 0, 0)         # Exit
START_BLUE = (0, 0, 255)  # Start
PURPLE = (40, 0, 80)      # Visited cells

# --- Cell Class ---
class Cell:
    def __init__(self, col, row):
        self.col = col
        self.row = row
        self.walls = {'top': True, 'right': True, 'bottom': True, 'left': True}
        self.visited = False

    def draw(self, screen):
        x = self.col * CELL_SIZE
        y = self.row * CELL_SIZE

        # Fill visited cells with a different color
        if self.visited:
            pygame.draw.rect(screen, PURPLE, (x, y, CELL_SIZE, CELL_SIZE))

        # Draw walls
        if self.walls['top']:
            pygame.draw.line(screen, WHITE, (x, y), (x + CELL_SIZE, y), 1)
        if self.walls['right']:
            pygame.draw.line(screen, WHITE, (x + CELL_SIZE, y), (x + CELL_SIZE, y + CELL_SIZE), 1)
        if self.walls['bottom']:
            pygame.draw.line(screen, WHITE, (x + CELL_SIZE, y + CELL_SIZE), (x, y + CELL_SIZE), 1)
        if self.walls['left']:
            pygame.draw.line(screen, WHITE, (x, y + CELL_SIZE), (x, y), 1)

    def check_neighbors(self, grid):
        neighbors = []
        
        # Check potential neighbors (top, right, bottom, left)
        indices = [
            (self.col, self.row - 1),  # Top
            (self.col + 1, self.row),  # Right
            (self.col, self.row + 1),  # Bottom
            (self.col - 1, self.row)   # Left
        ]

        for c, r in indices:
            if 0 <= c < COLS and 0 <= r < ROWS:
                neighbor = grid[c][r]
                if not neighbor.visited:
                    neighbors.append(neighbor)
        
        if neighbors:
            return random.choice(neighbors)
        return None

# --- Helper Function ---
def remove_walls(current, next_cell):
    dx = current.col - next_cell.col
    dy = current.row - next_cell.row

    if dx == 1:  # Next cell is to the left
        current.walls['left'] = False
        next_cell.walls['right'] = False
    elif dx == -1: # Next cell is to the right
        current.walls['right'] = False
        next_cell.walls['left'] = False
    
    if dy == 1:  # Next cell is above
        current.walls['top'] = False
        next_cell.walls['bottom'] = False
    elif dy == -1: # Next cell is below
        current.walls['bottom'] = False
        next_cell.walls['top'] = False

# --- Main Function ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Maze Generator (DFS Recursive Backtracker)")
    clock = pygame.time.Clock()

    # 1. Create the grid of cells
    grid = [[Cell(c, r) for r in range(ROWS)] for c in range(COLS)]

    # 2. Setup the algorithm
    stack = []
    current_cell = grid[0][0]
    current_cell.visited = True
    stack.append(current_cell)
    
    generation_complete = False
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        screen.fill(BLACK)

        # --- Algorithm Step ---
        if not generation_complete:
            current_cell.visited = True
            
            # Highlight the current "carver" cell
            x = current_cell.col * CELL_SIZE
            y = current_cell.row * CELL_SIZE
            pygame.draw.rect(screen, GREEN, (x, y, CELL_SIZE, CELL_SIZE))

            # Find a random unvisited neighbor
            next_cell = current_cell.check_neighbors(grid)
            
            if next_cell:
                # 1. Push current cell to stack
                stack.append(current_cell)
                # 2. Remove walls between current and next
                remove_walls(current_cell, next_cell)
                # 3. Move to the next cell
                current_cell = next_cell
            elif stack:
                # Backtrack
                current_cell = stack.pop()
            else:
                # Generation is finished!
                generation_complete = True
                # Create the entrance and exit
                grid[0][0].walls['top'] = False
                grid[COLS - 1][ROWS - 1].walls['bottom'] = False

        # --- Draw all cells ---
        for c in range(COLS):
            for r in range(ROWS):
                grid[c][r].draw(screen)

        # --- Draw Start and End ---
        if generation_complete:
            # Draw Start (Entrance)
            pygame.draw.rect(screen, START_BLUE, (0, 0, CELL_SIZE, CELL_SIZE))
            # Draw End (Exit)
            pygame.draw.rect(screen, RED, ((COLS - 1) * CELL_SIZE, (ROWS - 1) * CELL_SIZE, CELL_SIZE, CELL_SIZE))

        pygame.display.flip()
        clock.tick(60) # Adjust FPS to speed up/slow down generation

    pygame.quit()

if __name__ == "__main__":
    main()
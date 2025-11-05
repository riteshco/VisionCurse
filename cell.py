import random
import pygame
from constants import *

class Cell:
    def __init__(self, col, row):
        self.col = col
        self.row = row
        # World coordinates of the top-left corner
        self.x = col * CELL_SIZE
        self.y = row * CELL_SIZE
        self.walls = {'top': True, 'right': True, 'bottom': True, 'left': True}
        self.visited = False

    def draw(self, screen, camera_offset):
        # Calculate screen position from world position
        screen_x = self.x - camera_offset[0]
        screen_y = self.y - camera_offset[1]
        
        # --- Optimization ---
        # Only draw cells that are visible on the screen
        if (screen_x + CELL_SIZE < 0 or screen_x > WIN_WIDTH or
            screen_y + CELL_SIZE < 0 or screen_y > WIN_HEIGHT):
            return

        # Fill visited cells with a different color (now our floor)
        # pygame.draw.rect(screen, PURPLE, (screen_x, screen_y, CELL_SIZE, CELL_SIZE))

        # Draw walls
        if self.walls['top']:
            pygame.draw.line(screen, WHITE, (screen_x, screen_y), (screen_x + CELL_SIZE, screen_y), WALL_THICKNESS)
        if self.walls['right']:
            pygame.draw.line(screen, WHITE, (screen_x + CELL_SIZE, screen_y), (screen_x + CELL_SIZE, screen_y + CELL_SIZE), WALL_THICKNESS)
        if self.walls['bottom']:
            pygame.draw.line(screen, WHITE, (screen_x + CELL_SIZE, screen_y + CELL_SIZE), (screen_x, screen_y + CELL_SIZE), WALL_THICKNESS)
        if self.walls['left']:
            pygame.draw.line(screen, WHITE, (screen_x, screen_y + CELL_SIZE), (screen_x, screen_y), WALL_THICKNESS)

    def get_wall_rects(self):
        # Return a list of pygame.Rect objects for this cell's walls
        rects = []
        if self.walls['top']:
            rects.append(pygame.Rect(self.x, self.y, CELL_SIZE, WALL_THICKNESS))
        if self.walls['right']:
            rects.append(pygame.Rect(self.x + CELL_SIZE - WALL_THICKNESS, self.y, WALL_THICKNESS, CELL_SIZE))
        if self.walls['bottom']:
            rects.append(pygame.Rect(self.x, self.y + CELL_SIZE - WALL_THICKNESS, CELL_SIZE, WALL_THICKNESS))
        if self.walls['left']:
            rects.append(pygame.Rect(self.x, self.y, WALL_THICKNESS, CELL_SIZE))
        return rects

    def check_neighbors(self, grid):
        neighbors = []
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
import pygame
from constants import *

class Player:
    def __init__(self, pos, size):
        self.pos = [pos[0], pos[1]] # World position
        self.size = [size, size]
        self.health = 100
        self.speed = PLAYER_SPEED

    def render(self, screen, camera_offset):
        # Calculate screen position from world position
        screen_x = self.pos[0] - camera_offset[0]
        screen_y = self.pos[1] - camera_offset[1]
        
        # Draw player as a simple red square
        pygame.draw.rect(screen, PLAYER_COLOR, (screen_x, screen_y, self.size[0], self.size[1]))

    def get_rect(self):
        # Helper to get the player's collision rectangle
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
    
    def get_center_pos(self):
        return [self.pos[0] + self.size[0] / 2, self.pos[1] + self.size[1] / 2]
    
    def get_aura_center(self , camera_offset):
        return [self.pos[0] - camera_offset[0] + self.size[0] / 2 , self.pos[1] - camera_offset[1] + self.size[1]/2]
    # --- New Movement Function with Collisions ---
    def move_player(self, grid, dx, dy):
        # Calculate potential new position
        new_x = self.pos[0] + dx * self.speed
        new_y = self.pos[1] + dy * self.speed

        new_x = max(0 , new_x)
        new_y = max(0 , new_y)

        # Create rects for X and Y separately
        new_rect_x = pygame.Rect(new_x, self.pos[1], self.size[0], self.size[1])
        new_rect_y = pygame.Rect(self.pos[0], new_y, self.size[0], self.size[1])

        can_move_x = True
        can_move_y = True

        # Get player's current grid cell indices to check nearby walls
        current_col = int((self.pos[0] + self.size[0] / 2) // CELL_SIZE)
        current_row = int((self.pos[1] + self.size[1] / 2) // CELL_SIZE)

        # Check a 3x3 area around the player for relevant walls
        for c in range(max(0, current_col - 1), min(COLS, current_col + 2)):
            for r in range(max(0, current_row - 1), min(ROWS, current_row + 2)):
                cell = grid[c][r]
                
                for wall in cell.get_wall_rects():
                    if new_rect_x.colliderect(wall):
                        can_move_x = False
                    if new_rect_y.colliderect(wall):
                        can_move_y = False

        # Apply movement if allowed
        if can_move_x:
            self.pos[0] = new_x
        if can_move_y:
            self.pos[1] = new_y


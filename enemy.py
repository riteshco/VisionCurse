import pygame
import math
import random
from constants import *

class Enemy:
    def __init__(self, pos, size):
        self.pos = [pos[0], pos[1]] # World position
        self.size = size
        self.health = ENEMY_HEALTH
        self.speed = ENEMY_SPEED
        self.last_attack_time = 0
        self.is_alerted = False
        self.is_far = False

    def render(self, screen, camera_offset):
        # Calculate screen position
        screen_x = self.pos[0] - camera_offset[0]
        screen_y = self.pos[1] - camera_offset[1]
        
        # Simple green rectangle
        pygame.draw.rect(screen, ENEMY_COLOR, (screen_x, screen_y, self.size[0], self.size[1]))

    def get_rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
    
    def get_center_pos(self):
        return [self.pos[0] + self.size[0] / 2, self.pos[1] + self.size[1] / 2]

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.health = 0
            return True # Return True if dead
        return False

    def update(self, player, grid , current_detection_range , attack_sound , alert_sound):
        player_center = player.get_center_pos()
        self_center = self.get_center_pos()

        dist = math.dist(player_center, self_center)

        # --- AI Logic ---
        if dist < current_detection_range:
            if not self.is_alerted:
                self.is_alerted = True
                alert_sound.play()
            # 1. Move towards player
            dx = player_center[0] - self_center[0]
            dy = player_center[1] - self_center[1]
            # Normalize vector
            norm = math.sqrt(dx * dx + dy * dy)
            if norm > 0:
                dx = (dx / norm) * self.speed
                dy = (dy / norm) * self.speed
                self.move(grid, dx, dy) # Call move method

            # 2. Attack player (melee)
            player_rect = player.get_rect()
            if self.get_rect().colliderect(player_rect):
                current_time = pygame.time.get_ticks()
                if current_time - self.last_attack_time > ENEMY_ATTACK_COOLDOWN:
                    player.take_damage(ENEMY_MELEE_DAMAGE)
                    attack_sound.play()
                    self.last_attack_time = current_time
        elif dist > current_detection_range * 1.5:
            self.is_alerted = False
        
        if dist > current_detection_range * 3:
            self.is_far = True
        else:
            self.is_far = False 

    def move(self, grid, dx, dy):
        # This is the same collision logic as the player
        new_x = self.pos[0] + dx
        new_y = self.pos[1] + dy

        new_x = max(0 , new_x)
        new_y = max(0 , new_y)

        new_rect_x = pygame.Rect(new_x, self.pos[1], self.size[0], self.size[1])
        new_rect_y = pygame.Rect(self.pos[0], new_y, self.size[0], self.size[1])

        can_move_x = True
        can_move_y = True

        current_col = int((self.pos[0] + self.size[0] / 2) // CELL_SIZE)
        current_row = int((self.pos[1] + self.size[1] / 2) // CELL_SIZE)

        for c in range(max(0, current_col - 1), min(COLS, current_col + 2)):
            for r in range(max(0, current_row - 1), min(ROWS, current_row + 2)):
                cell = grid[c][r]
                
                for wall in cell.get_wall_rects():
                    if new_rect_x.colliderect(wall):
                        can_move_x = False
                    if new_rect_y.colliderect(wall):
                        can_move_y = False

        if can_move_x:
            self.pos[0] = new_x
        if can_move_y:
            self.pos[1] = new_y
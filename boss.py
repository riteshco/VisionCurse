import pygame
import math
from constants import *

class Boss:
    def __init__(self, pos, size, health):
        self.pos = [pos[0], pos[1]]
        self.size = size
        self.max_health = health
        self.health = health
        self.speed = BOSS_SPEED
        self.last_attack_time = 0

        try:
            self.original_image = pygame.image.load(BOSS_SPRITE_PATH).convert_alpha()
            self.original_image = pygame.transform.scale(self.original_image, (self.size[0], self.size[1]))
        except pygame.error as e:
            print(f"Error loading boss image: {e}")
            # Fallback to a simple surface if images are missing
            self.original_image = pygame.Surface(self.size)
            self.original_image.fill(BOSS_COLOR)

        self.image = self.original_image
        self.rect = self.image.get_rect(center=self.get_center_pos())

    def get_rect(self):
        self.rect.topleft = (self.pos[0], self.pos[1])
        return self.rect
    
    def get_center_pos(self):
        return [self.pos[0] + self.size[0] / 2, self.pos[1] + self.size[1] / 2]

    def take_damage(self, amount, hit_sound):
        self.health -= amount
        hit_sound.play()
        if self.health <= 0:
            self.health = 0
            return True # Return True if dead
        return False

    def update(self, player, attack_sound):
        player_center = player.get_center_pos()
        self_center = self.get_center_pos()

        dx = player_center[0] - self_center[0]
        dy = player_center[1] - self_center[1]
        norm = math.sqrt(dx * dx + dy * dy)
        if norm > 0:
            dx_norm = (dx / norm)
            dy_norm = (dy / norm)
            self.pos[0] += dx_norm * self.speed
            self.pos[1] += dy_norm * self.speed

            angle = math.degrees(math.atan2(-dy_norm, dx_norm)) # -dy because pygame's y is inverted
            self.image = pygame.transform.rotate(self.original_image, angle)
            self.rect = self.image.get_rect(center=self_center)


        self.pos[0] = max(ARENA_WALL_THICKNESS, min(self.pos[0], ARENA_WIDTH - self.size[0] - ARENA_WALL_THICKNESS))
        self.pos[1] = max(ARENA_WALL_THICKNESS, min(self.pos[1], ARENA_HEIGHT - self.size[1] - ARENA_WALL_THICKNESS))

        player_rect = player.get_rect()
        if self.get_rect().colliderect(player_rect):
            current_time = pygame.time.get_ticks()
            if current_time - self.last_attack_time > BOSS_ATTACK_COOLDOWN:
                player.take_damage(BOSS_MELEE_DAMAGE)
                self.last_attack_time = current_time
                attack_sound.play()

    def render(self, screen, camera_offset):
        world_center = self.get_center_pos()
        screen_center_x = world_center[0] - camera_offset[0]
        screen_center_y = world_center[1] - camera_offset[1]
        screen_rect = self.image.get_rect(center=(screen_center_x, screen_center_y))
        
        screen.blit(self.image, screen_rect)
        
        bar_width = self.size[0]
        bar_height = 20
        bar_x = screen_rect.centerx - bar_width / 2
        bar_y = screen_rect.top - bar_height - 10

        if bar_y > WIN_HEIGHT or bar_y + bar_height < 0:
            return

        pygame.draw.rect(screen, (100, 0, 0), (bar_x, bar_y, bar_width, bar_height))
        
        health_percent = self.health / self.max_health
        pygame.draw.rect(screen, (0, 200, 0), (bar_x, bar_y, bar_width * health_percent, bar_height))
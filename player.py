import pygame
import math
import random
from constants import *

class Player:
    def __init__(self, pos, size):
        self.pos = [pos[0], pos[1]]
        self.size = [size, size]
        self.health = 100
        self.speed = PLAYER_SPEED

        self.inventory = ["flashlight", "shotgun"]
        self.equipped_item = "flashlight"

        self.max_health = PLAYER_MAX_HEALTH
        self.health = self.max_health
        self.shotgun_ammo_capacity = SHOTGUN_AMMO_CAPACITY
        self.shotgun_ammo = self.shotgun_ammo_capacity
        self.shotgun_reload_time = SHOTGUN_RELOAD_TIME
        self.fov_angle = FOV_ANGLE_DEGREES
        self.flashlight_brightness = FLASHLIGHT_MAX_BRIGHTNESS
        self.shotgun_pellet_count = SHOTGUN_PELLET_COUNT
        self.flashlight_base_brightness = FLASHLIGHT_BASE_BRIGHTNESS
        
        self.skill_points = 0

        self.shotgun_ammo = SHOTGUN_AMMO_CAPACITY
        self.is_reloading = False
        self.reload_start_time = 0

        try:
            self.idle_image_right = pygame.image.load('images/improved_images/player_idle.png').convert_alpha()
            self.idle_image_left = pygame.transform.flip(self.idle_image_right, True, False)

            self.walk_right_frames = [
                pygame.image.load('images/improved_images/player_right1.png').convert_alpha(),
                pygame.image.load('images/improved_images/player_right2.png').convert_alpha(),
                pygame.image.load('images/improved_images/player_right3.png').convert_alpha(),
                pygame.image.load('images/improved_images/player_right4.png').convert_alpha()
            ]
            self.walk_left_frames = [
                pygame.image.load('images/improved_images/player_left1.png').convert_alpha(),
                pygame.image.load('images/improved_images/player_left2.png').convert_alpha(),
                pygame.image.load('images/improved_images/player_left3.png').convert_alpha(),
                pygame.image.load('images/improved_images/player_left4.png').convert_alpha()
            ]

            self.shotgun_original_image = pygame.image.load(SHOTGUN_SPRITE_PATH).convert_alpha()
            self.flashlight_original_image = pygame.image.load(FLASHLIGHT_SPRITE_PATH).convert_alpha()
            
            self.idle_image_right = pygame.transform.scale(self.idle_image_right, (self.size[0], self.size[1]))
            self.idle_image_left = pygame.transform.scale(self.idle_image_left, (self.size[0], self.size[1]))
            
            self.walk_right_frames = [pygame.transform.scale(img, (self.size[0], self.size[1])) for img in self.walk_right_frames]
            self.walk_left_frames = [pygame.transform.scale(img, (self.size[0], self.size[1])) for img in self.walk_left_frames]



            shotgun_size = (int(self.size[0] * 1.5), int(self.size[1] * 1.6))
            self.shotgun_original_image = pygame.transform.scale(self.shotgun_original_image, shotgun_size)
            self.shotgun_original_left = pygame.transform.flip(self.shotgun_original_image, False, True)


            flashlight_size = (int(self.size[0] * 1.2), int(self.size[1] * 0.6))
            self.flashlight_original_image = pygame.transform.scale(self.flashlight_original_image, flashlight_size)
            self.flashlight_original_left = pygame.transform.flip(self.flashlight_original_image, False, True)
            
        except pygame.error as e:
            print(f"Error loading player images: {e}")
            self.idle_image_right = pygame.Surface(self.size)
            self.idle_image_right.fill(PLAYER_COLOR)
            self.idle_image_left = self.idle_image_right
            self.walk_right_frames = [self.idle_image_right] * 4
            self.walk_left_frames = [self.idle_image_right] * 4

            self.flashlight_original_image = pygame.Surface((20,10)); self.flashlight_original_image.fill((255,255,0))
            self.flashlight_original_left = self.flashlight_original_image

        self.current_frame = 0
        self.last_anim_update = 0
        self.anim_speed_ms = 150 # Time between frames (in milliseconds)
        self.facing_right = True

        self.image = self.idle_image_right

        self.shotgun_image = self.shotgun_original_image
        self.flashlight_image = self.flashlight_original_image
        self.weapon_angle = 0 
        self.weapon_pivot_offset = [5, 3]

    def render(self, screen, camera_offset):
        screen_x = self.pos[0] - camera_offset[0]
        screen_y = self.pos[1] - camera_offset[1]
        
        screen.blit(self.image, (screen_x, screen_y))
        player_rect = pygame.Rect(screen_x, screen_y, self.size[0], self.size[1])
        # pygame.draw.rect(screen, PLAYER_COLOR, player_rect)

        item_size = self.size[0] * 0.5
        item_rect = pygame.Rect(player_rect.centerx - item_size / 2, 
                                player_rect.centery - item_size / 2, 
                                item_size, item_size)

        player_screen_center = self.get_aura_center(camera_offset)
        
        # Adjust pivot based on facing direction
        pivot = (player_screen_center[0] - self.weapon_pivot_offset[0], player_screen_center[1] + self.weapon_pivot_offset[1])
            
        if self.equipped_item == "shotgun":
            shotgun_screen_rect = self.shotgun_image.get_rect(center=pivot)
            screen.blit(self.shotgun_image, shotgun_screen_rect)
            
        elif self.equipped_item == "flashlight":
            flashlight_screen_rect = self.flashlight_image.get_rect(center=pivot)
            screen.blit(self.flashlight_image, flashlight_screen_rect)

    def get_rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
    
    def get_center_pos(self):
        return [self.pos[0] + self.size[0] / 2, self.pos[1] + self.size[1] / 2]
    
    def get_aura_center(self , camera_offset):
        return [self.pos[0] - camera_offset[0] + self.size[0] / 2 , self.pos[1] - camera_offset[1] + self.size[1]/2]

    def take_damage(self, amount):
        self.health -= amount
        if self.health < 0:
            self.health = 0
        print(f"Player took {amount} damage, health is now {self.health}")

    def update(self, move_dict, camera_offset , joystick_horizontal_aim , joystick_vertical_aim):
        if self.is_reloading:
            current_time = pygame.time.get_ticks()
            if current_time - self.reload_start_time >= self.shotgun_reload_time:
                self.shotgun_ammo = self.shotgun_ammo_capacity
                self.is_reloading = False
                print("Reload complete.")
        
        current_time = pygame.time.get_ticks()
        is_moving = False

        if current_time - self.last_anim_update > self.anim_speed_ms:
            self.last_anim_update = current_time
            # Advance the frame, looping back to 0
            self.current_frame = (self.current_frame + 1) % len(self.walk_right_frames) # 4 frames

        if move_dict["Right"] or move_dict["Joystick_Right"]:
            self.image = self.walk_right_frames[self.current_frame]
            self.facing_right = True
            is_moving = True
        elif move_dict["Left"] or move_dict["Joystick_Left"]:
            self.image = self.walk_left_frames[self.current_frame]
            self.facing_right = False
            is_moving = True
        elif move_dict["Up"] or move_dict["Down"] or move_dict["Joystick_Up"] or move_dict["Joystick_Down"]:
            # If moving vertically, use the last faced direction
            if self.facing_right:
                self.image = self.walk_right_frames[self.current_frame]
            else:
                self.image = self.walk_left_frames[self.current_frame]
            is_moving = True
        
        if not is_moving:
            # Player is standing still, show idle image for the last direction
            if self.facing_right:
                self.image = self.idle_image_right
            else:
                self.image = self.idle_image_left
            self.current_frame = 0
        
        if joystick_horizontal_aim or joystick_vertical_aim:
            mouse_x , mouse_y = joystick_horizontal_aim , joystick_vertical_aim
            self.weapon_angle = math.degrees(math.atan2(-joystick_vertical_aim , joystick_horizontal_aim))
        else:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            player_screen_center = self.get_aura_center(camera_offset)
            dx = mouse_x - player_screen_center[0]
            dy = mouse_y - player_screen_center[1]
            self.weapon_angle = math.degrees(math.atan2(-dy, dx)) # -dy because pygame's y is inverted


        base_shotgun_img = self.shotgun_original_image
        self.shotgun_image = pygame.transform.rotate(base_shotgun_img, self.weapon_angle)

        base_flash_img = self.flashlight_original_image
        self.flashlight_image = pygame.transform.rotate(base_flash_img, self.weapon_angle)
    
    def swap_item(self , swap_sound):
        if self.is_reloading: # Don't swap while reloading
            return
            
        if self.equipped_item == "flashlight":
            self.equipped_item = "shotgun"
        else:
            self.equipped_item = "flashlight"
        swap_sound.play()
        print(f"Equipped: {self.equipped_item}")

    def shoot(self, target_angle, grid , fire_sound , reload_sound , is_boss_fight=False):
        if self.equipped_item != "shotgun" or self.is_reloading:
            return None
        
        if self.shotgun_ammo <= 0:
            print("Out of ammo. Reloading...")
            self.reload(reload_sound)
            return None
            
        self.shotgun_ammo -= 1
        fire_sound.play()
        pellet_lines = []
        player_center_world = self.get_center_pos()

        for _ in range(self.shotgun_pellet_count):
            angle = target_angle + math.radians(random.uniform(-SHOTGUN_SPREAD_ANGLE / 2, SHOTGUN_SPREAD_ANGLE / 2))
            
            step_x = math.cos(angle)
            step_y = math.sin(angle)
            
            ray_x, ray_y = player_center_world
            current_dist = 0
            hit_wall = False
            
            # Cast ray
            while not hit_wall and current_dist < SHOTGUN_RANGE:
                current_dist += 1
                ray_x = player_center_world[0] + step_x * current_dist
                ray_y = player_center_world[1] + step_y * current_dist

                if is_boss_fight:
                    # In boss fight, only check arena boundaries
                    if (ray_x < ARENA_WALL_THICKNESS or ray_x > ARENA_WIDTH - ARENA_WALL_THICKNESS or
                        ray_y < ARENA_WALL_THICKNESS or ray_y > ARENA_HEIGHT - ARENA_WALL_THICKNESS):
                        hit_wall = True
                else:
                    # In maze, check grid
                    col = int(ray_x // CELL_SIZE)
                    row = int(ray_y // CELL_SIZE)
                    if not (0 <= col < COLS and 0 <= row < ROWS):
                        hit_wall = True
                        break
                        
                    cell = grid[col][row]
                    for wall in cell.get_wall_rects():
                        if wall.collidepoint(ray_x, ray_y):
                            hit_wall = True
                            break
                
                if hit_wall:
                    break
            
            # Add the line to be drawn
            pellet_lines.append((player_center_world, (ray_x, ray_y)))
            
        return pellet_lines

    def reload(self , reload_sound):
        if self.equipped_item == "shotgun" and not self.is_reloading and self.shotgun_ammo < SHOTGUN_AMMO_CAPACITY:
            print("Reloading...")
            self.is_reloading = True
            self.reload_start_time = pygame.time.get_ticks()
            reload_sound.play()

    def move_player(self, grid, dx, dy):
        new_x = self.pos[0] + dx * self.speed
        new_y = self.pos[1] + dy * self.speed

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
    
    def move_player_arena(self, dx, dy):
        new_x = self.pos[0] + dx * self.speed
        new_y = self.pos[1] + dy * self.speed

        new_x = max(ARENA_WALL_THICKNESS, min(new_x, ARENA_WIDTH - self.size[0] - ARENA_WALL_THICKNESS))
        new_y = max(ARENA_WALL_THICKNESS, min(new_y, ARENA_HEIGHT - self.size[1] - ARENA_WALL_THICKNESS))
        
        self.pos[0] = new_x
        self.pos[1] = new_y
    
    def add_skill_points(self, amount , add_sound):
        self.skill_points += amount
        add_sound.play()
        print(f"Gained {amount} skill points! Total: {self.skill_points}")

    def upgrade(self, upgrade_type):
        if self.skill_points < SKILL_POINT_COST:
            print("Not enough skill points!")
            return

        self.skill_points -= SKILL_POINT_COST

        if upgrade_type == 'health':
            self.max_health += UPGRADE_HEALTH_AMOUNT
            self.health = self.max_health # Full heal on upgrade
            print(f"Upgraded Max Health to {self.max_health}")
            
        elif upgrade_type == 'ammo':
            self.shotgun_ammo_capacity += UPGRADE_AMMO_AMOUNT
            self.shotgun_ammo = self.shotgun_ammo_capacity # Refill ammo
            print(f"Upgraded Ammo Capacity to {self.shotgun_ammo_capacity}")

        elif upgrade_type == 'reload':
            self.shotgun_reload_time = max(500, self.shotgun_reload_time - UPGRADE_RELOAD_SPEED_AMOUNT) # 0.5s min
            print(f"Upgraded Reload Speed to {self.shotgun_reload_time}ms")

        elif upgrade_type == 'fov':
            self.fov_angle += UPGRADE_FOV_AMOUNT
            print(f"Upgraded Flashlight Angle to {self.fov_angle}")
            
        elif upgrade_type == 'brightness':
            b = self.flashlight_brightness
            up = UPGRADE_BRIGHTNESS_AMOUNT
            c = self.flashlight_base_brightness
            self.flashlight_base_brightness = (min(255 , c[0] + up[0]) , min(255 , c[1] + up[1]) , min(255 , c[2] + up[2]))
            self.flashlight_brightness = (min(255, b[0] + up[0]), min(255, b[1] + up[1]), min(255, b[2] + up[2]))
            print(f"Upgraded Flashlight Brightness to {self.flashlight_brightness}")
        
        elif upgrade_type == 'pellet_count':
            self.shotgun_pellet_count = min(MAX_UPGRADABLE_PELLET_COUNT , self.shotgun_pellet_count + 1)
            print(f"Upgraded Shotgun pellet count to {self.shotgun_pellet_count}")
        
        return True


import pygame
import random
import sys
from maze import *
from player import *
from enemy import *
from boss import * # <-- Import the new Boss class

# --- Game States ---
GAME_STATE_MENU = 0
GAME_STATE_PLAYING = 1
GAME_STATE_GAME_OVER = 2
GAME_STATE_FADING = 3
GAME_STATE_BOSS_FIGHT = 4
GAME_STATE_WIN = 5

def create_light_aura(radius):
    surface = pygame.Surface((radius * 2, radius * 2))
    surface.fill(BLACK)
    
    for r in range(radius, 0, -1):
        brightness = int(255 * (1.0 - (r / radius)))
        color = (brightness, brightness, brightness)
        pygame.draw.circle(surface, color, (radius, radius), r)
        
    surface.set_colorkey(BLACK)
    return surface

def draw_menu(screen, title_font, button_font , is_controller_connected):
    screen.fill(BLACK)
    
    title_text = title_font.render("VISIONCURSE", True, RED)
    title_rect = title_text.get_rect(center=(WIN_WIDTH / 2, WIN_HEIGHT / 3))
    screen.blit(title_text, title_rect)
    
    if is_controller_connected:
        play_button_rect = pygame.Rect((WIN_WIDTH / 2) - 200, (WIN_HEIGHT / 2), 400, 50)
        pygame.draw.rect(screen, (0, 100, 0), play_button_rect)
        play_text = button_font.render("Press X to PLAY", True, WHITE)
    else:
        play_button_rect = pygame.Rect((WIN_WIDTH / 2) - 100, (WIN_HEIGHT / 2), 200, 50)
        pygame.draw.rect(screen, (0, 100, 0), play_button_rect)
        play_text = button_font.render("PLAY", True, WHITE)
    play_text_rect = play_text.get_rect(center=play_button_rect.center)
    screen.blit(play_text, play_text_rect)
    
    if is_controller_connected:
        quit_button_rect = pygame.Rect((WIN_WIDTH / 2) - 200, (WIN_HEIGHT / 2) + 70, 400, 50)
        pygame.draw.rect(screen, (100, 0, 0), quit_button_rect)
        quit_text = button_font.render("Press B to QUIT" , True , WHITE)
    else:
        quit_button_rect = pygame.Rect((WIN_WIDTH / 2) - 100, (WIN_HEIGHT / 2) + 70, 200, 50)
        pygame.draw.rect(screen, (100, 0, 0), quit_button_rect)
        quit_text = button_font.render("QUIT", True, WHITE)
    quit_text_rect = quit_text.get_rect(center=quit_button_rect.center)
    screen.blit(quit_text, quit_text_rect)
    
    return play_button_rect, quit_button_rect

def draw_tiled_floor(screen, tile_img, camera_offset):
    tile_width, tile_height = tile_img.get_size()
    
    # Calculate the top-left tile index based on camera
    # Use modulo to find the offset *within* a tile
    start_x = - (camera_offset[0] % tile_width)
    start_y = - (camera_offset[1] % tile_height)
    
    # Calculate how many tiles we need to draw
    num_tiles_x = (WIN_WIDTH // tile_width) + 2 # +2 to cover edges
    num_tiles_y = (WIN_HEIGHT // tile_height) + 2
    
    for x in range(num_tiles_x):
        for y in range(num_tiles_y):
            screen.blit(tile_img, (start_x + x * tile_width, start_y + y * tile_height))

# --- Function to draw the boss arena walls ---
def draw_arena_walls(screen, camera_offset):
    wall_rects = [
        pygame.Rect(0, 0, ARENA_WIDTH, ARENA_WALL_THICKNESS), # Top
        pygame.Rect(0, 0, ARENA_WALL_THICKNESS, ARENA_HEIGHT), # Left
        pygame.Rect(0, ARENA_HEIGHT - ARENA_WALL_THICKNESS, ARENA_WIDTH, ARENA_WALL_THICKNESS), # Bottom
        pygame.Rect(ARENA_WIDTH - ARENA_WALL_THICKNESS, 0, ARENA_WALL_THICKNESS, ARENA_HEIGHT) # Right
    ]
    
    for rect in wall_rects:
        # Check if the wall is on screen before drawing
        screen_x = rect.x - camera_offset[0]
        screen_y = rect.y - camera_offset[1]
        
        if (screen_x + rect.width < 0 or screen_x > WIN_WIDTH or
            screen_y + rect.height < 0 or screen_y > WIN_HEIGHT):
            continue
            
        pygame.draw.rect(screen, WHITE, (screen_x, screen_y, rect.width, rect.height))

# --- Main Game Function ---
def main():
    pygame.init()
    pygame.joystick.init()
    pygame.mixer.init()
    pygame.mixer.set_num_channels(16)

    screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    pygame.display.set_caption('VisionCurse - The Cave')
    clock = pygame.time.Clock()

    # --- Fonts ---
    ui_font = pygame.font.SysFont('Arial', 30)
    upgrade_font = pygame.font.SysFont('Arial', 22)
    game_over_font = pygame.font.SysFont('Arial', 100)
    menu_title_font = pygame.font.SysFont('Arial', 120)
    menu_button_font = pygame.font.SysFont('Arial', 40)

    try:
        floor_tile_img = pygame.image.load(TILE2_PATH).convert()
        floor_tile_img = pygame.transform.scale(floor_tile_img, (CELL_SIZE, CELL_SIZE))
    except pygame.error as e:
        print(f"Error loading floor tile: {e}")
        floor_tile_img = pygame.Surface((CELL_SIZE, CELL_SIZE))
        floor_tile_img.fill(PURPLE)

    # --- Load Sounds ---
    try:
        sounds = {
            'shotgun_fire': pygame.mixer.Sound(SOUND_SHOTGUN_FIRE),
            'shotgun_reload': pygame.mixer.Sound(SOUND_SHOTGUN_RELOAD),
            'swap_item': pygame.mixer.Sound(SOUND_SWAP_ITEM),
            'footsteps': pygame.mixer.Sound(SOUND_PLAYER_MOVE),
            'enemy_attack': pygame.mixer.Sound(SOUND_ENEMY_ATTACK),
            'skill_upgrade': pygame.mixer.Sound(SOUND_SKILL_UPGRADE),
            'skill_gain': pygame.mixer.Sound(SOUND_SKILL_GAIN),
            'enemy_alert': pygame.mixer.Sound(SOUND_ENEMY_ALERT),
            'boss_hit': pygame.mixer.Sound(SOUND_BOSS_HIT),
            'boss_death': pygame.mixer.Sound(SOUND_BOSS_DEATH),
            'boss_attack': pygame.mixer.Sound(SOUND_BOSS_ATTACK),
            'win_game': pygame.mixer.Sound(SOUND_WIN_GAME)
        }
        
        sounds['footsteps'].set_volume(0.4)
        sounds['shotgun_fire'].set_volume(0.7)
        sounds['swap_item'].set_volume(0.7)
        
        pygame.mixer.music.load(MUSIC_BACKGROUND)
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play(-1)

    except pygame.error as e:
        print(f"Error loading sound: {e}")
        # Create dummy sounds
        sounds = {k: pygame.mixer.Sound(buffer=b"") for k in [
            'shotgun_fire', 'shotgun_reload', 'swap_item', 'footsteps',
            'enemy_attack', 'skill_upgrade', 'skill_gain', 'enemy_alert',
            'boss_hit', 'boss_death', 'boss_attack', 'win_game'
        ]}
        pass
        
    footstep_channel = pygame.mixer.Channel(1)

    # --- Game Variables ---
    grid = gen_maze()
    start_x = (CELL_SIZE / 2) - (PLAYER_SIZE / 2)
    start_y = (CELL_SIZE / 2) - (PLAYER_SIZE / 2)
    player = Player([start_x, start_y], PLAYER_SIZE)
    enemies = []
    boss = None # Boss variable
    
    light_surface = pygame.Surface((WIN_WIDTH , WIN_HEIGHT))
    
    # --- MODIFICATION: Create both auras ---
    light_aura_sprite_normal = create_light_aura(LIGHT_AURA_RADIUS)
    light_aura_sprite_boss = create_light_aura(BOSS_LIGHT_AURA_RADIUS)
    # --- END MODIFICATION ---
    
    pellet_lines = []
    pellet_draw_start_time = 0
    is_shaking = False
    shake_start_time = 0 
    last_enemy_spawn_time = pygame.time.get_ticks()
    
    current_spawn_interval = ENEMY_SPAWN_INTERVAL
    current_max_enemies = ENEMY_MAX_COUNT
    current_detection_range = ENEMY_DETECTION_RANGE

    camera_offset = [0, 0]
    move = {"Up": False, "Down": False, "Left": False, "Right": False , "Joystick_Up" : False , "Joystick_Down" : False , "Joystick_Left":False , "Joystick_Right":False}
    
    # --- State Management ---
    game_state = GAME_STATE_MENU # Start at menu
    play_button_rect = None
    quit_button_rect = None
    
    # --- Fade Transition Variables ---
    fade_surface = pygame.Surface((WIN_WIDTH, WIN_HEIGHT))
    fade_surface.fill(BLACK)
    fade_alpha = 0
    fading_to_state = -1 # State to go to after fading

    flashlight_max_trade_off = FLASHLIGHT_TRADE_OFF_MAX_ENEMIES_INCREASE

    joysticks = []
    joystick_shoot = False
    swap_cooldown = 30
    shoot_cooldown = 30

    skill_upgrade_cooldown = 4

    # Main game loop
    running = True
    while running:
        current_time = pygame.time.get_ticks()
        dx, dy = 0, 0 # Reset movement deltas each frame
        horizontal_aiming_component = 0
        vertical_aiming_component = 0

        if pygame.joystick.get_count():
            is_controller_connected = True
        else:
            is_controller_connected = False

        for joystick in joysticks:
            if joystick.get_axis(0) > 0.001:
                move["Joystick_Right"] = True
            elif joystick.get_axis(0) < -0.001:
                move["Joystick_Left"] = True
            else:
                move["Joystick_Right"] = False
                move["Joystick_Left"] = False
            if joystick.get_axis(1) > 0.001:
                move["Joystick_Down"] = True
            elif joystick.get_axis(1) < -0.001:
                move["Joystick_Up"] = True
            else:
                move["Joystick_Down"] = False
                move["Joystick_Up"] = False
            print("Joystick Up : " , move["Joystick_Up"])
            print("Joystick Down : " , move["Joystick_Down"])
            
            if joystick.get_axis(0) > 0.001 or joystick.get_axis(0) < -0.001:
                dx = joystick.get_axis(0)
            if joystick.get_axis(1) > 0.001 or joystick.get_axis(1) < -0.001:
                dy = joystick.get_axis(1)

            if abs(joystick.get_axis(4)) > 0.001:
                vertical_aiming_component = joystick.get_axis(4)
            if abs(joystick.get_axis(3)) > 0.001:
                horizontal_aiming_component = joystick.get_axis(3)

            if(joystick.get_axis(5) > 0.99):
                joystick_shoot = True
            
            if joystick.get_button(4):
                if swap_cooldown == 30:
                    player.swap_item(sounds["swap_item"])
                    swap_cooldown = 0
            
            if game_state == GAME_STATE_MENU and joystick.get_button(2):
                game_state = GAME_STATE_PLAYING
            if game_state == GAME_STATE_MENU and joystick.get_button(1):
                running = False

            print("hat : " , joystick.get_hat(0))

            if game_state == GAME_STATE_PLAYING:
                if skill_upgrade_cooldown == 4:
                    if joystick.get_hat(0)[1] == 1:
                        sounds['skill_upgrade'].play()
                        player.upgrade('health')
                    elif joystick.get_hat(0)[1] == -1:
                        sounds['skill_upgrade'].play()
                        player.upgrade('ammo')
                    elif joystick.get_hat(0)[0] == -1:
                        sounds['skill_upgrade'].play()
                        player.upgrade('reload')
                    elif joystick.get_hat(0)[0] == 1:
                        sounds['skill_upgrade'].play()
                        if player.upgrade('fov'):
                            current_spawn_interval = max(500, current_spawn_interval - FLASHLIGHT_TRADE_OFF_SPAWN_INTERVAL_REDUCTION)
                            current_max_enemies += flashlight_max_trade_off
                            flashlight_max_trade_off *= 2
                            current_detection_range += FLASHLIGHT_TRADE_OFF_DETECTION_RANGE_INCREASE
                            print(f"WARNING: Difficulty increased! Spawn Rate: {current_spawn_interval}ms, Max Enemies: {current_max_enemies}, Detect Range: {current_detection_range}")
                    elif joystick.get_button(2):
                        sounds['skill_upgrade'].play()
                        if player.upgrade('brightness'):
                            current_spawn_interval = max(500, current_spawn_interval - FLASHLIGHT_TRADE_OFF_SPAWN_INTERVAL_REDUCTION)
                            current_max_enemies += flashlight_max_trade_off
                            flashlight_max_trade_off *= 2
                            current_detection_range += FLASHLIGHT_TRADE_OFF_DETECTION_RANGE_INCREASE
                            print(f"WARNING: Difficulty increased! Spawn Rate: {current_spawn_interval}ms, Max Enemies: {current_max_enemies}, Detect Range: {current_detection_range}")
                    elif joystick.get_button(3):
                        sounds['skill_upgrade'].play()
                        player.upgrade('pellet_count')
                    skill_upgrade_cooldown = 0


            if swap_cooldown < 30:
                swap_cooldown+=1
            
            print("1: " , joystick.get_axis(2))
            print("2: " , joystick.get_axis(5))
            print("button : " , joystick.get_button(4))
            
            # print("horizontal : " , horizontal_aiming_component)
            # print("vertical : " , vertical_aiming_component)

        if shoot_cooldown < 30:
            shoot_cooldown += 1
        if skill_upgrade_cooldown < 4:
            skill_upgrade_cooldown += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False    
            
            if event.type == pygame.JOYDEVICEADDED:
                joy = pygame.joystick.Joystick(event.device_index)
                joysticks.append(joy)
            
            if game_state == GAME_STATE_MENU:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if play_button_rect and play_button_rect.collidepoint(event.pos):
                            game_state = GAME_STATE_PLAYING
                        if quit_button_rect and quit_button_rect.collidepoint(event.pos):
                            running = False

            elif game_state == GAME_STATE_PLAYING or game_state == GAME_STATE_BOSS_FIGHT:
                # --- Events for both Play and Boss states ---
                if ((event.type == pygame.MOUSEBUTTONDOWN and  event.button == 1) or joystick_shoot == True) and player.health > 0:
                    if horizontal_aiming_component or vertical_aiming_component:
                        mouse_x , mouse_y = horizontal_aiming_component , vertical_aiming_component
                        target_angle = math.atan2(mouse_y , mouse_x)
                    else:
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        player_screen_center = (player.pos[0] - camera_offset[0] , player.pos[1] - camera_offset[1])
                        target_angle = math.atan2(mouse_y - player_screen_center[1], 
                                              mouse_x - player_screen_center[0])
                    if shoot_cooldown == 30:
                        is_boss = (game_state == GAME_STATE_BOSS_FIGHT)
                        hits = player.shoot(target_angle, grid, sounds['shotgun_fire'], sounds['shotgun_reload'], is_boss)
                        joystick_shoot = False
                        shoot_cooldown = 0
                    
                        if hits:
                            pellet_lines = hits
                            pellet_draw_start_time = current_time
                            is_shaking = True
                            shake_start_time = current_time
                    
                if event.type == pygame.KEYDOWN:
                    if player.health > 0:
                        if event.key == pygame.K_ESCAPE:
                            running = False
                        if event.key == pygame.K_s:
                            move["Down"] = True
                        if event.key == pygame.K_w:
                            move["Up"] = True
                        if event.key == pygame.K_d:
                            move["Right"] = True
                        if event.key == pygame.K_a:
                            move["Left"] = True

                        if event.key == SWAP_KEY:
                            player.swap_item(sounds['swap_item'])
                        if event.key == RELOAD_KEY:
                            player.reload(sounds['shotgun_reload'])
                        
                        if game_state == GAME_STATE_PLAYING:
                            if event.key == UPGRADE_KEY_HEALTH:
                                sounds['skill_upgrade'].play()
                                player.upgrade('health')
                            elif event.key == UPGRADE_KEY_AMMO:
                                sounds['skill_upgrade'].play()
                                player.upgrade('ammo')
                            elif event.key == UPGRADE_KEY_RELOAD:
                                sounds['skill_upgrade'].play()
                                player.upgrade('reload')
                            elif event.key == UPGRADE_KEY_FOV:
                                sounds['skill_upgrade'].play()
                                if player.upgrade('fov'):
                                    current_spawn_interval = max(500, current_spawn_interval - FLASHLIGHT_TRADE_OFF_SPAWN_INTERVAL_REDUCTION)
                                    current_max_enemies += flashlight_max_trade_off
                                    flashlight_max_trade_off *= 2
                                    current_detection_range += FLASHLIGHT_TRADE_OFF_DETECTION_RANGE_INCREASE
                                    print(f"WARNING: Difficulty increased! Spawn Rate: {current_spawn_interval}ms, Max Enemies: {current_max_enemies}, Detect Range: {current_detection_range}")
                            elif event.key == UPGRADE_KEY_BRIGHTNESS:
                                sounds['skill_upgrade'].play()
                                if player.upgrade('brightness'):
                                    current_spawn_interval = max(500, current_spawn_interval - FLASHLIGHT_TRADE_OFF_SPAWN_INTERVAL_REDUCTION)
                                    current_max_enemies += flashlight_max_trade_off
                                    flashlight_max_trade_off *= 2
                                    current_detection_range += FLASHLIGHT_TRADE_OFF_DETECTION_RANGE_INCREASE
                                    print(f"WARNING: Difficulty increased! Spawn Rate: {current_spawn_interval}ms, Max Enemies: {current_max_enemies}, Detect Range: {current_detection_range}")
                            elif event.key == UPGRADE_PELLET_COUNT:
                                sounds['skill_upgrade'].play()
                                player.upgrade('pellet_count')

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_s:
                        move["Down"] = False
                    if event.key == pygame.K_w:
                        move["Up"] = False
                    if event.key == pygame.K_d:
                        move["Right"] = False
                    if event.key == pygame.K_a:
                        move["Left"] = False
            
            elif game_state == GAME_STATE_GAME_OVER or game_state == GAME_STATE_WIN:
                 if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    # Reset game
                    main()
                    return

        
        if game_state == GAME_STATE_PLAYING:
            if player.health > 0:
                if move["Up"]: dy = -1
                if move["Down"]: dy = 1
                if move["Left"]: dx = -1
                if move["Right"]: dx = 1
                
                if (dx != 0 or dy != 0) and not footstep_channel.get_busy():
                    footstep_channel.play(sounds['footsteps'], -1)
                elif (dx == 0 and dy == 0) and footstep_channel.get_busy():
                    footstep_channel.stop()
                
                player.move_player(grid, dx, dy)
                player.update(move , camera_offset , horizontal_aiming_component , vertical_aiming_component) 

                # --- Enemy Spawning ---
                if current_time - last_enemy_spawn_time > current_spawn_interval:
                    if len(enemies) < current_max_enemies:
                        player_col = int(player.get_center_pos()[0] // CELL_SIZE)
                        player_row = int(player.get_center_pos()[1] // CELL_SIZE)
                        spawn_col, spawn_row = player_col, player_row
                        dist = 0
                        while dist < 5 or dist > 7:
                            spawn_col = random.randint(0, COLS - 1)
                            spawn_row = random.randint(0, ROWS - 1)
                            dist = math.dist((player_col, player_row), (spawn_col, spawn_row))
                        spawn_x = spawn_col * CELL_SIZE + (CELL_SIZE / 2) - (ENEMY_SIZE / 2)
                        spawn_y = spawn_row * CELL_SIZE + (CELL_SIZE / 2) - (ENEMY_SIZE / 2)
                        enemies.append(Enemy([spawn_x, spawn_y], [ENEMY_SIZE, ENEMY_SIZE]))
                        last_enemy_spawn_time = current_time
                
                for enemy in enemies:
                    enemy.update(player, grid , current_detection_range, sounds['enemy_attack'], sounds['enemy_alert'])
                    if enemy.is_far:
                        enemies.remove(enemy)

                if pellet_lines:
                    dead_enemies = []
                    for enemy in enemies:
                        enemy_rect = enemy.get_rect()
                        pellets_hit = 0
                        for start, end in pellet_lines:
                            if enemy_rect.clipline(start, end):
                                pellets_hit += 1
                        if pellets_hit > 0:
                            is_dead = enemy.take_damage(pellets_hit * SHOTGUN_PELLET_DAMAGE)
                            if is_dead:
                                dead_enemies.append(enemy)
                    
                    for enemy in dead_enemies:
                        enemies.remove(enemy) 
                        player.add_skill_points(ENEMY_KILL_REWARD, sounds['skill_gain'])
            
            if player.health <= 0:
                game_state = GAME_STATE_GAME_OVER
                footstep_channel.stop()
                pygame.mixer.music.stop()

            # --- Check for Boss Trigger ---
            player_col = int(player.get_center_pos()[0] // CELL_SIZE)
            player_row = int(player.get_center_pos()[1] // CELL_SIZE)
            if player_col == COLS - 1 and player_row == ROWS - 1:
                game_state = GAME_STATE_FADING
                fading_to_state = GAME_STATE_BOSS_FIGHT
                fade_alpha = 0 
                footstep_channel.stop()
                pygame.mixer.music.fadeout(1000)
            
            # --- Camera Update (Maze) ---
            player_center_x = player.pos[0] + PLAYER_SIZE / 2
            player_center_y = player.pos[1] + PLAYER_SIZE / 2
            camera_offset[0] = player_center_x - (WIN_WIDTH / 2)
            camera_offset[1] = player_center_y - (WIN_HEIGHT / 2)
            camera_offset[0] = max(0, min(camera_offset[0], WORLD_WIDTH - WIN_WIDTH))
            camera_offset[1] = max(0, min(camera_offset[1], WORLD_HEIGHT - WIN_HEIGHT))

        elif game_state == GAME_STATE_BOSS_FIGHT:
            if player.health > 0:
                if move["Up"]: dy = -1
                if move["Down"]: dy = 1
                if move["Left"]: dx = -1
                if move["Right"]: dx = 1
                
                if (dx != 0 or dy != 0) and not footstep_channel.get_busy():
                    footstep_channel.play(sounds['footsteps'], -1)
                elif (dx == 0 and dy == 0) and footstep_channel.get_busy():
                    footstep_channel.stop()
                
                player.move_player_arena(dx, dy)
                player.update(move , camera_offset , horizontal_aiming_component , vertical_aiming_component) 

                if boss:
                    boss.update(player, sounds['boss_attack'])
                
                if pellet_lines and boss:
                    pellets_hit = 0
                    boss_rect = boss.get_rect()
                    for start, end in pellet_lines:
                        if boss_rect.clipline(start, end):
                            pellets_hit += 1
                    
                    if pellets_hit > 0:
                        is_dead = boss.take_damage(pellets_hit * SHOTGUN_PELLET_DAMAGE, sounds['boss_hit'])
                        if is_dead:
                            sounds['boss_death'].play()
                            game_state = GAME_STATE_WIN
                            footstep_channel.stop()
                            pygame.mixer.music.fadeout(1000)
                            sounds['win_game'].play()

            if player.health <= 0:
                game_state = GAME_STATE_GAME_OVER
                footstep_channel.stop()
                pygame.mixer.music.stop()
            
            # --- Camera Update (Arena) ---
            player_center_x = player.pos[0] + PLAYER_SIZE / 2
            player_center_y = player.pos[1] + PLAYER_SIZE / 2
            camera_offset[0] = player_center_x - (WIN_WIDTH / 2)
            camera_offset[1] = player_center_y - (WIN_HEIGHT / 2)
            camera_offset[0] = max(0, min(camera_offset[0], ARENA_WIDTH - WIN_WIDTH))
            camera_offset[1] = max(0, min(camera_offset[1], ARENA_HEIGHT - WIN_HEIGHT))
        
        elif game_state == GAME_STATE_FADING:
            if fade_alpha < 255 and fading_to_state != -1: # Fading IN (to black)
                fade_alpha = min(255, fade_alpha + 5)
                if fade_alpha == 255: # Reached black
                    if fading_to_state == GAME_STATE_BOSS_FIGHT:
                        enemies.clear() # Clear maze enemies
                        player.pos = [ARENA_WIDTH / 2, ARENA_HEIGHT - (PLAYER_SIZE * 4)]
                        boss = Boss(
                            [ARENA_WIDTH / 2 - BOSS_SIZE / 2, ARENA_HEIGHT / 4],
                            [BOSS_SIZE, BOSS_SIZE],
                            BOSS_HEALTH
                        )
                        pygame.mixer.music.load(MUSIC_BOSS_FIGHT)
                        pygame.mixer.music.set_volume(0.4)
                        pygame.mixer.music.play(-1)
                    
                    fading_to_state = -1
            
            elif fade_alpha > 0 and fading_to_state == -1: # Fading OUT (from black)
                fade_alpha = max(0, fade_alpha - 5)
                if fade_alpha == 0:
                    game_state = GAME_STATE_BOSS_FIGHT # Finished fading

        if is_shaking and current_time - shake_start_time < IMPACT_SHAKE_DURATION:
            camera_offset[0] += random.randint(-IMPACT_SHAKE_STRENGTH, IMPACT_SHAKE_STRENGTH)
            camera_offset[1] += random.randint(-IMPACT_SHAKE_STRENGTH, IMPACT_SHAKE_STRENGTH)
        else:
            is_shaking = False

        draw_tiled_floor(screen , floor_tile_img , camera_offset)

        if game_state == GAME_STATE_MENU:
            play_button_rect, quit_button_rect = draw_menu(screen, menu_title_font, menu_button_font , is_controller_connected)

        elif game_state == GAME_STATE_PLAYING:
            for c in range(COLS):
                for r in range(ROWS):
                    grid[c][r].draw(screen, camera_offset)
            
            start_screen_x = 0 - camera_offset[0]
            start_screen_y = 0 - camera_offset[1]
            pygame.draw.rect(screen, START_BLUE, (start_screen_x, start_screen_y, CELL_SIZE, CELL_SIZE))
            end_screen_x = ((COLS - 1) * CELL_SIZE) - camera_offset[0]
            end_screen_y = ((ROWS - 1) * CELL_SIZE) - camera_offset[1]
            pygame.draw.rect(screen, RED, (end_screen_x, end_screen_y, CELL_SIZE, CELL_SIZE))

            for enemy in enemies:
                enemy.render(screen, camera_offset)
            player.render(screen, camera_offset)

        elif game_state == GAME_STATE_BOSS_FIGHT:
            draw_arena_walls(screen, camera_offset)
            if boss:
                boss.render(screen, camera_offset)
            player.render(screen, camera_offset)

        # --- Draw lighting (Common to Play and Boss) ---
        if game_state == GAME_STATE_PLAYING or game_state == GAME_STATE_BOSS_FIGHT:
            if pellet_lines and current_time - pellet_draw_start_time < SHOTGUN_PELLET_LIFETIME:
                for start_world, end_world in pellet_lines:
                    start_screen = (start_world[0] - camera_offset[0], start_world[1] - camera_offset[1])
                    end_screen = (end_world[0] - camera_offset[0], end_world[1] - camera_offset[1])
                    pygame.draw.line(screen, SHOTGUN_PELLET_COLOR, start_screen, end_screen, SHOTGUN_PELLET_THICKNESS)
            else:
                pellet_lines.clear()

            light_surface.fill(BLACK)
            player_screen_center = player.get_aura_center(camera_offset)
            if player.equipped_item == "flashlight":
                is_boss = (game_state == GAME_STATE_BOSS_FIGHT)
                # Only cast rays in maze
                if not is_boss: 
                    vision_polygon_world = cast_rays(player, grid , player.fov_angle , camera_offset , horizontal_aiming_component , vertical_aiming_component)
                    vision_polygon_screen = []
                    for world_pos in vision_polygon_world:
                        screen_x = world_pos[0] - camera_offset[0]
                        screen_y = world_pos[1] - camera_offset[1]
                        vision_polygon_screen.append((screen_x, screen_y))

                    if len(vision_polygon_screen) > 2:
                        base_c = player.flashlight_base_brightness
                        max_c = player.flashlight_brightness
                        steps = FLASHLIGHT_GRADIENT_STEPS
                        ray_end_points = vision_polygon_screen[1:]
                        for i in range(steps, 0, -1):
                            scale = i / steps
                            r = max_c[0] - (max_c[0] - base_c[0]) * scale
                            g = max_c[1] - (max_c[1] - base_c[1]) * scale
                            b = max_c[2] - (max_c[2] - base_c[2]) * scale
                            color = (int(r), int(g), int(b))
                            scaled_polygon = [player_screen_center]
                            for p in ray_end_points:
                                vec_x = p[0] - player_screen_center[0]
                                vec_y = p[1] - player_screen_center[1]
                                scaled_x = player_screen_center[0] + vec_x * scale
                                scaled_y = player_screen_center[1] + vec_y * scale
                                scaled_polygon.append((scaled_x, scaled_y))
                            pygame.draw.polygon(light_surface, color, scaled_polygon)
            
            if game_state == GAME_STATE_BOSS_FIGHT:
                current_aura_sprite = light_aura_sprite_boss
            else:
                current_aura_sprite = light_aura_sprite_normal

            aura_rect = current_aura_sprite.get_rect(center=player_screen_center)
            light_surface.blit(current_aura_sprite, aura_rect, special_flags=pygame.BLEND_RGB_ADD)

            screen.blit(light_surface, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

            # --- Draw UI ---
            health_percent = player.health / player.max_health
            bg_rect = pygame.Rect(10, 10, 300, 30)
            fg_rect = pygame.Rect(10, 10, int(300 * health_percent), 30)
            pygame.draw.rect(screen, (100,0,0), bg_rect)
            pygame.draw.rect(screen, (0,200,0), fg_rect)

            if player.equipped_item == "shotgun":
                ammo_text = "Reloading..." if player.is_reloading else f"Ammo: {player.shotgun_ammo} / {player.shotgun_ammo_capacity}"
                text_surface = ui_font.render(ammo_text, True, WHITE)
                screen.blit(text_surface, (10, WIN_HEIGHT - 40))
            
            if game_state == GAME_STATE_PLAYING:
                sp_text = ui_font.render(f"Skill Points: {player.skill_points}", True, WHITE)
                sp_rect = sp_text.get_rect(right=WIN_WIDTH - sp_text.get_width(), top=10)
                screen.blit(sp_text, sp_rect)
                if player.skill_points > 0:
                    # ... (upgrade UI logic) ...
                    y_offset = 50
                    menu_title = upgrade_font.render("Upgrades Available (Cost: 1)", True, (255, 255, 0))
                    screen.blit(menu_title, (sp_rect.left, y_offset))
                    y_offset += 30
                    if pygame.joystick.get_count():
                        upgrades = [
                            f"[D-pad Up] Max Health (+{UPGRADE_HEALTH_AMOUNT})",
                            f"[D-pad Down] Ammo Capacity (+{UPGRADE_AMMO_AMOUNT})",
                            f"[D-pad Left] Reload Speed (-{UPGRADE_RELOAD_SPEED_AMOUNT}ms)",
                            f"[D-pad Right] Flashlight Angle (+{UPGRADE_FOV_AMOUNT})",
                            f"[X] Flashlight Brightness",
                            f"[Y] Shotgun Pellet count"
                        ]
                    else:
                        upgrades = [
                            f"[1] Max Health (+{UPGRADE_HEALTH_AMOUNT})",
                            f"[2] Ammo Capacity (+{UPGRADE_AMMO_AMOUNT})",
                            f"[3] Reload Speed (-{UPGRADE_RELOAD_SPEED_AMOUNT}ms)",
                            f"[4] Flashlight Angle (+{UPGRADE_FOV_AMOUNT})",
                            f"[5] Flashlight Brightness",
                            f"[6] Shotgun Pellet count"
                        ]
                    for text in upgrades:
                        text_surf = upgrade_font.render(text, True, WHITE)
                        screen.blit(text_surf, (sp_rect.left, y_offset))
                        y_offset += 25

        elif game_state == GAME_STATE_GAME_OVER:
            text = game_over_font.render("YOU DIED", True, (150, 0, 0))
            text_rect = text.get_rect(center=(WIN_WIDTH / 2, WIN_HEIGHT / 2))
            s = pygame.Surface((WIN_WIDTH, WIN_HEIGHT), pygame.SRCALPHA)
            s.fill((0,0,0,150)) 
            screen.blit(s, (0,0))
            screen.blit(text, text_rect)
            prompt_text = ui_font.render("Click anywhere to restart", True, WHITE)
            prompt_rect = prompt_text.get_rect(center=(WIN_WIDTH / 2, WIN_HEIGHT / 2 + 100))
            screen.blit(prompt_text, prompt_rect)

        elif game_state == GAME_STATE_WIN:
            text = game_over_font.render("YOU WON", True, (0, 255, 0))
            text_rect = text.get_rect(center=(WIN_WIDTH / 2, WIN_HEIGHT / 2))
            s = pygame.Surface((WIN_WIDTH, WIN_HEIGHT), pygame.SRCALPHA)
            s.fill((0,0,0,150)) 
            screen.blit(s, (0,0))
            screen.blit(text, text_rect)
            prompt_text = ui_font.render("Click anywhere to return to menu", True, WHITE)
            prompt_rect = prompt_text.get_rect(center=(WIN_WIDTH / 2, WIN_HEIGHT / 2 + 100))
            screen.blit(prompt_text, prompt_rect)

        # --- Draw Fade (On top of everything) ---
        if game_state == GAME_STATE_FADING:
            fade_surface.set_alpha(fade_alpha)
            screen.blit(fade_surface, (0, 0))

        font = pygame.font.SysFont("Futura" , 30)
        if pygame.joystick.get_count():
            img = font.render("Controller Connected !" , True , "green")
            screen.blit(img , (WIN_WIDTH - img.get_width() , WIN_HEIGHT - img.get_height()))
        
            
        pygame.display.flip()
        
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
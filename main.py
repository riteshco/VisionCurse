import pygame
from maze import *
from player import *

def create_light_aura(radius):
    surface = pygame.Surface((radius * 2, radius * 2))
    surface.fill(BLACK)
    
    # Draw concentric circles, getting dimmer from center
    for r in range(radius, 0, -1):
        brightness = int(255 * (1.0 - (r / radius)))
        color = (brightness, brightness, brightness)
        pygame.draw.circle(surface, color, (radius, radius), r)
        
    # Set black to be transparent (colorkey)
    surface.set_colorkey(BLACK)
    return surface

# --- Main Game Function ---
def main():
    pygame.init()

    screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    pygame.display.set_caption('VisionCurse - The Cave')
    clock = pygame.time.Clock()

    # --- Pre-generate the maze ---
    grid = gen_maze()
    
    # --- Initialize Player ---
    # Start player in the middle of the first cell
    start_x = (CELL_SIZE / 2) - (PLAYER_SIZE / 2)
    start_y = (CELL_SIZE / 2) - (PLAYER_SIZE / 2)
    player = Player([start_x, start_y], PLAYER_SIZE)

    light_surface = pygame.Surface((WIN_WIDTH , WIN_HEIGHT))
    light_aura_sprite = create_light_aura(LIGHT_AURA_RADIUS)
    
    # --- Camera Offset ---
    # This will store the [x, y] of the top-left corner of the camera
    camera_offset = [0, 0]

    move = {"Up": False, "Down": False, "Left": False, "Right": False}

    # Main game loop
    running = True
    while running:
        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False    
            if event.type == pygame.KEYDOWN:
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
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_s:
                    move["Down"] = False
                if event.key == pygame.K_w:
                    move["Up"] = False
                if event.key == pygame.K_d:
                    move["Right"] = False
                if event.key == pygame.K_a:
                    move["Left"] = False

        # --- Player Movement ---
        dx, dy = 0, 0
        if move["Up"]:
            dy = -1
        if move["Down"]:
            dy = 1
        if move["Left"]:
            dx = -1
        if move["Right"]:
            dx = 1

        # Move player based on world coordinates
        player.move_player(grid, dx, dy)

        # --- Camera Update ---
        # Center the camera on the player's center
        player_center_x = player.pos[0] + PLAYER_SIZE / 2
        player_center_y = player.pos[1] + PLAYER_SIZE / 2
        
        camera_offset[0] = player_center_x - (WIN_WIDTH / 2)
        camera_offset[1] = player_center_y - (WIN_HEIGHT / 2)

        # --- Camera Clamping ---
        # Stop the camera from moving off the edge of the world
        camera_offset[0] = max(0, min(camera_offset[0], WORLD_WIDTH - WIN_WIDTH))
        camera_offset[1] = max(0, min(camera_offset[1], WORLD_HEIGHT - WIN_HEIGHT))


        # --- Drawing ---
        screen.fill(BLACK)

        # Draw the maze (cells will check if they are on-screen)
        for c in range(COLS):
            for r in range(ROWS):
                grid[c][r].draw(screen, camera_offset)
        
        # Draw Start and End indicators
        start_screen_x = 0 - camera_offset[0]
        start_screen_y = 0 - camera_offset[1]
        pygame.draw.rect(screen, START_BLUE, (start_screen_x, start_screen_y, CELL_SIZE, CELL_SIZE))
        
        end_screen_x = ((COLS - 1) * CELL_SIZE) - camera_offset[0]
        end_screen_y = ((ROWS - 1) * CELL_SIZE) - camera_offset[1]
        pygame.draw.rect(screen, RED, (end_screen_x, end_screen_y, CELL_SIZE, CELL_SIZE))

        # Draw the player
        player.render(screen, camera_offset)

        light_surface.fill(BLACK)

        vision_polygon_world = cast_rays(player, grid , camera_offset)

        player_screen_center = player.get_aura_center(camera_offset)
        vision_polygon_screen = []
        for world_pos in vision_polygon_world:
            screen_x = world_pos[0] - camera_offset[0]
            screen_y = world_pos[1] - camera_offset[1]
            vision_polygon_screen.append((screen_x, screen_y))

        if len(vision_polygon_screen) > 2:
            
            # Calculate brightness steps
            base_c = FLASHLIGHT_BASE_BRIGHTNESS
            max_c = FLASHLIGHT_MAX_BRIGHTNESS
            steps = FLASHLIGHT_GRADIENT_STEPS
            
            # Get the points *without* the player center (which is at index 0)
            ray_end_points = vision_polygon_screen[1:]
            
            for i in range(steps, 0, -1): # Draw from biggest (dimmest) to smallest (brightest)
                scale = i / steps
                
                # Calculate color for this step (dimmest to brightest)
                r = max_c[0] - (max_c[0] - base_c[0]) * scale
                g = max_c[1] - (max_c[1] - base_c[1]) * scale
                b = max_c[2] - (max_c[2] - base_c[2]) * scale
                color = (int(r), int(g), int(b))

                # Create the scaled polygon for this step
                scaled_polygon = [player_screen_center] # Start at the player
                for p in ray_end_points:
                    # Get vector from player to point
                    vec_x = p[0] - player_screen_center[0]
                    vec_y = p[1] - player_screen_center[1]
                    
                    # Scale vector and add back to player center
                    scaled_x = player_screen_center[0] + vec_x * scale
                    scaled_y = player_screen_center[1] + vec_y * scale
                    scaled_polygon.append((scaled_x, scaled_y))
                
                # Draw the polygon
                pygame.draw.polygon(light_surface, color, scaled_polygon)
        
        aura_rect = light_aura_sprite.get_rect(center=player_screen_center)
        light_surface.blit(light_aura_sprite, aura_rect, special_flags=pygame.BLEND_RGB_ADD)

        screen.blit(light_surface, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

        # Update the display
        pygame.display.flip()
        
        # Cap the framerate
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
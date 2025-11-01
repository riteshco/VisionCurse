import pygame
from maze import *
from player import *


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

    fog_surface = pygame.Surface((WIN_WIDTH, WIN_HEIGHT), pygame.SRCALPHA)
    
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

        vision_polygon_world = cast_rays(player, grid , camera_offset)

        vision_polygon_screen = []
        for world_pos in vision_polygon_world:
            screen_x = world_pos[0] - camera_offset[0]
            screen_y = world_pos[1] - camera_offset[1]
            vision_polygon_screen.append((screen_x, screen_y))

        fog_surface.fill((0, 0, 0, 255))

        if len(vision_polygon_screen) > 2: # Need at least 3 points to draw
            pygame.draw.circle(fog_surface, (0, 0, 0, 0), player.get_aura_center(camera_offset), AURA_RADIUS)
            pygame.draw.polygon(fog_surface, (0, 0, 0, 0), vision_polygon_screen)
        
        screen.blit(fog_surface, (0, 0))

        # Update the display
        pygame.display.flip()
        
        # Cap the framerate
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
import pygame
import sys
import random
import math
from cell import Cell
from constants import *

def remove_walls(current, next_cell):
    dx = current.col - next_cell.col
    if dx == 1:
        current.walls['left'] = False
        next_cell.walls['right'] = False
    elif dx == -1:
        current.walls['right'] = False
        next_cell.walls['left'] = False
    
    dy = current.row - next_cell.row
    if dy == 1:
        current.walls['top'] = False
        next_cell.walls['bottom'] = False
    elif dy == -1:
        current.walls['bottom'] = False
        next_cell.walls['top'] = False

def gen_maze():
    grid = [[Cell(c, r) for r in range(ROWS)] for c in range(COLS)]
    stack = []
    current_cell = grid[0][0]
    current_cell.visited = True
    
    generation_complete = False
    while not generation_complete:
        current_cell.visited = True
        next_cell = current_cell.check_neighbors(grid)
        
        if next_cell:
            stack.append(current_cell)
            remove_walls(current_cell, next_cell)
            current_cell = next_cell
        elif stack:
            current_cell = stack.pop()
        else:
            generation_complete = True

    grid[0][0].walls['top'] = False
    grid[COLS - 1][ROWS - 1].walls['bottom'] = False
    
    print("Maze generation complete.")
    return grid

def cast_rays(player , grid , fov_angle , camera_offset, horizontal_aiming_component , vertical_aiming_component , is_boss_fight=False):
    fov_points = []
    player_center_world = player.get_center_pos()

    if horizontal_aiming_component or vertical_aiming_component:
        center_angle = math.atan2(vertical_aiming_component , horizontal_aiming_component)
    else:
        mouse_x, mouse_y = pygame.mouse.get_pos()

        player_screen_x = player.pos[0] - camera_offset[0]
        player_screen_y = player.pos[1] - camera_offset[1]

        center_angle = math.atan2(mouse_y - player_screen_y, mouse_x - player_screen_x)

    start_angle = center_angle - math.radians(fov_angle / 2)
    angle_step = math.radians(fov_angle) / RAY_COUNT

    fov_points.append(player_center_world)

    for i in range(RAY_COUNT + 1):
        current_angle = start_angle + i * angle_step
        
        step_x = math.cos(current_angle)
        step_y = math.sin(current_angle)
        
        ray_x, ray_y = player_center_world
        current_dist = 0
        hit_wall = False
        
        while not hit_wall and current_dist < RAY_LENGTH:
            current_dist += 1
            ray_x = player_center_world[0] + step_x * current_dist
            ray_y = player_center_world[1] + step_y * current_dist
            
            if is_boss_fight:
                if (ray_x < ARENA_WALL_THICKNESS or ray_x > ARENA_WIDTH - ARENA_WALL_THICKNESS or
                    ray_y < ARENA_WALL_THICKNESS or ray_y > ARENA_HEIGHT - ARENA_WALL_THICKNESS):
                    hit_wall = True
            else:
                col = int(ray_x // CELL_SIZE)
                row = int(ray_y // CELL_SIZE)
                
                if not (0 <= col < COLS and 0 <= row < ROWS):
                    hit_wall = True
                    ray_x = max(0, min(ray_x, WORLD_WIDTH))
                    ray_y = max(0, min(ray_y, WORLD_HEIGHT))
                    break
                    
                cell = grid[col][row]
                for wall in cell.get_wall_rects():
                    if wall.collidepoint(ray_x, ray_y):
                        hit_wall = True
                        break

            if hit_wall:
                break
        
        if is_boss_fight:
            ray_x = max(ARENA_WALL_THICKNESS , min(ray_x, ARENA_WIDTH - ARENA_WALL_THICKNESS))
            ray_y = max(ARENA_WALL_THICKNESS , min(ray_y, ARENA_HEIGHT - ARENA_WALL_THICKNESS))
        else:
            ray_x = max(0 , min(ray_x + step_x * WALL_THICKNESS , WORLD_WIDTH))
            ray_y = max(0 , min(ray_y + step_y * WALL_THICKNESS , WORLD_HEIGHT))
        
        fov_points.append((ray_x, ray_y))
        
    return fov_points
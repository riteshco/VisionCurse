import pygame
import sys
import random
import math
from Player import Player


WIN_WIDTH , WIN_HEIGHT = 800, 600
player = Player([400 , 300] , [10 , 10])

def main():
    pygame.init()

    screen = pygame.display.set_mode((WIN_WIDTH , WIN_HEIGHT))
    pygame.display.set_caption('Falling Sand!')
    directions = {"NONE":[0,0],"UP":[0,-1],"DOWN":[0,1],"RIGHT":[1,0],"LEFT":[-1,0]}
    dir_to_move = [0,0]
    move = {"Up":False,"Down":False,"Left":False,"Right":False}

    # Main game loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False    
            if event.type == pygame.KEYDOWN:
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

        screen.fill((0, 0, 0))
        player.render(screen)

        if move["Up"]:
            dir_to_move = directions["UP"]
            player.move(dir_to_move)
        elif move["Down"]:
            dir_to_move = directions["DOWN"]
            player.move(dir_to_move)
        elif move["Left"]:
            dir_to_move = directions["LEFT"]
            player.move(dir_to_move)
        elif move["Right"]:
            dir_to_move = directions["RIGHT"]
            player.move(dir_to_move)

        # Update the display to show the changes
        pygame.display.flip()

    pygame.quit()
    sys.exit()

main()
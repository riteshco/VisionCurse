import pygame

class Player:
    def __init__(self , pos , size):
        self.pos = pos #[x , y]
        self.size = size #[width , height]
        self.health = 100
        self.speed = 0.1

    def render(self , screen):
        pygame.draw.rect(screen , (100,20,21) , (self.pos[0] , self.pos[1] , self.size[0] , self.size[1]))
    
    def update(self):
        pass
    
    def move(self , dir):
        self.pos[0] += dir[0] * self.speed
        self.pos[1] += dir[1] * self.speed
import pygame
from CollisionBox import CollisionBox

import math
class Entity:

    def __init__(self, position:list, collider : list, velocity:list,texture):
        self.position = position
        self.collider = collider #no. this should be the rctangles + position start
        self.velocity = velocity
        self.texture = texture

    def changePos(self):
        self.position[0] += math.floor(self.velocity[0]) #so acceleration will represent whole numbers
        self.position[1] += math.floor(self.velocity[1]) #for future if acceleration in needed

    #def lose(self):




    def isCollided(self, other):
        for collisionBox in self.collider:
           selfBox = pygame.Rect(self.position[0]+collisionBox.offsetX,self.position[1]+collisionBox.offsetY,collisionBox.width,collisionBox.height)
           for box in other.collider:
            otherBox = pygame.Rect(other.position[0]+box.offsetX,other.position[1]+box.offsetY,box.width,box.height)
            if selfBox.colliderect(otherBox):
               return True

        return False





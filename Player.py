import pygame
from CollisionBox import CollisionBox
from Entity import Entity

import math

class Player(Entity):
    def __init__(self, position: list, collider:list, velocity: list, texture,health,immunity):
        super().__init__(position.copy(), collider, velocity, texture)
        self.health = health
        self.immunity = immunity

    def decHealth(self):
        self.health -= 1





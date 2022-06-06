import pygame
from CollisionBox import CollisionBox
from Entity import Entity

import math

class Rocket(Entity):
    def __init__(self, position: list, collider: list, velocity: list,side : int, texture):
        super().__init__(position, collider, velocity, texture)
        self.side = side


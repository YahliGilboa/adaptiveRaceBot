from Entity import Entity

class Explosion(Entity):
    def __init__(self, position: list, collider: list, velocity: list, deSpawnTimer: int, texture):
        super().__init__(position, collider, velocity, texture)
        self.deSpawnTimer = deSpawnTimer


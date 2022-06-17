from Entity import Entity

class Car(Entity):
    def __init__(self, position: list, collider:list, velocity: list, lane, texture):
        super().__init__(position,collider,velocity,texture)
        self.lane = lane

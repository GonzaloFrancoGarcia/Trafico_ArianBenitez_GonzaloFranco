# simulacion_trafico/entorno/vehicle.py

class Vehicle:
    """
    Modela el comportamiento de un vehículo:
    posición, velocidad, dirección y estado de movimiento.
    """
    def __init__(self, id_, position=(0, 0), speed=0.0, direction="NORTE"):
        self.id_ = id_
        self.position = position
        self.speed = speed
        self.direction = direction
        self.moving = True

    def move(self):
        x, y = self.position
        if self.direction == "NORTE":
            y += self.speed
        elif self.direction == "SUR":
            y -= self.speed
        elif self.direction == "ESTE":
            x += self.speed
        elif self.direction == "OESTO":
            x -= self.speed
        self.position = (x, y)

    def __str__(self):
        return f"Vehicle {self.id_} at {self.position}, dir={self.direction}, moving={self.moving}"

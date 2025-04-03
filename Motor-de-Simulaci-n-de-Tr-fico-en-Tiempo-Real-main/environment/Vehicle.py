# simulacion_trafico/environment/vehicle.py

class Vehicle:
    """
    Clase que modela el comportamiento básico de un vehículo.
    """
    def __init__(self, id_, position=(0, 0), speed=0.0, direction="NORTE"):
        self.id_ = id_
        self.position = position
        self.speed = speed
        self.direction = direction

    def move(self):
        """
        Actualiza la posición del vehículo en función de su dirección y velocidad.
        Aquí se usa un modelo muy simplificado; en un motor real se realizarían
        cálculos de física, detección de colisiones, etc.
        """
        x, y = self.position

        if self.direction == "NORTE":
            y += self.speed
        elif self.direction == "SUR":
            y -= self.speed
        elif self.direction == "ESTE":
            x += self.speed
        elif self.direction == "OESTE":
            x -= self.speed

        self.position = (x, y)

    def __str__(self):
        return f"Vehicle {self.id_} at position {self.position}, speed {self.speed}, direction {self.direction}"

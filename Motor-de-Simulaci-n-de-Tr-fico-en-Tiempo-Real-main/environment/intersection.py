
# simulacion_trafico/entorno/intersection.py

class Intersection:
    """
    Representa una intersección de la ciudad, controlada por uno o varios semáforos.
    """
    def __init__(self, id_, location):
        self.id_ = id_
        self.location = location  # Ej: (x, y)
        self.traffic_lights = []  # Lista de semáforos asociados

    def add_traffic_light(self, traffic_light):
        self.traffic_lights.append(traffic_light)

    def can_vehicle_pass(self):
        """
        Permite el paso si al menos un semáforo está en verde.
        """
        return any(tl.current_state == "GREEN" for tl in self.traffic_lights)

    def __str__(self):
        estados = ", ".join(f"{tl.id_}:{tl.current_state}" for tl in self.traffic_lights)
        return f"Intersection {self.id_} at {self.location} with TLs [{estados}]"

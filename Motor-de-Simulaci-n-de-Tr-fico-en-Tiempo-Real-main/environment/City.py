
# simulacion_trafico/entorno/city.py

import asyncio

class City:
    """
    Clase que representa la ciudad que contiene semáforos, vehículos y
    cualquier otro elemento urbano (calles, intersecciones, etc.).
    """
    def __init__(self, name: str):
        self.name = name
        self.traffic_lights = []
        self.vehicles = []

    def add_traffic_light(self, traffic_light):
        self.traffic_lights.append(traffic_light)

    def add_vehicle(self, vehicle):
        self.vehicles.append(vehicle)

    async def run_simulation(self):
        """
        Lanza las tareas de los semáforos de la ciudad.
        """
        print(f"[{self.name}] Iniciando simulación con {len(self.traffic_lights)} semáforos...")
        tareas = [tl.run() for tl in self.traffic_lights]
        await asyncio.gather(*tareas)

    def __str__(self):
        return f"City: {self.name}, TrafficLights: {len(self.traffic_lights)}, Vehicles: {len(self.vehicles)}"

# simulacion_trafico/entorno/city.py

import asyncio

class City:
    """
    Clase que representa la ciudad que contiene semáforos, vehículos,
    intersecciones y cualquier otro elemento urbano.
    """
    def __init__(self, name: str):
        self.name = name
        self.traffic_lights = []
        self.vehicles = []
        self.intersections = []

    def add_traffic_light(self, traffic_light):
        self.traffic_lights.append(traffic_light)

    def add_vehicle(self, vehicle):
        self.vehicles.append(vehicle)

    def add_intersection(self, intersection):
        self.intersections.append(intersection)

    async def run_simulation(self):
        """
        Lanza las tareas de los semáforos de la ciudad.
        """
        print(f"[{self.name}] Iniciando simulación con {len(self.traffic_lights)} semáforos...")
        tareas = [tl.run() for tl in self.traffic_lights]
        await asyncio.gather(*tareas)

    def get_state_summary(self):
        """
        Devuelve un resumen del estado actual de los elementos urbanos.
        """
        summary = f"City: {self.name}\n"
        summary += "Semáforos:\n" + "\n".join(str(tl) for tl in self.traffic_lights) + "\n"
        summary += "Intersecciones:\n" + "\n".join(str(ix) for ix in self.intersections) + "\n"
        summary += "Vehículos:\n" + "\n".join(str(v) for v in self.vehicles) + "\n"
        return summary

    def get_snapshot(self):
        """
        Devuelve una representación estructurada del estado actual para la GUI.
        """
        lights_info = []
        for tl in self.traffic_lights:
            try:
                lights_info.append({
                    "id": tl.id_,
                    "x": tl.x,
                    "y": tl.y,
                    "estado": tl.current_state
                })
            except:
                pass  # Si el semáforo no tiene posición, se ignora

        vehicles_info = []
        for v in self.vehicles:
            vehicles_info.append({
                "id": v.id_,
                "x": v.position[0],
                "y": v.position[1],
                "speed": v.speed,
                "direction": v.direction
            })

        intersections_info = []
        for ix in self.intersections:
            try:
                intersections_info.append({
                    "id": ix.id_,
                    "x": ix.location[0],
                    "y": ix.location[1]
                })
            except:
                pass

        return {
            "traffic_lights": lights_info,
            "vehicles": vehicles_info,
            "intersections": intersections_info
        }

    def __str__(self):
        return f"City: {self.name}, TrafficLights: {len(self.traffic_lights)}, Vehicles: {len(self.vehicles)}, Intersections: {len(self.intersections)}"
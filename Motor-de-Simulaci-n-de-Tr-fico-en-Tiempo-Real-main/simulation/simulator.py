# simulacion_trafico/simulation/simulator.py

class Simulator:
    """
    Clase encargada de orquestar las actualizaciones de la ciudad.
    """
    def __init__(self, city):
        self.city = city

    def update(self):
        """
        Actualiza el estado de todos los elementos de la ciudad en cada 'tick' de la simulación.
        """
        # 1. Actualizar semáforos
        for tl in self.city.traffic_lights:
            tl.update_state()

        # 2. Mover vehículos
        for v in self.city.vehicles:
            v.move()

        # Aquí podrías añadir más lógica (detección de colisiones, congestión, etc.)

    def get_snapshot(self):
        """
        Retorna un resumen del estado actual de la simulación en formato de diccionario.
        Cada semáforo y vehículo se representa mediante un diccionario con la información necesaria para la visualización.
        """
        lights_info = []
        for tl in self.city.traffic_lights:
            # Se asume que cada objeto semáforo tiene atributos 'x', 'y' y 'estado'
            lights_info.append({
                "x": getattr(tl, "x", 0),
                "y": getattr(tl, "y", 0),
                "estado": getattr(tl, "estado", "RED").upper()  # Aseguramos el formato en mayúsculas
            })

        vehicles_info = []
        for v in self.city.vehicles:
            # Se asume que cada vehículo tiene atributos 'x' e 'y'
            vehicles_info.append({
                "x": getattr(v, "x", 0),
                "y": getattr(v, "y", 0)
            })

        return {
            "traffic_lights": lights_info,
            "vehicles": vehicles_info
        }

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
        Retorna un resumen del estado actual de la simulación.
        Se delega la creación del snapshot a la ciudad para asegurar consistencia.
        """
        return self.city.get_snapshot()

# simulacion_trafico/environment/traffic_light.py

class TrafficLight:
    """
    Clase que modela un semáforo con tiempos específicos para cada estado.
    """
    def __init__(self, id_, green_time=4, yellow_time=1, red_time=3):
        self.id_ = id_
        self.green_time = green_time
        self.yellow_time = yellow_time
        self.red_time = red_time

        self.current_state = "RED"  # Estado inicial
        self.timer = 0  # Contador interno para el cambio de estado

    def update_state(self):
        """
        Cambia el estado del semáforo en función del tiempo transcurrido.
        """
        self.timer += 1

        if self.current_state == "GREEN":
            if self.timer >= self.green_time:
                self._change_state("YELLOW")
        elif self.current_state == "YELLOW":
            if self.timer >= self.yellow_time:
                self._change_state("RED")
        elif self.current_state == "RED":
            if self.timer >= self.red_time:
                self._change_state("GREEN")

    def _change_state(self, new_state):
        self.current_state = new_state
        self.timer = 0  # Reiniciamos el temporizador

    def __str__(self):
        return f"TrafficLight {self.id_} - State: {self.current_state}"

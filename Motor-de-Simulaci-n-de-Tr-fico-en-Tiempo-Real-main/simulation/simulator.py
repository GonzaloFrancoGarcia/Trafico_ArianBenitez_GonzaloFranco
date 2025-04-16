# simulacion_trafico/simulation/simulator.py
import random

def can_vehicle_proceed(vehicle, traffic_lights, threshold=20, tolerance=3):
    """
    Retorna False si existe algún semáforo en frente del vehículo cuyo estado sea ROJO.
    Cuando el semáforo está en VERDE o ÁMBAR, el vehículo puede avanzar.
    Se basa en la posición, dirección del vehículo y una distancia umbral.
    """
    x, y = vehicle.position
    for tl in traffic_lights:
        if tl.current_state == "RED":
            if vehicle.direction == "NORTE":
                if abs(tl.x - x) <= tolerance and tl.y > y and (tl.y - y) <= threshold:
                    return False
            elif vehicle.direction == "SUR":
                if abs(tl.x - x) <= tolerance and tl.y < y and (y - tl.y) <= threshold:
                    return False
            elif vehicle.direction == "ESTE":
                if abs(tl.y - y) <= tolerance and tl.x > x and (tl.x - x) <= threshold:
                    return False
            elif vehicle.direction == "OESTE":
                if abs(tl.y - y) <= tolerance and tl.x < x and (x - tl.x) <= threshold:
                    return False
    return True

def reorient_vehicle(vehicle, intersections, tolerance=5, min_distance=2):
    """
    Si el vehículo está cerca de una intersección (dentro de 'tolerance' unidades)
    y se encuentra en movimiento, se reorienta para seguir la dirección predominante de la carretera.
    Si la diferencia horizontal es mayor, se ajusta a ESTE u OESTE; si la vertical es mayor, a NORTE o SUR.
    Esta reorientación se aplica solo si el vehículo está en movimiento y no está demasiado cerca (menos de min_distance)
    para evitar oscilaciones.
    """
    if not vehicle.moving:
        return

    x, y = vehicle.position
    for inter in intersections:
        ix, iy = inter.location
        dx = abs(x - ix)
        dy = abs(y - iy)
        if dx <= tolerance and dy <= tolerance:
            if dx < min_distance and dy < min_distance:
                continue
            if dx < dy:
                if iy > y:
                    vehicle.direction = "NORTE"
                else:
                    vehicle.direction = "SUR"
            else:
                if ix > x:
                    vehicle.direction = "ESTE"
                else:
                    vehicle.direction = "OESTE"
            break

def bounce_vehicle(vehicle, width=800, height=600):
    """
    Si el vehículo alcanza algún límite del área (0,0)-(width, height),
    invierte su dirección (rebota) y lo coloca justo en el borde.
    """
    x, y = vehicle.position
    reversed_flag = False
    if x < 0:
        x = 0
        reversed_flag = True
    elif x > width:
        x = width
        reversed_flag = True
    if y < 0:
        y = 0
        reversed_flag = True
    elif y > height:
        y = height
        reversed_flag = True
    vehicle.position = (x, y)
    if reversed_flag:
        reverse = {'NORTE': 'SUR', 'SUR': 'NORTE', 'ESTE': 'OESTE', 'OESTE': 'ESTE'}
        if vehicle.direction in reverse:
            vehicle.direction = reverse[vehicle.direction]

class Simulator:
    """
    Orquesta la actualización en tiempo real de la ciudad:
      - Actualiza semáforos y vehículos.
      - Un vehículo se mueve solo si puede proceder (es decir, si no hay semáforo ROJO de frente).
      - Si un vehículo estaba detenido y ahora puede avanzar, se le aplica un pequeño empujón (delta) para que salga del área del semáforo.
      - Luego, si procede, se reorienta según la red de intersecciones y se verifica el rebote en los límites.
    """
    def __init__(self, city):
        self.city = city

    def update(self):
        # Actualizar semáforos
        for tl in self.city.traffic_lights:
            tl.update_state()

        # Actualizar vehículos
        for v in self.city.vehicles:
            allowed = can_vehicle_proceed(v, self.city.traffic_lights)
            was_stopped = not v.moving
            if allowed:
                v.move()
                v.moving = True
                # Si el vehículo estaba detenido y ahora puede avanzar, se le aplica un pequeño impulso
                if was_stopped:
                    delta = 5
                    if v.direction == "NORTE":
                        v.position = (v.position[0], v.position[1] + delta)
                    elif v.direction == "SUR":
                        v.position = (v.position[0], v.position[1] - delta)
                    elif v.direction == "ESTE":
                        v.position = (v.position[0] + delta, v.position[1])
                    elif v.direction == "OESTE":
                        v.position = (v.position[0] - delta, v.position[1])
            else:
                v.moving = False
            # Reorientar solo si el vehículo se está moviendo
            reorient_vehicle(v, self.city.intersections)
            bounce_vehicle(v, 800, 600)

    def get_snapshot(self):
        return self.city.get_snapshot()

# simulacion_trafico/simulation/simulator.py
import random

def can_vehicle_proceed(vehicle, traffic_lights, threshold=20, tolerance=3):
    """
    Retorna False si existe algún semáforo en frente del vehículo cuyo estado sea ROJO.
    Si el semáforo está en VERDE o ÁMBAR (YELLOW), el vehículo puede pasar.
    Se basa en la posición del vehículo, su dirección y una distancia umbral.
    """
    x, y = vehicle.position
    for tl in traffic_lights:
        # Solo se bloquea el avance si el semáforo está en ROJO.
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

def reorient_vehicle(vehicle, intersections, tolerance=5):
    """
    Si el vehículo está muy cerca de una intersección (dentro de 'tolerance' unidades)
    y está en movimiento, ajusta su dirección para seguir la carretera.
    Se determina si la diferencia vertical u horizontal es mayor para orientar el vehículo.
    """
    if not vehicle.moving:
        return

    x, y = vehicle.position
    for inter in intersections:
        ix, iy = inter.location
        if abs(x - ix) <= tolerance and abs(y - iy) <= tolerance:
            if abs(x - ix) < abs(y - iy):
                # La diferencia vertical es mayor: orienta en dirección vertical.
                if iy > y:
                    vehicle.direction = "NORTE"
                else:
                    vehicle.direction = "SUR"
            else:
                # La diferencia horizontal es mayor: orienta en dirección horizontal.
                if ix > x:
                    vehicle.direction = "ESTE"
                else:
                    vehicle.direction = "OESTE"
            break

def bounce_vehicle(vehicle, width=800, height=600):
    """
    Si el vehículo alcanza el límite del área (0,0)-(width, height),
    se invierte su dirección (rebota) y se coloca justo en el borde.
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
    Clase encargada de orquestar la actualización de la ciudad.
    Actualiza semáforos y vehículos:
      - Un vehículo se mueve solo si no hay un semáforo ROJO en su camino.
      - Si se encuentra frente a un semáforo en rojo, se detiene (moving = False).
      - Cuando el semáforo cambie a verde o ámbar, el vehículo continúa sin reorientarse abruptamente.
      - Se reorienta (si está en movimiento) según la cercanía a una intersección y se aplica la función de rebote.
    """
    def __init__(self, city):
        self.city = city

    def update(self):
        # Actualizar semáforos
        for tl in self.city.traffic_lights:
            tl.update_state()

        # Actualizar vehículos
        for v in self.city.vehicles:
            if can_vehicle_proceed(v, self.city.traffic_lights):
                v.move()
                v.moving = True
            else:
                v.moving = False
            # Solo reorienta si el vehículo sigue en movimiento
            reorient_vehicle(v, self.city.intersections)
            bounce_vehicle(v, 800, 600)

    def get_snapshot(self):
        return self.city.get_snapshot()

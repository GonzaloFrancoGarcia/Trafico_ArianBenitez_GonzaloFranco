# simulacion_trafico/simulation/simulator.py

import random

def can_vehicle_proceed(vehicle, traffic_lights, lane_tol=5):
    """
    Devuelve False solo si un semáforo ROJO se interpone entre la posición actual
    y la siguiente (pos + speed), dentro de la tolerancia perpendicular 'lane_tol'.
    Semáforos en VERDE o AMARILLO dejan pasar.
    """
    x, y = vehicle.position
    s = vehicle.speed
    # Cálculo de la siguiente posición
    if vehicle.direction == "ESTE":
        next_x, next_y = x + s, y
    elif vehicle.direction == "OESTO":
        next_x, next_y = x - s, y
    elif vehicle.direction == "NORTE":
        next_x, next_y = x, y + s
    else:  # SUR
        next_x, next_y = x, y - s

    for tl in traffic_lights:
        if tl.current_state != "RED":
            continue  # verde o amarillo no bloquean
        # Comprobar intersección del segmento (x,y)->(next_x,next_y) con la posición del semáforo
        if vehicle.direction in ("ESTE", "OESTO"):
            if min(x, next_x) <= tl.x <= max(x, next_x) and abs(tl.y - y) <= lane_tol:
                return False
        else:
            if min(y, next_y) <= tl.y <= max(y, next_y) and abs(tl.x - x) <= lane_tol:
                return False
    return True

def align_to_road(vehicle, h_roads, v_roads):
    """
    Recuerda centrar al vehículo sobre su carretera:
    - Si va ESTE/OESTE, fija su y en la horizontal más cercana.
    - Si va NORTE/SUR, fija su x en la vertical más cercana.
    """
    x, y = vehicle.position
    if vehicle.direction in ("ESTE", "OESTO"):
        y = min(h_roads, key=lambda ry: abs(ry - y))
    else:
        x = min(v_roads, key=lambda rx: abs(rx - x))
    vehicle.position = (x, y)

def clamp_and_bounce_on_road(vehicle, h_extents, v_extents):
    """
    Evita que el vehículo salga de los extremos de su propia carretera:
    - Para carreteras horizontales (y fijo), mantiene x en [min_x, max_x].
    - Para verticales (x fijo), mantiene y en [min_y, max_y].
    Y si toca un extremo, invierte su dirección.
    """
    x, y = vehicle.position
    dir0 = vehicle.direction

    if dir0 in ("ESTE", "OESTO"):
        # Carretera horizontal
        road_y = y
        min_x, max_x = h_extents[road_y]
        if x < min_x:
            x, vehicle.direction = min_x, "ESTE"
        elif x > max_x:
            x, vehicle.direction = max_x, "OESTO"
    else:
        # Carretera vertical
        road_x = x
        min_y, max_y = v_extents[road_x]
        if y < min_y:
            y, vehicle.direction = min_y, "NORTE"
        elif y > max_y:
            y, vehicle.direction = max_y, "SUR"

    vehicle.position = (x, y)

def reorient_vehicle(vehicle, intersections, tol=5, turn_prob=0.3):
    """
    En intersecciones y si el vehículo sigue moviéndose, gira perpendicularmente
    con probabilidad 'turn_prob'; si no, sigue recto.
    """
    if not vehicle.moving:
        return

    x, y = vehicle.position
    for inter in intersections:
        ix, iy = inter.location
        if abs(x - ix) <= tol and abs(y - iy) <= tol:
            if vehicle.direction in ("ESTE", "OESTO"):
                opts = ["NORTE", "SUR"]
            else:
                opts = ["ESTE", "OESTO"]
            if random.random() < turn_prob:
                vehicle.direction = random.choice(opts)
            break

class Simulator:
    """
    Orquesta la simulación de semáforos y vehículos en tiempo real.
    """
    def __init__(self, city):
        self.city = city
        coords = [ix.location for ix in city.intersections]

        # Conjuntos de carreteras
        self.h_roads = sorted({y for x, y in coords})
        self.v_roads = sorted({x for x, y in coords})

        # Extents para cada carretera
        self.h_extents = {}
        for y in self.h_roads:
            xs = [x for x, yy in coords if yy == y]
            self.h_extents[y] = (min(xs), max(xs))

        self.v_extents = {}
        for x in self.v_roads:
            ys = [y for xx, y in coords if xx == x]
            self.v_extents[x] = (min(ys), max(ys))

    def update(self):
        # 1) Actualizar todos los semáforos
        for tl in self.city.traffic_lights:
            tl.update_state()

        # 2) Actualizar cada vehículo
        for v in self.city.vehicles:
            if can_vehicle_proceed(v, self.city.traffic_lights):
                v.move()
                v.moving = True
            else:
                v.moving = False

            # Mantener siempre en carretera
            align_to_road(v, self.h_roads, self.v_roads)
            clamp_and_bounce_on_road(v, self.h_extents, self.v_extents)
            reorient_vehicle(v, self.city.intersections)

    def get_snapshot(self):
        return self.city.get_snapshot()

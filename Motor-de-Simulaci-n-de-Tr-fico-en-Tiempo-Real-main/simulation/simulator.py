# simulacion_trafico/simulation/simulator.py

import random

def can_vehicle_proceed(vehicle, traffic_lights, tol=5):
    """
    Bloquea solo si la siguiente posición del vehículo (pos + speed)
    queda dentro de 'tol' píxeles de un semáforo en ROJO.
    Verde y ÁMBAR dejan pasar.
    """
    x, y = vehicle.position
    s = vehicle.speed

    if vehicle.direction == "ESTE":
        nx, ny = x + s, y
    elif vehicle.direction == "OESTO":
        nx, ny = x - s, y
    elif vehicle.direction == "NORTE":
        nx, ny = x, y + s
    else:  # SUR
        nx, ny = x, y - s

    for tl in traffic_lights:
        if tl.current_state != "RED":
            continue
        if abs(nx - tl.x) <= tol and abs(ny - tl.y) <= tol:
            return False
    return True

def align_to_road(vehicle, h_roads, v_roads):
    """
    Centra al vehículo en el eje de su carretera:
    - Si va ESTE/OESTO, fija su y
    - Si va NORTE/SUR, fija su x
    """
    x, y = vehicle.position
    if vehicle.direction in ("ESTE", "OESTO"):
        y = min(h_roads, key=lambda ry: abs(ry - y))
    else:
        x = min(v_roads, key=lambda rx: abs(rx - x))
    vehicle.position = (x, y)

def clamp_and_bounce_on_road(vehicle, h_ext, v_ext):
    """
    Impide que el vehículo salga de los límites de su propia carretera,
    rebota e invierte dirección al tocar un borde.
    """
    x, y = vehicle.position
    d = vehicle.direction
    if d in ("ESTE", "OESTO"):
        mn, mx = h_ext[y]
        if x < mn:
            x, vehicle.direction = mn, "ESTE"
        elif x > mx:
            x, vehicle.direction = mx, "OESTO"
    else:
        mn, mx = v_ext[x]
        if y < mn:
            y, vehicle.direction = mn, "NORTE"
        elif y > mx:
            y, vehicle.direction = mx, "SUR"
    vehicle.position = (x, y)

def reorient_vehicle(vehicle, intersections, tol=5, prob=0.3):
    """
    En intersecciones, si el vehículo está en movimiento,
    gira con probabilidad 'prob' perpendicularmente.
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
            if random.random() < prob:
                vehicle.direction = random.choice(opts)
            break

class Simulator:
    """
    Orquesta la simulación con semáforos desfasados en escalera:
    - update_interval = 120 frames (~2s a 60 FPS)
    - Offset fijo de 10 frames entre semáforo y semáforo,
      en orden de arriba a abajo, izquierda a derecha.
    """
    def __init__(self, city):
        self.city = city
        coords = [ix.location for ix in city.intersections]

        # Carreteras horizontales y verticales
        self.h_roads = sorted({y for _, y in coords})
        self.v_roads = sorted({x for x, _ in coords})

        # Límites de cada carretera
        self.h_ext = {
            y: (min(x for x, yy in coords if yy == y),
                max(x for x, yy in coords if yy == y))
            for y in self.h_roads
        }
        self.v_ext = {
            x: (min(y for xx, y in coords if xx == x),
                max(y for xx, y in coords if xx == x))
            for x in self.v_roads
        }

        # Cada semáforo cambia cada 120 frames (~2s)
        self.update_interval = 120

        # Ordenamos semáforos: fila (y) ascendente, luego columna (x) ascendente
        sorted_tls = sorted(city.traffic_lights, key=lambda tl: (tl.y, tl.x))

        # Offset de 10 frames entre cada semáforo
        self.tl_offsets = {
            tl: idx * 10
            for idx, tl in enumerate(sorted_tls)
        }

        self.frame_count = 0

    def update(self):
        self.frame_count += 1

        # Actualizar semáforos según su offset y el intervalo
        for tl, offset in self.tl_offsets.items():
            if (self.frame_count - offset) % self.update_interval == 0:
                tl.update_state()

        # Actualizar vehículos cada frame
        for v in self.city.vehicles:
            if can_vehicle_proceed(v, self.city.traffic_lights):
                v.move()
                v.moving = True
            else:
                v.moving = False

            align_to_road(v, self.h_roads, self.v_roads)
            clamp_and_bounce_on_road(v, self.h_ext, self.v_ext)
            reorient_vehicle(v, self.city.intersections)

    def get_snapshot(self):
        return self.city.get_snapshot()

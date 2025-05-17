# simulacion_trafico/simulation/simulator.py
import random


# ────────────────────────────────────────────────────────────
#  Helpers de lógica de tráfico
# ────────────────────────────────────────────────────────────
def can_vehicle_proceed(vehicle, traffic_lights, tol=5):
    x, y = vehicle.position
    s = vehicle.speed

    if vehicle.direction == "ESTE":
        nx, ny = x + s, y
    elif vehicle.direction == "OESTE":
        nx, ny = x - s, y
    elif vehicle.direction == "NORTE":
        nx, ny = x, y + s
    else:                           # SUR
        nx, ny = x, y - s

    for tl in traffic_lights:
        if tl.current_state != "RED":
            continue
        if abs(nx - tl.x) <= tol and abs(ny - tl.y) <= tol:
            return False
    return True


def align_to_road(vehicle, h_roads, v_roads):
    """
    Centra el vehículo sobre el eje de la carretera más cercana.
    Si todavía no hay carreteras definidas, no hace nada.
    """
    x, y = vehicle.position

    if vehicle.direction in ("ESTE", "OESTE") and h_roads:
        y = min(h_roads, key=lambda ry: abs(ry - y))
    elif vehicle.direction in ("NORTE", "SUR") and v_roads:
        x = min(v_roads, key=lambda rx: abs(rx - x))

    vehicle.position = (x, y)


def clamp_and_bounce_on_road(vehicle, h_ext, v_ext):
    """
    Impide que el vehículo salga de su carretera; rebota e invierte
    dirección al tocar un borde.  Si aún no hay límites definidos,
    no hace nada.
    """
    x, y = vehicle.position
    d = vehicle.direction

    if d in ("ESTE", "OESTE") and y in h_ext:
        mn, mx = h_ext[y]
        if x < mn:
            x, vehicle.direction = mn, "ESTE"
        elif x > mx:
            x, vehicle.direction = mx, "OESTE"
    elif d in ("NORTE", "SUR") and x in v_ext:
        mn, mx = v_ext[x]
        if y < mn:
            y, vehicle.direction = mn, "NORTE"
        elif y > mx:
            y, vehicle.direction = mx, "SUR"

    vehicle.position = (x, y)


def reorient_vehicle(vehicle, intersections, tol=5, prob=0.3):
    if not vehicle.moving:
        return

    x, y = vehicle.position
    for inter in intersections:
        ix, iy = inter.location
        if abs(x - ix) <= tol and abs(y - iy) <= tol:
            if vehicle.direction in ("ESTE", "OESTE"):
                opts = ["NORTE", "SUR"]
            else:
                opts = ["ESTE", "OESTE"]
            if random.random() < prob:
                vehicle.direction = random.choice(opts)
            break


# ────────────────────────────────────────────────────────────
#  Clase principal de simulación
# ────────────────────────────────────────────────────────────
class Simulator:
    """
    Orquesta la simulación con semáforos desfasados en escalera.
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

        # Semáforos: cambia cada 120 frames (~2 s)
        self.update_interval = 120

        # Orden de activación: fila (y) asc, luego columna (x) asc
        sorted_tls = sorted(city.traffic_lights, key=lambda tl: (tl.y, tl.x))
        self.tl_offsets = {tl: idx * 10 for idx, tl in enumerate(sorted_tls)}

        self.frame_count = 0

    # -------------------------------------------------------
    def update(self):
        self.frame_count += 1

        # Semáforos
        for tl, offset in self.tl_offsets.items():
            if (self.frame_count - offset) % self.update_interval == 0:
                tl.update_state()

        # Vehículos
        for v in self.city.vehicles:
            if can_vehicle_proceed(v, self.city.traffic_lights):
                v.move()
                v.moving = True
            else:
                v.moving = False

            align_to_road(v, self.h_roads, self.v_roads)
            clamp_and_bounce_on_road(v, self.h_ext, self.v_ext)
            reorient_vehicle(v, self.city.intersections)

    # -------------------------------------------------------
    def get_snapshot(self):
        return self.city.get_snapshot()

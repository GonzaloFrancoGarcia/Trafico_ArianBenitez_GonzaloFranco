# simulacion_trafico/ui/gui.py

import threading
import asyncio
import pygame
import hashlib
import random

from environment.City         import City
from environment.Vehicle      import Vehicle
from environment.TrafficLight import TrafficLight
from environment.intersection import Intersection
from simulation.simulator     import Simulator
from concurrency.tasks        import run_simulation_tasks

WIDTH, HEIGHT = 800, 600
BG_COLOR    = (30, 30, 30)
ROAD_COLOR  = (100, 100, 100)
BOUND_COLOR = (200, 200, 200)
FONT_COLOR  = (255, 255, 255)
FPS_COLOR   = (200, 200, 200)
STOP_COLOR  = (200,   0,   0)

def draw_roads(screen, intersections, tol=10):
    horiz, vert = {}, {}
    for inter in intersections:
        x, y = inter["x"], inter["y"]
        yy = round(y / tol) * tol
        horiz.setdefault(yy, []).append(x)
        xx = round(x / tol) * tol
        vert.setdefault(xx, []).append(y)
    for y, xs in horiz.items():
        if len(xs) >= 2:
            xs = sorted(xs)
            pygame.draw.line(screen, ROAD_COLOR, (xs[0], y), (xs[-1], y), 5)
    for x, ys in vert.items():
        if len(ys) >= 2:
            ys = sorted(ys)
            pygame.draw.line(screen, ROAD_COLOR, (x, ys[0]), (x, ys[-1]), 5)

def color_from_id(id_str):
    h = hashlib.md5(id_str.encode()).digest()
    return (h[0], h[1], h[2])

async def spawn_vehicles_periodically(city, limit=20):
    """
    Genera vehículos nuevos cada pocos segundos en los bordes de la zona,
    hasta alcanzar un total de 'limit' vehículos generados.
    """
    cnt = 0
    while cnt < limit:
        await asyncio.sleep(3)  # cada 3 segundos
        # Entra desde Oeste o Norte
        if random.random() < 0.5:
            pos = (0, random.uniform(100, 500))
            dir = "ESTE"
        else:
            pos = (random.uniform(100, 700), 0)
            dir = "SUR"
        cnt += 1
        veh = Vehicle(f"DYN-{cnt}", pos, speed=1.5, direction=dir)
        city.add_vehicle(veh)
    # Cuando cnt == limit, la corrutina termina y deja de generar.

class GUISimulation:
    def __init__(self, city_name):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(f"Simulación {city_name}")
        self.clock  = pygame.time.Clock()
        self.font   = pygame.font.SysFont(None, 20)

        # 1) Construye la ciudad y el grid de intersecciones/semaforos
        self.city = City(name=city_name)
        ys = [100, 300, 500]
        xs = [100, 300, 500, 700]
        idx = 1
        for y in ys:
            for x in xs:
                tl = TrafficLight(id_=f"T{idx}", x=x, y=y,
                                  green_time=3, yellow_time=1, red_time=3)
                tl.current_state = "GREEN" if idx % 2 == 0 else "RED"
                tl.timer = 0
                self.city.add_traffic_light(tl)

                inter = Intersection(id_=f"I{idx}", location=(x, y))
                self.city.add_intersection(inter)
                idx += 1

        # Vehículos iniciales estáticos
        self.city.add_vehicle(Vehicle("V1", (150,150), 2.0, "ESTE"))
        self.city.add_vehicle(Vehicle("V2", (700,300), 2.0, "OESTE"))

        # 2) Prepara el simulador
        self.sim = Simulator(self.city)
        self.running = True

    def start_sim(self):
        """
        Hilo dedicado que arranca las corutinas de simulación y spawning.
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        coros = run_simulation_tasks(self.sim, update_interval=0.05)
        # Agregamos el spawn con límite de 20 vehículos
        coros.append(spawn_vehicles_periodically(self.city, limit=20))
        loop.run_until_complete(asyncio.gather(*coros))

    def draw(self):
        snap = self.sim.get_snapshot()
        self.screen.fill(BG_COLOR)
        pygame.draw.rect(self.screen, BOUND_COLOR, (0,0,WIDTH,HEIGHT), 2)

        # Dibuja carreteras
        draw_roads(self.screen, snap["intersections"])

        # Dibuja semáforos
        for tl in snap["traffic_lights"]:
            x, y = int(tl["x"]), int(tl["y"])
            st = tl["estado"].upper()
            col = {"RED":(255,0,0),"YELLOW":(255,255,0),"GREEN":(0,255,0)}[st]
            pygame.draw.circle(self.screen, col, (x, y), 12)
            label = self.font.render(st, True, FONT_COLOR)
            self.screen.blit(label, (x-20, y+15))

        # Dibuja vehículos
        for v in snap["vehicles"]:
            x, y = v["x"], v["y"]
            base = color_from_id(v["id"])
            col  = base if v.get("moving", True) else STOP_COLOR
            if v["direction"] in ("NORTE","SUR"):
                w, h = 10, 20
            else:
                w, h = 20, 10
            rect = pygame.Rect(int(x-w/2), int(y-h/2), w, h)
            pygame.draw.rect(self.screen, col, rect)

        # Texto de estadísticas
        info1 = self.font.render(f"Vehículos: {len(snap['vehicles'])}", True, FONT_COLOR)
        info2 = self.font.render(f"FPS: {int(self.clock.get_fps())}", True, FPS_COLOR)
        self.screen.blit(info1, (10, 10))
        self.screen.blit(info2, (10, 30))

    def run(self):
        # Arranca simulación en segundo plano
        threading.Thread(target=self.start_sim, daemon=True).start()

        # Bucle principal de dibujo
        while self.running:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    self.running = False
            self.draw()
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()

if __name__ == "__main__":
    GUISimulation("zona_distribuida").run()

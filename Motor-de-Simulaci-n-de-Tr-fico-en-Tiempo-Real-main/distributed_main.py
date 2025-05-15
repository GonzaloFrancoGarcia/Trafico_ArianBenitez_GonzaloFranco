# simulacion_trafico/distributed_main.py

import asyncio
import json
import os
from pathlib import Path
from importlib import import_module

from environment.City import City
from environment.Vehicle import Vehicle
from environment.TrafficLight import TrafficLight
from environment.intersection import Intersection
from simulation.simulator import Simulator
from ui.gui import launch_gui
from concurrency.tasks import run_simulation_tasks

ZONES_FILE = Path(__file__).parent.parent / "zones.json"

async def start_zone(zone_cfg):
    """
    Arranca un nodo simulador para una zona:
    - Construye City con semáforos e intersecciones
    - Añade vehículos aleatorios dentro de sus límites
    - Inicia Simulator + GUI o runner específico
    """
    name   = zone_cfg["name"]
    xmin   = zone_cfg["xmin"]
    xmax   = zone_cfg["xmax"]
    ymin   = zone_cfg["ymin"]
    ymax   = zone_cfg["ymax"]
    queue  = zone_cfg["queue"]

    # 1) Crear ciudad zonal
    city = City(name=f"Zona-{name}")

    # 2) Definir semáforos e intersecciones dentro de los límites
    #    (Ejemplo: grid 2×2 dentro de zona)
    xs = [xmin + (xmax - xmin) * frac for frac in (0.25, 0.75)]
    ys = [ymin + (ymax - ymin) * frac for frac in (0.25, 0.75)]
    idx = 1
    for y in ys:
        for x in xs:
            tl = TrafficLight(
                id_=f"{name.upper()}-T{idx}",
                x=int(x), y=int(y),
                green_time=3, yellow_time=1, red_time=3
            )
            city.add_traffic_light(tl)
            inter = Intersection(id_=f"{name.upper()}-I{idx}", location=(int(x), int(y)))
            city.add_intersection(inter)
            idx += 1

    # 3) Poblamos vehículos aleatorios dentro de la zona
    num_veh = 5
    for i in range(num_veh):
        x = random.uniform(xmin, xmax)
        y = random.uniform(ymin, ymax)
        direction = random.choice(["NORTE", "SUR", "ESTE", "OESTO"])
        veh = Vehicle(id_=f"{name.upper()}-V{i+1}", position=(x, y), speed=3.0, direction=direction)
        city.add_vehicle(veh)

    # 4) Iniciar simulación concurrente
    simulator = Simulator(city)
    tasks = run_simulation_tasks(simulator, update_interval=0.1)

    print(f"[{name}] nodo iniciado: {num_veh} vehículos, semáforos {len(city.traffic_lights)}")
    await asyncio.gather(*tasks)

async def main():
    # Cargamos configuración de zonas
    with open(ZONES_FILE, "r") as f:
        cfg = json.load(f)
    zones = cfg.get("zones", [])

    # Arrancamos cada zona en una tarea distinta
    zone_tasks = [asyncio.create_task(start_zone(z)) for z in zones]

    # (Opcional) arrancar GUI global, o comentar si cada zona tiene su propia interfaz
    # gui_task = asyncio.create_task(launch_gui(GlobalSimulator()))

    await asyncio.gather(*zone_tasks)

if __name__ == "__main__":
    import random
    asyncio.run(main())

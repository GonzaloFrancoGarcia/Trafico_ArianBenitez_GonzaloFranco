# simulacion_trafico/main.py

import asyncio
import random
from environment.City import City
from environment.Vehicle import Vehicle
from environment.TrafficLight import TrafficLight
from simulation.simulator import Simulator
from ui.gui import launch_gui
from environment.intersection import Intersection

def random_vehicle_initial_position():
    """
    Genera una posición y dirección aleatorias sobre una carretera:
    - Horizontal: y ∈ {100, 300, 500}, x ∈ [100,700], dir ESTE/OESTE
    - Vertical:   x ∈ {100, 300, 500, 700}, y ∈ [100,400], dir NORTE/SUR
    """
    if random.random() < 0.5:
        y = random.choice([100, 300, 500])
        direction = random.choice(["ESTE", "OESTE"])
        x = random.uniform(100, 700)
    else:
        x = random.choice([100, 300, 500, 700])
        direction = random.choice(["NORTE", "SUR"])
        y = random.uniform(100, 400)
    return (x, y), direction

async def main():
    city = City(name="Ciudad Ejemplo")

    # Grid 3 filas × 4 columnas de semáforos + intersecciones
    ys = [100, 300, 500]
    xs = [100, 300, 500, 700]
    idx = 1
    for y in ys:
        for x in xs:
            tl = TrafficLight(
                id_=f"T{idx}", x=x, y=y,
                green_time=3, yellow_time=1, red_time=3
            )
            # Alternamos estado inicial para que algunos arranquen en VERDE y otros en ROJO
            if idx % 2 == 0:
                tl.current_state = "GREEN"
            else:
                tl.current_state = "RED"
            tl.timer = 0

            city.add_traffic_light(tl)

            inter = Intersection(id_=f"I{idx}", location=(x, y))
            city.add_intersection(inter)

            idx += 1

    # Crear vehículos con velocidad reducida a 3.0
    for i in range(12):
        pos, direction = random_vehicle_initial_position()
        veh = Vehicle(id_=f"V{i+1}", position=pos, speed=3.0, direction=direction)
        city.add_vehicle(veh)

    simulator = Simulator(city)
    # La GUI llama a simulator.update() cada frame
    await launch_gui(simulator)

if __name__ == "__main__":
    asyncio.run(main())

# simulacion_trafico/main.py

import asyncio
import random
from environment.City import City
from environment.Vehicle import Vehicle
from environment.TrafficLight import TrafficLight
from simulation.simulator import Simulator
from concurrency.tasks import run_simulation_tasks
from ui.gui import launch_gui
from environment.intersection import Intersection

def random_vehicle_initial_position():
    """
    Genera una posición y dirección aleatorias sobre una carretera.
    - En una carretera horizontal: se fija y (100 para la parte superior o 400 para la parte inferior)
      y se asigna una coordenada x aleatoria entre 100 y 500. La dirección se elige entre ESTE y OESTE.
    - En una carretera vertical: se fija x (entre 100, 300 o 500) y se asigna una coordenada y aleatoria entre 100 y 400.
      La dirección se elige entre NORTE y SUR.
    """
    if random.random() < 0.5:  # carretera horizontal
        if random.random() < 0.5:
            y = 100
            direction = random.choice(["ESTE", "OESTE"])
        else:
            y = 400
            direction = random.choice(["ESTE", "OESTE"])
        x = random.uniform(100, 500)
    else:  # carretera vertical
        x = random.choice([100, 300, 500])
        direction = random.choice(["NORTE", "SUR"])
        y = random.uniform(100, 400)
    return (x, y), direction

async def main():
    city = City(name="Ciudad Ejemplo")
    
    # Crear semáforos repartidos en la red:
    tl1 = TrafficLight(id_="T1", x=100, y=100, green_time=10, yellow_time=3, red_time=10)
    tl2 = TrafficLight(id_="T2", x=300, y=100, green_time=10, yellow_time=3, red_time=10)
    tl3 = TrafficLight(id_="T3", x=500, y=100, green_time=10, yellow_time=3, red_time=10)
    tl4 = TrafficLight(id_="T4", x=100, y=400, green_time=10, yellow_time=3, red_time=10)
    tl5 = TrafficLight(id_="T5", x=500, y=400, green_time=10, yellow_time=3, red_time=10)
    tl6 = TrafficLight(id_="T6", x=300, y=400, green_time=10, yellow_time=3, red_time=10)  # Semáforo del medio abajo

    city.add_traffic_light(tl1)
    city.add_traffic_light(tl2)
    city.add_traffic_light(tl3)
    city.add_traffic_light(tl4)
    city.add_traffic_light(tl5)
    city.add_traffic_light(tl6)
    
    # Crear intersecciones para formar un grid (carreteras fijas)
    inter1 = Intersection(id_="I1", location=(100, 100))
    inter2 = Intersection(id_="I2", location=(300, 100))
    inter3 = Intersection(id_="I3", location=(500, 100))
    inter4 = Intersection(id_="I4", location=(100, 400))
    inter5 = Intersection(id_="I5", location=(300, 400))
    inter6 = Intersection(id_="I6", location=(500, 400))
    
    city.add_intersection(inter1)
    city.add_intersection(inter2)
    city.add_intersection(inter3)
    city.add_intersection(inter4)
    city.add_intersection(inter5)
    city.add_intersection(inter6)
    
    # Crear vehículos con posiciones iniciales aleatorias sobre las carreteras
    vehicles = []
    num_vehicles = 8  # Número de vehículos a generar
    for i in range(num_vehicles):
        pos, direction = random_vehicle_initial_position()
        veh = Vehicle(id_=f"V{i+1}", position=pos, speed=5.0, direction=direction)
        vehicles.append(veh)
    for veh in vehicles:
        city.add_vehicle(veh)

    simulator = Simulator(city=city)
    tasks = run_simulation_tasks(simulator, update_interval=0.5)
    gui_task = asyncio.create_task(launch_gui(simulator))
    await asyncio.gather(*tasks, gui_task)

if __name__ == "__main__":
    asyncio.run(main())

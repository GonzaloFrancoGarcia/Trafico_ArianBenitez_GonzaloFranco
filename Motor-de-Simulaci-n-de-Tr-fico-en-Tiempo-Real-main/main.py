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
    - Carretera horizontal: y ∈ {100, 300, 400}, x aleatorio en [100, 700].
      Dirección ESTE u OESTO.
    - Carretera vertical: x ∈ {100, 300, 500, 700}, y aleatorio en [100, 400].
      Dirección NORTE o SUR.
    """
    if random.random() < 0.5:
        # Carretera horizontal: fila superior, media o inferior
        y = random.choice([100, 300, 400])
        direction = random.choice(["ESTE", "OESTE"])
        x = random.uniform(100, 700)
    else:
        # Carretera vertical: columnas izquierdas o derechas
        x = random.choice([100, 300, 500, 700])
        direction = random.choice(["NORTE", "SUR"])
        y = random.uniform(100, 400)
    return (x, y), direction

async def main():
    city = City(name="Ciudad Ejemplo")
    
    # Crear semáforos repartidos en la red:
    tl1 = TrafficLight(id_="T1", x=100, y=100, green_time=10, yellow_time=3, red_time=10)
    tl2 = TrafficLight(id_="T2", x=300, y=100, green_time=10, yellow_time=3, red_time=10)
    tl3 = TrafficLight(id_="T3", x=500, y=100, green_time=10, yellow_time=3, red_time=10)
    tl4 = TrafficLight(id_="T4", x=700, y=100, green_time=10, yellow_time=3, red_time=10)
    tl5 = TrafficLight(id_="T5", x=100, y=400, green_time=10, yellow_time=3, red_time=10)
    tl6 = TrafficLight(id_="T6", x=300, y=400, green_time=10, yellow_time=3, red_time=10)
    tl7 = TrafficLight(id_="T7", x=500, y=400, green_time=10, yellow_time=3, red_time=10)
    tl8 = TrafficLight(id_="T8", x=700, y=400, green_time=10, yellow_time=3, red_time=10)
    tl9 = TrafficLight(id_="T5", x=100, y=700, green_time=10, yellow_time=3, red_time=10)
    tl10 = TrafficLight(id_="T6", x=300, y=700, green_time=10, yellow_time=3, red_time=10)
    tl11 = TrafficLight(id_="T7", x=500, y=700, green_time=10, yellow_time=3, red_time=10)
    tl12 = TrafficLight(id_="T8", x=700, y=700, green_time=10, yellow_time=3, red_time=10)


    city.add_traffic_light(tl1)
    city.add_traffic_light(tl2)
    city.add_traffic_light(tl3)
    city.add_traffic_light(tl4)
    city.add_traffic_light(tl5)
    city.add_traffic_light(tl6)
    city.add_traffic_light(tl7)
    city.add_traffic_light(tl8)
    city.add_traffic_light(tl9)
    city.add_traffic_light(tl10)
    city.add_traffic_light(tl11)
    city.add_traffic_light(tl12)
    
    # Crear intersecciones para formar un grid (carreteras fijas)
    inter1 = Intersection(id_="I1", location=(100, 100))
    inter2 = Intersection(id_="I2", location=(300, 100))
    inter3 = Intersection(id_="I3", location=(500, 100))
    inter4 = Intersection(id_="I4", location=(700, 100))
    inter5 = Intersection(id_="I5", location=(100, 400))
    inter6 = Intersection(id_="I6", location=(300, 400))
    inter7 = Intersection(id_="I7", location=(500, 400))
    inter8 = Intersection(id_="I8", location=(700, 400))
    inter9 = Intersection(id_="I5", location=(100, 700))
    inter10 = Intersection(id_="I6", location=(300, 700))
    inter11 = Intersection(id_="I7", location=(500, 700))
    inter12 = Intersection(id_="I8", location=(700, 700))
    
    city.add_intersection(inter1)
    city.add_intersection(inter2)
    city.add_intersection(inter3)
    city.add_intersection(inter4)
    city.add_intersection(inter5)
    city.add_intersection(inter6)
    city.add_intersection(inter7)
    city.add_intersection(inter8)
    city.add_intersection(inter9)
    city.add_intersection(inter10)
    city.add_intersection(inter11)
    city.add_intersection(inter12)
    
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
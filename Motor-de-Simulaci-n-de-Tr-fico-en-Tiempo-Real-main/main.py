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
    Genera una posición aleatoria sobre una carretera y asigna una dirección correspondiente.
    - Para una carretera horizontal, se selecciona y fijo (100 para la fila superior o 400 para la inferior)
      y un valor x aleatorio entre 100 y 500. La dirección será 'ESTE' u 'OESTE' (elegida aleatoriamente).
    - Para una carretera vertical, se selecciona x fijo (100, 300 o 500) y un valor y aleatorio entre 100 y 400.
      La dirección será 'NORTE' o 'SUR'.
    """
    if random.random() < 0.5:  # carretera horizontal
        # Escoger fila: superior (y = 100) o inferior (y = 400)
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
    
    # Crear varios semáforos repartidos por el área
    traffic_light_1 = TrafficLight(id_="T1", x=100, y=100, green_time=10, yellow_time=3, red_time=10)
    traffic_light_2 = TrafficLight(id_="T2", x=300, y=100, green_time=10, yellow_time=3, red_time=10)
    traffic_light_3 = TrafficLight(id_="T3", x=500, y=100, green_time=10, yellow_time=3, red_time=10)
    traffic_light_4 = TrafficLight(id_="T4", x=100, y=400, green_time=10, yellow_time=3, red_time=10)
    traffic_light_5 = TrafficLight(id_="T5", x=500, y=400, green_time=10, yellow_time=3, red_time=10)
    
    city.add_traffic_light(traffic_light_1)
    city.add_traffic_light(traffic_light_2)
    city.add_traffic_light(traffic_light_3)
    city.add_traffic_light(traffic_light_4)
    city.add_traffic_light(traffic_light_5)
    
    # Crear intersecciones para formar un grid de carreteras
    # Se definen las intersecciones en los puntos fijos de las carreteras.
    inter_1 = Intersection(id_="I1", location=(100, 100))
    inter_2 = Intersection(id_="I2", location=(300, 100))
    inter_3 = Intersection(id_="I3", location=(500, 100))
    inter_4 = Intersection(id_="I4", location=(100, 400))
    inter_5 = Intersection(id_="I5", location=(300, 400))
    inter_6 = Intersection(id_="I6", location=(500, 400))
    
    city.add_intersection(inter_1)
    city.add_intersection(inter_2)
    city.add_intersection(inter_3)
    city.add_intersection(inter_4)
    city.add_intersection(inter_5)
    city.add_intersection(inter_6)
    
    # Crear vehículos con posiciones iniciales aleatorias que coincidan con las carreteras
    vehicles = []
    num_vehicles = 8  # Puedes aumentar o reducir la cantidad
    for i in range(num_vehicles):
        pos, direction = random_vehicle_initial_position()
        # Aumentar la velocidad para que se muevan más rápido (por ejemplo, 5.0)
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

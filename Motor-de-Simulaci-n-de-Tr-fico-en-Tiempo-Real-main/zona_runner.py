
# simulacion_trafico/simulation/zona_runner.py

import asyncio

from environment.City import City
from environment.Vehicle import Vehicle
from environment.TrafficLight import TrafficLight
from simulation.simulator import Simulator
from concurrency.tasks import run_simulation_tasks


async def main():
    # Crear una ciudad para esta zona
    city = City(name="Zona Norte")

    # Semáforos propios de esta zona
    traffic_light_1 = TrafficLight(id_="ZN-TL1", green_time=3, yellow_time=1, red_time=4)
    traffic_light_2 = TrafficLight(id_="ZN-TL2", green_time=5, yellow_time=2, red_time=5)

    city.add_traffic_light(traffic_light_1)
    city.add_traffic_light(traffic_light_2)

    # Vehículos propios de esta zona
    vehicle_1 = Vehicle(id_="ZN-V1", position=(0, 0), speed=1.0, direction="ESTE")
    vehicle_2 = Vehicle(id_="ZN-V2", position=(5, 5), speed=0.5, direction="SUR")

    city.add_vehicle(vehicle_1)
    city.add_vehicle(vehicle_2)

    # Instanciar simulador
    simulator = Simulator(city=city)

    # Obtener tareas de simulación (concurrentes)
    tasks = run_simulation_tasks(simulator, update_interval=0.5)

    # Ejecutar la simulación de esta zona
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())

# simulacion_trafico/main.py

import asyncio

from environment.City import City
from environment.Vehicle import Vehicle
from environment.TrafficLight import TrafficLight
from simulation.simulator import Simulator
from concurrency.tasks import run_simulation_tasks
from ui.gui import launch_gui


async def main():
    # 1. Crear el entorno (ciudad, vehículos, semáforos, etc.)
    city = City(name="Ciudad Ejemplo")

    # Creamos algunos semáforos de ejemplo
    traffic_light_1 = TrafficLight(id_="T1", green_time=4, yellow_time=1, red_time=3)
    traffic_light_2 = TrafficLight(id_="T2", green_time=5, yellow_time=1, red_time=4)

    # Creamos algunos vehículos de ejemplo
    vehicle_1 = Vehicle(id_="V1", position=(0, 0), speed=1.0, direction="NORTE")
    vehicle_2 = Vehicle(id_="V2", position=(10, 10), speed=1.5, direction="OESTE")

    # Agregamos estos objetos a la ciudad
    city.add_traffic_light(traffic_light_1)
    city.add_traffic_light(traffic_light_2)
    city.add_vehicle(vehicle_1)
    city.add_vehicle(vehicle_2)

    # 2. Crear el simulador
    simulator = Simulator(city=city)

    # 3. Iniciar las tareas concurrentes (movimiento de vehículos, cambios de semáforo, etc.)
    #    Usamos una función que nos devuelve la lista de tareas asyncio
    tasks = run_simulation_tasks(simulator, update_interval=0.5)

    # 4. Lanzar la interfaz de usuario (opcional) en paralelo
    #    En este ejemplo, la interfaz se ejecuta en modo asíncrono.
    gui_task = asyncio.create_task(launch_gui(simulator))

    # 5. Ejecutar todas las tareas en conjunto
    await asyncio.gather(*tasks, gui_task)


if __name__ == "__main__":
    asyncio.run(main())

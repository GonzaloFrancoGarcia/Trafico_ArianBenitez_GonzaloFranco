
# test_city_runner.py

import asyncio
from TrafficLight import TrafficLight
from City import City

async def main():
    # Crear instancia de la ciudad
    ciudad = City("Zona Centro")

    # Crear e insertar algunos semáforos con distintos tiempos
    semaforo_1 = TrafficLight(id_="A", green_time=3, yellow_time=1, red_time=2)
    semaforo_2 = TrafficLight(id_="B", green_time=4, yellow_time=2, red_time=3)

    ciudad.add_traffic_light(semaforo_1)
    ciudad.add_traffic_light(semaforo_2)

    # Ejecutar la simulación
    await ciudad.run_simulation()

if __name__ == "__main__":
    asyncio.run(main())

# test_intersection_runner.py

import asyncio
from TrafficLight import TrafficLight
from intersection import Intersection
from City import City

async def main():
    # Crear ciudad
    ciudad = City("Testopolis")

    # Crear semáforos
    tl1 = TrafficLight(id_="X1", green_time=2, yellow_time=1, red_time=2)
    tl2 = TrafficLight(id_="X2", green_time=3, yellow_time=1, red_time=3)

    ciudad.add_traffic_light(tl1)
    ciudad.add_traffic_light(tl2)

    # Crear intersección y asociar semáforos
    interseccion = Intersection(id_="I1", location=(5, 5))
    interseccion.add_traffic_light(tl1)
    interseccion.add_traffic_light(tl2)

    ciudad.add_intersection(interseccion)

    # Mostrar estado inicial
    print(ciudad.get_state_summary())

    # Simular 15 segundos e ir preguntando si se puede pasar
    async def monitor():
        for _ in range(5):
            puede = interseccion.can_vehicle_pass()
            estado = "PUEDE PASAR" if puede else "DEBE ESPERAR"
            print(f"[Estado intersección {interseccion.id_}]: {estado}")
            await asyncio.sleep(3)

    # Ejecutar todo simultáneamente
    await asyncio.gather(ciudad.run_simulation(), monitor())

if __name__ == "__main__":
    asyncio.run(main())

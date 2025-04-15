
# simulacion_trafico/simulation/zona_distribuida_runner.py

import asyncio

from environment.City import City
from environment.Vehicle import Vehicle
from environment.TrafficLight import TrafficLight
from simulation.simulator import Simulator
from concurrency.tasks import run_simulation_tasks
from distribution.rabbitmq_client import RabbitMQClient
from distribution.protocolo import crear_mensaje, TipoMensaje


async def procesar_mensaje(msg):
    print(f"[ZONA] Mensaje recibido: {msg}")
    if msg["tipo"] == TipoMensaje.VEHICULO_ENTRANTE.value:
        datos = msg["datos"]
        vehiculo = Vehicle(
            id_=datos["id"],
            position=tuple(datos["posicion"]),
            speed=datos["velocidad"],
            direction=datos["direccion"]
        )
        ciudad.add_vehicle(vehiculo)
        print(f"[ZONA] Vehículo {vehiculo.id_} agregado a la zona")


async def main():
    global ciudad
    ciudad = City(name="ZonaDistribuida")

    # Crear semáforos y vehículos de esta zona
    ciudad.add_traffic_light(TrafficLight(id_="ZD-T1", green_time=3, yellow_time=1, red_time=3))
    ciudad.add_vehicle(Vehicle(id_="ZD-V1", position=(0, 0), speed=1.0, direction="SUR"))

    # Iniciar simulador local
    simulador = Simulator(city=ciudad)
    tasks_simulacion = run_simulation_tasks(simulador, update_interval=0.5)

    # Conexión a RabbitMQ
    rabbit = RabbitMQClient()
    await rabbit.connect()

    # Lanzar consumidor de mensajes
    consumer_task = asyncio.create_task(
        rabbit.start_consumer(queue_name="zona_distribuida_queue", callback=procesar_mensaje)
    )

    # Enviar mensaje de estado de zona como demostración
    estado = {
        "zona": ciudad.name,
        "vehiculos": len(ciudad.vehicles),
        "trafico": "MODERADO"
    }
    mensaje = crear_mensaje(
        tipo=TipoMensaje.ESTADO_ZONA,
        datos=estado,
        origen="zona_distribuida",
        destino="zona_central"
    )
    await rabbit.send_message(mensaje, queue_name="zona_central_queue")

    # Ejecutar simulación + consumidor
    await asyncio.gather(*tasks_simulacion, consumer_task)

if __name__ == "__main__":
    asyncio.run(main())

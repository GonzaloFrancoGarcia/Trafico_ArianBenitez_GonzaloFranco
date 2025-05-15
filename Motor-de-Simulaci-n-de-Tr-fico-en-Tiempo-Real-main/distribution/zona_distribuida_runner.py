import asyncio, logging
from datetime import datetime

from environment.City import City
from environment.Vehicle import Vehicle
from environment.TrafficLight import TrafficLight
from simulation.simulator import Simulator
from concurrency.tasks import run_simulation_tasks
from distribution.rabbitmq_client import RabbitMQClient
from distribution.protocolo import (
    mensaje_estado_zona,
    mensaje_ack
)
from distribution.message_models import Mensaje, TipoMensaje

_LOG = logging.getLogger("ZonaDistribuida")

# ---------- Handlers de mensajes ---------- #

async def handle_vehiculo_entrante(m: Mensaje):
    datos = m.datos  # ya es DatosVehiculoEntrante validado
    v = Vehicle(
        id_=datos.id,
        position=tuple(datos.posicion),
        speed=datos.velocidad,
        direction=datos.direccion
    )
    ciudad.add_vehicle(v)
    _LOG.info("Vehículo %s integrado en la zona.", v.id_)

    # publicar ACK de recepción
    ack = mensaje_ack(
        acked_id=m.id,
        origen=ciudad.name,
        destino=m.origen
    )
    await rabbit.send_message(ack, queue_name=f"{m.origen}_queue")

# mapping tipo → handler
HANDLERS = {
    TipoMensaje.VEHICULO_ENTRANTE.value: handle_vehiculo_entrante,
}

# ---------- Arranque ---------- #
async def main():
    global ciudad, rabbit
    ciudad = City(name="zona_distribuida")
    rabbit  = RabbitMQClient(prefetch=5)   # evita bursts

    # elementos locales
    ciudad.add_traffic_light(TrafficLight(id_="ZD-T1",
                                          green_time=3, yellow_time=1, red_time=3))
    ciudad.add_vehicle(Vehicle(id_="ZD-V1", position=(0, 0),
                               speed=1.0, direction="SUR"))

    # simulación local
    sim = Simulator(city=ciudad)
    sim_tasks = run_simulation_tasks(sim, update_interval=0.5)

    await rabbit.connect()

    # consumidor de cola propia
    consumer = asyncio.create_task(
        rabbit.start_consumer("zona_distribuida_queue", HANDLERS)
    )

    # informe periódico de estado (cada 5 s)
    async def publicar_estado():
        while True:
            estado = {
                "zona": ciudad.name,
                "vehiculos": len(ciudad.vehicles),
                "trafico": "MODERADO"
            }
            msg = mensaje_estado_zona(
                estado=estado,
                origen=ciudad.name,
                destino="zona_central"
            )
            await rabbit.send_message(msg, queue_name="zona_central_queue")
            await asyncio.sleep(5)

    await asyncio.gather(*sim_tasks, consumer, publicar_estado())

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(name)s | %(message)s")
    asyncio.run(main())
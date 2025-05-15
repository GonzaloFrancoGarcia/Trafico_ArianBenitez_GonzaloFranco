# simulacion_trafico/distribution/send_vehicle_to_zona_distribuida.py
import asyncio, logging

from distribution.rabbitmq_client import RabbitMQClient
from distribution.protocolo           import mensaje_vehiculo_entrante
from distribution.migracion_utils     import destino_menos_cargado

logging.basicConfig(level=logging.INFO, format="%(name)s | %(message)s")
_LOG = logging.getLogger("SenderDemo")

ORIGEN  = "zona_central"

async def main():
    rabbit = RabbitMQClient()
    await rabbit.connect()

    # 1) Preguntar al coordinador qué nodo está más libre
    destino = await destino_menos_cargado(excluir=[ORIGEN])
    if not destino:
        _LOG.error("No hay nodo HEALTHY disponible — abortando prueba.")
        return

    vehiculo = {
        "id": "VC-TEST",
        "posicion": [20.0, 5.0],
        "velocidad": 1.2,
        "direccion": "ESTE"
    }

    msg = mensaje_vehiculo_entrante(
        vehiculo=vehiculo,
        origen=ORIGEN,
        destino=destino
    )

    await rabbit.send_message(msg, queue_name=f"{destino}_queue")
    _LOG.info("Vehículo enviado a %s.", destino)

if __name__ == "__main__":
    asyncio.run(main())


# send_vehicle_to_zona_distribuida.py

import asyncio
from distribution.rabbitmq_client import RabbitMQClient
from distribution.protocolo import crear_mensaje, TipoMensaje

async def main():
    # Crear cliente RabbitMQ
    rabbit = RabbitMQClient()
    await rabbit.connect()

    # Crear mensaje VEHICULO_ENTRANTE
    vehiculo = {
        "id": "VC-TEST",
        "posicion": [20, 5],
        "velocidad": 1.2,
        "direccion": "ESTE"
    }

    mensaje = crear_mensaje(
        tipo=TipoMensaje.VEHICULO_ENTRANTE,
        datos=vehiculo,
        origen="zona_central",
        destino="zona_distribuida"
    )

    # Enviar a la cola de zona_distribuida
    await rabbit.send_message(mensaje, queue_name="zona_distribuida_queue")

if __name__ == "__main__":
    asyncio.run(main())

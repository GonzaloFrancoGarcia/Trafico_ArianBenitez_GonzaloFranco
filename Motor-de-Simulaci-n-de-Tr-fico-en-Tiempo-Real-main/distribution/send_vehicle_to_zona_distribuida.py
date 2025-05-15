import asyncio
from distribution.rabbitmq_client import RabbitMQClient
from distribution.protocolo import mensaje_vehiculo_entrante

async def main():
    rabbit = RabbitMQClient()
    await rabbit.connect()

    vehiculo = {
        "id": "VC-TEST",
        "posicion": [20.0, 5.0],
        "velocidad": 1.2,
        "direccion": "ESTE"
    }

    msg = mensaje_vehiculo_entrante(
        vehiculo=vehiculo,
        origen="zona_central",
        destino="zona_distribuida"
    )

    await rabbit.send_message(msg, queue_name="zona_distribuida_queue")
    print("Mensaje de migración enviado.")

if __name__ == "__main__":
    asyncio.run(main())

# simulacion_trafico/distribution/rabbit_client.py

# EJEMPLO con 'aio_pika' (instalar con: pip install aio-pika)
# NOTA: Este código no se usa en la plantilla final, pero sirve de referencia.

import asyncio
import aio_pika

async def send_message(message, queue_name="simulacion_queue"):
    connection = await aio_pika.connect_robust("amqp://guest:guest@localhost/")
    async with connection:
        channel = await connection.channel()
        await channel.default_exchange.publish(
            aio_pika.Message(body=message.encode()),
            routing_key=queue_name
        )

async def receive_messages(queue_name="simulacion_queue"):
    connection = await aio_pika.connect_robust("amqp://guest:guest@localhost/")
    async with connection:
        channel = await connection.channel()
        queue = await channel.declare_queue(queue_name, durable=True)

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    print("Mensaje recibido:", message.body.decode())
                    # Aquí podrías disparar un evento, actualizar otra parte de la simulación, etc.

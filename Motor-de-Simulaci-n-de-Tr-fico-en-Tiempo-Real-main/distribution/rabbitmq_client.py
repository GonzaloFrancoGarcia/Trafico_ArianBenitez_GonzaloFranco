
# simulacion_trafico/comunicacion/rabbitmq_client.py

import asyncio
import aio_pika
import json

class RabbitMQClient:
    def __init__(self, amqp_url="amqp://guest:guest@localhost/"):
        self.amqp_url = amqp_url
        self.connection = None
        self.channel = None

    async def connect(self):
        """
        Establece conexión con RabbitMQ y abre un canal.
        """
        self.connection = await aio_pika.connect_robust(self.amqp_url)
        self.channel = await self.connection.channel()
        print("[RabbitMQ] Conectado y canal abierto.")

    async def send_message(self, message: dict, queue_name: str):
        """
        Envía un mensaje JSON a una cola específica.
        """
        if not self.channel:
            raise Exception("Conexión no inicializada. Llama a connect() primero.")
        body = json.dumps(message).encode()
        await self.channel.default_exchange.publish(
            aio_pika.Message(body=body),
            routing_key=queue_name
        )
        print(f"[RabbitMQ] Mensaje enviado a '{queue_name}': {message}")

    async def start_consumer(self, queue_name: str, callback):
        """
        Inicia un consumidor en una cola específica y ejecuta un callback por mensaje recibido.
        """
        if not self.channel:
            raise Exception("Conexión no inicializada. Llama a connect() primero.")
        queue = await self.channel.declare_queue(queue_name, durable=True)
        print(f"[RabbitMQ] Esperando mensajes en '{queue_name}'...")

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    try:
                        data = json.loads(message.body.decode())
                        await callback(data)
                    except Exception as e:
                        print(f"[RabbitMQ] Error al procesar mensaje: {e}")

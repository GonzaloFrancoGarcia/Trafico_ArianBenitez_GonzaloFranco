"""
Envoltorio robusto sobre aio-pika con:
  • reconexión automática y back-off
  • prefetch configurable
  • publicación con reintentos
  • dispatch por tipo de mensaje
"""

import asyncio, json, logging
from typing import Callable, Dict, Awaitable
import aio_pika
from tenacity import retry, stop_after_attempt, wait_exponential, RetryError
from .message_models import Mensaje

_LOG = logging.getLogger("RabbitMQ")

class RabbitMQClient:
    def __init__(
        self,
        amqp_url: str = "amqp://guest:guest@localhost/",
        prefetch: int = 10
    ):
        self.amqp_url  = amqp_url
        self.prefetch  = prefetch
        self.connection: aio_pika.RobustConnection | None = None
        self.channel   : aio_pika.Channel | None = None

    # ---------- Conexión ---------- #
    async def connect(self) -> None:
        self.connection = await aio_pika.connect_robust(self.amqp_url)
        self.channel    = await self.connection.channel()
        await self.channel.set_qos(prefetch_count=self.prefetch)
        _LOG.info("Conectado a RabbitMQ (%s) con prefetch=%d", self.amqp_url, self.prefetch)

    # ---------- Envío ---------- #
    @retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=0.5, max=10))
    async def send_message(self, message_dict: dict, queue_name: str) -> None:
        if not self.channel:
            raise RuntimeError("Debes llamar a connect() antes de publicar.")

        msg_json = json.dumps(message_dict).encode()
        await self.channel.default_exchange.publish(
            aio_pika.Message(body=msg_json),
            routing_key=queue_name
        )
        _LOG.debug("Publicado en %s: %s", queue_name, message_dict["id"])

    # ---------- Consumo ---------- #
    async def start_consumer(
        self,
        queue_name : str,
        handlers   : Dict[str, Callable[[Mensaje], Awaitable[None]]]
    ) -> None:
        """
        `handlers` es un dict {tipo_mensaje_str: coroutine}.
        Si no existe handler para un tipo, se ignora con aviso.
        """
        if not self.channel:
            raise RuntimeError("Debes llamar a connect() antes de consumir.")

        queue = await self.channel.declare_queue(queue_name, durable=True)
        _LOG.info("Esperando mensajes en '%s'…", queue_name)

        async with queue.iterator() as it:
            async for msg in it:
                async with msg.process():
                    try:
                        m = Mensaje.validate(json.loads(msg.body.decode()))
                        handler = handlers.get(m.tipo.value)
                        if handler:
                            await handler(m)
                        else:
                            _LOG.warning("Sin handler para tipo=%s", m.tipo)
                    except Exception as exc:
                        _LOG.exception("Error procesando mensaje: %s", exc)

# simulacion_trafico/distribution/rabbitmq_client.py
"""
Envoltorio robusto sobre aio-pika para RabbitMQ:

• Reconexión automática  • Prefetch configurable
• Publicación con reintentos (tenacity)
• Dispatcher por tipo de mensaje (handlers)
"""

from __future__ import annotations
import asyncio, json, logging, os
from typing import Callable, Awaitable, Dict

import aio_pika
from tenacity import retry, wait_exponential, stop_after_attempt

from .message_models import Mensaje

_LOG = logging.getLogger("RabbitMQ")


class RabbitMQClient:
    def __init__(
        self,
        amqp_url: str | None = None,
        prefetch: int = 10,
    ) -> None:
        # ── URL por defecto: usuario 'sim' ───────────────
        self.amqp_url: str = (
            amqp_url
            or os.getenv("AMQP_URL", "amqp://sim:sim@localhost/")
        )
        self.prefetch = prefetch

        self.connection: aio_pika.RobustConnection | None = None
        self.channel: aio_pika.Channel | None = None

    # ─────────────────────────────────────────────────────
    # CONEXIÓN
    # ─────────────────────────────────────────────────────
    async def connect(self) -> None:
        self.connection = await aio_pika.connect_robust(self.amqp_url)
        self.channel = await self.connection.channel()
        await self.channel.set_qos(prefetch_count=self.prefetch)
        _LOG.info(
            "Conectado a RabbitMQ (%s) con prefetch=%d",
            self.amqp_url,
            self.prefetch,
        )

    # ─────────────────────────────────────────────────────
    # ENVÍO
    # ─────────────────────────────────────────────────────
    @retry(wait=wait_exponential(multiplier=0.5, max=8), stop=stop_after_attempt(5))
    async def send_message(self, message_dict: dict, queue_name: str) -> None:
        if not self.channel:
            raise RuntimeError("Debes llamar a connect() antes de publicar.")

        body = json.dumps(message_dict).encode()
        await self.channel.default_exchange.publish(
            aio_pika.Message(body=body),
            routing_key=queue_name,
        )
        _LOG.debug("Publicado en %s: %s", queue_name, message_dict.get("id"))

    # ─────────────────────────────────────────────────────
    # CONSUMO
    # ─────────────────────────────────────────────────────
    async def start_consumer(
        self,
        queue_name: str,
        handlers: Dict[str, Callable[[Mensaje], Awaitable[None]]],
    ) -> None:
        """
        `handlers` es un dict  {tipo_mensaje_str: coroutine}.  
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
                            _LOG.warning(
                                "Sin handler para tipo=%s (mensaje %s)",
                                m.tipo.value,
                                m.id,
                            )
                    except Exception as exc:
                        _LOG.exception("Error procesando mensaje: %s", exc)

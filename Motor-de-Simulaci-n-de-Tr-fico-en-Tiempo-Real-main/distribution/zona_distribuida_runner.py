import asyncio, logging
import httpx
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

import performance.metrics as metrics

# ─────────────────────────────────────────────────────────────
COORD_URL       = "http://localhost:8000"           # API FastAPI del coordinador
QUEUE_PROPIA    = "zona_distribuida_queue"
LOG_FORMAT      = "%(name)s | %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
_LOG = logging.getLogger("ZonaDistribuida")
# ─────────────────────────────────────────────────────────────

# ---------- Heart-beat helpers ---------- #
async def registrar_nodo(ciudad: City):
    payload = {
        "zona": ciudad.name,
        "queue": QUEUE_PROPIA,
        "vehiculos": len(ciudad.vehicles),
        "trafico": "MODERADO",
    }
    async with httpx.AsyncClient(timeout=5) as cli:
        await cli.post(f"{COORD_URL}/register", json=payload)
    _LOG.info("Nodo %s registrado en coordinador.", ciudad.name)

async def enviar_heartbeat(ciudad: City):
    while True:
        n = len(ciudad.vehicles)
        traf = "BAJO" if n < 20 else ("ALTO" if n > 50 else "MODERADO")
        payload = {
            "zona": ciudad.name,
            "queue": QUEUE_PROPIA,
            "vehiculos": n,
            "trafico": traf,
        }
        async with httpx.AsyncClient(timeout=5) as cli:
            try:
                r = await cli.post(f"{COORD_URL}/heartbeat", json=payload)
                estado = r.json().get("estado")
                if estado == "OVERLOADED":
                    _LOG.warning("Coordinador indica SOBRE-CARGA; considera limitar entrada.")
            except Exception as exc:
                _LOG.error("Error enviando heart-beat: %s", exc)

        metrics.ESTADO_VEHICULOS.labels(zona=ciudad.name).set(n)
        metrics.HB_ENVIADOS.inc()
        await asyncio.sleep(5)

# ---------- Handler de mensajes ---------- #
async def handle_vehiculo_entrante(m: Mensaje, ciudad: City, rabbit: RabbitMQClient):
    datos = m.datos                      # DatosVehiculoEntrante (Pydantic) validado
    v = Vehicle(
        id_=datos.id,
        position=tuple(datos.posicion),
        speed=datos.velocidad,
        direction=datos.direccion
    )
    ciudad.add_vehicle(v)
    _LOG.info("Vehículo %s integrado en la zona.", v.id_)

    ack = mensaje_ack(
        acked_id=m.id,
        origen=ciudad.name,
        destino=m.origen
    )
    await rabbit.send_message(ack, queue_name=f"{m.origen}_queue")

# ---------- MAIN ---------- #
async def main():
    # ── Ciudad y elementos locales ───────────────────────────
    ciudad = City(name="zona_distribuida")
    ciudad.add_traffic_light(TrafficLight(id_="ZD-T1",
                                          green_time=3, yellow_time=1, red_time=3))
    ciudad.add_vehicle(Vehicle(id_="ZD-V1",
                               position=(0, 0), speed=1.0, direction="SUR"))

    simulator = Simulator(city=ciudad)
    sim_tasks = run_simulation_tasks(simulator, update_interval=0.5)

    # ── Métricas Prometheus ─────────────────────────────────
    metrics.start_metrics_server(port=9200)

    # ── RabbitMQ ────────────────────────────────────────────
    rabbit = RabbitMQClient(prefetch=5)
    await rabbit.connect()

    handlers = {
        TipoMensaje.VEHICULO_ENTRANTE.value:
            lambda m: handle_vehiculo_entrante(m, ciudad, rabbit)
    }
    consumer_task = asyncio.create_task(
        rabbit.start_consumer(QUEUE_PROPIA, handlers)
    )

    # ── Registro inicial y tareas de estado/heart-beat ─────
    await registrar_nodo(ciudad)

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

    await asyncio.gather(
        *sim_tasks,
        consumer_task,
        publicar_estado(),
        enviar_heartbeat(ciudad)
    )

if __name__ == "__main__":
    asyncio.run(main())
# simulacion_trafico/distribution/zona_distribuida_runner.py
"""
Nodo "zona_distribuida"

• Simulación local (City / Vehicle / TrafficLight)
• Registro + heart-beats con el Coordinador
• RabbitMQ → maneja VEHICULO_ENTRANTE
• Migración saliente con balanceo (destino menos cargado)
• Métricas Prometheus en :9200
"""

from __future__ import annotations
import asyncio, logging, httpx, time
from typing import List

from environment.City import City
from environment.Vehicle import Vehicle
from environment.TrafficLight import TrafficLight
from simulation.simulator import Simulator
from concurrency.tasks import run_simulation_tasks

from distribution.rabbitmq_client import RabbitMQClient
from distribution.protocolo        import (
    mensaje_vehiculo_entrante,
    mensaje_estado_zona,
    mensaje_ack,
    TipoMensaje,
)
from distribution.migracion_utils  import destino_menos_cargado
from distribution.message_models   import Mensaje

import performance.metrics as metrics


# ─────────────────────────────────────────────────────────
NOMBRE_ZONA      = "zona_distribuida"
QUEUE_PROPIA     = f"{NOMBRE_ZONA}_queue"
LIMITE_X_POSITIVO = 100.0          # criterio de salida de zona
COORD_URL         = "http://localhost:8000"
HB_SEC            = 5
ESTADO_SEC        = 5
MIGRA_SEC         = 1
# ─────────────────────────────────────────────────────────

logging.basicConfig(level=logging.INFO, format="%(name)s | %(message)s")
_LOG = logging.getLogger(NOMBRE_ZONA)


# ╔════════════════════════════════════════════════════════╗
#  Coordinador: registro + heart-beats
# ╚════════════════════════════════════════════════════════╝
async def registrar(ciudad: City) -> None:
    payload = dict(
        zona=ciudad.name,
        queue=QUEUE_PROPIA,
        vehiculos=len(ciudad.vehicles),
        trafico="MODERADO",
    )
    async with httpx.AsyncClient(timeout=5) as cli:
        await cli.post(f"{COORD_URL}/register", json=payload)
    _LOG.info("Nodo %s registrado en el Coordinador.", ciudad.name)


async def heartbeat(ciudad: City) -> None:
    while True:
        veh = len(ciudad.vehicles)
        traf = "BAJO" if veh < 20 else ("ALTO" if veh > 50 else "MODERADO")

        payload = dict(
            zona=ciudad.name,
            queue=QUEUE_PROPIA,
            vehiculos=veh,
            trafico=traf,
        )
        try:
            async with httpx.AsyncClient(timeout=5) as cli:
                await cli.post(f"{COORD_URL}/heartbeat", json=payload)
        except Exception as exc:
            _LOG.warning("HB error: %s", exc)

        metrics.ESTADO_VEHICULOS.labels(zona=ciudad.name).set(veh)
        metrics.HB_ENVIADOS.inc()
        await asyncio.sleep(HB_SEC)


# ╔════════════════════════════════════════════════════════╗
#  RabbitMQ handlers
# ╚════════════════════════════════════════════════════════╝
async def on_vehicle(m: Mensaje, ciudad: City, rabbit: RabbitMQClient):
    d = m.datos
    v = Vehicle(
        id_=d.id,
        position=tuple(d.posicion),
        speed=d.velocidad,
        direction=d.direccion,
    )
    ciudad.add_vehicle(v)
    _LOG.info("Vehículo %s integrado.", v.id_)

    ack = mensaje_ack(acked_id=m.id, origen=ciudad.name, destino=m.origen)
    await rabbit.send_message(ack, queue_name=f"{m.origen}_queue")


# ╔════════════════════════════════════════════════════════╗
#  Migraciones salientes  (← aquí estaba el AttributeError)
# ╚════════════════════════════════════════════════════════╝
async def revisar_migraciones(ciudad: City, rabbit: RabbitMQClient):
    while True:
        # ciudad.vehicles es LISTA, no dict → iteramos directamente
        salir: List[Vehicle] = [
            v for v in ciudad.vehicles if v.position[0] > LIMITE_X_POSITIVO
        ]
        if salir:
            destino = await destino_menos_cargado(excluir=[ciudad.name])
            if destino:
                for v in salir:
                    ciudad.remove_vehicle(v.id_)
                    msg = mensaje_vehiculo_entrante(
                        vehiculo=dict(
                            id=v.id_,
                            posicion=list(v.position),
                            velocidad=v.speed,
                            direccion=v.direction,
                        ),
                        origen=ciudad.name,
                        destino=destino,
                    )
                    await rabbit.send_message(msg, queue_name=f"{destino}_queue")
                    _LOG.info("Vehículo %s migrado → %s", v.id_, destino)
            else:
                _LOG.warning("Sin destino HEALTHY; %d veh retenidos.", len(salir))
        await asyncio.sleep(MIGRA_SEC)


# ╔════════════════════════════════════════════════════════╗
#  Publicar estado periódico
# ╚════════════════════════════════════════════════════════╝
async def publicar_estado(ciudad: City, rabbit: RabbitMQClient):
    while True:
        estado = dict(
            zona=ciudad.name,
            vehiculos=len(ciudad.vehicles),
            trafico="MODERADO",
            timestamp=time.time(),
        )
        msg = mensaje_estado_zona(datos=estado, origen=ciudad.name, destino="zona_central")        
        await rabbit.send_message(msg, queue_name="zona_central_queue")
        await asyncio.sleep(ESTADO_SEC)


# ╔════════════════════════════════════════════════════════╗
#  Main
# ╚════════════════════════════════════════════════════════╝
async def main():
    # 1. Ciudad base
    ciudad = City(name=NOMBRE_ZONA)
    ciudad.add_traffic_light(TrafficLight("ZD-T1", 3, 1, 3))
    ciudad.add_vehicle(Vehicle("ZD-V1", (0, 0), 1.0, "SUR"))

    # 2. Simulador
    sim = Simulator(ciudad)
    sim_tasks = run_simulation_tasks(sim, update_interval=0.5)

    # 3. Métricas Prometheus
    metrics.start_metrics_server(port=9200)

    # 4. RabbitMQ
    rabbit = RabbitMQClient(prefetch=5)
    await rabbit.connect()
    handlers = {
        TipoMensaje.VEHICULO_ENTRANTE.value: lambda m: on_vehicle(m, ciudad, rabbit)
    }
    consumer = asyncio.create_task(rabbit.start_consumer(QUEUE_PROPIA, handlers))

    # 5. Registro y tareas auxiliares
    await registrar(ciudad)

    await asyncio.gather(
        *sim_tasks,
        consumer,
        heartbeat(ciudad),
        publicar_estado(ciudad, rabbit),
        revisar_migraciones(ciudad, rabbit),
    )


if __name__ == "__main__":
    asyncio.run(main())

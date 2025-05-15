# simulacion_trafico/distribution/zona_distribuida_runner.py
"""
Nodo “zona_distribuida” – versión completa (B-1 + B-2 + B-3)

• Simulación local (Vehicle / TrafficLight / City)  
• Consumo de mensajes RabbitMQ (vehículos entrantes)  
• Heart-beats y registro en el Coordinador central  
• Métricas Prometheus en puerto 9200  
• Balanceo: cuando un vehículo sale de la zona se consulta al Coordinador
   para elegir el destino menos cargado y se publica su migración.
"""

import asyncio
import logging
from typing import Optional, List, Tuple

import httpx

from environment.City import City
from environment.Vehicle import Vehicle
from environment.TrafficLight import TrafficLight
from simulation.simulator import Simulator
from concurrency.tasks import run_simulation_tasks

from distribution.rabbitmq_client import RabbitMQClient
from distribution.protocolo import (
    mensaje_estado_zona,
    mensaje_ack,
    mensaje_vehiculo_entrante,
)
from distribution.message_models import Mensaje, TipoMensaje
from distribution.migracion_utils import destino_menos_cargado

import performance.metrics as metrics

# ─────────────────────────────────────────────────────────────
COORD_URL        = "http://localhost:8000"
NOMBRE_ZONA      = "zona_distribuida"
QUEUE_PROPIA     = f"{NOMBRE_ZONA}_queue"
LIMITE_X_POSITIVO = 100.0         #-- criterio simplificado de “salida de zona”
HEARTBEAT_SEC     = 5
ESTADO_SEC        = 5
MIGRACION_SEC     = 1             #-- revisión periódica de vehículos que salen
# ─────────────────────────────────────────────────────────────

logging.basicConfig(level=logging.INFO, format="%(name)s | %(message)s")
_LOG = logging.getLogger(NOMBRE_ZONA)


# ═════════════════════════════════════════════════════════════
# Helpers – Coordinador
# ═════════════════════════════════════════════════════════════
async def registrar_nodo(ciudad: City) -> None:
    payload = {
        "zona": ciudad.name,
        "queue": QUEUE_PROPIA,
        "vehiculos": len(ciudad.vehicles),
        "trafico": "MODERADO",
    }
    async with httpx.AsyncClient(timeout=5) as cli:
        await cli.post(f"{COORD_URL}/register", json=payload)
    _LOG.info("Nodo %s registrado en el Coordinador.", ciudad.name)


async def enviar_heartbeat(ciudad: City) -> None:
    """Envia heart-beats periódicos al Coordinador."""
    while True:
        n_veh = len(ciudad.vehicles)
        traf  = "BAJO" if n_veh < 20 else ("ALTO" if n_veh > 50 else "MODERADO")

        payload = {
            "zona": ciudad.name,
            "queue": QUEUE_PROPIA,
            "vehiculos": n_veh,
            "trafico": traf,
        }
        try:
            async with httpx.AsyncClient(timeout=5) as cli:
                r = await cli.post(f"{COORD_URL}/heartbeat", json=payload)
                estado = r.json()["estado"]
                if estado == "OVERLOADED":
                    _LOG.warning("Coordinador avisa: SOBRE-CARGA.")
        except Exception as exc:
            _LOG.error("Error enviando heart-beat: %s", exc)

        # Actualizar métricas locales
        metrics.ESTADO_VEHICULOS.labels(zona=ciudad.name).set(n_veh)
        metrics.HB_ENVIADOS.inc()
        await asyncio.sleep(HEARTBEAT_SEC)


# ═════════════════════════════════════════════════════════════
# RabbitMQ – handlers
# ═════════════════════════════════════════════════════════════
async def handle_vehiculo_entrante(
    m: Mensaje,
    ciudad: City,
    rabbit: RabbitMQClient,
) -> None:
    """Procesa VEHICULO_ENTRANTE → añadir a la simulación y enviar ACK."""
    d = m.datos  # DatosVehiculoEntrante (Pydantic) ya validado
    v = Vehicle(id_=d.id, position=tuple(d.posicion),
                speed=d.velocidad, direction=d.direccion)
    ciudad.add_vehicle(v)
    _LOG.info("Vehículo %s integrado en la zona.", v.id_)

    ack = mensaje_ack(
        acked_id=m.id,
        origen=ciudad.name,
        destino=m.origen,
    )
    await rabbit.send_message(ack, queue_name=f"{m.origen}_queue")


# ═════════════════════════════════════════════════════════════
# Migración saliente – detección simplificada
# ═════════════════════════════════════════════════════════════
async def revisar_migraciones(
    ciudad: City,
    rabbit: RabbitMQClient,
) -> None:
    """
    Revisa vehículos cuya x supera LIMITE_X_POSITIVO -> migrarlos
    usando balanceo (destino menos cargado).
    """
    while True:
        salir: List[Vehicle] = [
            v for v in list(ciudad.vehicles.values())
            if v.position[0] > LIMITE_X_POSITIVO
        ]
        if salir:
            destino = await destino_menos_cargado(excluir=[ciudad.name])
            if destino:
                for v in salir:
                    ciudad.remove_vehicle(v.id_)
                    msg = mensaje_vehiculo_entrante(
                        vehiculo={
                            "id": v.id_,
                            "posicion": list(v.position),
                            "velocidad": v.speed,
                            "direccion": v.direction,
                        },
                        origen=ciudad.name,
                        destino=destino,
                    )
                    await rabbit.send_message(
                        msg, queue_name=f"{destino}_queue"
                    )
                    _LOG.info("Vehículo %s migrado → %s", v.id_, destino)
            else:
                _LOG.warning("Sin destino HEALTHY disponible, retengo %d vehículos.", len(salir))
        await asyncio.sleep(MIGRACION_SEC)


# ═════════════════════════════════════════════════════════════
# Publicar estado periódicamente
# ═════════════════════════════════════════════════════════════
async def publicar_estado(ciudad: City, rabbit: RabbitMQClient) -> None:
    while True:
        estado = {
            "zona": ciudad.name,
            "vehiculos": len(ciudad.vehicles),
            "trafico": "MODERADO",
        }
        msg = mensaje_estado_zona(
            estado=estado,
            origen=ciudad.name,
            destino="zona_central",
        )
        await rabbit.send_message(msg, queue_name="zona_central_queue")
        await asyncio.sleep(ESTADO_SEC)


# ═════════════════════════════════════════════════════════════
# MAIN
# ═════════════════════════════════════════════════════════════
async def main() -> None:
    # 1. Entorno local
    ciudad = City(name=NOMBRE_ZONA)
    ciudad.add_traffic_light(TrafficLight(
        id_="ZD-T1", green_time=3, yellow_time=1, red_time=3))
    ciudad.add_vehicle(Vehicle(
        id_="ZD-V1", position=(0, 0), speed=1.0, direction="SUR"))

    simulator = Simulator(city=ciudad)
    sim_tasks = run_simulation_tasks(simulator, update_interval=0.5)

    # 2. Prometheus
    metrics.start_metrics_server(port=9200)

    # 3. RabbitMQ
    rabbit = RabbitMQClient(prefetch=5)
    await rabbit.connect()

    handlers = {
        TipoMensaje.VEHICULO_ENTRANTE.value:
            lambda m: handle_vehiculo_entrante(m, ciudad, rabbit)
    }
    consumer_task = asyncio.create_task(
        rabbit.start_consumer(QUEUE_PROPIA, handlers)
    )

    # 4. Registro + tareas periódicas
    await registrar_nodo(ciudad)

    await asyncio.gather(
        *sim_tasks,
        consumer_task,
        publicar_estado(ciudad, rabbit),
        enviar_heartbeat(ciudad),
        revisar_migraciones(ciudad, rabbit),
    )

if __name__ == "__main__":
    asyncio.run(main())

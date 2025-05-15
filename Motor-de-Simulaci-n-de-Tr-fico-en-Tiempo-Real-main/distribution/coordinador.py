"""
Coordinador central de la simulación distribuida.
 - Registro y heart-beats de nodos
 - Detección de sobrecarga / fallo
 - Exposición de métricas Prometheus
 - API REST para consulta y administración
"""

import time, asyncio
from typing import Dict, Literal
from enum import Enum

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from prometheus_client import (
    Counter, Gauge, Histogram, start_http_server
)

# ---------- MODELOS ---------- #

class EstadoNodo(str, Enum):
    HEALTHY     = "HEALTHY"
    OVERLOADED  = "OVERLOADED"
    UNHEALTHY   = "UNHEALTHY"

class RegistroHB(BaseModel):
    zona        : str
    queue       : str
    vehiculos   : int = Field(..., ge=0)
    trafico     : Literal["BAJO", "MODERADO", "ALTO"]
    timestamp   : float | None = None   # se completará en servidor

# ---------- MÉTRICAS ---------- #
NODOS_TOTALES       = Gauge("nodos_registrados", "Número de nodos registrados")
NODOS_HEALTHY       = Gauge("nodos_healthy", "Nodos en estado HEALTHY")
NODOS_OVERLOADED    = Gauge("nodos_overloaded", "Nodos sobrecargados")
NODOS_UNHEALTHY     = Gauge("nodos_unhealthy", "Nodos sin latido")

HB_RECIBIDOS        = Counter("heartbeats_total", "Heart-beats recibidos")
VEHICULOS_POR_NODO  = Gauge("vehiculos_nodo", "Vehículos actuales por nodo", ["zona"])

# ---------- ALMACEN ---------- #
NODOS: Dict[str, RegistroHB] = {}         # zona → último HB
ESTADO: Dict[str, EstadoNodo] = {}        # zona → estado evaluado

# ---------- FASTAPI ---------- #
app = FastAPI(title="Coordinador Central",
              description="Coordina zonas, balancea y monitoriza.",
              version="0.1")

@app.post("/register", status_code=201)
async def register_node(hb: RegistroHB):
    hb.timestamp = time.time()
    NODOS[hb.zona] = hb
    ESTADO[hb.zona] = EstadoNodo.HEALTHY
    _actualiza_metricas()
    return {"msg": f"Zona {hb.zona} registrada."}

@app.post("/heartbeat")
async def heartbeat(hb: RegistroHB):
    if hb.zona not in NODOS:
        raise HTTPException(status_code=404, detail="Nodo no registrado")
    hb.timestamp = time.time()
    NODOS[hb.zona] = hb
    HB_RECIBIDOS.inc()

    # Evaluar sobrecarga
    if hb.vehiculos > 50 or hb.trafico == "ALTO":
        ESTADO[hb.zona] = EstadoNodo.OVERLOADED
    else:
        ESTADO[hb.zona] = EstadoNodo.HEALTHY

    _actualiza_metricas()
    return {"estado": ESTADO[hb.zona]}

@app.get("/nodos")
async def list_nodes():
    return {
        zona: {
            **hb.dict(),
            "estado": ESTADO[zona]
        } for zona, hb in NODOS.items()
    }

# ---------- BACKGROUND ---------- #
HEARTBEAT_TIMEOUT = 15      # s

async def monitor_health():
    while True:
        now = time.time()
        for zona, hb in list(NODOS.items()):
            if now - hb.timestamp > HEARTBEAT_TIMEOUT:
                ESTADO[zona] = EstadoNodo.UNHEALTHY
        _actualiza_metricas()
        await asyncio.sleep(5)

def _actualiza_metricas():
    NODOS_TOTALES.set(len(NODOS))
    # reset label metrics
    VEHICULOS_POR_NODO.clear()
    healthy = overloaded = unhealthy = 0
    for zona, hb in NODOS.items():
        status = ESTADO[zona]
        if status == EstadoNodo.HEALTHY:
            healthy += 1
        elif status == EstadoNodo.OVERLOADED:
            overloaded += 1
        else:
            unhealthy += 1
        VEHICULOS_POR_NODO.labels(zona=zona).set(hb.vehiculos)
    NODOS_HEALTHY.set(healthy)
    NODOS_OVERLOADED.set(overloaded)
    NODOS_UNHEALTHY.set(unhealthy)

# ---------- ARRANQUE ---------- #
def main():
    # Exponer /metrics en puerto 8001
    start_http_server(8001)
    # Lanzar loop con FastAPI
    import uvicorn
    loop = asyncio.get_event_loop()
    loop.create_task(monitor_health())
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()

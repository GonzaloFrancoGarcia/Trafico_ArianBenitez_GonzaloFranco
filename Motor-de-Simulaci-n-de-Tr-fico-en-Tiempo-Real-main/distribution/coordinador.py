# simulacion_trafico/distribution/coordinador.py
"""
Coordinador central:
• Registro y heart-beats de nodos           • Balanceo: nodo menos cargado
• Detección de UNHEALTHY / OVERLOADED       • Métricas Prometheus
"""
import time, asyncio, logging
from typing import Dict, List, Literal
from enum import Enum

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from prometheus_client import (
    Gauge, Counter, start_http_server
)

# ───────────────────────────────────────── log
logging.basicConfig(level=logging.INFO, format="%(name)s | %(message)s")
_LOG = logging.getLogger("Coordinador")

# ───────────────────────────────────────── modelos
class EstadoNodo(str, Enum):
    HEALTHY     = "HEALTHY"
    OVERLOADED  = "OVERLOADED"
    UNHEALTHY   = "UNHEALTHY"

class RegistroHB(BaseModel):
    zona        : str
    queue       : str
    vehiculos   : int = Field(..., ge=0)
    trafico     : Literal["BAJO", "MODERADO", "ALTO"]
    timestamp   : float | None = None

# ───────────────────────────────────────── almacén
NODOS   : Dict[str, RegistroHB]  = {}
ESTADO  : Dict[str, EstadoNodo]  = {}

# ───────────────────────────────────────── métricas
NODOS_TOTALES       = Gauge("nodos_registrados",     "Nº de nodos")
NODOS_HEALTHY       = Gauge("nodos_healthy",         "Nodos HEALTHY")
NODOS_OVERLOADED    = Gauge("nodos_overloaded",      "Nodos OVERLOADED")
NODOS_UNHEALTHY     = Gauge("nodos_unhealthy",       "Nodos UNHEALTHY")
HB_RECIBIDOS        = Counter("heartbeats_total",    "Heart-beats recibidos")
VEHICULOS_POR_NODO  = Gauge("vehiculos_nodo",        "Vehículos por nodo", ["zona"])

def _actualiza_metricas():
    NODOS_TOTALES.set(len(NODOS))
    VEHICULOS_POR_NODO.clear()
    healthy = overloaded = unhealthy = 0
    for z, hb in NODOS.items():
        if ESTADO[z] == EstadoNodo.HEALTHY:      healthy     += 1
        elif ESTADO[z] == EstadoNodo.OVERLOADED: overloaded  += 1
        else:                                    unhealthy   += 1
        VEHICULOS_POR_NODO.labels(zona=z).set(hb.vehiculos)
    NODOS_HEALTHY.set(healthy)
    NODOS_OVERLOADED.set(overloaded)
    NODOS_UNHEALTHY.set(unhealthy)

# ───────────────────────────────────────── fastapi
app = FastAPI(title="Coordinador Central", version="0.2")

@app.post("/register", status_code=201)
async def register_node(hb: RegistroHB):
    hb.timestamp = time.time()
    NODOS[hb.zona]  = hb
    ESTADO[hb.zona] = EstadoNodo.HEALTHY
    _actualiza_metricas()
    _LOG.info("Nodo %s registrado (vehículos=%d).", hb.zona, hb.vehiculos)
    return {"msg": f"Zona {hb.zona} registrada."}

@app.post("/heartbeat")
async def heartbeat(hb: RegistroHB):
    if hb.zona not in NODOS:
        raise HTTPException(404, "Nodo no registrado")

    hb.timestamp = time.time()
    NODOS[hb.zona] = hb
    HB_RECIBIDOS.inc()

    if hb.vehiculos > 50 or hb.trafico == "ALTO":
        ESTADO[hb.zona] = EstadoNodo.OVERLOADED
    else:
        ESTADO[hb.zona] = EstadoNodo.HEALTHY
    _actualiza_metricas()
    return {"estado": ESTADO[hb.zona]}

@app.get("/nodos")
async def list_nodes():
    return {z: {**hb.dict(), "estado": ESTADO[z]} for z, hb in NODOS.items()}

# -------- BALANCEO: nodo menos cargado ---------------------------------
def _elige_menos_cargado(exclude: List[str]) -> str | None:
    candidatos = [
        (hb.vehiculos, z) for z, hb in NODOS.items()
        if ESTADO[z] == EstadoNodo.HEALTHY and z not in exclude
    ]
    return min(candidatos, default=(None, None))[1]

@app.get("/nodo_menos_cargado")
async def nodo_menos_cargado(exclude: str = Query("", description="Zonas a excluir, separadas por coma")):
    excl = [e.strip() for e in exclude.split(",") if e.strip()]
    zona = _elige_menos_cargado(excl)
    if not zona:
        raise HTTPException(503, "Sin nodo HEALTHY disponible")
    return {"zona": zona}

# -------- Monitor de salud (UNHEALTHY) ---------------------------------
HB_TIMEOUT = 15   # s

async def monitor_health():
    while True:
        ahora = time.time()
        for z, hb in list(NODOS.items()):
            if ahora - hb.timestamp > HB_TIMEOUT:
                if ESTADO[z] != EstadoNodo.UNHEALTHY:
                    ESTADO[z] = EstadoNodo.UNHEALTHY
                    _LOG.warning("Nodo %s marcado UNHEALTHY.", z)
        _actualiza_metricas()
        await asyncio.sleep(5)

# -------- main ---------------------------------------------------------
def main():
    start_http_server(8001)
    loop = asyncio.get_event_loop()
    loop.create_task(monitor_health())
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()

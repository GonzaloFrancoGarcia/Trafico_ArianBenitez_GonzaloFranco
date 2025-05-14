from fastapi import FastAPI
from pydantic import BaseModel
import asyncio
import random

app = FastAPI(title="Coordinador Central")

# Simulamos carga de cada zona
class ZoneReport(BaseModel):
    zone: str
    vehicles: int
    load: float

reports = {}

@app.post("/report")
async def receive_report(r: ZoneReport):
    """
    Cada zona envía su estado aquí periódicamente.
    """
    reports[r.zone] = r
    return {"status": "ok"}

@app.get("/recommend")
def recommend():
    """
    Devuelve la zona con menor carga (para redirigir migraciones).
    """
    if not reports:
        return {"zone": None}
    # elegimos la que tenga menor load
    best = min(reports.values(), key=lambda r: r.load)
    return {"zone": best.zone}

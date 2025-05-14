from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio
import json
from comunicacion.rabbitmq_client import RabbitMQClient

app = FastAPI(title="Microservicio Vehículos")

# Modelo de datos
class VehicleData(BaseModel):
    id: str
    x: float
    y: float
    speed: float
    direction: str
    timestamp: float

# Estado local
vehicles = {}

# Inicializo cliente RabbitMQ
rabbit = RabbitMQClient()

@app.on_event("startup")
async def startup():
    await rabbit.connect()
    # Consumo migraciones entrantes de esta zona
    asyncio.create_task(rabbit.start_consumer(
        queue_name=app.title.lower().replace(" ", "_") + "_queue",
        callback=on_migrate_message
    ))

async def on_migrate_message(msg: dict):
    """
    Callback RabbitMQ: cuando recibimos migración, lo añadimos localmente.
    """
    try:
        v = VehicleData(**msg["datos"])
        vehicles[v.id] = v
        print(f"[vehiculos] Migrado vehículo {v.id}")
    except Exception as e:
        print("[vehiculos] Error procesando migración:", e)

@app.post("/migrate")
async def migrate_vehicle(v: VehicleData):
    """
    Recibe un POST con un vehículo nuevo o que llega de otra zona.
    """
    vehicles[v.id] = v
    return {"status": "ok", "id": v.id}

@app.get("/status")
async def status():
    """
    Estado de este microservicio de vehículos.
    """
    return {
        "zone": app.title,
        "vehicles": len(vehicles),
        "load": round(len(vehicles) * 1.0, 2)
    }

@app.post("/send_migrate/{target_queue}")
async def send_migrate(target_queue: str, v: VehicleData):
    """
    Publica un mensaje de migración hacia otra zona.
    """
    msg = {"tipo": "VEHICULO_ENTRANTE", "datos": v.dict()}
    await rabbit.send_message(msg, queue_name=target_queue)
    return {"status": "migrating", "to": target_queue}

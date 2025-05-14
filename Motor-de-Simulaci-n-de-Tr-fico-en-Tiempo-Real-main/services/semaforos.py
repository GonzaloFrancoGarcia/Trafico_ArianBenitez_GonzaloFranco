from fastapi import FastAPI
import asyncio
from pydantic import BaseModel
from environment.TrafficLight import TrafficLight

app = FastAPI(title="Microservicio Semáforos")

# Ejemplo de semáforos locales  
semaforos = [
    TrafficLight(id_="T1", x=100, y=100, green_time=3, yellow_time=1, red_time=3),
    TrafficLight(id_="T2", x=300, y=100, green_time=3, yellow_time=1, red_time=3),
]

class TLState(BaseModel):
    id: str
    x: int
    y: int
    estado: str

@app.on_event("startup")
async def run_cycle():
    """
    Arranca el ciclo asíncrono de cambio de estados.
    """
    async def loop():
        while True:
            for tl in semaforos:
                tl.update_state()
            await asyncio.sleep(1)  # 1s entre ticks
    asyncio.create_task(loop())

@app.get("/semaforos")
def get_all():
    """
    Devuelve el estado de todos los semáforos de la zona.
    """
    return [TLState(
        id=tl.id_, x=tl.x, y=tl.y, estado=tl.current_state
    ) for tl in semaforos]

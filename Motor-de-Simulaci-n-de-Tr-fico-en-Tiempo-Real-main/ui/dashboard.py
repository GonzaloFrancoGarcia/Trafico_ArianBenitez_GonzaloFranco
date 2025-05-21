# simulacion_trafico/ui/dashboard.py
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader
import httpx, pathlib

BASE_DIR = pathlib.Path(__file__).parent
env = Environment(loader=FileSystemLoader(BASE_DIR / "templates"))

app = FastAPI(title="Dashboard Tráfico Distribuido")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

COORD_URL = "http://localhost:8000"

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    tpl = env.get_template("dashboard.html")
    return tpl.render(request=request)

@app.get("/snapshot")
async def snapshot():
    # Llamada al coordinador para obtener todos los nodos
    async with httpx.AsyncClient(timeout=5) as cli:
        r = await cli.get(f"{COORD_URL}/nodos")
        r.raise_for_status()
        data = r.json()
    # Devolvemos la lista de valores: {"zona","vehiculos","trafico",...}
    return JSONResponse(content={"nodos": list(data.values())})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("dashboard:app", host="0.0.0.0", port=8500, reload=True)

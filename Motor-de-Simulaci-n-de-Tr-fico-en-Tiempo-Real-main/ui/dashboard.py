# simulacion_trafico/ui/dashboard.py
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader
import httpx, pathlib

BASE_DIR = pathlib.Path(__file__).parent
env = Environment(loader=FileSystemLoader(BASE_DIR / "templates"))

app = FastAPI(title="Dashboard Tráfico Distribuido")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

COORD_URL = "http://localhost:8000"        # coordinador

@app.get("/", response_class=HTMLResponse)
async def root():
    tpl = env.get_template("dashboard.html")
    return tpl.render()

@app.get("/snapshot")
async def snapshot():
    async with httpx.AsyncClient(timeout=5) as cli:
        r = await cli.get(f"{COORD_URL}/nodos")
    return {"nodos": list(r.json().values())}

def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8500)

if __name__ == "__main__":
    main()

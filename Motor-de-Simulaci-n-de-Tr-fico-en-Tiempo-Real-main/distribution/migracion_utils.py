# simulacion_trafico/distribution/migracion_utils.py
"""
Utilidades para que un nodo averigüe el destino más ligero
antes de publicar una migración.
"""
import httpx, logging
from typing import Optional, List

COORD_URL = "http://localhost:8000"

async def destino_menos_cargado(excluir: List[str]) -> Optional[str]:
    """
    Devuelve la zona HEALTHY con menos vehículos,
    excluyendo las que se pasen en la lista.
    """
    excl_param = ",".join(excluir)
    try:
        async with httpx.AsyncClient(timeout=5) as cli:
            r = await cli.get(f"{COORD_URL}/nodo_menos_cargado",
                              params={"exclude": excl_param})
            return r.json()["zona"]
    except Exception as exc:
        logging.getLogger("MigracionUtils").error("Error consultando coordinador: %s", exc)
        return None

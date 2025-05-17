# simulacion_trafico/distribution/migracion_utils.py
"""
Utilidades de balanceo de carga y elección de nodo destino.
"""

from __future__ import annotations
import httpx, logging
from typing import List, Optional

_LOG = logging.getLogger("Balanceo")


COORD_URL = "http://localhost:8000"


async def destino_menos_cargado(excluir: List[str] | None = None) -> Optional[str]:
    """
    Devuelve el nombre del nodo con menos vehículos, excluyendo los
    indicados.  Si no se puede contactar al Coordinador, retorna None.
    """
    excluir = set(excluir or [])

    try:
        async with httpx.AsyncClient(timeout=2) as cli:
            r = await cli.get(f"{COORD_URL}/nodos")
            r.raise_for_status()
            data = r.json()
    except Exception as exc:
        _LOG.warning("No pude consultar al Coordinador: %s", exc)
        return None

    # Filtrar nodos excluidos
    candidatos = [
        info for name, info in data.items() if name not in excluir
    ]
    if not candidatos:
        return None

    # Elige el que menos vehículos tenga
    destino = min(candidatos, key=lambda i: i["vehiculos"])
    return destino["zona"]

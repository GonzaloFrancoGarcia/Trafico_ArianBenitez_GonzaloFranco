# simulacion_trafico/distribution/protocolo.py
"""
Especificación de los mensajes intercambiados entre nodos.

• Todos los mensajes siguen el formato del helper `crear_mensaje`.
• Los tipos están definidos en la Enum `TipoMensaje`.
"""

from __future__ import annotations
from enum import Enum
from datetime import datetime, timezone
import uuid
from typing import Any, Dict


# ──────────────────────────────────────────────────────────
#  Enumeración de tipos de mensaje
# ──────────────────────────────────────────────────────────
class TipoMensaje(str, Enum):
    VEHICULO_ENTRANTE   = "VEHICULO_ENTRANTE"
    ESTADO_ZONA         = "ESTADO_ZONA"
    ACTUALIZACION_SEMAFORO = "ACTUALIZACION_SEMAFORO"
    ACK                 = "ACK"


# ──────────────────────────────────────────────────────────
#  Helper generador
# ──────────────────────────────────────────────────────────
def crear_mensaje(
    *,
    tipo: TipoMensaje,
    datos: Dict[str, Any],
    origen: str,
    destino: str,
) -> Dict[str, Any]:
    """
    Fabrica un mensaje estándar con UUID y timestamp UTC ISO-8601.
    """
    return {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tipo": tipo.value,
        "origen": origen,
        "destino": destino,
        "datos": datos,
    }


# ──────────────────────────────────────────────────────────
#  Fábricas concretas
# ──────────────────────────────────────────────────────────
def mensaje_vehiculo_entrante(
    vehiculo: Dict[str, Any],
    origen: str,
    destino: str,
) -> Dict[str, Any]:
    return crear_mensaje(
        tipo=TipoMensaje.VEHICULO_ENTRANTE,
        datos=vehiculo,
        origen=origen,
        destino=destino,
    )


def mensaje_estado_zona(
    datos: Dict[str, Any],
    origen: str,
    destino: str,
) -> Dict[str, Any]:
    """
    Mensaje periódico con el estado agregado de una zona.
    (vehículos, tráfico, timestamp, etc.)
    """
    return crear_mensaje(
        tipo=TipoMensaje.ESTADO_ZONA,
        datos=datos,
        origen=origen,
        destino=destino,
    )


def mensaje_ack(
    acked_id: str,
    origen: str,
    destino: str,
) -> Dict[str, Any]:
    return crear_mensaje(
        tipo=TipoMensaje.ACK,
        datos={"acked_id": acked_id},
        origen=origen,
        destino=destino,
    )

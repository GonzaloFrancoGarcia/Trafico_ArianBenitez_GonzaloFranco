"""
Funciones utilitarias para construir mensajes validados.
"""

import uuid
from datetime import datetime
from .message_models import Mensaje, TipoMensaje, DatosVehiculoEntrante, DatosEstadoZona, DatosAck

def crear_id() -> str:
    return str(uuid.uuid4())

def ahora_utc() -> datetime:
    return datetime.utcnow()

# ---- Fábricas específicas ---- #

def mensaje_vehiculo_entrante(*, vehiculo: dict, origen: str, destino: str) -> dict:
    return Mensaje(
        id=crear_id(),
        timestamp=ahora_utc(),
        tipo=TipoMensaje.VEHICULO_ENTRANTE,
        origen=origen,
        destino=destino,
        datos=DatosVehiculoEntrante(**vehiculo).dict()
    ).dict()

def mensaje_estado_zona(*, estado: dict, origen: str, destino: str) -> dict:
    return Mensaje(
        id=crear_id(),
        timestamp=ahora_utc(),
        tipo=TipoMensaje.ESTADO_ZONA,
        origen=origen,
        destino=destino,
        datos=DatosEstadoZona(**estado).dict()
    ).dict()

def mensaje_ack(*, acked_id: str, origen: str, destino: str) -> dict:
    return Mensaje(
        id=crear_id(),
        timestamp=ahora_utc(),
        tipo=TipoMensaje.ACK,
        origen=origen,
        destino=destino,
        datos=DatosAck(acked_id=acked_id).dict()
    ).dict()

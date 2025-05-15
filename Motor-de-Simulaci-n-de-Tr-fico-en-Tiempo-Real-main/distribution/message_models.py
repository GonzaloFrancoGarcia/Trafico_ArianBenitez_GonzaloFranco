"""
Modelos Pydantic que tipan y validan la mensajería entre nodos.
"""

from enum import Enum
from datetime import datetime
from typing import List, Tuple, Literal
from pydantic import BaseModel, Field

class TipoMensaje(str, Enum):
    VEHICULO_ENTRANTE   = "VEHICULO_ENTRANTE"
    ESTADO_ZONA         = "ESTADO_ZONA"
    ACK                 = "ACK"

# ---------- Contenidos de `datos` por tipo ---------- #

class DatosVehiculoEntrante(BaseModel):
    id          : str
    posicion    : Tuple[float, float] = Field(..., min_items=2, max_items=2)
    velocidad   : float
    direccion   : Literal["NORTE", "SUR", "ESTE", "OESTE"]

class DatosEstadoZona(BaseModel):
    zona        : str
    vehiculos   : int
    trafico     : Literal["BAJO", "MODERADO", "ALTO"]

class DatosAck(BaseModel):
    acked_id    : str
    ok          : bool = True

# ---------- Mensaje genérico ---------- #

class Mensaje(BaseModel):
    id          : str
    timestamp   : datetime
    tipo        : TipoMensaje
    origen      : str
    destino     : str
    datos       : dict              # se valida dinámicamente

    # validación condicional según tipo
    @classmethod
    def validate(cls, obj):
        m = super().validate(obj)

        if m.tipo is TipoMensaje.VEHICULO_ENTRANTE:
            m.datos = DatosVehiculoEntrante(**m.datos)
        elif m.tipo is TipoMensaje.ESTADO_ZONA:
            m.datos = DatosEstadoZona(**m.datos)
        elif m.tipo is TipoMensaje.ACK:
            m.datos = DatosAck(**m.datos)
        return m

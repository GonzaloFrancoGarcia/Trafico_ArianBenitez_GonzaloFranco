
# simulacion_trafico/comunicacion/protocolo.py

"""
Define los formatos de mensaje usados entre zonas distribuidas.
"""

from enum import Enum
import uuid
from datetime import datetime

class TipoMensaje(str, Enum):
    VEHICULO_ENTRANTE = "VEHICULO_ENTRANTE"
    ESTADO_ZONA = "ESTADO_ZONA"
    ALIANZA = "ALIANZA"
    ACTUALIZACION_SEMAFORO = "ACTUALIZACION_SEMAFORO"
    ACK = "ACK"

def crear_mensaje(tipo: TipoMensaje, datos: dict, origen: str = "zona_x", destino: str = "zona_y") -> dict:
    return {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat(),
        "tipo": tipo.value,
        "origen": origen,
        "destino": destino,
        "datos": datos
    }

# Ejemplo de datos para VEHICULO_ENTRANTE
# {
#     "id": "V42",
#     "posicion": [10, 0],
#     "velocidad": 1.5,
#     "direccion": "ESTE"
# }

# Ejemplo de datos para ESTADO_ZONA
# {
#     "zona": "zona_este",
#     "vehiculos": 8,
#     "trafico": "ALTO"
# }

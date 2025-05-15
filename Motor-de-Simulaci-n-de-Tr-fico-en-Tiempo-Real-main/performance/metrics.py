# simulacion_trafico/performance/metrics.py

import logging
from prometheus_client import Gauge, Counter, start_http_server

# Configuramos un logger básico
logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger("SimMetrics")

def log_simulation_state(simulator):
    """
    Registra un snapshot del simulador en el logger INFO.
    """
    snapshot = simulator.get_snapshot()
    _logger.info("Estado de la simulación: %s", snapshot)

def log_simulation_state(simulator):
    """
    Función de ejemplo que registra el estado de la simulación.
    """
    snapshot = simulator.get_snapshot()
    logging.info(f"Estado de la simulación: {snapshot}")

ESTADO_VEHICULOS = Gauge(
    "vehiculos_en_zona",
    "Número de vehículos presentes en la zona",
    ["zona"]
)

HB_ENVIADOS = Counter(
    "heartbeats_enviados_total",
    "Heart-beats enviados por este nodo"
)

def start_metrics_server(port: int = 9200):
    """
    Arranca el servidor HTTP de Prometheus en el puerto indicado.
    Llamar una sola vez en el arranque del runner.
    """
    _logger.info("Prometheus metrics listening on :%d", port)
    start_http_server(port)
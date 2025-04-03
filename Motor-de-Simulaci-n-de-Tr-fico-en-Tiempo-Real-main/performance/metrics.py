# simulacion_trafico/performance/metrics.py

import logging

# Configuramos un logger básico
logging.basicConfig(level=logging.INFO)

def log_simulation_state(simulator):
    """
    Función de ejemplo que registra el estado de la simulación.
    """
    snapshot = simulator.get_snapshot()
    logging.info(f"Estado de la simulación: {snapshot}")

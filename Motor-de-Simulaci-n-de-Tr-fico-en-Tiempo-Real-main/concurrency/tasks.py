# simulacion_trafico/concurrency/tasks.py

import asyncio

async def simulation_loop(simulator, interval):
    """
    Bucle principal que actualiza periódicamente la simulación.
    """
    while True:
        simulator.update()
        # print("[Simulación] Estado actualizado.")  # Descomenta para debug
        await asyncio.sleep(interval)

def run_simulation_tasks(simulator, update_interval=1.0):
    """
    Devuelve una lista de corutinas (no tareas) para ejecutar la simulación.
    El hilo que arranque estas corutinas será responsable de convertirlas en tareas.
    """
    # Simplemente devolvemos la corutina; no tocamos create_task aquí
    return [simulation_loop(simulator, update_interval)]

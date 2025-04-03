# simulacion_trafico/concurrency/tasks.py

import asyncio

async def simulation_loop(simulator, interval):
    """
    Bucle que actualiza periódicamente la simulación.
    """
    while True:
        simulator.update()
        await asyncio.sleep(interval)

def run_simulation_tasks(simulator, update_interval=1.0):
    """
    Crea y devuelve una lista de tareas asíncronas necesarias para la simulación:
    - Bucle de actualización de la ciudad
    - En un caso complejo, aquí se podrían añadir más tareas.
    """
    tasks = []
    tasks.append(asyncio.create_task(simulation_loop(simulator, update_interval)))
    return tasks

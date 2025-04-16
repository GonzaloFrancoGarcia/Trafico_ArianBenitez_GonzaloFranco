# simulacion_trafico/concurrency/tasks.py

import asyncio

async def simulation_loop(simulator, interval):
    """
    Bucle principal que actualiza periódicamente la simulación.
    """
    while True:
        simulator.update()
        # print("[Simulación] Estado actualizado.")  # Activar para depuración
        await asyncio.sleep(interval)

def run_simulation_tasks(simulator, update_interval=1.0):
    """
    Devuelve una lista de tareas asíncronas necesarias para la simulación:
    - Actualización periódica del simulador
    - Aquí se pueden añadir tareas adicionales (sensores, registro, etc.)
    """
    tasks = []
    main_task = asyncio.create_task(simulation_loop(simulator, update_interval))
    main_task.set_name("simulacion_loop")
    tasks.append(main_task)
    return tasks
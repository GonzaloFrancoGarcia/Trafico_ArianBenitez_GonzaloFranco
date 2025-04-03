# simulacion_trafico/ui/gui.py

import asyncio

async def launch_gui(simulator):
    """
    Ejemplo de interfaz "gráfica" minimalista que simplemente imprime el estado
    de la simulación cada X segundos. En un proyecto real, aquí se usaría Pygame,
    Tkinter o cualquier otra librería de tu preferencia.
    """
    while True:
        snapshot = simulator.get_snapshot()
        print("\n--- Estado Actual de la Simulación ---")
        print("Semáforos:")
        for tl_info in snapshot["traffic_lights"]:
            print("  ", tl_info)
        print("Vehículos:")
        for v_info in snapshot["vehicles"]:
            print("  ", v_info)
        await asyncio.sleep(2)  # Ajusta el intervalo de refresco según tus necesidades

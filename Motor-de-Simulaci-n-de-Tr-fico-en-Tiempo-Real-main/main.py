# simulacion_trafico/main.py

from ui.gui import GUISimulation

def main():
    """
    Punto de entrada unificado para la simulación local con interfaz Pygame.
    Configura una ciudad en la zona 'zona_distribuida' y arranca la GUI.
    """
    gui = GUISimulation("zona_distribuida")
    gui.run()

if __name__ == "__main__":
    main()

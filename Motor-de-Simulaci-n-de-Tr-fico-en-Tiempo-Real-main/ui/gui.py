# simulacion_trafico/ui/gui.py

import asyncio
import pygame

WIDTH, HEIGHT = 800, 600
BACKGROUND_COLOR = (30, 30, 30)
VEHICLE_COLOR = (0, 150, 255)
STOPPED_VEHICLE_COLOR = (200, 0, 0)
ROAD_COLOR = (120, 120, 120)
FONT_COLOR = (255, 255, 255)
FPS_COLOR = (200, 200, 200)
BOUND_COLOR = (255, 255, 255)

def draw_roads(screen, intersections, tolerance=10):
    """
    Dibuja carreteras conectando intersecciones del grid.
    Se agrupan intersecciones alineadas horizontal o verticalmente.
    """
    if not intersections:
        return
    # Grupos horizontales
    horizontal = {}
    for inter in intersections:
        y = inter.get("y", 0)
        key = round(y / tolerance) * tolerance
        horizontal.setdefault(key, []).append(inter)
    for group in horizontal.values():
        if len(group) >= 2:
            group.sort(key=lambda i: i.get("x", 0))
            for i in range(len(group) - 1):
                x1 = group[i].get("x", 0)
                x2 = group[i+1].get("x", 0)
                y_val = group[i].get("y", 0)
                start = (int(x1), int(y_val))
                end = (int(x2), int(y_val))
                pygame.draw.line(screen, ROAD_COLOR, start, end, 5)
    # Grupos verticales
    vertical = {}
    for inter in intersections:
        x = inter.get("x", 0)
        key = round(x / tolerance) * tolerance
        vertical.setdefault(key, []).append(inter)
    for group in vertical.values():
        if len(group) >= 2:
            group.sort(key=lambda i: i.get("y", 0))
            for i in range(len(group) - 1):
                y1 = group[i].get("y", 0)
                y2 = group[i+1].get("y", 0)
                x_val = group[i].get("x", 0)
                start = (int(x_val), int(y1))
                end = (int(x_val), int(y2))
                pygame.draw.line(screen, ROAD_COLOR, start, end, 5)

async def launch_gui(simulator):
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Simulación de Tráfico")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 20)

    running = True
    # Mapeo 1:1; consideramos que las coordenadas del mundo son 0-800 y 0-600.
    scale = 1.0
    offset = (0, 0)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(BACKGROUND_COLOR)

        # Dibujar límite (rectángulo) del área
        pygame.draw.rect(screen, BOUND_COLOR, (0, 0, WIDTH, HEIGHT), 2)

        snapshot = simulator.get_snapshot()

        # Dibujar carreteras basadas en intersecciones
        intersections = snapshot.get("intersections", [])
        draw_roads(screen, intersections)

        # Dibujar intersecciones (círculos amarillos)
        for inter in intersections:
            try:
                x = int(inter.get("x", 0) * scale + offset[0])
                y = int(inter.get("y", 0) * scale + offset[1])
                pygame.draw.circle(screen, (255, 255, 0), (x, y), 8)
            except Exception as e:
                print("Error drawing intersection:", e)
                continue

        # Dibujar semáforos (fijos)
        for tl in snapshot.get("traffic_lights", []):
            try:
                x = int(tl.get("x", 0) * scale + offset[0])
                y = int(tl.get("y", 0) * scale + offset[1])
                estado = tl.get("estado", "RED").upper()
                if estado == "GREEN":
                    color = (0, 255, 0)
                elif estado == "YELLOW":
                    color = (255, 255, 0)
                else:
                    color = (255, 0, 0)
                pygame.draw.circle(screen, color, (x, y), 15)
                label = font.render(estado, True, FONT_COLOR)
                screen.blit(label, (x - 20, y + 20))
            except Exception as e:
                print("Error drawing traffic light:", e)
                continue

        # Dibujar vehículos (más grandes: 30x15)
        for v in snapshot.get("vehicles", []):
            try:
                x = int(v.get("x", 0) * scale + offset[0])
                y = int(v.get("y", 0) * scale + offset[1])
                # Si el vehículo está detenido, usar color alterno
                veh_color = STOPPED_VEHICLE_COLOR if not v.get("moving", True) else VEHICLE_COLOR
                rect = pygame.Rect(x, y, 30, 15)
                pygame.draw.rect(screen, veh_color, rect)
            except Exception as e:
                print("Error drawing vehicle:", e)
                continue

        # Mostrar estadísticas (cantidad de vehículos, FPS)
        stats = f"Vehículos: {len(snapshot.get('vehicles', []))}"
        fps_text = f"FPS: {int(clock.get_fps())}"
        screen.blit(font.render(stats, True, FONT_COLOR), (10, 10))
        screen.blit(font.render(fps_text, True, FPS_COLOR), (10, 30))

        pygame.display.flip()
        await asyncio.sleep(0.001)
        clock.tick(30)

    pygame.quit()

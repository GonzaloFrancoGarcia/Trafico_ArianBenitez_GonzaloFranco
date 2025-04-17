# simulacion_trafico/ui/gui.py

import asyncio
import pygame

WIDTH, HEIGHT = 800, 600
BACKGROUND_COLOR = (30, 30, 30)
VEHICLE_COLOR = (0, 150, 255)
STOPPED_VEHICLE_COLOR = (200, 0, 0)
ROAD_COLOR = (120, 120, 120)
BOUND_COLOR = (255, 255, 255)
FONT_COLOR = (255, 255, 255)
FPS_COLOR = (200, 200, 200)

def draw_roads(screen, intersections, tol=10):
    # Dibuja carreteras horizontales y verticales según intersecciones
    if not intersections:
        return
    horiz, vert = {}, {}
    for inter in intersections:
        y = round(inter["y"]/tol)*tol
        horiz.setdefault(y, []).append(inter)
        x = round(inter["x"]/tol)*tol
        vert.setdefault(x, []).append(inter)
    for y, grp in horiz.items():
        if len(grp) >= 2:
            xs = sorted(i["x"] for i in grp)
            pygame.draw.line(screen, ROAD_COLOR, (xs[0], y), (xs[-1], y), 5)
    for x, grp in vert.items():
        if len(grp) >= 2:
            ys = sorted(i["y"] for i in grp)
            pygame.draw.line(screen, ROAD_COLOR, (x, ys[0]), (x, ys[-1]), 5)

async def launch_gui(simulator):
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Simulación de Tráfico")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 20)
    running = True

    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False

        screen.fill(BACKGROUND_COLOR)
        pygame.draw.rect(screen, BOUND_COLOR, (0, 0, WIDTH, HEIGHT), 2)

        snap = simulator.get_snapshot()
        draw_roads(screen, snap["intersections"])

        # Dibujar semáforos
        for tl in snap["traffic_lights"]:
            x, y = int(tl["x"]), int(tl["y"])
            st = tl["estado"]
            color = (255, 0, 0) if st == "RED" else (0, 255, 0)
            pygame.draw.circle(screen, color, (x, y), 15)
            screen.blit(font.render(st, True, FONT_COLOR), (x - 20, y + 20))

        # Dibujar vehículos
        for v in snap["vehicles"]:
            x, y = v["x"], v["y"]
            mv = v.get("moving", True)
            color = VEHICLE_COLOR if mv else STOPPED_VEHICLE_COLOR
            if v["direction"] in ("NORTE", "SUR"):
                w, h = 15, 30
            else:
                w, h = 30, 15
            rect = pygame.Rect(int(x - w/2), int(y - h/2), w, h)
            pygame.draw.rect(screen, color, rect)

        # Estadísticas
        screen.blit(font.render(f"Vehículos: {len(snap['vehicles'])}", True, FONT_COLOR), (10, 10))
        screen.blit(font.render(f"FPS: {int(clock.get_fps())}", True, FPS_COLOR), (10, 30))

        pygame.display.flip()
        await asyncio.sleep(0.001)
        clock.tick(30)

    pygame.quit()

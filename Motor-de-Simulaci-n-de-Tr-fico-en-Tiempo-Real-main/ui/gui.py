import asyncio
import pygame
import hashlib

WIDTH, HEIGHT = 800, 800
BG_COLOR = (30, 30, 30)
STOP_COLOR = (200, 0, 0)
ROAD_COLOR = (120, 120, 120)
BOUND_COLOR = (255, 255, 255)
FONT_COLOR = (255, 255, 255)
FPS_COLOR = (200, 200, 200)

def draw_roads(screen, intersections, tol=10):
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

def color_from_id(id_str):
    h = hashlib.md5(id_str.encode()).digest()
    return (h[0], h[1], h[2])

async def launch_gui(simulator):
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Simulación de Tráfico")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 20)

    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                return

        simulator.update()

        screen.fill(BG_COLOR)
        pygame.draw.rect(screen, BOUND_COLOR, (0, 0, WIDTH, HEIGHT), 2)

        snap = simulator.get_snapshot()
        draw_roads(screen, snap["intersections"])

        # Semáforos con tres colores
        for tl in snap["traffic_lights"]:
            x, y = int(tl["x"]), int(tl["y"])
            st = tl["estado"].upper()
            if st == "RED":
                color = (255, 0, 0)
            elif st == "YELLOW":
                color = (255, 255, 0)
            else:  # GREEN
                color = (0, 255, 0)
            pygame.draw.circle(screen, color, (x, y), 15)
            screen.blit(font.render(st, True, FONT_COLOR), (x - 20, y + 20))

        # Vehículos
        for v in snap["vehicles"]:
            x, y = v["x"], v["y"]
            moving = v.get("moving", True)
            base = color_from_id(v["id"])
            col = base if moving else STOP_COLOR
            if v["direction"] in ("NORTE", "SUR"):
                w, h = 15, 30
            else:
                w, h = 30, 15
            pygame.draw.rect(screen, col, pygame.Rect(int(x-w/2), int(y-h/2), w, h))

        screen.blit(font.render(f"Vehículos: {len(snap['vehicles'])}", True, FONT_COLOR), (10, 10))
        screen.blit(font.render(f"FPS: {int(clock.get_fps())}", True, FPS_COLOR), (10, 30))

        pygame.display.flip()
        await asyncio.sleep(0)
        clock.tick(60)

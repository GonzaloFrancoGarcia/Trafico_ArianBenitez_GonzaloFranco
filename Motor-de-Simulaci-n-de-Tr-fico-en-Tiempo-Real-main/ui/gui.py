# simulacion_trafico/ui/gui.py

import asyncio
import pygame

# Configuración visual
WIDTH, HEIGHT = 800, 600
BACKGROUND_COLOR = (30, 30, 30)
VEHICLE_COLOR = (0, 150, 255)
FONT_COLOR = (255, 255, 255)
FPS_COLOR = (200, 200, 200)

CAMERA_SPEED = 5

async def launch_gui(simulator):
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Simulación de Tráfico")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 20)

    running = True
    camera_offset = [0, 0]  # x, y

    while running:
        # Manejo de eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Movimiento de cámara
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            camera_offset[0] += CAMERA_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            camera_offset[0] -= CAMERA_SPEED
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            camera_offset[1] += CAMERA_SPEED
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            camera_offset[1] -= CAMERA_SPEED

        # Limpiar pantalla
        screen.fill(BACKGROUND_COLOR)

        # Obtener snapshot del simulador
        snapshot = simulator.get_snapshot()

        # Dibujar semáforos
        for i, tl_info in enumerate(snapshot["traffic_lights"]):
            estado = "RED"
            if "GREEN" in tl_info:
                color = (0, 255, 0)
                estado = "GREEN"
            elif "YELLOW" in tl_info:
                color = (255, 255, 0)
                estado = "YELLOW"
            else:
                color = (255, 0, 0)

            x, y = 100 + i*100 + camera_offset[0], 50 + camera_offset[1]
            pygame.draw.circle(screen, color, (x, y), 15)
            label = font.render(estado, True, FONT_COLOR)
            screen.blit(label, (x - 20, y + 20))

        # Dibujar vehículos
        for v_info in snapshot["vehicles"]:
            try:
                id_part = v_info.split("at position (")[1]
                pos_str = id_part.split(")")[0]
                x, y = map(float, pos_str.split(","))
                x += camera_offset[0]
                y += camera_offset[1]
                rect = pygame.Rect(int(x), int(y), 20, 10)
                pygame.draw.rect(screen, VEHICLE_COLOR, rect)
            except:
                pass

        # Mostrar estadísticas
        stats = f"Vehículos: {len(snapshot['vehicles'])}"
        fps_text = f"FPS: {int(clock.get_fps())}"
        screen.blit(font.render(stats, True, FONT_COLOR), (10, 10))
        screen.blit(font.render(fps_text, True, FPS_COLOR), (10, 30))

        # Actualizar pantalla
        pygame.display.flip()
        clock.tick(30)
        await asyncio.sleep(0.01)

    pygame.quit()
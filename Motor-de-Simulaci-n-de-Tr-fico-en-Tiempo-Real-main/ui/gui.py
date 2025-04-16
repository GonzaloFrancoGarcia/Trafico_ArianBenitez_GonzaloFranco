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
SCALE = 1.0  # Factor de escala (puedes ajustar si las coordenadas del mundo son muy grandes o pequeñas)

async def launch_gui(simulator):
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Simulación de Tráfico")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 20)

    running = True

    # Ajuste de la cámara para que (0,0) (coordenadas del mundo) quede en el centro de la pantalla
    camera_offset = [WIDTH // 2, HEIGHT // 2]

    while running:
        # Manejo de eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Movimiento de cámara (las teclas modifican el offset)
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
        for tl in snapshot.get("traffic_lights", []):
            try:
                # Calcula la posición en pantalla: escala + offset
                x = int(tl.get("x", 0) * SCALE + camera_offset[0])
                y = int(tl.get("y", 0) * SCALE + camera_offset[1])
                # Solo dibujar si está dentro de la ventana
                if 0 <= x <= WIDTH and 0 <= y <= HEIGHT:
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
                print("Error al renderizar semáforo:", e)
                continue

        # Dibujar vehículos
        for v in snapshot.get("vehicles", []):
            try:
                x = int(v.get("x", 0) * SCALE + camera_offset[0])
                y = int(v.get("y", 0) * SCALE + camera_offset[1])
                if 0 <= x <= WIDTH and 0 <= y <= HEIGHT:
                    rect = pygame.Rect(x, y, 20, 10)
                    pygame.draw.rect(screen, VEHICLE_COLOR, rect)
            except Exception as e:
                print("Error al renderizar vehículo:", e)
                continue

        # Mostrar estadísticas (número de vehículos y FPS)
        stats = f"Vehículos: {len(snapshot.get('vehicles', []))}"
        fps_text = f"FPS: {int(clock.get_fps())}"
        screen.blit(font.render(stats, True, FONT_COLOR), (10, 10))
        screen.blit(font.render(fps_text, True, FPS_COLOR), (10, 30))

        # Actualizar pantalla y sincronizar el loop
        pygame.display.flip()
        await asyncio.sleep(0.001)
        clock.tick(30)

    pygame.quit()

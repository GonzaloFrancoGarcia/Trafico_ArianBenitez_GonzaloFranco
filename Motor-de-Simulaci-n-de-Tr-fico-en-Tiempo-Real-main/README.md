# Motor de Simulación de Tráfico en Tiempo Real

Simulador urbano modular, visual y escalable para representar el tráfico en una ciudad virtual usando Python, Pygame, concurrencia y distribución con RabbitMQ.

---

## 📁 Estructura del Proyecto

```bash
simulacion_trafico/
├── main.py                          # Lanzador principal de simulación local
├── zona_runner.py                  # Simulación autónoma de una zona
├── README.md
│
├── environment/                    # Entidades urbanas
│   ├── __init__.py
│   ├── city.py                     # Contiene vehículos, semáforos, intersecciones
│   ├── intersection.py             # Representa puntos de cruce
│   ├── traffic_light.py            # Semáforo con lógica de tiempo
│   ├── vehicle.py                  # Vehículo con posición, dirección, velocidad
│   ├── test_city_runner.py
│   └── test_intersection_runner.py
│
├── simulation/
│   ├── __init__.py
│   └── simulator.py                # Motor de simulación (update() + snapshot)
│
├── concurrency/
│   ├── __init__.py
│   └── tasks.py                    # Bucle asíncrono de simulación
│
├── ui/
│   ├── __init__.py
│   └── gui.py                      # Interfaz visual con Pygame, cámara, FPS
│
├── distribution/                   # Simulación distribuida y mensajería
│   ├── __init__.py
│   ├── protocolo.py                # Estructura estándar de mensajes
│   ├── rabbit_client.py            # Cliente RabbitMQ (envío y consumo)
│   ├── send_vehicle_to_zona_distribuida.py
│   └── zona_distribuida_runner.py  # Microservicio de simulación de zona
│
├── performance/
│   ├── __init__.py
│   └── metrics.py                  # (Placeholder) para logging y rendimiento
```

---

## 🚀 Cómo ejecutar la simulación

1. Instala dependencias:
```bash
pip install pygame aio-pika
```

2. Ejecuta la simulación local:
```bash
python main.py
```

3. Ejecuta una zona independiente (modo distribuido):
```bash
python distribution/zona_distribuida_runner.py
```

4. Envía un vehículo a una zona (desde otra):
```bash
python distribution/send_vehicle_to_zona_distribuida.py
```

⚠️ Asegúrate de tener RabbitMQ ejecutándose en localhost.

---

## 🧱 Cómo funciona

- Cada tick de simulación actualiza vehículos y semáforos
- La GUI se refresca con snapshot() en tiempo real
- Cada zona puede correr como microservicio
- Comunicación distribuida mediante colas RabbitMQ
- Cámara desplazable, FPS visibles, panel de estadísticas

---

## 🛠️ ¿Cómo extenderlo?

1. Añadir detección de colisiones o congestión en simulator.py
2. Ampliar interacciones en gui.py (crear botones, clics, zoom)
3. Diseñar un mapa urbano completo desde city.py
4. Escalar a múltiples zonas conectadas (más microservicios)
5. Agregar pruebas de estrés y métrica de rendimiento
6. Añadir IA de tráfico (decisión de dirección, prioridad, etc.)

---

## ⚡ Optimización aplicada

- Render selectivo: solo se dibuja lo visible en cámara
- asyncio + Pygame sincronizados para evitar lag
- Datos estructurados (no strings) entre módulos
- Código modular y desacoplado

---

## ✅ Estado actual

- Fase 1 completada (entidades, simulación local)
- Fase 2 completada (visualización, concurrencia, distribución)
- Fase 3 completada (optimización, documentación técnica)

---

## 📦 Autores y Créditos

Proyecto desarrollado por Arián Benítez y Gonzalo Franco 
Coordinado por fases: visualización, simulación, distribución, mensajería, rendimiento.


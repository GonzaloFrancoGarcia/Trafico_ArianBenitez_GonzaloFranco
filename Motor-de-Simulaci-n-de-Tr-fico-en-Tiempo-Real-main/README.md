# Motor de Simulación de Tráfico en Tiempo Real 

Simulador urbano modular, visual y escalable para representar el tráfico en una ciudad virtual usando Python, Pygame y programación concurrente y distribuida con RabbitMQ.

---

## 📁 Estructura del Proyecto

```bash
simulacion_trafico/
├── main.py                          # Lanzador principal: grid de semáforos 3×4 y vehículos aleatorios
├── zona_runner.py                   # Simulación autónoma de una zona (sin GUI)
├── README.md                        # Documentación del proyecto
│
├── environment/                     # Entidades urbanas
│   ├── __init__.py
│   ├── city.py                      # Contiene vehículos, semáforos, intersecciones y snapshot
│   ├── intersection.py              # Representa puntos de cruce
│   ├── traffic_light.py             # Semáforo con lógica de tiempos (ROJO, AMBAR, VERDE)
│   ├── vehicle.py                   # Vehículo con posición, dirección, velocidad y estado
│   ├── test_city_runner.py          # Pruebas de la clase City
│   └── test_intersection_runner.py  # Pruebas de Intersection y TrafficLight
│
├── simulation/                      # Lógica de simulación
│   ├── __init__.py
│   └── simulator.py                 # Motor de simulación: update(), snapshot()
│
├── concurrency/                     # Concurrencia con asyncio
│   ├── __init__.py
│   └── tasks.py                     # Creación de tasks asíncronas para simulación continua
│
├── ui/                              # Interfaz gráfica con Pygame
│   ├── __init__.py
│   └── gui.py                       # Dibujado de semáforos, carreteras y vehículos (colores únicos)
│
├── distribution/                    # Simulación distribuida y mensajería
│   ├── __init__.py
│   ├── protocolo.py                 # Estructura estándar de mensajes JSON
│   ├── rabbit_client.py             # Cliente RabbitMQ (envío y consumo asíncrono)
│   ├── send_vehicle_to_zona_distribuida.py
│   └── zona_distribuida_runner.py   # Microservicio de simulación de zona con RabbitMQ
│
└── performance/                     # Métricas y logging
    ├── __init__.py
    └── metrics.py                   # Logging de snapshots y posibles cuellos de botella
```

---

## 🚀 Cómo ejecutar la simulación

1. Instala dependencias:
   ```bash
   pip install pygame aio-pika
   ```

2. Ejecuta la simulación local completa (grid 3×4):
   ```bash
   python main.py
   ```

3. Ejecuta una zona independiente (modo distribuido):
   ```bash
   python distribution/zona_distribuida_runner.py
   ```

4. Envía un vehículo a una zona (desde otro proceso):
   ```bash
   python distribution/send_vehicle_to_zona_distribuida.py
   ```

> ⚠️ Asegúrate de tener RabbitMQ ejecutándose en localhost antes de los modos distribuidos.

---

## 🧱 Cómo funciona

- **Grid de semáforos**: 3 filas horizontales (y = 100, 250, 400) y 4 columnas verticales (x = 100, 300, 500, 700).
- **Intersecciones**: definidas en los mismos puntos que semáforos para dibujar carreteras.
- **Vehículos**: se generan en posiciones aleatorias sobre cualquiera de las carreteras horizontales o verticales.
- **Colores únicos**: cada vehículo obtiene un color RGB determinista basado en su `id`, sin afectar la simulación.
- **Semáforos**: ROJO detiene el vehículo al contactar, VERDE/AMBAR dejan avanzar.
- **Mantenimiento de carril**: tras cada tick, los vehículos se realinean al centro de su carretera evitando salirse.
- **Giros opcionales**: en cada intersección pueden girar perpendicularmente con probabilidad configurada.
- **Concurrencia**: asyncio gestiona el bucle de simulación y el GUI sin bloquear.
- **Distribución**: microservicios en distintas zonas se comunican por RabbitMQ.

---

## 🛠️ ¿Cómo extenderlo?

1. **Colisiones y congestión**: detectar y manejar proximidad entre vehículos.
2. **Controles en GUI**: agregar botones, sliders para densidad, tiempos de semáforo o zoom.
3. **Mapas personalizados**: cargar posiciones de carreteras y semáforos desde un archivo JSON/CSV.
4. **Escalabilidad**: desplegar microservicios en contenedores (Docker + Kubernetes).
5. **Análisis de rendimiento**: integrar métricas en tiempo real con Prometheus/Grafana.
6. **IA de tráfico**: implementar lógica de toma de decisiones, rutas óptimas y prioridades.

---

## ⚡ Optimización aplicada

- **Sincronización eficiente**: uso de `await asyncio.sleep(0)` y `clock.tick` para evitar stutter.
- **Render selectivo**: dibujado de carreteras y elementos en posiciones relevantes.
- **Datos estructurados**: snapshot en diccionarios en lugar de strings parseados.
- **Colores deterministas**: hashing de `id` evita collisions y simplifica paleta.

---

## ✅ Estado actual

- **Versión final**: grid 3×4 semáforos + fila intermedia, vehículos aleatorios, colores únicos.
- **Concurrencia**: bucle de simulación + GUI en paralelo.
- **Distribución**: microservicios con RabbitMQ listos para comunicación.
- **Estabilidad**: vehículos respetan carriles, semáforos y límites de carretera.

---

## 📦 Autores y Créditos

Proyecto desarrollado por Arián Benítez y Gonzalo Franco.  
Fases: modelado, visualización, concurrencia, distribución y optimización.


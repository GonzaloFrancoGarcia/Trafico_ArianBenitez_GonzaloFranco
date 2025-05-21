# Motor de Simulación de Tráfico en Tiempo Real

Simulador urbano modular, visual y escalable para representar el tráfico en una ciudad virtual usando Python, Pygame y programación concurrente y distribuida con RabbitMQ.

---

## 📁 Estructura del Proyecto

```bash
simulacion_trafico/
├── main.py                          # Lanzador principal: grid de semáforos 3×4 y vehículos aleatorios
├── zona_runner.py                   # Simulación autónoma de una zona (sin GUI)
├── README.md                        # Documentación actualizada
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
│   └── simulator.py                 # Motor de simulación: update(), snapshot() con semáforos desfasados
│
├── concurrency/                     # Concurrencia con asyncio
│   ├── __init__.py
│   └── tasks.py                     # Creación de corutinas asíncronas para simulación continua
│
├── ui/                              # Interfaz gráfica con Pygame y Dashboard web
│   ├── __init__.py
│   ├── gui.py                       # Dibujado de semáforos, carreteras y vehículos (colores únicos)
│   └── dashboard.py                 # Dashboard FastAPI con Chart.js
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
   pip install pygame aio-pika httpx uvicorn fastapi jinja2
   ```

2. Ejecuta la simulación local completa (grid 3×4 semáforos):

   ```bash
   python main.py
   ```

   * La cuadrícula de semáforos está en tres filas horizontalmente (y = 100, 300, 500)
     y cuatro columnas verticalmente (x = 100, 300, 500, 700).
   * Los semáforos comienzan alternando estados iniciales (algunos en ROJO, otros en VERDE).
   * Ciclo de semáforo: GREEN 3s → YELLOW 1s → RED 3s.

3. Ejecuta una zona independiente (modo distribuido):

   ```bash
   python -m distribution.zona_distribuida_runner
   ```

4. Envía un vehículo a una zona (desde otro proceso):

   ```bash
   python -m distribution.send_vehicle_to_zona_distribuida
   ```

> ⚠️ Asegúrate de tener RabbitMQ ejecutándose en localhost antes de usar los modos distribuidos.

---

## 🧱 Cómo funciona

* **Grid de semáforos**: 3 filas (y=100, 300, 500) × 4 columnas (x=100, 300, 500, 700).
* **Estados iniciales alternos**: al iniciar, cada semáforo arranca en ROJO o VERDE según su índice.
* **Ciclo de semáforo**: 3 s VERDE → 1 s AMARILLO → 3 s ROJO.
* **Desfase escalonado**: semáforos cambian en orden de arriba a abajo y de izquierda a derecha,
  con un offset de 10 frames (\~0.17 s) entre cada uno.
* **Vehículos**: generados aleatoriamente sobre cualquier carretera horizontal o vertical.
* **Colores únicos**: cada vehículo recibe un color RGB derivado de su `id`.
* **Lógica de movimiento**: los vehículos se detienen al contactar semáforos ROJOS,
  se realinean al carril, rebotan en los extremos y pueden girar en intersecciones.
* **Generación dinámica**: nuevos vehículos aparecen desde los bordes hasta un límite configurable.
* **Distribución**: microservicios de zonas comunican vehículos vía RabbitMQ.

---

## 🛠️ Extensiones posibles

1. **Detección de colisiones**: prevenir choques entre vehículos.
2. **Controles en GUI**: sliders para ajustar densidad de tráfico o tiempos de semáforo dinámicamente.
3. **Mapas personalizados**: cargar carreteras y semáforos desde archivos de configuración.
4. **Escalado**: desplegar microservicios en contenedores Docker + Kubernetes.
5. **Métricas**: integrar Prometheus y Grafana para monitorizar rendimiento.
6. **IA de tráfico**: rutas óptimas, prioridades y lógica avanzada de conducción.

---

## ✅ Estado actual

* **Versión final**: grid 3×4 con desfase, semáforos alternando, ciclo 3-1-3, vehículos fluidos.
* **Concurrencia**: simulación y GUI en paralelo sin bloqueos.
* **Distribución**: microservicios RabbitMQ listos.
* **Monitorización**: Dashboard web y posibilidad de integrar Prometheus/Grafana.
* **Generación dinámica**: hasta 20 vehículos generados automáticamente.

---

## 📦 Autores y Créditos

Proyecto desarrollado por Arián Benítez y Gonzalo Franco.

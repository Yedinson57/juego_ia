# Top-Down Racing

Juego de carreras 2D de vista aérea desarrollado con Python y Pygame. Incluye selección de vehículos y circuitos, bots controlados por IA y carreras por vueltas.

## Requisitos

- Python 3.10 o posterior
- pip

## Instalación

Desde la raíz del proyecto, instala las dependencias:

```bash
python -m pip install -r requirements.txt
```

Si todavía no existe `requirements.txt`, añade `pygame`:

```text
pygame
```

## Ejecutar

Desde la carpeta del proyecto:

```bash
python main.py
```

## Controles

| Acción | Teclas |
|---|---|
| Navegar por menús y selecciones | Flechas |
| Confirmar una opción | Enter |
| Acelerar | W o Flecha Arriba |
| Frenar | S o Flecha Abajo |
| Girar a la izquierda | A o Flecha Izquierda |
| Girar a la derecha | D o Flecha Derecha |

Al terminar la carrera, pulsa **Enter** para volver al menú principal.

## Características

- **Menús y selección:** menú principal, selección de vehículo y selección de circuito.
- **Bots con IA:** siguen los waypoints de la pista y giran gradualmente hacia el siguiente objetivo.
- **Físicas de velocidad:** aceleración, frenado, marcha atrás, giro y fricción.
- **Superficies:** salirse del asfalto reduce temporalmente la velocidad máxima del vehículo.
- **Carreras por vueltas:** checkpoints ordenados, clasificación y pantalla de resultados.
- **HUD:** muestra la vuelta, posición y velocidad del jugador.

## Estructura del proyecto

```text
src/
├── core/          # Gestión de escenas
├── entities/      # Vehículos, jugador y bots
├── scenes/        # Menús, selecciones y carrera
├── systems/       # IA de bots y progreso de carrera
├── tracks/        # Pistas y carga de circuitos
└── ui/            # HUD
data/
├── vehicles.json  # Configuración de vehículos
└── maps.json      # Configuración de circuitos
assets/            # Imágenes, audio y fuentes
```

## Configuración de vehículos y mapas

Los datos se leen desde `data/vehicles.json` y `data/maps.json`. Los vehículos pueden definir, entre otros, `name`, `max_speed`, `acceleration` y `color_rgb`.

Los circuitos pueden incluir `name`, `laps` y una lista de `waypoints` en coordenadas de pantalla, por ejemplo:

```json
{
  "name": "Circuito de prueba",
  "laps": 3,
  "waypoints": [[640, 150], [900, 300], [640, 550], [380, 300]]
}
```

El orden de los waypoints determina el recorrido. Si un circuito necesita invertir el orden, puede configurarse con `"reverse_waypoints": true`.

## Solución de problemas

- Si falta una dependencia, vuelve a ejecutar `python -m pip install -r requirements.txt`.
- Ejecuta los comandos desde `c:\car_racing` para que Python encuentre `main.py` y los archivos de datos.
- Comprueba que los JSON sean válidos y contengan las claves esperadas si no aparecen vehículos o circuitos.
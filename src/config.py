from pathlib import Path

# Resolución y rendimiento
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

# Título de la ventana
GAME_TITLE = "Top-Down Racing"

# Colores RGB
NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
GRIS = (128, 128, 128)
ROJO = (255, 0, 0)
VERDE = (0, 255, 0)
AZUL = (0, 0, 255)
AMARILLO = (255, 255, 0)

# Rutas a recursos, relativas a la raíz del proyecto
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
ASSETS_DIR = PROJECT_ROOT / "assets"
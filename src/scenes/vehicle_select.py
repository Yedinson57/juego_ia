import json

import pygame

from pathlib import Path

from src import config
from src.core.asset_manager import AssetManager
from src.core.scene_manager import Scene


class VehicleSelectScene(Scene):
    def __init__(self, scene_manager):
        self.scene_manager = scene_manager
        self.vehicles = self._load_vehicles()
        self.selected_index = 0
        self.selected_vehicle = None

        self.title_font = pygame.font.Font(None, 48)
        self.name_font = pygame.font.Font(None, 40)
        self.text_font = pygame.font.Font(None, 28)

        self.asset_manager = AssetManager()
        self.preview_size = (220, 120)

    def _load_vehicles(self):
        vehicles_path = config.DATA_DIR / "vehicles.json"

        try:
            with vehicles_path.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except (OSError, json.JSONDecodeError) as error:
            raise RuntimeError(f"No se pudo cargar {vehicles_path}: {error}") from error

        vehicles = data.get("vehicles", [])
        if not vehicles:
            raise ValueError(f"No hay vehículos definidos en {vehicles_path}")

        return vehicles

    def handle_events(self, events):
        for event in events:
            if event.type != pygame.KEYDOWN:
                continue

            if event.key == pygame.K_LEFT:
                self.selected_index = (self.selected_index - 1) % len(self.vehicles)
            elif event.key == pygame.K_RIGHT:
                self.selected_index = (self.selected_index + 1) % len(self.vehicles)
            elif event.key == pygame.K_RETURN:
                self.selected_vehicle = self.vehicles[self.selected_index]
                from src.scenes.map_select import MapSelectScene

                self.scene_manager.change_scene(
                    MapSelectScene(self.scene_manager, self.selected_vehicle)
                )

    def update(self, dt):
        pass

    def draw(self, surface):
        surface.fill(config.NEGRO)
        vehicle = self.vehicles[self.selected_index]

        self._draw_centered(
            surface,
            "SELECCIONA TU VEHÍCULO",
            self.title_font,
            config.BLANCO,
            75,
        )
        self._draw_centered(
            surface,
            vehicle.get("name", "Vehículo sin nombre"),
            self.name_font,
            config.AMARILLO,
            155,
        )

        color = vehicle.get("color_rgb", [128, 128, 128])
        if not isinstance(color, (list, tuple)) or len(color) != 3:
            color = [128, 128, 128]
        color = tuple(max(0, min(255, int(channel))) for channel in color)

        car_rect = pygame.Rect(0, 0, 120, 60)
        car_rect.center = (surface.get_width() // 2, 245)
        pygame.draw.rect(surface, color, car_rect, border_radius=10)

        stats = (
            ("Velocidad Máxima", "max_speed"),
            ("Aceleración", "acceleration"),
            ("Manejo", "handling"),
        )
        bar_x = surface.get_width() // 2 - 180
        bar_width = 360

        for index, (label, key) in enumerate(stats):
            y = 330 + index * 75
            value = float(vehicle.get(key, 0))
            maximum = max(
                (float(item.get(key, 0)) for item in self.vehicles),
                default=0,
            )
            ratio = max(0.0, min(1.0, value / maximum)) if maximum > 0 else 0.0

            text = self.text_font.render(f"{label}: {value:g}", True, config.BLANCO)
            surface.blit(text, (bar_x, y))

            pygame.draw.rect(
                surface, config.GRIS, (bar_x, y + 32, bar_width, 14)
            )
            pygame.draw.rect(
                surface,
                config.VERDE,
                (bar_x, y + 32, int(bar_width * ratio), 14),
            )

        hint = self.text_font.render(
            "← / →: elegir     Enter: confirmar", True, config.BLANCO
        )
        surface.blit(hint, hint.get_rect(center=(surface.get_width() // 2, 630)))

        self._draw_vehicle_preview(surface, vehicle)

    @staticmethod
    def _draw_centered(surface, text, font, color, y):
        rendered = font.render(text, True, color)
        surface.blit(
            rendered,
            rendered.get_rect(center=(surface.get_width() // 2, y)),
        )

    def _draw_vehicle_preview(self, surface, vehicle):
        filename = vehicle.get("image_file") or vehicle.get("sprite_filename")
        if filename:
            path = config.ASSETS_DIR / "images" / "cars" / Path(filename).name
            try:
                image = self.asset_manager.get_image(path, size=self.preview_size)
                surface.blit(image, image.get_rect(
                    center=(surface.get_width() // 2, 260)
                ))
                return
            except (OSError, pygame.error) as error:
                print(f"No se pudo cargar la vista previa {path}: {error}")

        fallback = pygame.Rect(0, 0, *self.preview_size)
        fallback.center = (surface.get_width() // 2, 260)
        pygame.draw.rect(
            surface,
            tuple(vehicle.get("color_rgb", config.GRIS)),
            fallback,
            border_radius=10,
        )
import json
import math

import pygame

from src import config
from src.core.scene_manager import Scene


class MapSelectScene(Scene):
    def __init__(self, scene_manager, selected_vehicle):
        self.scene_manager = scene_manager
        self.selected_vehicle = selected_vehicle
        self.maps = self._load_maps()
        self.selected_index = 0

        self.title_font = pygame.font.Font(None, 48)
        self.name_font = pygame.font.Font(None, 40)
        self.option_font = pygame.font.Font(None, 32)
        self.text_font = pygame.font.Font(None, 28)

    def _load_maps(self):
        maps_path = config.DATA_DIR / "maps.json"
        try:
            with maps_path.open("r", encoding="utf-8") as file:
                maps = json.load(file).get("maps", [])
        except (OSError, json.JSONDecodeError) as error:
            raise RuntimeError(f"No se pudieron cargar los mapas: {error}") from error

        if not maps:
            raise ValueError(f"No hay circuitos definidos en {maps_path}")
        return maps

    def handle_events(self, events):
        for event in events:
            if event.type != pygame.KEYDOWN:
                continue

            if event.key == pygame.K_LEFT:
                self.selected_index = (self.selected_index - 1) % len(self.maps)
            elif event.key == pygame.K_RIGHT:
                self.selected_index = (self.selected_index + 1) % len(self.maps)
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                from src.scenes.race_scene import RaceScene

                selected_map = self.maps[self.selected_index]
                self.scene_manager.change_scene(
                    RaceScene(
                        self.scene_manager,
                        self.selected_vehicle,
                        selected_map,
                    )
                )

    def update(self, dt):
        pass

    def draw(self, surface):
        surface.fill(config.NEGRO)
        selected_map = self.maps[self.selected_index]
        center_x = surface.get_width() // 2

        self._draw_centered(
            surface, "SELECCIONA UN CIRCUITO", self.title_font,
            config.BLANCO, 55
        )
        self._draw_centered(
            surface, selected_map.get("name", "Circuito"),
            self.name_font, config.AMARILLO, 110
        )

        laps = selected_map.get("laps", 3)
        description = selected_map.get("description", "Sin descripción.")
        self._draw_centered(
            surface, f"Vueltas: {laps}", self.text_font, config.BLANCO, 145
        )
        self._draw_centered(
            surface, description, self.text_font, config.BLANCO, 180
        )

        preview = pygame.Rect(0, 0, 520, 330)
        preview.center = (center_x, 390)
        pygame.draw.rect(surface, (35, 75, 40), preview)
        pygame.draw.rect(surface, config.BLANCO, preview, width=2)
        self._draw_track_preview(surface, preview, selected_map.get("waypoints"))

        self._draw_centered(
            surface,
            "← / →: elegir     Enter: iniciar carrera",
            self.option_font,
            config.BLANCO,
            610,
        )

    def _draw_track_preview(self, surface, preview_rect, raw_waypoints):
        if raw_waypoints:
            points = [self._to_point(point) for point in raw_waypoints]
        else:
            cx, cy = 0.0, 0.0
            points = [
                (cx + 2 * math.cos(2 * math.pi * i / 12),
                 cy + math.sin(2 * math.pi * i / 12))
                for i in range(12)
            ]

        if len(points) < 2:
            return

        min_x = min(point[0] for point in points)
        max_x = max(point[0] for point in points)
        min_y = min(point[1] for point in points)
        max_y = max(point[1] for point in points)

        source_width = max(max_x - min_x, 1)
        source_height = max(max_y - min_y, 1)
        padding = 45
        scale = min(
            (preview_rect.width - 2 * padding) / source_width,
            (preview_rect.height - 2 * padding) / source_height,
        )

        scaled_points = [
            (
                round(preview_rect.centerx + (x - (min_x + max_x) / 2) * scale),
                round(preview_rect.centery + (y - (min_y + max_y) / 2) * scale),
            )
            for x, y in points
        ]

        pygame.draw.lines(
            surface, (190, 190, 190), True, scaled_points, 24
        )
        pygame.draw.lines(
            surface, (50, 50, 50), True, scaled_points, 18
        )
        pygame.draw.circle(
            surface, config.AMARILLO, scaled_points[0], 7
        )

    @staticmethod
    def _to_point(point):
        if isinstance(point, dict):
            return float(point["x"]), float(point["y"])
        return float(point[0]), float(point[1])

    @staticmethod
    def _draw_centered(surface, text, font, color, y):
        rendered = font.render(str(text), True, color)
        surface.blit(
            rendered,
            rendered.get_rect(center=(surface.get_width() // 2, y)),
        )
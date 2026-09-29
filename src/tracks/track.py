import math

import pygame

from src import config


class Track:
    ROAD_WIDTH = 70
    CHECKPOINT_RADIUS = 100.0
    ASPHALT_COLOR = (65, 65, 65)
    EDGE_COLORS = ((235, 55, 45), (245, 245, 245))

    TERRAIN_COLORS = {
        "green_circuit": (34, 139, 34),
        "desert_loop": (194, 153, 91),
        "city_night": (38, 42, 48),
    }

    def __init__(self, map_data, road_width=ROAD_WIDTH):
        self.name = map_data.get("name", "Circuito")
        self.map_id = map_data.get("id", "")
        self.laps = int(map_data.get("laps", 3))
        self.road_width = int(road_width)
        self.checkpoint_radius = self.CHECKPOINT_RADIUS
        self.terrain_color = self.TERRAIN_COLORS.get(
            self.map_id,
            (34, 139, 34),
        )

        raw_waypoints = map_data.get("waypoints")
        if raw_waypoints:
            self.waypoints = [self._to_vector(point) for point in raw_waypoints]
        else:
            center_x = config.SCREEN_WIDTH / 2
            center_y = config.SCREEN_HEIGHT / 2
            radius_x = config.SCREEN_WIDTH * 0.32
            radius_y = config.SCREEN_HEIGHT * 0.30
            self.waypoints = [
                pygame.Vector2(
                    center_x + radius_x * math.cos(2 * math.pi * i / 12),
                    center_y + radius_y * math.sin(2 * math.pi * i / 12),
                )
                for i in range(12)
            ]

        if map_data.get("reverse_waypoints", False) and len(self.waypoints) > 1:
            self.waypoints = [
                self.waypoints[0],
                *reversed(self.waypoints[1:]),
            ]

        if len(self.waypoints) < 3:
            raise ValueError("La pista necesita al menos tres waypoints.")

        finish_line = map_data.get("finish_line")
        if finish_line:
            self.finish_start = self._to_vector(finish_line["start"])
            self.finish_end = self._to_vector(finish_line["end"])
        else:
            self.finish_start = None
            self.finish_end = None

    @staticmethod
    def _to_vector(point):
        if isinstance(point, dict):
            return pygame.Vector2(point["x"], point["y"])
        return pygame.Vector2(point)

    def draw(self, surface):
        surface.fill(self.terrain_color)

        points = [(round(point.x), round(point.y)) for point in self.waypoints]

        # Bordes exteriores sutiles y superficie de asfalto.
        pygame.draw.lines(
            surface,
            (225, 225, 225),
            True,
            points,
            self.road_width + 12,
        )
        pygame.draw.lines(
            surface,
            self.ASPHALT_COLOR,
            True,
            points,
            self.road_width,
        )

        # Pianos discontinuos rojos y blancos junto a ambos bordes.
        self._draw_curb_segments(surface)

        # La meta se dibuja encima de la pista para que destaque claramente.
        self._draw_finish_line(surface)

    def _draw_curb_segments(self, surface):
        half_width = self.road_width / 2 - 3
        dash_length = 24
        dash_index = 0

        for index, start in enumerate(self.waypoints):
            end = self.waypoints[(index + 1) % len(self.waypoints)]
            segment = end - start
            length = segment.length()

            if length == 0:
                continue

            direction = segment / length
            normal = pygame.Vector2(-direction.y, direction.x)
            dash_count = max(1, math.ceil(length / dash_length))

            for side in (-1, 1):
                offset = normal * half_width * side

                for dash in range(dash_count):
                    t0 = dash / dash_count
                    t1 = min(1.0, (dash + 1) / dash_count)
                    color = self.EDGE_COLORS[dash_index % 2]

                    p0 = start + segment * t0 + offset
                    p1 = start + segment * t1 + offset
                    pygame.draw.line(
                        surface,
                        color,
                        (round(p0.x), round(p0.y)),
                        (round(p1.x), round(p1.y)),
                        6,
                    )
                    dash_index += 1

    def _draw_finish_line(self, surface):
        if self.finish_start is None or self.finish_end is None:
            start = self.waypoints[0]
            direction = self.waypoints[1] - start
            if direction.length_squared() == 0:
                return

            normal = pygame.Vector2(-direction.y, direction.x).normalize()
            self.finish_start = start - normal * (self.road_width / 2)
            self.finish_end = start + normal * (self.road_width / 2)

        across = self.finish_end - self.finish_start
        if across.length_squared() == 0:
            return

        across_length = across.length()
        across_direction = across.normalize()
        normal = pygame.Vector2(-across_direction.y, across_direction.x)
        stripe_depth = 12
        tile_count = 8

        for index in range(tile_count):
            t0 = index / tile_count
            t1 = (index + 1) / tile_count
            edge0 = self.finish_start + across * t0
            edge1 = self.finish_start + across * t1
            offset = normal * (stripe_depth / 2)

            tile = [
                edge0 - offset,
                edge1 - offset,
                edge1 + offset,
                edge0 + offset,
            ]
            color = config.BLANCO if index % 2 == 0 else config.NEGRO
            pygame.draw.polygon(
                surface,
                color,
                [(round(point.x), round(point.y)) for point in tile],
            )

    def is_on_track(self, pos):
        point = pygame.Vector2(pos)
        max_distance_squared = (self.road_width / 2) ** 2

        for index, start in enumerate(self.waypoints):
            end = self.waypoints[(index + 1) % len(self.waypoints)]
            segment = end - start
            length_squared = segment.length_squared()

            if length_squared == 0:
                closest = start
            else:
                t = max(
                    0.0,
                    min(1.0, (point - start).dot(segment) / length_squared),
                )
                closest = start + segment * t

            if point.distance_squared_to(closest) <= max_distance_squared:
                return True

        return False
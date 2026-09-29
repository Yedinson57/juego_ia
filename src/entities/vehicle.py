import math
from pathlib import Path

import pygame

from src import config
from src.core.asset_manager import AssetManager


class Vehicle(pygame.sprite.Sprite):
    PIXELS_PER_METER = 20.0

    def __init__(
        self,
        pos,
        max_speed=320.0,
        acceleration=220.0,
        turn_speed=180.0,
        friction=0.98,
        color=(220, 40, 40),
        size=(44, 24),
        data=None,
        image_file=None,
        asset_manager=None,
    ):
        super().__init__()
        data = data or {}

        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2()
        self.angle = 0.0
        self.speed = 0.0
        self.max_speed = float(max_speed)
        self.base_max_speed = self.max_speed
        self.acceleration = float(acceleration)
        self.turn_speed = float(turn_speed)
        self.friction = float(friction)
        self.color = color
        self.asset_manager = asset_manager or AssetManager()

        filename = image_file or data.get("image_file") or data.get("sprite_filename")
        self.original_image = self._load_image(filename, size)
        self.image = self.original_image
        self.rect = self.image.get_rect(center=self.pos)

    def _load_image(self, filename, size):
        if filename:
            path = config.ASSETS_DIR / "images" / "cars" / Path(filename).name
            try:
                return self.asset_manager.get_image(path, size=size)
            except (OSError, pygame.error) as error:
                print(f"No se pudo cargar la imagen del vehículo {path}: {error}")

        fallback = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.rect(fallback, self.color, fallback.get_rect(), border_radius=5)
        return fallback

    @property
    def speed_kmh(self):
        """Velocidad convertida desde píxeles por segundo a km/h."""
        return abs(self.speed) / self.PIXELS_PER_METER * 3.6

    def accelerate(self, dt=1 / 60):
        self.speed = min(self.max_speed, self.speed + self.acceleration * dt)

    def brake(self, dt=1 / 60):
        amount = self.acceleration * dt
        if self.speed > 0:
            self.speed = max(0.0, self.speed - amount)
        elif self.speed < 0:
            self.speed = min(0.0, self.speed + amount)

    def reverse(self, dt=1 / 60):
        reverse_limit = self.max_speed * 0.35
        self.speed = max(-reverse_limit, self.speed - self.acceleration * dt)

    def turn(self, direction, dt=1 / 60):
        if self.speed != 0:
            self.angle = (self.angle + direction * self.turn_speed * dt) % 360

    def update(self, dt):
        self.speed *= self.friction ** (dt * 60)

        radians = math.radians(self.angle)
        direction = pygame.Vector2(math.cos(radians), math.sin(radians))
        self.vel = direction * self.speed
        self.pos += self.vel * dt
        self.rect.center = self.pos

    def draw(self, surface):
        rotated_image = pygame.transform.rotate(self.original_image, -self.angle)
        new_rect = rotated_image.get_rect(center=self.pos)
        self.image = rotated_image
        self.rect = new_rect
        surface.blit(rotated_image, new_rect.topleft)
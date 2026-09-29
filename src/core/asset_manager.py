from pathlib import Path

import pygame


class AssetManager:
    def __init__(self):
        self.images = {}

    def get_image(self, file_path, size=None):
        """Carga y cachea una imagen, opcionalmente escalada."""
        path = str(Path(file_path).resolve())
        normalized_size = tuple(size) if size is not None else None
        cache_key = (path, normalized_size)

        if cache_key not in self.images:
            image = pygame.image.load(path).convert_alpha()
            if normalized_size is not None:
                image = pygame.transform.scale(image, normalized_size)
            self.images[cache_key] = image

        return self.images[cache_key]
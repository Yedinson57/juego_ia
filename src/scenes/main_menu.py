import sys

import pygame

from src import config
from src.core.scene_manager import Scene
from src.scenes.vehicle_select import VehicleSelectScene


class MainMenuScene(Scene):
    def __init__(self, scene_manager):
        self.scene_manager = scene_manager
        self.options = ("JUGAR", "SALIR")
        self.selected_index = 0
        self.title_font = pygame.font.Font(None, 72)
        self.option_font = pygame.font.Font(None, 44)

    def handle_events(self, events):
        for event in events:
            if event.type != pygame.KEYDOWN:
                continue

            if event.key == pygame.K_UP:
                self.selected_index = (self.selected_index - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.selected_index = (self.selected_index + 1) % len(self.options)
            elif event.key == pygame.K_RETURN:
                if self.options[self.selected_index] == "SALIR":
                    pygame.quit()
                    sys.exit()
                else:
                    self.scene_manager.change_scene(
                        VehicleSelectScene(self.scene_manager)
                    )

    def update(self, dt):
        pass

    def draw(self, surface):
        surface.fill(config.NEGRO)
        center_x = surface.get_width() // 2
        title_y = surface.get_height() // 3

        title = self.title_font.render(config.GAME_TITLE, True, config.BLANCO)
        surface.blit(title, title.get_rect(center=(center_x, title_y)))

        for index, option in enumerate(self.options):
            color = config.AMARILLO if index == self.selected_index else config.BLANCO
            text = self.option_font.render(option, True, color)
            position = (center_x, title_y + 100 + index * 60)
            surface.blit(text, text.get_rect(center=position))
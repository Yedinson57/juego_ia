import pygame

from src import config
from src.core.scene_manager import SceneManager
from src.scenes.main_menu import MainMenuScene


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(
            (config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
        )
        pygame.display.set_caption(config.GAME_TITLE)
        self.clock = pygame.time.Clock()
        self.running = False

        self.scene_manager = SceneManager()
        self.scene_manager.change_scene(MainMenuScene(self.scene_manager))

    def run(self):
        self.running = True
        try:
            while self.running:
                dt = self.clock.tick(config.FPS) / 1000.0
                self.handle_events()

                if self.running:
                    self.update(dt)
                    self.draw()
        finally:
            pygame.quit()

    def handle_events(self):
        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                self.running = False

        self.scene_manager.handle_events(events)

    def update(self, dt):
        self.scene_manager.update(dt)

    def draw(self):
        self.screen.fill(config.NEGRO)
        self.scene_manager.draw(self.screen)
        pygame.display.flip()
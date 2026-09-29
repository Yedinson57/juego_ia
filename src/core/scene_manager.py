from abc import ABC, abstractmethod


class Scene(ABC):
    @abstractmethod
    def handle_events(self, events):
        pass

    @abstractmethod
    def update(self, dt):
        pass

    @abstractmethod
    def draw(self, surface):
        pass


class SceneManager:
    def __init__(self, initial_scene=None):
        self.current_scene = initial_scene

    def change_scene(self, new_scene):
        if not isinstance(new_scene, Scene):
            raise TypeError("new_scene debe ser una instancia de Scene")
        self.current_scene = new_scene

    def handle_events(self, events):
        if self.current_scene is not None:
            self.current_scene.handle_events(events)

    def update(self, dt):
        if self.current_scene is not None:
            self.current_scene.update(dt)

    def draw(self, surface):
        if self.current_scene is not None:
            self.current_scene.draw(surface)
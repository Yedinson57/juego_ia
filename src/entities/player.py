import pygame

from src.entities.vehicle import Vehicle


class Player(Vehicle):
    def handle_input(self, dt=1 / 60):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.accelerate(dt)

        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.brake(dt)

        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.turn(-1, dt)

        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.turn(1, dt)
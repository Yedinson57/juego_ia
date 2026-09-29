import math

import pygame


class BotController:
    def __init__(self, bot, waypoints):
        self.bot = bot
        self.waypoints = [pygame.Vector2(point) for point in waypoints]
        self.current_waypoint_index = 0

    def update(self, dt):
        if not self.waypoints:
            return

        target = self.waypoints[self.current_waypoint_index]
        offset = target - self.bot.pos

        if offset.length_squared() > 0:
            target_angle = math.degrees(math.atan2(offset.y, offset.x)) % 360
            difference = (target_angle - self.bot.angle + 180) % 360 - 180
            max_rotation = self.bot.turn_speed * dt
            rotation = max(-max_rotation, min(max_rotation, difference))
            self.bot.angle = (self.bot.angle + rotation) % 360

        self.bot.accelerate(dt)

        if offset.length() < 60:
            self.current_waypoint_index = (
                self.current_waypoint_index + 1
            ) % len(self.waypoints)
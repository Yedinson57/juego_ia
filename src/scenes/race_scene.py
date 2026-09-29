import math

import pygame

import json

from src import config
from src.core.asset_manager import AssetManager
from src.core.scene_manager import Scene
from src.entities.bot import BotVehicle
from src.entities.player import Player
from src.scenes.main_menu import MainMenuScene
from src.systems.bot_controller import BotController
from src.systems.race_manager import RaceManager
from src.tracks.track import Track
from src.ui.hud import HUD


class RaceScene(Scene):
    def __init__(self, scene_manager, selected_vehicle_data, selected_map_data):
        self.scene_manager = scene_manager
        self.vehicle_name = selected_vehicle_data.get("name", "Vehículo")
        self.track = Track(selected_map_data)

        waypoints = self.track.waypoints
        start = waypoints[0]
        direction = waypoints[1] - start
        self.start_angle = math.degrees(math.atan2(direction.y, direction.x))
        across_track = pygame.Vector2(-direction.y, direction.x).normalize()

        self.asset_manager = AssetManager()

        player_stats = self._vehicle_kwargs(selected_vehicle_data)
        self.player = Player(
            pos=start,
            data=selected_vehicle_data,
            asset_manager=self.asset_manager,
            **player_stats,
        )
        self.player.angle = self.start_angle
        self.player.name = selected_vehicle_data.get("name", "Jugador")

        bot_vehicle_data = self._load_bot_vehicle_data(selected_vehicle_data)
        self.bots = []
        self.bot_controllers = []

        bot_colors = (config.AZUL, config.AMARILLO)
        for index, vehicle_data in enumerate(bot_vehicle_data):
            bot = BotVehicle(
                pos=start + across_track * ((index + 1) * 32),
                data=vehicle_data,
                asset_manager=self.asset_manager,
                **self._vehicle_kwargs(vehicle_data, bot_colors[index]),
            )
            bot.angle = self.start_angle
            bot.name = vehicle_data.get("name", f"Bot {index + 1}")
            self.bots.append(bot)
            self.bot_controllers.append(
                BotController(bot, self.track.waypoints)
            )

        self.vehicles = [self.player, *self.bots]
        self.base_max_speeds = {
            vehicle: vehicle.max_speed for vehicle in self.vehicles
        }

        self.race_manager = RaceManager(
            self.track,
            self.vehicles,
            self.track.laps,
        )
        self.hud = HUD()
        self.race_finished = False
        self.winner_name = "—"
        self.player_position = len(self.vehicles)

    def handle_events(self, events):
        if not self.race_finished:
            return

        for event in events:
            if event.type == pygame.KEYDOWN and event.key in (
                pygame.K_RETURN,
                pygame.K_KP_ENTER,
            ):
                self.scene_manager.change_scene(MainMenuScene(self.scene_manager))
                return

    def update(self, dt):
        if self.race_finished:
            return

        self.player.handle_input(dt)

        for vehicle in self.vehicles:
            base_speed = self.base_max_speeds[vehicle]
            on_track = self.track.is_on_track(vehicle.pos)
            vehicle.max_speed = base_speed if on_track else base_speed * 0.4
            vehicle.speed = max(
                -vehicle.max_speed,
                min(vehicle.speed, vehicle.max_speed),
            )

        for controller in self.bot_controllers:
            controller.update(dt)

        for vehicle in self.vehicles:
            vehicle.update(dt)

        standings = self.race_manager.update(dt)
        player_standing = next(
            entry for entry in standings if entry["vehicle"] is self.player
        )
        self.player_position = player_standing["position"]

        bots_finished = all(
            entry["is_finished"]
            for entry in standings
            if entry["vehicle"] in self.bots
        )
        self.race_finished = (
            player_standing["is_finished"]
            or (bool(self.bots) and bots_finished)
        )

        if self.race_finished:
            finish_order = self.race_manager.finish_order
            if finish_order:
                self.winner_name = getattr(finish_order[0], "name", "Desconocido")

    def draw(self, surface):
        self.track.draw(surface)

        for bot in self.bots:
            bot.draw(surface)
        self.player.draw(surface)

        self.hud.draw_race_info(surface, self.player, self.race_manager)
        if self.race_finished:
            self.hud.draw_game_over(
                surface,
                self.winner_name,
                self.player_position,
            )


    @staticmethod
    def _vehicle_kwargs(vehicle_data, fallback_color=None):
        return {
            "max_speed": float(vehicle_data.get("max_speed", 320)),
            "acceleration": float(vehicle_data.get("acceleration", 220)),
            "turn_speed": float(vehicle_data.get("turn_speed", 180)),
            "friction": float(vehicle_data.get("friction", 0.98)),
            "color": tuple(
                vehicle_data.get("color_rgb")
                or fallback_color
                or config.ROJO
            ),
        }

    @staticmethod
    def _load_bot_vehicle_data(selected_vehicle_data):
        vehicles_path = config.DATA_DIR / "vehicles.json"
        try:
            with vehicles_path.open("r", encoding="utf-8") as file:
                all_vehicles = json.load(file).get("vehicles", [])
        except (OSError, json.JSONDecodeError) as error:
            raise RuntimeError(
                f"No se pudieron cargar los vehículos desde {vehicles_path}: {error}"
            ) from error

        selected_id = selected_vehicle_data.get("id")
        selected_name = selected_vehicle_data.get("name")

        alternatives = [
            vehicle
            for vehicle in all_vehicles
            if vehicle.get("id") != selected_id
            and vehicle.get("name") != selected_name
            and vehicle != selected_vehicle_data
        ]

        if len(alternatives) < 2:
            raise ValueError(
                "Se necesitan al menos tres vehículos distintos en vehicles.json."
            )

        return alternatives[:2]
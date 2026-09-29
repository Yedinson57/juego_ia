import pygame

from src import config


class HUD:
    def __init__(self):
        self.info_font = pygame.font.Font(None, 30)
        self.result_font = pygame.font.Font(None, 48)
        self.detail_font = pygame.font.Font(None, 34)

    def draw_race_info(self, surface, player, race_manager):
        standings = race_manager.get_standings()
        player_standing = next(
            (entry for entry in standings if entry["vehicle"] is player),
            None,
        )
        if player_standing is None:
            return

        lap = min(player_standing["current_lap"], race_manager.total_laps)
        position = player_standing["position"]
        speed_kmh = abs(player.speed) * 3.6

        raw_max_kmh = (
            player.base_max_speed / player.PIXELS_PER_METER
        ) * 3.6

        # Calibra la velocidad máxima mostrada según las estadísticas del coche.
        stat_ratio = max(
            0.0,
            min(1.0, (player.base_max_speed - 250.0) / (320.0 - 250.0)),
        )
        displayed_max_kmh = 120.0 + stat_ratio * 100.0
        scale = displayed_max_kmh / raw_max_kmh if raw_max_kmh > 0 else 1.0
        speed_kmh = min(player.speed_kmh * scale, displayed_max_kmh)

        lines = (
            f"VUELTA: {lap} / {race_manager.total_laps}",
            f"POSICIÓN: {position}º",
            f"VELOCIDAD: {speed_kmh:.0f} km/h",
        )

        for index, line in enumerate(lines):
            text = self.info_font.render(line, True, config.BLANCO)
            surface.blit(text, (16, 16 + index * 34))

    def draw_game_over(self, surface, winner_name, player_position):
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        panel = pygame.Rect(0, 0, 600, 280)
        panel.center = surface.get_rect().center
        pygame.draw.rect(surface, config.GRIS, panel, border_radius=12)
        pygame.draw.rect(surface, config.BLANCO, panel, width=2, border_radius=12)

        lines = (
            ("¡CARRERA FINALIZADA!", self.result_font),
            (f"Ganador: {winner_name}", self.detail_font),
            (f"Tu posición: {player_position}º", self.detail_font),
            ("Presiona ENTER para volver al Menú Principal", self.info_font),
        )

        center_x = panel.centerx
        start_y = panel.top + 40
        for index, (line, font) in enumerate(lines):
            text = font.render(line, True, config.BLANCO)
            surface.blit(
                text,
                text.get_rect(center=(center_x, start_y + index * 52)),
            )
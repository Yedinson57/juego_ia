import pygame


class RaceManager:
    CROSSING_EPSILON = 0.01

    def __init__(self, track, vehicles, total_laps):
        if total_laps < 1:
            raise ValueError("total_laps debe ser al menos 1.")
        if len(track.waypoints) < 2:
            raise ValueError("La pista necesita al menos dos waypoints.")

        self.track = track
        self.vehicles = list(vehicles)
        self.total_laps = int(total_laps)
        self.waypoints = [pygame.Vector2(point) for point in track.waypoints]
        self.checkpoint_radius = getattr(track, "checkpoint_radius", 100.0)
        self.finish_order = []

        direction = self.waypoints[1] - self.waypoints[0]
        if direction.length_squared() == 0:
            raise ValueError("Los dos primeros waypoints no pueden coincidir.")
        self._finish_direction = direction.normalize()
        self._finish_normal = pygame.Vector2(
            -self._finish_direction.y,
            self._finish_direction.x,
        )

        self._states = {
            vehicle: {
                "current_lap": 1,
                # La salida es waypoint 0; el primer objetivo está delante.
                "next_checkpoint_index": 1,
                "is_finished": False,
                "previous_pos": pygame.Vector2(vehicle.pos),
            }
            for vehicle in self.vehicles
        }

    def update(self, dt):
        for vehicle in self.vehicles:
            state = self._states[vehicle]
            current_pos = pygame.Vector2(vehicle.pos)

            if state["is_finished"]:
                state["previous_pos"] = current_pos
                continue

            previous_pos = state["previous_pos"]
            checkpoint_index = state["next_checkpoint_index"]

            if checkpoint_index == 0:
                if self._crossed_finish(previous_pos, current_pos):
                    state["current_lap"] += 1
                    print(
                        f"Vehículo {vehicle} completó la vuelta "
                        f"{state['current_lap'] - 1}"
                    )

                    state["next_checkpoint_index"] = 1
                    print(
                        f"Objetivo actual: waypoint "
                        f"{state['next_checkpoint_index']} de "
                        f"{len(self.waypoints)}"
                    )

                    if state["current_lap"] > self.total_laps:
                        state["is_finished"] = True
                        self.finish_order.append(vehicle)
            else:
                checkpoint = self.waypoints[checkpoint_index]
                if self._passed_checkpoint(
                    previous_pos, current_pos, checkpoint
                ):
                    if checkpoint_index == len(self.waypoints) - 1:
                        state["next_checkpoint_index"] = 0
                    else:
                        state["next_checkpoint_index"] += 1

                    print(
                        f"Objetivo actual: waypoint "
                        f"{state['next_checkpoint_index']} de "
                        f"{len(self.waypoints)}"
                    )

            state["previous_pos"] = current_pos

        return self.get_standings()

    def get_standings(self):
        finish_positions = {
            vehicle: index for index, vehicle in enumerate(self.finish_order)
        }

        def sort_key(vehicle):
            state = self._states[vehicle]
            if state["is_finished"]:
                return (0, finish_positions[vehicle], 0, 0)

            checkpoint_index = state["next_checkpoint_index"]
            progress = (
                len(self.waypoints)
                if checkpoint_index == 0
                else checkpoint_index - 1
            )
            distance = pygame.Vector2(vehicle.pos).distance_to(
                self.waypoints[checkpoint_index]
            )
            return (1, -state["current_lap"], -progress, distance)

        ordered = sorted(self.vehicles, key=sort_key)
        return [
            {
                "position": index + 1,
                "vehicle": vehicle,
                "current_lap": self._states[vehicle]["current_lap"],
                "next_checkpoint_index": self._states[vehicle][
                    "next_checkpoint_index"
                ],
                "is_finished": self._states[vehicle]["is_finished"],
            }
            for index, vehicle in enumerate(ordered)
        ]

    def _passed_checkpoint(self, previous_pos, current_pos, checkpoint):
        movement = current_pos - previous_pos
        length_squared = movement.length_squared()

        if length_squared == 0:
            return current_pos.distance_to(checkpoint) <= self.checkpoint_radius

        t = max(
            0.0,
            min(1.0, (checkpoint - previous_pos).dot(movement) / length_squared),
        )
        closest_point = previous_pos + movement * t
        return closest_point.distance_to(checkpoint) <= self.checkpoint_radius

    def _crossed_finish(self, previous_pos, current_pos):
        start = self.waypoints[0]
        previous_offset = previous_pos - start
        current_offset = current_pos - start

        previous_side = previous_offset.dot(self._finish_direction)
        current_side = current_offset.dot(self._finish_direction)

        # El sentido correcto va desde antes de la salida hacia el waypoint 1.
        if not (
            previous_side < -self.CROSSING_EPSILON
            and current_side >= -self.CROSSING_EPSILON
        ):
            return False

        denominator = current_side - previous_side
        if denominator == 0:
            return False

        t = -previous_side / denominator
        crossing_point = previous_pos + (current_pos - previous_pos) * t
        lateral_distance = abs(
            (crossing_point - start).dot(self._finish_normal)
        )
        return lateral_distance <= self.track.road_width / 2
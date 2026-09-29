from src.entities.vehicle import Vehicle


class BotVehicle(Vehicle):
    """Vehículo controlado por la IA."""

    def __init__(self, pos, data=None, **kwargs):
        super().__init__(pos=pos, data=data or {}, **kwargs)
        self.name = (data or {}).get("name", "Bot")
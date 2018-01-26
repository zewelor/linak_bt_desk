from desk_position import DeskPosition
from desk_speed import DeskSpeed


class HeightSpeed:
    @classmethod
    def from_bytes(cls, data):
        height = DeskPosition.from_bytes(data)
        speed = DeskSpeed.from_bytes(data)

        return cls(height, speed)

    def __init__(self, height, speed):
        self._height = height
        self._speed = speed

    @property
    def height(self):
        return self._height

    @property
    def speed(self):
        return self._speed

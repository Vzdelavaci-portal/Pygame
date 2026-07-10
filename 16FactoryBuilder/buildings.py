from dataclasses import dataclass

from settings import DIRECTION_ORDER, MINER_PRODUCTION_TIME, SMELTER_PRODUCTION_TIME


@dataclass
class Miner:
    direction: str = "right"
    timer: float = 0.0
    waiting: bool = True
    kind: str = "miner"

    def rotate(self):
        index = DIRECTION_ORDER.index(self.direction)
        self.direction = DIRECTION_ORDER[(index + 1) % len(DIRECTION_ORDER)]

    def ready(self):
        return self.timer >= MINER_PRODUCTION_TIME


@dataclass
class Belt:
    direction: str
    kind: str = "belt"


@dataclass
class Smelter:
    direction: str = "right"
    input_count: int = 0
    timer: float = 0.0
    status: str = "Waiting for ore"
    kind: str = "smelter"

    def rotate(self):
        index = DIRECTION_ORDER.index(self.direction)
        self.direction = DIRECTION_ORDER[(index + 1) % len(DIRECTION_ORDER)]

    def ready(self):
        return self.timer >= SMELTER_PRODUCTION_TIME


@dataclass
class Factory:
    delivered_total: int = 0
    kind: str = "factory"

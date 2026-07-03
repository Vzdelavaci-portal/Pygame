from dataclasses import dataclass

from settings import DIRECTION_ORDER, MINER_PRODUCTION_TIME


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
class Factory:
    delivered_total: int = 0
    kind: str = "factory"

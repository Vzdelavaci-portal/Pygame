from dataclasses import dataclass

from settings import ITEM_SPEED, TILE_SIZE, TOP_PANEL_HEIGHT


def tile_center(tile):
    x, y = tile
    return (
        x * TILE_SIZE + TILE_SIZE // 2,
        TOP_PANEL_HEIGHT + y * TILE_SIZE + TILE_SIZE // 2,
    )


@dataclass
class Item:
    tile: tuple[int, int]
    target_tile: tuple[int, int]
    x: float
    y: float
    moving: bool = True

    @classmethod
    def between(cls, start_tile, target_tile):
        x, y = tile_center(start_tile)
        return cls(start_tile, target_tile, float(x), float(y), True)

    def update(self, dt):
        if not self.moving:
            return True

        target_x, target_y = tile_center(self.target_tile)
        dx = target_x - self.x
        dy = target_y - self.y
        distance = (dx * dx + dy * dy) ** 0.5

        if distance <= ITEM_SPEED * dt:
            self.x = float(target_x)
            self.y = float(target_y)
            self.tile = self.target_tile
            self.moving = False
            return True

        self.x += dx / distance * ITEM_SPEED * dt
        self.y += dy / distance * ITEM_SPEED * dt
        return False

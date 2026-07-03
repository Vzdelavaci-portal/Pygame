import random

from buildings import Belt, Factory, Miner
from items import Item
from orders import OrderManager
from settings import (
    BELT_COST,
    DIRECTION_ORDER,
    DIRECTIONS,
    FLOATING_TEXT_TIME,
    GRID_COLS,
    GRID_ROWS,
    MESSAGE_TIME,
    MINER_COST,
    ORE_VALUE,
    START_MONEY,
)


class World:
    def __init__(self):
        self.reset()

    def reset(self):
        self.money = START_MONEY
        self.selected_tool = "miner"
        self.engineer_mode = False
        self.message = "Build a miner on ore."
        self.message_timer = 0.0
        self.factory_pos = (GRID_COLS - 4, GRID_ROWS // 2)
        self.factory = Factory()
        self.buildings = {}
        self.items = []
        self.orders = OrderManager()
        self.floating_texts = []
        self.ore_tiles = self._make_ores()

    def _make_ores(self):
        random.seed(16)
        ores = set()
        clusters = [(4, 4), (7, 9), (10, 3)]
        for cx, cy in clusters:
            for _ in range(10):
                x = max(1, min(GRID_COLS // 2, cx + random.randint(-2, 2)))
                y = max(1, min(GRID_ROWS - 2, cy + random.randint(-2, 2)))
                if (x, y) != self.factory_pos:
                    ores.add((x, y))
        return ores

    def in_bounds(self, tile):
        x, y = tile
        return 0 <= x < GRID_COLS and 0 <= y < GRID_ROWS

    def set_message(self, text):
        self.message = text
        self.message_timer = MESSAGE_TIME

    def update_message(self, tutorial_hint, dt):
        if self.message_timer > 0:
            self.message_timer = max(0.0, self.message_timer - dt)
        else:
            self.message = tutorial_hint

    def cost_for(self, tool):
        if tool == "miner":
            return MINER_COST
        if tool == "belt":
            return BELT_COST
        return 0

    def can_place(self, tile, tool):
        if tile is None or not self.in_bounds(tile):
            return False, "Outside the build area."
        if tile == self.factory_pos:
            return False, "Cannot build over the factory."
        if tool == "belt" and isinstance(self.buildings.get(tile), Belt):
            return True, ""
        if tool != "remove" and tile in self.buildings:
            return False, "Tile is already occupied."
        if tool == "miner" and tile not in self.ore_tiles:
            return False, "Miner must be placed on ore."
        if self.money < self.cost_for(tool):
            return False, "Not enough money."
        return True, ""

    def build(self, tile, tool, direction="right"):
        if tool == "remove":
            if tile in self.buildings:
                del self.buildings[tile]
                self.set_message("Removed building.")
            else:
                self.set_message("Nothing to remove here.")
            return

        allowed, reason = self.can_place(tile, tool)
        if not allowed:
            self.set_message(reason)
            return

        if tool == "miner":
            self.buildings[tile] = Miner()
            self.money -= MINER_COST
            self.set_message("Miner built. Add a belt on its output side.")
        elif tool == "belt":
            self.buildings[tile] = Belt(direction)
            self.money -= BELT_COST
            self.set_message("Belt built.")

    def place_belt(self, tile, direction, quiet=False):
        if tile is None or not self.in_bounds(tile):
            if not quiet:
                self.set_message("Outside the build area.")
            return False
        if tile == self.factory_pos:
            if not quiet:
                self.set_message("Belts can feed into the factory, but not replace it.")
            return False

        existing = self.buildings.get(tile)
        if isinstance(existing, Belt):
            existing.direction = direction
            return True
        if existing is not None:
            if not quiet:
                self.set_message("Tile is already occupied.")
            return False
        if self.money < BELT_COST:
            if not quiet:
                self.set_message("Not enough money.")
            return False

        self.buildings[tile] = Belt(direction)
        self.money -= BELT_COST
        if not quiet:
            self.set_message("Belt built.")
        return True

    def rotate_miner(self, tile):
        building = self.buildings.get(tile)
        if isinstance(building, Miner):
            building.rotate()
            self.set_message(f"Miner output rotated {building.direction}.")

    def rotate_building(self, tile):
        building = self.buildings.get(tile)
        if isinstance(building, Miner):
            building.rotate()
            self.set_message(f"Miner output rotated {building.direction}.")
        elif isinstance(building, Belt):
            index = DIRECTION_ORDER.index(building.direction)
            building.direction = DIRECTION_ORDER[(index + 1) % len(DIRECTION_ORDER)]
            self.set_message(f"Belt rotated {building.direction}.")

    def has_miner(self):
        return any(isinstance(building, Miner) for building in self.buildings.values())

    def has_belt_next_to_miner(self):
        for tile, building in self.buildings.items():
            if isinstance(building, Miner) and self.output_belt_tile(tile, building):
                return True
        return False

    def output_belt_tile(self, tile, miner):
        dx, dy = DIRECTIONS[miner.direction]
        target = (tile[0] + dx, tile[1] + dy)
        if isinstance(self.buildings.get(target), Belt):
            return target
        return None

    def tile_has_item(self, tile):
        return any(item.tile == tile or item.target_tile == tile for item in self.items)

    def next_accepts_item(self, tile):
        if tile == self.factory_pos:
            return True
        return isinstance(self.buildings.get(tile), Belt)

    def update(self, dt):
        self.orders.update(dt)
        self._update_miners(dt)
        self._update_items(dt)
        self._update_floating_texts(dt)

    def _update_miners(self, dt):
        for tile, building in list(self.buildings.items()):
            if not isinstance(building, Miner):
                continue

            output = self.output_belt_tile(tile, building)
            building.waiting = output is None
            if building.waiting:
                building.timer = min(building.timer, 0.3)
                continue

            if self.tile_has_item(output):
                continue

            building.timer += dt
            if building.ready():
                self.items.append(Item.between(tile, output))
                building.timer = 0.0

    def _update_items(self, dt):
        for item in self.items[:]:
            arrived = item.update(dt)
            if not arrived or item.moving:
                continue

            if item.tile == self.factory_pos:
                self._deliver_item(item)
                continue

            belt = self.buildings.get(item.tile)
            if not isinstance(belt, Belt):
                continue

            dx, dy = DIRECTIONS[belt.direction]
            next_tile = (item.tile[0] + dx, item.tile[1] + dy)
            if not self.in_bounds(next_tile):
                continue
            if not self.next_accepts_item(next_tile):
                continue
            if self.tile_has_item(next_tile):
                continue

            item.target_tile = next_tile
            item.moving = True

    def _deliver_item(self, item):
        if item in self.items:
            self.items.remove(item)
        self.factory.delivered_total += 1
        self.money += ORE_VALUE
        reward = self.orders.add_iron()
        self.floating_texts.append({"text": "+1 Iron", "x": item.x - 8, "y": item.y - 18, "timer": FLOATING_TEXT_TIME})
        self.floating_texts.append({"text": f"+${ORE_VALUE}", "x": item.x + 8, "y": item.y + 2, "timer": FLOATING_TEXT_TIME})
        if reward:
            self.money += reward
            self.set_message(f"Order complete. Reward +${reward}.")

    def _update_floating_texts(self, dt):
        for text in self.floating_texts[:]:
            text["timer"] -= dt
            text["y"] -= 28 * dt
            if text["timer"] <= 0:
                self.floating_texts.remove(text)

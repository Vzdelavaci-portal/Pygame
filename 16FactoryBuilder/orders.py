from dataclasses import dataclass

from settings import POPUP_TIME


@dataclass
class OrderManager:
    number: int = 1
    target: int = 20
    delivered: int = 0
    reward: int = 150
    item_kind: str = "iron_ore"
    item_name: str = "Iron Ore"
    popup_timer: float = 0.0
    last_reward: int = 0

    def add_item(self, item_kind):
        if item_kind != self.item_kind:
            return 0

        self.delivered += 1
        if self.delivered >= self.target:
            reward = self.reward
            self.last_reward = reward
            self.popup_timer = POPUP_TIME
            self._next_order()
            return reward
        return 0

    def _next_order(self):
        self.number += 1
        self.delivered = 0
        if self.number == 2:
            self.item_kind = "iron_plate"
            self.item_name = "Iron Plates"
            self.target = 15
            self.reward = 300
        else:
            self.item_kind = "iron_plate"
            self.item_name = "Iron Plates"
            self.target += 15
            self.reward += 150

    def update(self, dt):
        self.popup_timer = max(0.0, self.popup_timer - dt)

    @property
    def popup_visible(self):
        return self.popup_timer > 0

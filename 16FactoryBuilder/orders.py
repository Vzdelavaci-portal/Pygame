from dataclasses import dataclass

from settings import POPUP_TIME


@dataclass
class OrderManager:
    number: int = 1
    target: int = 20
    delivered: int = 0
    reward: int = 150
    popup_timer: float = 0.0
    last_reward: int = 0

    def add_iron(self):
        self.delivered += 1
        if self.delivered >= self.target:
            reward = self.reward
            self.last_reward = reward
            self.popup_timer = POPUP_TIME
            self.number += 1
            self.delivered = 0
            self.target += 20
            self.reward += 100
            return reward
        return 0

    def update(self, dt):
        self.popup_timer = max(0.0, self.popup_timer - dt)

    @property
    def popup_visible(self):
        return self.popup_timer > 0

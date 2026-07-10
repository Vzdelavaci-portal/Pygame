import pygame

from settings import (
    BELT_COST,
    BELT_UPGRADE_COST,
    BLUE,
    BOTTOM_TOOLBAR_HEIGHT,
    HEIGHT,
    MINER_COST,
    MINER_UPGRADE_COST,
    MUTED,
    PANEL,
    PANEL_2,
    SMELTER_COST,
    WHITE,
    WIDTH,
    YELLOW,
)


TOOLS = [
    {"id": "miner", "name": "Miner", "price": MINER_COST},
    {"id": "belt", "name": "Belt", "price": BELT_COST},
    {"id": "smelter", "name": "Smelter", "price": SMELTER_COST},
    {"id": "remove", "name": "Remove", "price": 0},
]


class Toolbar:
    def __init__(self):
        self.rects = {}
        self.upgrade_rects = {}

    def tool_at(self, pos):
        for tool_id, rect in self.rects.items():
            if rect.collidepoint(pos):
                return tool_id
        return None

    def upgrade_at(self, pos):
        for upgrade_id, rect in self.upgrade_rects.items():
            if rect.collidepoint(pos):
                return upgrade_id
        return None

    def draw(self, screen, fonts, world):
        pygame.draw.rect(screen, PANEL, (0, HEIGHT - BOTTOM_TOOLBAR_HEIGHT, WIDTH, BOTTOM_TOOLBAR_HEIGHT))
        pygame.draw.line(screen, BLUE, (0, HEIGHT - BOTTOM_TOOLBAR_HEIGHT), (WIDTH, HEIGHT - BOTTOM_TOOLBAR_HEIGHT), 2)

        self.rects.clear()
        self.upgrade_rects.clear()
        button_w = 118
        button_h = 58
        gap = 10
        start_x = 22
        y = HEIGHT - BOTTOM_TOOLBAR_HEIGHT + 22

        for index, tool in enumerate(TOOLS):
            x = start_x + index * (button_w + gap)
            rect = pygame.Rect(x, y, button_w, button_h)
            self.rects[tool["id"]] = rect

            active = world.selected_tool == tool["id"]
            locked = tool["id"] == "smelter" and not world.smelter_unlocked
            fill = BLUE if active else PANEL_2
            border = WHITE if active else MUTED
            if locked:
                fill = (36, 33, 34)
            pygame.draw.rect(screen, fill, rect, border_radius=8)
            pygame.draw.rect(screen, border, rect, 2, border_radius=8)

            name = tool["name"] if not locked else "Smelter*"
            screen.blit(fonts["small"].render(name, True, WHITE if not locked else MUTED), (x + 10, y + 9))
            price_text = "Locked" if locked else ("Free" if tool["price"] == 0 else f"${tool['price']}")
            screen.blit(fonts["small"].render(price_text, True, YELLOW), (x + 14, y + 31))

        self._draw_upgrade_button(
            screen,
            fonts,
            "miner_speed",
            "Miner Speed",
            MINER_UPGRADE_COST * (world.miner_speed_level + 1),
            world.miner_speed_level,
            pygame.Rect(540, y, 150, button_h),
        )
        self._draw_upgrade_button(
            screen,
            fonts,
            "belt_speed",
            "Belt Speed",
            BELT_UPGRADE_COST * (world.belt_speed_level + 1),
            world.belt_speed_level,
            pygame.Rect(700, y, 150, button_h),
        )

        screen.blit(fonts["tiny"].render("Drag: belt/remove", True, MUTED), (866, HEIGHT - BOTTOM_TOOLBAR_HEIGHT + 31))
        screen.blit(fonts["tiny"].render("R reset | TAB engineer", True, MUTED), (866, HEIGHT - BOTTOM_TOOLBAR_HEIGHT + 51))

    def _draw_upgrade_button(self, screen, fonts, upgrade_id, name, price, level, rect):
        self.upgrade_rects[upgrade_id] = rect
        pygame.draw.rect(screen, PANEL_2, rect, border_radius=8)
        pygame.draw.rect(screen, YELLOW, rect, 2, border_radius=8)
        screen.blit(fonts["tiny"].render(name, True, WHITE), (rect.x + 10, rect.y + 8))
        screen.blit(fonts["tiny"].render(f"Lv {level}  ${price}", True, YELLOW), (rect.x + 10, rect.y + 31))

import pygame

from settings import BELT_COST, BLUE, BOTTOM_TOOLBAR_HEIGHT, HEIGHT, MINER_COST, MUTED, PANEL, PANEL_2, WHITE, WIDTH, YELLOW


TOOLS = [
    {"id": "miner", "name": "Miner", "price": MINER_COST},
    {"id": "belt", "name": "Belt", "price": BELT_COST},
    {"id": "remove", "name": "Remove", "price": 0},
]


class Toolbar:
    def __init__(self):
        self.rects = {}

    def tool_at(self, pos):
        for tool_id, rect in self.rects.items():
            if rect.collidepoint(pos):
                return tool_id
        return None

    def draw(self, screen, fonts, selected_tool):
        pygame.draw.rect(screen, PANEL, (0, HEIGHT - BOTTOM_TOOLBAR_HEIGHT, WIDTH, BOTTOM_TOOLBAR_HEIGHT))
        pygame.draw.line(screen, BLUE, (0, HEIGHT - BOTTOM_TOOLBAR_HEIGHT), (WIDTH, HEIGHT - BOTTOM_TOOLBAR_HEIGHT), 2)

        self.rects.clear()
        button_w = 150
        button_h = 58
        gap = 14
        start_x = 22
        y = HEIGHT - BOTTOM_TOOLBAR_HEIGHT + 22

        for index, tool in enumerate(TOOLS):
            x = start_x + index * (button_w + gap)
            rect = pygame.Rect(x, y, button_w, button_h)
            self.rects[tool["id"]] = rect

            active = selected_tool == tool["id"]
            fill = BLUE if active else PANEL_2
            border = WHITE if active else MUTED
            pygame.draw.rect(screen, fill, rect, border_radius=8)
            pygame.draw.rect(screen, border, rect, 2, border_radius=8)

            screen.blit(fonts["small"].render(tool["name"], True, WHITE), (x + 14, y + 9))
            price_text = "Free" if tool["price"] == 0 else f"${tool['price']}"
            screen.blit(fonts["small"].render(price_text, True, YELLOW), (x + 14, y + 31))

        help_text = "Belt: hold left and draw   Right: rotate miner/belt   R: reset   TAB: engineer"
        screen.blit(fonts["tiny"].render(help_text, True, MUTED), (520, HEIGHT - BOTTOM_TOOLBAR_HEIGHT + 40))

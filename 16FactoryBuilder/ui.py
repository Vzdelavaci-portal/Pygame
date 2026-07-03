import pygame

from buildings import Belt, Miner
from settings import (
    BG,
    BLUE,
    CYAN,
    DARK,
    DIRECTIONS,
    FLOATING_TEXT_TIME,
    GREEN,
    GRID,
    GRID_COLS,
    GRID_ROWS,
    HEIGHT,
    IRON_DARK,
    MINER_PRODUCTION_TIME,
    MUTED,
    ORANGE,
    PANEL,
    PANEL_2,
    RED,
    TILE_SIZE,
    TOP_PANEL_HEIGHT,
    WHITE,
    WIDTH,
    YELLOW,
)


class Renderer:
    def __init__(self, screen):
        self.screen = screen
        self.fonts = {
            "tiny": pygame.font.SysFont("Arial", 16),
            "small": pygame.font.SysFont("Arial", 19),
            "normal": pygame.font.SysFont("Arial", 23),
            "big": pygame.font.SysFont("Arial", 42, bold=True),
        }
        self.belt_anim = 0.0

    def update(self, dt):
        self.belt_anim = (self.belt_anim + dt * 40) % 40

    def tile_rect(self, tile, pad=0):
        x, y = tile
        return pygame.Rect(
            x * TILE_SIZE + pad,
            TOP_PANEL_HEIGHT + y * TILE_SIZE + pad,
            TILE_SIZE - pad * 2,
            TILE_SIZE - pad * 2,
        )

    def draw(self, world, toolbar, mouse_tile, ghost_valid):
        self.screen.fill(BG)
        self.draw_grid()
        self.draw_ores(world)
        self.draw_factory(world)
        self.draw_buildings(world)
        self.draw_items(world)
        self.draw_ghost(mouse_tile, ghost_valid, world.selected_tool)
        if world.engineer_mode:
            self.draw_engineer_labels(world)
        self.draw_floating_texts(world)
        self.draw_top_panel(world)
        toolbar.draw(self.screen, self.fonts, world.selected_tool)
        if world.orders.popup_visible:
            self.draw_popup(world)

    def draw_grid(self):
        for y in range(GRID_ROWS):
            for x in range(GRID_COLS):
                pygame.draw.rect(self.screen, BG, self.tile_rect((x, y)))
                pygame.draw.rect(self.screen, GRID, self.tile_rect((x, y)), 1)

    def draw_ores(self, world):
        for tile in world.ore_tiles:
            rect = self.tile_rect(tile)
            pygame.draw.circle(self.screen, IRON_DARK, rect.center, 17)
            pygame.draw.circle(self.screen, ORANGE, (rect.centerx - 2, rect.centery + 2), 12)
            pygame.draw.circle(self.screen, YELLOW, (rect.centerx - 7, rect.centery - 5), 4)

    def draw_factory(self, world):
        rect = self.tile_rect(world.factory_pos, 3)
        pygame.draw.rect(self.screen, RED, rect, border_radius=7)
        pygame.draw.rect(self.screen, WHITE, rect, 2, border_radius=7)
        pygame.draw.rect(self.screen, DARK, (rect.x + 7, rect.y + 18, rect.width - 14, rect.height - 10))
        pygame.draw.rect(self.screen, WHITE, (rect.x + 10, rect.y + 8, 7, 15))
        pygame.draw.rect(self.screen, WHITE, (rect.x + 24, rect.y + 5, 7, 18))
        pygame.draw.rect(self.screen, YELLOW, (rect.x + 7, rect.y + 28, rect.width - 14, 4))

    def draw_buildings(self, world):
        for tile, building in world.buildings.items():
            if isinstance(building, Belt):
                self.draw_belt(tile, building.direction)
            elif isinstance(building, Miner):
                self.draw_miner(tile, building)

    def draw_belt(self, tile, direction):
        rect = self.tile_rect(tile, 4)
        pygame.draw.rect(self.screen, (94, 101, 108), rect, border_radius=6)
        pygame.draw.rect(self.screen, (55, 61, 69), rect, 2, border_radius=6)
        dx, dy = DIRECTIONS[direction]
        for i in range(3):
            offset = ((self.belt_anim + i * 13) % 38) - 19
            pygame.draw.circle(self.screen, WHITE, (int(rect.centerx + dx * offset), int(rect.centery + dy * offset)), 3)
        self.draw_arrow(rect.center, direction, DARK, 13)

    def draw_miner(self, tile, miner):
        rect = self.tile_rect(tile, 4)
        pygame.draw.rect(self.screen, BLUE, rect, border_radius=7)
        pygame.draw.rect(self.screen, WHITE, rect, 2, border_radius=7)
        pygame.draw.circle(self.screen, DARK, rect.center, 11)
        pygame.draw.circle(self.screen, ORANGE, rect.center, 5)
        progress = max(0.0, min(1.0, miner.timer / MINER_PRODUCTION_TIME))
        pygame.draw.rect(self.screen, YELLOW, (rect.x + 5, rect.bottom - 8, int((rect.width - 10) * progress), 4), border_radius=2)
        self.draw_arrow(rect.center, miner.direction, GREEN if not miner.waiting else YELLOW, 15)

    def draw_arrow(self, center, direction, color, size):
        cx, cy = center
        if direction == "right":
            points = [(cx + size, cy), (cx - size // 2, cy - size // 2), (cx - size // 2, cy + size // 2)]
        elif direction == "left":
            points = [(cx - size, cy), (cx + size // 2, cy - size // 2), (cx + size // 2, cy + size // 2)]
        elif direction == "up":
            points = [(cx, cy - size), (cx - size // 2, cy + size // 2), (cx + size // 2, cy + size // 2)]
        else:
            points = [(cx, cy + size), (cx - size // 2, cy - size // 2), (cx + size // 2, cy - size // 2)]
        pygame.draw.polygon(self.screen, color, points)

    def draw_items(self, world):
        for item in world.items:
            pygame.draw.circle(self.screen, ORANGE, (int(item.x), int(item.y)), 8)
            pygame.draw.circle(self.screen, YELLOW, (int(item.x - 3), int(item.y - 3)), 3)

    def draw_ghost(self, tile, valid, selected_tool):
        if tile is None:
            return
        color = GREEN if valid else RED
        overlay = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        overlay.fill((*color, 68))
        self.screen.blit(overlay, self.tile_rect(tile).topleft)
        if selected_tool == "belt":
            pygame.draw.rect(self.screen, color, self.tile_rect(tile, 5), 2, border_radius=6)

    def draw_top_panel(self, world):
        pygame.draw.rect(self.screen, PANEL, (0, 0, WIDTH, TOP_PANEL_HEIGHT))
        pygame.draw.line(self.screen, BLUE, (0, TOP_PANEL_HEIGHT), (WIDTH, TOP_PANEL_HEIGHT), 2)
        self.screen.blit(self.fonts["normal"].render(f"Money: ${world.money}", True, GREEN), (18, 12))
        self.screen.blit(self.fonts["normal"].render(f"Order #{world.orders.number}: {world.orders.delivered}/{world.orders.target} Iron", True, YELLOW), (180, 12))
        self.screen.blit(self.fonts["normal"].render(f"Reward: ${world.orders.reward}", True, WHITE), (462, 12))
        self.screen.blit(self.fonts["normal"].render(f"Selected: {world.selected_tool.title()}", True, CYAN), (650, 12))
        mode = "Engineer: ON" if world.engineer_mode else "Engineer: OFF"
        self.screen.blit(self.fonts["small"].render(mode, True, GREEN if world.engineer_mode else MUTED), (850, 15))
        self.screen.blit(self.fonts["small"].render(world.message, True, MUTED), (18, 52))

    def draw_popup(self, world):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        self.screen.blit(overlay, (0, 0))
        rect = pygame.Rect(WIDTH // 2 - 210, HEIGHT // 2 - 95, 420, 190)
        pygame.draw.rect(self.screen, PANEL_2, rect, border_radius=8)
        pygame.draw.rect(self.screen, GREEN, rect, 3, border_radius=8)
        self.screen.blit(self.fonts["big"].render("Mission Complete", True, WHITE), (rect.x + 48, rect.y + 28))
        self.screen.blit(self.fonts["normal"].render(f"Reward paid: ${world.orders.last_reward}", True, YELLOW), (rect.x + 118, rect.y + 92))
        self.screen.blit(self.fonts["small"].render("Next order is already active.", True, MUTED), (rect.x + 106, rect.y + 130))

    def draw_floating_texts(self, world):
        for text in world.floating_texts:
            alpha = max(0, min(255, int(255 * text["timer"] / FLOATING_TEXT_TIME)))
            surface = self.fonts["small"].render(text["text"], True, YELLOW)
            surface.set_alpha(alpha)
            self.screen.blit(surface, (text["x"], text["y"]))

    def draw_engineer_labels(self, world):
        self.draw_label(world.factory_pos, f"Delivered: {world.factory.delivered_total}", GREEN)
        for tile, building in world.buildings.items():
            if isinstance(building, Miner):
                color = YELLOW if building.waiting else GREEN
                status = "Waiting for belt" if building.waiting else "Running"
                self.draw_label(tile, status, color)
            elif isinstance(building, Belt):
                self.draw_label(tile, "Flow", GREEN)

    def draw_label(self, tile, text, color):
        rect = self.tile_rect(tile)
        label = self.fonts["tiny"].render(text, True, color)
        bg = pygame.Rect(rect.centerx - label.get_width() // 2 - 4, rect.y - 17, label.get_width() + 8, 18)
        pygame.draw.rect(self.screen, DARK, bg, border_radius=4)
        self.screen.blit(label, (bg.x + 4, bg.y + 1))

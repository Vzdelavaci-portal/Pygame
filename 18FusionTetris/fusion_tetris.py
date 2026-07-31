import math
import random
import sys
from dataclasses import dataclass

import pygame


# =========================================================
# INITIALIZATION
# =========================================================

pygame.init()

WINDOW_WIDTH = 1120
WINDOW_HEIGHT = 900
FPS = 60

CELL_SIZE = 34
GRID_COLS = 10
GRID_ROWS = 20

BOARD_WIDTH = GRID_COLS * CELL_SIZE
BOARD_HEIGHT = GRID_ROWS * CELL_SIZE

BOARD_X = 90
BOARD_Y = 70

PANEL_X = BOARD_X + BOARD_WIDTH + 55
PANEL_WIDTH = 520
PANEL_HEIGHT = WINDOW_HEIGHT - BOARD_Y - 30

SCREEN = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Fusion Tetris")

CLOCK = pygame.time.Clock()

FONT_SMALL = pygame.font.SysFont("consolas", 18)
FONT_MEDIUM = pygame.font.SysFont("consolas", 24, bold=True)
FONT_LARGE = pygame.font.SysFont("consolas", 38, bold=True)
FONT_TITLE = pygame.font.SysFont("consolas", 56, bold=True)


# =========================================================
# COLORS
# =========================================================

BACKGROUND = (5, 8, 18)
PANEL_BACKGROUND = (10, 15, 30)
BOARD_BACKGROUND = (8, 13, 26)
GRID_COLOR = (20, 30, 52)

WHITE = (240, 245, 255)
LIGHT_GRAY = (170, 180, 205)
GRAY = (105, 118, 145)
DARK_GRAY = (42, 51, 72)

CYAN = (50, 235, 255)
GREEN = (55, 235, 135)
YELLOW = (255, 215, 70)
ORANGE = (255, 140, 45)
RED = (255, 70, 90)
PURPLE = (190, 85, 255)


# =========================================================
# MATERIALS
# =========================================================

MATERIALS = [
    {
        "name": "Stone",
        "short": "S",
        "color": (110, 125, 150),
        "score": 10,
    },
    {
        "name": "Copper",
        "short": "C",
        "color": (215, 115, 55),
        "score": 25,
    },
    {
        "name": "Iron",
        "short": "I",
        "color": (160, 180, 205),
        "score": 60,
    },
    {
        "name": "Steel",
        "short": "ST",
        "color": (80, 170, 220),
        "score": 140,
    },
    {
        "name": "Titanium",
        "short": "T",
        "color": (170, 100, 255),
        "score": 320,
    },
    {
        "name": "Crystal",
        "short": "CR",
        "color": (50, 240, 220),
        "score": 750,
    },
    {
        "name": "Diamond",
        "short": "D",
        "color": (245, 250, 255),
        "score": 2000,
    },
]


# =========================================================
# TETROMINO SHAPES
# =========================================================

SHAPES = {
    "I": [
        [(0, 1), (1, 1), (2, 1), (3, 1)],
        [(2, 0), (2, 1), (2, 2), (2, 3)],
    ],
    "O": [
        [(1, 0), (2, 0), (1, 1), (2, 1)],
    ],
    "T": [
        [(1, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (1, 1), (2, 1), (1, 2)],
        [(0, 1), (1, 1), (2, 1), (1, 2)],
        [(1, 0), (0, 1), (1, 1), (1, 2)],
    ],
    "L": [
        [(2, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (1, 1), (1, 2), (2, 2)],
        [(0, 1), (1, 1), (2, 1), (0, 2)],
        [(0, 0), (1, 0), (1, 1), (1, 2)],
    ],
    "J": [
        [(0, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (2, 0), (1, 1), (1, 2)],
        [(0, 1), (1, 1), (2, 1), (2, 2)],
        [(1, 0), (1, 1), (0, 2), (1, 2)],
    ],
    "S": [
        [(1, 0), (2, 0), (0, 1), (1, 1)],
        [(1, 0), (1, 1), (2, 1), (2, 2)],
    ],
    "Z": [
        [(0, 0), (1, 0), (1, 1), (2, 1)],
        [(2, 0), (1, 1), (2, 1), (1, 2)],
    ],
}

SHAPE_NAMES = list(SHAPES.keys())


# =========================================================
# DATA CLASSES
# =========================================================

@dataclass
class Block:
    level: int


@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    life: float
    max_life: float
    size: float
    color: tuple


@dataclass
class FloatingText:
    text: str
    x: float
    y: float
    life: float
    max_life: float
    color: tuple


# =========================================================
# PIECE
# =========================================================

class Piece:
    def __init__(self, shape_name=None):
        self.shape_name = shape_name or random.choice(SHAPE_NAMES)
        self.rotation = 0

        self.x = GRID_COLS // 2 - 2
        self.y = -2

        self.levels = [
            self.generate_material_level()
            for _ in range(4)
        ]

    @staticmethod
    def generate_material_level():
        roll = random.random()

        if roll < 0.72:
            return 0

        if roll < 0.94:
            return 1

        return 2

    def cells(self, x_offset=0, y_offset=0, rotation=None):
        selected_rotation = (
            self.rotation if rotation is None else rotation
        )

        shape = SHAPES[self.shape_name][
            selected_rotation % len(SHAPES[self.shape_name])
        ]

        result = []

        for index, (cell_x, cell_y) in enumerate(shape):
            result.append(
                (
                    self.x + cell_x + x_offset,
                    self.y + cell_y + y_offset,
                    self.levels[index],
                )
            )

        return result


# =========================================================
# HELPERS
# =========================================================

def clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))


def lighten(color, amount):
    return tuple(
        clamp(channel + amount, 0, 255)
        for channel in color
    )


def darken(color, amount):
    return tuple(
        clamp(channel - amount, 0, 255)
        for channel in color
    )


def draw_text(
    surface,
    text,
    font,
    color,
    x,
    y,
    center=False,
):
    rendered = font.render(text, True, color)
    rect = rendered.get_rect()

    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)

    surface.blit(rendered, rect)
    return rect


def draw_glow_rect(
    surface,
    rect,
    color,
    radius=8,
    glow_layers=3,
):
    for layer in range(glow_layers, 0, -1):
        expansion = layer * 4

        glow_rect = pygame.Rect(
            rect.x - expansion,
            rect.y - expansion,
            rect.width + expansion * 2,
            rect.height + expansion * 2,
        )

        glow_surface = pygame.Surface(
            glow_rect.size,
            pygame.SRCALPHA,
        )

        alpha = max(10, 55 - layer * 12)

        pygame.draw.rect(
            glow_surface,
            (*color, alpha),
            glow_surface.get_rect(),
            border_radius=radius + expansion,
        )

        surface.blit(
            glow_surface,
            glow_rect.topleft,
        )


# =========================================================
# GAME
# =========================================================

class FusionTetris:
    def __init__(self):
        self.reset()

    def reset(self):
        self.board = [
            [None for _ in range(GRID_COLS)]
            for _ in range(GRID_ROWS)
        ]

        self.current_piece = Piece()
        self.next_piece = Piece()

        self.score = 0
        self.combo = 0
        self.best_combo = 0
        self.highest_material = 0

        self.fall_timer = 0.0
        self.fall_delay = 0.72

        self.lock_timer = 0.0
        self.lock_delay = 0.38

        self.soft_drop = False
        self.state = "playing"

        self.particles = []
        self.floating_texts = []

        self.screen_shake = 0.0
        self.flash_alpha = 0.0

        self.message = "Merge equal materials and create Diamond!"
        self.message_timer = 4.0

        self.total_merges = 0
        self.pieces_placed = 0

        self.start_time = pygame.time.get_ticks()
        self.game_over_time = 0.0

    # -----------------------------------------------------
    # Input
    # -----------------------------------------------------

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if self.state == "playing":
                if event.key in (pygame.K_LEFT, pygame.K_a):
                    self.move_piece(-1, 0)

                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    self.move_piece(1, 0)

                elif event.key in (pygame.K_UP, pygame.K_w):
                    self.rotate_piece()

                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.soft_drop = True

                elif event.key == pygame.K_SPACE:
                    self.hard_drop()

                elif event.key == pygame.K_r:
                    self.reset()

            elif self.state == "game_over":
                if event.key in (
                    pygame.K_RETURN,
                    pygame.K_r,
                ):
                    self.reset()

        elif event.type == pygame.KEYUP:
            if event.key in (pygame.K_DOWN, pygame.K_s):
                self.soft_drop = False

    # -----------------------------------------------------
    # Update
    # -----------------------------------------------------

    def update(self, dt):
        self.update_particles(dt)
        self.update_floating_texts(dt)

        self.screen_shake = max(
            0,
            self.screen_shake - 30 * dt,
        )

        self.flash_alpha = max(
            0,
            self.flash_alpha - 230 * dt,
        )

        self.message_timer = max(
            0,
            self.message_timer - dt,
        )

        if self.state != "playing":
            return

        current_delay = (
            0.055 if self.soft_drop else self.fall_delay
        )

        self.fall_timer += dt

        if self.fall_timer >= current_delay:
            self.fall_timer = 0

            if self.is_valid_position(
                self.current_piece,
                y_offset=1,
            ):
                self.current_piece.y += 1
                self.lock_timer = 0
            else:
                self.lock_timer += current_delay

        if not self.is_valid_position(
            self.current_piece,
            y_offset=1,
        ):
            self.lock_timer += dt

            if self.lock_timer >= self.lock_delay:
                self.lock_piece()
        else:
            self.lock_timer = 0

    # -----------------------------------------------------
    # Piece movement
    # -----------------------------------------------------

    def move_piece(self, dx, dy):
        if self.is_valid_position(
            self.current_piece,
            x_offset=dx,
            y_offset=dy,
        ):
            self.current_piece.x += dx
            self.current_piece.y += dy
            self.lock_timer = 0

    def rotate_piece(self):
        next_rotation = (
            self.current_piece.rotation + 1
        ) % len(SHAPES[self.current_piece.shape_name])

        kick_tests = [
            (0, 0),
            (-1, 0),
            (1, 0),
            (-2, 0),
            (2, 0),
            (0, -1),
        ]

        for kick_x, kick_y in kick_tests:
            if self.is_valid_position(
                self.current_piece,
                x_offset=kick_x,
                y_offset=kick_y,
                rotation=next_rotation,
            ):
                self.current_piece.rotation = next_rotation
                self.current_piece.x += kick_x
                self.current_piece.y += kick_y
                self.lock_timer = 0
                return

    def hard_drop(self):
        distance = 0

        while self.is_valid_position(
            self.current_piece,
            y_offset=distance + 1,
        ):
            distance += 1

        self.current_piece.y += distance
        self.score += distance * 2

        self.lock_piece()

    def is_valid_position(
        self,
        piece,
        x_offset=0,
        y_offset=0,
        rotation=None,
    ):
        for x, y, _ in piece.cells(
            x_offset,
            y_offset,
            rotation,
        ):
            if x < 0 or x >= GRID_COLS:
                return False

            if y >= GRID_ROWS:
                return False

            if y >= 0 and self.board[y][x] is not None:
                return False

        return True

    # -----------------------------------------------------
    # Piece locking
    # -----------------------------------------------------

    def lock_piece(self):
        game_over = False

        for x, y, level in self.current_piece.cells():
            if y < 0:
                game_over = True
                continue

            if 0 <= y < GRID_ROWS:
                self.board[y][x] = Block(level)

        self.pieces_placed += 1

        if game_over:
            self.end_game()
            return

        self.combo = 0
        self.resolve_board()

        if self.state != "playing":
            return

        self.current_piece = self.next_piece
        self.next_piece = Piece()

        self.fall_timer = 0
        self.lock_timer = 0

        if not self.is_valid_position(self.current_piece):
            self.end_game()

    # -----------------------------------------------------
    # Merge system
    # -----------------------------------------------------

    def resolve_board(self):
        chain = 0

        while True:
            groups = self.find_merge_groups()

            if not groups:
                break

            chain += 1
            self.combo += 1
            self.best_combo = max(
                self.best_combo,
                self.combo,
            )

            occupied_cells = set()

            for group in groups:
                if any(cell in occupied_cells for cell in group):
                    continue

                for cell in group:
                    occupied_cells.add(cell)

                self.merge_group(group, chain)

            self.apply_gravity()

        if chain > 0:
            self.message = f"CHAIN REACTION x{chain}"
            self.message_timer = 2.0

            if chain >= 3:
                self.screen_shake = 10
                self.flash_alpha = 120

    def find_merge_groups(self):
        visited = set()
        groups = []

        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                block = self.board[row][col]

                if block is None:
                    continue

                if (col, row) in visited:
                    continue

                group = self.flood_fill_group(
                    col,
                    row,
                    block.level,
                    visited,
                )

                if len(group) >= 2:
                    groups.append(group)

        groups.sort(
            key=lambda group: max(y for _, y in group),
            reverse=True,
        )

        return groups

    def flood_fill_group(
        self,
        start_x,
        start_y,
        level,
        visited,
    ):
        stack = [(start_x, start_y)]
        group = []

        while stack:
            x, y = stack.pop()

            if (x, y) in visited:
                continue

            if not (
                0 <= x < GRID_COLS
                and 0 <= y < GRID_ROWS
            ):
                continue

            block = self.board[y][x]

            if block is None or block.level != level:
                continue

            visited.add((x, y))
            group.append((x, y))

            stack.extend(
                [
                    (x + 1, y),
                    (x - 1, y),
                    (x, y + 1),
                    (x, y - 1),
                ]
            )

        return group

    def merge_group(self, group, chain):
        source_x, source_y = self.choose_merge_target(group)

        source_block = self.board[source_y][source_x]

        if source_block is None:
            return

        old_level = source_block.level
        new_level = min(
            old_level + 1,
            len(MATERIALS) - 1,
        )

        group_size = len(group)

        for x, y in group:
            self.board[y][x] = None

        self.board[source_y][source_x] = Block(new_level)

        material = MATERIALS[new_level]

        score_gain = int(
            material["score"]
            * group_size
            * max(1, chain)
        )

        self.score += score_gain
        self.total_merges += 1

        self.highest_material = max(
            self.highest_material,
            new_level,
        )

        pixel_x = (
            BOARD_X
            + source_x * CELL_SIZE
            + CELL_SIZE // 2
        )

        pixel_y = (
            BOARD_Y
            + source_y * CELL_SIZE
            + CELL_SIZE // 2
        )

        self.create_particles(
            pixel_x,
            pixel_y,
            material["color"],
            14 + group_size * 3,
        )

        self.floating_texts.append(
            FloatingText(
                text=f"+{score_gain}",
                x=pixel_x,
                y=pixel_y,
                life=1.1,
                max_life=1.1,
                color=material["color"],
            )
        )

        if group_size >= 4:
            self.floating_texts.append(
                FloatingText(
                    text=f"MERGE x{group_size}",
                    x=pixel_x,
                    y=pixel_y - 28,
                    life=1.4,
                    max_life=1.4,
                    color=YELLOW,
                )
            )

        self.screen_shake = min(
            14,
            self.screen_shake + group_size * 0.7,
        )

        if new_level == len(MATERIALS) - 1:
            self.message = "DIAMOND CREATED!"
            self.message_timer = 4.0
            self.flash_alpha = 210

    @staticmethod
    def choose_merge_target(group):
        lowest_row = max(y for _, y in group)

        candidates = [
            (x, y)
            for x, y in group
            if y == lowest_row
        ]

        average_x = sum(x for x, _ in group) / len(group)

        return min(
            candidates,
            key=lambda cell: abs(cell[0] - average_x),
        )

    def apply_gravity(self):
        moved = True

        while moved:
            moved = False

            for row in range(GRID_ROWS - 2, -1, -1):
                for col in range(GRID_COLS):
                    if self.board[row][col] is None:
                        continue

                    if self.board[row + 1][col] is None:
                        self.board[row + 1][col] = (
                            self.board[row][col]
                        )
                        self.board[row][col] = None
                        moved = True

    # -----------------------------------------------------
    # Game over
    # -----------------------------------------------------

    def end_game(self):
        self.state = "game_over"
        self.game_over_time = self.get_play_time()
        self.screen_shake = 15
        self.flash_alpha = 150

    def get_play_time(self):
        if self.state == "game_over":
            return self.game_over_time

        return (
            pygame.time.get_ticks() - self.start_time
        ) / 1000

    # -----------------------------------------------------
    # Particles
    # -----------------------------------------------------

    def create_particles(
        self,
        x,
        y,
        color,
        amount=18,
    ):
        for _ in range(amount):
            angle = random.uniform(0, math.tau)
            speed = random.uniform(45, 190)

            self.particles.append(
                Particle(
                    x=x,
                    y=y,
                    vx=math.cos(angle) * speed,
                    vy=math.sin(angle) * speed,
                    life=random.uniform(0.35, 0.9),
                    max_life=0.9,
                    size=random.uniform(2, 6),
                    color=color,
                )
            )

    def update_particles(self, dt):
        for particle in self.particles[:]:
            particle.x += particle.vx * dt
            particle.y += particle.vy * dt

            particle.vx *= 0.965
            particle.vy *= 0.965
            particle.vy += 90 * dt

            particle.life -= dt

            if particle.life <= 0:
                self.particles.remove(particle)

    def update_floating_texts(self, dt):
        for text in self.floating_texts[:]:
            text.y -= 40 * dt
            text.life -= dt

            if text.life <= 0:
                self.floating_texts.remove(text)

    # -----------------------------------------------------
    # Drawing
    # -----------------------------------------------------

    def draw(self):
        SCREEN.fill(BACKGROUND)

        shake_x = 0
        shake_y = 0

        if self.screen_shake > 0:
            shake_x = random.randint(
                -int(self.screen_shake),
                int(self.screen_shake),
            )

            shake_y = random.randint(
                -int(self.screen_shake),
                int(self.screen_shake),
            )

        game_surface = pygame.Surface(
            (WINDOW_WIDTH, WINDOW_HEIGHT),
            pygame.SRCALPHA,
        )

        self.draw_background(game_surface)
        self.draw_board(game_surface)
        self.draw_side_panel(game_surface)

        SCREEN.blit(
            game_surface,
            (shake_x, shake_y),
        )

        self.draw_particles()
        self.draw_floating_texts()

        if self.flash_alpha > 0:
            flash = pygame.Surface(
                (WINDOW_WIDTH, WINDOW_HEIGHT),
                pygame.SRCALPHA,
            )

            flash.fill(
                (
                    255,
                    255,
                    255,
                    int(self.flash_alpha),
                )
            )

            SCREEN.blit(flash, (0, 0))

        if self.state == "game_over":
            self.draw_game_over()

    def draw_background(self, surface):
        for x in range(0, WINDOW_WIDTH, 80):
            pygame.draw.line(
                surface,
                (9, 14, 29),
                (x, 0),
                (x, WINDOW_HEIGHT),
            )

        for y in range(0, WINDOW_HEIGHT, 80):
            pygame.draw.line(
                surface,
                (9, 14, 29),
                (0, y),
                (WINDOW_WIDTH, y),
            )

        draw_text(
            surface,
            "FUSION TETRIS",
            FONT_LARGE,
            CYAN,
            BOARD_X,
            20,
        )

    def draw_board(self, surface):
        board_rect = pygame.Rect(
            BOARD_X - 8,
            BOARD_Y - 8,
            BOARD_WIDTH + 16,
            BOARD_HEIGHT + 16,
        )

        draw_glow_rect(
            surface,
            board_rect,
            CYAN,
            radius=14,
            glow_layers=3,
        )

        pygame.draw.rect(
            surface,
            BOARD_BACKGROUND,
            board_rect,
            border_radius=14,
        )

        pygame.draw.rect(
            surface,
            CYAN,
            board_rect,
            2,
            border_radius=14,
        )

        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                cell_rect = pygame.Rect(
                    BOARD_X + col * CELL_SIZE,
                    BOARD_Y + row * CELL_SIZE,
                    CELL_SIZE,
                    CELL_SIZE,
                )

                pygame.draw.rect(
                    surface,
                    GRID_COLOR,
                    cell_rect,
                    1,
                )

                block = self.board[row][col]

                if block is not None:
                    self.draw_block(
                        surface,
                        col,
                        row,
                        block.level,
                    )

        if self.state == "playing":
            self.draw_ghost_piece(surface)
            self.draw_current_piece(surface)

    def draw_block(
        self,
        surface,
        grid_x,
        grid_y,
        level,
        alpha=255,
        outline_only=False,
    ):
        material = MATERIALS[level]
        color = material["color"]

        rect = pygame.Rect(
            BOARD_X + grid_x * CELL_SIZE + 3,
            BOARD_Y + grid_y * CELL_SIZE + 3,
            CELL_SIZE - 6,
            CELL_SIZE - 6,
        )

        if outline_only:
            ghost_surface = pygame.Surface(
                rect.size,
                pygame.SRCALPHA,
            )

            pygame.draw.rect(
                ghost_surface,
                (*color, alpha),
                ghost_surface.get_rect(),
                2,
                border_radius=6,
            )

            surface.blit(
                ghost_surface,
                rect.topleft,
            )
            return

        block_surface = pygame.Surface(
            rect.size,
            pygame.SRCALPHA,
        )

        pygame.draw.rect(
            block_surface,
            (*darken(color, 45), alpha),
            block_surface.get_rect(),
            border_radius=6,
        )

        inner_rect = block_surface.get_rect().inflate(
            -6,
            -6,
        )

        pygame.draw.rect(
            block_surface,
            (*color, alpha),
            inner_rect,
            border_radius=5,
        )

        highlight_rect = pygame.Rect(
            inner_rect.x + 2,
            inner_rect.y + 2,
            max(4, inner_rect.width - 4),
            5,
        )

        pygame.draw.rect(
            block_surface,
            (*lighten(color, 55), alpha),
            highlight_rect,
            border_radius=3,
        )

        surface.blit(
            block_surface,
            rect.topleft,
        )

        if alpha >= 220:
            font = (
                FONT_SMALL
                if len(material["short"]) == 1
                else pygame.font.SysFont(
                    "consolas",
                    12,
                    bold=True,
                )
            )

            draw_text(
                surface,
                material["short"],
                font,
                BACKGROUND,
                rect.centerx,
                rect.centery,
                center=True,
            )

    def draw_current_piece(self, surface):
        for x, y, level in self.current_piece.cells():
            if y >= 0:
                self.draw_block(
                    surface,
                    x,
                    y,
                    level,
                )

    def draw_ghost_piece(self, surface):
        drop_distance = 0

        while self.is_valid_position(
            self.current_piece,
            y_offset=drop_distance + 1,
        ):
            drop_distance += 1

        for x, y, level in self.current_piece.cells(
            y_offset=drop_distance,
        ):
            if y >= 0:
                self.draw_block(
                    surface,
                    x,
                    y,
                    level,
                    alpha=100,
                    outline_only=True,
                )

    def draw_side_panel(self, surface):
        panel_rect = pygame.Rect(
            PANEL_X,
            BOARD_Y,
            PANEL_WIDTH,
            PANEL_HEIGHT,
        )

        pygame.draw.rect(
            surface,
            PANEL_BACKGROUND,
            panel_rect,
            border_radius=16,
        )

        pygame.draw.rect(
            surface,
            DARK_GRAY,
            panel_rect,
            2,
            border_radius=16,
        )

        self.draw_stats(surface)
        self.draw_next_piece(surface)
        self.draw_material_progress(surface)
        self.draw_controls(surface)

    def draw_stats(self, surface):
        draw_text(
            surface,
            "SCORE",
            FONT_SMALL,
            GRAY,
            PANEL_X + 28,
            BOARD_Y + 25,
        )

        draw_text(
            surface,
            f"{self.score:,}",
            FONT_LARGE,
            WHITE,
            PANEL_X + 28,
            BOARD_Y + 48,
        )

        draw_text(
            surface,
            f"Combo: x{self.combo}",
            FONT_MEDIUM,
            YELLOW if self.combo > 0 else GRAY,
            PANEL_X + 28,
            BOARD_Y + 105,
        )

        draw_text(
            surface,
            f"Best combo: x{self.best_combo}",
            FONT_SMALL,
            LIGHT_GRAY,
            PANEL_X + 28,
            BOARD_Y + 140,
        )

        draw_text(
            surface,
            f"Pieces: {self.pieces_placed}",
            FONT_SMALL,
            LIGHT_GRAY,
            PANEL_X + 245,
            BOARD_Y + 112,
        )

        draw_text(
            surface,
            f"Merges: {self.total_merges}",
            FONT_SMALL,
            LIGHT_GRAY,
            PANEL_X + 245,
            BOARD_Y + 140,
        )

        if self.message_timer > 0:
            draw_text(
                surface,
                self.message,
                FONT_SMALL,
                CYAN,
                PANEL_X + 28,
                BOARD_Y + 180,
            )

    def draw_next_piece(self, surface):
        preview_x = PANEL_X + 28
        preview_y = BOARD_Y + 225

        draw_text(
            surface,
            "NEXT PIECE",
            FONT_MEDIUM,
            WHITE,
            preview_x,
            preview_y,
        )

        preview_rect = pygame.Rect(
            preview_x,
            preview_y + 42,
            190,
            145,
        )

        pygame.draw.rect(
            surface,
            BOARD_BACKGROUND,
            preview_rect,
            border_radius=12,
        )

        pygame.draw.rect(
            surface,
            DARK_GRAY,
            preview_rect,
            2,
            border_radius=12,
        )

        shape = SHAPES[self.next_piece.shape_name][0]

        min_x = min(x for x, _ in shape)
        max_x = max(x for x, _ in shape)
        min_y = min(y for _, y in shape)
        max_y = max(y for _, y in shape)

        shape_width = (max_x - min_x + 1) * 27
        shape_height = (max_y - min_y + 1) * 27

        offset_x = (
            preview_rect.centerx - shape_width // 2
        )

        offset_y = (
            preview_rect.centery - shape_height // 2
        )

        for index, (cell_x, cell_y) in enumerate(shape):
            level = self.next_piece.levels[index]
            color = MATERIALS[level]["color"]

            rect = pygame.Rect(
                offset_x + (cell_x - min_x) * 27,
                offset_y + (cell_y - min_y) * 27,
                24,
                24,
            )

            pygame.draw.rect(
                surface,
                darken(color, 35),
                rect,
                border_radius=5,
            )

            pygame.draw.rect(
                surface,
                color,
                rect.inflate(-5, -5),
                border_radius=4,
            )

    def draw_material_progress(self, surface):
        start_x = PANEL_X + 250
        start_y = BOARD_Y + 225

        draw_text(
            surface,
            "MATERIALS",
            FONT_MEDIUM,
            WHITE,
            start_x,
            start_y,
        )

        for index, material in enumerate(MATERIALS):
            y = start_y + 45 + index * 25

            unlocked = index <= self.highest_material

            color = (
                material["color"]
                if unlocked
                else DARK_GRAY
            )

            pygame.draw.rect(
                surface,
                color,
                (
                    start_x,
                    y,
                    22,
                    22,
                ),
                border_radius=5,
            )

            draw_text(
                surface,
                material["name"],
                FONT_SMALL,
                WHITE if unlocked else GRAY,
                start_x + 38,
                y + 2,
            )

    def draw_controls(self, surface):
        # The bottom part of the side panel is split into two columns.
        # Everything stays inside PANEL_HEIGHT without overlapping.
        section_y = BOARD_Y + 455
        left_x = PANEL_X + 20
        right_x = PANEL_X + 320
        bottom_y = BOARD_Y + PANEL_HEIGHT - 24

        pygame.draw.line(
            surface,
            DARK_GRAY,
            (left_x, section_y),
            (PANEL_X + PANEL_WIDTH - 28, section_y),
            2,
        )

        # Left column: rules
        draw_text(
            surface,
            "HOW TO PLAY",
            FONT_MEDIUM,
            WHITE,
            left_x,
            section_y + 22,
        )

        instructions = [
            "Connect equal materials.",
            "Two or more blocks merge.",
            "Gravity can start chains.",
            "Create Diamond to win.",
        ]

        for index, instruction in enumerate(instructions):
            draw_text(
                surface,
                f"• {instruction}",
                FONT_SMALL,
                LIGHT_GRAY,
                left_x,
                section_y + 62 + index * 31,
            )

        # Vertical separator
        # pygame.draw.line(
        #     surface,
        #     DARK_GRAY,
        #     (PANEL_X + 245, section_y + 20),
        #     (PANEL_X + 245, bottom_y),
        #     2,
        # )

        # Right column: controls
        draw_text(
            surface,
            "CONTROLS",
            FONT_MEDIUM,
            WHITE,
            right_x,
            section_y + 22,
        )

        controls = [
            ("A / D", "Move"),
            ("W / Up", "Rotate"),
            ("S / Down", "Soft drop"),
            ("SPACE", "Hard drop"),
            ("R", "Restart"),
        ]

        for index, (key, action) in enumerate(controls):
            row_y = section_y + 62 + index * 31

            draw_text(
                surface,
                key,
                FONT_SMALL,
                CYAN,
                right_x,
                row_y,
            )

            draw_text(
                surface,
                action,
                FONT_SMALL,
                GRAY,
                right_x + 105,
                row_y,
            )

    def draw_particles(self):
        for particle in self.particles:
            life_ratio = clamp(
                particle.life / particle.max_life,
                0,
                1,
            )

            radius = max(
                1,
                int(particle.size * life_ratio),
            )

            pygame.draw.circle(
                SCREEN,
                particle.color,
                (
                    int(particle.x),
                    int(particle.y),
                ),
                radius,
            )

    def draw_floating_texts(self):
        for item in self.floating_texts:
            alpha_ratio = clamp(
                item.life / item.max_life,
                0,
                1,
            )

            text_surface = FONT_MEDIUM.render(
                item.text,
                True,
                item.color,
            )

            text_surface.set_alpha(
                int(255 * alpha_ratio)
            )

            rect = text_surface.get_rect(
                center=(
                    int(item.x),
                    int(item.y),
                )
            )

            SCREEN.blit(text_surface, rect)

    def draw_game_over(self):
        overlay = pygame.Surface(
            (WINDOW_WIDTH, WINDOW_HEIGHT),
            pygame.SRCALPHA,
        )

        overlay.fill((2, 4, 12, 225))
        SCREEN.blit(overlay, (0, 0))

        card = pygame.Rect(
            WINDOW_WIDTH // 2 - 330,
            WINDOW_HEIGHT // 2 - 280,
            660,
            560,
        )

        pygame.draw.rect(
            SCREEN,
            PANEL_BACKGROUND,
            card,
            border_radius=24,
        )

        pygame.draw.rect(
            SCREEN,
            RED,
            card,
            3,
            border_radius=24,
        )

        draw_text(
            SCREEN,
            "FUSION ENDED",
            FONT_TITLE,
            RED,
            card.centerx,
            card.y + 75,
            center=True,
        )

        highest = MATERIALS[self.highest_material]

        statistics = [
            f"Final score: {self.score:,}",
            f"Highest material: {highest['name']}",
            f"Best combo: x{self.best_combo}",
            f"Total merges: {self.total_merges}",
            f"Pieces placed: {self.pieces_placed}",
            f"Survival time: {self.game_over_time:.1f}s",
        ]

        for index, statistic in enumerate(statistics):
            draw_text(
                SCREEN,
                statistic,
                FONT_MEDIUM,
                WHITE,
                card.centerx,
                card.y + 170 + index * 48,
                center=True,
            )

        if self.highest_material == len(MATERIALS) - 1:
            final_message = "You created Diamond!"
            final_color = CYAN
        else:
            final_message = "Can you reach Diamond?"
            final_color = YELLOW

        draw_text(
            SCREEN,
            final_message,
            FONT_MEDIUM,
            final_color,
            card.centerx,
            card.bottom - 100,
            center=True,
        )

        draw_text(
            SCREEN,
            "Press ENTER to play again",
            FONT_MEDIUM,
            CYAN,
            card.centerx,
            card.bottom - 52,
            center=True,
        )


# =========================================================
# MAIN LOOP
# =========================================================

def main():
    game = FusionTetris()
    running = True

    while running:
        dt = CLOCK.tick(FPS) / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                game.handle_event(event)

        game.update(dt)
        game.draw()

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
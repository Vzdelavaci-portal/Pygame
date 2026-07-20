import math
import random
import sys
from dataclasses import dataclass

import pygame


# =========================================================
# INITIALIZATION
# =========================================================

pygame.init()

WIDTH = 1100
HEIGHT = 760
FPS = 60

TOP_PANEL_HEIGHT = 80
PLAY_TOP = TOP_PANEL_HEIGHT
PLAY_BOTTOM = HEIGHT - 20

CELL_SIZE = 20
COLS = WIDTH // CELL_SIZE
ROWS = (PLAY_BOTTOM - PLAY_TOP) // CELL_SIZE

SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Evolution Snake")

CLOCK = pygame.time.Clock()

FONT_SMALL = pygame.font.SysFont("consolas", 18)
FONT_MEDIUM = pygame.font.SysFont("consolas", 26, bold=True)
FONT_LARGE = pygame.font.SysFont("consolas", 46, bold=True)
FONT_TITLE = pygame.font.SysFont("consolas", 64, bold=True)


# =========================================================
# COLORS
# =========================================================

BACKGROUND = (5, 8, 18)
GRID_COLOR = (15, 23, 42)

WHITE = (240, 245, 255)
GRAY = (125, 140, 165)
DARK_GRAY = (38, 48, 68)

CYAN = (40, 240, 255)
GREEN = (70, 255, 130)
BLUE = (70, 150, 255)
PURPLE = (190, 80, 255)
GOLD = (255, 205, 55)
RED = (255, 70, 90)
ORANGE = (255, 140, 45)

CARD_BG = (18, 25, 45)
CARD_HOVER = (28, 42, 70)


# =========================================================
# DATA CLASSES
# =========================================================

@dataclass
class DNA:
    x: int
    y: int
    dna_type: str
    pulse: float = 0.0


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
    color: tuple


# =========================================================
# MUTATIONS
# =========================================================

MUTATIONS = {
    "Swift": {
        "icon": ">>",
        "description": "Snake moves 15% faster.",
        "color": ORANGE,
    },
    "Magnet": {
        "icon": "M",
        "description": "Nearby DNA is pulled toward you.",
        "color": PURPLE,
    },
    "Ghost": {
        "icon": "G",
        "description": "Press G to pass through your tail.",
        "color": CYAN,
    },
    "Turtle": {
        "icon": "T",
        "description": "Survive one fatal collision.",
        "color": GREEN,
    },
    "Dash": {
        "icon": "D",
        "description": "Press SPACE for a short speed boost.",
        "color": BLUE,
    },
    "Lucky DNA": {
        "icon": "L",
        "description": "Higher chance of valuable DNA.",
        "color": GOLD,
    },
}


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))


def grid_to_pixel(position):
    x, y = position
    return (
        x * CELL_SIZE + CELL_SIZE // 2,
        PLAY_TOP + y * CELL_SIZE + CELL_SIZE // 2,
    )


def draw_text(text, font, color, x, y, center=False):
    surface = font.render(text, True, color)
    rect = surface.get_rect()

    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)

    SCREEN.blit(surface, rect)
    return rect


def draw_glow_circle(surface, position, radius, color, glow_strength=3):
    x, y = position

    for layer in range(glow_strength, 0, -1):
        glow_radius = radius + layer * 5
        alpha = max(10, 45 - layer * 8)

        glow_surface = pygame.Surface(
            (glow_radius * 2, glow_radius * 2),
            pygame.SRCALPHA,
        )

        pygame.draw.circle(
            glow_surface,
            (*color, alpha),
            (glow_radius, glow_radius),
            glow_radius,
        )

        surface.blit(
            glow_surface,
            (x - glow_radius, y - glow_radius),
        )

    pygame.draw.circle(surface, color, position, radius)


# =========================================================
# PARTICLES
# =========================================================

def create_particles(particles, x, y, color, amount=15):
    for _ in range(amount):
        angle = random.uniform(0, math.tau)
        speed = random.uniform(40, 150)

        particles.append(
            Particle(
                x=x,
                y=y,
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed,
                life=random.uniform(0.35, 0.8),
                max_life=0.8,
                size=random.uniform(2, 6),
                color=color,
            )
        )


def update_particles(particles, dt):
    for particle in particles[:]:
        particle.x += particle.vx * dt
        particle.y += particle.vy * dt

        particle.vx *= 0.97
        particle.vy *= 0.97

        particle.life -= dt

        if particle.life <= 0:
            particles.remove(particle)


def draw_particles(particles):
    for particle in particles:
        alpha_ratio = clamp(particle.life / particle.max_life, 0, 1)
        radius = max(1, int(particle.size * alpha_ratio))

        pygame.draw.circle(
            SCREEN,
            particle.color,
            (int(particle.x), int(particle.y)),
            radius,
        )


# =========================================================
# FLOATING TEXT
# =========================================================

def update_floating_texts(texts, dt):
    for item in texts[:]:
        item.y -= 35 * dt
        item.life -= dt

        if item.life <= 0:
            texts.remove(item)


def draw_floating_texts(texts):
    for item in texts:
        draw_text(
            item.text,
            FONT_SMALL,
            item.color,
            int(item.x),
            int(item.y),
            center=True,
        )


# =========================================================
# DNA
# =========================================================

def choose_dna_type(lucky_level):
    green_chance = max(45, 78 - lucky_level * 8)
    blue_chance = min(40, 18 + lucky_level * 5)
    gold_chance = min(15, 4 + lucky_level * 3)

    roll = random.uniform(0, green_chance + blue_chance + gold_chance)

    if roll < green_chance:
        return "green"

    if roll < green_chance + blue_chance:
        return "blue"

    return "gold"


def create_dna(snake, lucky_level):
    for _ in range(100):
        x = random.randint(1, COLS - 2)
        y = random.randint(1, ROWS - 2)

        if (x, y) not in snake:
            return DNA(
                x=x,
                y=y,
                dna_type=choose_dna_type(lucky_level),
            )

    return DNA(5, 5, "green")


def dna_value(dna_type):
    if dna_type == "blue":
        return 5

    if dna_type == "gold":
        return 10

    return 1


def dna_color(dna_type):
    if dna_type == "blue":
        return BLUE

    if dna_type == "gold":
        return GOLD

    return GREEN


# =========================================================
# GAME
# =========================================================

class Game:
    def __init__(self):
        self.reset()

    def reset(self):
        center_x = COLS // 2
        center_y = ROWS // 2

        self.snake = [
            (center_x, center_y),
            (center_x - 1, center_y),
            (center_x - 2, center_y),
            (center_x - 3, center_y),
        ]

        self.direction = (1, 0)
        self.next_direction = (1, 0)

        self.dna = create_dna(self.snake, 0)

        self.score = 0
        self.total_dna = 0
        self.next_evolution = 20

        self.base_move_delay = 0.105
        self.move_delay = self.base_move_delay
        self.move_timer = 0.0

        self.state = "playing"

        self.mutations = []
        self.mutation_levels = {}
        self.mutation_choices = []

        self.ghost_active = False
        self.ghost_timer = 0.0
        self.ghost_cooldown = 0.0

        self.dash_active = False
        self.dash_timer = 0.0
        self.dash_cooldown = 0.0

        self.turtle_shields = 0

        self.particles = []
        self.floating_texts = []

        self.start_ticks = pygame.time.get_ticks()
        self.end_time = 0.0

        self.screen_shake = 0.0
        self.message = "Collect DNA and evolve!"

    # -----------------------------------------------------
    # Mutation helpers
    # -----------------------------------------------------

    def mutation_level(self, name):
        return self.mutation_levels.get(name, 0)

    def has_mutation(self, name):
        return self.mutation_level(name) > 0

    def generate_mutation_choices(self):
        names = list(MUTATIONS.keys())

        weights = []

        for name in names:
            level = self.mutation_level(name)

            if level == 0:
                weights.append(5)
            elif level < 3:
                weights.append(3)
            else:
                weights.append(1)

        choices = []

        while len(choices) < 3:
            selected = random.choices(names, weights=weights, k=1)[0]

            if selected not in choices:
                choices.append(selected)

        self.mutation_choices = choices

    def apply_mutation(self, name):
        self.mutation_levels[name] = self.mutation_level(name) + 1

        if name not in self.mutations:
            self.mutations.append(name)

        level = self.mutation_level(name)

        if name == "Swift":
            self.base_move_delay = max(0.05, self.base_move_delay * 0.85)
            self.move_delay = self.base_move_delay

        elif name == "Turtle":
            self.turtle_shields += 1

        self.message = f"{name} evolved to level {level}"
        self.state = "playing"

    # -----------------------------------------------------
    # Input
    # -----------------------------------------------------

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if self.state == "playing":
                self.handle_playing_keys(event.key)

            elif self.state == "evolution":
                if event.key in (pygame.K_1, pygame.K_KP1):
                    self.choose_mutation(0)

                elif event.key in (pygame.K_2, pygame.K_KP2):
                    self.choose_mutation(1)

                elif event.key in (pygame.K_3, pygame.K_KP3):
                    self.choose_mutation(2)

            elif self.state == "game_over":
                if event.key == pygame.K_RETURN:
                    self.reset()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.state == "evolution" and event.button == 1:
                self.handle_mutation_click(event.pos)

    def handle_playing_keys(self, key):
        dx, dy = self.direction

        if key in (pygame.K_UP, pygame.K_w) and dy != 1:
            self.next_direction = (0, -1)

        elif key in (pygame.K_DOWN, pygame.K_s) and dy != -1:
            self.next_direction = (0, 1)

        elif key in (pygame.K_LEFT, pygame.K_a) and dx != 1:
            self.next_direction = (-1, 0)

        elif key in (pygame.K_RIGHT, pygame.K_d) and dx != -1:
            self.next_direction = (1, 0)

        elif key == pygame.K_SPACE:
            self.activate_dash()

        elif key == pygame.K_g:
            self.activate_ghost()

    def activate_dash(self):
        if not self.has_mutation("Dash"):
            return

        if self.dash_active or self.dash_cooldown > 0:
            return

        level = self.mutation_level("Dash")

        self.dash_active = True
        self.dash_timer = 0.8 + level * 0.2
        self.dash_cooldown = max(3.0, 7.0 - level)

        self.message = "Dash activated!"

    def activate_ghost(self):
        if not self.has_mutation("Ghost"):
            return

        if self.ghost_active or self.ghost_cooldown > 0:
            return

        level = self.mutation_level("Ghost")

        self.ghost_active = True
        self.ghost_timer = 3.0 + level
        self.ghost_cooldown = max(6.0, 14.0 - level * 2)

        self.message = "Ghost mode activated!"

    # -----------------------------------------------------
    # Update
    # -----------------------------------------------------

    def update(self, dt):
        update_particles(self.particles, dt)
        update_floating_texts(self.floating_texts, dt)

        self.screen_shake = max(0, self.screen_shake - 25 * dt)

        if self.state != "playing":
            return

        self.update_abilities(dt)
        self.update_magnet(dt)

        current_delay = self.base_move_delay

        if self.dash_active:
            current_delay *= 0.45

        self.move_timer += dt

        if self.move_timer >= current_delay:
            self.move_timer = 0
            self.move_snake()

    def update_abilities(self, dt):
        if self.ghost_active:
            self.ghost_timer -= dt

            if self.ghost_timer <= 0:
                self.ghost_active = False
                self.message = "Ghost mode ended"

        elif self.ghost_cooldown > 0:
            self.ghost_cooldown = max(0, self.ghost_cooldown - dt)

        if self.dash_active:
            self.dash_timer -= dt

            if self.dash_timer <= 0:
                self.dash_active = False
                self.message = "Dash ended"

        elif self.dash_cooldown > 0:
            self.dash_cooldown = max(0, self.dash_cooldown - dt)

    def update_magnet(self, dt):
        if not self.has_mutation("Magnet"):
            return

        head_x, head_y = self.snake[0]
        dx = head_x - self.dna.x
        dy = head_y - self.dna.y

        distance = math.sqrt(dx * dx + dy * dy)

        magnet_range = 4 + self.mutation_level("Magnet") * 2

        if distance <= magnet_range and distance > 0:
            chance = min(1.0, dt * (7 + self.mutation_level("Magnet") * 2))

            if random.random() < chance:
                if abs(dx) > abs(dy):
                    self.dna.x += 1 if dx > 0 else -1
                else:
                    self.dna.y += 1 if dy > 0 else -1

                self.dna.x = clamp(self.dna.x, 1, COLS - 2)
                self.dna.y = clamp(self.dna.y, 1, ROWS - 2)

    # -----------------------------------------------------
    # Snake movement
    # -----------------------------------------------------

    def move_snake(self):
        self.direction = self.next_direction

        head_x, head_y = self.snake[0]
        dx, dy = self.direction

        new_head = (head_x + dx, head_y + dy)

        wall_collision = (
            new_head[0] < 0
            or new_head[0] >= COLS
            or new_head[1] < 0
            or new_head[1] >= ROWS
        )

        body_collision = (
            new_head in self.snake[:-1]
            and not self.ghost_active
        )

        if wall_collision or body_collision:
            if self.turtle_shields > 0:
                self.turtle_shields -= 1
                self.handle_turtle_save()
                return

            self.game_over()
            return

        self.snake.insert(0, new_head)

        if new_head == (self.dna.x, self.dna.y):
            self.collect_dna()
        else:
            self.snake.pop()

    def handle_turtle_save(self):
        center_x = COLS // 2
        center_y = ROWS // 2

        length = max(4, len(self.snake) - 3)

        self.snake = [
            (center_x - index, center_y)
            for index in range(length)
        ]

        self.direction = (1, 0)
        self.next_direction = (1, 0)

        self.screen_shake = 12
        self.message = "Turtle shield saved you!"

        x, y = grid_to_pixel((center_x, center_y))
        create_particles(self.particles, x, y, GREEN, 35)

    def collect_dna(self):
        value = dna_value(self.dna.dna_type)
        color = dna_color(self.dna.dna_type)

        lucky_level = self.mutation_level("Lucky DNA")

        if lucky_level > 0 and random.random() < 0.08 * lucky_level:
            value *= 2

        self.score += value
        self.total_dna += value

        growth = min(value, 5)

        for _ in range(growth - 1):
            self.snake.append(self.snake[-1])

        x, y = grid_to_pixel((self.dna.x, self.dna.y))

        create_particles(
            self.particles,
            x,
            y,
            color,
            18 if value < 10 else 35,
        )

        self.floating_texts.append(
            FloatingText(
                text=f"+{value} DNA",
                x=x,
                y=y,
                life=1.0,
                color=color,
            )
        )

        self.dna = create_dna(
            self.snake,
            self.mutation_level("Lucky DNA"),
        )

        if self.total_dna >= self.next_evolution:
            self.next_evolution += 20
            self.generate_mutation_choices()
            self.state = "evolution"

    def game_over(self):
        self.state = "game_over"
        self.end_time = self.get_survival_time()

        x, y = grid_to_pixel(self.snake[0])
        create_particles(self.particles, x, y, RED, 55)

    # -----------------------------------------------------
    # Evolution screen
    # -----------------------------------------------------

    def get_mutation_card_rects(self):
        card_width = 290
        card_height = 300
        gap = 30

        total_width = card_width * 3 + gap * 2
        start_x = (WIDTH - total_width) // 2
        y = 250

        return [
            pygame.Rect(
                start_x + index * (card_width + gap),
                y,
                card_width,
                card_height,
            )
            for index in range(3)
        ]

    def handle_mutation_click(self, mouse_position):
        for index, rect in enumerate(self.get_mutation_card_rects()):
            if rect.collidepoint(mouse_position):
                self.choose_mutation(index)
                return

    def choose_mutation(self, index):
        if 0 <= index < len(self.mutation_choices):
            self.apply_mutation(self.mutation_choices[index])

    # -----------------------------------------------------
    # Time
    # -----------------------------------------------------

    def get_survival_time(self):
        if self.state == "game_over":
            return self.end_time

        return (pygame.time.get_ticks() - self.start_ticks) / 1000

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

        world_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

        self.draw_grid(world_surface)
        self.draw_dna(world_surface)
        self.draw_snake(world_surface)

        SCREEN.blit(world_surface, (shake_x, shake_y))

        draw_particles(self.particles)
        draw_floating_texts(self.floating_texts)
        self.draw_top_panel()

        if self.state == "evolution":
            self.draw_evolution_screen()

        elif self.state == "game_over":
            self.draw_game_over()

    def draw_grid(self, surface):
        for x in range(0, WIDTH, CELL_SIZE):
            pygame.draw.line(
                surface,
                GRID_COLOR,
                (x, PLAY_TOP),
                (x, PLAY_TOP + ROWS * CELL_SIZE),
            )

        for row in range(ROWS + 1):
            y = PLAY_TOP + row * CELL_SIZE

            pygame.draw.line(
                surface,
                GRID_COLOR,
                (0, y),
                (WIDTH, y),
            )

    def draw_dna(self, surface):
        self.dna.pulse += 0.08

        x, y = grid_to_pixel((self.dna.x, self.dna.y))
        color = dna_color(self.dna.dna_type)

        pulse_radius = 6 + int(math.sin(self.dna.pulse) * 2)

        draw_glow_circle(
            surface,
            (x, y),
            pulse_radius,
            color,
            4,
        )

        pygame.draw.circle(
            surface,
            WHITE,
            (x - 3, y - 3),
            2,
        )

        pygame.draw.circle(
            surface,
            WHITE,
            (x + 3, y + 3),
            2,
        )

        pygame.draw.line(
            surface,
            WHITE,
            (x - 2, y - 2),
            (x + 2, y + 2),
            2,
        )

    def draw_snake(self, surface):
        ghost_alpha = 120 if self.ghost_active else 255

        for index, segment in enumerate(self.snake):
            x, y = grid_to_pixel(segment)

            ratio = 1 - index / max(1, len(self.snake))

            if self.dash_active:
                base_color = BLUE

            elif self.ghost_active:
                base_color = CYAN

            else:
                base_color = (
                    int(40 + 40 * ratio),
                    int(180 + 75 * ratio),
                    int(160 + 95 * ratio),
                )

            radius = 8 if index == 0 else 7

            segment_surface = pygame.Surface(
                (CELL_SIZE * 2, CELL_SIZE * 2),
                pygame.SRCALPHA,
            )

            local_center = (CELL_SIZE, CELL_SIZE)

            pygame.draw.circle(
                segment_surface,
                (*base_color, ghost_alpha),
                local_center,
                radius,
            )

            surface.blit(
                segment_surface,
                (x - CELL_SIZE, y - CELL_SIZE),
            )

            if index == 0:
                self.draw_snake_head(surface, x, y)

        if self.has_mutation("Magnet"):
            self.draw_magnet_effect(surface)

        if self.turtle_shields > 0:
            self.draw_turtle_effect(surface)

    def draw_snake_head(self, surface, x, y):
        dx, dy = self.direction

        if dx != 0:
            eye_1 = (x + dx * 3, y - 4)
            eye_2 = (x + dx * 3, y + 4)
        else:
            eye_1 = (x - 4, y + dy * 3)
            eye_2 = (x + 4, y + dy * 3)

        pygame.draw.circle(surface, WHITE, eye_1, 2)
        pygame.draw.circle(surface, WHITE, eye_2, 2)

    def draw_magnet_effect(self, surface):
        head_x, head_y = grid_to_pixel(self.snake[0])

        radius = (
            32
            + self.mutation_level("Magnet") * 7
            + math.sin(pygame.time.get_ticks() * 0.005) * 4
        )

        pygame.draw.circle(
            surface,
            (*PURPLE, 100),
            (head_x, head_y),
            int(radius),
            2,
        )

    def draw_turtle_effect(self, surface):
        head_x, head_y = grid_to_pixel(self.snake[0])

        pygame.draw.circle(
            surface,
            GREEN,
            (head_x, head_y),
            13,
            2,
        )

    def draw_top_panel(self):
        pygame.draw.rect(
            SCREEN,
            (9, 14, 28),
            (0, 0, WIDTH, TOP_PANEL_HEIGHT),
        )

        pygame.draw.line(
            SCREEN,
            CYAN,
            (0, TOP_PANEL_HEIGHT - 1),
            (WIDTH, TOP_PANEL_HEIGHT - 1),
            2,
        )

        draw_text(
            "EVOLUTION SNAKE",
            FONT_MEDIUM,
            CYAN,
            20,
            12,
        )

        draw_text(
            f"DNA: {self.total_dna}",
            FONT_SMALL,
            WHITE,
            22,
            48,
        )

        evolution_progress = self.total_dna % 20

        if evolution_progress == 0 and self.total_dna > 0:
            evolution_progress = 20

        progress_ratio = evolution_progress / 20

        bar_x = 145
        bar_y = 49
        bar_width = 190
        bar_height = 14

        pygame.draw.rect(
            SCREEN,
            DARK_GRAY,
            (bar_x, bar_y, bar_width, bar_height),
            border_radius=7,
        )

        pygame.draw.rect(
            SCREEN,
            PURPLE,
            (
                bar_x,
                bar_y,
                int(bar_width * progress_ratio),
                bar_height,
            ),
            border_radius=7,
        )

        draw_text(
            f"Next evolution: {evolution_progress}/20",
            FONT_SMALL,
            GRAY,
            355,
            45,
        )

        draw_text(
            f"Length: {len(self.snake)}",
            FONT_SMALL,
            WHITE,
            580,
            16,
        )

        draw_text(
            f"Time: {self.get_survival_time():.1f}s",
            FONT_SMALL,
            WHITE,
            580,
            45,
        )

        mutation_text = (
            ", ".join(
                f"{name} {self.mutation_level(name)}"
                for name in self.mutations
            )
            if self.mutations
            else "No mutations"
        )

        draw_text(
            mutation_text,
            FONT_SMALL,
            GRAY,
            750,
            15,
        )

        draw_text(
            self.message,
            FONT_SMALL,
            WHITE,
            750,
            46,
        )

        self.draw_ability_status()

    def draw_ability_status(self):
        y = HEIGHT - 50

        if self.has_mutation("Dash"):
            status = (
                "READY"
                if self.dash_cooldown <= 0
                else f"{self.dash_cooldown:.1f}s"
            )

            draw_text(
                f"SPACE Dash: {status}",
                FONT_SMALL,
                BLUE,
                20,
                y,
            )

        if self.has_mutation("Ghost"):
            status = (
                "READY"
                if self.ghost_cooldown <= 0
                else f"{self.ghost_cooldown:.1f}s"
            )

            draw_text(
                f"G Ghost: {status}",
                FONT_SMALL,
                CYAN,
                220,
                y,
            )

        if self.turtle_shields > 0:
            draw_text(
                f"Turtle shields: {self.turtle_shields}",
                FONT_SMALL,
                GREEN,
                420,
                y,
            )

    def draw_evolution_screen(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((2, 4, 12, 225))
        SCREEN.blit(overlay, (0, 0))

        draw_text(
            "CHOOSE YOUR EVOLUTION",
            FONT_LARGE,
            PURPLE,
            WIDTH // 2,
            120,
            center=True,
        )

        draw_text(
            "Select one mutation with the mouse or press 1, 2 or 3",
            FONT_SMALL,
            WHITE,
            WIDTH // 2,
            180,
            center=True,
        )

        mouse_position = pygame.mouse.get_pos()
        card_rects = self.get_mutation_card_rects()

        for index, mutation_name in enumerate(self.mutation_choices):
            rect = card_rects[index]
            hovered = rect.collidepoint(mouse_position)

            info = MUTATIONS[mutation_name]
            color = info["color"]

            pygame.draw.rect(
                SCREEN,
                CARD_HOVER if hovered else CARD_BG,
                rect,
                border_radius=18,
            )

            pygame.draw.rect(
                SCREEN,
                color,
                rect,
                3 if hovered else 2,
                border_radius=18,
            )

            draw_text(
                str(index + 1),
                FONT_SMALL,
                GRAY,
                rect.x + 18,
                rect.y + 16,
            )

            draw_glow_circle(
                SCREEN,
                (rect.centerx, rect.y + 78),
                26,
                color,
                3,
            )

            draw_text(
                info["icon"],
                FONT_MEDIUM,
                BACKGROUND,
                rect.centerx,
                rect.y + 78,
                center=True,
            )

            draw_text(
                mutation_name,
                FONT_MEDIUM,
                color,
                rect.centerx,
                rect.y + 135,
                center=True,
            )

            next_level = self.mutation_level(mutation_name) + 1

            draw_text(
                f"Level {next_level}",
                FONT_SMALL,
                WHITE,
                rect.centerx,
                rect.y + 175,
                center=True,
            )

            description_lines = self.wrap_text(
                info["description"],
                FONT_SMALL,
                rect.width - 40,
            )

            for line_index, line in enumerate(description_lines):
                draw_text(
                    line,
                    FONT_SMALL,
                    GRAY,
                    rect.centerx,
                    rect.y + 220 + line_index * 25,
                    center=True,
                )

    def draw_game_over(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((2, 4, 12, 225))
        SCREEN.blit(overlay, (0, 0))

        draw_text(
            "EVOLUTION ENDED",
            FONT_TITLE,
            RED,
            WIDTH // 2,
            170,
            center=True,
        )

        draw_text(
            f"DNA collected: {self.total_dna}",
            FONT_MEDIUM,
            WHITE,
            WIDTH // 2,
            300,
            center=True,
        )

        draw_text(
            f"Final length: {len(self.snake)}",
            FONT_MEDIUM,
            WHITE,
            WIDTH // 2,
            350,
            center=True,
        )

        draw_text(
            f"Survival time: {self.end_time:.1f} seconds",
            FONT_MEDIUM,
            WHITE,
            WIDTH // 2,
            400,
            center=True,
        )

        draw_text(
            f"Mutations obtained: {len(self.mutations)}",
            FONT_MEDIUM,
            WHITE,
            WIDTH // 2,
            450,
            center=True,
        )

        mutation_summary = (
            ", ".join(
                f"{name} Lv.{self.mutation_level(name)}"
                for name in self.mutations
            )
            if self.mutations
            else "No mutations"
        )

        wrapped = self.wrap_text(
            mutation_summary,
            FONT_SMALL,
            850,
        )

        for index, line in enumerate(wrapped):
            draw_text(
                line,
                FONT_SMALL,
                GRAY,
                WIDTH // 2,
                500 + index * 26,
                center=True,
            )

        draw_text(
            "Press ENTER to evolve again",
            FONT_MEDIUM,
            CYAN,
            WIDTH // 2,
            620,
            center=True,
        )

    @staticmethod
    def wrap_text(text, font, max_width):
        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            test_line = (
                word if not current_line else f"{current_line} {word}"
            )

            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)

                current_line = word

        if current_line:
            lines.append(current_line)

        return lines


# =========================================================
# MAIN LOOP
# =========================================================

def main():
    game = Game()
    running = True

    while running:
        dt = CLOCK.tick(FPS) / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            game.handle_event(event)

        game.update(dt)
        game.draw()

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
import math
import random
import sys
from dataclasses import dataclass

import pygame


# =========================================================
# INITIALIZATION
# =========================================================

pygame.init()

WIDTH, HEIGHT = 1100, 760
FPS = 60

PLAYFIELD = pygame.Rect(40, 90, 760, 620)
PANEL = pygame.Rect(830, 90, 230, 620)

SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Arkanoid Factory")

CLOCK = pygame.time.Clock()

FONT_SMALL = pygame.font.SysFont("consolas", 18)
FONT_MEDIUM = pygame.font.SysFont("consolas", 24, bold=True)
FONT_LARGE = pygame.font.SysFont("consolas", 42, bold=True)
FONT_TITLE = pygame.font.SysFont("consolas", 54, bold=True)


# =========================================================
# COLORS
# =========================================================

BACKGROUND = (6, 9, 20)
PANEL_BG = (12, 18, 34)
FIELD_BG = (10, 15, 30)
GRID = (20, 30, 54)

WHITE = (240, 245, 255)
GRAY = (145, 155, 180)
DARK_GRAY = (44, 55, 78)

CYAN = (45, 235, 255)
GREEN = (70, 240, 145)
YELLOW = (255, 215, 75)
RED = (255, 75, 95)
PURPLE = (185, 95, 255)
BLUE = (75, 145, 255)


# =========================================================
# MATERIALS
# =========================================================

MATERIALS = {
    "iron": {
        "name": "Iron",
        "color": (150, 175, 205),
    },
    "copper": {
        "name": "Copper",
        "color": (215, 115, 60),
    },
    "crystal": {
        "name": "Crystal",
        "color": (60, 240, 220),
    },
}


# =========================================================
# DATA CLASSES
# =========================================================

@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    life: float
    color: tuple
    size: float


@dataclass
class Drop:
    x: float
    y: float
    material: str
    speed: float = 180.0
    radius: int = 9


# =========================================================
# HELPERS
# =========================================================

def clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))


def draw_text(surface, text, font, color, x, y, center=False):
    rendered = font.render(text, True, color)
    rect = rendered.get_rect()

    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)

    surface.blit(rendered, rect)
    return rect


def draw_glow_circle(surface, position, radius, color):
    for extra, alpha in ((16, 25), (10, 40), (5, 70)):
        glow = pygame.Surface(
            ((radius + extra) * 2, (radius + extra) * 2),
            pygame.SRCALPHA,
        )

        pygame.draw.circle(
            glow,
            (*color, alpha),
            (radius + extra, radius + extra),
            radius + extra,
        )

        surface.blit(
            glow,
            (
                position[0] - radius - extra,
                position[1] - radius - extra,
            ),
        )

    pygame.draw.circle(surface, color, position, radius)


# =========================================================
# BRICK
# =========================================================

class Brick:
    WIDTH = 68
    HEIGHT = 26

    def __init__(self, x, y, material, hp=1, special=None):
        self.rect = pygame.Rect(x, y, self.WIDTH, self.HEIGHT)
        self.material = material
        self.hp = hp
        self.max_hp = hp
        self.special = special
        self.hit_flash = 0.0

    def hit(self):
        self.hp -= 1
        self.hit_flash = 0.12
        return self.hp <= 0

    def update(self, dt):
        self.hit_flash = max(0.0, self.hit_flash - dt)

    def draw(self, surface):
        color = MATERIALS[self.material]["color"]

        if self.special == "bomb":
            color = RED
        elif self.special == "energy":
            color = PURPLE

        draw_color = WHITE if self.hit_flash > 0 else color

        pygame.draw.rect(
            surface,
            draw_color,
            self.rect,
            border_radius=7,
        )

        pygame.draw.rect(
            surface,
            DARK_GRAY,
            self.rect,
            2,
            border_radius=7,
        )

        highlight = pygame.Rect(
            self.rect.x + 5,
            self.rect.y + 4,
            self.rect.width - 10,
            5,
        )

        pygame.draw.rect(
            surface,
            tuple(min(255, channel + 55) for channel in draw_color),
            highlight,
            border_radius=3,
        )

        if self.special == "bomb":
            label = "B"
        elif self.special == "energy":
            label = "E"
        else:
            label = self.material[0].upper()

        draw_text(
            surface,
            label,
            FONT_SMALL,
            BACKGROUND,
            self.rect.centerx,
            self.rect.centery,
            center=True,
        )


# =========================================================
# GAME
# =========================================================

class ArkanoidFactory:
    def __init__(self):
        self.reset_all()

    def reset_all(self):
        self.level = 1
        self.money = 0

        self.inventory = {
            "iron": 0,
            "copper": 0,
            "crystal": 0,
        }

        self.paddle_width = 130
        self.ball_speed_bonus = 0
        self.magnet_level = 0
        self.multiball_level = 0

        self.reset_level()

    def reset_level(self):
        self.state = "playing"
        self.mode = "catch"

        self.paddle = pygame.Rect(
            PLAYFIELD.centerx - self.paddle_width // 2,
            PLAYFIELD.bottom - 45,
            self.paddle_width,
            18,
        )

        self.balls = []
        self.spawn_ball(stuck=True)

        self.bricks = []
        self.drops = []
        self.particles = []

        self.combo = 0
        self.best_combo = 0
        self.score = 0
        self.lives = 3

        self.message = "Catch resources and complete the order."
        self.message_timer = 3.0

        self.order = self.create_order()
        self.build_level()

    # -----------------------------------------------------
    # LEVEL / ORDER
    # -----------------------------------------------------

    def create_order(self):
        base = 5 + self.level * 2

        return {
            "iron": base + random.randint(1, 4),
            "copper": max(3, base - 1 + random.randint(0, 3)),
            "crystal": max(1, self.level // 2 + random.randint(1, 2)),
        }

    def build_level(self):
        rows = min(8, 5 + self.level // 2)
        cols = 10
        gap = 6

        total_width = cols * Brick.WIDTH + (cols - 1) * gap
        start_x = PLAYFIELD.centerx - total_width // 2
        start_y = PLAYFIELD.top + 35

        for row in range(rows):
            for col in range(cols):
                roll = random.random()

                if roll < 0.56:
                    material = "iron"
                elif roll < 0.88:
                    material = "copper"
                else:
                    material = "crystal"

                special = None
                special_roll = random.random()

                if special_roll < 0.05:
                    special = "bomb"
                elif special_roll < 0.09:
                    special = "energy"

                hp = 1 + min(2, self.level // 4)

                brick = Brick(
                    start_x + col * (Brick.WIDTH + gap),
                    start_y + row * (Brick.HEIGHT + gap),
                    material,
                    hp,
                    special,
                )

                self.bricks.append(brick)

    # -----------------------------------------------------
    # BALL
    # -----------------------------------------------------

    def spawn_ball(self, x=None, y=None, stuck=False):
        speed = 330 + self.ball_speed_bonus

        ball = {
            "x": float(x if x is not None else self.paddle.centerx),
            "y": float(y if y is not None else self.paddle.top - 12),
            "vx": random.choice((-1, 1)) * speed * 0.62,
            "vy": -speed,
            "radius": 9,
            "stuck": stuck,
        }

        self.balls.append(ball)

    # -----------------------------------------------------
    # PARTICLES
    # -----------------------------------------------------

    def create_particles(self, x, y, color, amount=16):
        for _ in range(amount):
            angle = random.uniform(0, math.tau)
            speed = random.uniform(45, 180)

            self.particles.append(
                Particle(
                    x=x,
                    y=y,
                    vx=math.cos(angle) * speed,
                    vy=math.sin(angle) * speed,
                    life=random.uniform(0.3, 0.85),
                    color=color,
                    size=random.uniform(2, 5),
                )
            )

    # -----------------------------------------------------
    # INPUT
    # -----------------------------------------------------

    def cycle_mode(self):
        modes = ["catch", "power", "magnet"]
        current_index = modes.index(self.mode)

        self.mode = modes[(current_index + 1) % len(modes)]
        self.message = f"Paddle mode: {self.mode.upper()}"
        self.message_timer = 1.5

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if self.state == "playing":
                if event.key == pygame.K_SPACE:
                    for ball in self.balls:
                        if ball["stuck"]:
                            ball["stuck"] = False

                elif event.key == pygame.K_TAB:
                    self.cycle_mode()

                elif event.key == pygame.K_r:
                    self.reset_level()

            elif self.state == "shop":
                if event.key == pygame.K_1:
                    self.buy_upgrade("paddle")

                elif event.key == pygame.K_2:
                    self.buy_upgrade("speed")

                elif event.key == pygame.K_3:
                    self.buy_upgrade("magnet")

                elif event.key == pygame.K_4:
                    self.buy_upgrade("multiball")

                elif event.key == pygame.K_RETURN:
                    self.level += 1
                    self.reset_level()

            elif self.state == "game_over":
                if event.key == pygame.K_RETURN:
                    self.reset_all()

    # -----------------------------------------------------
    # UPDATE
    # -----------------------------------------------------

    def update(self, dt):
        self.message_timer = max(0.0, self.message_timer - dt)

        for brick in self.bricks:
            brick.update(dt)

        self.update_particles(dt)

        if self.state != "playing":
            return

        mouse_x = pygame.mouse.get_pos()[0]

        self.paddle.centerx = clamp(
            mouse_x,
            PLAYFIELD.left + self.paddle.width // 2,
            PLAYFIELD.right - self.paddle.width // 2,
        )

        for ball in self.balls[:]:
            self.update_ball(ball, dt)

        self.update_drops(dt)

        if not self.balls:
            self.lives -= 1
            self.combo = 0

            if self.lives <= 0:
                self.state = "game_over"
                return

            self.spawn_ball(stuck=True)

        if not self.bricks:
            self.complete_level()

    # -----------------------------------------------------
    # BALL COLLISIONS
    # -----------------------------------------------------

    def update_ball(self, ball, dt):
        if ball["stuck"]:
            ball["x"] = self.paddle.centerx
            ball["y"] = self.paddle.top - 12
            return

        ball["x"] += ball["vx"] * dt
        ball["y"] += ball["vy"] * dt

        if ball["x"] - ball["radius"] <= PLAYFIELD.left:
            ball["x"] = PLAYFIELD.left + ball["radius"]
            ball["vx"] = abs(ball["vx"])

        elif ball["x"] + ball["radius"] >= PLAYFIELD.right:
            ball["x"] = PLAYFIELD.right - ball["radius"]
            ball["vx"] = -abs(ball["vx"])

        if ball["y"] - ball["radius"] <= PLAYFIELD.top:
            ball["y"] = PLAYFIELD.top + ball["radius"]
            ball["vy"] = abs(ball["vy"])

        if ball["y"] - ball["radius"] > PLAYFIELD.bottom:
            self.balls.remove(ball)
            return

        ball_rect = pygame.Rect(
            int(ball["x"] - ball["radius"]),
            int(ball["y"] - ball["radius"]),
            ball["radius"] * 2,
            ball["radius"] * 2,
        )

        # Paddle collision
        if ball_rect.colliderect(self.paddle) and ball["vy"] > 0:
            relative = (
                ball["x"] - self.paddle.centerx
            ) / (self.paddle.width / 2)

            relative = clamp(relative, -1, 1)

            speed = math.hypot(ball["vx"], ball["vy"])

            ball["vx"] = relative * speed * 0.95
            ball["vy"] = -max(
                220,
                abs(speed * (1.05 - abs(relative) * 0.2)),
            )

            if self.mode == "catch":
                ball["stuck"] = True

            elif self.mode == "power":
                ball["vx"] *= 1.25
                ball["vy"] *= 1.25

            self.combo = 0

        # Brick collision
        for brick in self.bricks[:]:
            if not ball_rect.colliderect(brick.rect):
                continue

            destroyed = brick.hit()

            overlap_left = ball_rect.right - brick.rect.left
            overlap_right = brick.rect.right - ball_rect.left
            overlap_top = ball_rect.bottom - brick.rect.top
            overlap_bottom = brick.rect.bottom - ball_rect.top

            min_overlap = min(
                overlap_left,
                overlap_right,
                overlap_top,
                overlap_bottom,
            )

            if min_overlap in (overlap_left, overlap_right):
                ball["vx"] *= -1
            else:
                ball["vy"] *= -1

            self.combo += 1
            self.best_combo = max(self.best_combo, self.combo)
            self.score += 10 * max(1, self.combo)

            if destroyed:
                self.destroy_brick(brick)

            break

    # -----------------------------------------------------
    # BRICK DESTRUCTION
    # -----------------------------------------------------

    def destroy_brick(self, brick):
        if brick not in self.bricks:
            return

        self.bricks.remove(brick)

        color = MATERIALS[brick.material]["color"]

        self.create_particles(
            brick.rect.centerx,
            brick.rect.centery,
            color,
            18,
        )

        if brick.special == "bomb":
            self.explode_bricks(brick.rect.center, 105)
        else:
            self.spawn_drop(brick)

        if brick.special == "energy":
            self.message = "Energy brick destroyed!"
            self.message_timer = 1.2

    def explode_bricks(self, center, radius):
        for other in self.bricks[:]:
            distance = math.hypot(
                other.rect.centerx - center[0],
                other.rect.centery - center[1],
            )

            if distance <= radius:
                self.bricks.remove(other)
                self.spawn_drop(other)

                self.create_particles(
                    other.rect.centerx,
                    other.rect.centery,
                    MATERIALS[other.material]["color"],
                    12,
                )

    # -----------------------------------------------------
    # DROPS / INVENTORY
    # -----------------------------------------------------

    def spawn_drop(self, brick):
        self.drops.append(
            Drop(
                x=float(brick.rect.centerx),
                y=float(brick.rect.centery),
                material=brick.material,
            )
        )

    def update_drops(self, dt):
        for drop in self.drops[:]:
            target_x = self.paddle.centerx
            target_y = self.paddle.centery

            if self.mode == "magnet" or self.magnet_level > 0:
                distance = math.hypot(
                    target_x - drop.x,
                    target_y - drop.y,
                )

                magnet_range = 170 + self.magnet_level * 55

                if 0 < distance <= magnet_range:
                    pull = 180 + self.magnet_level * 90

                    drop.x += (
                        (target_x - drop.x) / distance
                    ) * pull * dt

                    drop.y += (
                        (target_y - drop.y) / distance
                    ) * pull * dt

            drop.y += drop.speed * dt

            drop_rect = pygame.Rect(
                int(drop.x - drop.radius),
                int(drop.y - drop.radius),
                drop.radius * 2,
                drop.radius * 2,
            )

            if drop_rect.colliderect(self.paddle):
                self.collect_drop(drop)
                continue

            if drop.y - drop.radius > PLAYFIELD.bottom:
                self.drops.remove(drop)

    def collect_drop(self, drop):
        if drop not in self.drops:
            return

        self.drops.remove(drop)

        self.inventory[drop.material] += 1

        if drop.material == "iron":
            self.money += 3
        elif drop.material == "copper":
            self.money += 5
        else:
            self.money += 10

        color = MATERIALS[drop.material]["color"]

        self.create_particles(
            drop.x,
            drop.y,
            color,
            12,
        )

        self.message = (
            f"+1 {MATERIALS[drop.material]['name']}"
        )
        self.message_timer = 0.8

        self.check_order()

    # -----------------------------------------------------
    # ORDER / LEVEL COMPLETE
    # -----------------------------------------------------

    def check_order(self):
        completed = all(
            self.inventory[material] >= needed
            for material, needed in self.order.items()
        )

        if not completed:
            return

        reward = 120 + self.level * 50
        self.money += reward

        self.message = f"ORDER COMPLETE! +${reward}"
        self.message_timer = 2.5

        for material, needed in self.order.items():
            self.inventory[material] -= needed

        self.state = "shop"

    def complete_level(self):
        if self.state != "playing":
            return

        reward = 80 + self.level * 30
        self.money += reward

        self.message = f"LEVEL CLEARED! +${reward}"
        self.message_timer = 2.5

        self.state = "shop"

    # -----------------------------------------------------
    # UPGRADES
    # -----------------------------------------------------

    def buy_upgrade(self, kind):
        costs = {
            "paddle": 100 + max(0, self.paddle_width - 130) * 3,
            "speed": 120 + self.ball_speed_bonus,
            "magnet": 150 + self.magnet_level * 120,
            "multiball": 180 + self.multiball_level * 150,
        }

        cost = costs[kind]

        if self.money < cost:
            return

        self.money -= cost

        if kind == "paddle":
            self.paddle_width = min(
                220,
                self.paddle_width + 20,
            )

        elif kind == "speed":
            self.ball_speed_bonus += 25

        elif kind == "magnet":
            self.magnet_level += 1

        elif kind == "multiball":
            self.multiball_level += 1

    # -----------------------------------------------------
    # PARTICLE UPDATE
    # -----------------------------------------------------

    def update_particles(self, dt):
        for particle in self.particles[:]:
            particle.x += particle.vx * dt
            particle.y += particle.vy * dt

            particle.vx *= 0.97
            particle.vy *= 0.97
            particle.life -= dt

            if particle.life <= 0:
                self.particles.remove(particle)

    # -----------------------------------------------------
    # DRAW
    # -----------------------------------------------------

    def draw(self):
        SCREEN.fill(BACKGROUND)

        self.draw_background()
        self.draw_field()
        self.draw_panel()
        self.draw_particles()

        if self.state == "shop":
            self.draw_shop()

        elif self.state == "game_over":
            self.draw_game_over()

        pygame.display.flip()

    def draw_background(self):
        for x in range(0, WIDTH, 80):
            pygame.draw.line(
                SCREEN,
                (10, 15, 28),
                (x, 0),
                (x, HEIGHT),
            )

        for y in range(0, HEIGHT, 80):
            pygame.draw.line(
                SCREEN,
                (10, 15, 28),
                (0, y),
                (WIDTH, y),
            )

        draw_text(
            SCREEN,
            "ARKANOID FACTORY",
            FONT_TITLE,
            CYAN,
            40,
            20,
        )

        draw_text(
            SCREEN,
            f"Level {self.level}",
            FONT_MEDIUM,
            WHITE,
            620,
            35,
        )

        mode_color = (
            PURPLE
            if self.mode == "magnet"
            else BLUE
            if self.mode == "power"
            else GREEN
        )

        draw_text(
            SCREEN,
            f"Mode: {self.mode.upper()}",
            FONT_MEDIUM,
            mode_color,
            770,
            35,
        )

    def draw_field(self):
        pygame.draw.rect(
            SCREEN,
            FIELD_BG,
            PLAYFIELD,
            border_radius=14,
        )

        pygame.draw.rect(
            SCREEN,
            CYAN,
            PLAYFIELD,
            2,
            border_radius=14,
        )

        for x in range(
            PLAYFIELD.left,
            PLAYFIELD.right,
            40,
        ):
            pygame.draw.line(
                SCREEN,
                GRID,
                (x, PLAYFIELD.top),
                (x, PLAYFIELD.bottom),
            )

        for y in range(
            PLAYFIELD.top,
            PLAYFIELD.bottom,
            40,
        ):
            pygame.draw.line(
                SCREEN,
                GRID,
                (PLAYFIELD.left, y),
                (PLAYFIELD.right, y),
            )

        for brick in self.bricks:
            brick.draw(SCREEN)

        paddle_color = (
            GREEN
            if self.mode == "catch"
            else BLUE
            if self.mode == "power"
            else PURPLE
        )

        pygame.draw.rect(
            SCREEN,
            paddle_color,
            self.paddle,
            border_radius=9,
        )

        pygame.draw.rect(
            SCREEN,
            WHITE,
            self.paddle,
            2,
            border_radius=9,
        )

        for ball in self.balls:
            draw_glow_circle(
                SCREEN,
                (
                    int(ball["x"]),
                    int(ball["y"]),
                ),
                ball["radius"],
                CYAN,
            )

        for drop in self.drops:
            color = MATERIALS[drop.material]["color"]

            draw_glow_circle(
                SCREEN,
                (
                    int(drop.x),
                    int(drop.y),
                ),
                drop.radius,
                color,
            )

        if self.message_timer > 0:
            draw_text(
                SCREEN,
                self.message,
                FONT_MEDIUM,
                WHITE,
                PLAYFIELD.centerx,
                PLAYFIELD.bottom - 85,
                center=True,
            )

        draw_text(
            SCREEN,
            "Mouse = Move | SPACE = Launch | TAB = Change mode | R = Restart",
            FONT_SMALL,
            GRAY,
            PLAYFIELD.centerx,
            PLAYFIELD.bottom + 20,
            center=True,
        )

    def draw_panel(self):
        pygame.draw.rect(
            SCREEN,
            PANEL_BG,
            PANEL,
            border_radius=14,
        )

        pygame.draw.rect(
            SCREEN,
            DARK_GRAY,
            PANEL,
            2,
            border_radius=14,
        )

        x = PANEL.x + 20

        draw_text(
            SCREEN,
            "SCORE",
            FONT_SMALL,
            GRAY,
            x,
            PANEL.y + 20,
        )

        draw_text(
            SCREEN,
            f"{self.score:,}",
            FONT_LARGE,
            WHITE,
            x,
            PANEL.y + 42,
        )

        draw_text(
            SCREEN,
            f"Combo x{self.combo}",
            FONT_MEDIUM,
            YELLOW if self.combo > 0 else GRAY,
            x,
            PANEL.y + 95,
        )

        draw_text(
            SCREEN,
            f"Lives: {self.lives}",
            FONT_MEDIUM,
            RED,
            x,
            PANEL.y + 130,
        )

        draw_text(
            SCREEN,
            f"Money: ${self.money}",
            FONT_MEDIUM,
            GREEN,
            x,
            PANEL.y + 165,
        )

        draw_text(
            SCREEN,
            "ORDER",
            FONT_MEDIUM,
            WHITE,
            x,
            PANEL.y + 215,
        )

        order_y = PANEL.y + 255

        for index, material in enumerate(
            ("iron", "copper", "crystal")
        ):
            current = self.inventory[material]
            needed = self.order[material]
            color = MATERIALS[material]["color"]

            draw_text(
                SCREEN,
                (
                    f"{MATERIALS[material]['name']}: "
                    f"{current}/{needed}"
                ),
                FONT_SMALL,
                color,
                x,
                order_y + index * 30,
            )

        draw_text(
            SCREEN,
            "INVENTORY",
            FONT_MEDIUM,
            WHITE,
            x,
            PANEL.y + 365,
        )

        inventory_y = PANEL.y + 405

        for index, material in enumerate(
            ("iron", "copper", "crystal")
        ):
            draw_text(
                SCREEN,
                (
                    f"{MATERIALS[material]['name']}: "
                    f"{self.inventory[material]}"
                ),
                FONT_SMALL,
                MATERIALS[material]["color"],
                x,
                inventory_y + index * 30,
            )

        draw_text(
            SCREEN,
            "PADDLE MODES",
            FONT_MEDIUM,
            WHITE,
            x,
            PANEL.y + 515,
        )

        draw_text(
            SCREEN,
            "Catch  - hold ball",
            FONT_SMALL,
            GREEN,
            x,
            PANEL.y + 550,
        )

        draw_text(
            SCREEN,
            "Power  - faster hit",
            FONT_SMALL,
            BLUE,
            x,
            PANEL.y + 576,
        )

        draw_text(
            SCREEN,
            "Magnet - pull drops",
            FONT_SMALL,
            PURPLE,
            x,
            PANEL.y + 602,
        )

    def draw_particles(self):
        for particle in self.particles:
            pygame.draw.circle(
                SCREEN,
                particle.color,
                (
                    int(particle.x),
                    int(particle.y),
                ),
                max(1, int(particle.size)),
            )

    # -----------------------------------------------------
    # SHOP
    # -----------------------------------------------------

    def draw_shop(self):
        overlay = pygame.Surface(
            (WIDTH, HEIGHT),
            pygame.SRCALPHA,
        )

        overlay.fill((2, 4, 12, 225))
        SCREEN.blit(overlay, (0, 0))

        card = pygame.Rect(
            WIDTH // 2 - 320,
            HEIGHT // 2 - 270,
            640,
            540,
        )

        pygame.draw.rect(
            SCREEN,
            PANEL_BG,
            card,
            border_radius=22,
        )

        pygame.draw.rect(
            SCREEN,
            CYAN,
            card,
            3,
            border_radius=22,
        )

        draw_text(
            SCREEN,
            "FACTORY UPGRADE",
            FONT_LARGE,
            CYAN,
            card.centerx,
            card.y + 55,
            center=True,
        )

        draw_text(
            SCREEN,
            f"Money: ${self.money}",
            FONT_MEDIUM,
            GREEN,
            card.centerx,
            card.y + 105,
            center=True,
        )

        upgrades = [
            (
                "1",
                "Wider Paddle",
                f"Width: {self.paddle_width}",
                100 + max(0, self.paddle_width - 130) * 3,
            ),
            (
                "2",
                "Faster Ball",
                f"Bonus: +{self.ball_speed_bonus}",
                120 + self.ball_speed_bonus,
            ),
            (
                "3",
                "Stronger Magnet",
                f"Level: {self.magnet_level}",
                150 + self.magnet_level * 120,
            ),
            (
                "4",
                "Multiball Upgrade",
                f"Level: {self.multiball_level}",
                180 + self.multiball_level * 150,
            ),
        ]

        for index, (
            key,
            name,
            detail,
            cost,
        ) in enumerate(upgrades):
            y = card.y + 155 + index * 72

            rect = pygame.Rect(
                card.x + 55,
                y,
                card.width - 110,
                56,
            )

            pygame.draw.rect(
                SCREEN,
                FIELD_BG,
                rect,
                border_radius=12,
            )

            pygame.draw.rect(
                SCREEN,
                DARK_GRAY,
                rect,
                2,
                border_radius=12,
            )

            draw_text(
                SCREEN,
                key,
                FONT_MEDIUM,
                CYAN,
                rect.x + 18,
                rect.y + 14,
            )

            draw_text(
                SCREEN,
                name,
                FONT_MEDIUM,
                WHITE,
                rect.x + 62,
                rect.y + 7,
            )

            draw_text(
                SCREEN,
                detail,
                FONT_SMALL,
                GRAY,
                rect.x + 62,
                rect.y + 32,
            )

            draw_text(
                SCREEN,
                f"${cost}",
                FONT_MEDIUM,
                YELLOW,
                rect.right - 90,
                rect.y + 14,
            )

        draw_text(
            SCREEN,
            "Press ENTER to continue to the next level",
            FONT_MEDIUM,
            WHITE,
            card.centerx,
            card.bottom - 45,
            center=True,
        )

    # -----------------------------------------------------
    # GAME OVER
    # -----------------------------------------------------

    def draw_game_over(self):
        overlay = pygame.Surface(
            (WIDTH, HEIGHT),
            pygame.SRCALPHA,
        )

        overlay.fill((2, 4, 12, 230))
        SCREEN.blit(overlay, (0, 0))

        draw_text(
            SCREEN,
            "FACTORY SHUTDOWN",
            FONT_TITLE,
            RED,
            WIDTH // 2,
            HEIGHT // 2 - 100,
            center=True,
        )

        draw_text(
            SCREEN,
            f"Final score: {self.score:,}",
            FONT_MEDIUM,
            WHITE,
            WIDTH // 2,
            HEIGHT // 2 - 20,
            center=True,
        )

        draw_text(
            SCREEN,
            f"Best combo: x{self.best_combo}",
            FONT_MEDIUM,
            YELLOW,
            WIDTH // 2,
            HEIGHT // 2 + 25,
            center=True,
        )

        draw_text(
            SCREEN,
            "Press ENTER to restart",
            FONT_MEDIUM,
            CYAN,
            WIDTH // 2,
            HEIGHT // 2 + 95,
            center=True,
        )


# =========================================================
# MAIN LOOP
# =========================================================

def main():
    game = ArkanoidFactory()
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

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
import pygame
import random
import math

pygame.init()

# Window
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ocean Explorer")

clock = pygame.time.Clock()

# Fonts
font = pygame.font.SysFont("Arial", 28)
big_font = pygame.font.SysFont("Arial", 56)
small_font = pygame.font.SysFont("Arial", 22)

# Colors
WHITE = (255, 255, 255)
CYAN = (0, 220, 255)
BLUE = (40, 130, 220)
DARK_BLUE = (5, 15, 35)
YELLOW = (255, 220, 80)
RED = (255, 80, 90)
PURPLE = (180, 100, 255)
GREEN = (90, 255, 160)
GRAY = (150, 160, 170)

# Submarine
submarine = pygame.Rect(WIDTH // 2 - 35, 120, 70, 36)
sub_speed = 4
slow_timer = 0

# Game values
depth = 0
oxygen = 100
max_oxygen = 100
health = 3
gold = 0
stored_gold = 0
level = 1

game_over = False
message = ""
message_timer = 0
running = True

# Objects
treasures = []
enemies = []
bubbles = []
particles = []
background_fish = []

spawn_timer = 0
enemy_timer = 0


def reset_game():
    global depth, oxygen, health, gold, stored_gold, level
    global game_over, message, message_timer
    global treasures, enemies, bubbles, particles, background_fish
    global spawn_timer, enemy_timer, slow_timer

    submarine.centerx = WIDTH // 2
    submarine.y = 120

    depth = 0
    oxygen = max_oxygen
    health = 3
    gold = 0
    stored_gold = 0
    level = 1

    game_over = False
    message = ""
    message_timer = 0
    slow_timer = 0

    treasures = []
    enemies = []
    bubbles = []
    particles = []
    background_fish = []

    spawn_timer = 0
    enemy_timer = 0

    for _ in range(12):
        background_fish.append({
            "x": random.randint(0, WIDTH),
            "y": random.randint(120, HEIGHT - 40),
            "speed": random.uniform(0.4, 1.2),
            "size": random.randint(8, 18)
        })


def create_particles(x, y, color):
    for _ in range(18):
        particles.append({
            "x": x,
            "y": y,
            "vx": random.uniform(-3, 3),
            "vy": random.uniform(-3, 3),
            "life": random.randint(18, 35),
            "color": color
        })


def create_bubble():
    bubbles.append({
        "x": submarine.x + random.randint(5, 20),
        "y": submarine.centery + random.randint(-8, 8),
        "size": random.randint(3, 7),
        "speed": random.uniform(1, 2.5)
    })


def spawn_treasure():
    treasure_type = random.choices(
        ["chest", "pearl", "relic", "artifact", "oxygen"],
        weights=[45, 25, 15, 8, 7],
        k=1
    )[0]

    values = {
        "chest": 10,
        "pearl": 20,
        "relic": 50,
        "artifact": 100,
        "oxygen": 0
    }

    colors = {
        "chest": YELLOW,
        "pearl": WHITE,
        "relic": PURPLE,
        "artifact": GREEN,
        "oxygen": CYAN
    }

    treasures.append({
        "rect": pygame.Rect(
            random.randint(40, WIDTH - 60),
            HEIGHT + random.randint(20, 180),
            28,
            28
        ),
        "type": treasure_type,
        "value": values[treasure_type],
        "color": colors[treasure_type]
    })


def spawn_enemy():
    enemy_type = random.choice(["piranha", "jellyfish"])

    if enemy_type == "piranha":
        speed = random.uniform(2.0, 3.2) + depth / 600
        color = RED
        size = 34
    else:
        speed = random.uniform(1.0, 1.8) + depth / 900
        color = PURPLE
        size = 38

    side = random.choice(["left", "right"])

    if side == "left":
        x = -60
        direction = 1
    else:
        x = WIDTH + 60
        direction = -1

    enemies.append({
        "rect": pygame.Rect(x, random.randint(120, HEIGHT - 60), size, size),
        "type": enemy_type,
        "speed": speed,
        "direction": direction,
        "color": color
    })


def draw_background():
    depth_factor = min(1, depth / 800)

    r = int(20 * (1 - depth_factor) + 3 * depth_factor)
    g = int(120 * (1 - depth_factor) + 10 * depth_factor)
    b = int(190 * (1 - depth_factor) + 35 * depth_factor)

    screen.fill((r, g, b))

    # Light waves
    for i in range(8):
        y = 90 + i * 55
        pygame.draw.arc(
            screen,
            (255, 255, 255, max(20, 80 - int(depth_factor * 70))),
            (i * 80 - 120, y, 260, 50),
            0,
            math.pi,
            2
        )

    # Background fish
    for fish in background_fish:
        fish["x"] += fish["speed"]

        if fish["x"] > WIDTH + 30:
            fish["x"] = -30
            fish["y"] = random.randint(120, HEIGHT - 40)

        pygame.draw.ellipse(
            screen,
            (30, 80, 120),
            (fish["x"], fish["y"], fish["size"] * 2, fish["size"])
        )

    # Darkness overlay for deeper water
    darkness = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    darkness.fill((0, 0, 0, int(depth_factor * 140)))
    screen.blit(darkness, (0, 0))


def draw_submarine():
    # Light cone
    light = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    pygame.draw.polygon(
        light,
        (255, 240, 160, 45),
        [
            (submarine.right - 5, submarine.centery - 8),
            (WIDTH, submarine.centery - 120),
            (WIDTH, submarine.centery + 120),
            (submarine.right - 5, submarine.centery + 8)
        ]
    )
    screen.blit(light, (0, 0))

    # Body
    pygame.draw.ellipse(screen, YELLOW, submarine)
    pygame.draw.ellipse(screen, WHITE, (submarine.x + 15, submarine.y + 8, 18, 18))
    pygame.draw.circle(screen, BLUE, (submarine.x + 24, submarine.y + 17), 6)

    # Tail
    pygame.draw.polygon(
        screen,
        YELLOW,
        [
            (submarine.x, submarine.centery),
            (submarine.x - 22, submarine.y + 5),
            (submarine.x - 22, submarine.bottom - 5)
        ]
    )

    # Propeller
    pygame.draw.line(screen, GRAY, (submarine.x - 25, submarine.centery), (submarine.x - 38, submarine.centery - 8), 3)
    pygame.draw.line(screen, GRAY, (submarine.x - 25, submarine.centery), (submarine.x - 38, submarine.centery + 8), 3)


def draw_treasure(treasure):
    rect = treasure["rect"]
    color = treasure["color"]

    glow = pygame.Surface((60, 60), pygame.SRCALPHA)
    pygame.draw.circle(glow, (*color, 70), (30, 30), 26)
    screen.blit(glow, (rect.centerx - 30, rect.centery - 30))

    if treasure["type"] == "oxygen":
        pygame.draw.circle(screen, CYAN, rect.center, 14)
        pygame.draw.circle(screen, WHITE, rect.center, 14, 2)
        text = small_font.render("O2", True, DARK_BLUE)
        screen.blit(text, (rect.x + 3, rect.y + 3))
    else:
        pygame.draw.rect(screen, color, rect, border_radius=6)
        pygame.draw.rect(screen, WHITE, rect, 2, border_radius=6)


def draw_enemy(enemy):
    rect = enemy["rect"]

    if enemy["type"] == "piranha":
        pygame.draw.ellipse(screen, RED, rect)
        pygame.draw.polygon(
            screen,
            RED,
            [
                (rect.x, rect.centery),
                (rect.x - 15 * enemy["direction"], rect.y + 5),
                (rect.x - 15 * enemy["direction"], rect.bottom - 5)
            ]
        )
        pygame.draw.circle(screen, WHITE, (rect.centerx + 8 * enemy["direction"], rect.y + 11), 4)
        pygame.draw.circle(screen, DARK_BLUE, (rect.centerx + 8 * enemy["direction"], rect.y + 11), 2)

    else:
        pygame.draw.circle(screen, PURPLE, rect.center, rect.width // 2)
        pygame.draw.circle(screen, WHITE, rect.center, rect.width // 2, 2)

        for i in range(4):
            x = rect.x + 8 + i * 7
            pygame.draw.line(screen, PURPLE, (x, rect.bottom - 4), (x - 5, rect.bottom + 18), 2)


def update_objects():
    global oxygen, gold, stored_gold, health, depth
    global game_over, message, message_timer, slow_timer, level

    # Depth logic
    if submarine.y > 140:
        depth += 0.25 + submarine.y / 1600
    else:
        depth = max(0, depth - 0.8)

    level = max(1, int(depth // 150) + 1)

    # Oxygen
    if depth > 20:
        oxygen -= 0.04 + depth / 25000
    else:
        oxygen = min(max_oxygen, oxygen + 0.35)

    if oxygen <= 0:
        oxygen = 0
        game_over = True

    # Surface deposit
    if depth <= 3 and gold > 0:
        stored_gold += gold
        message = f"Treasure stored: +{gold} gold"
        message_timer = 120
        gold = 0

    # Move treasures upward relative to diving
    for treasure in treasures[:]:
        treasure["rect"].y -= 1 + depth / 500

        if treasure["rect"].bottom < 80:
            treasures.remove(treasure)

        if submarine.colliderect(treasure["rect"]):
            if treasure["type"] == "oxygen":
                oxygen = min(max_oxygen, oxygen + 30)
                message = "Oxygen restored!"
                create_particles(treasure["rect"].centerx, treasure["rect"].centery, CYAN)
            else:
                gold += treasure["value"]
                message = f"+{treasure['value']} gold"
                create_particles(treasure["rect"].centerx, treasure["rect"].centery, treasure["color"])

            message_timer = 90
            treasures.remove(treasure)

    # Move enemies
    for enemy in enemies[:]:
        enemy["rect"].x += enemy["speed"] * enemy["direction"]

        if enemy["rect"].right < -80 or enemy["rect"].left > WIDTH + 80:
            enemies.remove(enemy)

        if submarine.colliderect(enemy["rect"]):
            enemies.remove(enemy)

            if enemy["type"] == "jellyfish":
                slow_timer = 120
                message = "Jellyfish shock! Slowed down."
            else:
                health -= 1
                message = "-1 health"

            message_timer = 100
            create_particles(submarine.centerx, submarine.centery, RED)

            if health <= 0:
                game_over = True


def update_particles():
    for particle in particles[:]:
        particle["x"] += particle["vx"]
        particle["y"] += particle["vy"]
        particle["life"] -= 1

        if particle["life"] <= 0:
            particles.remove(particle)


def draw_particles():
    for particle in particles:
        pygame.draw.circle(
            screen,
            particle["color"],
            (int(particle["x"]), int(particle["y"])),
            3
        )


def update_bubbles():
    for bubble in bubbles[:]:
        bubble["y"] -= bubble["speed"]
        bubble["x"] += random.uniform(-0.4, 0.4)

        if bubble["y"] < 80:
            bubbles.remove(bubble)


def draw_bubbles():
    for bubble in bubbles:
        pygame.draw.circle(
            screen,
            (180, 230, 255),
            (int(bubble["x"]), int(bubble["y"])),
            bubble["size"],
            1
        )


def draw_ui():
    pygame.draw.rect(screen, (5, 12, 28), (0, 0, WIDTH, 76))
    pygame.draw.line(screen, CYAN, (0, 76), (WIDTH, 76), 3)

    screen.blit(font.render(f"Depth: {int(depth)} m", True, WHITE), (20, 18))
    screen.blit(font.render(f"Oxygen: {int(oxygen)}%", True, CYAN), (190, 18))
    screen.blit(font.render(f"Health: {health}", True, RED), (390, 18))
    screen.blit(font.render(f"Gold: {gold}", True, YELLOW), (530, 18))
    screen.blit(font.render(f"Stored: {stored_gold}", True, GREEN), (650, 18))

    oxygen_bar_w = 180
    pygame.draw.rect(screen, (40, 50, 70), (190, 52, oxygen_bar_w, 10), border_radius=5)
    pygame.draw.rect(screen, CYAN, (190, 52, int(oxygen_bar_w * (oxygen / max_oxygen)), 10), border_radius=5)

    title = small_font.render("OCEAN EXPLORER", True, GRAY)
    screen.blit(title, (WIDTH - 195, 54))


reset_game()

while running:
    clock.tick(60)

    draw_background()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if game_over and event.key == pygame.K_RETURN:
                reset_game()

    keys = pygame.key.get_pressed()

    if not game_over:
        speed = sub_speed

        if slow_timer > 0:
            speed *= 0.45
            slow_timer -= 1

        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            submarine.x -= speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            submarine.x += speed
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            submarine.y -= speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            submarine.y += speed

        submarine.clamp_ip(pygame.Rect(0, 76, WIDTH, HEIGHT - 76))

        spawn_timer += 1
        enemy_timer += 1

        if spawn_timer > max(30, 80 - level * 5):
            spawn_treasure()
            spawn_timer = 0

        if enemy_timer > max(35, 110 - level * 8):
            spawn_enemy()
            enemy_timer = 0

        if random.random() < 0.25:
            create_bubble()

        update_objects()

    update_bubbles()
    update_particles()

    for treasure in treasures:
        draw_treasure(treasure)

    for enemy in enemies:
        draw_enemy(enemy)

    draw_bubbles()
    draw_submarine()
    draw_particles()
    draw_ui()

    controls = small_font.render(
        "WASD / ARROWS = move   Return near surface to store treasure",
        True,
        GRAY
    )
    screen.blit(controls, (WIDTH // 2 - 270, HEIGHT - 28))

    if message_timer > 0:
        msg = font.render(message, True, WHITE)
        screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, 95))
        message_timer -= 1

    if game_over:
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(205)
        overlay.fill(DARK_BLUE)
        screen.blit(overlay, (0, 0))

        title = big_font.render("MISSION FAILED", True, WHITE)
        final_gold = font.render(f"Stored Gold: {stored_gold}", True, YELLOW)
        max_depth = font.render(f"Final Depth: {int(depth)} m", True, CYAN)
        restart = font.render("Press ENTER to restart", True, WHITE)

        screen.blit(title, (WIDTH // 2 - 210, HEIGHT // 2 - 95))
        screen.blit(final_gold, (WIDTH // 2 - 110, HEIGHT // 2 - 25))
        screen.blit(max_depth, (WIDTH // 2 - 110, HEIGHT // 2 + 15))
        screen.blit(restart, (WIDTH // 2 - 165, HEIGHT // 2 + 70))

    pygame.display.update()

pygame.quit()
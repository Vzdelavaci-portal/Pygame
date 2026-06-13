import pygame
import random
import math
import time

pygame.init()

WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Crystal Collector")

clock = pygame.time.Clock()

font = pygame.font.SysFont("Arial", 28)
big_font = pygame.font.SysFont("Arial", 56)
small_font = pygame.font.SysFont("Arial", 22)

BG = (18, 16, 28)
CAVE_FLOOR = (32, 30, 45)
WALL = (65, 60, 80)
WALL_DARK = (42, 38, 55)
WHITE = (255, 255, 255)
GRAY = (150, 150, 170)
PLAYER = (90, 180, 255)
ENEMY = (255, 80, 90)
GREEN = (90, 255, 160)
YELLOW = (255, 220, 90)
TRAP_COLOR = (120, 90, 255)

CRYSTAL_COLORS = [
    (80, 240, 255),
    (180, 100, 255),
    (255, 90, 200),
    (90, 255, 160),
    (255, 220, 90)
]

player = pygame.Rect(WIDTH // 2 - 18, HEIGHT // 2 - 18, 36, 36)
player_speed = 5
player_health = 3

score = 0
combo = 0
max_combo = 0
level = 1
game_over = False
running = True

last_collect_time = 0
combo_time_limit = 2.0

traps = []
trap_count = 3
max_traps = 3
trap_duration = 6
trap_cooldown = 0.8
last_trap_time = 0

walls = []
crystals = []
enemies = []
particles = []


def create_particles(x, y, color):
    for _ in range(22):
        particles.append({
            "x": x,
            "y": y,
            "vx": random.uniform(-4, 4),
            "vy": random.uniform(-4, 4),
            "life": random.randint(18, 35),
            "color": color
        })


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


def spawn_crystal():
    for _ in range(100):
        size = random.randint(18, 26)
        rect = pygame.Rect(
            random.randint(30, WIDTH - 50),
            random.randint(100, HEIGHT - 50),
            size,
            size
        )

        if not any(rect.colliderect(wall) for wall in walls):
            color = random.choice(CRYSTAL_COLORS)
            value = CRYSTAL_COLORS.index(color) + 1

            crystals.append({
                "rect": rect,
                "color": color,
                "value": value
            })
            return


def spawn_enemy():
    side = random.choice(["left", "right", "top", "bottom"])

    if side == "left":
        rect = pygame.Rect(-50, random.randint(100, HEIGHT - 50), 34, 34)
    elif side == "right":
        rect = pygame.Rect(WIDTH + 50, random.randint(100, HEIGHT - 50), 34, 34)
    elif side == "top":
        rect = pygame.Rect(random.randint(0, WIDTH), 70, 34, 34)
    else:
        rect = pygame.Rect(random.randint(0, WIDTH), HEIGHT + 50, 34, 34)

    enemies.append({
        "rect": rect,
        "speed": random.uniform(1.2, 1.8) + level * 0.15
    })


def generate_map():
    global walls, crystals, enemies

    walls = []
    crystals = []
    enemies = []

    for _ in range(18):
        w = random.randint(45, 90)
        h = random.randint(35, 75)

        rect = pygame.Rect(
            random.randint(40, WIDTH - 120),
            random.randint(100, HEIGHT - 120),
            w,
            h
        )

        if not rect.colliderect(player.inflate(140, 140)):
            walls.append(rect)

    for _ in range(16):
        spawn_crystal()

    for _ in range(3 + level):
        spawn_enemy()


def reset_game():
    global score, combo, max_combo, level
    global player_health, game_over, particles
    global last_collect_time
    global traps, trap_count, last_trap_time

    player.center = (WIDTH // 2, HEIGHT // 2)

    score = 0
    combo = 0
    max_combo = 0
    level = 1
    player_health = 3
    game_over = False
    particles = []

    traps = []
    trap_count = max_traps
    last_trap_time = 0
    last_collect_time = 0

    generate_map()


def draw_background():
    screen.fill(BG)

    for _ in range(45):
        x = random.randint(0, WIDTH)
        y = random.randint(80, HEIGHT)
        pygame.draw.circle(screen, CAVE_FLOOR, (x, y), random.randint(1, 3))


def draw_wall(wall):
    pygame.draw.rect(screen, WALL_DARK, wall, border_radius=10)
    inner = pygame.Rect(wall.x + 4, wall.y + 4, wall.width - 8, wall.height - 8)
    pygame.draw.rect(screen, WALL, inner, border_radius=8)


def draw_crystal(crystal):
    rect = crystal["rect"]
    color = crystal["color"]

    glow = pygame.Surface((rect.width + 28, rect.height + 28), pygame.SRCALPHA)
    pygame.draw.circle(
        glow,
        (*color, 70),
        (glow.get_width() // 2, glow.get_height() // 2),
        rect.width
    )
    screen.blit(glow, (rect.x - 14, rect.y - 14))

    points = [
        (rect.centerx, rect.y),
        (rect.right, rect.centery),
        (rect.centerx, rect.bottom),
        (rect.x, rect.centery)
    ]

    pygame.draw.polygon(screen, color, points)
    pygame.draw.polygon(screen, WHITE, points, 2)


def draw_player():
    pygame.draw.rect(screen, PLAYER, player, border_radius=10)
    pygame.draw.circle(screen, WHITE, (player.x + 24, player.y + 12), 4)
    pygame.draw.circle(screen, (20, 30, 50), (player.x + 25, player.y + 13), 2)


def draw_enemy(enemy):
    rect = enemy["rect"]

    pygame.draw.rect(screen, ENEMY, rect, border_radius=10)
    pygame.draw.circle(screen, WHITE, (rect.x + 11, rect.y + 13), 4)
    pygame.draw.circle(screen, WHITE, (rect.x + 24, rect.y + 13), 4)
    pygame.draw.rect(screen, (80, 20, 30), (rect.x + 9, rect.y + 25, 16, 4), border_radius=2)


def draw_trap(trap):
    current_time = time.time()
    remaining = max(0, trap_duration - (current_time - trap["created_at"]))
    alpha = int(80 + remaining / trap_duration * 120)

    trap_surface = pygame.Surface((80, 80), pygame.SRCALPHA)
    pygame.draw.circle(trap_surface, (*TRAP_COLOR, alpha), (40, 40), 32, 4)
    pygame.draw.circle(trap_surface, (*TRAP_COLOR, 45), (40, 40), 25)
    pygame.draw.circle(trap_surface, WHITE + (120,), (40, 40), 6)

    screen.blit(trap_surface, (trap["x"] - 40, trap["y"] - 40))


def place_trap():
    global trap_count, last_trap_time

    current_time = time.time()

    if trap_count <= 0:
        return

    if current_time - last_trap_time < trap_cooldown:
        return

    traps.append({
        "x": player.centerx,
        "y": player.centery,
        "radius": 34,
        "created_at": current_time
    })

    trap_count -= 1
    last_trap_time = current_time


def update_traps():
    global score

    current_time = time.time()

    for trap in traps[:]:
        if current_time - trap["created_at"] > trap_duration:
            traps.remove(trap)
            continue

        for enemy in enemies[:]:
            distance = math.hypot(
                trap["x"] - enemy["rect"].centerx,
                trap["y"] - enemy["rect"].centery
            )

            if distance <= trap["radius"]:
                enemies.remove(enemy)

                if trap in traps:
                    traps.remove(trap)

                score += 5
                create_particles(enemy["rect"].centerx, enemy["rect"].centery, TRAP_COLOR)
                break


def draw_ui():
    pygame.draw.rect(screen, (24, 22, 38), (0, 0, WIDTH, 76))
    pygame.draw.line(screen, (120, 100, 180), (0, 76), (WIDTH, 76), 3)

    screen.blit(font.render(f"Score: {score}", True, WHITE), (20, 18))
    screen.blit(font.render(f"Health: {player_health}", True, ENEMY), (165, 18))
    screen.blit(font.render(f"Level: {level}", True, YELLOW), (340, 18))

    combo_text = font.render(f"Combo: x{combo}", True, GREEN if combo > 1 else GRAY)
    screen.blit(combo_text, (500, 18))

    trap_text = font.render(f"Traps: {trap_count}", True, TRAP_COLOR)
    screen.blit(trap_text, (675, 18))


def move_player(dx, dy):
    old_x = player.x
    old_y = player.y

    player.x += dx
    for wall in walls:
        if player.colliderect(wall):
            player.x = old_x
            break

    player.y += dy
    for wall in walls:
        if player.colliderect(wall):
            player.y = old_y
            break

    player.clamp_ip(screen.get_rect())


def move_enemies():
    global player_health, game_over

    for enemy in enemies[:]:
        rect = enemy["rect"]

        dx = player.centerx - rect.centerx
        dy = player.centery - rect.centery
        distance = math.hypot(dx, dy)

        if distance != 0:
            dx /= distance
            dy /= distance

        rect.x += dx * enemy["speed"]
        rect.y += dy * enemy["speed"]

        if rect.colliderect(player):
            enemies.remove(enemy)
            player_health -= 1
            create_particles(player.centerx, player.centery, ENEMY)

            if player_health <= 0:
                game_over = True


def collect_crystals():
    global score, combo, max_combo, level, last_collect_time, trap_count

    current_time = time.time()

    for crystal in crystals[:]:
        if player.colliderect(crystal["rect"]):
            if current_time - last_collect_time <= combo_time_limit:
                combo += 1
            else:
                combo = 1

            last_collect_time = current_time
            max_combo = max(max_combo, combo)

            gained_score = crystal["value"] * combo
            score += gained_score

            # Rare chance to restore trap
            if crystal["value"] >= 4 and trap_count < max_traps:
                trap_count += 1

            create_particles(
                crystal["rect"].centerx,
                crystal["rect"].centery,
                crystal["color"]
            )

            crystals.remove(crystal)
            spawn_crystal()

            if score >= level * 60:
                level += 1
                spawn_enemy()
                spawn_enemy()


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

            if not game_over and event.key == pygame.K_e:
                place_trap()

    keys = pygame.key.get_pressed()

    if not game_over:
        dx = 0
        dy = 0

        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx -= player_speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx += player_speed
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy -= player_speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy += player_speed

        if dx != 0 and dy != 0:
            dx *= 0.7
            dy *= 0.7

        move_player(dx, dy)
        move_enemies()
        update_traps()
        collect_crystals()

    update_particles()

    for wall in walls:
        draw_wall(wall)

    for trap in traps:
        draw_trap(trap)

    for crystal in crystals:
        draw_crystal(crystal)

    for enemy in enemies:
        draw_enemy(enemy)

    draw_player()
    draw_particles()
    draw_ui()

    controls = small_font.render(
        "WASD / ARROWS = move   E = place trap   Collect crystals and avoid enemies",
        True,
        GRAY
    )
    screen.blit(controls, (WIDTH // 2 - 330, HEIGHT - 28))

    if game_over:
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(190)
        overlay.fill(BG)
        screen.blit(overlay, (0, 0))

        screen.blit(big_font.render("GAME OVER", True, WHITE), (WIDTH // 2 - 155, HEIGHT // 2 - 80))
        screen.blit(font.render(f"Final Score: {score}", True, WHITE), (WIDTH // 2 - 100, HEIGHT // 2 - 20))
        screen.blit(font.render(f"Max Combo: x{max_combo}", True, GREEN), (WIDTH // 2 - 95, HEIGHT // 2 + 20))
        screen.blit(font.render("Press ENTER to restart", True, WHITE), (WIDTH // 2 - 165, HEIGHT // 2 + 70))

    pygame.display.update()

pygame.quit()
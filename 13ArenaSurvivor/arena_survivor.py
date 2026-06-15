import pygame
import random
import math
import time
from pathlib import Path

pygame.init()

# Window
WIDTH, HEIGHT = 960, 640
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Arena Survivor")

clock = pygame.time.Clock()

# Fonts
font = pygame.font.SysFont("Arial", 28)
big_font = pygame.font.SysFont("Arial", 56)
small_font = pygame.font.SysFont("Arial", 22)

# Paths
BASE_DIR = Path(__file__).parent
ASSET_DIR = BASE_DIR / "assets"

# Colors
BG = (20, 26, 28)
GRASS = (28, 45, 35)
GRID = (38, 62, 48)
WHITE = (255, 255, 255)
GRAY = (150, 160, 160)
RED = (255, 80, 90)
GREEN = (90, 255, 160)
CYAN = (0, 220, 255)
YELLOW = (255, 220, 90)
PURPLE = (180, 110, 255)
PANEL = (18, 24, 28)

# Load assets
def load_image(name, size=None):
    image = pygame.image.load(ASSET_DIR / name).convert_alpha()
    if size:
        image = pygame.transform.smoothscale(image, size)
    return image

player_img = load_image("player.png", (50, 50))
slime_img = load_image("slime.png", (44, 44))
bat_img = load_image("bat.png", (44, 44))
orc_img = load_image("orc.png", (56, 56))
orb_img = load_image("orb.png", (22, 22))
xp_img = load_image("xp_crystal.png", (22, 22))

# Player
player = pygame.Rect(WIDTH // 2 - 22, HEIGHT // 2 - 22, 44, 44)
player_speed = 4.8
player_health = 6
max_health = 6

# Combat
damage = 1
attack_cooldown = 0.75
last_attack_time = 0
projectile_count = 1
projectiles = []
projectile_speed = 8

# Enemies, XP, particles
enemies = []
xp_crystals = []
particles = []
floating_texts = []

# Game variables
score = 0
kills = 0
level = 1
xp = 0
xp_needed = 8
survival_time = 0
start_time = time.time()

enemy_spawn_timer = 0
game_state = "playing"  # playing, upgrade, game_over
running = True

# Background decorations
decorations = []
for _ in range(75):
    decorations.append({
        "x": random.randint(0, WIDTH),
        "y": random.randint(80, HEIGHT),
        "r": random.randint(1, 3),
        "color": random.choice([(45, 80, 55), (55, 90, 65), (70, 70, 55)])
    })


def create_particles(x, y, color, count=18):
    for _ in range(count):
        particles.append({
            "x": x,
            "y": y,
            "vx": random.uniform(-4, 4),
            "vy": random.uniform(-4, 4),
            "life": random.randint(18, 35),
            "color": color
        })


def add_floating_text(text, x, y, color):
    floating_texts.append({
        "text": text,
        "x": x,
        "y": y,
        "life": 45,
        "color": color
    })


def update_particles():
    for p in particles[:]:
        p["x"] += p["vx"]
        p["y"] += p["vy"]
        p["life"] -= 1
        if p["life"] <= 0:
            particles.remove(p)


def draw_particles():
    for p in particles:
        pygame.draw.circle(screen, p["color"], (int(p["x"]), int(p["y"])), 3)


def update_floating_texts():
    for text in floating_texts[:]:
        text["y"] -= 0.8
        text["life"] -= 1
        if text["life"] <= 0:
            floating_texts.remove(text)


def draw_floating_texts():
    for item in floating_texts:
        rendered = small_font.render(item["text"], True, item["color"])
        screen.blit(rendered, (item["x"], item["y"]))


def draw_background():
    screen.fill(BG)

    # subtle grid / grass texture
    for x in range(0, WIDTH, 48):
        pygame.draw.line(screen, GRID, (x, 76), (x, HEIGHT), 1)

    for y in range(76, HEIGHT, 48):
        pygame.draw.line(screen, GRID, (0, y), (WIDTH, y), 1)

    for d in decorations:
        pygame.draw.circle(screen, d["color"], (d["x"], d["y"]), d["r"])

    # vignette
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    pygame.draw.rect(overlay, (0, 0, 0, 80), (0, 0, WIDTH, HEIGHT), border_radius=0)
    pygame.draw.ellipse(overlay, (0, 0, 0, 0), (-160, -80, WIDTH + 320, HEIGHT + 180))
    screen.blit(overlay, (0, 0))


def spawn_enemy():
    enemy_type = random.choices(
        ["slime", "bat", "orc"],
        weights=[60, 30, 10 + level],
        k=1
    )[0]

    side = random.choice(["top", "bottom", "left", "right"])

    if side == "top":
        x, y = random.randint(0, WIDTH), 60
    elif side == "bottom":
        x, y = random.randint(0, WIDTH), HEIGHT + 50
    elif side == "left":
        x, y = -50, random.randint(100, HEIGHT)
    else:
        x, y = WIDTH + 50, random.randint(100, HEIGHT)

    if enemy_type == "slime":
        size, hp, speed, value, img = 38, 2 + level // 3, 1.3 + level * 0.05, 1, slime_img
    elif enemy_type == "bat":
        size, hp, speed, value, img = 34, 1 + level // 4, 2.2 + level * 0.07, 2, bat_img
    else:
        size, hp, speed, value, img = 48, 5 + level, 0.9 + level * 0.04, 4, orc_img

    enemies.append({
        "type": enemy_type,
        "rect": pygame.Rect(x, y, size, size),
        "hp": hp,
        "max_hp": hp,
        "speed": speed,
        "value": value,
        "img": img
    })


def shoot_projectiles():
    global last_attack_time

    current_time = time.time()
    if current_time - last_attack_time < attack_cooldown:
        return

    if not enemies:
        return

    # nearest enemies
    sorted_enemies = sorted(
        enemies,
        key=lambda e: math.hypot(e["rect"].centerx - player.centerx, e["rect"].centery - player.centery)
    )

    targets = sorted_enemies[:projectile_count]

    for target in targets:
        dx = target["rect"].centerx - player.centerx
        dy = target["rect"].centery - player.centery
        distance = math.hypot(dx, dy)

        if distance == 0:
            continue

        dx /= distance
        dy /= distance

        projectiles.append({
            "rect": pygame.Rect(player.centerx - 6, player.centery - 6, 12, 12),
            "dx": dx,
            "dy": dy
        })

    last_attack_time = current_time


def move_player():
    keys = pygame.key.get_pressed()

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

    player.x += dx
    player.y += dy
    player.clamp_ip(screen.get_rect())


def move_enemies():
    global player_health, game_state

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
            create_particles(player.centerx, player.centery, RED, 25)
            add_floating_text("-1 HP", player.x, player.y - 20, RED)

            if player_health <= 0:
                game_state = "game_over"


def move_projectiles():
    for projectile in projectiles[:]:
        projectile["rect"].x += projectile["dx"] * projectile_speed
        projectile["rect"].y += projectile["dy"] * projectile_speed

        if not screen.get_rect().colliderect(projectile["rect"]):
            projectiles.remove(projectile)


def projectile_collisions():
    global score, kills, xp

    for projectile in projectiles[:]:
        for enemy in enemies[:]:
            if projectile["rect"].colliderect(enemy["rect"]):
                if projectile in projectiles:
                    projectiles.remove(projectile)

                enemy["hp"] -= damage
                create_particles(enemy["rect"].centerx, enemy["rect"].centery, CYAN, 8)

                if enemy["hp"] <= 0:
                    enemies.remove(enemy)
                    kills += 1
                    score += enemy["value"] * 10

                    xp_crystals.append({
                        "rect": pygame.Rect(enemy["rect"].centerx - 10, enemy["rect"].centery - 10, 20, 20),
                        "value": enemy["value"]
                    })

                    create_particles(enemy["rect"].centerx, enemy["rect"].centery, GREEN, 20)

                break


def collect_xp():
    global xp, level, xp_needed, game_state

    for crystal in xp_crystals[:]:
        distance = math.hypot(crystal["rect"].centerx - player.centerx, crystal["rect"].centery - player.centery)

        # magnet when close
        if distance < 130:
            dx = player.centerx - crystal["rect"].centerx
            dy = player.centery - crystal["rect"].centery
            if distance != 0:
                crystal["rect"].x += (dx / distance) * 5
                crystal["rect"].y += (dy / distance) * 5

        if crystal["rect"].colliderect(player):
            xp_crystals.remove(crystal)
            xp += crystal["value"]
            create_particles(player.centerx, player.centery, GREEN, 10)

            if xp >= xp_needed:
                xp -= xp_needed
                level += 1
                xp_needed = int(xp_needed * 1.35 + 3)
                game_state = "upgrade"


def draw_player():
    glow = pygame.Surface((70, 70), pygame.SRCALPHA)
    pygame.draw.circle(glow, (0, 220, 255, 60), (35, 35), 32)
    screen.blit(glow, (player.centerx - 35, player.centery - 35))
    screen.blit(player_img, (player.centerx - 25, player.centery - 25))


def draw_enemies():
    for enemy in enemies:
        rect = enemy["rect"]
        image = enemy["img"]
        screen.blit(image, (rect.centerx - image.get_width() // 2, rect.centery - image.get_height() // 2))

        # HP bar
        if enemy["hp"] < enemy["max_hp"]:
            bar_width = rect.width
            hp_ratio = enemy["hp"] / enemy["max_hp"]
            pygame.draw.rect(screen, RED, (rect.x, rect.y - 8, bar_width, 4))
            pygame.draw.rect(screen, GREEN, (rect.x, rect.y - 8, bar_width * hp_ratio, 4))


def draw_projectiles():
    for projectile in projectiles:
        rect = projectile["rect"]
        glow = pygame.Surface((34, 34), pygame.SRCALPHA)
        pygame.draw.circle(glow, (0, 220, 255, 80), (17, 17), 16)
        screen.blit(glow, (rect.centerx - 17, rect.centery - 17))
        screen.blit(orb_img, (rect.centerx - 11, rect.centery - 11))


def draw_xp():
    for crystal in xp_crystals:
        rect = crystal["rect"]
        screen.blit(xp_img, (rect.x, rect.y))


def draw_ui():
    pygame.draw.rect(screen, PANEL, (0, 0, WIDTH, 76))
    pygame.draw.line(screen, CYAN, (0, 76), (WIDTH, 76), 3)

    elapsed = int(time.time() - start_time)
    minutes = elapsed // 60
    seconds = elapsed % 60

    screen.blit(font.render(f"Level: {level}", True, WHITE), (20, 18))
    screen.blit(font.render(f"HP: {player_health}/{max_health}", True, RED), (150, 18))
    screen.blit(font.render(f"Kills: {kills}", True, YELLOW), (310, 18))
    screen.blit(font.render(f"Time: {minutes:02d}:{seconds:02d}", True, WHITE), (455, 18))

    # XP bar
    bar_x, bar_y = 650, 26
    bar_w, bar_h = 260, 18
    pygame.draw.rect(screen, (55, 65, 70), (bar_x, bar_y, bar_w, bar_h), border_radius=8)
    xp_ratio = min(1, xp / xp_needed)
    pygame.draw.rect(screen, GREEN, (bar_x, bar_y, int(bar_w * xp_ratio), bar_h), border_radius=8)
    pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_w, bar_h), 2, border_radius=8)


def draw_upgrade_menu():
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(215)
    overlay.fill((10, 12, 18))
    screen.blit(overlay, (0, 0))

    draw_center("LEVEL UP!", big_font, WHITE, HEIGHT // 2 - 150)
    draw_center("Choose your upgrade", font, GRAY, HEIGHT // 2 - 100)

    upgrades = [
        "1 - More Damage",
        "2 - Faster Attack",
        "3 - Movement Speed",
        "4 - Extra Projectile"
    ]

    colors = [RED, CYAN, GREEN, PURPLE]

    for i, upgrade in enumerate(upgrades):
        y = HEIGHT // 2 - 35 + i * 52
        pygame.draw.rect(screen, (26, 34, 42), (WIDTH // 2 - 210, y - 22, 420, 42), border_radius=12)
        pygame.draw.rect(screen, colors[i], (WIDTH // 2 - 210, y - 22, 420, 42), 2, border_radius=12)
        draw_center(upgrade, font, WHITE, y)


def draw_center(text, used_font, color, y):
    rendered = used_font.render(text, True, color)
    rect = rendered.get_rect(center=(WIDTH // 2, y))
    screen.blit(rendered, rect)


def apply_upgrade(choice):
    global damage, attack_cooldown, player_speed, projectile_count, game_state

    if choice == 1:
        damage += 1
        add_floating_text("Damage Up!", player.x, player.y - 20, RED)

    elif choice == 2:
        attack_cooldown = max(0.25, attack_cooldown - 0.08)
        add_floating_text("Attack Speed Up!", player.x, player.y - 20, CYAN)

    elif choice == 3:
        player_speed += 0.35
        add_floating_text("Speed Up!", player.x, player.y - 20, GREEN)

    elif choice == 4:
        projectile_count = min(5, projectile_count + 1)
        add_floating_text("Extra Orb!", player.x, player.y - 20, PURPLE)

    game_state = "playing"


def reset_game():
    global player_health, score, kills, level, xp, xp_needed
    global damage, attack_cooldown, player_speed, projectile_count
    global projectiles, enemies, xp_crystals, particles, floating_texts
    global start_time, enemy_spawn_timer, game_state, last_attack_time

    player.center = (WIDTH // 2, HEIGHT // 2)

    player_health = 6
    score = 0
    kills = 0
    level = 1
    xp = 0
    xp_needed = 8

    damage = 1
    attack_cooldown = 0.75
    player_speed = 4.8
    projectile_count = 1

    projectiles = []
    enemies = []
    xp_crystals = []
    particles = []
    floating_texts = []

    start_time = time.time()
    enemy_spawn_timer = 0
    last_attack_time = 0
    game_state = "playing"


reset_game()

while running:
    clock.tick(60)

    draw_background()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if game_state == "game_over" and event.key == pygame.K_RETURN:
                reset_game()

            if game_state == "upgrade":
                if event.key == pygame.K_1:
                    apply_upgrade(1)
                elif event.key == pygame.K_2:
                    apply_upgrade(2)
                elif event.key == pygame.K_3:
                    apply_upgrade(3)
                elif event.key == pygame.K_4:
                    apply_upgrade(4)

    if game_state == "playing":
        move_player()

        enemy_spawn_timer += 1
        spawn_rate = max(10, 52 - level * 3)

        if enemy_spawn_timer >= spawn_rate:
            spawn_enemy()
            enemy_spawn_timer = 0

        shoot_projectiles()
        move_projectiles()
        move_enemies()
        projectile_collisions()
        collect_xp()

    update_particles()
    update_floating_texts()

    draw_xp()
    draw_projectiles()
    draw_enemies()
    draw_player()
    draw_particles()
    draw_floating_texts()
    draw_ui()

    controls = small_font.render("WASD / ARROWS = move   Magic orbs shoot automatically", True, GRAY)
    screen.blit(controls, (WIDTH // 2 - 255, HEIGHT - 28))

    if game_state == "upgrade":
        draw_upgrade_menu()

    if game_state == "game_over":
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(205)
        overlay.fill((10, 12, 18))
        screen.blit(overlay, (0, 0))

        draw_center("GAME OVER", big_font, WHITE, HEIGHT // 2 - 95)
        draw_center(f"Kills: {kills}", font, YELLOW, HEIGHT // 2 - 30)
        draw_center(f"Level Reached: {level}", font, GREEN, HEIGHT // 2 + 10)
        draw_center("Press ENTER to restart", font, CYAN, HEIGHT // 2 + 65)

    pygame.display.update()

pygame.quit()
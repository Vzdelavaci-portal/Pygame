import pygame
import random

pygame.init()

# Window
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Dodge")

clock = pygame.time.Clock()

# Fonts
font = pygame.font.SysFont("Arial", 28)
big_font = pygame.font.SysFont("Arial", 56)
small_font = pygame.font.SysFont("Arial", 22)

# Colors
BG = (8, 10, 25)
WHITE = (255, 255, 255)
CYAN = (0, 220, 255)
YELLOW = (255, 220, 80)
RED = (255, 80, 90)
GRAY = (140, 145, 160)
ASTEROID = (120, 110, 105)
ASTEROID_DARK = (70, 65, 65)

# Player
player = pygame.Rect(WIDTH // 2 - 22, HEIGHT - 80, 44, 52)
player_speed = 6

# Asteroids
asteroids = []
asteroid_speed = 4
spawn_timer = 0

# Stars
stars = []

# Game variables
score = 0
level = 1
survival_timer = 0
game_over = False
running = True


def create_stars():
    star_list = []

    for _ in range(90):
        star_list.append({
            "x": random.randint(0, WIDTH),
            "y": random.randint(0, HEIGHT),
            "speed": random.uniform(0.5, 2.2),
            "size": random.randint(1, 3)
        })

    return star_list


def reset_game():
    global asteroids, asteroid_speed, spawn_timer
    global score, level, survival_timer, game_over
    global stars

    player.centerx = WIDTH // 2
    player.y = HEIGHT - 80

    asteroids = []
    asteroid_speed = 4
    spawn_timer = 0

    score = 0
    level = 1
    survival_timer = 0
    game_over = False

    stars = create_stars()


def create_asteroid():
    size = random.randint(30, 70)
    x = random.randint(0, WIDTH - size)
    y = -size

    asteroid = {
        "rect": pygame.Rect(x, y, size, size),
        "speed": asteroid_speed + random.uniform(-0.8, 1.2),
        "rotation": random.randint(0, 360)
    }

    asteroids.append(asteroid)


def draw_background():
    screen.fill(BG)

    for star in stars:
        pygame.draw.circle(
            screen,
            WHITE,
            (int(star["x"]), int(star["y"])),
            star["size"]
        )


def update_stars():
    for star in stars:
        star["y"] += star["speed"]

        if star["y"] > HEIGHT:
            star["y"] = 0
            star["x"] = random.randint(0, WIDTH)


def draw_player():
    # Ship body
    pygame.draw.polygon(
        screen,
        CYAN,
        [
            (player.centerx, player.y),
            (player.x, player.bottom),
            (player.right, player.bottom)
        ]
    )

    # Ship core
    pygame.draw.polygon(
        screen,
        WHITE,
        [
            (player.centerx, player.y + 14),
            (player.x + 14, player.bottom - 8),
            (player.right - 14, player.bottom - 8)
        ]
    )

    # Engine flame
    pygame.draw.polygon(
        screen,
        YELLOW,
        [
            (player.centerx - 10, player.bottom),
            (player.centerx + 10, player.bottom),
            (player.centerx, player.bottom + random.randint(10, 22))
        ]
    )


def draw_asteroid(asteroid):
    rect = asteroid["rect"]
    center = rect.center
    radius = rect.width // 2

    pygame.draw.circle(screen, ASTEROID, center, radius)
    pygame.draw.circle(screen, ASTEROID_DARK, center, radius, 3)

    # Craters
    pygame.draw.circle(screen, ASTEROID_DARK, (rect.x + radius // 2, rect.y + radius), max(3, radius // 5))
    pygame.draw.circle(screen, ASTEROID_DARK, (rect.x + radius + 8, rect.y + radius // 2), max(3, radius // 6))
    pygame.draw.circle(screen, ASTEROID_DARK, (rect.x + radius + 2, rect.y + radius + 10), max(3, radius // 7))


def draw_ui():
    pygame.draw.rect(screen, (14, 18, 40), (0, 0, WIDTH, 70))
    pygame.draw.line(screen, CYAN, (0, 70), (WIDTH, 70), 3)

    score_text = font.render(f"Score: {score}", True, WHITE)
    level_text = font.render(f"Level: {level}", True, YELLOW)

    screen.blit(score_text, (20, 20))
    screen.blit(level_text, (WIDTH - 130, 20))

    title = small_font.render("SPACE DODGE", True, CYAN)
    screen.blit(title, (WIDTH // 2 - 70, 24))


reset_game()

while running:
    clock.tick(60)

    update_stars()
    draw_background()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if game_over and event.key == pygame.K_RETURN:
                reset_game()

    keys = pygame.key.get_pressed()

    if not game_over:
        # Player movement
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player.x -= player_speed

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player.x += player_speed

        if keys[pygame.K_UP] or keys[pygame.K_w]:
            player.y -= player_speed

        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            player.y += player_speed

        player.clamp_ip(screen.get_rect())

        # Spawn asteroids
        spawn_timer += 1
        spawn_rate = max(18, 55 - level * 4)

        if spawn_timer >= spawn_rate:
            create_asteroid()
            spawn_timer = 0

        # Move asteroids
        for asteroid in asteroids[:]:
            asteroid["rect"].y += asteroid["speed"]

            if asteroid["rect"].top > HEIGHT:
                asteroids.remove(asteroid)

        # Collision
        for asteroid in asteroids:
            if player.colliderect(asteroid["rect"]):
                game_over = True

        # Score over time
        survival_timer += 1

        if survival_timer >= 30:
            score += 1
            survival_timer = 0

            if score % 10 == 0:
                level += 1
                asteroid_speed += 0.8

    # Draw asteroids
    for asteroid in asteroids:
        draw_asteroid(asteroid)

    draw_player()
    draw_ui()

    controls = small_font.render("WASD / ARROWS = move", True, GRAY)
    screen.blit(controls, (WIDTH // 2 - 95, HEIGHT - 28))

    if game_over:
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(190)
        overlay.fill(BG)
        screen.blit(overlay, (0, 0))

        title = big_font.render("GAME OVER", True, WHITE)
        final_score = font.render(f"Final Score: {score}", True, WHITE)
        restart = font.render("Press ENTER to restart", True, CYAN)

        screen.blit(title, (WIDTH // 2 - 155, HEIGHT // 2 - 70))
        screen.blit(final_score, (WIDTH // 2 - 95, HEIGHT // 2 - 10))
        screen.blit(restart, (WIDTH // 2 - 165, HEIGHT // 2 + 40))

    pygame.display.update()

pygame.quit()
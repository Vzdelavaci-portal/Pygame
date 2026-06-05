import pygame
import random
import math

pygame.init()

# Window
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Zombie Survival")

clock = pygame.time.Clock()

# Fonts
font = pygame.font.SysFont("Arial", 28)
big_font = pygame.font.SysFont("Arial", 56)
small_font = pygame.font.SysFont("Arial", 22)

# Colors
BG = (12, 15, 25)
GRID = (25, 32, 50)
WHITE = (255, 255, 255)
GREEN = (80, 255, 150)
DARK_GREEN = (40, 160, 90)
RED = (255, 70, 80)
YELLOW = (255, 220, 80)
CYAN = (0, 220, 255)
GRAY = (130, 140, 160)

# Player
player = pygame.Rect(WIDTH // 2 - 20, HEIGHT // 2 - 20, 40, 40)
player_speed = 5
player_health = 5

# Bullets
bullets = []
bullet_speed = 10

# Zombies
zombies = []
zombie_spawn_timer = 0
zombie_speed = 1.4

# Game
score = 0
level = 1
game_over = False
running = True

# Particles
particles = []


def reset_game():
    global player_health, bullets, zombies
    global zombie_spawn_timer, zombie_speed
    global score, level, game_over, particles

    player.center = (WIDTH // 2, HEIGHT // 2)
    player_health = 5

    bullets = []
    zombies = []
    particles = []

    zombie_spawn_timer = 0
    zombie_speed = 1.4

    score = 0
    level = 1
    game_over = False


def spawn_zombie():
    side = random.choice(["top", "bottom", "left", "right"])

    if side == "top":
        x = random.randint(0, WIDTH)
        y = -40
    elif side == "bottom":
        x = random.randint(0, WIDTH)
        y = HEIGHT + 40
    elif side == "left":
        x = -40
        y = random.randint(0, HEIGHT)
    else:
        x = WIDTH + 40
        y = random.randint(0, HEIGHT)

    zombie = pygame.Rect(x, y, 38, 38)
    zombies.append(zombie)


def create_particles(x, y, color):
    for _ in range(18):
        particles.append({
            "x": x,
            "y": y,
            "vx": random.uniform(-4, 4),
            "vy": random.uniform(-4, 4),
            "life": random.randint(15, 30),
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


def draw_background():
    screen.fill(BG)

    for x in range(0, WIDTH, 40):
        pygame.draw.line(screen, GRID, (x, 0), (x, HEIGHT))

    for y in range(0, HEIGHT, 40):
        pygame.draw.line(screen, GRID, (0, y), (WIDTH, y))


def draw_player():
    pygame.draw.rect(screen, CYAN, player, border_radius=12)
    pygame.draw.circle(screen, WHITE, player.center, 8)

    mouse_x, mouse_y = pygame.mouse.get_pos()
    dx = mouse_x - player.centerx
    dy = mouse_y - player.centery
    angle = math.atan2(dy, dx)

    gun_length = 28
    end_x = player.centerx + math.cos(angle) * gun_length
    end_y = player.centery + math.sin(angle) * gun_length

    pygame.draw.line(screen, YELLOW, player.center, (end_x, end_y), 5)


def draw_zombie(zombie):
    pygame.draw.rect(screen, DARK_GREEN, zombie, border_radius=10)

    pygame.draw.circle(screen, RED, (zombie.x + 12, zombie.y + 14), 4)
    pygame.draw.circle(screen, RED, (zombie.x + 26, zombie.y + 14), 4)

    pygame.draw.rect(screen, GREEN, (zombie.x + 9, zombie.y + 28, 20, 4), border_radius=2)


def draw_ui():
    pygame.draw.rect(screen, (18, 24, 42), (0, 0, WIDTH, 70))
    pygame.draw.line(screen, CYAN, (0, 70), (WIDTH, 70), 3)

    score_text = font.render(f"Score: {score}", True, WHITE)
    level_text = font.render(f"Level: {level}", True, YELLOW)
    health_text = font.render(f"Health: {player_health}", True, RED)

    screen.blit(score_text, (20, 20))
    screen.blit(level_text, (WIDTH // 2 - 50, 20))
    screen.blit(health_text, (WIDTH - 150, 20))


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

        if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
            mouse_x, mouse_y = pygame.mouse.get_pos()

            dx = mouse_x - player.centerx
            dy = mouse_y - player.centery
            distance = math.hypot(dx, dy)

            if distance != 0:
                dx /= distance
                dy /= distance

            bullet = {
                "rect": pygame.Rect(player.centerx - 5, player.centery - 5, 10, 10),
                "dx": dx,
                "dy": dy
            }

            bullets.append(bullet)

    keys = pygame.key.get_pressed()

    if not game_over:
        # Player movement
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            player.y -= player_speed

        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            player.y += player_speed

        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            player.x -= player_speed

        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            player.x += player_speed

        player.clamp_ip(screen.get_rect())

        # Spawn zombies
        zombie_spawn_timer += 1

        spawn_rate = max(18, 60 - level * 4)

        if zombie_spawn_timer >= spawn_rate:
            spawn_zombie()
            zombie_spawn_timer = 0

        # Move bullets
        for bullet in bullets[:]:
            bullet["rect"].x += bullet["dx"] * bullet_speed
            bullet["rect"].y += bullet["dy"] * bullet_speed

            if not screen.get_rect().colliderect(bullet["rect"]):
                bullets.remove(bullet)

        # Move zombies toward player
        for zombie in zombies[:]:
            dx = player.centerx - zombie.centerx
            dy = player.centery - zombie.centery
            distance = math.hypot(dx, dy)

            if distance != 0:
                dx /= distance
                dy /= distance

            zombie.x += dx * zombie_speed
            zombie.y += dy * zombie_speed

            if zombie.colliderect(player):
                zombies.remove(zombie)
                player_health -= 1
                create_particles(player.centerx, player.centery, RED)

                if player_health <= 0:
                    game_over = True

        # Bullet collision with zombies
        for bullet in bullets[:]:
            for zombie in zombies[:]:
                if bullet["rect"].colliderect(zombie):
                    bullets.remove(bullet)
                    zombies.remove(zombie)

                    score += 1
                    create_particles(zombie.centerx, zombie.centery, GREEN)

                    if score % 10 == 0:
                        level += 1
                        zombie_speed += 0.25

                    break

    update_particles()

    # Draw objects
    draw_ui()

    for bullet in bullets:
        pygame.draw.circle(screen, YELLOW, bullet["rect"].center, 5)

    for zombie in zombies:
        draw_zombie(zombie)

    draw_player()
    draw_particles()

    controls = small_font.render("WASD / ARROWS = move   MOUSE CLICK = shoot", True, GRAY)
    screen.blit(controls, (WIDTH // 2 - 220, HEIGHT - 28))

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
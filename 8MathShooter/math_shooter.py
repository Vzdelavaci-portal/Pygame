import pygame
import random

pygame.init()

# Window
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Math Shooter")

clock = pygame.time.Clock()

# Fonts
font = pygame.font.SysFont("Arial", 28)
big_font = pygame.font.SysFont("Arial", 56)
small_font = pygame.font.SysFont("Arial", 22)

# Colors
BG = (12, 15, 30)
WHITE = (255, 255, 255)
CYAN = (0, 220, 255)
PINK = (255, 70, 180)
YELLOW = (255, 220, 80)
GREEN = (80, 255, 150)
RED = (255, 80, 90)
GRAY = (120, 130, 160)

# Player
player_width = 70
player_height = 25
player = pygame.Rect(WIDTH // 2 - player_width // 2, HEIGHT - 55, player_width, player_height)
player_speed = 7

# Bullets
bullets = []
bullet_speed = 10

# Targets
targets = []
target_speed = 2
spawn_timer = 0

# Game
score = 0
lives = 3
level = 1
current_answer = 0
game_over = False
running = True

# Particles
particles = []


def generate_question():
    a = random.randint(1, 12)
    b = random.randint(1, 12)
    operator = random.choice(["+", "-", "*"])

    if operator == "+":
        answer = a + b
    elif operator == "-":
        answer = a - b
    else:
        answer = a * b

    question = f"{a} {operator} {b}"
    return question, answer


question, current_answer = generate_question()


def create_targets():
    global current_answer

    correct_value = current_answer
    values = [correct_value]

    while len(values) < 4:
        fake_value = correct_value + random.randint(-15, 15)

        if fake_value != correct_value and fake_value not in values:
            values.append(fake_value)

    random.shuffle(values)

    new_targets = []

    spacing = WIDTH // 5

    for i, value in enumerate(values):
        x = spacing * (i + 1) - 45
        y = -random.randint(40, 180)

        rect = pygame.Rect(x, y, 90, 55)

        new_targets.append({
            "rect": rect,
            "value": value,
            "correct": value == correct_value
        })

    return new_targets


def reset_round():
    global question, current_answer, targets

    question, current_answer = generate_question()
    targets = create_targets()


def reset_game():
    global score, lives, level, target_speed
    global bullets, particles, game_over

    score = 0
    lives = 3
    level = 1
    target_speed = 2
    bullets = []
    particles = []
    game_over = False

    player.x = WIDTH // 2 - player_width // 2

    reset_round()


def draw_text_center(text, used_font, color, x, y):
    rendered = used_font.render(text, True, color)
    rect = rendered.get_rect(center=(x, y))
    screen.blit(rendered, rect)


def draw_neon_rect(rect, color):
    glow_rect = pygame.Rect(rect.x - 4, rect.y - 4, rect.width + 8, rect.height + 8)
    pygame.draw.rect(screen, color, glow_rect, border_radius=14)
    pygame.draw.rect(screen, BG, rect, border_radius=12)
    pygame.draw.rect(screen, color, rect, 3, border_radius=12)


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


reset_game()

while running:
    clock.tick(60)
    screen.fill(BG)

    # Background grid
    for x in range(0, WIDTH, 40):
        pygame.draw.line(screen, (22, 27, 50), (x, 0), (x, HEIGHT))

    for y in range(0, HEIGHT, 40):
        pygame.draw.line(screen, (22, 27, 50), (0, y), (WIDTH, y))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if game_over and event.key == pygame.K_RETURN:
                reset_game()

            if not game_over and event.key == pygame.K_SPACE:
                bullet = pygame.Rect(
                    player.centerx - 4,
                    player.y - 18,
                    8,
                    18
                )
                bullets.append(bullet)

    keys = pygame.key.get_pressed()

    if not game_over:
        # Player movement
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player.x -= player_speed

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player.x += player_speed

        if player.left < 0:
            player.left = 0

        if player.right > WIDTH:
            player.right = WIDTH

        # Move bullets
        for bullet in bullets[:]:
            bullet.y -= bullet_speed

            if bullet.bottom < 0:
                bullets.remove(bullet)

        # Move targets
        for target in targets[:]:
            target["rect"].y += target_speed

            if target["rect"].top > HEIGHT:
                lives -= 1
                reset_round()
                break

        # Bullet collision
        for bullet in bullets[:]:
            for target in targets[:]:
                if bullet.colliderect(target["rect"]):

                    if bullet in bullets:
                        bullets.remove(bullet)

                    if target["correct"]:
                        score += 1
                        create_particles(target["rect"].centerx, target["rect"].centery, GREEN)

                        if score % 5 == 0:
                            level += 1
                            target_speed += 0.5

                        reset_round()

                    else:
                        lives -= 1
                        create_particles(target["rect"].centerx, target["rect"].centery, RED)
                        reset_round()

                    break

        if lives <= 0:
            game_over = True

    update_particles()

    # UI panel
    pygame.draw.rect(screen, (18, 24, 45), (0, 0, WIDTH, 90))
    pygame.draw.line(screen, CYAN, (0, 90), (WIDTH, 90), 3)

    draw_text_center("MATH SHOOTER", small_font, CYAN, WIDTH // 2, 20)
    draw_text_center(f"Solve: {question}", big_font, WHITE, WIDTH // 2, 58)

    score_text = font.render(f"Score: {score}", True, WHITE)
    lives_text = font.render(f"Lives: {lives}", True, RED)
    level_text = font.render(f"Level: {level}", True, YELLOW)

    screen.blit(score_text, (20, 25))
    screen.blit(lives_text, (20, 55))
    screen.blit(level_text, (WIDTH - 130, 40))

    # Draw player
    pygame.draw.rect(screen, CYAN, player, border_radius=10)
    pygame.draw.polygon(
        screen,
        PINK,
        [
            (player.centerx, player.y - 18),
            (player.centerx - 18, player.y),
            (player.centerx + 18, player.y)
        ]
    )

    # Draw bullets
    for bullet in bullets:
        pygame.draw.rect(screen, YELLOW, bullet, border_radius=4)

    # Draw targets
    for target in targets:
        rect = target["rect"]
        draw_neon_rect(rect, PINK)

        value_text = font.render(str(target["value"]), True, WHITE)
        value_rect = value_text.get_rect(center=rect.center)
        screen.blit(value_text, value_rect)

    draw_particles()

    # Controls
    controls = small_font.render("A/D or ARROWS = move   SPACE = shoot", True, GRAY)
    screen.blit(controls, (WIDTH // 2 - 180, HEIGHT - 25))

    if game_over:
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(190)
        overlay.fill(BG)
        screen.blit(overlay, (0, 0))

        draw_text_center("GAME OVER", big_font, WHITE, WIDTH // 2, HEIGHT // 2 - 60)
        draw_text_center(f"Final Score: {score}", font, WHITE, WIDTH // 2, HEIGHT // 2)
        draw_text_center("Press ENTER to restart", font, CYAN, WIDTH // 2, HEIGHT // 2 + 45)

    pygame.display.update()

pygame.quit()
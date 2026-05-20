import pygame
import random
import time

pygame.init()

# Window
WIDTH, HEIGHT = 700, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Moving Target Shooting")

clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 30)
big_font = pygame.font.SysFont("Arial", 46)

# Colors
DARK = (20, 20, 30)
WHITE = (255, 255, 255)
RED = (230, 50, 50)
YELLOW = (255, 220, 0)
GREEN = (0, 220, 120)

# Game settings
GAME_TIME = 30
MAX_MISSES = 5

score = 0
misses = 0
combo = 0
level = 1
game_over = False
running = True

start_time = time.time()
time_left = GAME_TIME

target_radius = 40
target_x = 0
target_y = 0
target_speed_x = 0
target_speed_y = 0


def spawn_target():
    x = random.randint(target_radius, WIDTH - target_radius)
    y = random.randint(90 + target_radius, HEIGHT - target_radius)

    speed = 2 + level

    speed_x = random.choice([-speed, speed])
    speed_y = random.choice([-speed, speed])

    return x, y, speed_x, speed_y


def reset_game():
    global score, misses, combo, level
    global game_over, start_time, time_left
    global target_radius, target_x, target_y
    global target_speed_x, target_speed_y

    score = 0
    misses = 0
    combo = 0
    level = 1
    game_over = False
    start_time = time.time()
    time_left = GAME_TIME

    target_radius = 40
    target_x, target_y, target_speed_x, target_speed_y = spawn_target()


reset_game()

while running:
    screen.fill(DARK)

    if not game_over:
        elapsed_time = int(time.time() - start_time)
        time_left = max(0, GAME_TIME - elapsed_time)

        if time_left <= 0:
            game_over = True

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if game_over and event.key == pygame.K_RETURN:
                reset_game()

        if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
            mouse_x, mouse_y = pygame.mouse.get_pos()

            distance = ((mouse_x - target_x) ** 2 + (mouse_y - target_y) ** 2) ** 0.5

            if distance <= target_radius:
                combo += 1

                points = 1 + combo // 3
                score += points

                new_level = score // 5 + 1

                if new_level > level:
                    level = new_level
                    target_radius = max(18, target_radius - 4)

                target_x, target_y, target_speed_x, target_speed_y = spawn_target()

            else:
                misses += 1
                combo = 0

                if misses >= MAX_MISSES:
                    game_over = True

    if not game_over:
        # Move target
        target_x += target_speed_x
        target_y += target_speed_y

        # Bounce from walls
        if target_x - target_radius <= 0 or target_x + target_radius >= WIDTH:
            target_speed_x *= -1

        if target_y - target_radius <= 80 or target_y + target_radius >= HEIGHT:
            target_speed_y *= -1

        # Draw moving target
        pygame.draw.circle(screen, RED, (target_x, target_y), target_radius)
        pygame.draw.circle(screen, WHITE, (target_x, target_y), target_radius - 10)
        pygame.draw.circle(screen, RED, (target_x, target_y), max(5, target_radius - 20))
        pygame.draw.circle(screen, YELLOW, (target_x, target_y), 6)

    # UI
    score_text = font.render(f"Score: {score}", True, WHITE)
    misses_text = font.render(f"Misses: {misses}/{MAX_MISSES}", True, WHITE)
    combo_text = font.render(f"Combo: {combo}", True, GREEN)
    level_text = font.render(f"Level: {level}", True, WHITE)
    timer_text = font.render(f"Time: {time_left}", True, WHITE)

    screen.blit(score_text, (10, 10))
    screen.blit(misses_text, (10, 42))
    screen.blit(combo_text, (250, 10))
    screen.blit(level_text, (250, 42))
    screen.blit(timer_text, (560, 10))

    if game_over:
        game_over_text = big_font.render("GAME OVER", True, WHITE)
        final_score_text = font.render(f"Final Score: {score}", True, WHITE)
        restart_text = font.render("Press ENTER to restart", True, WHITE)

        screen.blit(game_over_text, (WIDTH // 2 - 140, HEIGHT // 2 - 70))
        screen.blit(final_score_text, (WIDTH // 2 - 100, HEIGHT // 2 - 15))
        screen.blit(restart_text, (WIDTH // 2 - 170, HEIGHT // 2 + 30))

    pygame.display.update()
    clock.tick(60)

pygame.quit()
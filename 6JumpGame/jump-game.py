import pygame
import random

pygame.init()

# Window
WIDTH, HEIGHT = 800, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Jump Game")

clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 30)
big_font = pygame.font.SysFont("Arial", 48)

# Colors
SKY = (40, 45, 65)
GROUND = (80, 200, 120)
WHITE = (255, 255, 255)
RED = (230, 70, 70)
BLUE = (80, 160, 255)
GRAY = (150, 150, 150)

# Player
player_width = 45
player_height = 55
player_x = 80
player_y = HEIGHT - 80 - player_height
player_velocity_y = 0
gravity = 0.8
jump_power = -14
is_jumping = False

# Ground
ground_y = HEIGHT - 80

# Obstacles
obstacles = []
obstacle_speed = 6
spawn_timer = 0

# Game variables
score = 0
level = 1
game_over = False
running = True


def reset_game():
    global player_y, player_velocity_y, is_jumping
    global obstacles, obstacle_speed, spawn_timer
    global score, level, game_over

    player_y = ground_y - player_height
    player_velocity_y = 0
    is_jumping = False

    obstacles = []
    obstacle_speed = 6
    spawn_timer = 0

    score = 0
    level = 1
    game_over = False


def create_obstacle():
    width = random.randint(25, 45)
    height = random.randint(35, 70)

    obstacle = pygame.Rect(
        WIDTH,
        ground_y - height,
        width,
        height
    )

    return obstacle


while running:
    screen.fill(SKY)

    # Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if game_over and event.key == pygame.K_RETURN:
                reset_game()

            if not game_over:
                if event.key == pygame.K_SPACE and not is_jumping:
                    player_velocity_y = jump_power
                    is_jumping = True

    if not game_over:
        # Player physics
        player_velocity_y += gravity
        player_y += player_velocity_y

        if player_y >= ground_y - player_height:
            player_y = ground_y - player_height
            player_velocity_y = 0
            is_jumping = False

        player = pygame.Rect(player_x, player_y, player_width, player_height)

        # Spawn obstacles
        spawn_timer += 1

        if spawn_timer > random.randint(60, 100):
            obstacles.append(create_obstacle())
            spawn_timer = 0

        # Move obstacles
        for obstacle in obstacles[:]:
            obstacle.x -= obstacle_speed

            if obstacle.right < 0:
                obstacles.remove(obstacle)
                score += 1

                if score % 5 == 0:
                    level += 1
                    obstacle_speed += 1

            if player.colliderect(obstacle):
                game_over = True

    else:
        player = pygame.Rect(player_x, player_y, player_width, player_height)

    # Draw ground
    pygame.draw.rect(screen, GROUND, (0, ground_y, WIDTH, HEIGHT - ground_y))

    # Draw player
    pygame.draw.rect(screen, BLUE, player)

    # Draw obstacles
    for obstacle in obstacles:
        pygame.draw.rect(screen, RED, obstacle)

    # UI
    score_text = font.render(f"Score: {score}", True, WHITE)
    level_text = font.render(f"Level: {level}", True, WHITE)

    screen.blit(score_text, (10, 10))
    screen.blit(level_text, (10, 45))

    # Hint
    if not game_over and score == 0:
        hint_text = font.render("Press SPACE to jump", True, GRAY)
        screen.blit(hint_text, (WIDTH // 2 - 130, 20))

    # Game over
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
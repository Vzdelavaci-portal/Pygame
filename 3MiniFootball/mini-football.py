import pygame
import random

pygame.init()

# Window
WIDTH, HEIGHT = 800, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mini Football")

clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 32)

# Colors
GREEN = (30, 140, 70)
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
BLUE = (50, 120, 255)

# Player
player_width = 120
player_height = 20
player_x = WIDTH // 2 - player_width // 2
player_y = HEIGHT - 40
player_speed = 8

# Ball
ball_size = 20
ball_x = WIDTH // 2
ball_y = HEIGHT // 2

ball_speed_x = random.choice([-5, 5])
ball_speed_y = -5

score = 0
game_over = False
running = True


def reset_game():
    global player_x
    global ball_x, ball_y
    global ball_speed_x, ball_speed_y
    global score
    global game_over

    player_x = WIDTH // 2 - player_width // 2

    ball_x = WIDTH // 2
    ball_y = HEIGHT // 2

    ball_speed_x = random.choice([-5, 5])
    ball_speed_y = -5

    score = 0
    game_over = False


while running:
    screen.fill(GREEN)

    # Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if game_over and event.key == pygame.K_RETURN:
                reset_game()

    keys = pygame.key.get_pressed()

    if not game_over:
        # Player movement
        if keys[pygame.K_LEFT] and player_x > 0:
            player_x -= player_speed

        if keys[pygame.K_RIGHT] and player_x < WIDTH - player_width:
            player_x += player_speed

        # Ball movement
        ball_x += ball_speed_x
        ball_y += ball_speed_y

        # Wall collision
        if ball_x <= 0 or ball_x >= WIDTH - ball_size:
            ball_speed_x *= -1

        if ball_y <= 0:
            ball_speed_y *= -1

        # Player collision
        player_rect = pygame.Rect(
            player_x,
            player_y,
            player_width,
            player_height
        )

        ball_rect = pygame.Rect(
            ball_x,
            ball_y,
            ball_size,
            ball_size
        )

        if ball_rect.colliderect(player_rect):
            ball_speed_y *= -1
            score += 1

        # Game over
        if ball_y > HEIGHT:
            game_over = True

    # Draw field line
    pygame.draw.line(screen, WHITE, (0, HEIGHT // 2), (WIDTH, HEIGHT // 2), 3)

    # Draw player
    pygame.draw.rect(screen, BLUE, player_rect)

    # Draw ball
    pygame.draw.ellipse(screen, WHITE, ball_rect)

    # Draw score
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

    # Game over text
    if game_over:
        game_over_text = font.render("GAME OVER", True, WHITE)
        restart_text = font.render("Press ENTER to restart", True, WHITE)

        screen.blit(game_over_text, (WIDTH // 2 - 120, HEIGHT // 2 - 40))
        screen.blit(restart_text, (WIDTH // 2 - 190, HEIGHT // 2 + 10))

    pygame.display.update()
    clock.tick(60)

pygame.quit()
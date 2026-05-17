#Space Shooter

import pygame
import random

pygame.init()

# Window
WIDTH, HEIGHT = 600, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter")

clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 32)

# Colors
BLACK = (15, 15, 20)
WHITE = (255, 255, 255)
GREEN = (0, 255, 100)
RED = (255, 60, 60)
YELLOW = (255, 220, 0)

# Player
player_width = 60
player_height = 20
player_x = WIDTH // 2 - player_width // 2
player_y = HEIGHT - 60
player_speed = 6

# Bullets
bullets = []
bullet_speed = 8

# Enemies
enemies = []
enemy_speed = 4
enemy_spawn_timer = 0

score = 0
game_over = False
running = True


def reset_game():
    global player_x, bullets, enemies, score, game_over

    player_x = WIDTH // 2 - player_width // 2
    bullets = []
    enemies = []
    score = 0
    game_over = False


while running:
    screen.fill(BLACK)

    # Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if game_over and event.key == pygame.K_RETURN:
                reset_game()

            if not game_over:
                if event.key == pygame.K_SPACE:
                    bullet = pygame.Rect(
                        player_x + player_width // 2 - 3,
                        player_y,
                        6,
                        15
                    )
                    bullets.append(bullet)

    keys = pygame.key.get_pressed()

    if not game_over:
        # Player movement
        if keys[pygame.K_LEFT] and player_x > 0:
            player_x -= player_speed

        if keys[pygame.K_RIGHT] and player_x < WIDTH - player_width:
            player_x += player_speed

        # Spawn enemies
        enemy_spawn_timer += 1

        if enemy_spawn_timer > 30:
            enemy_x = random.randint(0, WIDTH - 40)

            enemy = pygame.Rect(enemy_x, -40, 40, 40)
            enemies.append(enemy)

            enemy_spawn_timer = 0

        # Move bullets
        for bullet in bullets[:]:
            bullet.y -= bullet_speed

            if bullet.y < 0:
                bullets.remove(bullet)

        # Move enemies
        for enemy in enemies[:]:
            enemy.y += enemy_speed

            if enemy.y > HEIGHT:
                game_over = True

            # Collision with player
            player_rect = pygame.Rect(
                player_x,
                player_y,
                player_width,
                player_height
            )

            if enemy.colliderect(player_rect):
                game_over = True

            # Bullet collision
            for bullet in bullets[:]:
                if enemy.colliderect(bullet):
                    if enemy in enemies:
                        enemies.remove(enemy)

                    if bullet in bullets:
                        bullets.remove(bullet)

                    score += 1
                    break

    # Draw player
    pygame.draw.rect(
        screen,
        GREEN,
        (player_x, player_y, player_width, player_height)
    )

    # Draw bullets
    for bullet in bullets:
        pygame.draw.rect(screen, YELLOW, bullet)

    # Draw enemies
    for enemy in enemies:
        pygame.draw.rect(screen, RED, enemy)

    # Score
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

    # Game over
    if game_over:
        game_over_text = font.render("GAME OVER", True, WHITE)
        restart_text = font.render("Press ENTER to restart", True, WHITE)

        screen.blit(game_over_text, (WIDTH // 2 - 110, HEIGHT // 2 - 30))
        screen.blit(restart_text, (WIDTH // 2 - 180, HEIGHT // 2 + 10))

    pygame.display.update()
    clock.tick(60)

pygame.quit()
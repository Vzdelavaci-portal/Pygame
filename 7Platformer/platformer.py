import pygame
import random

pygame.init()

# Window
WIDTH, HEIGHT = 900, 520
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Modern Platformer")

clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 28)
big_font = pygame.font.SysFont("Arial", 50)

# Colors
BG = (18, 22, 38)
PLATFORM = (70, 90, 140)
PLATFORM_LIGHT = (100, 130, 210)
PLAYER = (80, 180, 255)
ENEMY = (255, 80, 100)
COIN = (255, 210, 60)
GOAL = (80, 255, 160)
WHITE = (255, 255, 255)
GRAY = (150, 160, 180)

# Player
player = pygame.Rect(70, 390, 38, 48)
player_speed = 6
player_velocity_y = 0
gravity = 0.8
jump_power = -15
on_ground = False

# Game
score = 0
game_over = False
level_complete = False
running = True

# Platforms
platforms = [
    pygame.Rect(0, 470, 900, 50),
    pygame.Rect(140, 380, 160, 22),
    pygame.Rect(360, 310, 160, 22),
    pygame.Rect(580, 240, 170, 22),
    pygame.Rect(240, 190, 140, 22),
    pygame.Rect(40, 260, 130, 22),
]

# Coins
coins = [
    pygame.Rect(190, 340, 20, 20),
    pygame.Rect(420, 270, 20, 20),
    pygame.Rect(650, 200, 20, 20),
    pygame.Rect(290, 150, 20, 20),
    pygame.Rect(85, 220, 20, 20),
]

# Enemy
enemy = pygame.Rect(600, 430, 40, 40)
enemy_speed = 3
enemy_left_limit = 520
enemy_right_limit = 820

# Goal
goal = pygame.Rect(810, 395, 45, 75)


def reset_game():
    global player, player_velocity_y, on_ground
    global score, game_over, level_complete
    global coins, enemy, enemy_speed

    player.x = 70
    player.y = 390
    player_velocity_y = 0
    on_ground = False

    score = 0
    game_over = False
    level_complete = False

    coins = [
        pygame.Rect(190, 340, 20, 20),
        pygame.Rect(420, 270, 20, 20),
        pygame.Rect(650, 200, 20, 20),
        pygame.Rect(290, 150, 20, 20),
        pygame.Rect(85, 220, 20, 20),
    ]

    enemy.x = 600
    enemy.y = 430
    enemy_speed = 3


def draw_background():
    screen.fill(BG)

    # simple modern stars / particles
    for x, y, size in [
        (80, 80, 3), (180, 120, 2), (310, 70, 3), (500, 110, 2),
        (700, 75, 3), (820, 140, 2), (120, 180, 2), (760, 190, 3)
    ]:
        pygame.draw.circle(screen, GRAY, (x, y), size)


def draw_platform(platform):
    pygame.draw.rect(screen, PLATFORM, platform, border_radius=8)
    highlight = pygame.Rect(platform.x, platform.y, platform.width, 5)
    pygame.draw.rect(screen, PLATFORM_LIGHT, highlight, border_radius=8)


def draw_player():
    pygame.draw.rect(screen, PLAYER, player, border_radius=10)
    pygame.draw.circle(screen, WHITE, (player.x + 27, player.y + 15), 4)


def draw_enemy():
    pygame.draw.rect(screen, ENEMY, enemy, border_radius=10)
    pygame.draw.circle(screen, WHITE, (enemy.x + 12, enemy.y + 14), 4)
    pygame.draw.circle(screen, WHITE, (enemy.x + 28, enemy.y + 14), 4)


def draw_coin(coin):
    pygame.draw.circle(screen, COIN, coin.center, 10)
    pygame.draw.circle(screen, WHITE, coin.center, 4)


def draw_goal():
    pygame.draw.rect(screen, GOAL, goal, border_radius=8)
    pygame.draw.rect(screen, WHITE, (goal.x + 12, goal.y + 15, 20, 45), border_radius=5)


while running:
    clock.tick(60)
    draw_background()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if (game_over or level_complete) and event.key == pygame.K_RETURN:
                reset_game()

            if not game_over and not level_complete:
                if event.key == pygame.K_SPACE and on_ground:
                    player_velocity_y = jump_power
                    on_ground = False

    keys = pygame.key.get_pressed()

    if not game_over and not level_complete:
        # Horizontal movement
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player.x -= player_speed

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player.x += player_speed

        # Keep player inside screen
        if player.left < 0:
            player.left = 0
        if player.right > WIDTH:
            player.right = WIDTH

        # Gravity
        player_velocity_y += gravity
        player.y += player_velocity_y
        on_ground = False

        # Platform collisions
        for platform in platforms:
            if player.colliderect(platform) and player_velocity_y >= 0:
                if player.bottom - player_velocity_y <= platform.top + 5:
                    player.bottom = platform.top
                    player_velocity_y = 0
                    on_ground = True

        # Enemy movement
        enemy.x += enemy_speed

        if enemy.left <= enemy_left_limit or enemy.right >= enemy_right_limit:
            enemy_speed *= -1

        # Coin collection
        for coin in coins[:]:
            if player.colliderect(coin):
                coins.remove(coin)
                score += 1

        # Enemy collision
        if player.colliderect(enemy):
            game_over = True

        # Fall check
        if player.top > HEIGHT:
            game_over = True

        # Goal check
        if player.colliderect(goal) and score == 5:
            level_complete = True

    # Draw objects
    for platform in platforms:
        draw_platform(platform)

    draw_goal()

    for coin in coins:
        draw_coin(coin)

    draw_enemy()
    draw_player()

    # UI
    score_text = font.render(f"Coins: {score}/5", True, WHITE)
    screen.blit(score_text, (20, 20))

    hint_text = font.render("A/D or ARROWS = move   SPACE = jump", True, GRAY)
    screen.blit(hint_text, (250, 20))

    if game_over:
        text = big_font.render("GAME OVER", True, WHITE)
        restart = font.render("Press ENTER to restart", True, WHITE)

        screen.blit(text, (WIDTH // 2 - 150, HEIGHT // 2 - 50))
        screen.blit(restart, (WIDTH // 2 - 150, HEIGHT // 2 + 10))

    if level_complete:
        text = big_font.render("LEVEL COMPLETE!", True, WHITE)
        restart = font.render("Press ENTER to play again", True, WHITE)

        screen.blit(text, (WIDTH // 2 - 210, HEIGHT // 2 - 50))
        screen.blit(restart, (WIDTH // 2 - 170, HEIGHT // 2 + 10))

    pygame.display.update()

pygame.quit()
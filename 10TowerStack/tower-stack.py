import pygame
import random

pygame.init()

# Window
WIDTH, HEIGHT = 700, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tower Stack")

clock = pygame.time.Clock()

# Fonts
font = pygame.font.SysFont("Arial", 28)
big_font = pygame.font.SysFont("Arial", 56)
small_font = pygame.font.SysFont("Arial", 22)

# Colors
SKY_TOP = (90, 150, 220)
SKY_BOTTOM = (245, 180, 120)
WHITE = (255, 255, 255)
DARK = (35, 40, 55)
GRAY = (120, 130, 150)
RED = (240, 90, 90)

# Game settings
BLOCK_HEIGHT = 32
START_BLOCK_WIDTH = 260
BLOCK_SPEED_START = 4

score = 0
game_over = False
running = True

camera_offset = 0
block_speed = BLOCK_SPEED_START

tower_blocks = []
moving_block = None
moving_direction = 1


def get_random_block_color():
    colors = [
        (80, 140, 220),
        (90, 190, 150),
        (240, 170, 80),
        (180, 120, 220),
        (230, 100, 120),
        (100, 200, 230),
    ]
    return random.choice(colors)


def reset_game():
    global score, game_over, camera_offset, block_speed
    global tower_blocks, moving_block, moving_direction

    score = 0
    game_over = False
    camera_offset = 0
    block_speed = BLOCK_SPEED_START
    moving_direction = 1

    base_block = {
        "x": WIDTH // 2 - START_BLOCK_WIDTH // 2,
        "y": HEIGHT - 90,
        "width": START_BLOCK_WIDTH,
        "height": BLOCK_HEIGHT,
        "color": (70, 80, 100)
    }

    tower_blocks = [base_block]
    create_moving_block()


def create_moving_block():
    global moving_block, moving_direction

    last_block = tower_blocks[-1]

    moving_direction = random.choice([-1, 1])

    if moving_direction == 1:
        start_x = -last_block["width"]
    else:
        start_x = WIDTH

    moving_block = {
        "x": start_x,
        "y": last_block["y"] - BLOCK_HEIGHT,
        "width": last_block["width"],
        "height": BLOCK_HEIGHT,
        "color": get_random_block_color()
    }


def place_block():
    global moving_block, score, game_over
    global camera_offset, block_speed

    last_block = tower_blocks[-1]

    moving_left = moving_block["x"]
    moving_right = moving_block["x"] + moving_block["width"]

    last_left = last_block["x"]
    last_right = last_block["x"] + last_block["width"]

    overlap_left = max(moving_left, last_left)
    overlap_right = min(moving_right, last_right)

    overlap_width = overlap_right - overlap_left

    if overlap_width <= 0:
        game_over = True
        return

    moving_block["x"] = overlap_left
    moving_block["width"] = overlap_width

    tower_blocks.append(moving_block)
    score += 1

    if score % 4 == 0:
        block_speed += 0.7

    if moving_block["y"] - camera_offset < 180:
        camera_offset -= BLOCK_HEIGHT

    create_moving_block()


def draw_gradient_background():
    for y in range(HEIGHT):
        ratio = y / HEIGHT

        r = int(SKY_TOP[0] * (1 - ratio) + SKY_BOTTOM[0] * ratio)
        g = int(SKY_TOP[1] * (1 - ratio) + SKY_BOTTOM[1] * ratio)
        b = int(SKY_TOP[2] * (1 - ratio) + SKY_BOTTOM[2] * ratio)

        pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))


def draw_city_background():
    pygame.draw.circle(screen, (255, 230, 150), (570, 90), 40)

    buildings = [
        (20, 420, 80, 180),
        (120, 360, 90, 240),
        (240, 400, 70, 200),
        (520, 380, 80, 220),
        (620, 430, 70, 170),
    ]

    for x, y, w, h in buildings:
        pygame.draw.rect(screen, (45, 55, 80), (x, y, w, h))

        for wx in range(x + 15, x + w - 10, 25):
            for wy in range(y + 20, y + h - 10, 35):
                pygame.draw.rect(screen, (255, 220, 120), (wx, wy, 10, 14))


def draw_block(block):
    visible_y = block["y"] + camera_offset

    rect = pygame.Rect(
        block["x"],
        visible_y,
        block["width"],
        block["height"]
    )

    pygame.draw.rect(screen, block["color"], rect, border_radius=6)

    top_highlight = pygame.Rect(rect.x, rect.y, rect.width, 6)
    pygame.draw.rect(screen, WHITE, top_highlight, border_radius=6)

    # Small windows
    for wx in range(rect.x + 12, rect.x + rect.width - 10, 32):
        pygame.draw.rect(
            screen,
            (240, 245, 255),
            (wx, rect.y + 11, 10, 10),
            border_radius=2
        )


def draw_ui():
    score_text = font.render(f"Floors: {score}", True, DARK)
    speed_text = small_font.render(f"Speed: {block_speed:.1f}", True, DARK)

    screen.blit(score_text, (20, 20))
    screen.blit(speed_text, (20, 55))

    hint = small_font.render("SPACE or CLICK = place block", True, DARK)
    screen.blit(hint, (WIDTH // 2 - 130, 25))


reset_game()

while running:
    clock.tick(60)

    draw_gradient_background()
    draw_city_background()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if game_over and event.key == pygame.K_RETURN:
                reset_game()

            elif not game_over and event.key == pygame.K_SPACE:
                place_block()

        if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
            place_block()

    if not game_over:
        moving_block["x"] += block_speed * moving_direction

        if moving_direction == 1 and moving_block["x"] > WIDTH:
            moving_block["x"] = -moving_block["width"]

        elif moving_direction == -1 and moving_block["x"] + moving_block["width"] < 0:
            moving_block["x"] = WIDTH

    for block in tower_blocks:
        draw_block(block)

    if not game_over:
        draw_block(moving_block)

    draw_ui()

    if game_over:
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(190)
        overlay.fill((20, 25, 40))
        screen.blit(overlay, (0, 0))

        title = big_font.render("TOWER FALLS!", True, WHITE)
        score_info = font.render(f"Final Floors: {score}", True, WHITE)
        restart = font.render("Press ENTER to restart", True, WHITE)

        screen.blit(title, (WIDTH // 2 - 175, HEIGHT // 2 - 80))
        screen.blit(score_info, (WIDTH // 2 - 105, HEIGHT // 2 - 15))
        screen.blit(restart, (WIDTH // 2 - 165, HEIGHT // 2 + 35))

    pygame.display.update()

pygame.quit()
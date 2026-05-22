import pygame
import random

pygame.init()

# Window
WIDTH, HEIGHT = 800, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong Game")

clock = pygame.time.Clock()

# Fonts
font = pygame.font.SysFont("Arial", 30)
big_font = pygame.font.SysFont("Arial", 52)
small_font = pygame.font.SysFont("Arial", 22)

# Colors
BLACK = (20, 20, 25)
WHITE = (255, 255, 255)
BLUE = (60, 140, 255)
RED = (255, 80, 80)
GRAY = (140, 140, 140)
GREEN = (80, 220, 120)
YELLOW = (255, 220, 80)

# Paddle settings
PADDLE_WIDTH = 15
PADDLE_HEIGHT = 90
PLAYER_SPEED = 7

# Ball settings
BALL_SIZE = 16

player = pygame.Rect(40, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
opponent = pygame.Rect(WIDTH - 55, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
ball = pygame.Rect(WIDTH // 2 - BALL_SIZE // 2, HEIGHT // 2 - BALL_SIZE // 2, BALL_SIZE, BALL_SIZE)

# Game variables
game_state = "mode_select"
game_mode = None
win_score = None
difficulty = None

player_score = 0
opponent_score = 0

ball_speed_x = 0
ball_speed_y = 0
ai_speed = 0
ai_error = 0
ball_base_speed = 0

running = True


def draw_text(text, used_font, color, x, y):
    rendered = used_font.render(text, True, color)
    rect = rendered.get_rect(center=(x, y))
    screen.blit(rendered, rect)


def set_difficulty(level):
    global ai_speed, ai_error, ball_base_speed

    if level == "easy":
        ai_speed = 3
        ai_error = 70
        ball_base_speed = 4

    elif level == "normal":
        ai_speed = 4
        ai_error = 45
        ball_base_speed = 5

    elif level == "hard":
        ai_speed = 5
        ai_error = 20
        ball_base_speed = 6


def reset_ball():
    global ball_speed_x, ball_speed_y

    ball.center = (WIDTH // 2, HEIGHT // 2)

    ball_speed_x = ball_base_speed * random.choice([-1, 1])
    ball_speed_y = random.choice([-ball_base_speed, -ball_base_speed + 1, ball_base_speed - 1, ball_base_speed])


def reset_game():
    global player_score, opponent_score

    player_score = 0
    opponent_score = 0

    player.centery = HEIGHT // 2
    opponent.centery = HEIGHT // 2

    reset_ball()


def draw_mode_select():
    screen.fill(BLACK)

    draw_text("PONG GAME", big_font, WHITE, WIDTH // 2, 80)
    draw_text("Choose game mode", font, WHITE, WIDTH // 2, 150)

    draw_text("1 - Player vs Computer", font, BLUE, WIDTH // 2, 230)
    draw_text("2 - Player vs Player", font, RED, WIDTH // 2, 280)

    draw_text("Step 1/3", small_font, GRAY, WIDTH // 2, 440)


def draw_score_select():
    screen.fill(BLACK)

    draw_text("Choose winning score", big_font, WHITE, WIDTH // 2, 90)

    selected_mode = "Player vs Computer" if game_mode == "ai" else "Player vs Player"
    draw_text(f"Selected mode: {selected_mode}", small_font, GRAY, WIDTH // 2, 145)

    draw_text("3 - First to 3 points", font, WHITE, WIDTH // 2, 230)
    draw_text("5 - First to 5 points", font, WHITE, WIDTH // 2, 280)
    draw_text("7 - First to 7 points", font, WHITE, WIDTH // 2, 330)

    draw_text("ESC - Back", small_font, GRAY, WIDTH // 2, 440)
    draw_text("Step 2/3", small_font, GRAY, WIDTH // 2, 470)


def draw_difficulty_select():
    screen.fill(BLACK)

    draw_text("Choose difficulty", big_font, WHITE, WIDTH // 2, 80)

    selected_mode = "Player vs Computer" if game_mode == "ai" else "Player vs Player"
    draw_text(f"Mode: {selected_mode}", small_font, GRAY, WIDTH // 2, 135)
    draw_text(f"Winning score: {win_score}", small_font, GRAY, WIDTH // 2, 165)

    draw_text("1 - Easy", font, GREEN, WIDTH // 2, 240)
    draw_text("2 - Normal", font, YELLOW, WIDTH // 2, 290)
    draw_text("3 - Hard", font, RED, WIDTH // 2, 340)

    if game_mode == "ai":
        draw_text("Difficulty changes AI skill and ball speed", small_font, GRAY, WIDTH // 2, 395)
    else:
        draw_text("Difficulty changes only ball speed", small_font, GRAY, WIDTH // 2, 395)

    draw_text("ESC - Back", small_font, GRAY, WIDTH // 2, 440)
    draw_text("Step 3/3", small_font, GRAY, WIDTH // 2, 470)


def draw_game():
    screen.fill(BLACK)

    for y in range(0, HEIGHT, 30):
        pygame.draw.rect(screen, WHITE, (WIDTH // 2 - 2, y, 4, 15))

    pygame.draw.rect(screen, BLUE, player)
    pygame.draw.rect(screen, RED, opponent)
    pygame.draw.ellipse(screen, WHITE, ball)

    draw_text(str(player_score), font, WHITE, WIDTH // 2 - 80, 30)
    draw_text(str(opponent_score), font, WHITE, WIDTH // 2 + 80, 30)

    if game_mode == "ai":
        controls = "Player: W/S"
    else:
        controls = "Player 1: W/S    Player 2: UP/DOWN"

    draw_text(controls, small_font, GRAY, WIDTH // 2, HEIGHT - 20)


def draw_game_over():
    screen.fill(BLACK)

    if player_score > opponent_score:
        winner = "PLAYER 1 WINS!"
    else:
        winner = "COMPUTER WINS!" if game_mode == "ai" else "PLAYER 2 WINS!"

    draw_text(winner, big_font, WHITE, WIDTH // 2, HEIGHT // 2 - 70)
    draw_text(f"Final Score: {player_score} : {opponent_score}", font, WHITE, WIDTH // 2, HEIGHT // 2 - 10)

    draw_text("ENTER - Play again", font, WHITE, WIDTH // 2, HEIGHT // 2 + 45)
    draw_text("ESC - Back to menu", small_font, GRAY, WIDTH // 2, HEIGHT // 2 + 85)


def move_ai():
    # AI only reacts when ball is coming towards it
    if ball_speed_x > 0 and ball.x > WIDTH // 2:
        target_y = ball.centery + random.randint(-ai_error, ai_error)

        if opponent.centery < target_y - 10:
            opponent.y += ai_speed
        elif opponent.centery > target_y + 10:
            opponent.y -= ai_speed
    else:
        # AI slowly returns to center
        if opponent.centery < HEIGHT // 2 - 25:
            opponent.y += max(1, ai_speed // 2)
        elif opponent.centery > HEIGHT // 2 + 25:
            opponent.y -= max(1, ai_speed // 2)

    if opponent.top < 0:
        opponent.top = 0
    if opponent.bottom > HEIGHT:
        opponent.bottom = HEIGHT


def move_ball():
    global ball_speed_x, ball_speed_y
    global player_score, opponent_score
    global game_state

    ball.x += ball_speed_x
    ball.y += ball_speed_y

    if ball.top <= 0 or ball.bottom >= HEIGHT:
        ball_speed_y *= -1

    if ball.colliderect(player) and ball_speed_x < 0:
        ball_speed_x *= -1
        ball_speed_y += random.choice([-1, 0, 1])

    if ball.colliderect(opponent) and ball_speed_x > 0:
        ball_speed_x *= -1
        ball_speed_y += random.choice([-1, 0, 1])

    if ball.left <= 0:
        opponent_score += 1
        reset_ball()

    if ball.right >= WIDTH:
        player_score += 1
        reset_ball()

    if player_score >= win_score or opponent_score >= win_score:
        game_state = "game_over"


while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if game_state == "mode_select":
                if event.key == pygame.K_1:
                    game_mode = "ai"
                    game_state = "score_select"

                elif event.key == pygame.K_2:
                    game_mode = "pvp"
                    game_state = "score_select"

            elif game_state == "score_select":
                if event.key == pygame.K_3:
                    win_score = 3
                    game_state = "difficulty_select"

                elif event.key == pygame.K_5:
                    win_score = 5
                    game_state = "difficulty_select"

                elif event.key == pygame.K_7:
                    win_score = 7
                    game_state = "difficulty_select"

                elif event.key == pygame.K_ESCAPE:
                    game_state = "mode_select"

            elif game_state == "difficulty_select":
                if event.key == pygame.K_1:
                    difficulty = "easy"
                    set_difficulty(difficulty)
                    reset_game()
                    game_state = "game"

                elif event.key == pygame.K_2:
                    difficulty = "normal"
                    set_difficulty(difficulty)
                    reset_game()
                    game_state = "game"

                elif event.key == pygame.K_3:
                    difficulty = "hard"
                    set_difficulty(difficulty)
                    reset_game()
                    game_state = "game"

                elif event.key == pygame.K_ESCAPE:
                    game_state = "score_select"

            elif game_state == "game_over":
                if event.key == pygame.K_RETURN:
                    reset_game()
                    game_state = "game"

                elif event.key == pygame.K_ESCAPE:
                    game_mode = None
                    win_score = None
                    difficulty = None
                    game_state = "mode_select"

    keys = pygame.key.get_pressed()

    if game_state == "mode_select":
        draw_mode_select()

    elif game_state == "score_select":
        draw_score_select()

    elif game_state == "difficulty_select":
        draw_difficulty_select()

    elif game_state == "game":
        if keys[pygame.K_w] and player.top > 0:
            player.y -= PLAYER_SPEED

        if keys[pygame.K_s] and player.bottom < HEIGHT:
            player.y += PLAYER_SPEED

        if game_mode == "ai":
            move_ai()
        else:
            if keys[pygame.K_UP] and opponent.top > 0:
                opponent.y -= PLAYER_SPEED

            if keys[pygame.K_DOWN] and opponent.bottom < HEIGHT:
                opponent.y += PLAYER_SPEED

        move_ball()
        draw_game()

    elif game_state == "game_over":
        draw_game_over()

    pygame.display.update()

pygame.quit()
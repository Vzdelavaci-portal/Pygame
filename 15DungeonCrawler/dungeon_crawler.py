import pygame
import random
import math

pygame.init()

WIDTH, HEIGHT = 960, 640
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dungeon Crawler V1.1")

clock = pygame.time.Clock()

font = pygame.font.SysFont("Arial", 26)
big_font = pygame.font.SysFont("Arial", 54)
small_font = pygame.font.SysFont("Arial", 20)

BLACK = (8, 8, 12)
FLOOR = (42, 38, 34)
FLOOR_DARK = (32, 29, 27)
WALL = (86, 76, 68)
WALL_DARK = (42, 36, 34)
PLAYER_BLUE = (70, 140, 240)
PLAYER_DARK = (30, 45, 85)
ARMOR = (210, 220, 230)
SLIME = (70, 220, 120)
SKELETON = (220, 220, 210)
CHEST = (160, 95, 45)
GOLD = (255, 210, 70)
RED = (255, 80, 90)
WHITE = (255, 255, 255)
GRAY = (150, 150, 160)
GREEN = (90, 255, 150)
PURPLE = (170, 110, 255)
SWORD = (230, 235, 255)

TILE = 40
MAP_WIDTH = 24
MAP_HEIGHT = 16

game_state = "playing"
running = True

player = pygame.Rect(80, 80, 30, 34)
player_speed = 4
player_hp = 5
max_hp = 5
player_damage = 1
player_direction = "right"

attack_cooldown = 0
attack_timer = 0
attack_arc = None

floor_number = 1
gold = 0
xp = 0
level = 1
xp_needed = 6

walls = []
floor_tiles = []
enemies = []
chests = []
coins = []
particles = []
floating_texts = []

exit_rect = None
exit_open = False
screen_shake = 0


def draw_center(text, used_font, color, y):
    rendered = used_font.render(text, True, color)
    rect = rendered.get_rect(center=(WIDTH // 2, y))
    screen.blit(rendered, rect)


def create_particles(x, y, color, count=18):
    for _ in range(count):
        particles.append({
            "x": x,
            "y": y,
            "vx": random.uniform(-3, 3),
            "vy": random.uniform(-3, 3),
            "life": random.randint(18, 35),
            "color": color
        })


def add_text(text, x, y, color):
    floating_texts.append({
        "text": text,
        "x": x,
        "y": y,
        "life": 45,
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


def update_floating_texts():
    for item in floating_texts[:]:
        item["y"] -= 0.7
        item["life"] -= 1

        if item["life"] <= 0:
            floating_texts.remove(item)


def draw_floating_texts():
    for item in floating_texts:
        rendered = small_font.render(item["text"], True, item["color"])
        screen.blit(rendered, (item["x"], item["y"]))


def generate_dungeon():
    global walls, floor_tiles, enemies, chests, coins
    global exit_rect, exit_open

    walls = []
    floor_tiles = []
    enemies = []
    chests = []
    coins = []
    exit_open = False

    layout = [[1 for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]
    rooms = []

    for _ in range(13):
        room_w = random.randint(4, 7)
        room_h = random.randint(3, 5)
        room_x = random.randint(1, MAP_WIDTH - room_w - 2)
        room_y = random.randint(2, MAP_HEIGHT - room_h - 2)

        new_room = pygame.Rect(room_x, room_y, room_w, room_h)

        if any(new_room.colliderect(room.inflate(1, 1)) for room in rooms):
            continue

        rooms.append(new_room)

        for y in range(room_y, room_y + room_h):
            for x in range(room_x, room_x + room_w):
                layout[y][x] = 0

    for i in range(1, len(rooms)):
        x1, y1 = rooms[i - 1].center
        x2, y2 = rooms[i].center

        for x in range(min(x1, x2), max(x1, x2) + 1):
            layout[y1][x] = 0

        for y in range(min(y1, y2), max(y1, y2) + 1):
            layout[y][x2] = 0

    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            rect = pygame.Rect(x * TILE, y * TILE, TILE, TILE)

            if layout[y][x] == 1:
                walls.append(rect)
            else:
                floor_tiles.append(rect)

    start_room = rooms[0]
    player.center = (start_room.centerx * TILE, start_room.centery * TILE)

    end_room = rooms[-1]
    exit_rect = pygame.Rect(
        end_room.centerx * TILE - 16,
        end_room.centery * TILE - 16,
        32,
        32
    )

    enemy_count = 4 + floor_number * 2

    for _ in range(enemy_count):
        room = random.choice(rooms[1:])
        x = random.randint(room.left, room.right - 1) * TILE + 5
        y = random.randint(room.top, room.bottom - 1) * TILE + 5

        enemy_type = random.choice(["slime", "skeleton"])

        if enemy_type == "slime":
            hp = 2 + floor_number // 2
            speed = 1.05
            size = 30
        else:
            hp = 3 + floor_number // 2
            speed = 1.45
            size = 32

        enemies.append({
            "rect": pygame.Rect(x, y, size, size),
            "type": enemy_type,
            "hp": hp,
            "max_hp": hp,
            "speed": speed,
            "hit_timer": 0
        })

    for _ in range(3):
        room = random.choice(rooms[1:])
        x = random.randint(room.left, room.right - 1) * TILE + 6
        y = random.randint(room.top, room.bottom - 1) * TILE + 8

        chests.append({
            "rect": pygame.Rect(x, y, 32, 26),
            "opened": False
        })


def reset_game():
    global floor_number, gold, xp, level, xp_needed
    global player_hp, max_hp, player_speed, player_damage
    global game_state, particles, floating_texts
    global player_direction, attack_cooldown, attack_timer, attack_arc

    floor_number = 1
    gold = 0
    xp = 0
    level = 1
    xp_needed = 6

    max_hp = 5
    player_hp = max_hp
    player_speed = 4
    player_damage = 1
    player_direction = "right"

    attack_cooldown = 0
    attack_timer = 0
    attack_arc = None

    particles = []
    floating_texts = []

    game_state = "playing"
    generate_dungeon()


def move_with_collision(rect, dx, dy):
    rect.x += dx

    for wall in walls:
        if rect.colliderect(wall):
            if dx > 0:
                rect.right = wall.left
            elif dx < 0:
                rect.left = wall.right

    rect.y += dy

    for wall in walls:
        if rect.colliderect(wall):
            if dy > 0:
                rect.bottom = wall.top
            elif dy < 0:
                rect.top = wall.bottom


def get_attack_rect():
    if player_direction == "up":
        return pygame.Rect(player.centerx - 24, player.top - 44, 48, 50)

    if player_direction == "down":
        return pygame.Rect(player.centerx - 24, player.bottom - 4, 48, 50)

    if player_direction == "left":
        return pygame.Rect(player.left - 44, player.centery - 24, 50, 48)

    return pygame.Rect(player.right - 4, player.centery - 24, 50, 48)


def attack():
    global screen_shake, attack_timer, attack_arc

    attack_arc = get_attack_rect()
    attack_timer = 9

    hit = False

    for enemy in enemies[:]:
        if attack_arc.colliderect(enemy["rect"]):
            enemy["hp"] -= player_damage
            enemy["hit_timer"] = 8
            hit = True

            create_particles(enemy["rect"].centerx, enemy["rect"].centery, RED, 14)
            add_text(f"-{player_damage}", enemy["rect"].x, enemy["rect"].y - 12, RED)

            if enemy["hp"] <= 0:
                kill_enemy(enemy)

    if hit:
        screen_shake = 5


def kill_enemy(enemy):
    global xp, level, xp_needed, game_state

    if enemy in enemies:
        enemies.remove(enemy)

    color = SLIME if enemy["type"] == "slime" else SKELETON
    create_particles(enemy["rect"].centerx, enemy["rect"].centery, color, 24)

    xp += 2
    add_text("+XP", enemy["rect"].x, enemy["rect"].y, GREEN)

    if random.random() < 0.7:
        coins.append({
            "rect": pygame.Rect(enemy["rect"].centerx - 8, enemy["rect"].centery - 8, 16, 16),
            "value": random.randint(3, 8)
        })

    if xp >= xp_needed:
        xp -= xp_needed
        level += 1
        xp_needed = int(xp_needed * 1.4)
        game_state = "upgrade"


def open_chest(chest):
    global gold, player_hp

    if chest["opened"]:
        return

    chest["opened"] = True
    reward = random.choice(["gold", "heal", "big_gold"])

    if reward == "gold":
        amount = random.randint(20, 45)
        gold += amount
        add_text(f"+{amount} gold", chest["rect"].x, chest["rect"].y - 15, GOLD)

    elif reward == "big_gold":
        amount = random.randint(60, 90)
        gold += amount
        add_text(f"+{amount} gold!", chest["rect"].x, chest["rect"].y - 15, GOLD)

    else:
        player_hp = min(max_hp, player_hp + 1)
        add_text("+1 HP", chest["rect"].x, chest["rect"].y - 15, RED)

    create_particles(chest["rect"].centerx, chest["rect"].centery, GOLD, 28)


def apply_upgrade(choice):
    global player_damage, player_speed, max_hp, player_hp, game_state

    if choice == 1:
        player_damage += 1
        add_text("Damage Up!", player.x, player.y - 20, RED)

    elif choice == 2:
        max_hp += 1
        player_hp = max_hp
        add_text("Max HP Up!", player.x, player.y - 20, RED)

    elif choice == 3:
        player_speed += 0.5
        add_text("Speed Up!", player.x, player.y - 20, GREEN)

    game_state = "playing"


def update_enemies():
    global player_hp, game_state, screen_shake

    for enemy in enemies[:]:
        if enemy["hit_timer"] > 0:
            enemy["hit_timer"] -= 1

        dx = player.centerx - enemy["rect"].centerx
        dy = player.centery - enemy["rect"].centery
        distance = math.hypot(dx, dy)

        if distance < 360:
            if distance != 0:
                dx /= distance
                dy /= distance

            old_x = enemy["rect"].x
            old_y = enemy["rect"].y

            enemy["rect"].x += dx * enemy["speed"]
            for wall in walls:
                if enemy["rect"].colliderect(wall):
                    enemy["rect"].x = old_x
                    break

            enemy["rect"].y += dy * enemy["speed"]
            for wall in walls:
                if enemy["rect"].colliderect(wall):
                    enemy["rect"].y = old_y
                    break

        if enemy["rect"].colliderect(player):
            enemies.remove(enemy)
            player_hp -= 1
            screen_shake = 8

            create_particles(player.centerx, player.centery, RED, 25)
            add_text("-1 HP", player.x, player.y - 20, RED)

            if player_hp <= 0:
                game_state = "game_over"


def collect_coins():
    global gold

    for coin in coins[:]:
        if player.colliderect(coin["rect"]):
            gold += coin["value"]
            add_text(f"+{coin['value']}", coin["rect"].x, coin["rect"].y - 10, GOLD)
            create_particles(coin["rect"].centerx, coin["rect"].centery, GOLD, 10)
            coins.remove(coin)


def check_exit():
    global floor_number, player_hp

    if len(enemies) == 0:
        open_exit()

    if exit_open and player.colliderect(exit_rect):
        floor_number += 1
        player_hp = min(max_hp, player_hp + 1)
        generate_dungeon()


def open_exit():
    global exit_open

    if not exit_open:
        exit_open = True
        create_particles(exit_rect.centerx, exit_rect.centery, PURPLE, 40)
        add_text("EXIT OPENED", exit_rect.x - 20, exit_rect.y - 25, PURPLE)


def draw_floor():
    for tile in floor_tiles:
        pygame.draw.rect(screen, FLOOR, tile)
        pygame.draw.rect(screen, FLOOR_DARK, tile, 1)

        if random.random() < 0.002:
            pygame.draw.circle(
                screen,
                (55, 50, 45),
                (
                    tile.x + random.randint(5, TILE - 5),
                    tile.y + random.randint(5, TILE - 5)
                ),
                random.randint(1, 3)
            )


def draw_walls():
    for wall in walls:
        pygame.draw.rect(screen, WALL_DARK, wall)
        pygame.draw.rect(screen, WALL, (wall.x + 3, wall.y + 3, wall.width - 6, wall.height - 6))
        pygame.draw.line(screen, (120, 110, 100), (wall.x + 5, wall.y + 6), (wall.right - 5, wall.y + 6), 2)


def draw_knight():
    pygame.draw.ellipse(screen, (0, 0, 0), (player.x - 2, player.bottom - 4, player.width + 4, 8))

    body = pygame.Rect(player.x + 4, player.y + 12, 22, 22)
    helmet = pygame.Rect(player.x + 5, player.y + 1, 20, 18)

    pygame.draw.rect(screen, PLAYER_BLUE, body, border_radius=6)
    pygame.draw.rect(screen, ARMOR, helmet, border_radius=7)
    pygame.draw.rect(screen, PLAYER_DARK, (helmet.x + 4, helmet.y + 9, 12, 4), border_radius=2)

    pygame.draw.rect(screen, ARMOR, (player.x + 2, player.y + 17, 6, 13), border_radius=3)
    pygame.draw.rect(screen, ARMOR, (player.right - 8, player.y + 17, 6, 13), border_radius=3)

    pygame.draw.rect(screen, PLAYER_DARK, (player.x + 9, player.bottom - 4, 5, 6))
    pygame.draw.rect(screen, PLAYER_DARK, (player.x + 18, player.bottom - 4, 5, 6))


def draw_sword_slash():
    if attack_timer <= 0 or attack_arc is None:
        return

    progress = (9 - attack_timer) / 9

    if player_direction == "right":
        center = (player.right + 12, player.centery)
        start = -55 + progress * 25
        end = 55 + progress * 25
        rect = pygame.Rect(center[0] - 30, center[1] - 30, 60, 60)

    elif player_direction == "left":
        center = (player.left - 12, player.centery)
        start = 125 + progress * 25
        end = 235 + progress * 25
        rect = pygame.Rect(center[0] - 30, center[1] - 30, 60, 60)

    elif player_direction == "up":
        center = (player.centerx, player.top - 12)
        start = 215 + progress * 25
        end = 325 + progress * 25
        rect = pygame.Rect(center[0] - 30, center[1] - 30, 60, 60)

    else:
        center = (player.centerx, player.bottom + 12)
        start = 35 + progress * 25
        end = 145 + progress * 25
        rect = pygame.Rect(center[0] - 30, center[1] - 30, 60, 60)

    pygame.draw.arc(
        screen,
        SWORD,
        rect,
        math.radians(start),
        math.radians(end),
        6
    )

    pygame.draw.arc(
        screen,
        PURPLE,
        rect.inflate(8, 8),
        math.radians(start),
        math.radians(end),
        2
    )


def draw_player():
    draw_knight()
    draw_sword_slash()


def draw_slime(rect, hit):
    color = WHITE if hit else SLIME

    pygame.draw.ellipse(screen, color, (rect.x, rect.y + 6, rect.width, rect.height - 4))
    pygame.draw.circle(screen, color, (rect.x + 10, rect.y + 13), 10)
    pygame.draw.circle(screen, color, (rect.x + 21, rect.y + 12), 11)

    pygame.draw.circle(screen, BLACK, (rect.x + 10, rect.y + 18), 3)
    pygame.draw.circle(screen, BLACK, (rect.x + 22, rect.y + 18), 3)


def draw_skeleton(rect, hit):
    color = WHITE if hit else SKELETON

    pygame.draw.circle(screen, color, (rect.centerx, rect.y + 11), 12)
    pygame.draw.rect(screen, color, (rect.x + 9, rect.y + 22, 14, 10), border_radius=4)

    pygame.draw.circle(screen, BLACK, (rect.centerx - 5, rect.y + 10), 3)
    pygame.draw.circle(screen, BLACK, (rect.centerx + 5, rect.y + 10), 3)
    pygame.draw.rect(screen, BLACK, (rect.centerx - 5, rect.y + 18, 10, 2))


def draw_enemies():
    for enemy in enemies:
        rect = enemy["rect"]
        hit = enemy["hit_timer"] > 0

        if enemy["type"] == "slime":
            draw_slime(rect, hit)
        else:
            draw_skeleton(rect, hit)

        if enemy["hp"] < enemy["max_hp"]:
            ratio = enemy["hp"] / enemy["max_hp"]
            pygame.draw.rect(screen, RED, (rect.x, rect.y - 7, rect.width, 4))
            pygame.draw.rect(screen, GREEN, (rect.x, rect.y - 7, rect.width * ratio, 4))


def draw_chests():
    for chest in chests:
        rect = chest["rect"]

        if chest["opened"]:
            pygame.draw.rect(screen, (90, 60, 40), rect, border_radius=5)
            pygame.draw.line(screen, GOLD, (rect.x, rect.y + 5), (rect.right, rect.y), 4)
        else:
            pygame.draw.rect(screen, CHEST, rect, border_radius=5)
            pygame.draw.rect(screen, (90, 55, 30), (rect.x, rect.y + 12, rect.width, 5))
            pygame.draw.rect(screen, GOLD, (rect.x + 12, rect.y + 9, 8, 10), border_radius=2)
            pygame.draw.rect(screen, GOLD, rect, 2, border_radius=5)


def draw_coins():
    for coin in coins:
        pygame.draw.circle(screen, GOLD, coin["rect"].center, 8)
        pygame.draw.circle(screen, WHITE, coin["rect"].center, 8, 1)


def draw_exit():
    if exit_open:
        pulse = 8 + math.sin(pygame.time.get_ticks() * 0.008) * 4

        glow = pygame.Surface((90, 90), pygame.SRCALPHA)
        pygame.draw.circle(glow, (170, 110, 255, 80), (45, 45), int(34 + pulse))
        screen.blit(glow, (exit_rect.centerx - 45, exit_rect.centery - 45))

        pygame.draw.circle(screen, PURPLE, exit_rect.center, 18)
        pygame.draw.circle(screen, WHITE, exit_rect.center, 18, 2)
        pygame.draw.circle(screen, BLACK, exit_rect.center, 9)
    else:
        pygame.draw.rect(screen, (55, 48, 60), exit_rect, border_radius=6)


def draw_lighting():
    darkness = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    darkness.fill((0, 0, 0, 145))

    pygame.draw.circle(darkness, (0, 0, 0, 0), player.center, 190)

    if exit_open:
        pygame.draw.circle(darkness, (0, 0, 0, 0), exit_rect.center, 110)

    screen.blit(darkness, (0, 0))


def draw_ui():
    pygame.draw.rect(screen, (15, 15, 22), (0, 0, WIDTH, 58))
    pygame.draw.line(screen, PURPLE, (0, 58), (WIDTH, 58), 3)

    hp_text = "❤" * player_hp

    screen.blit(font.render(hp_text, True, RED), (18, 15))
    screen.blit(font.render(f"Level: {level}", True, WHITE), (160, 15))
    screen.blit(font.render(f"XP: {xp}/{xp_needed}", True, GREEN), (285, 15))
    screen.blit(font.render(f"Gold: {gold}", True, GOLD), (425, 15))
    screen.blit(font.render(f"Floor: {floor_number}", True, PURPLE), (560, 15))
    screen.blit(font.render(f"Enemies: {len(enemies)}", True, WHITE), (700, 15))


def draw_upgrade_menu():
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(215)
    overlay.fill((10, 10, 16))
    screen.blit(overlay, (0, 0))

    draw_center("LEVEL UP!", big_font, WHITE, HEIGHT // 2 - 130)
    draw_center("Choose upgrade", font, GRAY, HEIGHT // 2 - 80)

    options = [
        ("1 - Damage +1", RED),
        ("2 - Max HP +1", GREEN),
        ("3 - Speed +", PURPLE),
    ]

    for i, (text, color) in enumerate(options):
        y = HEIGHT // 2 - 20 + i * 60

        pygame.draw.rect(screen, (28, 25, 35), (WIDTH // 2 - 190, y - 22, 380, 44), border_radius=12)
        pygame.draw.rect(screen, color, (WIDTH // 2 - 190, y - 22, 380, 44), 2, border_radius=12)

        draw_center(text, font, WHITE, y)


def draw_game_over():
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(220)
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))

    draw_center("YOU DIED", big_font, RED, HEIGHT // 2 - 90)
    draw_center(f"Floor Reached: {floor_number}", font, WHITE, HEIGHT // 2 - 25)
    draw_center(f"Gold Collected: {gold}", font, GOLD, HEIGHT // 2 + 15)
    draw_center("Press ENTER to restart", font, WHITE, HEIGHT // 2 + 75)


generate_dungeon()

while running:
    clock.tick(60)

    offset_x = 0
    offset_y = 0

    if screen_shake > 0:
        offset_x = random.randint(-screen_shake, screen_shake)
        offset_y = random.randint(-screen_shake, screen_shake)
        screen_shake -= 1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if game_state == "game_over" and event.key == pygame.K_RETURN:
                reset_game()

            elif game_state == "upgrade":
                if event.key == pygame.K_1:
                    apply_upgrade(1)
                elif event.key == pygame.K_2:
                    apply_upgrade(2)
                elif event.key == pygame.K_3:
                    apply_upgrade(3)

            elif game_state == "playing":

                if event.key == pygame.K_SPACE and attack_cooldown <= 0:
                    attack()
                    attack_cooldown = 20

                elif event.key == pygame.K_e:
                    for chest in chests:
                        if player.colliderect(chest["rect"].inflate(18, 18)):
                            open_chest(chest)

    if game_state == "playing":
        keys = pygame.key.get_pressed()

        dx = 0
        dy = 0

        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx -= player_speed
            player_direction = "left"

        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx += player_speed
            player_direction = "right"

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy -= player_speed
            player_direction = "up"

        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy += player_speed
            player_direction = "down"

        if dx != 0 and dy != 0:
            dx *= 0.7
            dy *= 0.7

        move_with_collision(player, dx, dy)

        if attack_cooldown > 0:
            attack_cooldown -= 1

        if attack_timer > 0:
            attack_timer -= 1

        update_enemies()
        collect_coins()
        check_exit()

    update_particles()
    update_floating_texts()

    frame = pygame.Surface((WIDTH, HEIGHT))
    old_screen = screen
    screen = frame

    screen.fill(BLACK)

    draw_floor()
    draw_exit()
    draw_chests()
    draw_coins()
    draw_enemies()
    draw_player()
    draw_particles()
    draw_floating_texts()
    draw_walls()
    draw_lighting()
    draw_ui()

    screen = old_screen
    screen.blit(frame, (offset_x, offset_y))

    controls = small_font.render(
        "WASD / ARROWS = move   SPACE = sword attack   E = open chest",
        True,
        GRAY
    )
    screen.blit(controls, (WIDTH // 2 - 310, HEIGHT - 26))

    if game_state == "upgrade":
        draw_upgrade_menu()

    if game_state == "game_over":
        draw_game_over()

    pygame.display.update()

pygame.quit()
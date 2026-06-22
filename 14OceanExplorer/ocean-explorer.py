import pygame, random, math, time
from pathlib import Path

pygame.init()
WIDTH, HEIGHT = 960, 640
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ocean Explorer V2")
clock = pygame.time.Clock()

font = pygame.font.SysFont("Arial", 27)
big_font = pygame.font.SysFont("Arial", 56)
small_font = pygame.font.SysFont("Arial", 22)

ASSET_DIR = Path(__file__).parent / "assets"
def load(name, size=None):
    image = pygame.image.load(ASSET_DIR / name).convert_alpha()
    return pygame.transform.smoothscale(image, size) if size else image

sub_img = load("submarine.png", (96, 56))
piranha_img = load("piranha.png", (64, 42))
jellyfish_img = load("jellyfish.png", (58, 70))
shark_img = load("shark.png", (118, 62))
treasure_imgs = {name: load(f"{name}.png", (46, 46)) for name in ["chest","pearl","ruby","sapphire","artifact","oxygen","vent"]}

WHITE=(255,255,255); CYAN=(0,220,255); DARK_BLUE=(4,10,28); YELLOW=(255,220,80)
RED=(255,80,90); PURPLE=(180,100,255); GREEN=(90,255,160); GRAY=(150,160,170); ORANGE=(255,130,70)

submarine = pygame.Rect(WIDTH//2-45, 120, 90, 44)
base_speed = 4.0
slow_timer = 0

oxygen_level = 1
engine_level = 1
light_level = 1
hull_level = 1

depth = 0
oxygen = 100
max_oxygen = 100
health = 3
max_health = 3
gold = 0
stored_gold = 0
best_depth = 0

game_over = False
message = ""
message_timer = 0
screen_shake = 0
show_shop = False
at_base = True
running = True

treasures = []
enemies = []
bubbles = []
particles = []
background_fish = []
plants = []
spawn_timer = 0
enemy_timer = 0
vent_timer = 0

def upgrade_cost(level): return 120 * level

def center(text, used_font, color, y):
    rendered = used_font.render(text, True, color)
    screen.blit(rendered, rendered.get_rect(center=(WIDTH//2, y)))

def get_zone():
    if depth < 200: return "Coral Zone"
    if depth < 450: return "Deep Blue"
    if depth < 750: return "Abyss"
    return "Volcanic Zone"

def reset_run():
    global depth, oxygen, health, gold, game_over, message, message_timer, treasures, enemies, bubbles, particles
    global background_fish, plants, spawn_timer, enemy_timer, vent_timer, slow_timer, screen_shake, show_shop
    submarine.centerx = WIDTH//2; submarine.y = 115
    depth = 0; oxygen = max_oxygen; health = max_health; gold = 0
    game_over = False; message = ""; message_timer = 0; slow_timer = 0; screen_shake = 0; show_shop = False
    treasures=[]; enemies=[]; bubbles=[]; particles=[]; background_fish=[]; plants=[]
    spawn_timer=0; enemy_timer=0; vent_timer=0
    for _ in range(14):
        background_fish.append({"x":random.randint(0,WIDTH),"y":random.randint(120,HEIGHT-40),"speed":random.uniform(0.3,1.1),"size":random.randint(8,18)})
    for _ in range(26):
        plants.append({"x":random.randint(0,WIDTH),"y":random.randint(460,HEIGHT),"h":random.randint(20,80),"color":random.choice([(20,120,95),(30,150,110),(120,70,160),(180,80,120)])})

def apply_upgrade(kind):
    global stored_gold, oxygen_level, engine_level, light_level, hull_level, max_oxygen, max_health, health, message, message_timer
    levels = {"oxygen":oxygen_level, "engine":engine_level, "light":light_level, "hull":hull_level}
    lvl = levels[kind]; cost = upgrade_cost(lvl)
    if stored_gold < cost:
        message = "Not enough stored gold!"; message_timer = 100; return
    if lvl >= 5:
        message = "Upgrade already maxed!"; message_timer = 100; return
    stored_gold -= cost
    if kind == "oxygen":
        oxygen_level += 1; max_oxygen = 100 + (oxygen_level - 1) * 30
    elif kind == "engine":
        engine_level += 1
    elif kind == "light":
        light_level += 1
    elif kind == "hull":
        hull_level += 1; max_health = 3 + (hull_level - 1); health = max_health
    message = f"{kind.title()} upgraded!"; message_timer = 100

def create_particles(x,y,color,count=18):
    for _ in range(count):
        particles.append({"x":x,"y":y,"vx":random.uniform(-3,3),"vy":random.uniform(-3,3),"life":random.randint(18,35),"color":color})

def create_bubble():
    bubbles.append({"x":submarine.x+random.randint(5,20),"y":submarine.centery+random.randint(-8,8),"size":random.randint(3,8),"speed":random.uniform(1,2.7)})

def spawn_treasure():
    if depth < 160: weights=[48,25,0,0,0,12]
    elif depth < 400: weights=[30,25,18,8,1,10]
    elif depth < 700: weights=[18,20,25,18,5,8]
    else: weights=[10,12,25,24,10,6]
    types=["chest","pearl","ruby","sapphire","artifact","oxygen"]
    kind=random.choices(types, weights=weights, k=1)[0]
    values={"chest":10,"pearl":25,"ruby":80,"sapphire":120,"artifact":300,"oxygen":0}
    treasures.append({"rect":pygame.Rect(random.randint(50,WIDTH-80), HEIGHT+random.randint(20,180), 38, 38), "type":kind, "value":values[kind], "phase":random.random()*math.pi*2})

def spawn_oxygen_vent():
    treasures.append({"rect":pygame.Rect(random.randint(60,WIDTH-100), HEIGHT+random.randint(30,160),46,46), "type":"vent", "value":0, "phase":random.random()*math.pi*2})

def spawn_enemy():
    possible=["piranha","jellyfish"]
    if depth >= 280: possible.append("shark")
    kind=random.choices(possible, weights=[50,35,15] if "shark" in possible else [60,40], k=1)[0]
    side=random.choice(["left","right"])
    x=-120 if side=="left" else WIDTH+120
    direction=1 if side=="left" else -1
    y=random.randint(115,HEIGHT-80)
    if kind=="piranha":
        rect=pygame.Rect(x,y,52,32); speed=random.uniform(2.0,3.2)+depth/650; damage=1
    elif kind=="jellyfish":
        rect=pygame.Rect(x,y,46,56); speed=random.uniform(1.0,1.8)+depth/900; damage=0
    else:
        rect=pygame.Rect(x,y,104,52); speed=random.uniform(2.2,3.4)+depth/900; damage=2
    enemies.append({"rect":rect,"type":kind,"speed":speed,"direction":direction,"damage":damage,"dash_timer":random.randint(90,180)})

def draw_background():
    zone=get_zone()
    if zone=="Coral Zone": top,bottom=(28,135,205),(12,80,145)
    elif zone=="Deep Blue": top,bottom=(12,60,125),(5,30,78)
    elif zone=="Abyss": top,bottom=(4,18,48),(2,8,28)
    else: top,bottom=(34,14,24),(8,5,15)
    for y in range(0, HEIGHT, 3):
        t=y/HEIGHT
        color=(int(top[0]*(1-t)+bottom[0]*t), int(top[1]*(1-t)+bottom[1]*t), int(top[2]*(1-t)+bottom[2]*t))
        pygame.draw.rect(screen, color, (0,y,WIDTH,3))
    for fish in background_fish:
        fish["x"] += fish["speed"]
        if fish["x"] > WIDTH+40:
            fish["x"]=-40; fish["y"]=random.randint(120,HEIGHT-40)
        pygame.draw.ellipse(screen, (20,70,115), (fish["x"],fish["y"],fish["size"]*2,fish["size"]))
    for p in plants:
        sway=math.sin(p["x"]*0.03+pygame.time.get_ticks()*0.002)*5
        pygame.draw.line(screen, p["color"], (p["x"],p["y"]), (p["x"]+sway,p["y"]-p["h"]), 4)
    if zone=="Volcanic Zone":
        for x in range(80, WIDTH, 220):
            pygame.draw.circle(screen, (255,80,35), (x,HEIGHT+20), 80)
    darkness=pygame.Surface((WIDTH,HEIGHT), pygame.SRCALPHA)
    darkness.fill((0,0,0,int(min(1,depth/900)*105)))
    screen.blit(darkness,(0,0))

def draw_light_cone():
    depth_factor=min(1,depth/850)
    light_range=220+light_level*70
    alpha=max(35,105-int(depth_factor*60))
    light=pygame.Surface((WIDTH,HEIGHT), pygame.SRCALPHA)
    pygame.draw.polygon(light, (255,240,160,alpha), [(submarine.right-5,submarine.centery-12),(min(WIDTH,submarine.right+light_range),submarine.centery-95),(min(WIDTH,submarine.right+light_range),submarine.centery+95),(submarine.right-5,submarine.centery+12)])
    screen.blit(light,(0,0))
    if depth > 350:
        dark_alpha=min(185,int((depth-350)/500*185))
        overlay=pygame.Surface((WIDTH,HEIGHT), pygame.SRCALPHA)
        overlay.fill((0,0,0,dark_alpha))
        pygame.draw.ellipse(overlay, (0,0,0,0), (submarine.centerx-180, submarine.centery-150, light_range+230, 300))
        screen.blit(overlay,(0,0))

def draw_submarine():
    draw_light_cone()
    screen.blit(sub_img, (submarine.centerx-48, submarine.centery-28))

def draw_treasure(t):
    rect=t["rect"]; kind=t["type"]; image=treasure_imgs[kind]
    offset=math.sin(pygame.time.get_ticks()*0.005+t["phase"])*3
    glow_color={"chest":YELLOW,"pearl":WHITE,"ruby":RED,"sapphire":CYAN,"artifact":GREEN,"oxygen":CYAN,"vent":CYAN}[kind]
    glow=pygame.Surface((76,76), pygame.SRCALPHA)
    pygame.draw.circle(glow, (*glow_color,55), (38,38), 32)
    screen.blit(glow, (rect.centerx-38, rect.centery-38+offset))
    screen.blit(image, (rect.centerx-image.get_width()//2, rect.centery-image.get_height()//2+offset))

def draw_enemy(e):
    image={"piranha":piranha_img,"jellyfish":jellyfish_img,"shark":shark_img}[e["type"]]
    if e["direction"] == -1: image = pygame.transform.flip(image, True, False)
    rect=e["rect"]
    screen.blit(image, (rect.centerx-image.get_width()//2, rect.centery-image.get_height()//2))

def update_objects():
    global oxygen,gold,stored_gold,health,depth,best_depth,game_over,message,message_timer,slow_timer,screen_shake,at_base
    if submarine.y > 145: depth += 0.25 + submarine.y/1500
    else: depth=max(0,depth-1.1)
    best_depth=max(best_depth,depth)
    at_base = depth <= 4 and submarine.y < 150
    if depth > 20: oxygen -= 0.035 + depth/26000
    else: oxygen = min(max_oxygen, oxygen + 0.45)
    if oxygen <= 0: oxygen=0; game_over=True
    if at_base and gold > 0:
        stored_gold += gold; message=f"Treasure stored: +{gold} gold"; message_timer=120; gold=0
    for t in treasures[:]:
        t["rect"].y -= 1.1 + depth/550
        if t["rect"].bottom < 80:
            treasures.remove(t); continue
        if submarine.colliderect(t["rect"]):
            if t["type"] in ["oxygen","vent"]:
                oxygen=min(max_oxygen, oxygen + (55 if t["type"]=="vent" else 35)); slow_timer=0
                message="Oxygen vent!" if t["type"]=="vent" else "Oxygen restored!"
                create_particles(t["rect"].centerx,t["rect"].centery,CYAN,30)
            else:
                gold += t["value"]; message=f"+{t['value']} gold"; create_particles(t["rect"].centerx,t["rect"].centery,YELLOW,24)
            message_timer=90; treasures.remove(t)
    for e in enemies[:]:
        speed=e["speed"]
        if e["type"]=="shark":
            e["dash_timer"] -= 1
            if e["dash_timer"] < 25: speed *= 2.2
            if e["dash_timer"] <= 0: e["dash_timer"]=random.randint(120,220)
        e["rect"].x += speed * e["direction"]
        if e["type"]=="jellyfish":
            e["rect"].y += math.sin(pygame.time.get_ticks()*0.006 + e["rect"].x*0.02) * 1.3
        if e["rect"].right < -160 or e["rect"].left > WIDTH+160:
            enemies.remove(e); continue
        if submarine.colliderect(e["rect"]):
            enemies.remove(e)
            if e["type"]=="jellyfish":
                slow_timer=140; message="Jellyfish shock! Slowed down."; screen_shake=5
            else:
                health -= e["damage"]; message=f"-{e['damage']} health"; screen_shake=12 if e["type"]=="shark" else 7
            message_timer=100; create_particles(submarine.centerx,submarine.centery,RED,30)
            if health <= 0: game_over=True

def update_particles():
    for p in particles[:]:
        p["x"]+=p["vx"]; p["y"]+=p["vy"]; p["life"]-=1
        if p["life"]<=0: particles.remove(p)

def draw_particles():
    for p in particles:
        pygame.draw.circle(screen, p["color"], (int(p["x"]),int(p["y"])), 3)

def update_bubbles():
    for b in bubbles[:]:
        b["y"]-=b["speed"]; b["x"]+=random.uniform(-0.4,0.4)
        if b["y"] < 80: bubbles.remove(b)

def draw_bubbles():
    for b in bubbles:
        pygame.draw.circle(screen, (180,230,255), (int(b["x"]),int(b["y"])), b["size"], 1)

def draw_ui():
    pygame.draw.rect(screen, (5,12,28), (0,0,WIDTH,82))
    pygame.draw.line(screen, CYAN, (0,82), (WIDTH,82), 3)
    screen.blit(font.render(f"Depth: {int(depth)} m", True, WHITE), (18,14))
    screen.blit(font.render(f"O2: {int(oxygen)}/{max_oxygen}", True, CYAN), (178,14))
    screen.blit(font.render(f"HP: {health}/{max_health}", True, RED), (355,14))
    screen.blit(font.render(f"Gold: {gold}", True, YELLOW), (500,14))
    screen.blit(font.render(f"Stored: {stored_gold}", True, GREEN), (620,14))
    screen.blit(small_font.render(get_zone(), True, ORANGE if get_zone()=="Volcanic Zone" else GRAY), (18,52))
    pygame.draw.rect(screen, (35,45,70), (178,52,150,10), border_radius=5)
    pygame.draw.rect(screen, CYAN, (178,52,int(150*(oxygen/max_oxygen)),10), border_radius=5)
    if at_base:
        screen.blit(small_font.render("BASE CAMP: Press U for upgrades", True, GREEN), (620,54))

def draw_shop():
    overlay=pygame.Surface((WIDTH,HEIGHT)); overlay.set_alpha(225); overlay.fill((5,10,22)); screen.blit(overlay,(0,0))
    center("BASE CAMP UPGRADES", big_font, WHITE, HEIGHT//2-190)
    center(f"Stored Gold: {stored_gold}", font, YELLOW, HEIGHT//2-135)
    items=[("1","Oxygen Tank",oxygen_level,"oxygen"),("2","Engine Speed",engine_level,"engine"),("3","Spotlight",light_level,"light"),("4","Hull Armor",hull_level,"hull")]
    for i,(key,name,lvl,kind) in enumerate(items):
        y=HEIGHT//2-70+i*58; cost=upgrade_cost(lvl)
        label=f"{key} - {name}  Lv.{lvl}  Cost: {cost}" if lvl < 5 else f"{key} - {name}  MAX"
        pygame.draw.rect(screen, (18,28,45), (WIDTH//2-260,y-22,520,44), border_radius=12)
        pygame.draw.rect(screen, CYAN, (WIDTH//2-260,y-22,520,44), 2, border_radius=12)
        center(label, font, WHITE, y)
    center("Press U or ESC to close", small_font, GRAY, HEIGHT//2+210)

reset_run()

while running:
    clock.tick(60)
    draw_background()

    for event in pygame.event.get():
        if event.type == pygame.QUIT: running=False
        if event.type == pygame.KEYDOWN:
            if game_over and event.key == pygame.K_RETURN: reset_run()
            if event.key == pygame.K_u and at_base and not game_over: show_shop = not show_shop
            if event.key == pygame.K_ESCAPE and show_shop: show_shop=False
            if show_shop:
                if event.key == pygame.K_1: apply_upgrade("oxygen")
                elif event.key == pygame.K_2: apply_upgrade("engine")
                elif event.key == pygame.K_3: apply_upgrade("light")
                elif event.key == pygame.K_4: apply_upgrade("hull")

    keys=pygame.key.get_pressed()
    if not game_over and not show_shop:
        speed = base_speed + (engine_level-1)*0.45
        if slow_timer > 0:
            speed *= 0.45; slow_timer -= 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: submarine.x -= speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: submarine.x += speed
        if keys[pygame.K_w] or keys[pygame.K_UP]: submarine.y -= speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]: submarine.y += speed
        submarine.clamp_ip(pygame.Rect(0,82,WIDTH,HEIGHT-82))

        spawn_timer += 1; enemy_timer += 1; vent_timer += 1
        level=max(1,int(depth//150)+1)
        if spawn_timer > max(25,75-level*4): spawn_treasure(); spawn_timer=0
        if enemy_timer > max(30,110-level*7): spawn_enemy(); enemy_timer=0
        if vent_timer > random.randint(420,720): spawn_oxygen_vent(); vent_timer=0
        if random.random() < 0.28: create_bubble()
        update_objects()

    update_bubbles(); update_particles()

    for t in treasures: draw_treasure(t)
    for e in enemies: draw_enemy(e)
    draw_bubbles(); draw_submarine(); draw_particles(); draw_ui()

    controls=small_font.render("WASD / ARROWS = move   Return to surface to store gold   U = upgrades at base", True, GRAY)
    screen.blit(controls, (WIDTH//2-360, HEIGHT-28))

    if message_timer > 0:
        msg=font.render(message, True, WHITE)
        screen.blit(msg, (WIDTH//2-msg.get_width()//2, 96))
        message_timer -= 1

    if show_shop: draw_shop()

    if game_over:
        overlay=pygame.Surface((WIDTH,HEIGHT)); overlay.set_alpha(215); overlay.fill(DARK_BLUE); screen.blit(overlay,(0,0))
        center("MISSION FAILED", big_font, WHITE, HEIGHT//2-105)
        center(f"Stored Gold: {stored_gold}", font, YELLOW, HEIGHT//2-35)
        center(f"Best Depth: {int(best_depth)} m", font, CYAN, HEIGHT//2+5)
        center("Press ENTER to restart", font, WHITE, HEIGHT//2+65)

    if screen_shake > 0:
        frame=screen.copy(); screen.fill(DARK_BLUE)
        screen.blit(frame, (random.randint(-screen_shake,screen_shake), random.randint(-screen_shake,screen_shake)))
        screen_shake -= 1

    pygame.display.update()

pygame.quit()

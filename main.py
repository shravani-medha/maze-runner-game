import pygame
import math
import random
pygame.init()

WIDTH = 800
HEIGHT = 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Maze Runner – HOD Protects Girl")

# ------------------ COLORS ------------------
WHITE  = (255,255,255)
BLACK  = (0,0,0)
RED    = (255,50,50)
BLUE   = (80,150,255)
GREEN  = (80,255,120)
YELLOW = (255,255,60)

# ------------------ GAME SPEEDS -----------------
PLAYER_SPEED = 3.0
BOY_SPEED    = 1.6
HOD_SPEED    = 2.0

# ------------------ IMAGES ----------------------
girl_img  = pygame.image.load("girl.png")
boy_img   = pygame.image.load("boy.png")
hod_img   = pygame.image.load("hod.png")
gate_img  = pygame.image.load("gate.png")
boost_img = pygame.image.load("boost.png")

girl_img = pygame.transform.scale(girl_img,(60,60))
boy_img  = pygame.transform.scale(boy_img,(60,60))
hod_img  = pygame.transform.scale(hod_img,(60,60))
gate_img = pygame.transform.scale(gate_img,(80,80))
boost_img = pygame.transform.scale(boost_img,(40,40))

# ------------------ START POS ---------------------
girl_pos = [80, 80]
boy_pos = [680, 450]
hod_pos = [400, 280]

# ------------------ TARGET GATE --------------------
gate_pos = [720, 20]

# ------------------ BOOST AREAS --------------------
boost_tiles = [
    pygame.Rect(200,150,50,50),
    pygame.Rect(420,320,50,50),
    pygame.Rect(130,430,50,50),
]

# ------------------ UTILS -------------------------
def dist(a,b):
    return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

def move_towards(pos, target, speed):
    dx = target[0] - pos[0]
    dy = target[1] - pos[1]
    d = math.hypot(dx, dy)
    if d > 0:
        pos[0] += (dx/d) * speed
        pos[1] += (dy/d) * speed

def move_away(pos, enemy, speed):
    dx = pos[0] - enemy[0]
    dy = pos[1] - enemy[1]
    d = math.hypot(dx, dy)
    if d > 0:
        pos[0] += (dx/d) * speed
        pos[1] += (dy/d) * speed

# ------------------ MAIN LOOP ---------------------
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial",28)

running = True
score = 0
boost_timer = 0

while running:
    clock.tick(60)
    WIN.fill(BLACK)

    # ------------ INPUT ------------
    keys = pygame.key.get_pressed()
    move_x = 0
    move_y = 0

    # WASD
    if keys[pygame.K_a]: move_x = -1
    if keys[pygame.K_d]: move_x = +1
    if keys[pygame.K_w]: move_y = -1
    if keys[pygame.K_s]: move_y = +1
    # ARROWS
    if keys[pygame.K_LEFT]:  move_x = -1
    if keys[pygame.K_RIGHT]: move_x = +1
    if keys[pygame.K_UP]:    move_y = -1
    if keys[pygame.K_DOWN]:  move_y = +1

    speed_now = PLAYER_SPEED
    if boost_timer > 0:
        speed_now = 5.5
        boost_timer -= 1

    # Player move
    girl_pos[0] += move_x * speed_now
    girl_pos[1] += move_y * speed_now

    # ------------------ CLAMP TO SCREEN ------------------
    girl_pos[0] = max(0,min(WIDTH-60,girl_pos[0]))
    girl_pos[1] = max(0,min(HEIGHT-60,girl_pos[1]))

    # -------------------- AI LOGIC -----------------------
    # If hod near boy → boy runs away
    if dist(hod_pos, boy_pos) < 150:
        move_away(boy_pos, hod_pos, BOY_SPEED)
    else:
        move_towards(boy_pos, girl_pos, BOY_SPEED)

    # HOD follows girl to protect
    move_towards(hod_pos, girl_pos, HOD_SPEED)

    # ---------------- COLLISIONS -------------------------
    # Boy catches girl — Game Over
    if dist(girl_pos, boy_pos) < 50:
        print("Caught! Game Over.")
        running = False

    # Girl touches gate — Win
    if dist(girl_pos, gate_pos) < 60:
        print("Level Complete! You Escaped!")
        running = False

    # Boost pickup
    girl_rect = pygame.Rect(girl_pos[0],girl_pos[1],60,60)
    for b in boost_tiles:
        if girl_rect.colliderect(b):
            boost_timer = 240  # 4 sec speed

    # ---------------- DRAW -------------------------------
    for b in boost_tiles:
        WIN.blit(boost_img,(b.x,b.y))

    WIN.blit(gate_img,(gate_pos[0],gate_pos[1]))
    WIN.blit(girl_img,(girl_pos[0],girl_pos[1]))
    WIN.blit(boy_img,(boy_pos[0],boy_pos[1]))
    WIN.blit(hod_img,(hod_pos[0],hod_pos[1]))

    # ---------------- UI TEXT ----------------------------
    txt = font.render("SHRAVANI MEDHA PROJECT",True,WHITE)
    WIN.blit(txt,(20,10))

    pygame.display.update()

pygame.quit()

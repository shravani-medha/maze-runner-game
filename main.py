import pygame
import math
import random

# ===================== SETTINGS =====================
CELL = 24
GRID_W = 50
GRID_H = 30
WIDTH  = GRID_W * CELL
HEIGHT = GRID_H * CELL + 70
FPS = 30

COLOR_BG     = (0, 0, 0)
COLOR_WALL   = (40, 40, 40)
COLOR_FLOOR  = (10, 10, 10)

SAFE_DIST = 6         # HOD fear radius
BOOST_TIME = 240      # frames (~8 sec)
COUNTDOWN_FRAMES = 90 # 3 seconds

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SHRAVANI MEDHA PROJECT")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 38)

# ===================== MAZE =====================
def empty_maze():
    maze = [[0 for _ in range(GRID_W)] for _ in range(GRID_H)]
    # Border walls
    for x in range(GRID_W):
        maze[0][x] = 1
        maze[GRID_H-1][x] = 1
    for y in range(GRID_H):
        maze[y][0] = 1
        maze[y][GRID_W-1] = 1
    return maze

maze = empty_maze()

# ===================== GAME OBJECTS =====================
runner_pos  = [1, 1]                  # Girl
hod_pos     = [GRID_W-2, 1]           # Protector
boy1_pos    = [1, GRID_H-2]           # Chaser
boy2_pos    = [GRID_W-2, GRID_H-2]    # Chaser
chasers     = [boy1_pos, boy2_pos]

gate_pos = [GRID_W//2, GRID_H//2]
maze[gate_pos[1]][gate_pos[0]] = 0

# random boost positions
boosts = [
    [GRID_W//3, GRID_H//2],
    [GRID_W//2, GRID_H//3],
    [GRID_W//2, GRID_H - GRID_H//3]
]

boosts2 = [  # second type
    [GRID_W - GRID_W//3, GRID_H//2],
]

# ===================== IMAGES =====================
runner_img = pygame.transform.scale(pygame.image.load("girl.png"),  (CELL, CELL))
boy_img    = pygame.transform.scale(pygame.image.load("boy.png"),   (CELL, CELL))
hod_img    = pygame.transform.scale(pygame.image.load("hod.png"),   (CELL, CELL))
gate_img   = pygame.transform.scale(pygame.image.load("gate.png"),  (CELL, CELL))
boost_img  = pygame.transform.scale(pygame.image.load("boost.png"), (CELL, CELL))
boost2_img = pygame.transform.scale(pygame.image.load("boost1.png"), (CELL, CELL))

# ===================== GAME VARS =====================
pulse = 0
speed = 1
boost_timer = 0
game_started = False
countdown = COUNTDOWN_FRAMES

# ===================== MOVEMENT HELPERS =====================
def try_move(pos, dx, dy):
    nx = pos[0] + dx
    ny = pos[1] + dy
    if 0 <= nx < GRID_W and 0 <= ny < GRID_H and maze[ny][nx] == 0:
        return [nx, ny]
    return pos

def move_toward(src, dst):
    dx = 1 if src[0] < dst[0] else -1 if src[0] > dst[0] else 0
    dy = 1 if src[1] < dst[1] else -1 if src[1] > dst[1] else 0
    if abs(src[0] - dst[0]) > abs(src[1] - dst[1]):
        return try_move(src, dx, 0)
    return try_move(src, 0, dy)

def move_away(src, enemy):
    dx = -1 if src[0] < enemy[0] else 1 if src[0] > enemy[0] else 0
    dy = -1 if src[1] < enemy[1] else 1 if src[1] > enemy[1] else 0
    if abs(src[0]-enemy[0]) > abs(src[1]-enemy[1]):
        return try_move(src, dx, 0)
    return try_move(src, 0, dy)

# ======================================================
#                     MAIN LOOP
# ======================================================
running = True
while running:
    clock.tick(FPS)
    pulse += 0.05

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False

    # ================= COUNTDOWN =================
    if not game_started:
        screen.fill(COLOR_BG)
        countdown -= 1
        num = (countdown // 30) + 1
        text = font.render(str(num), True, (255,255,255))
        screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2))
        pygame.display.flip()
        if countdown <= 0:
            game_started = True
        continue

    # ================= PLAYER =================
    keys = pygame.key.get_pressed()
    dx = keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]
    dy = keys[pygame.K_DOWN]  - keys[pygame.K_UP]
    if dx or dy:
        runner_pos = try_move(runner_pos, dx*speed, dy*speed)

    # ================= BOOST PICKUP =================
    for b in boosts[:]:
        if runner_pos == b:
            speed = 2
            boost_timer = BOOST_TIME
            boosts.remove(b)

    for b in boosts2[:]:
        if runner_pos == b:
            speed = 3
            boost_timer = BOOST_TIME * 1.5
            boosts2.remove(b)

    if boost_timer > 0:
        boost_timer -= 1
        if boost_timer <= 0:
            speed = 1

    # ================= AI =================
    for i,c in enumerate(chasers):
        dist_hod    = math.dist(c, hod_pos)
        dist_runner = math.dist(c, runner_pos)

        if dist_hod < SAFE_DIST:
            chasers[i] = move_away(c, hod_pos)
        else:
            chasers[i] = move_toward(c, runner_pos)

    # ================= CHECK WIN / LOSE =================
    if runner_pos == gate_pos:
        print("🏆 YOU WIN!")
        running = False

    for c in chasers:
        if runner_pos == c:
            print("💀 CAUGHT — GAME OVER")
            running = False

    # ================= DRAW =================
    screen.fill(COLOR_BG)

    # Title neon pulse
    r = int((math.sin(pulse) + 1) * 120)
    g = int((math.sin(pulse+1.5) + 1) * 120)
    b = int((math.sin(pulse+3) + 1) * 140)
    title = font.render("SHRAVANI MEDHA PROJECT", True,(r,g,b))
    screen.blit(title,(WIDTH//2-title.get_width()//2,10))

    # Maze blocks
    for y in range(GRID_H):
        for x in range(GRID_W):
            pygame.draw.rect(
                screen,
                COLOR_WALL if maze[y][x] == 1 else COLOR_FLOOR,
                (x*CELL, y*CELL+70, CELL, CELL)
            )

    # Objects
    screen.blit(gate_img, (gate_pos[0]*CELL, gate_pos[1]*CELL+70))
    screen.blit(runner_img, (runner_pos[0]*CELL, runner_pos[1]*CELL+70))
    screen.blit(hod_img, (hod_pos[0]*CELL, hod_pos[1]*CELL+70))

    for c in chasers:
        screen.blit(boy_img, (c[0]*CELL, c[1]*CELL+70))

    for b in boosts:
        screen.blit(boost_img, (b[0]*CELL, b[1]*CELL+70))
    for b in boosts2:
        screen.blit(boost2_img, (b[0]*CELL, b[1]*CELL+70))

    pygame.display.flip()

pygame.quit()

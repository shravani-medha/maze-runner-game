import pygame
import random
import math
import time

# ======================================================
# SETTINGS
# ======================================================
CELL = 22
GRID_W = 36
GRID_H = 22
WIDTH = GRID_W * CELL
HEIGHT = GRID_H * CELL + 60
FPS = 30

# Colors
COLOR_BG = (20, 20, 20)          # Dark background
COLOR_WALL = (60, 60, 60)        # Grey walls
COLOR_PATH = (0, 0, 0)           # Maze floor
COLOR_TEXT = (255, 255, 255)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption("Shravani Medha Maze Game")
font = pygame.font.SysFont("Arial", 34)

# ======================================================
# IMAGE LOAD
# ======================================================
girl_img  = pygame.transform.scale(pygame.image.load("girl.png"),   (CELL, CELL))
boy_img   = pygame.transform.scale(pygame.image.load("boy.png"),    (CELL, CELL))
hod_img   = pygame.transform.scale(pygame.image.load("hod.png"),    (CELL, CELL))
gate_img  = pygame.transform.scale(pygame.image.load("gate.png"),   (CELL, CELL))
boost_img = pygame.transform.scale(pygame.image.load("boost.png"),  (CELL, CELL))
boost2_img= pygame.transform.scale(pygame.image.load("boost1.png"), (CELL, CELL))

# ======================================================
# BASIC MAZE GENERATOR (binary recursive)
# ======================================================
def generate_maze(w, h):
    maze = [[1 for _ in range(w)] for _ in range(h)]

    def carve(cx, cy):
        dirs = [(1,0),(-1,0),(0,1),(0,-1)]
        random.shuffle(dirs)
        for dx,dy in dirs:
            nx = cx + dx*2
            ny = cy + dy*2
            if 2 <= nx < w-2 and 2 <= ny < h-2 and maze[ny][nx] == 1:
                maze[cy+dy][cx+dx] = 0
                maze[ny][nx] = 0
                carve(nx, ny)

    maze[1][1] = 0
    carve(1,1)

    return maze

maze = generate_maze(GRID_W, GRID_H)

# ======================================================
# GAME ENTITIES
# ======================================================

# Corners:
runner = [1, 1]                       # Top-left corner
catchers = [
    [GRID_W-2, 1],                    # Top-right
    [1, GRID_H-2],                    # Bottom-left
    [GRID_W-2, GRID_H-2],             # Bottom-right
]

# HOD (center area)
hod = [GRID_W//2, GRID_H//2]

# Gate = exact center
gate = hod[:]

# Boosts
boosts = [
    [GRID_W//2 - 4, GRID_H//2],
    [GRID_W//2 + 4, GRID_H//2],
]

runner_speed = 1
boost_timer = 0
countdown_done = False

# ======================================================
# HOD SAFETY LOGIC
# ======================================================
def distance(a, b):
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

# ======================================================
# A SIMPLE MOVE
# ======================================================
def try_move(pos, dx, dy):
    x = pos[0] + dx
    y = pos[1] + dy
    if 0 <= x < GRID_W and 0 <= y < GRID_H and maze[y][x] == 0:
        return [x,y]
    return pos

# ======================================================
# SMART CHASE (simple greedy)
# ======================================================
def move_to_target(c, target):
    cx, cy = c
    tx, ty = target
    dx, dy = 0,0
    if abs(cx-tx) > abs(cy-ty):
        dx = 1 if tx>cx else -1
    else:
        dy = 1 if ty>cy else -1
    return try_move(c,dx,dy)

# ======================================================
# RUN GAME
# ======================================================
running = True
start_time = pygame.time.get_ticks()

# -------------- COUNTDOWN -----------------
for i in [3,2,1]:
    screen.fill(COLOR_BG)
    txt = font.render(str(i), True, (255,255,255))
    screen.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2))
    pygame.display.flip()
    time.sleep(1)

countdown_done = True
start_game_time = time.time()

# ======================================================
# GAME LOOP
# ======================================================
while running:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # ---------------- PLAYER MOVE ----------------
    k = pygame.key.get_pressed()
    dx = (k[pygame.K_RIGHT] - k[pygame.K_LEFT]) * runner_speed
    dy = (k[pygame.K_DOWN]  - k[pygame.K_UP])   * runner_speed

    runner = try_move(runner, dx, dy)

    # ---------------- BOOST PICKUP ---------------
    for b in boosts[:]:
        if runner == b:
            runner_speed = 2
            boost_timer = 180
            boosts.remove(b)

    if boost_timer > 0:
        boost_timer -= 1
        if boost_timer <= 0:
            runner_speed = 1

    # ---------------- AI MOVE --------------------
    new_catchers = []
    for c in catchers:
        # If boy is CLOSE to HOD => run away
        if distance(c, hod) <= 3:
            # opposite direction
            dx = 1 if c[0] < hod[0] else -1
            dy = 1 if c[1] < hod[1] else -1
            new_catchers.append(try_move(c, -dx, -dy))
        else:
            new_catchers.append(move_to_target(c, runner))
    catchers = new_catchers

    # ---------------- HOD DOESN’T MOVE ----------------

    # ---------------- WIN/LOSE ------------------------
    if runner == gate:
        print("YOU WIN!")
        running = False

    for c in catchers:
        if c == runner:
            print("CAUGHT!")
            running = False

    # =================================================
    # DRAW
    # =================================================
    screen.fill(COLOR_BG)

    # Animated Title
    t = pygame.time.get_ticks() / 500
    r = int((math.sin(t)+1)*120)
    g = int((math.sin(t+2)+1)*120)
    b = int((math.sin(t+4)+1)*120)
    color_title = (r,g,b)
    title = font.render("SHRAVANI MEDHA PROJECT", True, color_title)
    screen.blit(title,(WIDTH//2-title.get_width()//2,10))

    # Maze
    for y in range(GRID_H):
        for x in range(GRID_W):
            color = COLOR_WALL if maze[y][x]==1 else COLOR_PATH
            pygame.draw.rect(screen, color,(x*CELL, y*CELL+60, CELL,CELL))

    # Boosts
    for b in boosts:
        screen.blit(boost_img,(b[0]*CELL, b[1]*CELL+60))

    # gate
    screen.blit(gate_img,(gate[0]*CELL, gate[1]*CELL+60))

    # Player
    screen.blit(girl_img,(runner[0]*CELL, runner[1]*CELL+60))

    # HOD
    screen.blit(hod_img,(hod[0]*CELL, hod[1]*CELL+60))

    # Catchers
    for c in catchers:
        screen.blit(boy_img,(c[0]*CELL, c[1]*CELL+60))

    # Timer HUD
    elapsed = int(time.time()-start_game_time)
    hud = font.render(f"Time: {elapsed}", True, COLOR_TEXT)
    screen.blit(hud, (10,10))

    pygame.display.flip()

pygame.quit()

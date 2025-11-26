# main.py
import pygame
import random
import math
import time
from collections import deque

# ---------------- SETTINGS ----------------
CELL = 24                # tile size in pixels
GRID_W = 36              # grid width (tiles)
GRID_H = 22              # grid height (tiles)
WIDTH = GRID_W * CELL
HEIGHT = GRID_H * CELL + 66
FPS = 30

SAFE_DIST = 6            # if catcher is within SAFE_DIST of HOD -> it runs away
BOOST_DURATION = FPS * 5 # frames (~5 seconds)
COUNTDOWN_SECONDS = 3    # 3..2..1 start

# Colors
COLOR_BG = (18, 18, 22)
COLOR_WALL = (60, 60, 60)
COLOR_FLOOR = (10, 10, 12)
COLOR_TEXT = (230, 230, 230)

# ---------------- PYGAME INIT ----------------
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Maze Runner - Shravan i Medha Project")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 20)
big_font = pygame.font.SysFont("Arial", 72)

# ---------------- SAFE IMAGE LOAD ----------------
def safe_load_image(path):
    try:
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(img, (CELL, CELL))
    except Exception as e:
        print(f"[WARN] couldn't load '{path}': {e}")
        # fallback: colored square
        s = pygame.Surface((CELL, CELL), pygame.SRCALPHA)
        s.fill((180, 50, 50))
        return s

girl_img   = safe_load_image("girl.png")
boy_img    = safe_load_image("boy.png")
hod_img    = safe_load_image("hod.png")
gate_img   = safe_load_image("gate.png")
boost_img  = safe_load_image("boost.png")
boost2_img = safe_load_image("boost1.png")

# ---------------- MAZE GENERATION (DFS on odd cells) ----------------
def generate_maze(w, h):
    maze = [[1 for _ in range(w)] for _ in range(h)]

    def carve(x, y):
        dirs = [(2,0),(-2,0),(0,2),(0,-2)]
        random.shuffle(dirs)
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if 1 <= nx < w-1 and 1 <= ny < h-1 and maze[ny][nx] == 1:
                maze[ y + dy//2 ][ x + dx//2 ] = 0
                maze[ny][nx] = 0
                carve(nx, ny)

    # ensure odd start
    maze[1][1] = 0
    carve(1, 1)
    # border safety
    for x in range(w):
        maze[0][x] = 1
        maze[h-1][x] = 1
    for y in range(h):
        maze[y][0] = 1
        maze[y][w-1] = 1
    return maze

maze = generate_maze(GRID_W, GRID_H)

# ---------------- UTILS ----------------
def in_bounds(x, y):
    return 0 <= x < GRID_W and 0 <= y < GRID_H

def neighbors(tile):
    x, y = tile
    for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
        nx, ny = x+dx, y+dy
        if in_bounds(nx, ny) and maze[ny][nx] == 0:
            yield (nx, ny)

def manhattan(a, b):
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

# BFS next-step pathfinder (fast, reliable)
def bfs_next_step(start, goal):
    if start == goal:
        return None
    sx, sy = start
    gx, gy = goal
    q = deque()
    q.append((sx, sy))
    parent = { (sx, sy): None }
    while q:
        x, y = q.popleft()
        for nx, ny in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
            if not in_bounds(nx, ny): 
                continue
            if maze[ny][nx] != 0: 
                continue
            if (nx, ny) in parent:
                continue
            parent[(nx, ny)] = (x, y)
            if (nx, ny) == (gx, gy):
                # reconstruct path and return the immediate next tile after start
                cur = (nx, ny)
                while parent[cur] != (sx, sy) and parent[cur] is not None:
                    cur = parent[cur]
                return [cur[0], cur[1]]
            q.append((nx, ny))
    return None

# make sure spawn areas are open (prevent instant catches)
def open_area(center, radius=2):
    cx, cy = center
    for dy in range(-radius, radius+1):
        for dx in range(-radius, radius+1):
            x, y = cx+dx, cy+dy
            if in_bounds(x,y):
                maze[y][x] = 0

# ---------------- SPAWN ENTITIES ----------------
runner = [1, 1]                             # top-left
hod = [GRID_W-2, 1]                         # top-right (protector)
catchers = [
    [1, GRID_H-2],                          # bottom-left
    [GRID_W-2, GRID_H-2],                   # bottom-right
    [GRID_W-4, 1]                           # near top-right but not same as HOD
]

# ensure no overlap and clear areas
open_area(runner, radius=2)
open_area(hod, radius=2)
for c in catchers:
    open_area(c, radius=2)
gate = [GRID_W//2, GRID_H//2]
open_area(gate, radius=2)

# spawn boosts on available open tiles (avoid spawns on entities)
def find_open_tiles(n, forbidden):
    tiles = [(x,y) for y in range(1, GRID_H-1) for x in range(1, GRID_W-1) if maze[y][x]==0 and [x,y] not in forbidden]
    random.shuffle(tiles)
    chosen = []
    for x,y in tiles:
        chosen.append([x,y])
        if len(chosen) >= n:
            break
    return chosen

forbidden_positions = [runner, hod, gate] + catchers
boosts = find_open_tiles(3, forbidden_positions)
# ensure chosen tiles are not duplicated for second type
forbidden_positions += boosts
boosts2 = find_open_tiles(1, forbidden_positions)

# ---------------- GAME STATE ----------------
runner_speed = 1           # tiles per key press
boost_timer = 0
start_time = None
pulse = 0.0

# ---------------- COUNTDOWN ----------------
def show_countdown():
    # 3..2..1..START
    for n in range(COUNTDOWN_SECONDS, 0, -1):
        screen.fill(COLOR_BG)
        txt = big_font.render(str(n), True, COLOR_TEXT)
        screen.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2 - txt.get_height()//2))
        pygame.display.flip()
        time.sleep(1.0)
    # START
    screen.fill(COLOR_BG)
    txt = big_font.render("START", True, (80, 200, 190))
    screen.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2 - txt.get_height()//2))
    pygame.display.flip()
    time.sleep(0.7)

show_countdown()
start_time = time.time()

# ---------------- MAIN LOOP ----------------
running = True
while running:
    dt = clock.tick(FPS) / 1000.0
    pulse += dt * 3.0

    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            running = False
        # TILE MOVEMENT on KEYDOWN for reliable one-tile steps
        elif ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_ESCAPE:
                running = False
            elif ev.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN):
                dx = 0; dy = 0
                if ev.key == pygame.K_LEFT:  dx = -1
                if ev.key == pygame.K_RIGHT: dx = 1
                if ev.key == pygame.K_UP:    dy = -1
                if ev.key == pygame.K_DOWN:  dy = 1
                # prefer single-axis move
                # try horizontal then vertical
                if dx != 0:
                    nx, ny = runner[0] + dx, runner[1]
                    if in_bounds(nx, ny) and maze[ny][nx] == 0:
                        runner = [nx, ny]
                elif dy != 0:
                    nx, ny = runner[0], runner[1] + dy
                    if in_bounds(nx, ny) and maze[ny][nx] == 0:
                        runner = [nx, ny]

    # ---------------- BOOSTS ----------------
    for b in boosts[:]:
        if runner == b:
            boosts.remove(b)
            runner_speed = 2
            boost_timer = BOOST_DURATION
            print("[BOOST] normal collected")
    for b in boosts2[:]:
        if runner == b:
            boosts2.remove(b)
            runner_speed = 3
            boost_timer = int(BOOST_DURATION * 1.5)
            print("[BOOST] super collected")

    if boost_timer > 0:
        boost_timer -= 1
        if boost_timer <= 0:
            runner_speed = 1

    # ---------------- CATCHERS AI ----------------
    new_catchers = []
    for c in catchers:
        # if too close to HOD -> run away
        if manhattan(c, hod) <= SAFE_DIST:
            # attempt to move to neighbor that increases distance from HOD
            best = c
            bestd = manhattan(c, hod)
            for nx, ny in ((c[0]+1,c[1]),(c[0]-1,c[1]),(c[0],c[1]+1),(c[0],c[1]-1)):
                if in_bounds(nx, ny) and maze[ny][nx] == 0:
                    d = manhattan([nx, ny], hod)
                    if d > bestd:
                        bestd = d
                        best = [nx, ny]
            # if best is different use it, else try BFS to farther node
            if best != c:
                new_catchers.append(best)
            else:
                # BFS search limited-depth for a farther cell
                q = deque([(c[0], c[1], 0)])
                seen = {(c[0], c[1])}
                candidate = None
                cand_dist = bestd
                while q:
                    x, y, depth = q.popleft()
                    if depth >= 6:
                        continue
                    for nx, ny in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
                        if in_bounds(nx, ny) and (nx, ny) not in seen and maze[ny][nx] == 0:

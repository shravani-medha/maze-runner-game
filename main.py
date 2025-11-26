import pygame
import random
import math

# ================= SETTINGS =================
CELL_SIZE = 20
GRID_WIDTH = 150
GRID_HEIGHT = 30
WIDTH = CELL_SIZE * GRID_WIDTH
HEIGHT = CELL_SIZE * GRID_HEIGHT + 40
FPS = 30

# Colors
COLOR_WALL = (135, 206, 235)   # Sky Blue wall
COLOR_PATH_FILL = (0, 0, 0)    # Path color
COLOR_PATH_BG = (255, 255, 255)

# ================ MAZE GENERATION ================
def generate_circular_maze():
    maze = [[1 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

    cx = GRID_WIDTH // 2
    cy = GRID_HEIGHT // 2
    max_r = min(GRID_WIDTH, GRID_HEIGHT) // 2

    for r in range(max_r):
        # circular rings
        for angle in range(0, 360, 5):
            rad = math.radians(angle)
            x = int(cx + r * math.cos(rad))
            y = int(cy + r * math.sin(rad))
            if 0 < x < GRID_WIDTH and 0 < y < GRID_HEIGHT:
                maze[y][x] = 0

        # radial spokes
        if r % 3 == 0:
            for a in range(0, 360, 45):
                rad = math.radians(a)
                x = int(cx + r * math.cos(rad))
                y = int(cy + r * math.sin(rad))
                if 0 < x < GRID_WIDTH and 0 < y < GRID_HEIGHT:
                    maze[y][x] = 0

    # clear center
    for i in range(cy - 2, cy + 3):
        for j in range(cx - 2, cx + 3):
            maze[i][j] = 0

    return maze

maze = generate_circular_maze()

# ================ PLAYER / OBJECT STARTS ================
runner_pos = [GRID_WIDTH // 2, GRID_HEIGHT // 2]
gate_pos = [GRID_WIDTH // 2, GRID_HEIGHT - 3]
maze[gate_pos[1]][gate_pos[0]] = 0  # ensure exit path

boosters = [
    [GRID_WIDTH // 2 + 10, GRID_HEIGHT // 2],
    [GRID_WIDTH // 2 - 10, GRID_HEIGHT // 2],
    [GRID_WIDTH // 2, GRID_HEIGHT // 2 + 10],
    [GRID_WIDTH // 2, GRID_HEIGHT // 2 - 10]
]

# Catchers
catchers = [
    [GRID_WIDTH // 2, GRID_HEIGHT // 2 - 5],  # HOD
    [GRID_WIDTH // 2 + 5, GRID_HEIGHT // 2 + 5],  # boy
    [GRID_WIDTH // 2 - 5, GRID_HEIGHT // 2 + 5]   # boy
]

# ================ GAME VARIABLES ================
runner_speed = 1
boost_active = False
boost_timer = 0
pulse_counter = 0

# ================ PYGAME INIT & IMAGE LOAD ================
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ultimate Brain Maze 3 Catchers")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

# --- Load images ---
runner_img = pygame.transform.scale(pygame.image.load("girl.png"), (CELL_SIZE, CELL_SIZE))
catcher1_img = pygame.transform.scale(pygame.image.load("hod.png"), (CELL_SIZE, CELL_SIZE))
catcher_img = pygame.transform.scale(pygame.image.load("boy.png"), (CELL_SIZE, CELL_SIZE))
boost_img = pygame.transform.scale(pygame.image.load("note.png"), (CELL_SIZE, CELL_SIZE))
gate_img = pygame.transform.scale(pygame.image.load("gate.png"), (CELL_SIZE, CELL_SIZE))

# ================ MOVE CATCHERS ================
def move_toward_runner(catcher_pos, runner_pos, maze):
    x, y = catcher_pos
    rx, ry = runner_pos
    dx, dy = 0, 0

    if abs(x - rx) > abs(y - ry):
        if x < rx and maze[y][x + 1] == 0: dx = 1
        elif x > rx and maze[y][x - 1] == 0: dx = -1
    else:
        if y < ry and maze[y + 1][x] == 0: dy = 1
        elif y > ry and maze[y - 1][x] == 0: dy = -1

    return [x + dx, y + dy]

# ================ MAIN GAME LOOP ================
running = True
while running:
    clock.tick(FPS)
    pulse_counter += 0.05

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # -------- Runner Movement --------
    keys = pygame.key.get_pressed()
    dx = (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * runner_speed
    dy = (keys[pygame.K_DOWN] - keys[pygame.K_UP]) * runner_speed

    new_x = runner_pos[0] + dx
    new_y = runner_pos[1] + dy
    if 0 <= new_x < GRID_WIDTH and 0 <= new_y < GRID_HEIGHT and maze[new_y][new_x] == 0:
        runner_pos = [new_x, new_y]

    # -------- Catchers Move --------
    for i in range(3):
        catchers[i] = move_toward_runner(catchers[i], runner_pos, maze)

    # -------- Boost Pickup --------
    for b in boosters[:]:
        if runner_pos == b:
            boost_active = True
            boost_timer = 50
            runner_speed = 2
            boosters.remove(b)

    if boost_active:
        boost_timer -= 1
        if boost_timer <= 0:
            boost_active = False
            runner_speed = 1

    # -------- Win / Lose --------
    if runner_pos == gate_pos:
        print("You Win!")
        running = False

    for c in catchers:
        if runner_pos == c:
            print("Caught! Game Over.")
            running = False

    # ================ DRAWING ================
    screen.fill(COLOR_PATH_BG)

    # Pulsing Title
    r = int((math.sin(pulse_counter) + 1) * 127)
    g = int((math.sin(pulse_counter + 2) + 1) * 127)
    b = int((math.sin(pulse_counter + 4) + 1) * 127)
    title = font.render("SHRAVANI MEDHA PROJECT", True, (r, g, b))
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 5))

    # Draw Maze
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if maze[y][x] == 1:
                pygame.draw.rect(screen, COLOR_WALL, (x * CELL_SIZE, y * CELL_SIZE + 40, CELL_SIZE, CELL_SIZE))
            else:
                pygame.draw.rect(screen, COLOR_PATH_FILL, (x * CELL_SIZE, y * CELL_SIZE + 40, CELL_SIZE, CELL_SIZE))

    # Draw elements
    screen.blit(gate_img, (gate_pos[0] * CELL_SIZE, gate_pos[1] * CELL_SIZE + 40))
    for b in boosters:
        screen.blit(boost_img, (b[0] * CELL_SIZE, b[1] * CELL_SIZE + 40))
    screen.blit(runner_img, (runner_pos[0] * CELL_SIZE, runner_pos[1] * CELL_SIZE + 40))
    screen.blit(catcher1_img, (catchers[0][0] * CELL_SIZE, catchers[0][1] * CELL_SIZE + 40))
    screen.blit(catcher_img, (catchers[1][0] * CELL_SIZE, catchers[1][1] * CELL_SIZE + 40))
    screen.blit(catcher_img, (catchers[2][0] * CELL_SIZE, catchers[2][1] * CELL_SIZE + 40))

    pygame.display.flip()

pygame.quit()

import pygame
import random
import math

# --- Settings ---
CELL_SIZE = 20
GRID_WIDTH = 30
GRID_HEIGHT = 30
WIDTH = CELL_SIZE * GRID_WIDTH
HEIGHT = CELL_SIZE * GRID_HEIGHT + 40  # extra space for title
FPS = 10

# Colors
COLOR_WALL = (135, 206, 235)    # Sky Blue
COLOR_PATH_FILL = (0, 0, 0)     # Black
COLOR_PATH_BG = (255, 255, 255) # White
COLOR_GATE = (128, 0, 128)      # Purple
COLOR_RUNNER = (0, 255, 0)      # Green
COLOR_CATCHER = (255, 0, 0)     # Red
COLOR_BOOST = (255, 255, 0)     # Yellow

# --- Maze generation ---
def generate_maze():
    maze = [[1 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    for y in range(1, GRID_HEIGHT-1):
        for x in range(1, GRID_WIDTH-1):
            maze[y][x] = 0 if random.random() > 0.35 else 1
    return maze

maze = generate_maze()

# --- Runner and gate ---
runner_pos = [1, 1]
gate_pos = [GRID_WIDTH-2, GRID_HEIGHT-2]

# --- Define 3 risky paths for catchers ---
catcher_paths = [
    [[GRID_WIDTH//4, y] for y in range(1, GRID_HEIGHT-1)],  # left vertical
    [[GRID_WIDTH//2, y] for y in range(1, GRID_HEIGHT-1)],  # middle vertical
    [[3*GRID_WIDTH//4, y] for y in range(1, GRID_HEIGHT-1)] # right vertical
]
catchers = [path[0][:] for path in catcher_paths]
catcher_indices = [0, 0, 0]

# Clear risky paths in maze
for path in catcher_paths:
    for pos in path:
        maze[pos[1]][pos[0]] = 0

# --- Speed boosters ---
boosters = [
    [GRID_WIDTH//6, GRID_HEIGHT//6],
    [5*GRID_WIDTH//6, GRID_HEIGHT//6],
    [GRID_WIDTH//2, GRID_HEIGHT//3],
    [GRID_WIDTH//3, 2*GRID_HEIGHT//3],
    [2*GRID_WIDTH//3, 5*GRID_HEIGHT//6]
]

# Ensure gate path is clear
maze[gate_pos[1]][gate_pos[0]] = 0

# --- Pygame init ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ultimate Brain Maze 3 Catchers")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

# --- Game variables ---
runner_speed = 1
boost_active = False
boost_timer = 0
pulse_counter = 0

# --- Main loop ---
running = True
while running:
    clock.tick(FPS)
    pulse_counter += 0.05

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # --- Runner movement ---
    keys = pygame.key.get_pressed()
    dx, dy = 0, 0
    if keys[pygame.K_LEFT]: dx = -runner_speed
    if keys[pygame.K_RIGHT]: dx = runner_speed
    if keys[pygame.K_UP]: dy = -runner_speed
    if keys[pygame.K_DOWN]: dy = runner_speed

    new_x = runner_pos[0] + dx
    new_y = runner_pos[1] + dy
    if 0 <= new_x < GRID_WIDTH and 0 <= new_y < GRID_HEIGHT and maze[new_y][new_x] == 0:
        runner_pos = [new_x, new_y]

    # --- Catchers movement ---
    for i in range(3):
        path = catcher_paths[i]
        catchers[i] = path[catcher_indices[i]]
        catcher_indices[i] = (catcher_indices[i] + 1) % len(path)

    # --- Check booster pickup ---
    for b in boosters[:]:
        if runner_pos == b:
            boost_active = True
            boost_timer = 50
            boosters.remove(b)

    if boost_active:
        runner_speed = 2
        boost_timer -= 1
        if boost_timer <= 0:
            boost_active = False
            runner_speed = 1

    # --- Check win/lose ---
    if runner_pos == gate_pos:
        print("You Win!")
        running = False
    for c in catchers:
        if runner_pos == c:
            print("Caught! Game Over.")
            running = False

    # --- Drawing ---
    screen.fill(COLOR_PATH_BG)

    # Pulsing title
    r = int((math.sin(pulse_counter) + 1) * 127)
    g = int((math.sin(pulse_counter + 2) + 1) * 127)
    b = int((math.sin(pulse_counter + 4) + 1) * 127)
    title_color = (r, g, b)
    title_text = font.render("SHRAVANI MEDHA PROJECT", True, title_color)
    screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 5))

    # Draw maze
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            rect = pygame.Rect(x*CELL_SIZE, y*CELL_SIZE + 40, CELL_SIZE, CELL_SIZE)
            if maze[y][x] == 1:
                pygame.draw.rect(screen, COLOR_WALL, rect)
            else:
                pygame.draw.rect(screen, COLOR_PATH_FILL, rect)

    # Draw gate
    pygame.draw.rect(screen, COLOR_GATE, (gate_pos[0]*CELL_SIZE, gate_pos[1]*CELL_SIZE + 40, CELL_SIZE, CELL_SIZE))

    # Draw boosters
    for b in boosters:
        pygame.draw.rect(screen, COLOR_BOOST, (b[0]*CELL_SIZE, b[1]*CELL_SIZE + 40, CELL_SIZE, CELL_SIZE))

    # Draw runner
    pygame.draw.rect(screen, COLOR_RUNNER, (runner_pos[0]*CELL_SIZE, runner_pos[1]*CELL_SIZE + 40, CELL_SIZE, CELL_SIZE))

    # Draw catchers
    for c in catchers:
        pygame.draw.rect(screen, COLOR_CATCHER, (c[0]*CELL_SIZE, c[1]*CELL_SIZE + 40, CELL_SIZE, CELL_SIZE))

    pygame.display.flip()

pygame.quit()

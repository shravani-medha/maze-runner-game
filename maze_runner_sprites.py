"""
Maze Runner - Pac-Mac Designer (Sprites + Sound)

Place the following files in the same folder as this script:
 - boy.png        (player sprite option)
 - girl.png       (player sprite option)
 - hod.png        (enemy sprite)
Optional sound files:
 - eat.wav        (pellet sound)
 - hit.wav        (life lost sound)
 - win.wav        (win sound)
 - bgm.mp3        (background music)

Run:
    pip install pygame
    python maze_runner_sprites.py
Controls:
 - Arrow keys or WASD to move
 - At title: press B for Boy or G for Girl to pick sprite
 - Press R to restart after win/game over
"""

import pygame, random, collections, sys, math, time, os

# ---------- Config ----------
CELL = 22            # pixels per grid cell
ROWS = 21            # should be odd
COLS = 29            # should be odd
WIDTH = COLS * CELL
HEIGHT = ROWS * CELL
FPS = 60

PLAYER_SPEED = 5.0    # pixels per frame (smooth movement)
ENEMY_SPEED = 2.6

LIVES_START = 3

# Colors
WALL_COLOR = (8, 8, 8)
BG_COLOR = (22, 22, 22)
PELLET_COLOR = (255, 220, 100)
TEXT_COLOR = (230, 230, 230)

# Filenames (put these files in same folder)
PLAYER_BOY_IMG = "boy.png"
PLAYER_GIRL_IMG = "girl.png"
ENEMY_IMG = "hod.png"

SOUND_EAT = "eat.wav"
SOUND_HIT = "hit.wav"
SOUND_WIN = "win.wav"
BGM = "bgm.mp3"

# ---------- Utilities ----------
def resource_exists(name):
    return os.path.exists(name)

def load_image_scaled(name, target_size):
    try:
        img = pygame.image.load(name).convert_alpha()
        img = pygame.transform.smoothscale(img, target_size)
        return img
    except Exception as e:
        return None

# ---------- Maze generation ----------
def generate_maze(rows, cols):
    grid = [[0]*cols for _ in range(rows)]
    for r in range(1, rows, 2):
        for c in range(1, cols, 2):
            grid[r][c] = 1
    stack = [(1,1)]
    visited = set([(1,1)])
    while stack:
        r,c = stack[-1]
        neighbors = []
        for dr,dc in [(-2,0),(2,0),(0,-2),(0,2)]:
            nr, nc = r+dr, c+dc
            if 1 <= nr < rows and 1 <= nc < cols and (nr,nc) not in visited:
                neighbors.append((nr,nc))
        if neighbors:
            nr,nc = random.choice(neighbors)
            wr, wc = (r+nr)//2, (c+nc)//2
            grid[wr][wc] = 1
            visited.add((nr,nc))
            stack.append((nr,nc))
        else:
            stack.pop()
    return grid

def bfs_shortest(grid, start, goal):
    rows = len(grid); cols = len(grid[0])
    q = collections.deque([start])
    parent = {start: None}
    while q:
        r,c = q.popleft()
        if (r,c) == goal:
            path = []
            cur = goal
            while parent[cur] is not None:
                path.append(cur)
                cur = parent[cur]
            path.reverse()
            return path
        for dr,dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            nr, nc = r+dr, c+dc
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 1 and (nr,nc) not in parent:
                parent[(nr,nc)] = (r,c)
                q.append((nr,nc))
    return None

def grid_to_px(cell_r, cell_c):
    return cell_c * CELL, cell_r * CELL

# ---------- Actor class ----------
class Actor:
    def __init__(self, r, c, color, speed, sprite=None):
        self.r = r; self.c = c
        self.x, self.y = grid_to_px(r,c)
        self.color = color
        self.speed = speed
        self.target = (r,c)
        self.moving = False
        self.sprite = sprite  # pygame.Surface or None

    def set_target(self, tr, tc):
        self.target = (tr,tc)
        self.moving = True

    def update_smooth(self):
        tx, ty = grid_to_px(*self.target)
        dx = tx - self.x
        dy = ty - self.y
        dist = math.hypot(dx,dy)
        if dist < 0.5:
            self.x, self.y = tx, ty
            self.r, self.c = self.target
            self.moving = False
            return
        step = self.speed
        nx = dx / dist * step
        ny = dy / dist * step
        if abs(nx) > abs(dx): nx = dx
        if abs(ny) > abs(dy): ny = dy
        self.x += nx
        self.y += ny
        if abs(self.x - tx) < 0.5 and abs(self.y - ty) < 0.5:
            self.x, self.y = tx, ty
            self.r, self.c = self.target
            self.moving = False

    def draw(self, surf):
        cx = int(self.x + CELL/2)
        cy = int(self.y + CELL/2)
        if self.sprite:
            rect = self.sprite.get_rect(center=(cx, cy))
            surf.blit(self.sprite, rect)
        else:
            radius = max(4, CELL//2 - 2)
            pygame.draw.circle(surf, self.color, (cx, cy), radius)

# ---------- Game ----------
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Maze Runner — Pac-Mac Designer (Sprites + Sound)")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 22)
    bigfont = pygame.font.SysFont(None, 56)

    # Attempt to load resources
    # sprite size roughly cell-4
    sprite_size = (CELL-4, CELL-4)
    player_boy_img = load_image_scaled(PLAYER_BOY_IMG, sprite_size) if resource_exists(PLAYER_BOY_IMG) else None
    player_girl_img = load_image_scaled(PLAYER_GIRL_IMG, sprite_size) if resource_exists(PLAYER_GIRL_IMG) else None
    enemy_img = load_image_scaled(ENEMY_IMG, sprite_size) if resource_exists(ENEMY_IMG) else None

    # sounds (optional)
    pygame.mixer.init()
    s_eat = pygame.mixer.Sound(SOUND_EAT) if resource_exists(SOUND_EAT) else None
    s_hit = pygame.mixer.Sound(SOUND_HIT) if resource_exists(SOUND_HIT) else None
    s_win = pygame.mixer.Sound(SOUND_WIN) if resource_exists(SOUND_WIN) else None
    if resource_exists(BGM):
        try:
            pygame.mixer.music.load(BGM)
            pygame.mixer.music.set_volume(0.35)
            pygame.mixer.music.play(-1)
        except Exception:
            pass

    # Title / choose sprite
    choose = True
    chosen_sprite = None
    while choose:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_b:
                    chosen_sprite = player_boy_img
                    choose = False
                if ev.key == pygame.K_g:
                    chosen_sprite = player_girl_img
                    choose = False
                # if images not provided and user presses, choose fallback color
                if ev.key == pygame.K_b and not player_boy_img:
                    chosen_sprite = None
                    choose = False
                if ev.key == pygame.K_g and not player_girl_img:
                    chosen_sprite = None
                    choose = False

        screen.fill(BG_COLOR)
        title = bigfont.render("Maze Runner — Pick Player", True, TEXT_COLOR)
        screen.blit(title, ((WIDTH-title.get_width())//2, 60))
        sub = font.render("Press B for Boy or G for Girl", True, TEXT_COLOR)
        screen.blit(sub, ((WIDTH-sub.get_width())//2, 150))

        hint = font.render("Place boy.png/girl.png/hod.png in the folder to use sprites. Press B/G anyway to continue.", True, (180,180,180))
        screen.blit(hint, ((WIDTH-hint.get_width())//2, HEIGHT-80))

        pygame.display.flip()
        clock.tick(30)

    # generate maze and pellets
    grid = generate_maze(ROWS, COLS)
    pellets = set()
    for r in range(ROWS):
        for c in range(COLS):
            if grid[r][c] == 1:
                pellets.add((r,c))

    # helper random path cell
    def random_path_cell(min_dist=8):
        while True:
            r = random.randrange(1, ROWS, 2)
            c = random.randrange(1, COLS, 2)
            if grid[r][c] == 1:
                return (r,c)

    pr,pc = random_path_cell()
    er,ec = random_path_cell()
    while abs(pr-er)+abs(pc-ec) < max(ROWS,COLS)//4:
        er,ec = random_path_cell()

    player = Actor(pr,pc, (30,200,255), PLAYER_SPEED, sprite=chosen_sprite)
    enemy = Actor(er,ec, (255,90,150), ENEMY_SPEED, sprite=enemy_img)

    pellets.discard((player.r, player.c))

    lives = LIVES_START
    score = 0
    game_over = False
    win = False

    enemy_path = []
    enemy_path_index = 0
    enemy_recalc_timer = 0
    move_queue = []
    last_eat_time = 0

    def passable(r,c):
        return 0 <= r < ROWS and 0 <= c < COLS and grid[r][c] == 1

    while True:
        dt = clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if not game_over and not win:
                    if event.key in (pygame.K_UP, pygame.K_w): move_queue.append((-1,0))
                    elif event.key in (pygame.K_DOWN, pygame.K_s): move_queue.append((1,0))
                    elif event.key in (pygame.K_LEFT, pygame.K_a): move_queue.append((0,-1))
                    elif event.key in (pygame.K_RIGHT, pygame.K_d): move_queue.append((0,1))
                if event.key == pygame.K_r and (game_over or win):
                    # restart full game
                    pygame.mixer.music.stop()
                    main()
                    return

        if not game_over and not win:
            if not player.moving and move_queue:
                dr,dc = move_queue.pop(0)
                tr,tc = player.r + dr, player.c + dc
                if passable(tr,tc):
                    player.set_target(tr,tc)

            if not player.moving:
                if (player.r, player.c) in pellets:
                    pellets.remove((player.r, player.c))
                    score += 10
                    if s_eat: s_eat.play()
                    last_eat_time = time.time()

            enemy_recalc_timer += 1
            interval = max(6, int(22))  # recalc frequency
            if enemy_recalc_timer >= interval:
                enemy_recalc_timer = 0
                path = bfs_shortest(grid, (enemy.r, enemy.c), (player.r, player.c))
                if path:
                    enemy_path = path
                    enemy_path_index = 0

            if not enemy.moving and enemy_path and enemy_path_index < len(enemy_path):
                nr,nc = enemy_path[enemy_path_index]
                enemy.set_target(nr,nc)
                enemy_path_index += 1

            player.update_smooth()
            enemy.update_smooth()

            # collision detection (center distance)
            dx = (player.x - enemy.x); dy = (player.y - enemy.y)
            dist = math.hypot(dx,dy)
            if dist < CELL*0.35:
                lives -= 1
                if s_hit: s_hit.play()
                pr,pc = random_path_cell()
                er,ec = random_path_cell()
                while abs(pr-er)+abs(pc-ec) < max(ROWS,COLS)//4:
                    er,ec = random_path_cell()
                player = Actor(pr,pc, (30,200,255), PLAYER_SPEED, sprite=chosen_sprite)
                enemy = Actor(er,ec, (255,90,150), ENEMY_SPEED, sprite=enemy_img)
                pellets.discard((player.r, player.c))
                enemy_path = []
                move_queue = []
                if lives <= 0:
                    game_over = True
                    if s_win: s_win.play()  # optional, use win or hit as appropriate

            if len(pellets) == 0:
                win = True
                if s_win: s_win.play()

        # draw
        screen.fill(BG_COLOR)
        # maze
        for r in range(ROWS):
            for c in range(COLS):
                if grid[r][c] == 0:
                    pygame.draw.rect(screen, WALL_COLOR, (c*CELL, r*CELL, CELL, CELL))
                else:
                    pygame.draw.rect(screen, (40,40,40), (c*CELL, r*CELL, CELL, CELL))

        # pellets
        for (r,c) in pellets:
            px = int(c*CELL + CELL/2); py = int(r*CELL + CELL/2)
            pygame.draw.circle(screen, PELLET_COLOR, (px,py), max(2, CELL//8))

        # actors
        player.draw(screen)
        enemy.draw(screen)

        # HUD
        info = f"Score: {score}   Pellets: {len(pellets)}   Lives: {lives}"
        text = font.render(info, True, TEXT_COLOR)
        screen.blit(text, (8, 8))

        if game_over:
            over_surf = bigfont.render("GAME OVER", True, (220,60,60))
            screen.blit(over_surf, ((WIDTH-over_surf.get_width())//2, (HEIGHT-200)//2))
            sub = font.render("Press R to restart", True, TEXT_COLOR)
            screen.blit(sub, ((WIDTH-sub.get_width())//2, (HEIGHT-80)//2))
        if win:
            win_surf = bigfont.render("YOU WIN!", True, (120,220,120))
            screen.blit(win_surf, ((WIDTH-win_surf.get_width())//2, (HEIGHT-200)//2))
            sub = font.render(f"Score: {score}   Press R to play again", True, TEXT_COLOR)
            screen.blit(sub, ((WIDTH-sub.get_width())//2, (HEIGHT-80)//2))

        pygame.display.flip()

# ---------- Run ----------
if __name__ == "__main__":
    main()

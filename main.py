"""
Pac-style Maze Runner (Pygame)
- Tile-based maze
- Runner (player) controlled with arrow keys / WASD
- Catcher chases using BFS pathfinding (moves only on path tiles)
- Catcher speed is 1/4 of runner speed
- Speed boosters (note.png) temporarily increase runner speed
- Exit gate completes level and generates a harder maze (bigger)
Requirements:
    pip install pygame
Usage:
    python main.py
Assets:
    Place girl.png, hod.png, note.png in the same folder as this script.
"""

import pygame
import random
import collections
import time
import sys

# ---------------- CONFIG ----------------
FPS = 60
START_COLS = 21         # must be odd values
START_ROWS = 15         # must be odd values
TILE = 32               # tile size (pixels)
WALL = 1
PATH = 0
BOOST_DURATION = 4.0    # seconds
RUNNER_BASE_SPEED_TILES = 4.0   # tiles per second (movement speed)
# Catcher should be 1/4th of runner -> below we'll compute dynamically

# Colors
COLOR_WALL = (8, 10, 13)
COLOR_PATH_BG = (18, 130, 255)  # outer path color to match earlier look
COLOR_PATH_FILL = (0, 0, 0)
COLOR_GATE = (16, 185, 129)     # green for exit gate

# ---------------- UTILITIES ----------------
def oddify(n):
    return n if n % 2 == 1 else n + 1

# ---------------- MAZE GENERATION (recursive backtracker) ----------------
def generate_maze(cols, rows):
    """Generate a maze with odd cols/rows. Walls=1, path=0."""
    cols = oddify(cols)
    rows = oddify(rows)
    grid = [[WALL for _ in range(cols)] for _ in range(rows)]

    def in_bounds(x, y):
        return 0 <= x < cols and 0 <= y < rows

    # start at (1,1)
    stack = [(1, 1)]
    grid[1][1] = PATH

    while stack:
        x, y = stack[-1]
        neighbors = []
        for dx, dy in [(-2,0),(2,0),(0,-2),(0,2)]:
            nx, ny = x+dx, y+dy
            if in_bounds(nx, ny) and grid[ny][nx] == WALL:
                neighbors.append((nx, ny))
        if neighbors:
            nx, ny = random.choice(neighbors)
            # knock down wall between
            wall_x = (x + nx) // 2
            wall_y = (y + ny) // 2
            grid[wall_y][wall_x] = PATH
            grid[ny][nx] = PATH
            stack.append((nx, ny))
        else:
            stack.pop()

    return grid

# ---------------- PATHFINDING (BFS on tile grid) ----------------
def bfs_path(grid, start, goal):
    """Return list of tile coords from start to goal inclusive, or [] if none."""
    cols = len(grid[0])
    rows = len(grid)
    sx, sy = start
    gx, gy = goal
    if not (0 <= sx < cols and 0 <= sy < rows and 0 <= gx < cols and 0 <= gy < rows):
        return []
    if grid[sy][sx] == WALL or grid[gy][gx] == WALL:
        return []

    q = collections.deque()
    q.append((sx, sy))
    came_from = { (sx, sy): None }
    while q:
        x, y = q.popleft()
        if (x, y) == (gx, gy):
            break
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < cols and 0 <= ny < rows and grid[ny][nx] == PATH and (nx, ny) not in came_from:
                came_from[(nx, ny)] = (x, y)
                q.append((nx, ny))

    if (gx, gy) not in came_from:
        return []

    # reconstruct path
    path = []
    cur = (gx, gy)
    while cur:
        path.append(cur)
        cur = came_from[cur]
    path.reverse()
    return path

# ---------------- GAME ENTITIES ----------------
class Entity:
    def __init__(self, tile_x, tile_y, img=None):
        self.tile_x = tile_x
        self.tile_y = tile_y
        # pixel position (centered on tile)
        self.x = tile_x * TILE + TILE // 2
        self.y = tile_y * TILE + TILE // 2
        self.img = img
        self.target_tile = (tile_x, tile_y)
        self.speed_tiles_per_sec = RUNNER_BASE_SPEED_TILES
        self.boost_expires = 0.0

    def pixel_pos_from_tile(self, t):
        tx, ty = t
        return tx * TILE + TILE // 2, ty * TILE + TILE // 2

    def set_tile(self, tx, ty):
        self.tile_x = tx
        self.tile_y = ty
        self.x, self.y = self.pixel_pos_from_tile((tx, ty))
        self.target_tile = (tx, ty)

    def start_move_to(self, tx, ty):
        self.target_tile = (tx, ty)

    def is_moving(self):
        return (self.tile_x, self.tile_y) != tuple(self.target_tile)

    def update_position(self, dt):
        # move towards target_tile at current speed
        tx, ty = self.target_tile
        target_x, target_y = self.pixel_pos_from_tile((tx, ty))
        dx = target_x - self.x
        dy = target_y - self.y
        dist = (dx*dx + dy*dy) ** 0.5
        if dist < 1e-4:
            # snap
            self.x = target_x; self.y = target_y
            self.tile_x, self.tile_y = tx, ty
            return
        # speed in pixels per second
        pixels_per_sec = (self.speed_tiles_per_sec * TILE)
        step = pixels_per_sec * dt
        if step >= dist:
            self.x = target_x; self.y = target_y
            self.tile_x, self.tile_y = tx, ty
        else:
            self.x += dx / dist * step
            self.y += dy / dist * step

    def draw(self, surf):
        if self.img:
            rect = self.img.get_rect(center=(int(self.x), int(self.y)))
            surf.blit(self.img, rect)
        else:
            # placeholder circle
            pygame.draw.circle(surf, (255,255,0), (int(self.x), int(self.y)), TILE//3)

# ---------------- MAIN GAME CLASS ----------------
class MazeGame:
    def __init__(self, cols, rows):
        pygame.init()
        self.level = 1
        self.cols = oddify(cols)
        self.rows = oddify(rows)
        self.grid = generate_maze(self.cols, self.rows)
        # window size (with border)
        self.width = self.cols * TILE
        self.height = self.rows * TILE
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Pac-Maze Runner - Pygame")
        self.clock = pygame.time.Clock()

        # load images
        try:
            self.runner_img = pygame.image.load("girl.png").convert_alpha()
            self.catcher_img = pygame.image.load("hod.png").convert_alpha()
            self.boost_img = pygame.image.load("note.png").convert_alpha()
        except Exception as e:
            print("Error loading images. Make sure girl.png, hod.png, note.png exist in the same folder.")
            print(e)
            pygame.quit()
            sys.exit(1)

        # scale sprites to tile size
        self.runner_img = pygame.transform.smoothscale(self.runner_img, (TILE-4, TILE-4))
        self.catcher_img = pygame.transform.smoothscale(self.catcher_img, (TILE-4, TILE-4))
        self.boost_img = pygame.transform.smoothscale(self.boost_img, (TILE-6, TILE-6))

        # initialize entities
        self.player = None
        self.catcher = None
        self.boosters = []
        self.gate = None

        self.reset_level(self.cols, self.rows)

        self.running = True

    def find_first_path(self):
        # find a PATH tile to place player (prefer near top-left)
        for y in range(self.rows):
            for x in range(self.cols):
                if self.grid[y][x] == PATH:
                    return (x, y)
        return (1,1)

    def find_farthest_from(self, start):
        # BFS to find farthest reachable tile (useful for placing gate)
        cols = self.cols; rows = self.rows
        sx, sy = start
        q = collections.deque()
        q.append((sx, sy))
        dist = { (sx,sy): 0}
        last = (sx,sy)
        while q:
            x,y = q.popleft()
            last = (x,y)
            for dx,dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                nx, ny = x+dx, y+dy
                if 0 <= nx < cols and 0 <= ny < rows and self.grid[ny][nx] == PATH and (nx,ny) not in dist:
                    dist[(nx,ny)] = dist[(x,y)] + 1
                    q.append((nx,ny))
        return last

    def place_boosters(self, count=3):
        available = [(x,y) for y in range(self.rows) for x in range(self.cols) if self.grid[y][x] == PATH]
        random.shuffle(available)
        chosen = available[:count]
        self.boosters = [{"x":x,"y":y,"active":True} for x,y in chosen]

    def reset_level(self, cols, rows):
        # regenerate maze for current level difficulty
        # increase size slightly each level
        self.cols = oddify(cols + (self.level - 1) * 2)
        self.rows = oddify(rows + (self.level - 1) * 1)
        self.grid = generate_maze(self.cols, self.rows)

        # recreate screen if size changed
        self.width = self.cols * TILE
        self.height = self.rows * TILE
        self.screen = pygame.display.set_mode((self.width, self.height))

        # place player at first path and gate at farthest
        px, py = self.find_first_path()
        gx, gy = self.find_farthest_from((px,py))
        self.player = Entity(px, py, img=self.runner_img)
        self.catcher = Entity(gx, gy, img=self.catcher_img)

        # ensure catcher speed is 1/4 of runner (tiles per second)
        self.player.speed_tiles_per_sec = RUNNER_BASE_SPEED_TILES + (self.level - 1) * 0.5
        self.catcher.speed_tiles_per_sec = max(0.5, self.player.speed_tiles_per_sec / 4.0)

        # gate location (exit)
        self.gate = (gx, gy)
        # place boosters (fewer on higher levels)
        booster_count = max(1, 4 - (self.level // 2))
        self.place_boosters(count=booster_count)

        # AI path
        self.catcher_path = []
        self.catcher_path_index = 0
        self.next_path_update = 0.0

        # timing
        self.level_start_time = time.time()
        self.player.boost_expires = 0.0

    def tile_walkable(self, tx, ty):
        if 0 <= tx < self.cols and 0 <= ty < self.rows:
            return self.grid[ty][tx] == PATH
        return False

    def handle_input(self):
        # handle tile-based movement inputs:
        keys = pygame.key.get_pressed()
        # Only start a new move if player is not currently moving
        if not self.player.is_moving():
            cur_tx, cur_ty = self.player.tile_x, self.player.tile_y
            # allow up/down/left/right and WASD
            desired = None
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                desired = (cur_tx, cur_ty - 1)
            elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                desired = (cur_tx, cur_ty + 1)
            elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
                desired = (cur_tx - 1, cur_ty)
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                desired = (cur_tx + 1, cur_ty)

            if desired:
                tx, ty = desired
                if self.tile_walkable(tx, ty):
                    self.player.start_move_to(tx, ty)

    def update_catcher_ai(self, dt):
        # Update path occasionally (not every frame)
        now = time.time()
        if now >= self.next_path_update or not self.catcher_path:
            # compute BFS path from catcher tile to player tile
            start = (self.catcher.tile_x, self.catcher.tile_y)
            goal = (self.player.tile_x, self.player.tile_y)
            path = bfs_path(self.grid, start, goal)
            if path:
                # path is list of tiles inclusive of start->goal
                self.catcher_path = path[1:]  # skip current position
                self.catcher_path_index = 0
            else:
                self.catcher_path = []
                self.catcher_path_index = 0
            # next update in 0.35 - 0.9 sec (randomized to feel natural)
            self.next_path_update = now + 0.35 + random.random() * 0.55

        # If the catcher is not moving and has path remaining, move to next tile
        if not self.catcher.is_moving() and self.catcher_path_index < len(self.catcher_path):
            tx, ty = self.catcher_path[self.catcher_path_index]
            # ensure tile still walkable
            if self.tile_walkable(tx, ty):
                self.catcher.start_move_to(tx, ty)
                self.catcher_path_index += 1

    def check_boosters(self):
        # if player steps on booster tile (tile-based check)
        for b in self.boosters:
            if b["active"] and (b["x"], b["y"]) == (self.player.tile_x, self.player.tile_y):
                b["active"] = False
                # increase runner speed by 50% (relative)
                self.player.speed_tiles_per_sec = self.player.speed_tiles_per_sec * 1.75
                self.player.boost_expires = time.time() + BOOST_DURATION

    def update_boosts(self):
        if self.player.boost_expires and time.time() >= self.player.boost_expires:
            # reset to base for level
            self.player.speed_tiles_per_sec = RUNNER_BASE_SPEED_TILES + (self.level - 1) * 0.5
            self.player.boost_expires = 0.0
            # also reset catcher speed to remain 1/4 ratio
            self.catcher.speed_tiles_per_sec = max(0.5, self.player.speed_tiles_per_sec / 4.0)

    def check_caught(self):
        # if both occupy same tile, caught
        if (self.player.tile_x, self.player.tile_y) == (self.catcher.tile_x, self.catcher.tile_y):
            return True
        # Also if overlap mid-movement (distance small)
        dx = self.player.x - self.catcher.x
        dy = self.player.y - self.catcher.y
        if (dx*dx + dy*dy) ** 0.5 < (TILE * 0.45):
            return True
        return False

    def check_gate(self):
        if (self.player.tile_x, self.player.tile_y) == tuple(self.gate):
            # level complete
            return True
        return False

    def update(self, dt):
        # input -> start tile movement
        self.handle_input()

        # update entities interpolation
        self.player.update_position(dt)
        # update catcher AI and move
        self.update_catcher_ai(dt)
        self.catcher.update_position(dt)

        # update boosters and durations
        self.check_boosters()
        self.update_boosts()

        # maintain catcher speed 1/4th of runner if boost changed
        self.catcher.speed_tiles_per_sec = max(0.25, self.player.speed_tiles_per_sec / 4.0)

    def draw(self):
        # draw path background
        self.screen.fill(COLOR_PATH_BG)
        # draw grid: walls as rectangles, path as black areas
        for y in range(self.rows):
            for x in range(self.cols):
                rect = pygame.Rect(x*TILE, y*TILE, TILE, TILE)
                if self.grid[y][x] == WALL:
                    pygame.draw.rect(self.screen, COLOR_WALL, rect)
                else:
                    pygame.draw.rect(self.screen, COLOR_PATH_FILL, rect)

        # draw gate
        gx, gy = self.gate
        pygame.draw.rect(self.screen, COLOR_GATE, pygame.Rect(gx*TILE+4, gy*TILE+4, TILE-8, TILE-8))

        # draw boosters
        for b in self.boosters:
            if b["active"]:
                bx = b["x"]*TILE + TILE//2
                by = b["y"]*TILE + TILE//2
                rect = self.boost_img.get_rect(center=(bx, by))
                self.screen.blit(self.boost_img, rect)

        # draw catcher then player (so player appears on top)
        self.catcher.draw(self.screen)
        self.player.draw(self.screen)

        # HUD
        font = pygame.font.SysFont(None, 20)
        text = font.render(f"Level: {self.level}   Time: {int(time.time()-self.level_start_time)}s", True, (220,220,220))
        self.screen.blit(text, (6,6))

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0  # seconds elapsed
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    self.running = False
                elif ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_ESCAPE:
                        self.running = False

            self.update(dt)

            # Check lose
            if self.check_caught():
                # show message and reset level
                print("Caught! Game Over.")
                # Simple dialog via Pygame
                self.show_message("Caught! Game Over. Press Enter to restart or Esc to quit.")
                # wait for user input
                self.wait_for_restart_or_quit()
                # restart same level
                self.reset_level(START_COLS, START_ROWS)
                continue

            # Check level complete
            if self.check_gate():
                # show message
                self.level += 1
                self.show_message(f"Level {self.level-1} complete! Proceeding to Level {self.level}...")
                # regenerate new level (harder)
                self.reset_level(START_COLS, START_ROWS)
                continue

            self.draw()
            pygame.display.flip()

        pygame.quit()

    def show_message(self, message, seconds=None):
        # overlay message on screen; if seconds is None wait for short delay then return
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0,0,0,160))
        font = pygame.font.SysFont(None, 36)
        text = font.render(message, True, (255,255,255))
        tw, th = text.get_size()
        overlay.blit(text, ((self.width - tw)//2, (self.height - th)//2))
        self.screen.blit(overlay, (0,0))
        pygame.display.flip()
        if seconds:
            pygame.time.delay(int(seconds*1000))

    def wait_for_restart_or_quit(self):
        waiting = True
        while waiting:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
                elif ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_RETURN or ev.key == pygame.K_KP_ENTER:
                        waiting = False
                        return
                    elif ev.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit(0)
            self.clock.tick(20)

# ---------------- RUN ----------------
if __name__ == "__main__":
    game = MazeGame(START_COLS, START_ROWS)
    game.run()

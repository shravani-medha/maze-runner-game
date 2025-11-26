import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Maze Runner")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Load sprites
player_sprites = [pygame.image.load("boy.png"), pygame.image.load("girl.png")]
enemy_sprite = pygame.image.load("hod.png")

# Load sounds
eat_sound = pygame.mixer.Sound("eat.wav")
hit_sound = pygame.mixer.Sound("hit.wav")
win_sound = pygame.mixer.Sound("win.wav")

# Background music
try:
    pygame.mixer.music.load("bgm.mp3")
    pygame.mixer.music.play(-1)
except:
    print("Background music not found.")

# Game settings
TILE_SIZE = 40
PLAYER_SPEED = 4
ENEMY_SPEED = 4
FPS = 60
MAX_LIVES = 3

# Levels (0 = empty, 1 = wall, 2 = pellet)
LEVELS = [
    [
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,2,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,2,0,1],
        [1,0,1,1,0,1,0,1,1,1,0,1,0,1,1,1,0,1,0,1],
        [1,0,1,0,0,0,0,0,2,0,0,0,0,0,0,1,0,0,0,1],
        [1,0,1,0,1,1,1,1,1,1,1,1,1,1,0,1,1,1,0,1],
        [1,0,0,0,0,0,2,0,0,0,2,0,0,0,0,0,0,0,0,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
    ],
    # Add more levels here
]

current_level = 0
maze = LEVELS[current_level]

# Helper functions
def draw_maze(maze):
    for y, row in enumerate(maze):
        for x, tile in enumerate(row):
            rect = pygame.Rect(x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE)
            if tile == 1:
                pygame.draw.rect(screen, BLACK, rect)
            elif tile == 2:
                pygame.draw.circle(screen, GREEN, rect.center, 5)

def get_tile(pos):
    x, y = pos
    return maze[y // TILE_SIZE][x // TILE_SIZE]

def set_tile(pos, value):
    x, y = pos
    maze[y // TILE_SIZE][x // TILE_SIZE] = value

# Player class
class Player:
    def __init__(self):
        self.image = player_sprites[0]  # Default sprite
        self.rect = self.image.get_rect()
        self.rect.topleft = (TILE_SIZE, TILE_SIZE)
        self.lives = MAX_LIVES
        self.score = 0

    def move(self, dx, dy):
        new_rect = self.rect.move(dx, dy)
        if not self.collide(new_rect):
            self.rect = new_rect
            if get_tile(self.rect.center) == 2:
                set_tile(self.rect.center, 0)
                self.score += 1
                eat_sound.play()

    def collide(self, rect):
        x1 = rect.left // TILE_SIZE
        y1 = rect.top // TILE_SIZE
        x2 = rect.right // TILE_SIZE
        y2 = rect.bottom // TILE_SIZE
        for y in range(y1, y2+1):
            for x in range(x1, x2+1):
                if y < 0 or y >= len(maze) or x < 0 or x >= len(maze[0]):
                    return True
                if maze[y][x] == 1:
                    return True
        return False

    def draw(self):
        screen.blit(self.image, self.rect.topleft)

# Enemy class
class Enemy:
    def __init__(self):
        self.image = enemy_sprite
        self.rect = self.image.get_rect()
        self.rect.topleft = (WIDTH - TILE_SIZE*2, HEIGHT - TILE_SIZE*2)

    def move_towards(self, target):
        dx = dy = 0
        if self.rect.x < target.rect.x: dx = ENEMY_SPEED
        elif self.rect.x > target.rect.x: dx = -ENEMY_SPEED
        if self.rect.y < target.rect.y: dy = ENEMY_SPEED
        elif self.rect.y > target.rect.y: dy = -ENEMY_SPEED
        new_rect = self.rect.move(dx, dy)
        if not player.collide(new_rect):
            self.rect = new_rect

    def draw(self):
        screen.blit(self.image, self.rect.topleft)

# Game loop
player = Player()
enemy = Enemy()
clock = pygame.time.Clock()

font = pygame.font.SysFont(None, 36)

def show_text(text, pos, color=RED):
    img = font.render(text, True, color)
    screen.blit(img, pos)

running = True
while running:
    screen.fill(WHITE)
    draw_maze(maze)
    player.draw()
    enemy.draw()
    show_text(f"Lives: {player.lives} Score: {player.score}", (10, HEIGHT - 40))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player.move(-PLAYER_SPEED, 0)
    if keys[pygame.K_RIGHT]:
        player.move(PLAYER_SPEED, 0)
    if keys[pygame.K_UP]:
        player.move(0, -PLAYER_SPEED)
    if keys[pygame.K_DOWN]:
        player.move(0, PLAYER_SPEED)

    enemy.move_towards(player)

    if player.rect.colliderect(enemy.rect):
        player.lives -= 1
        hit_sound.play()
        player.rect.topleft = (TILE_SIZE, TILE_SIZE)
        enemy.rect.topleft = (WIDTH - TILE_SIZE*2, HEIGHT - TILE_SIZE*2)
        if player.lives <= 0:
            show_text("GAME OVER", (WIDTH//2 - 100, HEIGHT//2), RED)
            pygame.display.flip()
            pygame.time.wait(3000)
            running = False

    # Check if all pellets eaten
    if all(2 not in row for row in maze):
        win_sound.play()
        current_level += 1
        if current_level < len(LEVELS):
            maze = LEVELS[current_level]
            player.rect.topleft = (TILE_SIZE, TILE_SIZE)
            enemy.rect.topleft = (WIDTH - TILE_SIZE*2, HEIGHT - TILE_SIZE*2)
        else:
            show_text("YOU WIN!", (WIDTH//2 - 100, HEIGHT//2), GREEN)
            pygame.display.flip()
            pygame.time.wait(3000)
            running = False

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()

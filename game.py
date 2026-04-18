import pgzrun
import time
import random
import pygame

TILE_SIZE = 20
WIDTH, HEIGHT = 1200, 800
COLS, ROWS = WIDTH // TILE_SIZE, HEIGHT // TILE_SIZE
UI_HEIGHT_TILES = 4

show_intro = True
grid = []
lives = 3
score = 0
level = 1
game_over = False
move_delay = 0.08
timer = 0
invulnerable_timer = 0
TITLE = "XONIX"
#ICON = 'icon.png'

def init_grid():
    global grid
    grid = []
    PLAYABLE_ROWS = ROWS - UI_HEIGHT_TILES
    for y in range(ROWS):
        row = []
        for x in range(COLS):
            is_side = (x == 0 or x == COLS-1)
            is_top = (y == 0)
            is_bottom_safe_zone = (PLAYABLE_ROWS - 1 <= y < PLAYABLE_ROWS)
            if is_side or is_top or is_bottom_safe_zone or y >= PLAYABLE_ROWS:
                row.append(1)
            else:
                row.append(0)
        grid.append(row)

def create_enemies(count):
    global enemies
    enemies = []
    PLAYABLE_ROWS = ROWS - UI_HEIGHT_TILES
    divisions = int(count**0.5) if count > 1 else 1
    sec_w = COLS // divisions
    sec_h = PLAYABLE_ROWS // (max(1, count // divisions))

    for i in range(count):
        col_idx = i % divisions
        row_idx = i // divisions
        x_min, x_max = col_idx * sec_w, (col_idx + 1) * sec_w
        y_min, y_max = row_idx * sec_h, (row_idx + 1) * sec_h
        sector_cells = []
        for y in range(y_min, min(y_max, PLAYABLE_ROWS)):
            for x in range(x_min, min(x_max, COLS)):
                if grid[y][x] == 0:
                    sector_cells.append((x, y))
        if sector_cells:
            fx, fy = random.choice(sector_cells)
            spawn_pos = (fx * TILE_SIZE + 10, fy * TILE_SIZE + 10)
        else:
            all_free = [(x, y) for y in range(PLAYABLE_ROWS) for x in range(COLS) if grid[y][x] == 0]
            if all_free:
                fx, fy = random.choice(all_free)
                spawn_pos = (fx * TILE_SIZE + 10, fy * TILE_SIZE + 10)
            else:
                spawn_pos = (WIDTH//2, (HEIGHT - UI_HEIGHT_TILES*20)//2)

        e = Actor('enemy', center=spawn_pos)
        e.vx = random.choice([-4, -3, 3, 4])
        e.vy = random.choice([-4, -3, 3, 4])
        enemies.append(e)

def get_territory_percentage():
    """Calculate filled territory percentage"""
    PLAYABLE_ROWS = ROWS - UI_HEIGHT_TILES
    total_cells = COLS * PLAYABLE_ROWS
    captured_cells = sum(row.count(1) for row in grid[:PLAYABLE_ROWS])
    return int((captured_cells / total_cells) * 100)

def restart_game():
    global lives, score, level, game_over, show_intro
    lives = 3
    score = 0
    level = 1
    game_over = False
    show_intro = False
    init_grid()
    create_enemies(level)
    player.topleft = (0, 0)
    player.direction = (0, 0)

init_grid()
player = Actor('player', topleft=(0, 0))
player.direction = (0, 0)
enemies = []
create_enemies(level)

def draw():
    screen.clear()
    screen.blit('ui_panel', (0, 0))
    for y in range(ROWS - UI_HEIGHT_TILES):
        for x in range(COLS):
            if grid[y][x] == 1:
                screen.blit('tile_captured', (x * TILE_SIZE, y * TILE_SIZE))
            elif grid[y][x] == 2:
                screen.blit('trace', (x * TILE_SIZE, y * TILE_SIZE))

    for enemy in enemies:
        enemy.draw()

    for i in range(lives):
        screen.blit('heart', (1175, 771 - i * 22))
    screen.draw.text(f"{score}", (173, 741), color="white", fontsize=45, fontname="myfonta")
    screen.draw.text(f"{level}", (810, 741), color="white", fontsize=45, fontname="myfonta")
    territory_pct = get_territory_percentage()
    screen.draw.text(f"{territory_pct}%", (500, 741), color="white", fontsize=45, fontname="myfonta")

    if not game_over:
        if invulnerable_timer <= 0 or int(time.time() * 10) % 2 == 0:
            player.draw()

    if game_over:
        try:
            screen.blit('game_over_bg', (0, 0))
        except:
            screen.draw.filled_rect(Rect(0,0,WIDTH,HEIGHT-80), (0,0,0,180))
        screen.draw.text("GAME OVER", center=(WIDTH//2, HEIGHT//2 - 60), fontsize=80, color="white", fontname="myfonta")
        screen.draw.text("PRESS 'R' TO RESTART", center=(WIDTH//2, HEIGHT//2 + 10), fontsize=40, color="white", fontname="myfonta")
        # ДОБАВЛЕННЫЙ БЛОК НАДПИСИ
        screen.draw.text("IF YOU WANT TO SAVE A RECORD OF THIS GAME, PRESS 'V'", center=(WIDTH//2, HEIGHT//2 + 60), fontsize=30, color="white", fontname="myfonta")

    if show_intro:
        try:
            screen.blit('instruction', (0, 0))
        except:
            screen.draw.filled_rect(Rect(0,0,WIDTH,HEIGHT), (0,0,0,200))
        screen.draw.text("PRESS ENTER OR SPACE TO START", center=(WIDTH//2, HEIGHT - 25), color="white", fontsize=38, fontname="myfonta")

def update(dt):
    global timer, game_over, show_intro, invulnerable_timer
    if game_over:
        if keyboard.r: restart_game()
        # ДОБАВЛЕННЫЙ БЛОК СОХРАНЕНИЯ
        if keyboard.v:
            pygame.image.save(pygame.display.get_surface(), "game_screenshot.png")
        return
    if show_intro:
        if keyboard.RETURN or keyboard.KP_ENTER or keyboard.SPACE: show_intro = False
        return
    if invulnerable_timer > 0: invulnerable_timer -= dt

    on_base = False
    curr_x, curr_y = round(player.left / TILE_SIZE), round(player.top / TILE_SIZE)
    if 0 <= curr_x < COLS and 0 <= curr_y < (ROWS - UI_HEIGHT_TILES):
        if grid[curr_y][curr_x] == 1: on_base = True

    if keyboard.space and on_base: player.direction = (0, 0)
    if keyboard.a:
        if on_base or player.direction != (1, 0): player.direction = (-1, 0)
    elif keyboard.d:
        if on_base or player.direction != (-1, 0): player.direction = (1, 0)
    elif keyboard.w:
        if on_base or player.direction != (0, 1): player.direction = (0, -1)
    elif keyboard.s:
        if on_base or player.direction != (0, -1): player.direction = (0, 1)

    timer += dt
    if timer > move_delay:
        move_player()
        timer = 0
    for enemy in enemies: move_enemy(enemy)

def move_player():
    dx, dy = player.direction
    if dx == 0 and dy == 0: return
    curr_x, curr_y = round(player.left / TILE_SIZE), round(player.top / TILE_SIZE)
    nx, ny = curr_x + dx, curr_y + dy
    if 0 <= nx < COLS and 0 <= ny < (ROWS - UI_HEIGHT_TILES):
        if grid[ny][nx] == 2:
            reset_game()
            return
        old_status = grid[ny][nx]
        if old_status == 0: grid[ny][nx] = 2
        player.left, player.top = nx * TILE_SIZE, ny * TILE_SIZE
        if old_status == 1:
            if any(2 in row for row in grid):
                complete_capture()
                player.direction = (0, 0)

def move_enemy(enemy):
    if invulnerable_timer <= 0:
        ex, ey = int(enemy.x // TILE_SIZE), int(enemy.y // TILE_SIZE)
        if 0 <= ex < COLS and 0 <= ey < (ROWS - UI_HEIGHT_TILES):
            if grid[ey][ex] == 2 or player.colliderect(enemy):
                reset_game()
                return
    new_x = enemy.x + enemy.vx * 1.25
    new_y = enemy.y + enemy.vy * 1.25
    gx = int((new_x + (10 if enemy.vx > 0 else -10)) // TILE_SIZE)
    if gx < 0 or gx >= COLS or grid[int(enemy.y//TILE_SIZE)][gx] == 1:
        enemy.vx *= -1
    else:
        enemy.x = new_x
    gy = int((new_y + (10 if enemy.vy > 0 else -10)) // TILE_SIZE)
    if gy < 0 or gy >= (ROWS - UI_HEIGHT_TILES) or grid[gy][int(enemy.x//TILE_SIZE)] == 1:
        enemy.vy *= -1
    else:
        enemy.y = new_y

def complete_capture():
    global score, level
    captured_this_turn = 0
    for y in range(ROWS):
        for x in range(COLS):
            if grid[y][x] == 2:
                grid[y][x] = 1
                captured_this_turn += 1
    visited_by_any_enemy = [[False for _ in range(COLS)] for _ in range(ROWS)]
    for en in enemies:
        ex, ey = int(en.x // TILE_SIZE), int(en.y // TILE_SIZE)
        if 0 <= ex < COLS and 0 <= ey < (ROWS - UI_HEIGHT_TILES):
            stack = [(ex, ey)]
            while stack:
                cx, cy = stack.pop()
                if 0 <= cx < COLS and 0 <= cy < (ROWS - UI_HEIGHT_TILES) and grid[cy][cx] == 0 and not visited_by_any_enemy[cy][cx]:
                    visited_by_any_enemy[cy][cx] = True
                    stack.extend([(cx+1, cy), (cx-1, cy), (cx, cy+1), (cx, cy-1)])
    for y in range(ROWS - UI_HEIGHT_TILES):
        for x in range(COLS):
            if grid[y][x] == 0 and not visited_by_any_enemy[y][x]:
                grid[y][x] = 1
                captured_this_turn += 1
    score += captured_this_turn * 10
    captured_now = sum(row.count(1) for row in grid[:ROWS-UI_HEIGHT_TILES])
    if captured_now / (COLS * (ROWS-UI_HEIGHT_TILES)) >= 0.75:
        level += 1
        init_grid(); create_enemies(level)
        player.topleft = (0, 0); player.direction = (0, 0)

def reset_game():
    global lives, game_over, invulnerable_timer
    lives -= 1
    if lives <= 0: game_over = True; return
    invulnerable_timer = 2.0
    player.topleft, player.direction = (0, 0), (0, 0)
    for y in range(ROWS):
        for x in range(COLS):
            if grid[y][x] == 2: grid[y][x] = 0
    create_enemies(level)

pgzrun.go()

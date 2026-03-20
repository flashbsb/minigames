import random
import turtle
import os
import json

TILE_SIZE = 24
PLAYER_BASE_INTERVAL = 5
GHOST_BASE_INTERVAL = 10
MIN_GHOST_INTERVAL = 3
DIFFICULTY_STEP_PELLETS = 15
MAX_LEVEL = 5
LEVEL_CLEAR_BONUS = 500
RESPAWN_INVULNERABLE_FRAMES = 60
FRIGHTENED_FRAMES_POWER_PELLET = 200

COLOR_BG = "#05060a"
COLOR_WALL = "#1f4ae0"
COLOR_WALL_BORDER = "#6f8fff"
COLOR_PELLET = "#f0f0f0"
COLOR_POWER = "#ffd166"
COLOR_ROBOT = "#25c2f5"
GHOST_COLORS = ["#ff4d4d", "#ff8fab", "#7ae7ff", "#ffa94d", "#9d4edd", "#5ac18e"]

LEVEL_MAPS = [
    [
        "#####################",
        "#o........#........o#",
        "#.###.###.#.###.###.#",
        "#...................#",
        "#.###.#.#####.#.###.#",
        "#.....#...#...#.....#",
        "#####.###.#.###.#####",
        "#####.#.......#.#####",
        "#####.#.## ##.#.#####",
        "#.........G.........#",
        "#####.#.#####.#.#####",
        "#####.#...#...#.#####",
        "#.........#.........#",
        "#.###.###.#.###.###.#",
        "#o..#.....P.....#..o#",
        "###.#.#.#####.#.#.###",
        "#.....#...#...#.....#",
        "#.#######.#.#######.#",
        "#...................#",
        "#####################",
    ],
    [
        "#####################",
        "#.....#.......#.....#",
        "#.###.#.#####.#.###.#",
        "#.###.#.#o#o#.#.###.#",
        "#.###.#.#####.#.###.#",
        "#...................#",
        "###.###.## ##.###.###",
        "###.#.......G.....###",
        "###.#.##.###.##.#.###",
        "#.........P.........#",
        "###.#.##.###.##.#.###",
        "###.#.......G.....###",
        "###.###.## ##.###.###",
        "#...................#",
        "#.###.#.#####.#.###.#",
        "#...#.#...#...#.#...#",
        "#o..#.#...#...#.#..o#",
        "#####################",
    ],
    [
        "#####################",
        "#o..#.....#.....#..o#",
        "#.##.#.###.#.###.##.#",
        "#....#.....#.....#...#",
        "###..#.###.#.###..###",
        "#####.#.....G.....####",
        "#.....#.##.###.#.....#",
        "###..#.#.........#..###",
        "#....#.#.#######.#....#",
        "#.##.#.#.#o#o#o#.#.##.#",
        "#.##...#.#P P#.#...##.#",
        "#.##.#.#.#   #.#.#.##.#",
        "#....#.#.#######.#....#",
        "###..#.#.........#..###",
        "#.....#.##.###.##.#.....#",
        "#####.#.....#.....#.####",
        "#....#.#.###.#.###.#....#",
        "#o...#...............#..#",
        "#####################",
    ],
    [
        "#####################",
        "#.......#.....#......#",
        "#.#####.#.###.#.#####.#",
        "#.#...#.#.....#.#...#.#",
        "#.#.#.#.#.###.#.#.#.#.#",
        "#.....#.#..P..#.#.....#",
        "#####.#.##   ##.#.#####",
        "    #.#.#  G  #.#.#",
        "    #...#.....#...#",
        "    #.#.#.###.#.#.#",
        "    #.#.#.#o#.#.#.#",
        "    #.#.#.###.#.#.#",
        "    #...#.....#...#",
        "    #.#.#.###.#.#.#",
        "    #.#.#.#   #.#.#",
        "    #.#.#.....#.#.#",
        "    #...#.....#...#",
        "    #################",
    ],
    [
        "#####################",
        "#...................#",
        "#.#################.#",
        "#.#...............#.#",
        "#.#.#############.#.#",
        "#.#.#...........#.#.#",
        "#.#.#.#.## ##.#.#.#.#",
        "#.#.#.#.#  G  #.#.#.#",
        "#.#.#.#.#     #.#.#.#",
        "#.#.#.#.#.###.#.#.#.#",
        "#.#.#.#.#.#P#.#.#.#.#",
        "#.#.#.#.#.#o#.#.#.#.#",
        "#.#.#.#.#.###.#.#.#.#",
        "#.#.#.#.#     #.#.#.#",
        "#.#.#.#.#.###.#.#.#.#",
        "#.#.#.#.........#.#.#",
        "#.#.#.###########.#.#",
        "#.#................#.#",
        "#.#################.#",
        "#...................#",
        "#####################",
    ],
]

LEVEL_MAP = LEVEL_MAPS[0]
ROWS = len(LEVEL_MAP)
COLS = len(LEVEL_MAP[0])
SCREEN_WIDTH = COLS * TILE_SIZE + 150
SCREEN_HEIGHT = ROWS * TILE_SIZE + 150

DIRECTIONS = {
    "up": (0, -1),
    "down": (0, 1),
    "left": (-1, 0),
    "right": (1, 0),
    "stop": (0, 0),
}

GHOST_PERSONALITIES = ["random", "chaser", "ambusher", "confused"]


class GameState:
    def __init__(self):
        self.score = 0
        self.high_score = self.load_high_score()
        self.lives = 3
        self.level = 1
        self.game_over = False
        self.victory = False
        self.paused = False
        self.frame = 0
        self.eaten_this_level = 0
        self.total_pellets = 0
        self.difficulty_stage = 1
        self.ghost_interval = GHOST_BASE_INTERVAL
        self.respawn_invulnerable_frames = 0
        self.frightened_frames = 0
        self.combo_count = 0
        self.power_mode_timer = 0

    def load_high_score(self):
        try:
            if os.path.exists("pacrobot_highscore.txt"):
                with open("pacrobot_highscore.txt", "r") as f:
                    return int(f.read().strip())
        except:
            pass
        return 0

    def save_high_score(self):
        try:
            with open("pacrobot_highscore.txt", "w") as f:
                f.write(str(self.high_score))
        except:
            pass

    def reset_run(self):
        self.score = 0
        self.lives = 3
        self.level = 1
        self.game_over = False
        self.victory = False
        self.paused = False
        self.frame = 0
        self.eaten_this_level = 0
        self.difficulty_stage = 1
        self.ghost_interval = GHOST_BASE_INTERVAL
        self.respawn_invulnerable_frames = 0
        self.frightened_frames = 0
        self.combo_count = 0
        self.power_mode_timer = 0


class Actor(turtle.Turtle):
    def __init__(self, shape, color, size=1.0):
        super().__init__(shape=shape)
        self.penup()
        self.speed(0)
        self.color(color)
        self.base_color = color
        self.shapesize(size, size)
        self.grid_x = 0
        self.grid_y = 0
        self.direction = "stop"
        self.next_direction = "stop"
        self.personality = "random"
        self.dx = 0
        self.dy = 0
        self.life = 0

    def sync_to_grid(self):
        self.goto(grid_to_screen(self.grid_x, self.grid_y))


class Pellet(turtle.Turtle):
    def __init__(self, x, y, power=False):
        super().__init__(shape="circle")
        self.penup()
        self.speed(0)
        self.grid_x = x
        self.grid_y = y
        self.power = power
        if power:
            self.color(COLOR_POWER)
            self.shapesize(0.55, 0.55)
            self.pulse_state = 0
        else:
            self.color(COLOR_PELLET)
            self.shapesize(0.22, 0.22)
        self.goto(grid_to_screen(x, y))

    def pulse(self):
        if self.power:
            self.pulse_state = (self.pulse_state + 1) % 20
            size = 0.45 + 0.15 * (self.pulse_state / 10)
            self.shapesize(size, size)


state = GameState()

walls = set()
player_spawn = (1, 1)
ghost_spawns = []
pellet_map = {}
ghosts = []
particles = []


win = turtle.Screen()
win.title("PacRobot - Robot vs Aliens")
win.bgcolor(COLOR_BG)
win.setup(SCREEN_WIDTH, SCREEN_HEIGHT)
win.tracer(0)


maze_pen = turtle.Turtle()
maze_pen.hideturtle()
maze_pen.penup()
maze_pen.speed(0)

hud_pen = turtle.Turtle()
hud_pen.hideturtle()
hud_pen.penup()
hud_pen.speed(0)

message_pen = turtle.Turtle()
message_pen.hideturtle()
message_pen.penup()
message_pen.speed(0)

pause_pen = turtle.Turtle()
pause_pen.hideturtle()
pause_pen.penup()
pause_pen.speed(0)


def register_custom_shapes():
    robot = turtle.Shape("compound")
    robot.addcomponent(((-12, -10), (12, -10), (12, 6), (-12, 6)), "#25c2f5", "#0b132b")
    robot.addcomponent(((-9, 6), (9, 6), (9, 14), (-9, 14)), "#5fe1ff", "#0b132b")
    robot.addcomponent(((-5, 10), (5, 10), (5, 12), (-5, 12)), "#111827", "#111827")
    robot.addcomponent(((-1, 14), (1, 14), (1, 20), (-1, 20)), "#94d2ff", "#0b132b")
    robot.addcomponent(((-3, 20), (3, 20), (3, 22), (-3, 22)), "#94d2ff", "#0b132b")
    win.register_shape("robot_unit", robot)

    alien = (
        (-12, -8), (-9, -14), (-5, -12), (-3, -16), (0, -12),
        (3, -16), (5, -12), (9, -14), (12, -8),
        (9, 1), (6, 7), (3, 12), (0, 14),
        (-3, 12), (-6, 7), (-9, 1),
    )
    win.register_shape("alien_unit", alien)

    ghost = (
        (-10, -10), (-10, 8), (0, 14), (10, 8), (10, -10),
        (7, -6), (4, -10), (1, -6), (-1, -6), (-4, -10), (-7, -6),
    )
    win.register_shape("ghost_unit", ghost)


register_custom_shapes()
player = Actor("robot_unit", COLOR_ROBOT, 1.0)


def grid_to_screen(x, y):
    left = -(COLS * TILE_SIZE) / 2 + TILE_SIZE / 2
    top = (ROWS * TILE_SIZE) / 2 - TILE_SIZE / 2
    return left + x * TILE_SIZE, top - y * TILE_SIZE


def parse_static_map():
    global player_spawn, LEVEL_MAP
    LEVEL_MAP = LEVEL_MAPS[(state.level - 1) % len(LEVEL_MAPS)]
    expected_cols = len(LEVEL_MAP[0])

    walls.clear()
    ghost_spawns.clear()

    for y, row in enumerate(LEVEL_MAP):
        if len(row) != expected_cols:
            continue
        for x, char in enumerate(row):
            if char == "#":
                walls.add((x, y))
            elif char == "P":
                player_spawn = (x, y)
            elif char == "G":
                ghost_spawns.append((x, y))

    if not ghost_spawns:
        ghost_spawns.append((COLS // 2, ROWS // 2))


def draw_maze():
    maze_pen.clear()
    maze_pen.shape("square")
    maze_pen.shapesize(1.0, 1.0)

    for x, y in walls:
        sx, sy = grid_to_screen(x, y)
        maze_pen.goto(sx, sy)
        maze_pen.color(COLOR_WALL_BORDER)
        maze_pen.stamp()
        maze_pen.shapesize(0.82, 0.82)
        maze_pen.color(COLOR_WALL)
        maze_pen.stamp()
        maze_pen.shapesize(1.0, 1.0)


def build_pellets_for_level():
    for pellet in pellet_map.values():
        pellet.hideturtle()
    pellet_map.clear()

    parse_static_map()
    draw_maze()

    for y, row in enumerate(LEVEL_MAP):
        for x, char in enumerate(row):
            if char in {".", "o", "P", "G", " "} and (x, y) not in walls:
                power = char == "o"
                pellet = Pellet(x, y, power=power)
                pellet_map[(x, y)] = pellet

    state.total_pellets = len(pellet_map)
    state.eaten_this_level = 0


def update_hud():
    hud_pen.clear()
    x_pos = -SCREEN_WIDTH // 2 + 20
    y_pos = SCREEN_HEIGHT // 2 - 40

    hud_pen.goto(x_pos, y_pos)
    hud_pen.color("#9be564")
    hud_pen.write(f"SCORE: {state.score}", font=("Courier", 14, "bold"))

    hud_pen.goto(x_pos, y_pos - 25)
    hud_pen.color("#ffd166")
    hud_pen.write(f"HIGH: {state.high_score}", font=("Courier", 12, "normal"))

    hud_pen.goto(x_pos + SCREEN_WIDTH // 2 - 50, y_pos)
    hud_pen.color("#ff6b6b")
    lives_text = " ".join(["♥"] * state.lives) if state.lives > 0 else "X X X"
    hud_pen.write(f"LIVES: {lives_text}", font=("Courier", 14, "bold"))

    hud_pen.goto(x_pos + SCREEN_WIDTH // 2 - 50, y_pos - 25)
    hud_pen.color("#94d2ff")
    hud_pen.write(f"LEVEL: {state.level}/{MAX_LEVEL}", font=("Courier", 12, "normal"))

    y_pos2 = -SCREEN_HEIGHT // 2 + 30
    hud_pen.goto(0, y_pos2)

    if state.frightened_frames > 0:
        hud_pen.color("#ffd166")
        remaining = state.frightened_frames // 10
        hud_pen.write(f"POWER MODE: {remaining}s", font=("Courier", 12, "bold"))
    else:
        hud_pen.color("#5ac18e")
        hud_pen.write(f"ALIENS: {len(ghosts)}", font=("Courier", 12, "normal"))


def can_move(x, y):
    return 0 <= x < COLS and 0 <= y < ROWS and (x, y) not in walls


def try_move(actor):
    nx, ny = DIRECTIONS[actor.next_direction]
    tx, ty = actor.grid_x + nx, actor.grid_y + ny
    if actor.next_direction != "stop" and can_move(tx, ty):
        actor.direction = actor.next_direction

    dx, dy = DIRECTIONS[actor.direction]
    nx, ny = actor.grid_x + dx, actor.grid_y + dy
    if actor.direction != "stop" and can_move(nx, ny):
        actor.grid_x, actor.grid_y = nx, ny
        actor.sync_to_grid()


def spawn_ghosts():
    target = min(2 + state.level + state.difficulty_stage // 2, len(GHOST_COLORS))

    while len(ghosts) < target:
        spawn = ghost_spawns[len(ghosts) % len(ghost_spawns)]
        color = GHOST_COLORS[len(ghosts) % len(GHOST_COLORS)]
        ghost = Actor("ghost_unit", color, 0.9)
        ghost.grid_x, ghost.grid_y = spawn
        ghost.direction = random.choice(["up", "down", "left", "right"])
        ghost.next_direction = ghost.direction
        ghost.sync_to_grid()
        ghost.personality = random.choice(GHOST_PERSONALITIES)
        ghosts.append(ghost)


def reset_positions():
    player.grid_x, player.grid_y = player_spawn
    player.direction = "stop"
    player.next_direction = "stop"
    player.sync_to_grid()

    for i, ghost in enumerate(ghosts):
        spawn = ghost_spawns[i % len(ghost_spawns)]
        ghost.grid_x, ghost.grid_y = spawn
        ghost.direction = random.choice(["up", "down", "left", "right"])
        ghost.next_direction = ghost.direction
        ghost.sync_to_grid()


class Particle:
    def __init__(self, x, y, color):
        self.turtle = turtle.Turtle()
        self.turtle.shape("circle")
        self.turtle.color(color)
        self.turtle.shapesize(0.2, 0.2)
        self.turtle.penup()
        self.turtle.goto(grid_to_screen(x, y))
        self.dx = random.uniform(-2, 2)
        self.dy = random.uniform(-2, 2)
        self.life = 15

    def update(self):
        self.turtle.goto(self.turtle.xcor() + self.dx, self.turtle.ycor() + self.dy)
        self.life -= 1
        self.turtle.shapesize(self.life / 30, self.life / 30)
        return self.life > 0

    def hide(self):
        self.turtle.hideturtle()


def create_particle(x, y, color):
    p = Particle(x, y, color)
    particles.append(p)


def update_particles():
    global particles
    for p in particles[:]:
        if not p.update():
            p.hide()
            particles.remove(p)


def consume_pellet_if_any():
    key = (player.grid_x, player.grid_y)
    pellet = pellet_map.pop(key, None)
    if pellet is None:
        state.combo_count = 0
        return

    pellet.hideturtle()

    if pellet.power:
        gain = 50
        state.frightened_frames = FRIGHTENED_FRAMES_POWER_PELLET
        state.combo_count = 0
        for i in range(-1, 2):
            for j in range(-1, 2):
                if (i, j) != (0, 0):
                    create_particle(player.grid_x + i, player.grid_y + j, "#ffd166")
        show_message("POWER MODE!", "#ffd166", duration_frames=25)
        for ghost in ghosts:
            ghost.color("#7d8597")
    else:
        state.combo_count += 1
        combo_multiplier = min(state.combo_count, 5)
        gain = 10 * combo_multiplier
        if state.combo_count >= 3:
            create_particle(player.grid_x, player.grid_y, "#9be564")
            if state.combo_count == 5:
                show_message("INCREDIBLE! +50", "#9be564", duration_frames=15)

    state.score += gain
    if state.score > state.high_score:
        state.high_score = state.score
        state.save_high_score()

    state.eaten_this_level += 1
    update_difficulty()
    spawn_ghosts()
    update_hud()


def ghost_choose_direction(ghost):
    options = []
    for dname, (dx, dy) in DIRECTIONS.items():
        if dname == "stop":
            continue
        nx, ny = ghost.grid_x + dx, ghost.grid_y + dy
        if can_move(nx, ny):
            options.append(dname)

    if not options:
        return "stop"

    reverse = {
        "up": "down", "down": "up", "left": "right", "right": "left", "stop": "stop"
    }

    if state.frightened_frames > 0:
        if len(options) > 1 and reverse.get(ghost.direction) in options:
            options.remove(reverse[ghost.direction])
        return random.choice(options)

    personality = getattr(ghost, 'personality', 'random')

    if personality == "chaser":
        best = options[0]
        best_dist = 99999
        for dname in options:
            if reverse.get(ghost.direction) == dname and len(options) > 1:
                continue
            dx, dy = DIRECTIONS[dname]
            nx, ny = ghost.grid_x + dx, ghost.grid_y + dy
            dist = abs(player.grid_x - nx) + abs(player.grid_y - ny)
            if dist < best_dist:
                best_dist = dist
                best = dname
        return best

    elif personality == "ambusher":
        best = options[0]
        best_dist = 0
        for dname in options:
            if reverse.get(ghost.direction) == dname and len(options) > 1:
                continue
            dx, dy = DIRECTIONS[dname]
            nx, ny = ghost.grid_x + dx, ghost.grid_y + dy
            dist = abs(player.grid_x - nx) + abs(player.grid_y - ny)
            if dist > best_dist:
                best_dist = dist
                best = dname
        return best

    elif personality == "confused":
        if random.random() < 0.3:
            return random.choice(options)

    if len(options) > 1 and reverse.get(ghost.direction) in options:
        if random.random() < 0.6:
            options.remove(reverse[ghost.direction])

    return random.choice(options)


def move_ghosts():
    for ghost in ghosts:
        if state.frightened_frames > 0:
            ghost.color("#7d8597")
            ghost.shapesize(0.7, 0.7)
        else:
            ghost.color(ghost.base_color)
            ghost.shapesize(0.9, 0.9)

        if random.random() < 0.4:
            ghost.next_direction = ghost_choose_direction(ghost)
        try_move(ghost)


def check_collisions():
    if state.respawn_invulnerable_frames > 0:
        return

    for i, ghost in enumerate(ghosts):
        if (ghost.grid_x, ghost.grid_y) == (player.grid_x, player.grid_y):
            if state.frightened_frames > 0:
                state.score += 200
                for _ in range(8):
                    create_particle(ghost.grid_x, ghost.grid_y, ghost.base_color)
                spawn = ghost_spawns[i % len(ghost_spawns)]
                ghost.grid_x, ghost.grid_y = spawn
                ghost.sync_to_grid()
                show_message("ALIEN CAUGHT! +200", "#9be564", duration_frames=18)
                update_hud()
            else:
                state.lives -= 1
                update_hud()
                if state.lives <= 0:
                    finish_game(victory=False)
                else:
                    state.respawn_invulnerable_frames = RESPAWN_INVULNERABLE_FRAMES
                    show_message(f"LIVES LEFT: {state.lives}", "#ff6b6b", duration_frames=35)
                    reset_positions()
            return


def next_level():
    state.score += LEVEL_CLEAR_BONUS
    state.level += 1
    show_message(f"LEVEL {state.level}!", "#ffd166", duration_frames=40)

    for ghost in ghosts:
        ghost.hideturtle()
    ghosts.clear()

    build_pellets_for_level()
    update_difficulty()
    spawn_ghosts()
    reset_positions()
    update_hud()


def finish_game(victory):
    state.game_over = True
    state.victory = victory
    message_pen.clear()
    message_pen.goto(0, 30)

    if victory:
        message_pen.color("#9be564")
        message_pen.write("VICTORY!", align="center", font=("Courier", 36, "bold"))
        message_pen.goto(0, -20)
        message_pen.color("#ffd166")
        message_pen.write(f"FINAL SCORE: {state.score}", align="center", font=("Courier", 20, "bold"))
    else:
        message_pen.color("#ff4d6d")
        message_pen.write("GAME OVER", align="center", font=("Courier", 36, "bold"))
        message_pen.goto(0, -20)
        message_pen.color("#ffd166")
        message_pen.write(f"SCORE: {state.score}", align="center", font=("Courier", 20, "bold"))

    message_pen.goto(0, -60)
    message_pen.color("#94d2ff")
    message_pen.write("Press R to restart  |  Press Q to quit", align="center", font=("Courier", 14, "normal"))


message_frames_remaining = 0


def show_message(text, color, duration_frames=24):
    global message_frames_remaining
    message_frames_remaining = duration_frames
    message_pen.clear()
    message_pen.goto(0, -SCREEN_HEIGHT // 2 + 50)
    message_pen.color(color)
    message_pen.write(text, align="center", font=("Courier", 16, "bold"))


def tick_messages():
    global message_frames_remaining
    if message_frames_remaining <= 0:
        return
    message_frames_remaining -= 1
    if message_frames_remaining == 0 and not state.game_over:
        message_pen.clear()


def update_difficulty():
    stage = 1 + (state.eaten_this_level // DIFFICULTY_STEP_PELLETS) + ((state.level - 1) // 2)
    state.difficulty_stage = stage
    state.ghost_interval = max(MIN_GHOST_INTERVAL, GHOST_BASE_INTERVAL - (stage - 1))


def set_direction_up():
    player.next_direction = "up"


def set_direction_down():
    player.next_direction = "down"


def set_direction_left():
    player.next_direction = "left"


def set_direction_right():
    player.next_direction = "right"


def toggle_pause():
    if state.game_over:
        return
    state.paused = not state.paused
    if state.paused:
        pause_pen.goto(0, 0)
        pause_pen.color("#ffd166")
        pause_pen.write("PAUSED", align="center", font=("Courier", 32, "bold"))
        pause_pen.goto(0, -40)
        pause_pen.color("#94d2ff")
        pause_pen.write("Press P to resume", align="center", font=("Courier", 16, "normal"))
    else:
        pause_pen.clear()


def restart_game():
    for ghost in ghosts:
        ghost.hideturtle()
    ghosts.clear()

    for p in particles:
        p.hideturtle()
    particles.clear()

    pause_pen.clear()
    message_pen.clear()
    state.reset_run()
    build_pellets_for_level()
    update_difficulty()
    spawn_ghosts()
    reset_positions()
    update_hud()
    show_message("Arrow keys or WASD to move", "#9ad1ff", duration_frames=60)


def quit_game():
    win.bye()


def setup_controls():
    win.listen()
    win.onkeypress(set_direction_up, "Up")
    win.onkeypress(set_direction_down, "Down")
    win.onkeypress(set_direction_left, "Left")
    win.onkeypress(set_direction_right, "Right")
    win.onkeypress(set_direction_up, "w")
    win.onkeypress(set_direction_down, "s")
    win.onkeypress(set_direction_left, "a")
    win.onkeypress(set_direction_right, "d")
    win.onkeypress(restart_game, "r")
    win.onkeypress(restart_game, "R")
    win.onkeypress(toggle_pause, "p")
    win.onkeypress(toggle_pause, "P")
    win.onkeypress(quit_game, "q")
    win.onkeypress(quit_game, "Q")


def game_loop():
    if state.game_over:
        win.update()
        win.ontimer(game_loop, 16)
        return

    if state.paused:
        win.update()
        win.ontimer(game_loop, 16)
        return

    state.frame += 1

    if state.respawn_invulnerable_frames > 0:
        state.respawn_invulnerable_frames -= 1
        if state.respawn_invulnerable_frames % 8 < 4:
            player.hideturtle()
        else:
            player.showturtle()
    else:
        player.showturtle()

    if state.frightened_frames > 0:
        state.frightened_frames -= 1
        if state.frightened_frames == 0:
            for ghost in ghosts:
                ghost.color(ghost.base_color)
            update_hud()

    if state.frame % PLAYER_BASE_INTERVAL == 0:
        try_move(player)
        consume_pellet_if_any()

        if not pellet_map:
            if state.level >= MAX_LEVEL:
                finish_game(victory=True)
            else:
                next_level()

    if state.frame % state.ghost_interval == 0:
        move_ghosts()

    check_collisions()
    tick_messages()
    update_particles()

    for pellet in pellet_map.values():
        pellet.pulse()

    win.update()
    win.ontimer(game_loop, 16)


def setup_game():
    state.reset_run()
    parse_static_map()
    draw_maze()
    build_pellets_for_level()
    spawn_ghosts()
    reset_positions()
    update_difficulty()
    update_hud()
    setup_controls()
    show_message("Arrow keys or WASD to move  |  P to pause", "#9ad1ff", duration_frames=80)


if __name__ == "__main__":
    setup_game()
    game_loop()
    win.mainloop()

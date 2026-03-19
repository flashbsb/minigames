import random
import turtle

# General configuration
TILE_SIZE = 24
PLAYER_BASE_INTERVAL = 6
GHOST_BASE_INTERVAL = 12
MIN_GHOST_INTERVAL = 4
DIFFICULTY_STEP_PELLETS = 18
MAX_LEVEL = 8
LEVEL_CLEAR_BONUS = 200
RESPAWN_INVULNERABLE_FRAMES = 50
FRIGHTENED_FRAMES_POWER_PELLET = 180

COLOR_BG = "#05060a"
COLOR_WALL = "#1f4ae0"
COLOR_WALL_BORDER = "#6f8fff"
COLOR_PELLET = "#f0f0f0"
COLOR_POWER = "#ffd166"
COLOR_ROBOT = "#25c2f5"
GHOST_COLORS = ["#ff4d4d", "#ff8fab", "#7ae7ff", "#ffa94d", "#9d4edd", "#5ac18e"]

LEVEL_MAP = [
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
]

ROWS = len(LEVEL_MAP)
COLS = len(LEVEL_MAP[0])
SCREEN_WIDTH = COLS * TILE_SIZE + 120
SCREEN_HEIGHT = ROWS * TILE_SIZE + 120

DIRECTIONS = {
    "up": (0, -1),
    "down": (0, 1),
    "left": (-1, 0),
    "right": (1, 0),
    "stop": (0, 0),
}


class GameState:
    def __init__(self):
        self.score = 0
        self.lives = 3
        self.level = 1
        self.game_over = False
        self.victory = False
        self.frame = 0
        self.eaten_this_level = 0
        self.total_pellets = 0
        self.difficulty_stage = 1
        self.ghost_interval = GHOST_BASE_INTERVAL
        self.respawn_invulnerable_frames = 0
        self.frightened_frames = 0

    def reset_run(self):
        self.score = 0
        self.lives = 3
        self.level = 1
        self.game_over = False
        self.victory = False
        self.frame = 0
        self.eaten_this_level = 0
        self.total_pellets = 0
        self.difficulty_stage = 1
        self.ghost_interval = GHOST_BASE_INTERVAL
        self.respawn_invulnerable_frames = 0
        self.frightened_frames = 0


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
        else:
            self.color(COLOR_PELLET)
            self.shapesize(0.24, 0.24)
        self.goto(grid_to_screen(x, y))


state = GameState()

walls = set()
player_spawn = (1, 1)
ghost_spawns = []
pellet_map = {}
ghosts = []


# Screen
win = turtle.Screen()
win.title("PacRobot")
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
hud_pen.color("white")

message_pen = turtle.Turtle()
message_pen.hideturtle()
message_pen.penup()
message_pen.speed(0)


def register_custom_shapes():
    # Robot: compound shape with body, head, and visor.
    robot = turtle.Shape("compound")
    robot.addcomponent(((-12, -10), (12, -10), (12, 6), (-12, 6)), "#25c2f5", "#0b132b")
    robot.addcomponent(((-9, 6), (9, 6), (9, 14), (-9, 14)), "#5fe1ff", "#0b132b")
    robot.addcomponent(((-5, 10), (5, 10), (5, 12), (-5, 12)), "#111827", "#111827")
    robot.addcomponent(((-1, 14), (1, 14), (1, 20), (-1, 20)), "#94d2ff", "#0b132b")
    robot.addcomponent(((-3, 20), (3, 20), (3, 22), (-3, 22)), "#94d2ff", "#0b132b")
    win.register_shape("robot_unit", robot)

    # Alien: simplified polygon that supports dynamic color changes.
    alien = (
        (-12, -8),
        (-9, -14),
        (-5, -12),
        (-3, -16),
        (0, -12),
        (3, -16),
        (5, -12),
        (9, -14),
        (12, -8),
        (9, 1),
        (6, 7),
        (3, 12),
        (0, 14),
        (-3, 12),
        (-6, 7),
        (-9, 1),
    )
    win.register_shape("alien_unit", alien)


register_custom_shapes()
player = Actor("robot_unit", COLOR_ROBOT, 1.0)


def grid_to_screen(x, y):
    left = -(COLS * TILE_SIZE) / 2 + TILE_SIZE / 2
    top = (ROWS * TILE_SIZE) / 2 - TILE_SIZE / 2
    return left + x * TILE_SIZE, top - y * TILE_SIZE


def parse_static_map():
    global player_spawn
    expected_cols = len(LEVEL_MAP[0])
    for row in LEVEL_MAP:
        if len(row) != expected_cols:
            raise ValueError("LEVEL_MAP has rows with different lengths.")

    walls.clear()
    ghost_spawns.clear()

    for y, row in enumerate(LEVEL_MAP):
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
    stage = state.difficulty_stage
    hud_pen.goto(0, SCREEN_HEIGHT // 2 - 52)
    frightened_label = "ON" if state.frightened_frames > 0 else "OFF"
    hud_pen.write(
        f"Score: {state.score}    Lives: {state.lives}    Level: {state.level}    Difficulty: {stage}    Fright: {frightened_label}",
        align="center",
        font=("Courier", 14, "bold"),
    )


def can_move(x, y):
    return 0 <= x < COLS and 0 <= y < ROWS and (x, y) not in walls


def try_move(actor):
    # Allows turning as soon as the desired direction is open.
    nx, ny = DIRECTIONS[actor.next_direction]
    tx, ty = actor.grid_x + nx, actor.grid_y + ny
    if actor.next_direction != "stop" and can_move(tx, ty):
        actor.direction = actor.next_direction

    dx, dy = DIRECTIONS[actor.direction]
    nx, ny = actor.grid_x + dx, actor.grid_y + dy
    if actor.direction != "stop" and can_move(nx, ny):
        actor.grid_x, actor.grid_y = nx, ny
        actor.sync_to_grid()


def desired_ghost_count():
    # Progressive scaling based on level and difficulty stage.
    return min(2 + ((state.level - 1) // 2) + (state.difficulty_stage // 2), len(GHOST_COLORS))


def update_difficulty():
    stage = 1 + (state.eaten_this_level // DIFFICULTY_STEP_PELLETS) + ((state.level - 1) // 2)
    state.difficulty_stage = stage
    state.ghost_interval = max(MIN_GHOST_INTERVAL, GHOST_BASE_INTERVAL - (stage - 1))


def spawn_ghosts():
    target = desired_ghost_count()

    while len(ghosts) < target:
        spawn = ghost_spawns[len(ghosts) % len(ghost_spawns)]
        color = GHOST_COLORS[len(ghosts) % len(GHOST_COLORS)]
        ghost = Actor("alien_unit", color, 1.0)
        ghost.grid_x, ghost.grid_y = spawn
        ghost.direction = random.choice(["up", "down", "left", "right"])
        ghost.next_direction = ghost.direction
        ghost.sync_to_grid()
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


def consume_pellet_if_any():
    key = (player.grid_x, player.grid_y)
    pellet = pellet_map.pop(key, None)
    if pellet is None:
        return

    pellet.hideturtle()
    gain = 50 if pellet.power else 10
    state.score += gain
    state.eaten_this_level += 1
    if pellet.power:
        state.frightened_frames = FRIGHTENED_FRAMES_POWER_PELLET
        show_message("Fright mode enabled!", "#ffee93", duration_frames=28)

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

    # Chance to chase the player rises with difficulty.
    chase_chance = min(0.18 + 0.07 * (state.difficulty_stage - 1), 0.7)
    if state.frightened_frames > 0:
        chase_chance = 0.02
    if random.random() < chase_chance:
        best = options[0]
        best_dist = 99999
        for dname in options:
            dx, dy = DIRECTIONS[dname]
            nx, ny = ghost.grid_x + dx, ghost.grid_y + dy
            dist = abs(player.grid_x - nx) + abs(player.grid_y - ny)
            if dist < best_dist:
                best_dist = dist
                best = dname
        return best

    # Reduces frequent immediate backtracking.
    reverse = {
        "up": "down",
        "down": "up",
        "left": "right",
        "right": "left",
        "stop": "stop",
    }
    if len(options) > 1 and reverse.get(ghost.direction) in options:
        if random.random() < 0.65:
            options.remove(reverse[ghost.direction])

    return random.choice(options)


def move_ghosts():
    for ghost in ghosts:
        if state.frightened_frames > 0:
            ghost.color("#7d8597")
        else:
            ghost.color(ghost.base_color)
        if random.random() < 0.33:
            ghost.next_direction = ghost_choose_direction(ghost)
        try_move(ghost)


def check_collisions():
    if state.respawn_invulnerable_frames > 0:
        return

    for i, ghost in enumerate(ghosts):
        if (ghost.grid_x, ghost.grid_y) == (player.grid_x, player.grid_y):
            if state.frightened_frames > 0:
                state.score += 120
                spawn = ghost_spawns[i % len(ghost_spawns)]
                ghost.grid_x, ghost.grid_y = spawn
                ghost.sync_to_grid()
                show_message("+120 alien!", "#9be564", duration_frames=22)
                update_hud()
            else:
                state.lives -= 1
                update_hud()
                if state.lives <= 0:
                    finish_game(victory=False)
                else:
                    state.respawn_invulnerable_frames = RESPAWN_INVULNERABLE_FRAMES
                    show_message("You lost a life!", "#ff6b6b", duration_frames=32)
                    reset_positions()
            return


def next_level():
    state.score += LEVEL_CLEAR_BONUS
    state.level += 1
    show_message(f"Level {state.level}!", "#ffd166", duration_frames=36)
    build_pellets_for_level()
    update_difficulty()
    spawn_ghosts()
    reset_positions()
    update_hud()


def finish_game(victory):
    state.game_over = True
    state.victory = victory
    message_pen.clear()
    message_pen.goto(0, 0)
    if victory:
        message_pen.color("#9be564")
        message_pen.write("You Win!", align="center", font=("Courier", 30, "bold"))
    else:
        message_pen.color("#ff4d6d")
        message_pen.write("Game Over", align="center", font=("Courier", 30, "bold"))
    show_message("Press R to restart", "#d9ed92", duration_frames=999999)


message_frames_remaining = 0


def show_message(text, color, duration_frames=24):
    global message_frames_remaining
    message_frames_remaining = duration_frames
    message_pen.clear()
    message_pen.goto(0, -SCREEN_HEIGHT // 2 + 30)
    message_pen.color(color)
    message_pen.write(text, align="center", font=("Courier", 15, "bold"))


def tick_messages():
    global message_frames_remaining
    if message_frames_remaining <= 0:
        return
    message_frames_remaining -= 1
    if message_frames_remaining == 0 and not state.game_over:
        message_pen.clear()


def set_direction_up():
    player.next_direction = "up"


def set_direction_down():
    player.next_direction = "down"


def set_direction_left():
    player.next_direction = "left"


def set_direction_right():
    player.next_direction = "right"


def restart_game():
    for ghost in ghosts:
        ghost.hideturtle()
    ghosts.clear()
    message_pen.clear()
    state.reset_run()
    build_pellets_for_level()
    update_difficulty()
    spawn_ghosts()
    reset_positions()
    update_hud()
    show_message("New game started!", "#9ad1ff", duration_frames=40)


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


def game_loop():
    if state.game_over:
        win.update()
        win.ontimer(game_loop, 16)
        return

    state.frame += 1
    if state.respawn_invulnerable_frames > 0:
        state.respawn_invulnerable_frames -= 1
        if state.respawn_invulnerable_frames % 6 < 3:
            player.hideturtle()
        else:
            player.showturtle()
    else:
        player.showturtle()

    if state.frightened_frames > 0:
        state.frightened_frames -= 1
        if state.frightened_frames == 0:
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
    show_message("Arrow keys or WASD to move", "#9ad1ff", duration_frames=60)


if __name__ == "__main__":
    setup_game()
    game_loop()
    win.mainloop()

import math
import random
import shelve

import pygame
# To run a game execute:
#    pgzrun space_survivor.py


# CONFIGURATION

DEFAULT_NAME = "New Player"
PLAYER_NAME = DEFAULT_NAME
PLAYER_SCORE = 0

GAME_STAGE = "start"
ASTEROIDS = []
BULLETS = []
BONUS = None
BONUS_PERIODS = [15, 20]

# Screen settings
WIDTH = 800
HEIGHT = 600
BACKGROUND = pygame.transform.scale(images.background, (WIDTH, HEIGHT))

SOUND_VOLUME = 0.05

# Difficulty level
GAME_TIME_BASIC = 60
GAME_TIME = GAME_TIME_BASIC
DIFFICULTY = 2

# Spaceship settings
SPACESHIP_SPEED = 0.3
SPACESHIP_MAX_SPEED = 3
SPACESHIP_SLOWING_DOWN_SPEED = 0.1
SPACESHIP_TURNING_SPEED = 2

# Large asteroid settings
LRG_ASTEROID_STARTING_QNT = 5
LRG_ASTEROID_MIN_SPEED = 1
LRG_ASTEROID_MAX_SPEED = 2

SML_ASTEROID_STARTING_QNT = 3
SML_ASTEROID_MIN_SPEED = 2
SML_ASTEROID_MAX_SPEED = 3

MIN_SML_SPAWN_AFTER_DES = 1
MAX_SML_SPAWN_AFTER_DES = 4

# Bullet settings
BULLET_SPEED = 4

# New game screen UI
NEW_GAME_BTN = Actor('button', center=(WIDTH // 2, HEIGHT // 4 + 100))
SCORE_BTN = Actor('button', center=(WIDTH // 2, HEIGHT // 4 + 180))

# Difficulty selection screen UI
EASY_BTN = Actor('button', center=(WIDTH // 2, HEIGHT // 4 + 100))
NORMAL_BTN = Actor('button_pressed', center=(WIDTH // 2, HEIGHT // 4 + 180))
HARD_BTN = Actor('button', center=(WIDTH // 2, HEIGHT // 4 + 260))
APPLY_BTN = Actor('button', center=(WIDTH // 2, HEIGHT - 100))

# End game screen UI
RESTART_YES_BTN = Actor('button', midright=(WIDTH // 2 - 10, HEIGHT // 1.5))
RESTART_NO_BTN = Actor('button', midleft=(WIDTH // 2 + 10, HEIGHT // 1.5))

SCORE_BACK_BTN = Actor('button', midbottom=(WIDTH // 2, HEIGHT - 50))

PLAYER_NAME_INPUT_BOX = Rect((WIDTH // 2 - 150, HEIGHT // 4 + 50), (300, 50))
PLAYER_NAME_BTN = Actor('pname_button', midbottom=(WIDTH // 2, HEIGHT - 50))
CLEAR_INPUT_BTN = Actor('button', center=(WIDTH // 2, HEIGHT // 4 + 180))
SAVE_NEW_NAME_BTN = Actor('button', center=(WIDTH // 2, HEIGHT // 4 + 260))


# Spaceship's functions
def spaceship_create():
    spaceship = Actor('spaceship', (WIDTH / 2, HEIGHT / 2))
    spaceship.x_direction = 0
    spaceship.y_direction = 0
    spaceship.speed = 0
    spaceship.mask = pygame.mask.from_surface(images.spaceship)

    return spaceship


def spaceship_turn_right(space_ship):
    space_ship.angle -= SPACESHIP_TURNING_SPEED


def spaceship_turn_left(space_ship):
    space_ship.angle += SPACESHIP_TURNING_SPEED


def spaceship_boost(space_ship):
    if space_ship.speed <= SPACESHIP_MAX_SPEED:
        space_ship.speed += SPACESHIP_SPEED


def spaceship_slow_down(space_ship):
    space_ship.speed -= SPACESHIP_SLOWING_DOWN_SPEED


def spaceship_fire(space_ship):
    bullet = Actor('bullet', (space_ship.x, space_ship.y))
    bullet.x_direction, bullet.y_direction = calculate_actor_direction(
        space_ship)
    bullet.speed = BULLET_SPEED
    BULLETS.append(bullet)
    sounds.shoot.play().set_volume(SOUND_VOLUME)


# Asteroid's functions
def asteroid_create(asteroid_kind):
    """Asteroids will randomly spawn in one of the corner of the screen
    """
    x = random.choice([0, WIDTH])
    y = random.choice([0, HEIGHT])

    asteroid = None
    if asteroid_kind == 'small':
        asteroid = Actor('smallmeteorite', (x, y))
        asteroid.kind = 'small'
        asteroid.score_points = 1
        asteroid.speed = random.uniform(SML_ASTEROID_MIN_SPEED,
                                        SML_ASTEROID_MAX_SPEED)
    elif asteroid_kind == 'large':
        asteroid = Actor('largemeteorite', (x, y))
        asteroid.kind = 'large'
        asteroid.score_points = 3
        asteroid.speed = random.uniform(LRG_ASTEROID_MIN_SPEED,
                                        LRG_ASTEROID_MAX_SPEED)
    asteroid.x_direction = random.uniform(-1, 1)
    asteroid.y_direction = random.uniform(-1, 1)

    ASTEROIDS.append(asteroid)


def asteroid_destroy(asteroid):
    global PLAYER_SCORE
    if asteroid.kind == 'small':
        asteroid_create('small')
    elif asteroid.kind == 'large':
        asteroid_create('large')

    ASTEROIDS.remove(asteroid)
    PLAYER_SCORE += asteroid.score_points


def spawn_asteroids():
    for i in range(LRG_ASTEROID_STARTING_QNT):
        asteroid_create('large')

    for i in range(SML_ASTEROID_STARTING_QNT):
        asteroid_create('small')


# HELPER METHODS
def update_actor_position(actor):
    actor.x -= actor.x_direction * actor.speed
    actor.y -= actor.y_direction * actor.speed


def calculate_actor_direction(actor):
    x = math.sin(math.radians(actor.angle))
    y = math.cos(math.radians(actor.angle))
    return x, y


def remove_actors(actor_list):
    if not actor_list:
        return

    actor_list.clear()


def loop_actor_in_frame(actor):
    if actor.left > WIDTH:
        actor.right = 0

    if actor.right < 0:
        actor.left = WIDTH

    if actor.top > HEIGHT:
        actor.bottom = 0

    if actor.bottom < 0:
        actor.top = HEIGHT


def remove_actor_out_frame(actor):
    if (actor.left > WIDTH or actor.right < 0
            or actor.top > HEIGHT or actor.bottom < 0):
        if actor in BULLETS:
            BULLETS.remove(actor)


def set_player_name(name):
    global PLAYER_NAME
    PLAYER_NAME = name


def reset_player_score():
    global PLAYER_SCORE
    PLAYER_SCORE = 0


def schedule_bonus():
    clock.schedule_unique(set_bonus, random.randint(*BONUS_PERIODS))


def set_bonus():
    global BONUS

    BONUS = Actor('star')
    BONUS.x = random.randint(0, WIDTH)
    BONUS.y = random.randint(0, HEIGHT)


def game_start(lives=None, game_stage=None, hard_start=True):
    global GAME_STAGE
    global ASTEROIDS
    global BULLETS
    global SPACESHIP
    global GAME_TIME
    global PLAYER_SCORE
    global LIVES
    global BONUS

    if hard_start:
        set_player_name(PLAYER_NAME)
        reset_player_score()
        PLAYER_SCORE = 0
        GAME_TIME = GAME_TIME_BASIC

    SPACESHIP = spaceship_create()

    if lives:
        LIVES = lives
    else:
        LIVES = 3

    if game_stage:
        GAME_STAGE = game_stage
    else:
        GAME_STAGE = "running"

    remove_actors(ASTEROIDS)
    remove_actors(BULLETS)

    spawn_asteroids()

    schedule_bonus()


# PLAYING MUSIC
def play_start_end_game_music():
    music.stop()
    music.play('start_end')
    music.set_volume(SOUND_VOLUME)


def play_running_game_music():
    music.stop()
    music.play('play_music')
    music.set_volume(SOUND_VOLUME)


def get_rank():
    data = shelve.open('rank.db')
    rank = data.get('rank')
    data.close()

    return rank


def add_rank(player_name, player_score):
    data = shelve.open('rank.db')

    rank = data.get('rank')
    if not rank:
        rank = []

    if DIFFICULTY == 1:
        difficulty = 'EASY'
    elif DIFFICULTY == 2:
        difficulty = 'NORMAL'
    else:
        difficulty = 'HARD'

    rank.append(
        {
            "player_name": player_name,
            "player_score": player_score,
            "difficulty": difficulty
        }
    )
    rank = sorted(rank, key=lambda i: i['player_score'], reverse=True)

    if len(rank) > 5:
        rank.pop()

    data['rank'] = rank
    data.close()


# DRAWING GAME
def start_game_screen():
    screen.clear()

    NEW_GAME_BTN.draw()
    screen.draw.text("New game", center=NEW_GAME_BTN.center, fontsize=48)

    SCORE_BTN.draw()
    screen.draw.text("Scores", center=SCORE_BTN.center, fontsize=48)

    PLAYER_NAME_BTN.draw()
    screen.draw.text("Rename player", center=PLAYER_NAME_BTN.center, fontsize=48)


def difficulty_screen():
    screen.clear()
    screen.fill((10, 8, 26))
    screen.draw.text(
        f"Choose game difficulty", midtop=(WIDTH//2, HEIGHT//5),
        fontsize=72, color=(50, 242, 50)
    )

    EASY_BTN.draw()
    # the easiest way to move button caption with pressed button
    screen.draw.text(
        "Easy", midtop=(EASY_BTN.midtop[0], EASY_BTN.midtop[1] + 7),
        fontsize=48
    )

    NORMAL_BTN.draw()
    screen.draw.text(
        "Normal", midtop=(NORMAL_BTN.midtop[0], NORMAL_BTN.midtop[1]+7),
        fontsize=48
    )

    HARD_BTN.draw()
    screen.draw.text(
        "Hard", midtop=(HARD_BTN.midtop[0], HARD_BTN.midtop[1] + 7),
        fontsize=48
    )

    APPLY_BTN.draw()
    screen.draw.text("Apply", center=APPLY_BTN.center, fontsize=30)

    play_start_end_game_music()


NAME_INPUT_ACTIVE = False


def change_player_name_screen():
    global PLAYER_NAME
    global NAME_INPUT_ACTIVE

    screen.clear()
    screen.fill((10, 8, 26))
    screen.draw.text(
        f"Enter new name", midtop=(WIDTH//2, HEIGHT//5),
        fontsize=72, color=(50, 242, 50)
    )

    if NAME_INPUT_ACTIVE:
        screen.draw.rect(PLAYER_NAME_INPUT_BOX, (50, 242, 50))
    else:
        screen.draw.rect(PLAYER_NAME_INPUT_BOX, (150, 142, 150))

    screen.draw.text(
        f"{PLAYER_NAME}", midtop=(PLAYER_NAME_INPUT_BOX.midtop[0], PLAYER_NAME_INPUT_BOX.midtop[1] + 7),
        fontsize=48
    )

    CLEAR_INPUT_BTN.draw()
    screen.draw.text(
        "Clear", midtop=(CLEAR_INPUT_BTN.midtop[0], CLEAR_INPUT_BTN.midtop[1] + 7),
        fontsize=48
    )

    SAVE_NEW_NAME_BTN.draw()
    screen.draw.text("Apply", center=SAVE_NEW_NAME_BTN.center, fontsize=30)


def end_game_screen():
    screen.clear()
    screen.draw.text(
        f"Game oveR", midtop=(WIDTH//2, HEIGHT//5),
        fontsize=72, color=(50, 242, 50)
    )
    screen.draw.text(
        f"Score: {PLAYER_SCORE}", midtop=(WIDTH//2, HEIGHT//3),
        fontsize=56, color=(50, 242, 50)
    )
    screen.draw.text(
        f"One more try ?", midtop=(WIDTH//2, HEIGHT//2),
        fontsize=56, color=(50, 242, 50)
    )

    RESTART_YES_BTN.draw()
    RESTART_NO_BTN.draw()
    screen.draw.text("YES", center=RESTART_YES_BTN.center, fontsize=48)
    screen.draw.text("NO", center=RESTART_NO_BTN.center, fontsize=48)

    play_start_end_game_music()


def play_game_screen():
    screen.clear()
    screen.blit(BACKGROUND, (0, 0))

    SPACESHIP.draw()

    if BONUS:
        BONUS.draw()

    # Draw asteroids
    for m in ASTEROIDS:
        m.draw()

    # Draw bullets
    for s in BULLETS:
        s.draw()

    play_running_game_music()


def scores_screen():
    screen.clear()
    screen.draw.text(
        f"LAST RUNS:", midtop=(WIDTH // 2, HEIGHT // 6),
        fontsize=48, color=(50, 242, 50)
    )
    screen.draw.text(
        f"NAME : SCORE : DIFFICULTY", midtop=(WIDTH // 2, HEIGHT // 4),
        fontsize=36, color=(50, 242, 50)
    )

    scores = get_rank()
    if scores != None:
        start_height = HEIGHT // 4
        for record in scores:
            start_height += 40
            screen.draw.text(
                f"{record.get('player_name')} : {record.get('player_score')} : {record.get('difficulty', 332)}", midtop=(WIDTH // 2, start_height),
                fontsize=32, color=(50, 242, 50)
            )

    SCORE_BACK_BTN.draw()
    screen.draw.text("Back", center=SCORE_BACK_BTN.center, fontsize=48)


def draw():
    # global SPACESHIP
    if GAME_STAGE == "difficulty":
        difficulty_screen()
    elif GAME_STAGE == "start":
        start_game_screen()
    elif GAME_STAGE == "running":
        play_game_screen()
        update_hud()
    elif GAME_STAGE == "end":
        end_game_screen()
    elif GAME_STAGE == "scores":
        scores_screen()
    elif GAME_STAGE == "rename_player":
        change_player_name_screen()


# Draw countdown timer and score
def update_hud():
    screen.draw.text(
        f"Time left: {GAME_TIME:.0f} s", topright=(WIDTH-10, 10),
        fontsize=42, color=(50, 242, 50)
    )
    screen.draw.text(
        f"Score: {PLAYER_SCORE}", midtop=(WIDTH//2, 10),
        fontsize=56, color=(50, 242, 50)
    )

    w = 10
    for i in range(LIVES):
        w += 50
        live = Actor('heart', (w, 30))
        live.draw()


# UPDATING GAME
def update(dt):
    global GAME_STAGE
    global GAME_TIME
    global PLAYER_SCORE
    global ASTEROIDS
    global LIVES
    global BONUS

    if GAME_STAGE == 'running':
        # Update spaceship
        if keyboard.up:
            spaceship_boost(SPACESHIP)
        else:
            spaceship_slow_down(SPACESHIP)
        if keyboard.right:
            spaceship_turn_right(SPACESHIP)
        if keyboard.left:
            spaceship_turn_left(SPACESHIP)

        # Move spaceship
        if SPACESHIP.speed > 0:
            SPACESHIP.x_direction, SPACESHIP.y_direction =\
                calculate_actor_direction(SPACESHIP)
            update_actor_position(SPACESHIP)
        else:
            SPACESHIP.speed = 0

        loop_actor_in_frame(SPACESHIP)

        # Bonus collision
        if BONUS and SPACESHIP.colliderect(BONUS):
            BONUS = None
            if LIVES < 5:
                LIVES += 1
            else:
                PLAYER_SCORE += 10
            schedule_bonus()

        # Collisions
        if SPACESHIP.collidelist(ASTEROIDS) >= 0:
            sounds.explosion.play()

            LIVES -= 1
            if LIVES <= 0:
                GAME_STAGE = "end"
                add_rank(PLAYER_NAME, PLAYER_SCORE)
            else:
                game_start(lives=LIVES, game_stage="running", hard_start=False)

        for bullet in BULLETS[::]:
            collided_asteroid_index = bullet.collidelist(ASTEROIDS)
            if collided_asteroid_index >= 0:
                asteroid_destroy(ASTEROIDS[collided_asteroid_index])
                BULLETS.remove(bullet)

        # Update asteroids
        for m in ASTEROIDS:
            update_actor_position(m)
            loop_actor_in_frame(m)

        # Update bullets
        for b in BULLETS:
            update_actor_position(b)
            remove_actor_out_frame(b)

        # update_hud()
        GAME_TIME -= dt
        if GAME_TIME < 0:
            GAME_STAGE = "end"
            PLAYER_SCORE += LIVES*3
            add_rank(PLAYER_NAME, PLAYER_SCORE)


# HOOKS
def on_key_down(key, unicode):
    global GAME_STAGE
    global PLAYER_NAME

    if GAME_STAGE == "running" and key == keys.SPACE:
        spaceship_fire(SPACESHIP)

    if key == keys.ESCAPE:
        quit(0)

    if GAME_STAGE == 'rename_player':
        if NAME_INPUT_ACTIVE:
            if key == keys.BACKSPACE:
                PLAYER_NAME = PLAYER_NAME[:-1]
            else:
                PLAYER_NAME += unicode


def set_difficulty(level):
    global BONUS_PERIODS
    global DIFFICULTY
    global LRG_ASTEROID_MIN_SPEED
    global LRG_ASTEROID_MAX_SPEED
    global SML_ASTEROID_MIN_SPEED
    global SML_ASTEROID_MAX_SPEED

    if level == 'easy':
        EASY_BTN.image = 'button_pressed'
        NORMAL_BTN.image = 'button'
        HARD_BTN.image = 'button'
        BONUS_PERIODS = [5, 10]
        DIFFICULTY = 1
        LRG_ASTEROID_MIN_SPEED = 0.5
        LRG_ASTEROID_MAX_SPEED = 1.5
        SML_ASTEROID_MIN_SPEED = 1.5
        SML_ASTEROID_MAX_SPEED = 2.5
    elif level == 'normal':
        EASY_BTN.image = 'button'
        NORMAL_BTN.image = 'button_pressed'
        HARD_BTN.image = 'button'
        BONUS_PERIODS = [15, 20]
        DIFFICULTY = 2
        LRG_ASTEROID_MIN_SPEED = 1
        LRG_ASTEROID_MAX_SPEED = 2
        SML_ASTEROID_MIN_SPEED = 2
        SML_ASTEROID_MAX_SPEED = 3
    elif level == 'hard':
        EASY_BTN.image = 'button'
        NORMAL_BTN.image = 'button'
        HARD_BTN.image = 'button_pressed'
        BONUS_PERIODS = [25, 30]
        DIFFICULTY = 3
        LRG_ASTEROID_MIN_SPEED = 2
        LRG_ASTEROID_MAX_SPEED = 3
        SML_ASTEROID_MIN_SPEED = 4
        SML_ASTEROID_MAX_SPEED = 5

    clock.unschedule(set_bonus)
    clock.schedule_unique(set_bonus, random.randint(*BONUS_PERIODS))


def on_mouse_down(pos, button):
    global GAME_STAGE
    global NAME_INPUT_ACTIVE
    global PLAYER_NAME

    if GAME_STAGE == 'difficulty' and button == mouse.LEFT:
        if EASY_BTN.collidepoint(pos):
            set_difficulty('easy')
        if NORMAL_BTN.collidepoint(pos):
            set_difficulty('normal')
        if HARD_BTN.collidepoint(pos):
            set_difficulty('hard')
        if APPLY_BTN.collidepoint(pos):
            game_start()
    if GAME_STAGE == 'end' and button == mouse.LEFT:
        if RESTART_YES_BTN.collidepoint(pos):
            game_start()
        if RESTART_NO_BTN.collidepoint(pos):
            GAME_STAGE = 'start'
    if GAME_STAGE == 'start' and button == mouse.LEFT:
        if NEW_GAME_BTN.collidepoint(pos):
            GAME_STAGE = 'difficulty'
        if SCORE_BTN.collidepoint(pos):
            GAME_STAGE = 'scores'
        if PLAYER_NAME_BTN.collidepoint(pos):
            GAME_STAGE = 'rename_player'
    if GAME_STAGE == 'scores' and button == mouse.LEFT:
        if SCORE_BACK_BTN.collidepoint(pos):
            GAME_STAGE = 'start'
    if GAME_STAGE == 'rename_player' and button == mouse.LEFT:
        if PLAYER_NAME_INPUT_BOX.collidepoint(pos):
            NAME_INPUT_ACTIVE = True
        else:
            NAME_INPUT_ACTIVE = False
        if CLEAR_INPUT_BTN.collidepoint(pos):
            PLAYER_NAME = ''
        if SAVE_NEW_NAME_BTN.collidepoint(pos):
            GAME_STAGE = 'start'

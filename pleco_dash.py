# Pleco Dash - Casio fx-CG50 edition
#
# You play as a plecostomus hypostomus (a "pleco") - the algae-eating
# catfish people keep in aquariums. Cruise the tank grabbing algae to
# grow longer, while dodging debris that drifts down from the filter
# above you. Touch the debris, or run into your own tail, and it's
# game over.
#
# Mechanics: the "grow by eating" idea from snake.py, combined with
# the "falling obstacles" idea from dodge_collect_casio.py.
#
# Written for the calculator's built-in MicroPython, which does NOT
# have an "os" module (no real screen clear) or a way to read single
# keypresses - so, same as the other two games, this stays fully
# turn-based: type a move, press EXE, repeat.
#
# Controls (type the character, then press EXE/Enter):
#   8 / w = up
#   2 / s = down
#   4 / a = left
#   6 / d = right
#   .     = quit

import random

empty = "-"
body_segment = "o"
direction_characters = ["^", "v", "<", ">"]  # up, down, left, right - the head
algae_char = "$"
debris_char = "#"

# Small grid so a full frame fits on the calculator's console.
horizontal = 10
vertical = 6

positions_x = [horizontal // 2]
positions_y = [vertical // 2]
direction = 1  # start facing down

algae_position = [0, 0]
debris = []  # each entry is [x, y]

grow_next_turn = False
game_is_running = True
frame = 0


def clear_screen():
    # No os.system() available, so just push the old frame off screen.
    print("\n" * 6)


def is_on_fish(x, y):
    for i in range(len(positions_x)):
        if positions_x[i] == x and positions_y[i] == y:
            return True
    return False


def is_on_debris(x, y):
    for item in debris:
        if item[0] == x and item[1] == y:
            return True
    return False


def spawn_algae():
    # Picks a new algae tile, avoiding the fish and any debris.
    while True:
        x = random.randint(0, horizontal - 1)
        y = random.randint(0, vertical - 1)

        if is_on_fish(x, y):
            continue
        if is_on_debris(x, y):
            continue

        algae_position[0] = x
        algae_position[1] = y
        return


def spawn_debris():
    # Debris starts one row above the visible tank (y = -1) so you
    # get one turn's warning before it actually drifts into play.
    x = random.randint(0, horizontal - 1)
    debris.append([x, -1])


def move_debris():
    for item in debris:
        item[1] += 1

    # Drop anything that has drifted past the bottom of the tank.
    kept = []
    for item in debris:
        if item[1] < vertical:
            kept.append(item)

    while debris:
        debris.pop()

    for item in kept:
        debris.append(item)


def check_algae():
    global grow_next_turn

    if positions_x[0] == algae_position[0] and positions_y[0] == algae_position[1]:
        grow_next_turn = True
        spawn_algae()


def has_crashed():
    # Any part of the fish touching debris ends the game.
    for i in range(len(positions_x)):
        if is_on_debris(positions_x[i], positions_y[i]):
            return True

    # So does running the head into your own tail.
    for i in range(1, len(positions_x)):
        if positions_x[i] == positions_x[0] and positions_y[i] == positions_y[0]:
            return True

    return False


def print_frame():
    clear_screen()

    print("PLECO DASH")
    print("Algae eaten: " + str(len(positions_x) - 1))
    print("8/w 2/s 4/a 6/d . quit")
    print("+" + "-" * horizontal + "+")

    for y in range(vertical):
        line = "|"

        for x in range(horizontal):
            if x == positions_x[0] and y == positions_y[0]:
                line += direction_characters[direction]
            elif is_on_fish(x, y):
                line += body_segment
            elif is_on_debris(x, y):
                line += debris_char
            elif x == algae_position[0] and y == algae_position[1]:
                line += algae_char
            else:
                line += empty

        line += "|"
        print(line)

    print("+" + "-" * horizontal + "+")


def display_end_screen(message):
    clear_screen()
    print("------------------------")
    print(message)
    print("Algae eaten: " + str(len(positions_x) - 1))
    print("------------------------")


def play_game():
    global direction
    global grow_next_turn
    global game_is_running
    global frame

    spawn_algae()
    print_frame()

    while game_is_running:
        # Type one movement command and press EXE.
        user_input = input("> ").strip().lower()

        if user_input == ".":
            display_end_screen("GAME FINISHED")
            return

        new_x = positions_x[0]
        new_y = positions_y[0]

        if user_input in ("8", "w"):
            new_y -= 1
            direction = 0
        elif user_input in ("2", "s"):
            new_y += 1
            direction = 1
        elif user_input in ("4", "a"):
            new_x -= 1
            direction = 2
        elif user_input in ("6", "d"):
            new_x += 1
            direction = 3
        else:
            print_frame()
            continue

        # The tank has glass walls, not open water - swimming into
        # the edge just stops you there instead of wrapping around.
        new_x = max(0, min(horizontal - 1, new_x))
        new_y = max(0, min(vertical - 1, new_y))

        if grow_next_turn:
            grow_next_turn = False
            positions_x.insert(0, new_x)
            positions_y.insert(0, new_y)
        else:
            for i in range(len(positions_x) - 1):
                positions_x[len(positions_x) - (1 + i)] = positions_x[len(positions_x) - (2 + i)]
                positions_y[len(positions_y) - (1 + i)] = positions_y[len(positions_y) - (2 + i)]
            positions_x[0] = new_x
            positions_y[0] = new_y

        check_algae()

        # Every couple of turns, more debris drifts down from the filter.
        frame += 1
        if frame % 2 == 0:
            spawn_debris()

        move_debris()

        if has_crashed():
            display_end_screen("GAME OVER")
            return

        print_frame()


play_game()

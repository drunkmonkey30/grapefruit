import sys
sys.path.append('../bt/')
sys.path.append('../board_hardware/')
sys.path.append('../pathing/')
sys.path.append('../game/')

import random
import time
import colorsys

from server import *
from game_board import *
from mainPath import *
from player import *


# main file for gameboard
# this will initialize bluetooth, connect to database, do whatever needs to be done when the game starts up
def gameboard_main():
    print("gameboard_main entry")

    print("\nstarting bluetooth server")
    bluetooth_server = BlueServer()
    connected = bluetooth_server.start_server()

    game_board = GameBoard(4)

    # didn't want to comment all of this out
    if False:
        for i in range(16):
            a1 = Animation(RGB_start=(0, 0, 0), RGB_end=(128, 0, 0), duration=2.0)
            a2 = Animation(RGB_start=(0, 0, 0), RGB_end=(0, 128, 0), duration=2.0)
            a3 = Animation(RGB_start=(0, 0, 0), RGB_end=(0, 0, 128), duration=2.0)
            ac = AnimationChain([a1, a2, a3], 0)

            game_board.set_tile_led_animation(i, LED_NORTH, ac)
            game_board.set_tile_led_animation(i, LED_SOUTH, ac)
            game_board.set_tile_led_animation(i, LED_EAST, ac)
            game_board.set_tile_led_animation(i, LED_WEST, ac)


    players = []
    players.append(Player("One", 0, 0))
    players.append(Player("Two", 0, 0))
    players.append(Player("Three", 0, 0))
    players.append(Player("Four", 0, 0))
    total_players = 0

    playing = True
    demo = False
    try:
        while playing:
            # reset game board
            game_board.turn_off_all_leds()

            if not demo:
                answer = str(input("Demo Mode? (y/n)"))
                if answer is not None and 'y' in answer:
                    demo = True
                    try:
                        while demo:
                            print("\n*** demo mode")
                            do_demo_mode(game_board)
                    except:
                        print("\n *** exiting demo mode")
                        demo = False
                        continue

            while total_players < 1 or total_players > 4:
                total_players = int(input("Please enter the number of players from 1 to 4: "))

            # generate the path and print it out
            path_length = random.randint(0, 5) + 8
            ghoul_density = random.random()
            path = generate_path(path_length, ghoul_density)
            print("\nNew path generated")
            print("path length   = " + str(len(path)))
            print("ghoul density = " + str(ghoul_density))

            # print out the path to the console
            for x in path:
                print(str(x.place), end="")
                if (x.ghoul):
                    print("!", end="")

                if x.next is not None:
                    print(" -> ", end="")
            print("\n")

            # circle the starting tile with green lights
            for i in range(4):
                up = Animation(RGB_start=(0, 0, 0), RGB_end=(0, 64, 0), duration = 0.75)
                dn = Animation(RGB_start=(0, 64, 0), RGB_end=(0, 0, 0), duration = 0.75)
                chain = AnimationChain([up, dn], 0)
                game_board.set_tile_led_animation(path[0].place, i, chain)
                time.sleep(0.2)

            # set starting position for all players
            for p in players:
                p.set_position(path[0].place)
                p.clear_question_totals()
                p.clear_furthest_path()

            game_on = True

            # turn counter is incremented at each iteration of the following loop
            # current player can be found like so:
            # current = turn_counter % 4
            turn_counter = -1

            # this will keep track of how far down the path we have seen
            furthest_path = 0

            # used to light up the path
            color_step = 1.0 / float(len(path))
            color_counter = 0.0

            while game_on:
                print("\ntop of game loop")
                turn_counter += 1
                print("turn counter = " + str(turn_counter))
                current_player = turn_counter % total_players
                print("current player = " + str(current_player))

                if furthest_path > 0:
                    # light up current tile of player
                    player_tile = path[players[current_player].furthest_path].place
                    current_anims = save_animations(game_board, player_tile)
                    for i in range(4):
                        game_board.set_tile_led_animation(player_tile, i, my_hsv_to_animation(0.9, 0.2))

                # current_player must answer a question to proceed
                print("\nPlayer " + players[current_player].name + " must answer a question.")
                terminal = input("Did the current_player answer the question correctly? (y/n) ")

                if furthest_path > 0:
                    # restore existing animations to player tile
                    restore_animations(game_board, player_tile, current_anims)

                if 'y' in terminal:
                    # if answer is correct keep stats for current_player
                    players[current_player].inc_correct()
                    players[current_player].inc_questions()
                    players[current_player].inc_furthest_path()

                else:
                    players[current_player].inc_questions()
                    continue

                print("question answered correctly")

                on_final_tile = False
                # check for final tile
                # this is immediately after the player path is incremented, so they will be moving to the final tile
                if players[current_player].furthest_path == len(path) - 1:
                    on_final_tile = True

                if players[current_player].furthest_path > len(path) - 1:
                    print("\nGAME OVER")
                    print("Player " + players[current_player].name + " WINS the game!")
                    print("\nStats:")
                    print("\tTotal Questions: " + str(players[current_player].total_questions))
                    print("\tCorrect Answers: " + str(players[current_player].total_correct))

                    game_on = False
                    x = input("\nPress enter to continue!")
                    continue

                # check if we need to light up another tile (if a player is in the lead)
                need_to_light_next_tile = False
                if players[current_player].furthest_path > furthest_path:
                    need_to_light_next_tile = True

                print("need to light tile = " + str(need_to_light_next_tile))
                current_tile = path[furthest_path].place

                #on_final_tile = False
                #if path[furthest_path].next is None:
                #    on_final_tile = True

                next_tile = path[players[current_player].furthest_path].place
                if need_to_light_next_tile:
                    # circle the current tile with lights for anticipation of the next tile
                    # first, see which leds have an existing animation
                    # atleast one should have an animation, since the current tile will have an arrow on it
                    current_anims = save_animations(game_board, current_tile)

                    # now that existing animations are saved, circle the leds with some color
                    for i in range(4):
                        game_board.set_tile_led_animation(current_tile, i, my_hsv_to_animation(random.uniform(0.1, 1.0), 0.07))
                        time.sleep(0.2)

                    # sleep and watch animations for a bit
                    time.sleep(1.5)

                    # restore existing animations, then light next path
                    restore_animations(game_board, current_tile, current_anims)


                    # prepare to light up the next tile
                    #current_tile = path[furthest_path].place
                    # this player is in the lead so increment the furthest path
                    if not on_final_tile:
                        furthest_path += 1

                    print("current tile = " + str(current_tile) + "\nnext tile = " + str(next_tile))

                    light_next_tile(game_board, current_tile, next_tile, color_step * color_counter)
                    color_counter += 1.0

                    # check if we are at the end of the path
                    #if furthest_path >= len(path):
                    #    print("*** end of path reached")
                    #    time.sleep(1.0)
                        # light the final tile in white
                    #    for i in range(4):

                # save animations for next tile
                player_tile = path[players[current_player].furthest_path].place
                current_anims = save_animations(game_board, player_tile)
                for i in range(4):
                    game_board.set_tile_led_animation(player_tile, i, my_hsv_to_animation(0.9, 0.2))

                print("waiting on cap sensor for tile " + str(next_tile))
                # we are now expecting the capacitive sensor to be activated for the next tile
                waiting_on_cap_sensor = True
                while waiting_on_cap_sensor:
                    if game_board.read_tile_capacitive_sensor(next_tile):
                        waiting_on_cap_sensor = False

                print("cap sensor activated for tile " + str(next_tile))

                restore_animations(game_board, player_tile, current_anims)

                if on_final_tile and need_to_light_next_tile:
                    # circle the final tile in white leds
                    for i in range(4):
                        game_board.set_tile_led_animation(next_tile, i, my_hsv_to_animation(1.0, 0.5))
                        time.sleep(0.2)

                time.sleep(1.0)

                # when the cap sensor is activated, we wait for a second then check if this tile is a ghoul
                # or check if this tile is the end of the path
                print("checking for ghoul")

                # if it is a ghoul, lock this current_player until they answer two questions
    except:
        print("Exception caught")

    bluetooth_server.stop_server()
    game_board.close()


def light_next_tile(game_board, tile_num, next_tile, color, duration=0.5):
    # next tile is to the east, so light up the east led on the current tile
    # and the west led on the next tile
    if tile_num - next_tile == -1:
        game_board.set_tile_led_animation(tile_num, LED_EAST, my_hsv_to_animation(color, duration))
        time.sleep(0.2)
        game_board.set_tile_led_animation(next_tile, LED_WEST, my_hsv_to_animation(color, duration))

    # next tile is south
    if tile_num - next_tile == -4:
        game_board.set_tile_led_animation(tile_num, LED_SOUTH, my_hsv_to_animation(color, duration))
        time.sleep(0.2)
        game_board.set_tile_led_animation(next_tile, LED_NORTH, my_hsv_to_animation(color, duration))

    # next tile is west
    if tile_num - next_tile == 1:
        game_board.set_tile_led_animation(tile_num, LED_WEST, my_hsv_to_animation(color, duration))
        time.sleep(0.2)
        game_board.set_tile_led_animation(next_tile, LED_EAST, my_hsv_to_animation(color, duration))

    # next tile is north
    if tile_num - next_tile == 4:
        game_board.set_tile_led_animation(tile_num, LED_NORTH, my_hsv_to_animation(color, duration))
        time.sleep(0.2)
        game_board.set_tile_led_animation(next_tile, LED_SOUTH, my_hsv_to_animation(color, duration))


# converts from hue to RGB in range 0 to 255
def my_hsv_to_animation(h, d=0.5):
    rgb = colorsys.hsv_to_rgb(h, 1.0, 0.25)
    rgb = (int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))
    up = Animation(RGB_start=(0,0,0), RGB_end=rgb, duration=d)
    dn = Animation(RGB_start=rgb, RGB_end=(0,0,0), duration=d)
    return AnimationChain([up, dn], 0)


def save_animations(game_board, current_tile):
    current_anims = []
    for i in range(4):
        if game_board.check_if_led_has_animation(current_tile, i):
            current_anims.append(
                game_board.animation_manager.get_animation(game_board.convert_tile_led_to_num(current_tile, i)))
        else:
            current_anims.append(None)

    return current_anims

def restore_animations(game_board, current_tile, current_anims):
    for i in range(4):
        game_board.clear_tile_led_animation(current_tile, i)
        game_board.set_tile_led_solid_color(current_tile, i, 0, 0, 0)
        if current_anims[i] is not None:
            game_board.set_tile_led_animation(current_tile, i, current_anims[i])


def do_demo_mode(game_board):
    game_board.turn_off_all_leds()

    # generate the path and print it out
    path_length = random.randint(0, 5) + 8
    ghoul_density = random.random()
    path = generate_path(path_length, ghoul_density)
    print("\nNew path generated")
    print("path length   = " + str(len(path)))
    print("ghoul density = " + str(ghoul_density))

    # print out the path to the console
    for x in path:
        print(str(x.place), end="")
        if (x.ghoul):
            print("!", end="")

        if x.next is not None:
            print(" -> ", end="")
    print("\n")

    # circle the starting tile with green lights
    for i in range(4):
        up = Animation(RGB_start=(0, 0, 0), RGB_end=(0, 64, 0), duration=0.75)
        dn = Animation(RGB_start=(0, 64, 0), RGB_end=(0, 0, 0), duration=0.75)
        chain = AnimationChain([up, dn], 0)
        game_board.set_tile_led_animation(path[0].place, i, chain)
        time.sleep(0.2)

    color_step = 1.0 / float(len(path))
    color_counter = 0.0
    for p in path:
        if p.next is not None:
            light_next_tile(game_board, p.place, p.next.place, color_step * color_counter)
        else:
            for i in range(4):
                up = Animation(RGB_start=(0, 0, 0), RGB_end=(0, 64, 64), duration=0.75)
                dn = Animation(RGB_start=(0, 64, 64), RGB_end=(0, 0, 0), duration=0.75)
                chain = AnimationChain([up, dn], 0)
                game_board.set_tile_led_animation(p.place, i, chain)
                time.sleep(0.2)

        time.sleep(0.5)

        color_counter += 1.0

    time.sleep(10)


if __name__ == "__main__":
    gameboard_main()
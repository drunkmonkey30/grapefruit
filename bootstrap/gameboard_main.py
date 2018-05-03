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
    total_players = 4

    playing = True
    try:
        while playing:
            # reset game board
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
            # current_player will be incremented after each turn
            # current_player can be found by mod'ing this with 4
            # ie current = turn_counter % 4
            turn_counter = -1

            # this will keep track of how far down the path we have seen
            furthest_path = 0

            # used to light up the path
            color_step = 1.0 / float(len(path))
            color_counter = 0.0

            while game_on:
                turn_counter += 1
                current_player = turn_counter % total_players

                # current_player must answer a question to proceed
                print(f'\nPlayer {players[current_player].name} must answer a question.')
                terminal = input("Did the current_player answer the question correctly? (y/n) ")
                if 'y' in terminal:
                    # if answer is correct keep stats for current_player
                    players[current_player].inc_correct()
                    players[current_player].inc_questions()
                    players[current_player].inc_furthest_path()

                else:
                    players[current_player].inc_questions()
                    # if answer is not correct, current current_player stays in the current square
                    # we increment current_player number, then continue from top of loop
                    continue

                # check if we need to light up another tile (if a player is in the lead)
                need_to_light_next_tile = False
                if players[current_player].furthest_path > furthest_path:
                    need_to_light_next_tile = True

                    # this player is in the lead so increment the furthest path
                    furthest_path += 1

                if need_to_light_next_tile:
                    # prepare to light up the next tile
                    current_tile = path[furthest_path].place

                    # check if we are at the end of the path
                    if furthest_path >= len(path):
                        # we are at the end of the path, so do something different
                        pass
                    else:
                        next_tile = path[furthest_path].place
                        #  TODO light the next tile

                # we are now expecting the capacitive sensor to be activated for the next tile

                while True:
                    if game_board.read_tile_capacitive_sensor()

                # when the cap sensor is activated, we wait for a second then check if this tile is a ghoul
                # or check if this tile is the end of the path

                # if it is a ghoul, lock this current_player until they answer two questions

                # if the tile is not a ghoul, we increment the current_player number and
                # continue from top of loop
                pass


            # light up the arrows for next tiles using colors
            # from the rainbow interpolated based on path length

            tile_num = 0
            for p in path:
                tile_num = p.place
                if p.next is not None:
                    next_tile = p.next.place
                    print("Tile: " + str(tile_num) + "  Next: " + str(next_tile) + "  Next - Tile: " + str(tile_num - next_tile))

                    # next tile is to the east, so light up the east led on the current tile
                    # and the west led on the next tile
                    if tile_num - next_tile == -1:
                        game_board.set_tile_led_animation(tile_num, LED_EAST, my_hsv_to_animation(color_step * color_counter))
                        game_board.set_tile_led_animation(next_tile, LED_WEST, my_hsv_to_animation(color_step * color_counter))

                    # next tile is south
                    if tile_num - next_tile == -4:
                        game_board.set_tile_led_animation(tile_num, LED_SOUTH, my_hsv_to_animation(color_step * color_counter))
                        game_board.set_tile_led_animation(next_tile, LED_NORTH, my_hsv_to_animation(color_step * color_counter))

                    # next tile is west
                    if tile_num - next_tile == 1:
                        game_board.set_tile_led_animation(tile_num, LED_WEST, my_hsv_to_animation(color_step * color_counter))
                        game_board.set_tile_led_animation(next_tile, LED_EAST, my_hsv_to_animation(color_step * color_counter))

                    # next tile is north
                    if tile_num - next_tile == 4:
                        game_board.set_tile_led_animation(tile_num, LED_NORTH, my_hsv_to_animation(color_step * color_counter))
                        game_board.set_tile_led_animation(next_tile, LED_SOUTH, my_hsv_to_animation(color_step * color_counter))

                color_counter += 1.0
                time.sleep(0.5)

            # color the final tile, which is held in tile_num
            for i in range(4):
                up = Animation(RGB_start=(0, 0, 0), RGB_end=(64, 64, 64), duration=0.75)
                dn = Animation(RGB_start=(64,64,64), RGB_end=(0, 0, 0), duration=0.75)
                chain = AnimationChain([up, dn], 0)
                game_board.set_tile_led_animation(tile_num, i, chain)
                time.sleep(0.2)

            time.sleep(10)

    except:
        print("Exception caught")

    bluetooth_server.stop_server()
    game_board.close()


# converts from hue to RGB in range 0 to 255
def my_hsv_to_animation(h, d=0.5):
    rgb = colorsys.hsv_to_rgb(h, 1.0, 0.25)
    rgb = (int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))
    up = Animation(RGB_start=(0,0,0), RGB_end=rgb, duration=d)
    dn = Animation(RGB_start=rgb, RGB_end=(0,0,0), duration=d)
    return AnimationChain([up, dn], 0)


if __name__ == "__main__":
    gameboard_main()
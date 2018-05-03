import sys
sys.path.append('../bt/')
sys.path.append('../board_hardware/')
sys.path.append('../pathing/')

import random
import time
import colorsys

from server import *
from game_board import *
from mainPath import *


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


    playing = True
    try:
        while playing:
            game_board.turn_off_all_leds()

            # generate the path and print it out
            path_length = random.randint(0, 5) + 8
            ghoul_density = random.random()

            path = generate_path(path_length, ghoul_density)
            print("\nNew path generated")
            print("path length   = " + str(len(path)))
            print("ghoul density = " + str(ghoul_density))

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

            # light up the arrows for next tiles using colors
            # from the rainbow interpolated based on path length
            step = 1.0 / float(len(path))
            counter = 0.0
            tile_num = 0
            for p in path:
                tile_num = p.place
                if p.next is not None:
                    next_tile = p.next.place
                    print("Tile: " + str(tile_num) + "  Next: " + str(next_tile) + "  Next - Tile: " + str(tile_num - next_tile))

                    # next tile is to the east, so light up the east led on the current tile
                    # and the west led on the next tile
                    if tile_num - next_tile == -1:
                        game_board.set_tile_led_animation(tile_num, LED_EAST, my_hsv_to_animation(step * counter))
                        game_board.set_tile_led_animation(next_tile, LED_WEST, my_hsv_to_animation(step * counter))

                    # next tile is south
                    if tile_num - next_tile == -4:
                        game_board.set_tile_led_animation(tile_num, LED_SOUTH, my_hsv_to_animation(step * counter))
                        game_board.set_tile_led_animation(next_tile, LED_NORTH, my_hsv_to_animation(step * counter))

                    # next tile is west
                    if tile_num - next_tile == 1:
                        game_board.set_tile_led_animation(tile_num, LED_WEST, my_hsv_to_animation(step * counter))
                        game_board.set_tile_led_animation(next_tile, LED_EAST, my_hsv_to_animation(step * counter))

                    # next tile is north
                    if tile_num - next_tile == 4:
                        game_board.set_tile_led_animation(tile_num, LED_NORTH, my_hsv_to_animation(step * counter))
                        game_board.set_tile_led_animation(next_tile, LED_SOUTH, my_hsv_to_animation(step * counter))

                counter += 1.0
                time.sleep(0.5)

            # color the final tile, which is held in tile_num
            for i in range(4):
                up = Animation(RGB_start=(0, 0, 0), RGB_end=(64, 64, 64), duration=0.75)
                dn = Animation(RGB_start=(64,64,64), RGB_end=(0, 0, 0), duration=0.75)
                chain = AnimationChain([up, dn], 0)
                game_board.set_tile_led_animation(tile_num, i, chain)
                time.sleep(0.2)

            for p in path:
                if p.ghoul:
                    for i in range(4):
                        led_num = game_board.convert_tile_led_to_num(p.place, i)
                        if not game_board.animation_manager.check_led_has_anim(led_num):
                            game_board.set_tile_led_animation(p.place, i, my_hsv_to_animation(0.0, d=0.1))

            time.sleep(10)

    except:
        print("Exception caught")

    if connected.is_set():
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
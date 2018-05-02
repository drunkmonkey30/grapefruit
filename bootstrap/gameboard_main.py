import sys
sys.path.append('../bt/')
sys.path.append('../board_hardware/')
from server import *
from game_board import *


# main file for gameboard
# this will initialize bluetooth, connect to database, do whatever needs to be done when the game starts up


def gameboard_main():
    print("gameboard_main entry")

    print("\nstarting bluetooth server")
    bluetooth_server = BlueServer()
    connected = bluetooth_server.start_server()

    game_board = GameBoard(2)

    a1 = Animation(RGB_start=(0, 0, 0), RGB_end=(255, 0, 0), duration=1.5)
    a2 = Animation(RGB_start=(0, 0, 0), RGB_end=(0, 255, 0), duration=1.5)
    a3 = Animation(RGB_start=(0, 0, 0), RGB_end=(0, 0, 255), duration=1.5)
    ac = AnimationChain([a1, a2, a3], 0)

    game_board.set_tile_led_animation(0, LED_NORTH, ac)
    game_board.set_tile_led_animation(0, LED_SOUTH, ac)
    game_board.set_tile_led_animation(0, LED_EAST, ac)
    game_board.set_tile_led_animation(0, LED_WEST, ac)

    playing = True
    try:
        while playing:
            pass
    except:
        print("Exception caught")
        pass

    if connected.is_set():
        bluetooth_server.stop_server()

    game_board.close()


if __name__ == "__main__":
    gameboard_main()
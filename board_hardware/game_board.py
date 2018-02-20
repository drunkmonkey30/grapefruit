import sys
sys.path.append('../led_things/')

from led_manager import *
from animation_manager import *

# provides access to hardware things on the game board
# eg. leds, capacitive sensors, solenoids...

# constants for specific leds on the tile
LED_NORTH   = 3
LED_SOUTH   = 1
LED_EAST    = 2
LED_WEST    = 0

class GameBoard:
    led_manager = None
    animation_manager = None
    num_tiles = 0

    """
    initialize the game board
    pass in N for NxN game board, so 4 for 4x4 grid
    """
    def __init__(self, tiles_N):
        self.num_tiles = tiles_N * tiles_N
        self.led_manager = LedManager(self.num_tiles * 4)
        self.animation_manager = LedAnimationManager(self.led_manager, 30.0)

    def start_animations(self):
        self.animation_manager.start_animation_thread()

    def stop_animations(self):
        self.animation_manager.end_animation_thread()

    """
    set a specifice led on a specific tile to a solid, unchanging color
    this will cancel any animations that have been set on that led
    """
    def set_tile_led_solid_color(self, tile_num, which_led, r, g, b):
        pass

    def set_tile_led_animation(self, tile_num, which_led, animation):
        pass

    def read_tile_capacitive_sensor(self, tile_num):
        pass

    def convert_tile_led_to_num(self, tile_num, which_led):
        return (tile_num * 4) + which_led


if __name__ == "__main__":
    print('testing game board api')

    board = GameBoard(2)
    print('led_manager:', board.led_manager, board.led_manager.numLeds)
    print('animation_manager:', board.animation_manager)

    print('done')
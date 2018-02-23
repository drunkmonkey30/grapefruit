import sys
sys.path.append('../led_things/')

from led_manager import *
from animation_manager import *
from animation import *

# main interface for hardware on the gameboard
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

    #initialize the game board
    #pass in N for NxN game board, so 4 for 4x4 grid
    def __init__(self, tiles_N):
        self.num_tiles = tiles_N * tiles_N
        self.led_manager = LedManager(self.num_tiles * 4)
        self.animation_manager = LedAnimationManager(self.led_manager, 30.0)

    def close(self):
        if not self.led_manager == None:
            self.led_manager.close()

    def start_animations(self):
        self.animation_manager.start_animation_thread()

    def stop_animations(self):
        self.animation_manager.end_animation_thread()


    #set a specifice led on a specific tile to a solid, unchanging color
    #this will cancel any animations that have been set on that led
    def set_tile_led_solid_color(self, tile_num, which_led, r, g, b):
        led = self.convert_tile_led_to_num(tile_num, which_led)
        self.led_manager.set_color(led, r, g, b)

    #set an animation of a specific led of a specific tile
    def set_tile_led_animation(self, tile_num, which_led, animation):
        led = self.convert_tile_led_to_num(tile_num, which_led)
        self.animation_manager.add_animation(led, animation)

    def read_tile_capacitive_sensor(self, tile_num):
        print("***ERROR: GameBoard.read_tile_capcitive_sensor is not yet implemented")
        return

    def convert_tile_led_to_num(self, tile_num, which_led):
        return (tile_num * 4) + which_led


if __name__ == "__main__":
    print('testing game board api')

    board = GameBoard(4)
    print('led_manager:', board.led_manager, board.led_manager.numLeds)
    print('animation_manager:', board.animation_manager)

    r_up = Animation((0,0,0),   (255,0,0),  2.0)
    r_dn = Animation((255,0,0), (0,0,0),    2.0)
    g_up = Animation((0,0,0),   (0,255,0),  2.0)
    g_dn = Animation((0,255,0), (0,0,0),    2.0)
    b_up = Animation((0,0,0),   (0,0,255),  2.0)
    b_dn = Animation((0,0,255), (0,0,0),    2.0)
    chain = AnimationChain([r_up, r_dn, g_up, g_dn, b_up, b_dn], 0)

    board.set_tile_led_animation(0, 0, chain)
    board.set_tile_led_animation(0, 1, chain)
    board.set_tile_led_animation(0, 2, chain)
    board.set_tile_led_animation(0, 3, chain)

    cycle_colors = AnimationChain(
        [
            Animation((0,0,0),(255,0,0), 3.0),
            Animation((255,0,0),(0,0,0), 3.0),
            Animation((0,0,0),   (0,255,0), 3.0),
            Animation((0,255,0), (0,0,0),   3.0),
            Animation((0,0,0),   (0,0,255), 3.0),
            Animation((0,0,255), (0,0,0),   3.0),
            Animation((0,0,0),(255,0,0),    3.0),
            Animation((255,0,0),(255,255,0), 3.0),
            Animation((255,255,0),(255,255,255), 3.0),
            Animation((255,255,255),(0,255,255), 3.0),
            Animation((0,255,255),(0,0,255),   3.0),
            Animation((0,0,255),(255,0,255),    3.0)
        ], 0)

    board.set_tile_led_animation(1, 1, cycle_colors)

    board.start_animations()

    try:
        while True:
            pass
    except:
        board.stop_animations()

    board.close()
    print('done')
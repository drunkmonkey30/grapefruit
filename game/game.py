import sys
sys.path.append('../board_hardware/')

from game_board import *

class Game:
    board = None

    def __init__(self, tiles_N):
        board = GameBoard(tiles_N)
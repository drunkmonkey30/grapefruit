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

    game_board = GameBoard(4)

    playing = True
    while playing:
        pass

    bluetooth_server.stop_server()
    game_board.close()


if __name__ == "__main__":
    gameboard_main()
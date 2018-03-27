import sys
sys.path.append('../bt/')
from server import *


# main file for gameboard
# this will initialize bluetooth, connect to database, do whatever needs to be done when the game starts up


def gameboard_main():
    print("gameboard_main entry")

    print("\nstarting bluetooth server")
    bluetooth_server = BlueServer()
    connected = bluetooth_server.start_server()




if __name__ == "__main__":
    gameboard_main()
import sys
sys.path.append('../bt/')
from client import *


# main executable for flashcard device
# starts bluetooth, connects to gameboard, does whatever...


def flashcard_main():
    blue_client = BlueClient()

    blue_client.start_client()





if __name__ == "__main__":
    flashcard_main()
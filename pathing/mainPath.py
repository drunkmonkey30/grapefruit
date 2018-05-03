import random

#Smaller number gives higher ghoul density
GHOUL_DENSITY = 5
#Set path lengths, could have user selection
#Tiles used in path are 1 + the path length
SHORT_PATH = 5
MED_PATH = 8
LONG_PATH = 12
#I'm lazy
T = True


#Tile definition
class Tile:
    def __init__(self, place):
        #place number in the array
        self.place = place
        #No tile starts out a ghoul or linked
        self.ghoul = False
        self.above = None
        self.right = None
        self.below = None
        self.left = None
        self.next = None

    #Links two tiles, cuts down on typing out all tiles
    def linkAbove(self, neighbor):
        self.above = neighbor
        neighbor.below = self

    def linkRight(self, neighbor):
        self.right = neighbor
        neighbor.left = self

    def linkBelow(self, neighbor):
        self.below = neighbor
        neighbor.above = self

    def linkLeft(self, neighbor):
        self.left = neighbor
        neighbor.right = self


#These are all global
#t=top,m=mid,l=left,r=right,b=bot
tll = Tile(0)
tml = Tile(1)
tmr = Tile(2)
trr = Tile(3)
mtll = Tile(4)
mtml = Tile(5)
mtmr = Tile(6)
mtrr = Tile(7)
mbll = Tile(8)
mbml = Tile(9)
mbmr = Tile(10)
mbrr = Tile(11)
bll = Tile(12)
bml = Tile(13)
bmr = Tile(14)
brr = Tile(15)
#Board array is also global
BOARD = [tll, tml, tmr, trr, mtll, mtml, mtmr, mtrr, mbll, mbml, mbmr, mbrr, bll, bml, bmr, brr]


#Figures out which tiles are available through controls,
#an rng, and recursion then assigns the next link of path
#controls are passed so that each tilespace gets checked
def nextStep(base, c1, c2, c3, c4):
    x = random.randint(0, 99)
    #if all spaces have been checked assign None to break out
    if c1 or c2 or c3 or c4:
        if x % 4 == 0:
            if base.above is not None:
                base.next = base.above
                nullSpace(base)
            else:
                #activate the control so that function knows this has been checked
                c1 = False
                nextStep(base, c1, c2, c3, c4)
        if x % 4 == 1:
            if base.right is not None:
                base.next = base.right
                nullSpace(base)
            else:
                c2 = False
                nextStep(base, c1, c2, c3, c4)
        if x % 4 == 2:
            if base.below is not None:
                base.next = base.below
                nullSpace(base)
            else:
                c3 = False
                nextStep(base, c1, c2, c3, c4)
        if x % 4 == 3:
            if base.left is not None:
                base.next = base.left
                nullSpace(base)
            else:
                c4 = False
                nextStep(base, c1, c2, c3, c4)
    else:
        base.next = None


#developing for void space detection
#going to work with a prev tile
def testNext(base):
    nextStep(base, T, T, T, T)
    if base.next is None:
        return base.next
    else:
        return base


def nullSpace(base):
    if base.above is not None:
        base.above.below = None
    if base.right is not None:
        base.right.left = None
    if base.below is not None:
        base.below.above = None
    if base.left is not None:
        base.left.right = None


#Used before each path is created
#Relinks all tiles on the board to original state
#sets ghouls back to False and clears Next spaces
def start(BOARD):
    BOARD[0].linkRight(BOARD[1])
    BOARD[1].linkRight(BOARD[2])
    BOARD[2].linkRight(BOARD[3])
    BOARD[4].linkRight(BOARD[5])
    BOARD[5].linkRight(BOARD[6])
    BOARD[6].linkRight(BOARD[7])
    BOARD[8].linkRight(BOARD[9])
    BOARD[9].linkRight(BOARD[10])
    BOARD[10].linkRight(BOARD[11])
    BOARD[12].linkRight(BOARD[13])
    BOARD[13].linkRight(BOARD[14])
    BOARD[14].linkRight(BOARD[15])
    BOARD[4].linkAbove(BOARD[0])
    BOARD[5].linkAbove(BOARD[1])
    BOARD[6].linkAbove(BOARD[2])
    BOARD[7].linkAbove(BOARD[3])
    BOARD[8].linkAbove(BOARD[4])
    BOARD[9].linkAbove(BOARD[5])
    BOARD[10].linkAbove(BOARD[6])
    BOARD[11].linkAbove(BOARD[7])
    BOARD[12].linkAbove(BOARD[8])
    BOARD[13].linkAbove(BOARD[9])
    BOARD[14].linkAbove(BOARD[10])
    BOARD[15].linkAbove(BOARD[11])
    for x in range(0, 16):
        BOARD[x].next = None
        BOARD[x].ghoul = False


#rng for starting place of board
def rando():
    s = random.randint(0, 15)
    return s


#Loops through to print(the grid, just for testing readability
def printGrid(brd):
    for x in range(len(brd)):
        if x % 4 != 0:
            if x < 10:
                print(brd[x].place, '  ', end=" ")
            else:
                print(brd[x].place, ' ', end=" ")
        else:
            if x < 10:
                print('\n', brd[x].place, '  ')
            else:
                print('\n', brd[x].place, ' ')

    print()


#starts at selected starting tile and follows
#the Next trail until a None space
def printPath(s):
    print(s.place)
    s = s.next
    while s is not None:
        print('->')
        if s.ghoul is True:
            print('!')
        print(s.place)
        s = s.next


#choose path length
#pathLen = SHORT_PATH

#for loop for testing
def generate_path(pathLen, ghoul_density):
    #for i in range(0, 50):
    #    print("*** Iteration #" + str(i))
    #clean everything up and print(grid
    start(BOARD)
    #printGrid(BOARD)
    #get a new starting place
    startPlace = rando()
    #temp is the tile finder, it communicates with the board tiles
    temp = BOARD[startPlace]
    for x in range(0, pathLen):
        if temp is not None:
            #make sure temp is an exact copy of current place on board
            temp = BOARD[temp.place]
            #test the next space for validity
            #and update temp
            temp = testNext(temp)
            #if temp is None the path is dead
            if temp is not None:
                #Ghoul tiles are placed as the next tiles are selected
                #r = random.randint(0, 99)
                #if r % ghoul_density == 0:
                #    temp.next.ghoul = True

                #g = random.normalvariate(0.5, 0.5)
                g = random.gauss(0.5, 0.5)
                #print("G = " + str(g))
                if g <= ghoul_density:
                    temp.next.ghoul = True

                #update temp to the next tile in the path
                temp = temp.next
                #update the board to match temp
                BOARD[temp.place] = temp
    #print(out the path
    #printPath(BOARD[startPlace])

    path = []
    path.append(BOARD[startPlace])
    t = BOARD[startPlace].next
    while t is not None:
        path.append(t)
        t = t.next

    #return BOARD
    return path


if __name__ == "__main__":
    path = generate_path(10, 0.2)
    print("length of path: " + str(len(path)))
    for x in path:
        print(str(x.place), end="")
        if x.ghoul:
            print("!", end="")

        print(" -> ", end="")

    print("\n")
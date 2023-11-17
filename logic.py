from random import randint

TOTAL_CARDS = 5
WIN_SIZE_X = 900
WIN_SIZE_Y = 600

rocks = 10
papers = 10
scissors = 10
test = ["rock", "paper", "paper", "rock"]

class player:

    def __init__(self):
        self.won = False
        self.cards = []
        self.points = [0,0,0]

    def draw(self, numOfCards):
        for i in range(numOfCards):
            self.cards.append(drawCard())

    def playCard(self, index):
        self.cards.pop(index)
        return self.cards

    def hasWon(self):
        if 3 in self.points:
            self.won = True
            return True
        elif self.points[0] >= 1 and self.points[1] >= 1 and self.points[2] >= 1:
            return True
        else:
            return False


def drawCard():
    global rocks, papers, scissors
    if rocks + papers + scissors == 0:
        return "----"
    
    while True:
        rand = randint(1,3)
        
        if rand == 1:
            if rocks == 0:
                continue
            rocks -= 1
            return "Rock"
        
        elif rand == 2:
            if papers == 0:
                continue
            papers -= 1
            return "Paper"
        
        elif rand == 3:
            if scissors == 0:
                continue
            scissors -= 1
            return "Scissors"

print(rocks, papers, scissors)

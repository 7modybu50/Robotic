import random
from random import randint

TOTAL_CARDS = 5
WIN_SIZE_X = 900
WIN_SIZE_Y = 600

class player:

    def __init__(self):
        self.won = False
        self.cards = []
        self.points = [0,0,0]

    def draw(self, numOfCards):
        for i in range(numOfCards):
            self.cards.append(drawCard())

    def draw2(self, num, remaining):
        cards = []

        for i in range(num):
            total = sum(remaining)
            if total <= 0:
                return [], [0,0,0]
            prob = [x/total for x in remaining]
            card = random.choices(['r', 'p', 's'], prob)[0]
            self.cards.append(card)

            if card == 'r':
                remaining[0] -= 1
            elif card == 'p':
                remaining[1] -= 1
            else:
                remaining[2] -= 1

        return cards, remaining

    def bin(self, card):
        self.cards.remove(card)

    def playCard(self, index):
        self.cards.pop(index)
        return self.cards

    def hasWon(self):
        if 3 in self.points:
            self.won = True
            return True
        elif self.points[0] >= 1 and self.points[1] >= 1 and self.points[2] >= 1:
            self.won = True
            return True
        else:
            return False


rocks = 10
papers = 10
scissors = 10

def drawCard():
    global rocks, papers, scissors
    if rocks + papers + scissors == 0:
        return "-"
    
    while True:
        rand = randint(1,3)
        
        if rand == 1:
            if rocks == 0:
                continue
            rocks -= 1
            return 'r'
        
        elif rand == 2:
            if papers == 0:
                continue
            papers -= 1
            return 'p'
        
        elif rand == 3:
            if scissors == 0:
                continue
            scissors -= 1
            return 's'

from random import randint

p1_points = []
p2_points = []
p1_cards = []
p2_cards = []
rocks = 10
papers = 10
scissors = 10
test = ["rock", "paper", "paper", "rock"]


def won(points):
    rocks = 0
    papers = 0
    scissors = 0
    for i in points:
        if i == "rock":
            rocks = rocks + 1
        elif i == "paper":
            papers = papers + 1
        elif i == "scissor":
            scissors = scissors + 1
        if rocks == 3 or papers == 3 or scissors == 3:
            return True
        elif rocks == 1 and papers == 1 and scissors == 1:
            return True
    return False


def playCard(cards, cardInd):
    cards.pop(cardInd)
    return cards


def drawCard(cards):
    global rocks, papers, scissors
    if rocks + papers + scissors == 0:
        return cards
    yes = True
    while yes:
        rand = randint(1,3)
        if rand == 1:
            if rocks == 0:
                continue
            cards.append("rock")
            rocks -= 1
            yes = False
        elif rand == 2:
            if papers == 0:
                continue
            cards.append("paper")
            papers -= 1
            yes = False
        elif rand == 3:
            if scissors == 0:
                continue
            cards.append("scissor")
            scissors -= 1
            yes = False
    return cards


print(drawCard(test))
print(rocks, papers, scissors)

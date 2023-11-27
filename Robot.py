import pomdp_py


class RRSPState(pomdp_py.State):
    def __init__(self, myPoints, oPoints, cards, oRock, oPaper, oScissor):
        self.myPoints = myPoints  # the robot's points
        self.oPoints = oPoints  # the opponent's points
        self.cards = cards
        self.oRock = oRock
        self.oPaper = oPaper
        self.oScissor = oScissor

    def __str__(self):
        return "My points:\nrocks: " + str(self.myPoints[0]) + ", papers: " + str(
            self.myPoints[1]) + ", scissors: " + str(self.myPoints[2]) + "Opponent's points:\nrocks: " + str(
            self.oPoints[0]) + ", papers: " + str(self.oPoints[1]) + ", scissors: " + str(self.oPoints[2])
    def __hash__(self):
        return hash(self.__str__())
    def __eq__(self, other):
        if isinstance(other, RRSPState):
            return self.myPoints == other.myPoints and self.oPoints == other.oPoints
        return False

class RRSPAction(pomdp_py.Action):
    def __init__(self, name):
        self.name = name

    def __eq__(self, other):
        if isinstance(other, RRSPAction):
            return self.name == other.name
        return False
    def __hash__(self):
        return hash(self.name)


class RRSPObservation(pomdp_py.Observation):
    def __init__(self, name):
        self.name = name
    def __eq__(self, other):
        if isinstance(other, RRSPObservation):
            return self.name == other.name
        return False

class ObservationModel(pomdp_py.ObservationModel):
    def __init__(self, current_state):
        self.current_state = current_state
    def probability(self, observation, next_state, action):
        mPoints = sum(next_state.myPoints) - sum(self.current_state.myPoints)
        oPoints = sum(next_state.oPoints) - sum(self.current_state.oPoints)
        #the probability of the opponent's card if you played a rock card
        if action.name == "play_rock" and mPoints + oPoints == 0:
            if observation == "rock": return 1
            else: return 0
        elif action.name == "play_rock" and oPoints == 1:
            if observation == "paper": return 1
            else: return 0
        elif action.name == "play_rock" and mPoints == 1:
            if observation == "scissor": return 1
            else: return 0
        # the probability of the opponent's card if you played a paper card
        elif action.name == "play_paper" and mPoints + oPoints == 0:
            if observation == "paper":
                return 1
            else:
                return 0
        elif action.name == "play_paper" and oPoints == 1:
            if observation == "scissor":
                return 1
            else:
                return 0
        elif action.name == "play_paper" and mPoints == 1:
            if observation == "rock":
                return 1
            else:
                return 0
        # the probability of the opponent's card if you played a paper card
        elif action.name == "play_scissor" and mPoints + oPoints == 0:
            if observation == "scissor":
                return 1
            else:
                return 0
        elif action.name == "play_scissor" and oPoints == 1:
            if observation == "rock":
                return 1
            else:
                return 0
        elif action.name == "play_scissor" and mPoints == 1:
            if observation == "paper":
                return 1
            else:
                return 0
        else: return 0

    def get_all_observations(self):
        return [RRSPObservation(s) for s in ["rock", "paper", "scissor"]]
    def update_state(self, state):
        self.current_state = state



standard = ['r','p','s'] #Put somewhere
class TransitionModel(pomdp_py.TransitionModel):
    def probability(self, start_state, end_state, action):

        base = 1/3 #at start prime_prob MUST be roughly == this

        #Can the opponent make it end_state?

        #First find the opponents move required to get to the end_state
        if (sum(end_state.points) > sum(end_state.points)): # player wins in end_state, opponent loses
            opp_action = (standard.index(action[5]) + 2) % 3
        elif (sum(end_state.opp_points) > sum(end_state.start_points)): #opponent wins in end_state, player loses
            opp_action = (standard.index(action[5]) + 1) % 3
        else:
            opp_action = standard.index(action[5])

        #Secondly, calculate the probability that the opponent wants to play that card P(plays x):
        # (1) Higher Probability of playing cards that have a chance of getting them a win (Offense)
        # (2) Higher Probability of playing cards that block opponent wins (Offense)
        # (3) To play the card, they need it in hand

        #(1)
        #See how close the opponent is to achieving the win condition of "winning with 1 of each type"
        if (start_state.opp_points[(opp_action+1)%3] >= 1) or (start_state.opp_points[(opp_action+2)%3] >= 1):
            spread_win_closeness = 1/3
            if (start_state.opp_points[(opp_action+1)%3] >= 1) or (start_state.opp_points[(opp_action+2)%3] >= 1):
                spread_win_closeness = 2/3

        #Extract the win condition the opponent is closer to in the form of a fraction of "closeness"
        opp_win_closeness = max((start_state.opp_points[opp_action] / 3), spread_win_closeness)

        #Calculate the probability of the opponent playing that card.
        #play_x_prob = opp_win_closeness (some operator) player_win_closeness

        #Thirdly, calculate the probability opponent plays that card given they've picked it up.
        #P(plays x | card_in_hand) = P(card_in_hand | plays x) * P(plays x) / P(card_in_hand)

        # prime_prob = 1? * see below? / (num_x_unobserved / remaining_cards)
        # return prime_prob


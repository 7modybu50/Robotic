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
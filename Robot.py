import pomdp_py
from pomdp_py import *
import random

class RRSPState(pomdp_py.State):
    def __init__(self, myPoints, oPoints, cards, oRock, oPaper, oScissor):
        self.myPoints = myPoints  # the robot's points
        self.oPoints = oPoints  # the opponent's points
        self.cards = cards
        self.oRock = oRock
        self.oPaper = oPaper
        self.oScissor = oScissor

    def __str__(self):
        return "\nMy points:\nrocks: " + str(self.myPoints[0]) + ", papers: " + str(
            self.myPoints[1]) + ", scissors: " + str(self.myPoints[2]) + "\n\nOpponent's points:\nrocks: " + str(
            self.oPoints[0]) + ", papers: " + str(self.oPoints[1]) + ", scissors: " + str(self.oPoints[2]) + "\n" + str(self.cards)

    def __repr__(self):
        return self.__str__()
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
    
    def __str__(self):
        return self.name
    
    def __hash__(self):
        return hash(self.name)


class RRSPObservation(pomdp_py.Observation):
    def __init__(self, name, draw):
        self.name = name
        self.draw = draw
    def __eq__(self, other):
        if isinstance(other, RRSPObservation):
            return self.name == other.name and self.draw == other.draw
        return False
    def __str__(self):
        return self.name + " " + self.draw
    def __hash__(self):
        return hash(self.name + self.draw)

class ObservationModel(pomdp_py.ObservationModel):
    def __init__(self, current_state):
        self.current_state = current_state
    def probability(self, observation, next_state, action):
        mPoints = sum(next_state.myPoints) - sum(self.current_state.myPoints)
        oPoints = sum(next_state.oPoints) - sum(self.current_state.oPoints)

        #the probability of the opponent's card if you played a rock card
        prob = 0
        if action.name == "play_rock" and mPoints + oPoints == 0:
            if observation.name == "rock":
                prob = 0.9
            else:
                prob = 0.1
        elif action.name == "play_rock" and oPoints == 1:
            if observation.name == "paper":
                prob = 0.9
            else:
                prob = 0.1
        elif action.name == "play_rock" and mPoints == 1:
            if observation.name == "scissor":
                prob = 0.9
            else:
                prob = 0.1
        # the probability of the opponent's card if you played a paper card
        elif action.name == "play_paper" and mPoints + oPoints == 0:
            if observation.name == "paper":
                prob = 0.9
            else:
                prob = 0.1
        elif action.name == "play_paper" and oPoints == 1:
            if observation.name == "scissor":
                prob = 0.9
            else:
                prob = 0.1
        elif action.name == "play_paper" and mPoints == 1:
            if observation.name == "rock":
                prob = 0.9
            else:
                prob = 0.1
        # the probability of the opponent's card if you played a paper card
        elif action.name == "play_scissor" and mPoints + oPoints == 0:
            if observation.name == "scissor":
                prob = 0.9
            else:
                prob = 0.1
        elif action.name == "play_scissor" and oPoints == 1:
            if observation.name == "rock":
                prob = 0.9
            else:
                prob = 0.1
        elif action.name == "play_scissor" and mPoints == 1:
            if observation.name == "paper":
                prob = 0.9
            else:
                prob = 0.1
        else:
            return 0
        if observation.draw == "rock":
            return prob * (10 - self.current_state.oRock)/(30 - (self.current_state.oRock + self.current_state.oPaper + self.current_state.oScissor))
        elif observation.draw == "paper":
            return prob * (10 - self.current_state.oPaper)/(30 - (self.current_state.oRock + self.current_state.oPaper + self.current_state.oScissor))
        elif observation.draw == "paper":
            return prob * (10 - self.current_state.oScissor)/(30 - (self.current_state.oRock + self.current_state.oPaper + self.current_state.oScissor))
        else:
            return prob
    def get_all_observations(self):
        return [RRSPObservation(s, x) for s in ["rock", "paper", "scissor"] for x in ["rock", "paper", "scissor"]]

    def sample(self, next_state, action):
        probabilities = [self.probability(obs, next_state, action) for obs in self.get_all_observations()]
        remaining = 1 - sum(probabilities)

        for i in range(len(probabilities) - 1):
            probabilities[i] += remaining / len(probabilities)

        return random.choices(self.get_all_observations(), probabilities)[0]
    def update_state(self, state):
        self.current_state = state


standard = ['r','p','s'] #Put somewhere

class TransitionModel(pomdp_py.TransitionModel):
    def probability(self, start_state, end_state, action):

        if action.name[5:] not in start_state.cards:
            print("yup")
            return 0

        base = 1/3 #at start prime_prob MUST be roughly == this

        #Can the opponent make it end_state?

        #First find the opponents move required to get to the end_state
        if (sum(end_state.myPoints) > sum(start_state.myPoints)): # player wins in end_state, opponent loses
            opp_action = (standard.index(action.name[5]) + 1) % 3
        elif (sum(end_state.oPoints) > sum(start_state.oPoints)): # opponent wins in end_state, player loses
            opp_action = (standard.index(action.name[5]) + 2) % 3
        else:
            opp_action = standard.index(action.name[5])

        #Secondly, calculate the probability that the opponent wants to play that card P(plays x):
        # (1) Higher Probability of playing cards that have a chance of getting them a big win (Offense)
        # (2) Higher Probability of playing cards that block our big win (defense)
        # (3) To play the card, they need it in hand

        #(1)
        #See how close the opponent is to achieving the win condition of "winning with 1 of each type"
        if (start_state.oPoints[(opp_action+1)%3] >= 1) or (start_state.oPoints[(opp_action+2)%3] >= 1):
            spread_win_closeness = 1/3
            if (start_state.oPoints[(opp_action+1)%3] >= 1) and (start_state.oPoints[(opp_action+2)%3] >= 1):
                spread_win_closeness = 2/3
        else:
            spread_win_closeness = 0

        #Extract the win condition the opponent is closer to in the form of a fraction of "closeness"
        opp_win_closeness = max((start_state.oPoints[opp_action] / 3), spread_win_closeness)

        #(2)
        #Get the highest point win type
        highest = max(start_state.myPoints)
        highest_types = []
        for i in range(3):
            if start_state.myPoints[i] == highest:
                highest_types.append(i)

        defense_effect = 0
        if len(highest_types) != 3:
            for item in highest_types:
                if (item+1)%3 == opp_action:
                    defense_effect += 0.6
                elif item == opp_action:
                    defense_effect += 0.4
                else:
                    defense_effect += 0.1                               # Maybe want negative value?
            defense_effect = defense_effect / len(highest_types)

        #Calculate the probability of the opponent playing that card.

        play_x_prob = base + opp_win_closeness + defense_effect         # Probably not how math works

        #Thirdly, calculate the probability opponent plays that card given they've picked it up.
        #P(plays x | card_in_hand) = P(card_in_hand | plays x) * P(plays x) / P(card_in_hand)

        if standard[opp_action] == 'r':
            prime_prob = play_x_prob/ (10 - start_state.oRock / (30 - (start_state.oRock + start_state.oPaper + start_state.oScissor))) #(3)
        if standard[opp_action] == 'p':
            prime_prob = play_x_prob/ (10 - start_state.oPaper / (30 - (start_state.oRock + start_state.oPaper + start_state.oScissor))) #(3)
        else:
            prime_prob = play_x_prob/ (10 - start_state.oScissor / (30 - (start_state.oRock + start_state.oPaper + start_state.oScissor)))

        return prime_prob

    def sample(self, state, action):
        probabilities = [self.probability(ss,state,action) for state in self.get_all_states()]
        remaining = 1 - sum(probabilities)

        for i in range(len(probabilities)-1):
            probabilities[i] += remaining/len(probabilities)

        return random.choices(self.get_all_states(), probabilities)[0]
    def get_all_states(self):

        state = ss
        states = [ss]

        #print("gas:")
        #print(state.cards)

        if "rock" in state.cards:
            states.append(RRSPState([ss.myPoints[0] + 1, ss.myPoints[1], ss.myPoints[2]], ss.oPoints, ss.cards, ss.oRock, ss.oPaper, ss.oScissor))
            states.append(RRSPState(ss.myPoints, [ss.oPoints[0], ss.oPoints[1] + 1, ss.oPoints[2]], ss.cards, ss.oRock, ss.oPaper, ss.oScissor))
        if "paper" in state.cards:
            states.append(RRSPState([ss.myPoints[0], ss.myPoints[1] + 1, ss.myPoints[2]], ss.oPoints, ss.cards, ss.oRock, ss.oPaper, ss.oScissor))
            states.append(RRSPState(ss.myPoints, [ss.oPoints[0], ss.oPoints[1], ss.oPoints[2] + 1], ss.cards, ss.oRock, ss.oPaper, ss.oScissor))
        if "scissor" in state.cards:
             states.append(RRSPState([ss.myPoints[0], ss.myPoints[1], ss.myPoints[2] + 1], ss.oPoints, ss.cards, ss.oRock, ss.oPaper, ss.oScissor))
             states.append(RRSPState(ss.myPoints, [ss.oPoints[0] + 1, ss.oPoints[1], ss.oPoints[2]], ss.cards, ss.oRock, ss.oPaper, ss.oScissor))       #all losses



        return states

class RewardModel(pomdp_py.RewardModel):
    def _reward_func(self, state, action, next_state):

        if action.name[5:] not in state.cards:
            return -9999999

        if isinstance(next_state, RRSPObservation):
            if next_state.name == "rock":
                if action.name == "play_rock":
                    return 0
                elif action.name == "play_paper":
                    return 10
                elif action.name == "play_scissor":
                    return -20
            elif next_state.name == "paper":
                if action.name == "play_rock":
                    return -20
                elif action.name == "play_paper":
                    return 0
                elif action.name == "play_scissor":
                    return 10
            elif next_state.name == "scissor":
                if action.name == "play_rock":
                    return 10
                elif action.name == "play_paper":
                    return -20
                elif action.name == "play_scissor":
                    return 0
            
        oNextRock = next_state.oPoints[0]
        oNextPaper = next_state.oPoints[1]
        oNextScissors = next_state.oPoints[2]
        
        oRock = state.oPoints[0]
        oPaper = state.oPoints[1]
        oScissors = state.oPoints[2]

        myRock = state.myPoints[0]
        myPaper = state.myPoints[1]
        myScissors = state.myPoints[2]

        myNextRock = next_state.myPoints[0]
        myNextPaper = next_state.myPoints[1]
        myNextScissors = next_state.myPoints[2]

        # In our version of RRPS, we have made the win condition more challenging than the typical best of 3. 
        # A player can only win upon winning using the same type 3 times (over the course of the game) 
        # or winning at least once with every type. 
        # In terms of deck of cards, the player draws a hand of 5 cards each labelled with one of the three RPS types. 

        opponent_about_to_win = any(win == 2 for win in state.oPoints) or all(win >= 1 for win in state.oPoints)
        robot_about_to_win = any(win == 2 for win in state.myPoints) or all(win >= 1 for win in state.myPoints)

        if opponent_about_to_win:
            if action.name == "play_rock":
                if oNextPaper == oPaper + 1 and oNextPaper == 3:
                    return -500  # robot loses this round and the game
                elif oNextPaper == 1 and oRock == 1 and oScissors == 1:
                    return -500 # robot loses this round and the game
                else:
                    return 100  # other cases not leading robot to lose the game
            elif action.name == "play_paper":
                if oNextScissors == oScissors + 1 and oNextScissors == 3:
                    return -500  # robot loses this round and the game
                elif oNextScissors == 1 and oPaper == 1 and oRock == 1:
                    return -500 # robot loses this round and the game
                else:
                    return 100  # other cases not leading robot to lose the game
            elif action.name == "play_scissor":
                if oNextRock == oRock + 1 and oNextRock == 3:
                    return -500 # robot loses this round and the game
                elif oNextRock == 1 and oScissors == 1 and oPaper == 1:
                    return -500  # robot loses this round and the game
                else:
                    return 100  # other cases not leading robot to lose the game
            else:
                return 1  # default case for debugging
        elif robot_about_to_win:
            if action.name == "play_rock":
                if myRock == 0 and myNextRock == 1 or myNextRock == 3:
                    return 200 # robot wins the game
                else:
                    return 0 # other cases not leading robot to win the game
            elif action.name == "play_paper":
                if myPaper == 0 and myNextPaper == 1 or myNextPaper == 3:
                    return 200
                else:
                    return 0 # other cases not leading robot to win the game
            elif action.name == "play_scissor":
                if myScissors == 0 and myNextScissors == 1 or myNextScissors == 3:
                    return 200
                else:
                    return 0 # other cases not leading robot to win the game
            else:
                return 1.0001  # default case
        else:
            if myPaper == 0 and myNextPaper == 1 or myRock == 0 and myNextRock == 1 or myScissors == 0 and myNextScissors == 1:
                return 100
            elif myPaper == 1 and myNextPaper == 2 or myRock == 1 and myNextRock == 2 or myScissors == 1 and myNextScissors == 2:
                return 200
            elif oPaper == 0 and oNextPaper == 1 or oRock == 0 and oNextRock == 1 or oScissors == 0 and oNextScissors == 1:
                return -200
            elif oPaper == 1 and oNextPaper == 2 or oRock == 1 and oNextRock == 2 or oScissors == 1 and oNextScissors == 2:
                return -300
            else:
                return 1.0000000001 # default case
    
    def sample(self, state, action, next_state):
        return self._reward_func(state, action, next_state)

# Policy Model
class PolicyModel(pomdp_py.RolloutPolicy): #TODO: just a placeholder for now
    """A simple policy model with uniform prior over a
       small, finite action space"""
    ACTIONS = [RRSPAction("play_rock"), RRSPAction("play_paper"), RRSPAction("play_scissor")]

    def sample(self, state):
        return random.sample(self.get_feasible_actions(state), 1)[0]

    def rollout(self, state, history=None):
        """Treating this PolicyModel as a rollout policy"""
        return self.sample(state)

    def probability(self, action, state):
        uniqueCards = len(set(state.cards))
        if action.name[5] in state.cards:
            return 1/uniqueCards
        else:
            return 0

    def get_feasible_actions(self, state):
        actions = []
        if "rock" in state.cards:
            actions.append(self.ACTIONS[0])
        if "paper" in state.cards:
            actions.append(self.ACTIONS[1])
        if "scissor" in state.cards:
            actions.append(self.ACTIONS[2])
        return actions

    def get_all_actions(self, state, history=None):
        return self.get_feasible_actions(state)



class RRSPProblem(pomdp_py.POMDP):

    def __init__(self,init_true_state, init_belief):
        #defining the agent
        agent = pomdp_py.Agent(init_belief,
                               PolicyModel(),
                               TransitionModel(),
                               ObservationModel(init_true_state),
                               RewardModel())        
        
        #defining the environment
        env = pomdp_py.Environment(init_true_state, TransitionModel(), RewardModel())
        
        super().__init__(agent, env, name = "RRSPPRroblem")


def test_planner(rrsp_problem, planner, debug_tree = False):
    
    action = planner.plan(rrsp_problem.agent)
    if debug_tree:
        from pomdp_py.utils import TreeDebugger
        dd = TreeDebugger(rrsp_problem.agent.tree)
        import pdb; pdb.set_trace()

    true_state = rrsp_problem.env.state

    print("True State:", rrsp_problem.env.state) # Current True State
    #print("Belief:", str(rrsp_problem.agent.cur_belief)) # Current Belief
    print("Action:", action.name)

    # reward = max([rrsp_problem.env.reward_model.sample(rrsp_problem.env.state, action, next_state) for next_state in rrsp_problem.agent.transition_model.get_all_states()])

    # Calculate the true state change
    real_observation = RRSPObservation("rock","rock")
    actionInd = standard.index(action.name[5])


   # print("Reward:", reward)

    print(action.name[5])
    print(real_observation.name[0])

    if ((actionInd+2) % 3) == (standard.index(real_observation.name[0])):
        next_state = true_state
        next_state.myPoints[standard.index(action.name[5])] += 1
        print("I won")
    elif ((actionInd+1) % 3) == (standard.index(real_observation.name[0])):
        next_state = true_state
        next_state.oPoints[standard.index(real_observation.name[0])] += 1
        print("I lost")
    else:
        next_state = true_state
        print("draw")

    # --- Card Replacement --- #
    next_state.cards.remove(action.name[5:])
    if actionInd == 0:
        next_state.oRock += 1
    elif actionInd == 1:
        next_state.oPaper += 1
    else:
        next_state.oScissor += 1

    #newCard = random.choice(rrsp_problem.agent.observation_model.get_all_observations())

    probabilities = [(10-next_state.oRock)/(30 - (next_state.oRock + next_state.oPaper + next_state.oScissor)),
                     (10-next_state.oPaper)/(30 - (next_state.oRock + next_state.oPaper + next_state.oScissor)),
                     (10-next_state.oScissor)/(30 - (next_state.oRock + next_state.oPaper + next_state.oScissor))]

    newCard = random.choices(["rock","paper","scissor"], probabilities)[0]


    next_state.cards.append(newCard)
    if newCard[0] == 'r':
        next_state.oRock += 1
    elif newCard[0] == 'p':
        next_state.oPaper += 1
    else:
        next_state.oScissor += 1

    if real_observation.name[0] == 'r':
        next_state.oRock += 1
    elif real_observation.name[0] == 'p':
        next_state.oPaper += 1
    else:
        next_state.oScissor += 1

    # --- ---------- --- #

    # Reward based on how well it actually did
    # true_reward = rrsp_problem.env.state_transition(action, execute=True)
    # print("True Reward:", true_reward)

    global ss
    ss = next_state

    rrsp_problem.env.apply_transition(next_state)
    print("New State:", rrsp_problem.env.state)

    #real_observation = rrsp_problem.env.observation_model.sample(rrsp_problem.env.state, action)
    #real_observation = random.choice(rrsp_problem.agent.observation_model.get_all_observations())
    print("Observation:", real_observation.name)
    rrsp_problem.agent.update_history(action, real_observation)

    # Save the state
    saved_state = rrsp_problem.env.state

    #Update Belief
    #planner.update(rrsp_problem.agent, action, real_observation)
    belief = pomdp_py.update_histogram_belief(rrsp_problem.agent.cur_belief, action, real_observation, rrsp_problem.agent.observation_model, rrsp_problem.agent.transition_model)
    rrsp_problem.agent.set_belief(pomdp_py.Particles.from_histogram(belief, num_particles=100), prior=False)

    print(rrsp_problem.agent.belief)


    if isinstance(planner, pomdp_py.POUCT):
        #print("Num sims:", planner.last_num_sims)
        print("Plan time: %2f" % planner.last_planning_time)

    if isinstance(rrsp_problem.agent.cur_belief, pomdp_py.Histogram):
        new_belief = pomdp_py.update_histogram_belief(
            rrsp_problem.agent.cur_belief,
            action, real_observation, rrsp_problem.agent.observation_model,
            rrsp_problem.agent.transition_model
        )
        rrsp_problem.agent.set_belief(new_belief)
    rrsp_problem.agent.observation_model.update_state(saved_state)
    return saved_state
            
def initialize_state():
    global ss
    ss = RRSPState([0,0,0], [0,0,0], ["rock", "rock", "paper", "paper", "scissor"], 2, 2, 1)
    return ss

def main():
    init_true_state = initialize_state() 
    init_belief = pomdp_py.Histogram({init_true_state: 1.0}) 
    rrspproblem = RRSPProblem(init_true_state, init_belief)

    # Reset agent belief
    rrspproblem.agent.set_belief(pomdp_py.Particles.from_histogram(init_belief, num_particles=100), prior=False)

    print("\n** Testing POUCT **")
    pouct = pomdp_py.POMCP(max_depth=5, discount_factor=0.95,
                           num_sims=8192, exploration_const=50,
                           rollout_policy=rrspproblem.agent.policy_model,
                           show_progress=True)

    test_planner(rrspproblem, pouct)
    test_planner(rrspproblem, pouct)
    test_planner(rrspproblem, pouct)
    test_planner(rrspproblem, pouct)
    test_planner(rrspproblem, pouct)
    test_planner(rrspproblem, pouct)
    test_planner(rrspproblem, pouct)
    test_planner(rrspproblem, pouct)
    test_planner(rrspproblem, pouct)
    test_planner(rrspproblem, pouct)
    test_planner(rrspproblem, pouct)
    test_planner(rrspproblem, pouct)
    #TreeDebugger(rrspproblem.agent.tree).pp

if __name__ == '__main__':
    main()

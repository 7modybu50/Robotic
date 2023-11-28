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
        if (sum(end_state.myPoints) > sum(start_state.myPoints)): # player wins in end_state, opponent loses
            opp_action = (standard.index(action[5]) + 1) % 3
        elif (sum(end_state.oPoints) > sum(start_state.oPoints)): # opponent wins in end_state, player loses
            opp_action = (standard.index(action[5]) + 2) % 3
        else:
            opp_action = standard.index(action[5])

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
        opp_win_closeness = max((start_state.opp_points[opp_action] / 3), spread_win_closeness)

        #(2)
        #Get highest point win type
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

        prime_prob = defense_effect / (num_x_unobserved / remaining_cards) #(3)
        return prime_prob

class RewardModel(pomdp_py.RewardModel):
    def _reward_func(self, state, action, next_state):

        # ignore variable names for now
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
                return 0  # default case
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
            if myPaper == 0 and myNextPaper == 1 or myRock == 0 and myNextRock == 1 or myScissors == 0 and myNextScissors == 1:
                return 100
            elif myPaper == 1 and myNextPaper == 2 or myRock == 1 and myNextRock == 2 or myScissors == 1 and myNextScissors == 2:
                return 200
            elif oPaper == 0 and oNextPaper == 1 or oRock == 0 and oNextRock == 1 or oScissors == 0 and oNextScissors == 1:
                return -200
            elif oPaper == 1 and oNextPaper == 2 or oRock == 1 and oNextRock == 2 or oScissors == 1 and oNextScissors == 2:
                return -300
            else:
                return 0
    
    def sample(self, state, action, next_state):
        return self._reward_func(state, action)



# class RewardModel(pomdp_py.RewardModel):
#     def _reward_func(self, state, action, next_state):
    
#         ROBOT_WIN_REWARD = 200
#         ROBOT_LOSE_PENALTY = -500
#         FIRST_POINT_REWARD = 100
#         SECOND_POINT_REWARD = 200
#         OPPONENT_FIRST_POINT_PENALTY = -200
#         OPPONENT_SECOND_POINT_PENALTY = -300

#         opponent_about_to_win = self.is_about_to_win(state.oPoints)
#         robot_about_to_win = self.is_about_to_win(state.myPoints)

#         action_to_points = {"play_rock": 0, "play_paper": 1, "play_scissors": 2}
#         action_index = action_to_points[action.name]

#         if opponent_about_to_win:
#             if next_state.oPoints[action_index] == state.oPoints[action_index] + 1 and next_state.oPoints[action_index] == 3:
#                 return ROBOT_LOSE_PENALTY
#             elif next_state.oPoints[action_index] == 1 and all(point == 1 for point in state.oPoints):
#                 return ROBOT_LOSE_PENALTY
#             else:
#                 return FIRST_POINT_REWARD
#         elif robot_about_to_win:
#             if state.myPoints[action_index] == 0 and next_state.myPoints[action_index] == 1 or next_state.myPoints[action_index] == 3:
#                 return ROBOT_WIN_REWARD
#             else:
#                 return 0
#         else:
#             if state.myPoints[action_index] == 0 and next_state.myPoints[action_index] == 1:
#                 return FIRST_POINT_REWARD
#             elif state.myPoints[action_index] == 1 and next_state.myPoints[action_index] == 2:
#                 return SECOND_POINT_REWARD
#             elif state.oPoints[action_index] == 0 and next_state.oPoints[action_index] == 1:
#                 return OPPONENT_FIRST_POINT_PENALTY
#             elif state.oPoints[action_index] == 1 and next_state.oPoints[action_index] == 2:
#                 return OPPONENT_SECOND_POINT_PENALTY
#             else:
#                 return 0
            
#     @staticmethod
#     def is_about_to_win(points):
#         return any(point == 2 for point in points) or all(point >= 1 for point in points)


    # def sample(self, state, action, next_state):
    #     return self._reward_func(state, action, next_state)

class RRSPProblem(pomdp_py.POMDP):

    def __init__(obs_state, init_true_state, init_belief):
        #defining the agent
        agent = pomdp_py.Agent(init_belief, ObservationModel(obs_state), TransitionModel(),RewardModel(),PolicyModel())
        
        #defining the environment
        env = pomdp_py.Environment(init_true_state, TransitionModel(), RewardModel())
        
        super__init__(agent, env, name = "RRSPPRroblem")
    
    def update_observation_model(self, new_obs_state,obs_state, init_true_state, init_belief):
        self.agent.observation_model = ObservationModel(new_obs_state)
        problem = RRSPProblem(obs_state, init_true_state, init_belief)
        # After the agent observes a new state
        problem.update_observation_model(new_obs_state)

def test_planner(rrsp_problem, planner, nsteps = , debug_tree = False):
    for i in range(nsteps):
        action = planner,plan(rrsp_problem)
        if debug_tree:
            from pomdp_py.utils import TreeDebugger
            dd = TreeDebugger(rrsp_problem.agent.tree)
            import pdb; pdb.set_trace()

        print("==== Step %d ====" % (i+1))
        print("True State:", rrsp_problem.env.state)
        print("Belief State:", rrsp_problem.agent.belief)
        print("Action:", action)

        reward = rrsp_problem.env.reward_model.sample(rrsp_problem.env.state, action, None)
        print("Reward:", reward)

        #Update Belief
        planner.update_belief(rrsp_problem.agent, action, real_observation)
        if isinstance(planner, pomdp_py.POUCT):
            print("Num sims:", planner.last_num_sims)
            print("Plan time: %5f" % planner.last_plan_time)

        if isinstance(rrsp_problem.agent.cur_belief, pomdp_py.Histogram):
            new_belief = pomdp_py.update_histogram_belief(
                rrsp_problem.agent.cur_belief,
                action, real_observation, rrsp_problem.agent.observation_model,
                rrsp_problem.agent.transition_model
            )
            rrsp_problem.agent.set_belief(new_belief)

        if action.name.startswith("play"):
            print("\n")


def main():
    init_true_state = 
    init_belief = 
    rrspproblem = RRSPProblem(init_true_state, init_belief)
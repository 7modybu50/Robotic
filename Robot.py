import pomdp_py


class RRSPState(pomdp_py.State):
    def __init__(self, myPoints, oPoints):
        self.myPoints = myPoints  # the robot's points
        self.oPoints = oPoints  # the opponent's points

    def __str__(self):
        return "My points:\nrocks: " + str(self.myPoints[0]) + ", papers: " + str(
            self.myPoints[1]) + ", scissors: " + str(self.myPoints[2]) + "Opponent's points:\nrocks: " + str(
            self.oPoints[0]) + ", papers: " + str(self.oPoints[1]) + ", scissors: " + str(self.oPoints[2])


class RRSPAction(pomdp_py.Action):
    def __init__(self, name):
        self.name = name

    def __eq__(self, other):
        if isinstance(other, RRSPAction):
            return self.name == other.name


class RRSPObservation(pomdp_py.Observation):
    def __init__(self, name):
        self.name = name

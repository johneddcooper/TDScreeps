from screep import REDTEAM, BLUETEAM
from copy import deepcopy
class CombatSim:

    def __init__(self):
        self.screeps = []

    def add_screep(self, screep):
        self.screeps.append(screep)

    def simulate(self, timeout = 100):
        histogram = []
        histogram.append(deepcopy(self.screeps))
        for _ in range(timeout):
            alive_screeps = [screep for screep in self.screeps if screep.hp > 0]
            for screep in self.screeps:
                screep.set_target(self.screeps)
            for screep in self.screeps:
                screep.attack(self.screeps)
            for screep in self.screeps:
                screep.set_target(self.screeps)
            for screep in self.screeps:
                screep.move(self.screeps)

            histogram.append(deepcopy(self.screeps))

            red_screeps = 0
            blue_screeps = 0
            for screep in [screep for screep in self.screeps if screep.hp > 0]:
                if screep.team == REDTEAM:
                    red_screeps += 1
                else:
                    blue_screeps += 1
            if red_screeps == 0 or blue_screeps == 0:
                break
                
        return histogram
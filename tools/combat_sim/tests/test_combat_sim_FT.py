import sys
sys.path.append('./')

from screep import REDTEAM, BLUETEAM
import screep
import pytest
from screep import Screep

from combat_sim import CombatSim

def test_determine_one_on_one_winner():

    # We want to determine who would win in a one on one fight

    # We make two screeps. A slow melee screep and a slow ranged screep, with closest screep as a target (default)
    
    melee_screep = Screep(REDTEAM, 10, move=1, melee_att=2, move_func=screep.maint_dist_to_target) 
    ranged_screep = Screep(BLUETEAM, 0, move=1, range_att=2, move_func=lambda self, screeps:screep.maint_dist_to_target(self, screeps, 3))

    # We run the sim and see the ranged screep wins (by kiting)
    sim = CombatSim()
    sim.add_screep(melee_screep)
    sim.add_screep(ranged_screep)

    # We get the results
    results = sim.simulate()
    # Assert first screep is alive, second is dead
    assert results[-1][0].hp <= 0
    assert results[-1][1].hp > 0

    # We get a graph of posn, dmg, and hp over time
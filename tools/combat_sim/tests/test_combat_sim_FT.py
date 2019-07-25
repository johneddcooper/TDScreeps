import sys
sys.path.append('./')

from screep import REDTEAM, BLUETEAM

import pytest
from screep import Screep
def test_determine_one_on_one_winner():

    # We want to determine who would win in a one on one fight

    # We make two screeps. A slow melee screep and a slow ranged screep, with closest screep as a target (default)
    
    melee_screep = Screep(RED_TEAM, 10, move=2, melee_att=4)
    ranged_screep = Screep(BLUE_TEAM, 0, move=1, range_att=2)

    # We set these screeps up at a distance apart

    # We run the sim and see the ranged screep wins (by kiting)

    # We get a graph of posn, dmg, and hp over time
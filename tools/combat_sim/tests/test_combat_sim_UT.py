import sys
sys.path.append('./')

from screep import BLUETEAM, REDTEAM
from screep import Screep
import screep
import combat_sim
import pytest

def test_screep_inits_with_proper_values():
    s = Screep(REDTEAM, 10, move=5, melee_att=1)
    assert s.team == REDTEAM
    assert s.posn == 10
    assert s.move_mods == 5
    assert s.speed == 5

def test_screeps_init_with_uuid():
    s1 = Screep(REDTEAM, 0)
    s2 = Screep(REDTEAM, 0)
    assert s1.uuid
    assert s1.uuid != s2.uuid

def test_screep_eq_uses_uuid():
    s1 = Screep(REDTEAM, 0)
    s2 = Screep(REDTEAM, 0)
    assert s1 ==  s1
    assert s1 != s2

def test_closest_to_target_selector_targets_closest_with_one_en():
    melee_screep = Screep(REDTEAM, 10, move=2, melee_att=4)
    ranged_screep = Screep(BLUETEAM, 0, move=1, range_att=2)

    screeps = [melee_screep, ranged_screep]

    melee_screep.set_target(screeps)
    ranged_screep.set_target(screeps)

    assert melee_screep.target == ranged_screep.uuid
    assert ranged_screep.target == melee_screep.uuid

def test_closest_to_target_selector_targets_closest_with_mult_en():
    en_melee_screep = Screep(REDTEAM, 10, move=2, melee_att=4)
    en_ranged_screep = Screep(REDTEAM, 11, move=1, range_att=2)
    
    ranged_screep = Screep(BLUETEAM, 0, move=1, range_att=2)
    
    screeps = [en_melee_screep, en_ranged_screep, ranged_screep]

    en_melee_screep.set_target(screeps)
    en_ranged_screep.set_target(screeps)
    ranged_screep.set_target(screeps)

    assert en_melee_screep.target == ranged_screep.uuid
    assert en_ranged_screep.target == ranged_screep.uuid
    assert ranged_screep.target == en_melee_screep.uuid
    
def test_screep_remains_same_posn_with_default_move_func():
    screep = Screep(0, REDTEAM, move = 2)
    screep.move([screep])
    assert screep.posn == 0

def test_screep_move_updates_posn():
    screep = Screep(0, REDTEAM, move = 1, move_func=lambda self, screeps: self.posn + self.speed)
    screep.move([screep])
    assert screep.posn == 1
    screep.move([screep])
    assert screep.posn == 2

def test_maint_dist_to_target_moves_closer_with_pos_numbers():
    s1 = Screep(REDTEAM, 0,move=1, move_func=screep.maint_dist_to_target)
    s2 = Screep(BLUETEAM, 10)
    s1.set_target([s1,s2])
    s1.move([s1, s2])
    assert s1.posn == 1

def test_maint_dist_to_target_moves_closer_with_pos_numbers():
    s1 = Screep(REDTEAM, -1,move=1, move_func=screep.maint_dist_to_target)
    s2 = Screep(BLUETEAM, -10)
    s1.set_target([s1,s2])
    s1.move([s1, s2])
    assert s1.posn == -2

def test_maint_dist_moves_multi_screeps_complex_posns():
    s1 = Screep(REDTEAM, 0, move=1, move_func=screep.maint_dist_to_target)
    s2 = Screep(REDTEAM, -10, move=2, move_func=screep.maint_dist_to_target)
    s3 = Screep(BLUETEAM, 20, move=1, move_func=screep.maint_dist_to_target)
    s4 = Screep(BLUETEAM, -40, move=.5, move_func=screep.maint_dist_to_target)
    screeps = [s1, s2, s3, s4]
    for s in screeps:
        s.set_target(screeps)
        s.move(screeps)
    assert s1.posn == 1
    assert s2.posn == -8
    assert s3.posn == 19
    assert s4.posn == -40
    for s in screeps:
        s.move(screeps)
    assert s1.posn == 2
    assert s2.posn == -6
    assert s3.posn == 18
    assert s4.posn == -39

def test_screep_maints_distance_from_approching_target():
    s1 = Screep(REDTEAM, 8, move=1, move_func=lambda self, screeps:screep.maint_dist_to_target(self, screeps, 6))
    s2 = Screep(BLUETEAM, 0, move=1, move_func=screep.maint_dist_to_target)
    screeps = [s1, s2]
    s1.set_target(screeps)
    s2.set_target(screeps)
    s1.move(screeps)
    s2.move(screeps)
    assert s1.posn == 7
    assert s2.posn == 1
    s1.move(screeps)
    s2.move(screeps)
    assert s1.posn == 7
    assert s2.posn == 2
    s1.move(screeps)
    s2.move(screeps)
    assert s1.posn == 8
    assert s2.poan == 3
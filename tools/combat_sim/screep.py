BLUETEAM = True
REDTEAM = False

import uuid
import math

def target_closest_to(self, screeps):
    screeps = [screep for screep in screeps if screep.team != self.team]
    return min(screeps, key=lambda screep: abs(screep.posn - self.posn))

def maint_dist_to_target(self, screeps, dist=1):
    screeps = dict([(screep.uuid,screep) for screep in screeps])
    delta = screeps[self.target].posn - self.posn
    print(self.uuid, self.posn, screeps[self.target].posn, delta)
    if delta >= 0: # target is to right of us
        # 20 - 10 = 10
        # -10 - -20 = 10
        move = delta - dist # Subtract target dist from distance to target to get desired move 
        # 10 - 8 = 2, move right 2
        # 10 - 12 = -2, move left 2
    if delta < 0: # Target is to left of us
        #print(move, self._posn + min(self.speed, abs(move)))
        #return self._posn + min(self.speed, abs(move))
        move = delta + dist

    if self.speed < abs(move):
        if move < 0:
            move = -self.speed
        if move > 0:
            move = self.speed

    return self._posn + move
        

# Issue: Attempting to move 1 right moves 1 left

class Screep:

    move_mods = 0
    work_mods = 0
    carry_mods = 0
    heal_mods = 0
    range_att_mods = 0
    melee_att_mods = 0
    armor_mods = 0
    friendly = False
    temp_hp = 100
    uuid = None
    target_func = None
    move_func = None
    target = None   
    _posn = None 

    @property
    def hp(self):
        return temp_hp + armor * 50

    @property
    def melee_dmg(self):
        return self.melee_att

    @property
    def weight(self):
        return 0
        #return int(sum([self.move_mods, self.work_mods, self.carry_mods, self.heal_mods, self.range_att_mods, self.melee_att_mods, self.armor_mods * 2])/2)

    @property
    def speed(self):
        return self.move_mods - self.weight

    @property
    def posn(self):
        return math.floor(self._posn)

    def __init__(self, team:bool, posn:int, move=0, work=0, carry=0, heal=0, melee_att=0, range_att=0, armor=0, target_func=target_closest_to, move_func=lambda self, _: self.posn):
        # if posn < 0:
        #     raise Exception('Posn must by >= 0')
        self._posn = posn
        self.team = team
        self.move_mods = move
        self.work_mods = work
        self.carry_mods = carry
        self.heal_mods = heal
        self.range_att_mods = range_att
        self.armor_mods = armor
        self.uuid = str(uuid.uuid4())
        self.target_func = target_func 
        self.move_func = move_func

    def __repr__(self):
        return self.uuid

    def set_target(self, screeps):
        self.target = self.target_func(self, screeps).uuid

    def move(self, screeps):

        self._posn = self.move_func(self, screeps)


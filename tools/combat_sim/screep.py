BLUETEAM = True
REDTEAM = False
MELEE_ATT_RANGE=1
RANGED_ATT_RANGE=3
MELEE_ATT_DMG = 30
RANGED_ATT_DMG = 10
BASE_HP = 50

import uuid
import math

def target_closest_to(self, screeps):
    screeps = [screep for screep in screeps if screep.team != self.team]
    return min(screeps, key=lambda screep: abs(screep.posn - self.posn))

def maint_dist_to_target(self, screeps, dist=1):
    screeps = dict([(screep.uuid,screep) for screep in screeps])
    delta = screeps[self.target].posn - self.posn
    if delta >= 0: # target is to right of us
        # 20 - 10 = 10
        # -10 - -20 = 10
        move = delta - dist # Subtract target dist from distance to target to get desired move 
        # 10 - 8 = 2, move right 2
        # 10 - 12 = -2, move left 2
        
    if delta < 0: # Target is to left of us
        # 10 - 20 = -10
        # -20 - -10 = -10 
        move = delta + dist # Add target dist from distance to target to get desired move
        # -10 + 8 = -2 # move left 2

        #print(move, self._posn + min(self.speed, abs(move)))
    if move > 0: #move right
        return self._posn + min(self.speed, move)

    if move < 0: #move left
        return self._posn + max(-self.speed, move)

    return self._posn

class Screep:

    move_mods = 0
    work_mods = 0
    carry_mods = 0
    heal_mods = 0
    range_att_mods = 0
    melee_att_mods = 0
    armor_mods = 0
    friendly = False
    hp = 100
    uuid = None
    target_func = None
    move_func = None
    target = None   
    _posn = None 

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
        self.hp = BASE_HP + armor*50

    def __repr__(self):
        return self.uuid

    def set_target(self, screeps):
        self.target = self.target_func(self, screeps).uuid

    def move(self, screeps):
        if self.hp <= 0:
            return False
        self._posn = self.move_func(self, screeps)

    def attack(self, screeps):
        if self.hp <= 0:
            return False
        target = dict([(screep.uuid,screep) for screep in screeps]).get(self.target)
        range_to_target = abs(abs(self.posn)-abs(target.posn))
        if self.melee_att_mods > 0 and range_to_target <= MELEE_ATT_RANGE:
            target.hp -= self.melee_att_mods * MELEE_ATT_DMG
            target.attack_back(self)
        if self.range_att_mods > 0 and range_to_target <= RANGED_ATT_RANGE:
            target.hp -= self.range_att_mods * RANGED_ATT_DMG
    
    def attack_back(self, screep):
        if self.hp > 0:
            screep.hp -= self.melee_att_mods * MELEE_ATT_DMG

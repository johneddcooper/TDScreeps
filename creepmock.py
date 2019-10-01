from definitions import C

def creep_cost(parts: list) -> int:
    cost = 0
    print(parts)
    for part in parts:
        print(part)
        if part not in [C.WORK, C.MOVE, C.CARRY, C.ATTACK, C.RANGED_ATTACK, C.TOUGH, C.HEAL]:
            raise Exception('Invalid Part')
        cost += C.BODYPART_COST[part]
    return cost

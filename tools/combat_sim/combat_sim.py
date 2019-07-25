class combat:

    screeps = []

    def add_screep(screep):
        screeps.append(screep)

    def simulate(ticks = 0):
        for screep in screeps:
            screep.simulate(screeps)

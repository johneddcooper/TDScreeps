import sys
sys.path.append('C:/Users/John/Documents/Programming/TDScreeps')
from src.gamebridge import gamebridge

def test_can_start_test_colony():
    
    # We get a WorldBridge for a new test world
    game = gamebridge.new_test_game()
    # Starting in an empty room, the planner gets a model of the world

    # The planner sees there is no spawner

    # The planner determines the best place for a spawner and places one in the world
    
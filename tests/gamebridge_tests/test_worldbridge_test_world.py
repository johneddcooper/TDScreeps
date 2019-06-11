import sys
sys.path.append('C:/Users/John/Documents/Programming/TDScreeps')
from src.gamebridge import gamebridge

def test_new_test_world_returns_gamebridge():
    assert gamebridge.new_test_game() is not None


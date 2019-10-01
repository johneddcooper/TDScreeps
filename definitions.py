import os
import sys

sys.path.append('./py-screeps-server-mockup')
sys.path.append('./screeps-starter-python/src/defs')

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
from pybridge import PyBridge
import constants as C
import creepmock
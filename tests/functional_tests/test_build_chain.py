sys.path.append("./")
from definitions import ROOT_DIR

import pytest
import pyjs_compiler as pjc

def test_compile_main_from_string():
    # We have a bit of test code as a string to compile
    
    src = """ 
    def main():
    # Main game logic loop.
        print("Echobot_string!")
    """

    # We pass it to pyjs_compiler as an adhoc build
    pjc.


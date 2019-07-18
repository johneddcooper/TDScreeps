import sys
sys.path.append("./")
from definitions import ROOT_DIR
from definitions import PyBridge


import pytest
import pyjs_compiler as pjc


def test_compile_main_from_valid_string():
    # We have a bit of test code as a string to compile
    
    src = """ 
def main():
# Main game logic loop.
    console.log('Tickbot buildchain!',Game.time);
"""

    # We pass it to pyjs_compiler as an adhoc build
    js_src = pjc.compile_from_string(src)

    # The compiler compiles it to JS and returns it as a string, which contains our test print statement
    assert "Tickbot buildchain!" in js_src

    # We create a server mockup instance
    bridge = PyBridge()
    bridge._start_jsbridge()
    bridge.make_stub_world()
    
    # We pass this string to the server as a bot
    bridge.add_bot('TickBot', 'W0N1', 15, 15, js_src)
   
    # We tick the server one time and get a reply
    bridge.start_server()
    response = bridge.tick(ticks = 1)

    # We get one return log
    assert len(response) == 1

    # The reply had no errors
    assert "Error" not in response[0]['logs']['notification_logs']['TickBot']

    # The reply had the output we expected from the running JS code
    assert 'Echobot_string!' in response[0]['logs']['bot_logs']['TickBot']

    # We tick the server a few more times
    response = bridge.tick(ticks = 2)

    # We get two logs back
    assert len(response) == 2

    # The reply had no errors
    assert "Error" not in response[0]['logs']['notification_logs']['TickBot']
    assert "Error" not in response[1]['logs']['notification_logs']['TickBot']

    # The reply had the output we expected from the running JS code for both ticks
    assert 'Echobot_string!' in response[0]['logs']['bot_logs']['TickBot']
    assert 'Echobot_string!' in response[1]['logs']['bot_logs']['TickBot']

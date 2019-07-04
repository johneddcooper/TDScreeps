import sys
import os
sys.path.append('../../')
from definitions import ROOT_DIR
sys.path.append(os.path.join(ROOT_DIR, 'py-screeps-server-mockup'))

import time
import subprocess
from pybridge import PyBridge
import pytest
import json

from pprint import pprint

@pytest.fixture()
def pyjsbridge():
    bridge = PyBridge()
    bridge._start_jsbridge()
    time.sleep(0.1)
    yield bridge
    time.sleep(0.1)
    bridge._stop_jsbridge()
    time.sleep(0.1)

def test_can_start_stop_jsbridge_process():
    pyb = PyBridge()
    pyb._start_jsbridge()
    time.sleep(0.1)
    assert pyb.jsbridge_process != None
    pyb._stop_jsbridge()
    time.sleep(0.2)
    assert pyb.jsbridge_process.poll() != None
    assert pyb.jsbridge_process.returncode == 0

def test_jsbridge_echos_JSON_on_root(pyjsbridge):
    r = pyjsbridge._msg_jsbridge({"msg": "MsgString"})
    assert r.status_code == 200
    assert r.json() == {"msg": "MsgString"}

def test_jsbridge_returns_200_when_reset_world(pyjsbridge):
    assert pyjsbridge.reset_world() == True

def test_get_world_load(pyjsbridge):
    load = pyjsbridge.get_world_load()
    assert 'rooms' in load['db']

def test_create_stub_world(pyjsbridge):
    pyjsbridge.make_stub_world()
    rooms = pyjsbridge.get_all_rooms()
    assert 'W2N2' in [room['_id'] for room in rooms] 

def test_create_blank_room(pyjsbridge):
    pyjsbridge.reset_world()
    room_name = "T3S7"
    assert pyjsbridge.add_room(room_name) == True
    assert room_name in [room['_id'] for room in pyjsbridge.get_all_rooms()]

def test_start_server(pyjsbridge):
    pyjsbridge.make_stub_world()
    assert pyjsbridge.start_server() == True

def test_tick_server_once(pyjsbridge):
    pyjsbridge.make_stub_world()
    pyjsbridge.start_server()
    response = pyjsbridge.tick()
    assert len(response) == 1
    assert 'gametime' in response[0]
    assert response[0]['gametime'] == 2
    
def test_tick_server_multi(pyjsbridge):
    pyjsbridge.make_stub_world()
    pyjsbridge.start_server()
    r = pyjsbridge.tick(ticks = 5)
    assert len(r) == 5
    assert r[0]['gametime'] == 2
    assert r[4]['gametime'] == 6

def test_add_bot_to_server(pyjsbridge):
    pyjsbridge.make_stub_world()
    assert pyjsbridge.add_bot('TickBot', 'W0N1', 15, 15, "function () {console.log('TickBot_out!',Game.time);") == True
    
def test_capture_single_bot_logs_on_tick(pyjsbridge):
    pyjsbridge.reset_world()
    pyjsbridge.make_stub_world()
    pyjsbridge.add_bot('TickBot', 'W0N1', 15, 15, """function () {\n    console.log('TickBot_out!',Game.time);\n}""")
    pyjsbridge.start_server()
    response = pyjsbridge.tick(ticks = 3)
    assert len(response) == 3
    assert len(response[0]['logs']['bot_logs']) == 1
    assert 'TickBot_out' in response[0]['logs']['bot_logs']['TickBot'][0]
    assert 'TickBot_out' in response[2]['logs']['bot_logs']['TickBot'][0]

def test_capture_single_bot_multiple_logs_on_tick(pyjsbridge):
    pyjsbridge.reset_world()
    pyjsbridge.make_stub_world()
    pyjsbridge.add_bot('TickBot', 'W0N1', 15, 15, """function () {\n    console.log('TickBot_out 0');\n    console.log('TickBot_out 1');\n}""")
    pyjsbridge.start_server()
    response = pyjsbridge.tick(ticks = 3)
    assert len(response) == 3
    assert len(response[0]['logs']['bot_logs']) == 1
    assert len(response[0]['logs']['bot_logs']['TickBot']) == 2
    assert 'TickBot_out 0' in response[0]['logs']['bot_logs']['TickBot'][0]
    assert 'TickBot_out 1' in response[2]['logs']['bot_logs']['TickBot'][1]

def test_capture_multiple_bot_logs_on_tick(pyjsbridge):
    pyjsbridge.reset_world()
    pyjsbridge.make_stub_world()
    pyjsbridge.add_bot('TickBot1', 'W0N1', 15, 15, """function () {\n    console.log('TickBot1 output',Game.time);\n}""")
    pyjsbridge.add_bot('TickBot3', 'W1N2', 15, 15, """function () {\n    console.log('TickBot3 output',Game.time);\n}""")
    pyjsbridge.add_bot('TickBot2', 'W0N2', 15, 15, """function () {\n    console.log('TickBot2 output',Game.time);\n}""")
    
    pyjsbridge.start_server()
    response = pyjsbridge.tick(ticks = 1)
    assert len(response) == 1
    assert len(response[0]['logs']['bot_logs']) == 3
    print(response)
    assert 'TickBot1 output' in response[0]['logs']['bot_logs']['TickBot1'][0]
    assert 'TickBot2 output' in response[0]['logs']['bot_logs']['TickBot2'][0]
    assert 'TickBot3 output' in response[0]['logs']['bot_logs']['TickBot3'][0]
    
def test_can_spawn_screep_for_single_bot(pyjsbridge):
    bot_main = """
        function () {
            console.log('Tickbot!',Game.time);
            const directions = [TOP, TOP_RIGHT, RIGHT, BOTTOM_RIGHT, BOTTOM, BOTTOM_LEFT, LEFT, TOP_LEFT];
            _.sample(Game.spawns).createCreep([MOVE]);
            _.each(Game.creeps, c => c.move(_.sample(directions)));
        }
    """
    
    pyjsbridge.reset_world()
    pyjsbridge.make_stub_world()
    pyjsbridge.add_bot('TickBot', 'W0N1', 15, 15, bot_main)
    pyjsbridge.start_server()
    response = pyjsbridge.tick(ticks = 1)
    assert len(response[0]['logs']['memory_logs']['TickBot']['creeps']) == 1

# def test_can_spawn_multi_screep_for_single_bot(pyjsbridge):
#     bot_main = """
#         function () {
#             console.log('Tickbot!',Game.time);
#             const directions = [TOP, TOP_RIGHT, RIGHT, BOTTOM_RIGHT, BOTTOM, BOTTOM_LEFT, LEFT, TOP_LEFT];
#             _.sample(Game.spawns).createCreep([MOVE]);
#             _.each(Game.creeps, c => c.move(_.sample(directions)));
#         }
#     """
#     pyjsbridge.reset_world()
#     pyjsbridge.make_stub_world()
#     pyjsbridge.add_bot('TickBot', 'W0N1', 15, 15, bot_main)
#     pyjsbridge.start_server()
#     response = pyjsbridge.tick(ticks = 20)
#     print(response)
#     assert len(response[19]['logs']['memory_logs']['TickBot']['creeps']) > 1
 
import sys
sys.path.append('../')
sys.path.append('./')

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
    yield bridge
    bridge._stop_jsbridge()

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
    assert pyjsbridge.add_bot('TickBot', 'W0N1', 15, 15, "function () {console.log('Tickbot!',Game.time);") == True
    
def test_capture_single_bot_logs_on_tick(pyjsbridge):
    pyjsbridge.reset_world()
    pyjsbridge.make_stub_world()
    pyjsbridge.add_bot('TickBot', 'W0N1', 15, 15, """function () {\n    console.log('Tickbot!',Game.time);\n}""")
    pyjsbridge.start_server()
    response = pyjsbridge.tick(ticks = 3)
    assert len(response) == 3
    assert len(response[0]['logs']['bot_logs']) == 1
    assert 'Tickbot' in response[0]['logs']['bot_logs'][0]
    assert 'Tickbot' in response[2]['logs']['bot_logs'][0]

# def test_capture_multiple_bot_logs_on_tick(pyjsbridge):
#     pyjsbridge.reset_world()
#     pyjsbridge.make_stub_world()
#     pyjsbridge.add_bot('TickBot1', 'W0N1', 15, 15, """function () {\n    console.log('Tickbot1!',Game.time);\n}""")
#     pyjsbridge.add_bot('TickBot2', 'W0N2', 15, 15, """function () {\n    console.log('Tickbot2!',Game.time);\n}""")
#     pyjsbridge.add_bot('TickBot3', 'W0N3', 15, 15, """function () {\n    console.log('Tickbot3!',Game.time);\n}""")
    
#     pyjsbridge.start_server()
#     response = pyjsbridge.tick(ticks = 1)
#     assert len(response) == 1
#     assert len(response[0]['logs']['bot_logs']) == 3
#     assert 'Tickbot1' in response[0]['logs']['bot_logs'][0]
#     assert 'Tickbot2' in response[0]['logs']['bot_logs'][1]
#     assert 'Tickbot3' in response[0]['logs']['bot_logs'][2]
    

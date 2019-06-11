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
    time.sleep(0.1)
    assert pyb.jsbridge_process.poll() == 1
    assert pyb.jsbridge_process.returncode == 1

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
    assert 'gametime' in pyjsbridge.tick()[0]
    
def test_tick_server_multi(pyjsbridge):
    pyjsbridge.make_stub_world()
    pyjsbridge.start_server()
    r = pyjsbridge.tick(ticks = 5)
    assert len(r) == 5
    assert r[0]['gametime'] == 2

def test_add_bot_to_server(pyjsbridge):
    pyjsbridge.make_stub_world()
    assert pyjsbridge.add_bot('TickBot', 'W0N1', 15, 15, "function () {console.log('Tickbot!',Game.time);") == True
    
def test_capture_bot_logs_on_tick(pyjsbridge):
    pyjsbridge.reset_world()
    pyjsbridge.make_stub_world()
    pyjsbridge.add_bot('TickBot', 'W0N1', 15, 15, "function () {console.log('Tickbot!',Game.time);")
    pyjsbridge.start_server()
    assert 'Tick' in pyjsbridge.tick(ticks = 3)[0]['logs']

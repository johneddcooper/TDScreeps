import sys
import os
sys.path.append('./')
from definitions import ROOT_DIR
from definitions import PyBridge

import time
import subprocess
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
    assert pyb._stop_jsbridge() != None
    assert pyb.jsbridge_process.poll() != None

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
    assert 'gametime' in response[0]._fields
    assert response[0].gametime == 1
    
def test_tick_server_multi(pyjsbridge):
    pyjsbridge.make_stub_world()
    pyjsbridge.start_server()
    r = pyjsbridge.tick(ticks = 5)
    assert len(r) == 5
    assert r[0].gametime == 1
    assert r[4].gametime == 5

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
    assert len(response[0].bot_logs) == 1
    assert 'TickBot_out' in response[0].bot_logs['TickBot'][0]
    assert 'TickBot_out' in response[2].bot_logs['TickBot'][0]

def test_capture_error_on_invalid_string(pyjsbridge):
    pyjsbridge.reset_world()
    pyjsbridge.make_stub_world()
    pyjsbridge.add_bot('TickBot', 'W0N1', 15, 15, """function () {\n    console.logg('TickBot_out!',Game.time);\n}""")
    pyjsbridge.start_server()
    response = pyjsbridge.tick(ticks = 1)
    assert len(response) == 1
    assert len(response[0].notification_logs) == 1
    assert 'notification' in response[0].notification_logs['TickBot'][0]
    assert 'TypeError' in response[0].notification_logs['TickBot'][1]
  

def test_capture_single_bot_multiple_logs_on_tick(pyjsbridge):
    pyjsbridge.reset_world()
    pyjsbridge.make_stub_world()
    pyjsbridge.add_bot('TickBot', 'W0N1', 15, 15, """function () {\n    console.log('TickBot_out 0');\n    console.log('TickBot_out 1');\n}""")
    pyjsbridge.start_server()
    response = pyjsbridge.tick(ticks = 3)
    assert len(response) == 3
    assert len(response[0].bot_logs) == 1
    assert len(response[0].bot_logs['TickBot']) == 2
    assert 'TickBot_out 0' in response[0].bot_logs['TickBot'][0]
    assert 'TickBot_out 1' in response[2].bot_logs['TickBot'][1]

def test_capture_multiple_bot_logs_on_tick(pyjsbridge):
    pyjsbridge.reset_world()
    pyjsbridge.make_stub_world()
    pyjsbridge.add_bot('TickBot1', 'W0N1', 15, 15, """function () {\n    console.log('TickBot1 output',Game.time);\n}""")
    pyjsbridge.add_bot('TickBot3', 'W1N2', 15, 15, """function () {\n    console.log('TickBot3 output',Game.time);\n}""")
    pyjsbridge.add_bot('TickBot2', 'W0N2', 15, 15, """function () {\n    console.log('TickBot2 output',Game.time);\n}""")
    
    pyjsbridge.start_server()
    response = pyjsbridge.tick(ticks = 1)
    assert len(response) == 1
    assert len(response[0].bot_logs) == 3
    print(response)
    assert 'TickBot1 output' in response[0].bot_logs['TickBot1'][0]
    assert 'TickBot2 output' in response[0].bot_logs['TickBot2'][0]
    assert 'TickBot3 output' in response[0].bot_logs['TickBot3'][0]
    
def test_can_spawn_screep_for_single_bot(pyjsbridge):
    bot_main = """
        function () {
            console.log('Tickbot!',Game.time);
            const directions = [TOP, TOP_RIGHT, RIGHT, BOTTOM_RIGHT, BOTTOM, BOTTOM_LEFT, LEFT, TOP_LEFT];
            _.sample(Game.spawns).createCreep([MOVE,MOVE]);
            _.each(Game.creeps, c => c.move(_.sample(directions)));
        }
    """
    pyjsbridge.reset_world()
    pyjsbridge.add_simple_room('W0N1')
    pyjsbridge.add_bot('TickBot', 'W0N1', 15, 15, bot_main)
    pyjsbridge.start_server()
    response = pyjsbridge.tick(ticks = 5)
    assert len(response[-1].memory_logs['TickBot']['creeps']) == 1
    assert response[-1].rooms['W0N1']['spawn'][0]['spawning']['remainingTime'] == 1
    assert response[-1].rooms['W0N1']['creep'][0]['spawning'] == True

    response = pyjsbridge.tick(ticks = 1)
    assert len(response[-1].memory_logs['TickBot']['creeps']) == 1
    assert response[-1].rooms['W0N1']['creep'][0]['spawning'] is False
    assert response[-1].rooms['W0N1']['spawn'][0]['spawning'] is None
    assert response[-1].rooms['W0N1']['creep'][0]['x'] != 15 or response[-1].rooms['W0N1']['creep'][0]['y'] != 15
    print(response[-1].rooms['W0N1']['creep'])

def test_logs_report_correct_game_time(pyjsbridge):
    pyjsbridge.reset_world()
    pyjsbridge.make_stub_world()
    pyjsbridge.add_bot('TickBot', 'W0N1', 15, 15, """function () {\n    console.log(Game.time);\n}""")
    pyjsbridge.start_server()
    response = pyjsbridge.tick(ticks = 3)
    assert str(response[0].gametime) in response[0].bot_logs['TickBot'][0]
    assert str(response[2].gametime) in response[2].bot_logs['TickBot'][0]

def test_tick_returns_rooms(pyjsbridge):
    pyjsbridge.reset_world()
    pyjsbridge.make_stub_world()
    pyjsbridge.add_bot('TickBot', 'W0N1', 15, 15, """function () {\n    console.log(Game.time);\n}""")
    pyjsbridge.start_server()
    response = pyjsbridge.tick(ticks = 1)

    # print(response[0])
    assert response[0].rooms is not None
    spawns = response[0].rooms['W0N1']['spawn']
    assert len(spawns) == 1
    assert spawns[0]['x'] == 15
    assert spawns[0]['y'] == 15 

def test_tick_returns_users(pyjsbridge):
    pyjsbridge.reset_world()
    pyjsbridge.make_stub_world()
    pyjsbridge.add_bot('TickBot', 'W0N1', 15, 15, """function () {\n    console.log(Game.time);\n}""")
    pyjsbridge.start_server()
    response = pyjsbridge.tick(ticks = 1)

    assert response[0].users is not None
    assert len(response[0].users) == 1
    assert 'W0N1' in response[0].users['TickBot']['rooms']
    

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
 
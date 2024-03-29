import requests
import json
from subprocess import Popen

import sys
import os
sys.path.append('../../')
from definitions import ROOT_DIR
path_to_jsbridge = os.path.join(ROOT_DIR, 'py-screeps-server-mockup/jsbridge.js')

from collections import namedtuple, defaultdict

jsbridge_url = "http://localhost:3000"
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

class PyBridge:

    active = False

    def __del__(self):
        self._stop_jsbridge()

    def _start_jsbridge(self):
        self.jsbridge_process = Popen(["node",path_to_jsbridge])
        self.active = True

    def _stop_jsbridge(self):
        if self.active:
            requests.post(jsbridge_url+"/stop")
            self.jsbridge_process.kill()
            self.active = False
            return self.jsbridge_process.wait()
        return True

    def _msg_jsbridge(self, data:dict, timeout=5):
        return requests.post(jsbridge_url, data=json.dumps(data), headers=headers, timeout = 5)    
    
    def reset_world(self):
        return True if requests.post(jsbridge_url+"/reset", timeout = 5).status_code==200 else False
    
    def get_world_load(self):
        r = requests.get(jsbridge_url+"/world/load", timeout = 2)
        return r.json() if r.status_code==200 else False

    def make_stub_world(self):
        r = requests.post(jsbridge_url+"/make_stub", timeout = 5)
        return True if r.status_code==200 else False

    def get_all_rooms(self):
        r = requests.get(jsbridge_url+"/driver/getAllRooms", timeout = 2)
        return r.json() if r.status_code==200 else False

    def add_room(self, room_name):
        r = requests.post(jsbridge_url+"/world/addRoom", timeout = 5,  headers=headers, data=json.dumps({'msg':room_name}))
        return True if r.status_code == 201 else False

    def add_simple_room(self, room_name):
        r = requests.post(jsbridge_url+"/world/addRoom/simple", timeout = 5,  headers=headers, data=json.dumps({'msg':room_name}))
        return True if r.status_code == 201 else False

    def start_server(self):
        r = requests.post(jsbridge_url+"/start_server", timeout = 5)
        return True if r.status_code==200 else False



    def tick(self, ticks=1):

        msgData = {'ticks':ticks}
        r = requests.post(jsbridge_url+"/tick", timeout = 5,  headers=headers, data=json.dumps({'msg':msgData}))
 
        return  [tick_response_to_objects(log) for log in r.json()]
      

    def start_tick(self):
        response = []
        requests.post(jsbridge_url +"/start_tick")
        

    def add_bot(self, username, room, x, y, main):
        msgData = {'username':username, 'room':room, 'x':x, 'y':y, 'main':main}
        r = requests.post(jsbridge_url+"/world/addBot", timeout = 2,  headers=headers, data=json.dumps({'msg':msgData}))
        return True if r.status_code == 201 else False

def tick_response_to_objects(response):
    Log = namedtuple("Log", "bot_logs notification_logs memory_logs gametime users rooms")
    rooms = defaultdict(lambda: defaultdict(list))
    for struct in response['rooms']:
        rooms[struct['room']][struct['type']].append(struct)

    log = Log(
        response['bot_logs'],
        response['notification_logs'],
        response['memory_logs'],
        response['gametime'],
        { user['username']: user for user in response['users'] },
        rooms
    )
    return log


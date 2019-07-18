import requests
import json
from subprocess import Popen

import sys
import os
sys.path.append('../../')
from definitions import ROOT_DIR
path_to_jsbridge = os.path.join(ROOT_DIR, 'py-screeps-server-mockup/jsbridge.js')

jsbridge_url = "http://localhost:3000"
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

class PyBridge:

    def __del__(self):
        self._stop_jsbridge()

    def _start_jsbridge(self):
        self.jsbridge_process = Popen(["node",path_to_jsbridge])

    def _stop_jsbridge(self):
        requests.post(jsbridge_url+"/stop", timeout = 2)
        self.jsbridge_process.kill()
        return self.jsbridge_process.wait()

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
        #headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        r = requests.post(jsbridge_url+"/world/addRoom", timeout = 5,  headers=headers, data=json.dumps({'msg':room_name}))
        return True if r.status_code == 201 else False

    def start_server(self):
        r = requests.post(jsbridge_url+"/start_server", timeout = 5)
        return True if r.status_code==200 else False

    def tick(self, ticks=1):
        response = []
        for tick in range(ticks):
            r = requests.post(jsbridge_url +"/tick", timeout = 5)
            if r.status_code != 200:
                return False 
            response.append(r.json())
        return response

    def add_bot(self, username, room, x, y, main):
        msgData = {'username':username, 'room':room, 'x':x, 'y':y, 'main':main}
        r = requests.post(jsbridge_url+"/world/addBot", timeout = 2,  headers=headers, data=json.dumps({'msg':msgData}))
        return True if r.status_code == 201 else False
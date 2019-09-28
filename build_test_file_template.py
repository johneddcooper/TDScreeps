import sys
sys.path.append("./")
from definitions import PyBridge
import pyjs_compiler as pjc
import pytest


@pytest.fixture(scope="module")
def persistant_stub_world():
    class PersistantStubWorld():
        bridge = PyBridge()
        current_tick = 0
        logs = []
        def get_logs(self,end_tick,start_tick=0):
            if end_tick > self.current_tick:
                log = self.bridge.tick(end_tick-self.current_tick)
                self.logs.extend(log)
                self.current_tick = end_tick
            return self.logs[start_tick:end_tick]
 
    build_name = {% BUILD_NAME %}

    js_src = pjc.compile_build(build_name)
    world = PersistantStubWorld()
    world.bridge._start_jsbridge()
    world.bridge.make_stub_world()
    world.bridge.add_bot('TickBot', 'W0N1', 15, 15, js_src)
    world.bridge.start_server()
    yield world
    world.bridge._stop_jsbridge()



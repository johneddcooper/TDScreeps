import sys
sys.path.append("./")
from definitions import ROOT_DIR
from definitions import PyBridge


import pytest
import pyjs_compiler as pjc
import os
import shutil

def test_compile_simple_main_from_valid_string():
    # We have a bit of test code as a string to compile
    
    src = """ 
# Without the 'noalias' pragma, each of the following would be translated into something like 'py_Infinity' or
#  'py_keys' in the output file.
__pragma__('noalias', 'name')
__pragma__('noalias', 'undefined')
__pragma__('noalias', 'Infinity')
__pragma__('noalias', 'keys')
__pragma__('noalias', 'get')
__pragma__('noalias', 'set')
__pragma__('noalias', 'type')
__pragma__('noalias', 'update')


def main():
    
    #Main game logic loop.
    
    console.log("Tickbot buildchain!")
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
    assert any('Tickbot buildchain!' in line for line in response[0]['logs']['bot_logs']['TickBot'])

    # We tick the server a few more times
    response = bridge.tick(ticks = 2)

    # We get two logs back
    assert len(response) == 2

    # The reply had no errors
    assert "Error" not in response[0]['logs']['notification_logs']['TickBot']
    assert "Error" not in response[1]['logs']['notification_logs']['TickBot']

    # The reply had the output we expected from the running JS code for both ticks
    assert any('Tickbot buildchain!' in line for line in response[0]['logs']['bot_logs']['TickBot'])
    assert any('Tickbot buildchain!' in line for line in response[1]['logs']['bot_logs']['TickBot'])

def test_compile_complex_main_from_dir():

    # We want to start a new persistant build, add some python code to the files, compile them, and run them

    # We call a method from the commandline from pyjs_compiler to make a new build
    ##TODO## Make below command line (?)
    build_name = "my_project"
    try:
        src_path, comp_path = pjc.make_project(build_name)

        # The compiler makes the directory, moves the required defs into it, and makes a blank main file for us
        assert os.path.isdir(os.path.join(src_path,"defs"))
        assert os.path.isfile(os.path.join(src_path, "main.py"))

        # We add some source code into the file that calls some Game functions and uses a second class
        
        with open(os.path.join(src_path, "main.py"), "r") as f:
            contents = f.readlines()
            f.close()
        contents.insert(1, "import gametime")
        contents.append("console.log('buildtest:', gametime.get_game_time(Game));")

        with open(os.path.join(src_path, "main.py"), "w") as f:
            f.write("".join(contents))
            f.close()

        # We create and add source code into the second class
        second_file_src="def get_game_time(game):\n\treturn game.time;"
        with open(os.path.join(src_path, "gametime.py"), "w") as f:
            f.write(second_file_src)
            f.close()     

        # We use pyjs_compiler to build the files
        js_src = pjc.compile_build(build_name)

        # We pass the string it returns to the mock-server, which we run and tick
        bridge = PyBridge()
        bridge._start_jsbridge()
        bridge.make_stub_world()
        bridge.add_bot('TickBot', 'W0N1', 15, 15, js_src)
        bridge.start_server()
        response = bridge.tick(ticks = 1)

        # The server returns no errors
        assert "Error" not in response[0]['logs']['notification_logs']['TickBot']
        
        # And has the output we expect
        assert any('buildtest: 1' in line for line in response[0]['logs']['bot_logs']['TickBot'])

        # We wait a few ticks
        response = bridge.tick(ticks = 2)

        # And see that our code is still providing the right output\
        assert any('buildtest: 2' in line for line in response[0]['logs']['bot_logs']['TickBot'])
        assert any('buildtest: 3' in line for line in response[1]['logs']['bot_logs']['TickBot'])

    finally:
        # And make a call to pyjs_compiler to remove the built folders
        pjc.remove_build_folders(build_name)

def test_run_tests_from_dir():
    # We want to start a new persistant build, add some python code to the files, and run some tests against them

    # We call a method from the commandline from pyjs_compiler to make a new build
    ##TODO## Make below command line (?)
    build_name = "my_project"
    try:
        src_path, comp_path = pjc.make_project(build_name)

        # The compiler makes a test directory for us
        assert os.path.isdir(os.path.join(pjc._get_build_path(build_name),'tests'))

        # We copy in the src files we want
        
        shutil.copy(os.path.join(ROOT_DIR, 'screeps-starter-python','src',"main.py"), os.path.join(src_path, "main.py"))
        shutil.copy(os.path.join(ROOT_DIR, 'screeps-starter-python','src',"harvester.py"), os.path.join(src_path, "harvester.py"))

        # We create and add source code into our tests
        tests_file_src="def get_game_time(game):\n\treturn game.time;"
        with open(os.path.join(src_path, "gametime.py"), "w") as f:
            f.write(second_file_src)
            f.close()     

        # We use pyjs_compiler to build the files
        js_src = pjc.compile_build(build_name)

        # We pass the string it returns to the mock-server, which we run and tick
        bridge = PyBridge()
        bridge._start_jsbridge()
        bridge.make_stub_world()
        bridge.add_bot('TickBot', 'W0N1', 15, 15, js_src)
        bridge.start_server()
        response = bridge.tick(ticks = 1)

import sys
import os
sys.path.append("../../")
sys.path.append("./")
from definitions import ROOT_DIR
import shutil
import pytest
import glob
import pyjs_compiler as pjc

TRANSVERSE_SRC_DIR = os.path.join(ROOT_DIR, 'screeps-starter-python')

@pytest.fixture()
def test_build_folder():
    pjc._make_build_folders("test_build")
    yield pjc._get_build_path("test_build")
    pjc._remove_build_folders("test_build")

def test_make_folders_raises_error_on_invalid_build_name():
    with pytest.raises(Exception) as e_info:
        pjc._make_build_folders("","0.1")
    with pytest.raises(Exception) as e_info:
        pjc._make_build_folders(None,None)

def test_make_folders_allows_empty_version():
    pjc._make_build_folders("test_build",None)
    assert os.path.isdir(pjc._get_build_path("test_build"))
    assert os.path.isdir(os.path.join(pjc._get_build_path("test_build"), 'src'))
    assert os.path.isdir(os.path.join(pjc._get_build_path("test_build"), 'dist'))
    pjc._remove_build_folders('test_build')

def test_make_folders_allows_version_to_be_type_int():
    pjc._make_build_folders("test_build",1)
    assert os.path.isdir(pjc._get_version_path("test_build", 1))
    pjc._remove_build_folders('test_build')
    
def test_make_folders():
    pjc._make_build_folders("test_build","0.1")
    assert os.path.isdir(pjc._get_build_path("test_build"))
    assert os.path.isdir(pjc._get_version_path("test_build", "0.1"))
    pjc._remove_build_folders('test_build')

def test_remove_build_folder():
    pjc._make_build_folders("test_build","1")
    pjc._remove_build_folders("test_build")
    assert not os.path.exists(pjc._get_build_path('test_build'))

def test_remove_versoned_src_files():
    pjc._make_build_folders("test_build","1")
    src_path = pjc._get_src_path("test_build", "1")
    open(os.path.join(src_path, 'test_file'), 'a').close()
    assert os.path.isfile(os.path.join(src_path, 'test_file'))
    pjc._remove_src_files("test_build", "1")
    assert not os.path.exists(os.path.join(pjc._get_src_path("test_build", "1"), 'test_file'))
    assert os.path.exists(src_path)
    pjc._remove_build_folders("test_build")

def test_remove_un_versoned_src_files():
    pjc._make_build_folders("test_build")
    src_path = pjc._get_src_path("test_build")
    open(os.path.join(src_path, 'test_file'), 'a').close()
    assert os.path.isfile(os.path.join(src_path, 'test_file'))
    pjc._remove_src_files("test_build")
    assert not os.path.exists(os.path.join(pjc._get_src_path("test_build"), 'test_file'))
    assert os.path.exists(src_path)
    pjc._remove_build_folders("test_build")

def test_compile_from_string_makes_folders_from_build_dir_and_version():
    pjc.compile_from_string("", build_name = "test_build", version = "0.1")
    assert os.path.isdir(os.path.join(pjc._get_version_path("test_build", "0.1"), 'src'))
    assert os.path.isdir(os.path.join(pjc._get_version_path("test_build", "0.1"), 'dist'))
    pjc._remove_build_folders("test_build")

def test_compile_from_string_makes_folders_from_build_dir_no_version():
    pjc.compile_from_string("", build_name = "test_build")
    assert os.path.isdir(os.path.join(pjc._get_build_path("test_build"), 'src'))
    assert os.path.isdir(os.path.join(pjc._get_build_path("test_build"), 'dist'))
    pjc._remove_build_folders("test_build")

def test_compile_from_string_makes_and_removes_folders_from_no_build_dir():
    pjc.compile_from_string("")
    assert len(glob.glob(os.path.join(ROOT_DIR, ".pyjs_builds", ".tmp*"))) == 0

def test_correctly_writes_string_to_file(test_build_folder):
    filepath = os.path.join(test_build_folder,'test_file.py')
    pjc._write_string_to_file(filepath, "def main():\n\tprint('test_func')")
    assert os.path.isfile(filepath)
    with open(filepath, 'r') as readfile:
        lines = readfile.readlines()
        assert lines[0] == "def main():\n"
        assert lines[1] == "\tprint('test_func')"

def test_pyjs_compiler_can_import_build_module():
    assert pjc.build != None

def test_builds_to_file_from_valid_simple_source_string():
    src = """
def main():
\tprint("test_build_print") 
module.exports.loop = main
"""
    pjc.compile_from_string(src, build_name="test_build")
    assert os.path.isfile(os.path.join(pjc._get_compiled_path("test_build"), 'main.js'))
    with open(os.path.join(pjc._get_compiled_path("test_build"), 'main.js'), 'r') as built_file:
        built_src = built_file.read()
        assert "test_build_print" in built_src
    pjc._remove_build_folders("test_build")
    
def test_builds_from_valid_simple_source_string_and_returns_compiled_string():
    src = """
def main():
\tprint("test_build_print") 
module.exports.loop = main
"""
    js_src = pjc.compile_from_string(src)
    assert "test_build_print" in js_src

def test_will_strip_main_func_contents_from_compiled_file():
    compiled_string = """
"use strict";
// Transcrypt'ed from Python, 2019-07-03 20:58:27
function main () {
    FunctionBody
}
main ();
"""
    assert pjc.strip_main_from_js(compiled_string) == "    FunctionBody"

# test can build py file to js

# test compile from string builds

# test compile from function builds

# test compile from dir builds

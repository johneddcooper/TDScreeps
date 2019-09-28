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
def temp_test_project():
    project = pjc.make_project("test_build")
    yield project
    pjc.remove_build_folders("test_build")

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
    pjc.remove_build_folders('test_build')

def test_make_folders_allows_version_to_be_type_int():
    pjc._make_build_folders("test_build",1)
    assert os.path.isdir(pjc._get_version_path("test_build", 1))
    pjc.remove_build_folders('test_build')
    
def test_make_folders():
    pjc._make_build_folders("test_build","0.1")
    assert os.path.isdir(pjc._get_build_path("test_build"))
    assert os.path.isdir(pjc._get_version_path("test_build", "0.1"))
    pjc.remove_build_folders('test_build')

def testremove_build_folder():
    pjc._make_build_folders("test_build","1")
    pjc.remove_build_folders("test_build")
    assert not os.path.exists(pjc._get_build_path('test_build'))

def test_remove_versoned_src_files():
    pjc._make_build_folders("test_build","1")
    src_path = pjc._get_src_path("test_build", "1")
    open(os.path.join(src_path, 'test_file'), 'a').close()
    assert os.path.isfile(os.path.join(src_path, 'test_file'))
    pjc._remove_src_files("test_build", "1")
    assert not os.path.exists(os.path.join(pjc._get_src_path("test_build", "1"), 'test_file'))
    assert os.path.exists(src_path)
    pjc.remove_build_folders("test_build")

def test_remove_un_versoned_src_files():
    pjc._make_build_folders("test_build")
    src_path = pjc._get_src_path("test_build")
    open(os.path.join(src_path, 'test_file'), 'a').close()
    assert os.path.isfile(os.path.join(src_path, 'test_file'))
    pjc._remove_src_files("test_build")
    assert not os.path.exists(os.path.join(pjc._get_src_path("test_build"), 'test_file'))
    assert os.path.exists(src_path)
    pjc.remove_build_folders("test_build")

def test_compile_from_string_makes_folders_from_build_dir_and_version():
    pjc.compile_from_string("", build_name = "test_build", version = "0.1")
    assert os.path.isdir(os.path.join(pjc._get_version_path("test_build", "0.1"), 'src'))
    assert os.path.isdir(os.path.join(pjc._get_version_path("test_build", "0.1"), 'dist'))
    pjc.remove_build_folders("test_build")

def test_compile_from_string_makes_folders_from_build_dir_no_version():
    pjc.compile_from_string("", build_name = "test_build")
    assert os.path.isdir(os.path.join(pjc._get_build_path("test_build"), 'src'))
    assert os.path.isdir(os.path.join(pjc._get_build_path("test_build"), 'dist'))
    pjc.remove_build_folders("test_build")

def test_compile_from_string_makes_and_removes_folders_from_no_build_dir():
    pjc.compile_from_string("")
    assert len(glob.glob(os.path.join(ROOT_DIR, ".pyjs_builds", ".tmp*"))) == 0

def test_correctly_writes_string_to_file(temp_test_project):
    src_path = temp_test_project.src_path
    comp_path = temp_test_project.comp_path
    filepath = os.path.join(src_path,'test_file.py')
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
    pjc.remove_build_folders("test_build")
    
def test_builds_from_valid_simple_source_string_and_returns_compiled_string():
    src = """
def main():
\tprint("test_build_print") 
module.exports.loop = main
"""
    js_src = pjc.compile_from_string(src)
    assert "test_build_print" in js_src

def test_function_call_to_make_project_returns_src_and_dist_paths(temp_test_project):
    src_path = temp_test_project.src_path
    comp_path = temp_test_project.comp_path
    assert src_path == pjc._get_src_path("test_build")
    assert comp_path == pjc._get_compiled_path("test_build")

def test_function_call_to_make_project_makes_folders(temp_test_project):
    assert os.path.isdir(pjc._get_build_path("test_build"))

def test_function_call_to_make_project_moves_defs_to_src_dir(temp_test_project):
    src_path = temp_test_project.src_path
    assert os.path.isdir(os.path.join(src_path,"defs"))
    constants_path = os.path.join(src_path, "defs", "constants.py")
    assert os.path.isfile(constants_path)
    with open(constants_path, 'r') as constants_file:
        constants = constants_file.read()
        assert "OK = 0" in constants
        constants_file.close()

def test_function_call_to_make_project_defs_not_empty(temp_test_project):
    src_path = temp_test_project.src_path
    constants_path = os.path.join(src_path, "defs", "constants.py")
    with open(constants_path, 'r') as constants_file:
        constants = constants_file.read()
        assert "OK = 0" in constants
        constants_file.close()

def test_function_call_to_make_project_makes_main(temp_test_project):
    src_path = temp_test_project.src_path
    main_path = os.path.join(src_path, "main.py")
    assert os.path.isfile(main_path)

def test_function_call_to_make_project_main_not_empty(temp_test_project):
    src_path = temp_test_project.src_path
    main_path = os.path.join(src_path, "main.py")
    with open(main_path, 'r') as main_file:
        main = main_file.read()
        assert "__pragma__('noalias', 'name')" in main
        main_file.close()

def test_compile_from_directory(temp_test_project):
    src_path = temp_test_project.src_path
    comp_path = temp_test_project.comp_path
    with open(os.path.join(src_path, "main.py"), "r") as f:
        contents = f.readlines()
        f.close()
    contents.append("console.log('buildtest:', Game.time)")
    print(contents)
    with open(os.path.join(src_path, "main.py"), "w") as f:
        f.write("".join(contents))
        f.close()
    src = pjc.compile_build("test_build")
    assert "console.log ('buildtest:', Game.time);" in src
    assert os.path.isfile(os.path.join(comp_path, 'main.js'))
    with open(os.path.join(comp_path,"main.js"), "r") as f:
        file_src = f.read()
        f.close()
    assert "console.log ('buildtest:', Game.time);" in file_src
    
def test_new_project_makes_tests_folder(temp_test_project):   
    assert temp_test_project.tests_path is not None
    assert os.path.isdir(temp_test_project.tests_path)

def test_new_projects_makes_FT_and_UT_template_files(temp_test_project):
    ut_file = os.path.join(temp_test_project.tests_path, "test_build_UT.py")
    ft_file = os.path.join(temp_test_project.tests_path, "test_build_FT.py")
    assert os.path.isfile(ut_file)
    assert os.path.isfile(ft_file)
    with open(ut_file, "r") as f:
        file_src = f.read()
        f.close()
    assert "build_name = test_build" in file_src

    with open(ft_file, "r") as f:
        file_src = f.read()
        f.close()
    assert "build_name = test_build" in file_src
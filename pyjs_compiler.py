import shutil
import os
import random 
from definitions import ROOT_DIR
import sys
sys.path.append("./screeps-starter-python")
from build import build_from_process as build
import re
from collections import namedtuple

def _get_build_path(build_name):
    return os.path.join(ROOT_DIR, ".pyjs_builds", str(build_name))

def _get_version_path(build_name, version):
    return os.path.join(_get_build_path(build_name), str(version))

def _get_src_path(build_name, version = ""):
    return os.path.join(_get_version_path(build_name, version), 'src')
   
def _get_compiled_path(build_name, version = ""):
    return os.path.join(_get_version_path(build_name, version), 'dist')

def _get_tests_path(build_name, version = ""):
    return os.path.join(_get_version_path(build_name, version), 'tests')

def _make_build_folders(build_name, version = ""):
    if (not build_name):
        raise Exception("build_name must not be empty.")
    if not version:
        version = ""
    os.makedirs(os.path.join(_get_version_path(build_name, version), 'src'))
    os.makedirs(os.path.join(_get_version_path(build_name, version), 'dist'))
    os.makedirs(os.path.join(_get_version_path(build_name, version), 'tests'))

def remove_build_folders(build_name):
    shutil.rmtree(_get_build_path(build_name))

def _remove_src_files(build_name, version = ""):
    if not version:
        version = ""
    shutil.rmtree(_get_version_path(build_name, version))
    os.makedirs(os.path.join(_get_version_path(build_name, version), 'src'))

def _write_string_to_file(path, src):
    with open(path, "w") as text_file:
        text_file.write(src)

def alter_main_for_running(js_src):
    return js_src.replace("};\n\t\t__", "};\n\t\tmodule.exports.loop = main;\n\t\t__")

    #re_match_string = r"(function.*)\nmain \(\);" #Matched end main()
    # match = re.search(re_match_string, js_src, re.DOTALL)
    # if match:
    #     code = match.group(1)
    # return code

def compile_from_string(src, build_name = None, version = ""):
    do_adhoc_build = not build_name
    if do_adhoc_build:
        build_name = '.tmp' + str(random.randint(10**3, 10**4))
        while os.path.exists(_get_build_path(build_name)):
            build_name = '.tmp' + str(random.randint(10**3, 10**4))
    _make_build_folders(build_name, version)
    src_dir = _get_src_path(build_name, version=version)
    dist_dir = _get_compiled_path(build_name, version=version)
    

    _write_string_to_file(os.path.join(src_dir, 'main.py'), src)
    build(src_dir, dist_dir)

    
    with open(os.path.join(dist_dir, 'main.js'), 'r') as js_src_file:
        js_src = js_src_file.read()
        js_src_file.close()
    
    if do_adhoc_build:
        remove_build_folders(build_name)

    return alter_main_for_running(js_src)

def make_project(build_name, version=""):
    _make_build_folders(build_name,version)
    src_path = _get_src_path(build_name)
    shutil.copytree(os.path.join(ROOT_DIR, "screeps-starter-python","src","defs"), os.path.join(src_path,"defs"))
    shutil.copyfile(os.path.join(ROOT_DIR, "screeps-starter-python","blank_main.py"), os.path.join(src_path,"main.py"))
    Project = namedtuple('Project', 'src_path comp_path tests_path build_name version')
    return Project(src_path, _get_compiled_path(build_name, version), _get_tests_path(build_name, version), build_name, version)

def compile_build(build_name, version = ""):
    src_dir = _get_src_path(build_name, version=version)
    dist_dir = _get_compiled_path(build_name, version=version)
    build(src_dir, dist_dir)
    with open(os.path.join(dist_dir, 'main.js'), 'r') as js_src_file:
        js_src = js_src_file.read()
        js_src_file.close()
    return alter_main_for_running(js_src)
import shutil
import os
import random 
from definitions import ROOT_DIR

def _get_build_path(build_name):
    return os.path.join(ROOT_DIR, ".pyjs_builds", str(build_name))

def _get_version_path(build_name, version):
    return os.path.join(_get_build_path(build_name), str(version))

def _get_src_path(build_name, version = ""):
    return os.path.join(_get_version_path(build_name, version), 'src')
   
def _get_compiled_path(build_name, version = ""):
    return os.path.join(_get_version_path(build_name, version), 'comp')

def _make_build_folders(build_name, version = ""):
    if (not build_name):
        raise Exception("build_name must not be empty.")
    if not version:
        version = ""
    os.makedirs(os.path.join(_get_version_path(build_name, version), 'src'))
    os.makedirs(os.path.join(_get_version_path(build_name, version), 'comp'))

def _remove_build_folders(build_name):
    shutil.rmtree(_get_build_path(build_name))

def _remove_src_files(build_name, version = ""):
    if not version:
        version = ""
    shutil.rmtree(_get_version_path(build_name, version))
    os.makedirs(os.path.join(_get_version_path(build_name, version), 'src'))

def _write_string_to_file(path, src):
    with open(path, "w") as text_file:
        text_file.write(src)

def compile_from_string(src, build_name = None, version = ""):
    do_adhoc_build = not build_name
    if do_adhoc_build:
        build_name = '.tmp' + str(random.randint(10**3, 10**4))
        while os.path.exists(_get_build_path(build_name)):
            build_name = '.tmp' + str(random.randint(10**3, 10**4))
    _make_build_folders(build_name, version)
    
    _write_string_to_file(os.path.join(_get_src_path(build_name), 'main.py'), src)


    # compile
    
    # fake output to test
    shutil.copy(os.path.join(_get_src_path(build_name), 'main.py'), os.path.join(_get_compiled_path(build_name), 'main.js'))
    
    if do_adhoc_build:
        _remove_build_folders(build_name)

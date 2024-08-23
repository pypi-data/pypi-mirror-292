from geo_auto_install.utils.g_common import *
from geo_auto_install.utils.g_logger import *
import subprocess
import shutil

def exec_command(cmd_args):
    try:
        result = subprocess.check_output(cmd_args, universal_newlines=True)
        log("\n"+result)
        return True
    except subprocess.CalledProcessError as e:
        log("Error: {}".format(e))
        return False

def get_files(path):
    files = []
    for filename in os.listdir(path):
        full_file_path = os.path.join(path, filename)
        if os.path.isfile(full_file_path):
            files.append(full_file_path)

    return files

def get_files_name(path):
    files = []
    for filename in os.listdir(path):
        full_file_path = os.path.join(path, filename)
        if os.path.isfile(full_file_path):
            files.append(filename)

    return files

def get_files_name_with_ext(path, ext):
    files = []
    for filename in os.listdir(path):
        full_file_path = os.path.join(path, filename)
        if os.path.isfile(full_file_path) and full_file_path.endswith(ext) : 
            files.append(filename)

    return files

def move_files_from_to(files_name, from_path, dest_path):
    if not os.path.exists(dest_path):
        os.mkdir(dest_path)

    for filename in files_name:
        dest_full_path = os.path.join(dest_path,filename)
        if os.path.exists(dest_full_path):
            os.remove(dest_full_path)
        
        from_full_path = os.path.join(from_path,filename)
        shutil.move(from_full_path, dest_path)

def copy_files_to(files_path, dest_path):
    for path in files_path:
        shutil.copy(path, dest_path)
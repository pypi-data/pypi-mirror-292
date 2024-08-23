import os
from geo_auto_install.utils.g_common import * 
from geo_auto_install.utils.g_logger import * 
from geo_auto_install.utils.g_logger import * 

def get_current_script_dir(file):
    return os.path.dirname(os.path.abspath(file))

def init_logger():
    current_script_folder = get_current_script_dir(__file__)

    context = {}
    context[CTX_PROP_LOG_DEST] = os.path.join(current_script_folder,"temp/log")
    Logger(context)
    
def make_test_dir(test_file_path, test_function_name):
    test_name = os.path.splitext(os.path.basename(test_file_path))[0]
    
    temp_folder = os.path.join(get_current_script_dir(__file__),"temp")
    if not os.path.exists(temp_folder):
        os.makedirs(temp_folder)
    
    test_folder = os.path.join(temp_folder,test_name)
    if not os.path.exists(test_folder):
        os.makedirs(test_folder)
        
    test_function_folder = os.path.join(test_folder, test_function_name)
    if not os.path.exists(test_function_folder):
        os.makedirs(test_function_folder)
    
    return test_function_folder
from geo_auto_install.utils.g_common import *
from geo_auto_install.utils.g_http import *
from geo_auto_install.utils.g_nextcloud import *
import os
import shutil
import copy

def download_geo_installer(context, action):
    versions = context[CTX_PROP_GEO_VERSIONS]
    is_windows = context[CTX_PROP_IS_WINDOWS]
    geo_version = versions["geo"]
    geo_current_version = geo_version["current"]
    geo_next_version = geo_version["next"]

    if geo_current_version == geo_next_version:
        log("The given target version is the same as the current one [{} -> {}]. Update will be stopped.".format(geo_current_version,geo_next_version))
        
        return True

    suffix = "windows" if is_windows else "linux"
    filename = "geo-installer-{}-{}.jar".format(geo_next_version,suffix)
    folder = context[CTX_PROP_GEO_INSTALL_PATH]
    installer_full_path = os.path.join(folder, filename)

    log("The geo-installer will be positioned in {}".format(folder))
    log("Searching for {} ".format(filename))
    
    context[CTX_PROP_GEO_INSTALLER_PATH] = installer_full_path

    if os.path.exists(installer_full_path):
        log("A geo installer exist at {}, no need to download".format(filename))
    else:
        fetched = ask_for_download_shared_link(folder=folder, filename=filename)
        
        if not fetched or not os.path.exists(installer_full_path) :
            return False
        
    return True


def download_geo_solutions(context, action):
    geo_extensions_folder = context[CTX_PROP_GEO_EXTENSIONS_PATH]
    versions = copy.deepcopy(context[CTX_PROP_GEO_VERSIONS])
    versions.pop("geo")

    if len(versions) == 0:
        log("It seems like there are no geo-solutions provided in the configuration. If you have geo-solutions, please note that they won't be updated.")
        return True

    log("Following geo solutions will be traited :")
    for key in list(versions.keys()):
        log("  {} : {} -> {}".format(key, versions[key]["current"], versions[key]["next"]))


    geo_solutions_temp_folder = os.path.join(context[CTX_PROP_GEO_INSTALL_PATH], "update_geo-solutions") 
    if not os.path.exists(geo_solutions_temp_folder):
        os.makedirs(geo_solutions_temp_folder)

    log("Geo solutions will be temporarily positioned in {}".format(geo_solutions_temp_folder))

    for key in list(versions.keys()):
        current_version = versions[key]["current"]
        next_version = versions[key]["next"]
        geo_solution_name = key
        
        geo_solution_current_file_name = geo_solution_name + "-" + current_version + ".jar"
        geo_solution_next_file_name = geo_solution_name + "-" + next_version + ".jar"

        geo_solution_current_path = os.path.join(geo_extensions_folder, geo_solution_current_file_name)
        geo_solution_temp_path =  os.path.join(geo_solutions_temp_folder, geo_solution_next_file_name)

        if current_version == next_version and os.path.exists(geo_solution_current_path):
            log("{} : the current version is the same as the target one, we have nothing to do. ".format(geo_solution_name))            
            shutil.copy(geo_solution_current_path,geo_solution_temp_path)
        else:           
            if os.path.exists(geo_solution_temp_path):
                log("{} already exists in {} , no need to download it.".format(geo_solution_next_file_name,geo_solutions_temp_folder))
            else:
                fetched = ask_for_download_shared_link(folder=geo_solutions_temp_folder, filename=geo_solution_next_file_name)
        
                if not fetched or not os.path.exists(geo_solution_temp_path) :
                    return False

        if os.path.exists(geo_solutions_temp_folder):
            log("{} ok".format(geo_solution_name))
        else: 
            return False
    
    # we need to persit the geo-solutions temp folder to perfom update later  
    context[CTX_PROP_GEO_EXTENSIONS_TEMP_PATH] = geo_solutions_temp_folder

    return True 

def download_version_file(context, action):
    url = SAAS_VERSIONS_FILE
    
    folder = context[CTX_PROP_GEO_INSTALL_PATH]
    filename = "versions_file.json"
    full_path = os.path.join(folder, filename)
    
    context[CTX_PROP_GEO_VERSIONS_FILE] = full_path

    if os.path.exists(full_path):
        os.remove(full_path)
        
    fetched = False
    headers = {}
    count = 0
    while count < 3 and not fetched:
        fetched = execute_download_request(url, headers, full_path)
        count+=1
    
    if not fetched or not os.path.exists(full_path):
        return False

    return True
    
def log_code_for_nextcloud_link(folder, filename):
    action = {
            "code":"link_nextcloud",
            "folder":folder,
            "filename":filename    
        }
    print("USER_ACTION:NEXTCLOUD:"+str(action).replace("'", '"'))
    
def ask_for_download_shared_link(folder, filename):
    full_path = os.path.join(folder, filename)
    log_code_for_nextcloud_link(folder=folder, filename=filename)
    log("We need to download the file {} at {}".format(filename, full_path))
    
    url = input("Write the download shared link : ")             
    password = input("Write the password (can be empty):")    
            
    count = 0
    fetched = False
    while count < 3 and not fetched:
        count+=1
        
        log("Try {} : download {}".format(count, filename))
        
        fetched = download_nextcloud(url, password, target_path=full_path)
    
    return fetched
    
    

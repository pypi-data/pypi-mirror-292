from geo_auto_install.utils.g_common import * 
from geo_auto_install.utils.g_logger import * 
import os
import shutil

def clean_updates_files(context, action):

    log("Remove the geo-installer")
    geo_installer_path = context[CTX_PROP_GEO_INSTALLER_PATH]
    if os.path.exists(geo_installer_path):
        os.remove(geo_installer_path)

    log("Remove downloaded geo-solutions")
    new_geo_solutions_path = context[CTX_PROP_GEO_EXTENSIONS_TEMP_PATH]
    if os.path.exists(new_geo_solutions_path):
        shutil.rmtree(new_geo_solutions_path)
        
    config_path = os.path.join(context[CTX_PROP_GEO_INSTALL_PATH],"config.json")
    log("Remove the config path {}".format(config_path))
    if os.path.exists(config_path):
        os.remove(config_path)
    
    return True
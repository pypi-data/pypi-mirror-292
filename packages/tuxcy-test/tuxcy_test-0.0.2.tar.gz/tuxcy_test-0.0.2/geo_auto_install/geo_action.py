from geo_auto_install.utils.g_common import *
from geo_auto_install.utils.g_os import *
from geo_auto_install.utils.g_logger import * 
import time


def stop_geo_services(context, action):
    geo_script = '/geo.bat' if context[CTX_PROP_IS_WINDOWS] else '/geo.sh'
    geo_script_path = context[CTX_PROP_GEO_INSTALL_PATH] + '/bin' + geo_script

    log("Geo services will stop")

    return exec_command([geo_script_path, 'stop'])

def deploy_geo_services(context, action):
    geo_script = '/geo.bat' if context[CTX_PROP_IS_WINDOWS] else '/geo.sh'
    geo_script_path = context[CTX_PROP_GEO_INSTALL_PATH] + '/bin' + geo_script

    log("Deploy geo services")
    
    is_deployed = exec_command([geo_script_path, 'deploy'])

    if not is_deployed:
        log("The deployement failed.")
        return is_deployed
    
        
    is_stopped = exec_command([geo_script_path, 'stop'])
    if not is_stopped:
        log("Stop failed.")
        return is_stopped
    
    
    log("Start Account and Auth services before other services")

    is_account_started = exec_command([geo_script_path, 'account-server start'])
    if not is_account_started :
        log("Account start failed.")
        return is_account_started
    

    is_auth_started = exec_command([geo_script_path, 'aigle-auth start'])
    if not is_auth_started:
        log("Auth start failed.")
        return is_auth_started


    log("Wait a moment ... ({}s)".format(context[CTX_PROP_SERVICE_START_TIMEOUT]))
    time.sleep(context[CTX_PROP_SERVICE_START_TIMEOUT])

    
    log("Start others services")
    is_started = exec_command([geo_script_path, 'start'])
    if not is_started:
        log("An error appear during the start of other geo services")
        return is_started

    log("Wait a moment ... ({}s)".format(context[CTX_PROP_SERVICE_START_TIMEOUT]))
    time.sleep(context[CTX_PROP_SERVICE_START_TIMEOUT])
    
    return True
    
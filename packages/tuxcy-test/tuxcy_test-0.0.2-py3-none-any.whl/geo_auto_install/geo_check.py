from geo_auto_install.utils.g_http import *



def check_geo_services_on_same_host(context, action):
    base_url = "http://localhost"

    urls = {
        "auth": "/auth/version",
        "aws": "/aws/version",
        "portal": "/portal/version",
        "account": "/account/version",
        "aas": "/aas/v1/common/version",
    }
    
    for key, value in urls.items():
        ping_url = base_url + value
        is_alive = ping(ping_url, {})

        if not is_alive:
            log("Service {} is not alive.".format(key))
            return False

    return True

    

def check_geo_services(context, action):
    return check_geo_services_on_same_host(context,action)

def check_internet(context, action):
    url = "http://example.org"
    is_alive = ping(url, {})
    
    return is_alive


def wait_for_confirm(context, action):
    log("Waiting for confirm...")
    
    action = {"code":"confirm"}
    print("USER_ACTION:CONFIRM:"+str(action).replace("'", '"'))
    input()
    
    log("Comfirmed !")
       
    return True
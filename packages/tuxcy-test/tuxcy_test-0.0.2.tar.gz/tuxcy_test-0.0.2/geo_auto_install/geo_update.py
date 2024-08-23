from geo_auto_install.utils.g_common import *
from geo_auto_install.utils.g_os import *
from geo_auto_install.utils.g_http import * 

def run_geo_installer_update(context, action):
    geo_installer_path = context[CTX_PROP_GEO_INSTALLER_PATH]
    geo_install_path = context[CTX_PROP_GEO_INSTALL_PATH]

    try:
        if context[CTX_PROP_GEO_VERSIONS]["geo"]["next"] == context[CTX_PROP_GEO_VERSIONS]["geo"]["current"]:
            return True
    except KeyError as e:
        log("Key error: {}".format(e))
        return False

    log("Run the geo installer [{}]".format(geo_installer_path))
    return exec_command([
        'java',
        '-jar',
        geo_installer_path,
        geo_install_path + '/auto-install.xml'
    ])

def remplace_geo_solutions_artefacts(context, action):
    if CTX_PROP_GEO_EXTENSIONS_TEMP_PATH not in context or context[CTX_PROP_GEO_EXTENSIONS_TEMP_PATH] == "" or context[CTX_PROP_GEO_EXTENSIONS_TEMP_PATH] is None:
        log("There is no extensions.")
        return True
    
    previous_geo_solutions_folder = context[CTX_PROP_GEO_EXTENSIONS_PATH]
    new_geo_solutions_folder = context[CTX_PROP_GEO_EXTENSIONS_TEMP_PATH]
 
    previous_geo_sols_filename = get_files_name_with_ext(previous_geo_solutions_folder, ".jar")
    new_geo_sols_path = get_files(new_geo_solutions_folder)

    if len(previous_geo_sols_filename) != len(new_geo_sols_path):
        log("Something is wrong with geo solutions. It seems it have not the same number of previous and next geo-solutions")

        log_geo_solutions("Previous geo-solutions .jar :", previous_geo_sols_filename)
        log_geo_solutions("New geo-solutions .jar :", new_geo_sols_path)

        return False


    log("Move previous geo solutions to a backup folder ({})".format(new_geo_solutions_folder))
    move_files_from_to(previous_geo_sols_filename, previous_geo_solutions_folder, new_geo_solutions_folder)


    log("Copying new geo-solutions artefacts in the extensions folder ({})".format(previous_geo_solutions_folder))
    copy_files_to(new_geo_sols_path, previous_geo_solutions_folder) 
            
    return True

def log_geo_solutions(title, geo_solutions):
    log(title)
    for geo_sol in geo_solutions:
        log(geo_sol)


def trigger_geo_maintenance(context, action):

    # Asking for auth token
    auth_url = "http://localhost/auth/token"
    
    aas_client_secret = get_aas_client_secret(context)
    data = {
        "grant_type":"client_credentials",
        "client_id" : "geo_aas",
        "client_secret" : aas_client_secret
    }
    
    headers = {}
    payload = {}
    
    response = execute_post_request(auth_url, data, payload, headers)

    if response is None:
        log("The authentication failed!")
        return False

    token = response.get("access_token")

    if not token:
        log("The authentication failed!")
        return False


    # Perform update account endpoint
    headers = {
        'Authorization': "Bearer " + token
    }

    maintenance_url = "http://localhost/account/api/v1/maintenance"
    payload =   {
        "organization": context[CTX_PROP_ORGANISATION_ID],
        "createResources" : context[CTX_PROP_CREATE_RESOURCES],
        "migrateFunctionalities" : context[CTX_PROP_MIGRATE_FUNCTIONNALITIES],
        "migrateFacetResources" : context[CTX_PROP_MIGRATE_FACET_RESOURCES]
    }

    response = execute_post_request(maintenance_url, None, payload, headers)

    if response is None:
        return False

    if response.get("errorNumber") is not None:
        return False

    return True

def get_aas_client_secret(context):
    geo_install_path = context[CTX_PROP_GEO_INSTALL_PATH]
    aas_custom_conf = os.path.join(geo_install_path,"data","conf","aigle-server-custom.conf")
    
    if os.path.exists(aas_custom_conf):
        with open(aas_custom_conf, "r") as file:
            lines = file.readlines()
         
        for line in lines:
            if line.startswith("com.bg.http.auth.clientSecret="):
                return line[len("com.bg.http.auth.clientSecret="):].strip()

from geo_auto_install.utils.g_common import *
from geo_auto_install.utils.g_logger import *
from geo_auto_install.utils.g_http import *
import json

def fetch_current_geo_version(context, action):
    version_file  = os.path.join(context[CTX_PROP_GEO_INSTALL_PATH], "apps/version.geo")
    if os.path.exists(version_file):
        with open(version_file, "r") as file:
            l = file.readline().strip()  
            
            if (len(l) >= 5 and 
                l[0].isdigit() and 
                l[1] == "." and 
                l[2].isdigit() and 
                l[3] == "." and 
                l[4].isdigit()):
                context[CTX_PROP_GEO_VERSIONS] = {
                    "geo" : {
                         "current": l 
                         }
                    }
                log("The current geo version is {}".format(l))
            else :
                log("An error appears during the internal file version reading({})".format(version_file))
                return False
    else : 
        log("The file version.geo does not exists at this path {}, but we need it to perfom the new targeted geo version".format(version_file))
        return False

    return True

def negociate_new_geo_version(context, action):
    versions_file = context[CTX_PROP_GEO_VERSIONS_FILE]
    geo_current_version = context[CTX_PROP_GEO_VERSIONS]["geo"]["current"]
    
    with open(versions_file, "r") as file:
        versions = json.load(file)
        if "geo" in versions and versions["geo"] is not None:
            geo_versions = versions["geo"]
            negocition_mode = context[CTX_PROP_NEGOCIATION_MODE]
            
            if negocition_mode == "LAST_PATCH":
                geo_versions_same_minor = [g for g in geo_versions if g.startswith(geo_current_version[:-1])]
                new_geo_version = geo_versions_same_minor[len(geo_versions_same_minor)-1]
            elif negocition_mode == "LAST_MINOR":
                geo_versions_same_major = [g for g in geo_versions if g.startswith(geo_current_version[:-3])]
                new_geo_version = geo_versions_same_major[len(geo_versions_same_major)-1]
            elif negocition_mode == "LAST_MAJOR":
                new_geo_version = geo_versions[len(geo_versions)-1]

            context[CTX_PROP_GEO_VERSIONS]["geo"]["next"] = new_geo_version
            log("The next geo version will be {}".format(new_geo_version))
        else : 
            log("An error appears during the version file reading ({})".format(versions_file))
    
    return True

def negociate_plugins_versions(context, action):    
    url = "http://localhost/aas/v1/common/version"
    
    log("Fetching plugins on aas ({})".format(url))
    headers = {}
    data = execute_get_request(url, headers)
    
    if "children" in data:
        fetch_new_geo_solutions_versions(context, data["children"])
    
    return True


def fetch_new_geo_solutions_versions(context, children):
    versions_file = context[CTX_PROP_GEO_VERSIONS_FILE]
    geo_targeted_version = context[CTX_PROP_GEO_VERSIONS]["geo"]["next"] 

    with open(versions_file, "r") as file:
        versions = json.load(file)
        
        plugins_versions = versions["plugins"]
        geo_version_plugin_node = plugins_versions[geo_targeted_version[:-2]]
        
        aliases = versions["aliases"]
    
    for child in children:
        name = child["name"]
        version = child["version"]
            
        for key, alias_list in aliases.items():
            if name in alias_list:
                plugin_artefact_name = key
        
        if key is None:
            return False
        
        plugin_versions_available  = geo_version_plugin_node[plugin_artefact_name]
        targeted_plugin_version = plugin_versions_available[len(plugin_versions_available)-1]
        context[CTX_PROP_GEO_VERSIONS][plugin_artefact_name] = {
            "current" : version,
            "next" : targeted_plugin_version
        }
    
    
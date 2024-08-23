from geo_auto_install.utils.g_common import *
from geo_auto_install.utils.g_fs import *
from geo_auto_install.utils.g_logger import *
from geo_auto_install.utils.g_utils import *
import os
import json
import platform


AUTO_INSTALL_FN = lambda ctx: """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<AutomatedInstallation langpack="fra">
    <com.izforge.izpack.panels.checkedhello.CheckedHelloPanel id="CheckedHelloPanel_0"/>
    <com.izforge.izpack.panels.htmllicence.HTMLLicencePanel id="GEO"/>
    <com.izforge.izpack.panels.htmllicence.HTMLLicencePanel id="OtherLicences"/>
    <com.izforge.izpack.panels.target.TargetPanel id="TargetPanel_3">
        <installpath>{GEO_CFG_INSTALL_PATH}</installpath>
    </com.izforge.izpack.panels.target.TargetPanel>
    <com.izforge.izpack.panels.userinput.UserInputPanel id="userConfigPanel1">
        <entry key="userDefined.serverPublicName" value="{GEO_CFG_BASEURL_HOST}"/>
        <entry key="userDefined.dbHost" value="{GEO_CFG_DB_HOST}"/>
        <entry key="userDefined.dbPort" value="{GEO_CFG_DB_PORT}"/>
        <entry key="userDefined.httpProtocol" value="{GEO_CFG_HTTP_SCHEME}"/>
        <entry key="userDefined.dbUser" value="{GEO_CFG_DB_USER}"/>
        <entry key="userDefined.dbPassword" value="{GEO_CFG_DB_PASSWORD}"/>
        <entry key="userDefined.dbType" value="postgresql"/>
        <entry key="userDefined.appsDataDir" value="{GEO_CFG_INSTALL_PATH}/data"/>
    </com.izforge.izpack.panels.userinput.UserInputPanel>
    <com.izforge.izpack.panels.treepacks.TreePacksPanel id="TreePacksPanel_5">
        <pack index="0" name="Main" selected="true"/>
        <pack index="1" name="Extra" selected="false"/>
        <pack index="2" name="Placeholders" selected="true"/>
        <pack index="3" name="GEO Core" selected="true"/>
        <pack index="4" name="Account" selected="true"/>
        <pack index="5" name="Auth" selected="true"/>
        <pack index="6" name="CAS" selected="false"/>
        <pack index="7" name="Server" selected="true"/>
        <pack index="8" name="Portal" selected="true"/>
        <pack index="9" name="Web Server" selected="true"/>
        <pack index="10" name="GDAL" selected="true"/>
        <pack index="11" name="Aigle 4 Proxy" selected="false"/>
        <pack index="12" name="GEO KEY" selected="false"/>
        <pack index="13" name="Swagger" selected="false"/>
    </com.izforge.izpack.panels.treepacks.TreePacksPanel>
    <com.izforge.izpack.panels.summary.SummaryPanel id="SummaryPanel_6"/>
    <com.izforge.izpack.panels.install.InstallPanel id="InstallPanel_7"/>
    <com.izforge.izpack.panels.userinput.UserInputPanel id="userConfigPanel2">
        <entry key="userDefined.dbAuthCreate" value="{GEO_IS_FRESH_INSTALL}"/>
        <entry key="userDefined.dbCJNRSCreate" value="{GEO_IS_FRESH_INSTALL}"/>
        <entry key="userDefined.dbAccountCreate" value="{GEO_IS_FRESH_INSTALL}"/>
    </com.izforge.izpack.panels.userinput.UserInputPanel>
    <com.izforge.izpack.panels.process.ProcessPanel id="ProcessPanel_9"/>
    <com.izforge.izpack.panels.finish.FinishPanel id="FinishPanel_10"/>
</AutomatedInstallation>
""".format(
    GEO_CFG_INSTALL_PATH=ctx[CTX_PROP_GEO_INSTALL_PATH],
    GEO_CFG_BASEURL_HOST=ctx[CTX_PROP_GEO_CFG_BASEURL_HOST],
    GEO_CFG_DB_HOST=ctx[CTX_PROP_GEO_CFG_DB_HOST],
    GEO_CFG_DB_PORT=ctx[CTX_PROP_GEO_CFG_DB_PORT],
    GEO_CFG_HTTP_SCHEME=ctx[CTX_PROP_GEO_CFG_HTTP_SCHEME],
    GEO_CFG_DB_USER=ctx[CTX_PROP_GEO_CFG_DB_USER],
    GEO_CFG_DB_PASSWORD=ctx[CTX_PROP_GEO_CFG_DB_PASSWORD],
    GEO_IS_FRESH_INSTALL=ctx[CTX_PROP_IS_FRESH_INSTALL]
)

def write_auto_install_file(context, action):
    file_path = context[CTX_PROP_GEO_INSTALL_PATH] + '/auto-install.xml'
    parent_dir = os.path.dirname(file_path)

    if os.path.exists(file_path):
        current_date_time = datetime.datetime.now().strftime("%d-%m-%Y-%H:%M")
        backup_file_name = "auto-install-backup-{}.xml".format(current_date_time)
        
        log("{} file already exists. A backup will be created ({})".format(file_path,backup_file_name))
        
        backup_file_path = context[CTX_PROP_GEO_INSTALL_PATH] + "/" + backup_file_name
        
        with open(file_path, 'r') as original_file:
            content = original_file.read()
            with open(backup_file_path, 'w') as backup_file:
                backup_file.write(content)
        
        log("Even if the auto-install.xml file exists, it will be rewriten to ensure the file veracity")

    if not os.path.exists(parent_dir):
        os.makedirs(parent_dir)
    

    log("File auto-install.xml generation")
    with open(file_path, 'w') as file:
            content = AUTO_INSTALL_FN(context)
            file.write(content)

    return True

def parse_config_file(config_file):
    try:
        with open(config_file, "r") as json_file:
            data = json.load(json_file)
    except json.JSONDecodeError:
        print("Error: The file is not a valid JSON file.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

    try:
        context = {
            # Context arguments
            CTX_PROP_IS_WINDOWS: platform.system() == "Windows",
            CTX_PROP_SERVICE_START_TIMEOUT: data["CTX_PROP_SERVICE_START_TIMEOUT"],
            
            # GEO Install parameters
            CTX_PROP_GEO_INSTALL_PATH: data["CTX_PROP_GEO_INSTALL_PATH"],
            CTX_PROP_GEO_INSTALLER_PATH: "",
            CTX_PROP_GEO_EXTENSIONS_PATH: data["CTX_PROP_GEO_EXTENSIONS_PATH"],
            CTX_PROP_GEO_EXTENSIONS_TEMP_PATH: "",
            CTX_PROP_GEO_VERSIONS: None,
            CTX_PROP_GEO_VERSIONS_FILE: "",
            CTX_PROP_NEGOCIATION_MODE: data["CTX_PROP_NEGOCIATION_MODE"],
            CTX_PROP_LOG_DEST:  data["CTX_PROP_LOG_DEST"],
            CTX_PROP_GEO_CFG_BASEURL_HOST: data["CTX_PROP_GEO_CFG_BASEURL_HOST"],

            CTX_PROP_ORGANISATION_ID : None,
            CTX_PROP_CREATE_RESOURCES : data["CTX_PROP_CREATE_RESOURCES"],
            CTX_PROP_MIGRATE_FUNCTIONNALITIES : data["CTX_PROP_MIGRATE_FUNCTIONNALITIES"],
            CTX_PROP_MIGRATE_FACET_RESOURCES : data["CTX_PROP_MIGRATE_FACET_RESOURCES"],

            CTX_PROP_GEO_CFG_DB_HOST: data["CTX_PROP_GEO_CFG_DB_HOST"],
            CTX_PROP_GEO_CFG_DB_PORT: data["CTX_PROP_GEO_CFG_DB_PORT"],
            CTX_PROP_GEO_CFG_DB_USER: data["CTX_PROP_GEO_CFG_DB_USER"],
            CTX_PROP_GEO_CFG_DB_PASSWORD: data["CTX_PROP_GEO_CFG_DB_PASSWORD"],
            CTX_PROP_GEO_CFG_HTTP_SCHEME: data["CTX_PROP_GEO_CFG_HTTP_SCHEME"],
            CTX_PROP_IS_FRESH_INSTALL: data["CTX_PROP_IS_FRESH_INSTALL"]
        }
    except KeyError as e:
        print(f"Error: Missing expected key in the config file: {e}")
        return None
    
    return context 


def generate_config():

    dictionary = {
        "CTX_PROP_SERVICE_START_TIMEOUT": 20,

        "CTX_PROP_GEO_INSTALL_PATH": "/opt/geo",

        "CTX_PROP_GEO_CFG_BASEURL_HOST": "localhost",
        "CTX_PROP_CREATE_RESOURCES" : True,
        "CTX_PROP_MIGRATE_FUNCTIONNALITIES" : True,
        "CTX_PROP_MIGRATE_FACET_RESOURCES" : True,

        "CTX_PROP_GEO_CFG_DB_HOST": "db",
        "CTX_PROP_GEO_CFG_DB_PORT": "5432",
        "CTX_PROP_GEO_CFG_DB_USER": "geo",
        "CTX_PROP_GEO_CFG_DB_PASSWORD": "geo",
        "CTX_PROP_GEO_CFG_HTTP_SCHEME": "http",


        "CTX_PROP_GEO_EXTENSIONS_PATH": "",
        "CTX_PROP_LOG_DEST": "",
        
        "CTX_PROP_NEGOCIATION_MODE" : "LAST_PATCH",
        
        "CTX_PROP_IS_FRESH_INSTALL" : False
    }

    language = get_language_choice()    
    
    # CTX_PROP_SERVICE_START_TIMEOUT
    value = input_str(get_message("ask.start.timeout", language, "20 sec"))
    if value == "":
        value = 20
    else:
        while str_to_int(value) is None:
            value = input_str(get_message("ask.start.timeout", language, "20 sec"))
    dictionary["CTX_PROP_SERVICE_START_TIMEOUT"] = value

    # CTX_PROP_GEO_INSTALL_PATH
    value = input_str(get_message("ask.install.path", language, "/opt/geo"))
    if value != "":
        while not os.path.isdir(value):
            value = input_str(get_message("ask.install.path.error", language, "/opt/geo"))
        dictionary["CTX_PROP_GEO_INSTALL_PATH"] = value
    else:
        dictionary["CTX_PROP_GEO_INSTALL_PATH"] = "/opt/geo"
    
    # CTX_PROP_LOG_DEST
    dictionary["CTX_PROP_LOG_DEST"] = os.path.join(dictionary["CTX_PROP_GEO_INSTALL_PATH"], "data/logs")
    dictionary["CTX_PROP_GEO_EXTENSIONS_PATH"] = os.path.join(dictionary["CTX_PROP_GEO_INSTALL_PATH"], "extensions")

    # CTX_PROP_GEO_CFG_BASEURL_HOST
    value = input_str(get_message("ask.base.url", language, "localhost"))
    dictionary["CTX_PROP_GEO_CFG_BASEURL_HOST"] = value if value != "" else "localhost"
    
    # CTX_PROP_GEO_CFG_HTTP_SCHEME
    value = input_str(get_message("ask.http.scheme", language, "http"))
    dictionary["CTX_PROP_GEO_CFG_HTTP_SCHEME"] = value if value != "" else "http"

    # CTX_PROP_GEO_CFG_DB_HOST
    value = input_str(get_message("ask.db.host", language, "localhost"))
    dictionary["CTX_PROP_GEO_CFG_DB_HOST"] = value if value != "" else "localhost"
    
    # CTX_PROP_GEO_CFG_DB_PORT
    value = input_str(get_message("ask.db.port", language, "5432"))
    if value != "":
        while str_to_int(value) is None:
            value = input_str(get_message("ask.db.port", language, "5432"))
    dictionary["CTX_PROP_GEO_CFG_DB_PORT"] = str_to_int(value) if str_to_int(value) is not None else 5432
    
    # CTX_PROP_GEO_CFG_DB_USER
    value = input_str(get_message("ask.db.user", language))
    while value == "":
        value = input_str(get_message("ask.db.user", language))
    dictionary["CTX_PROP_GEO_CFG_DB_USER"] = value

    # CTX_PROP_GEO_CFG_DB_PASSWORD
    value = input_str(get_message("ask.db.password", language))
    while value == "":
        value = input_str(get_message("ask.db.password", language))
    dictionary["CTX_PROP_GEO_CFG_DB_PASSWORD"] = value

    # CTX_PROP_CREATE_RESOURCES
    value = input_str(get_message("ask.update.resources", language))
    while value not in ["y", "n"]:
        value = input_str(get_message("ask.update.resources", language))
    dictionary["CTX_PROP_CREATE_RESOURCES"] = value == "y"

    # CTX_PROP_MIGRATE_FUNCTIONNALITIES
    value = input_str(get_message("ask.migrate.resources", language))
    while value not in ["y", "n"]:
        value = input_str(get_message("ask.migrate.resources", language))
    dictionary["CTX_PROP_MIGRATE_FUNCTIONNALITIES"] = value == "y"

    # CTX_PROP_MIGRATE_FACET_RESOURCES
    value = input_str(get_message("ask.update.indexing", language))
    while value not in ["y", "n"]:
        value = input_str(get_message("ask.update.indexing", language))
    dictionary["CTX_PROP_MIGRATE_FACET_RESOURCES"] = value == "y"
    
    
    path = os.path.join(dictionary["CTX_PROP_GEO_INSTALL_PATH"],"config.json")
    
    with open(path, 'w') as f:
        json.dump(dictionary, f, indent=4) 

    print("{} has been writen".format(path))

    return path

def get_language_choice():
    while True:
        value = input_str("Choose the language / Choisissez la langue (1: fr, 2: en): ")
        if value in ["1", "2"]:
            return "fr" if value == "1" else "en"
        else:
            print("Invalid choice. Please enter 1 for French (FR) or 2 for English (EN).")
            
def get_message(key, language, *args):
    return DICT_LANGUAGE.get(key, {}).get(language, "Message not found").format(*args) + " "

def input_str(message):
    try: 
        value = raw_input(message)
    except Exception: 
        value = input(message)
        
    return value


def write_ctx_file(context, action):
    ctx_file = context[CTX_PROP_CTX_FILE]
    try:
        with open(ctx_file, "w") as json_file:
            json.dump(context, json_file, indent=4)
        return True
    except TypeError:
        print("Error: The context provided is not serializable to JSON.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def parse_ctx_file(ctx_file):
        try:
            with open(ctx_file, "r") as json_file:
                data = json.load(json_file)
                return data
        except json.JSONDecodeError:
            print("Error: The file is not a valid JSON file.")
            return None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None
        
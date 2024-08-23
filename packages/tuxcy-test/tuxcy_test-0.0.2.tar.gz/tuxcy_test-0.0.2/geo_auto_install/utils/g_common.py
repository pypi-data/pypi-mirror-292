### CONSTS ###

## >>> REGEX
SAAS_VERSIONS_FILE = 'https://geoservices.business-geografic.com/maintenance/geo_versions_compat.json'
SEMVER_PATTERN = r'^(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$'
## >>> CONTEXT PROPS
# Context arguments
CTX_PROP_IS_WINDOWS = 'IS_WINDOWS'
CTX_PROP_SERVICE_START_TIMEOUT = 'SERVICE_START_TIMEOUT'

# GEO Install parameters
CTX_PROP_GEO_INSTALL_PATH = 'GEO_INSTALL_PATH'
CTX_PROP_GEO_INSTALLER_PATH = 'GEO_INSTALLER_PATH'
CTX_PROP_GEO_EXTENSIONS_PATH = 'GEO_EXTENSIONS_PATH'
CTX_PROP_GEO_EXTENSIONS_TEMP_PATH = 'GEO_EXTENSIONS_TEMP_PATH'
CTX_PROP_LOG_DEST = 'LOG_DEST'
CTX_PROP_ORGANISATION_ID = 'ORGANISATION_ID'
CTX_PROP_CREATE_RESOURCES = 'CREATE_RESOURCES'
CTX_PROP_MIGRATE_FUNCTIONNALITIES = 'MIGRATE_FUNCTIONNALITIES'
CTX_PROP_MIGRATE_FACET_RESOURCES = 'MIGRATE_FACET_RESOURCES'
CTX_PROP_GEO_INSTALL_APPS = "GEO_INSTALL_APPS"
CTX_PROP_GEO_INSTALL_DATA = "GEO_INSTALL_DATA"
CTX_PROP_GEOSOL_DIR_PATH = 'GEOSOL_DIR_PATH'
CTX_PROP_GEO_INSTALLER_BASEPATH = "GEO_INSTALLER_BASEPATH"
CTX_PROP_GEO_CFG_INSTALL_PATH = "GEO_CFG_INSTALL_PATH"
CTX_PROP_GEO_CFG_BASEURL_HOST = "GEO_CFG_BASEURL_HOST"
CTX_PROP_GEO_CFG_DB_HOST = "GEO_CFG_DB_HOST"
CTX_PROP_GEO_CFG_DB_PORT = "GEO_CFG_DB_PORT"
CTX_PROP_GEO_CFG_DB_USER = "GEO_CFG_DB_USER"
CTX_PROP_GEO_CFG_DB_PASSWORD = "GEO_CFG_DB_PASSWORD"
CTX_PROP_GEO_CFG_HTTP_SCHEME = "GEO_CFG_HTTP_SCHEME"

# Executions data
CTX_PROP_GEO_VERSIONS = 'GEO_VERSIONS'
CTX_PROP_GEO_VERSIONS_FILE = 'GEO_VERSIONS_FILE'
CTX_PROP_NEGOCIATION_MODE = 'CTX_PROP_NEGOCIATION_MODE'
CTX_PROP_GEO_AVAILABLE_VERSIONS = 'GEO_AVAILABLE_VERSIONS'
CTX_PROP_GEOSOL_AVAILABLE_VERSIONS = 'GEO_AVAILABLE_VERSIONS'
CTX_PROP_GEOSOL_TARGET_VERSIONS = 'GEOSOL_TARGET_VERSIONS'

## >>> CONFIG PROPS
CONFIG_GEO_PROP_ID = 'CONFIG_GEO_PROP_ID'
CONFIG_GEO_PROP_INSTALL_PATH = 'CONFIG_GEO_PROP_INSTALL_PATH'
CONFIG_GEO_PROP_USER = 'CONFIG_GEO_PROP_USER'

CTX_PROP_IS_FRESH_INSTALL = 'CTX_PROP_IS_FRESH_INSTALL'

CTX_PROP_RUN_PROFILE = 'CTX_PROP_RUN_PROFILE'
CTX_PROP_CTX_FILE = 'CTX_PROP_CTX_FILE'


DICT_LANGUAGE = {
    "ask.start.timeout": {
        "en": "Service start timeout ({}):",
        "fr": "Temps d'attente du lancement des services ({}):"
    },
    "ask.install.path": {
        "en": "Installation path ({}):",
        "fr": "Chemin d'installation ({}):"
    },
    "ask.install.path.error": {
        "en": "Wrong path! Try another installation path:",
        "fr": "Chemin incorrect! Essayez un autre chemin d'installation:"
    },
    "ask.base.url": {
        "en": "Base URL ({}):",
        "fr": "URL de base ({}):"
    },
       "ask.http.scheme": {
        "en": "HTTP scheme (http):",
        "fr": "Schema HTTP (http):"
    },
    "ask.db.host": {
        "en": "DB host ({}):",
        "fr": "Hote de la base de donnees ({}):"
    },
    "ask.db.port": {
        "en": "DB port ({}):",
        "fr": "Port de la base de donnees ({}):"
    },
    "ask.db.user": {
        "en": "DB user:",
        "fr": "Utilisateur de la base de donnees:"
    },
    "ask.db.password": {
        "en": "DB password:",
        "fr": "Mot de passe de la base de donnees:"
    },
    "ask.update.resources": {
        "en": "Update default resources (y or n):",
        "fr": "Mettre a jour les ressources par defaut (y ou n):"
    },
    "ask.migrate.resources": {
        "en": "Migrate resources (y or n):",
        "fr": "Migrer les ressources (y ou n):"
    },
    "ask.update.indexing": {
        "en": "Update resource indexing (y or n):",
        "fr": "Mettre a jour l'indexation des ressources (y ou n):"
    },
    "input.invalid": {
        "en": "Invalid input. Please try again:",
        "fr": "Entree invalide. Veuillez reessayer:"
    }
}
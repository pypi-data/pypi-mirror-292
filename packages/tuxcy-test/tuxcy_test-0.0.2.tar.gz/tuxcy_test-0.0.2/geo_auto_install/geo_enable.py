from geo_auto_install.utils.g_common import *


# Generic enabling functions

def is_not_fresh_install(context, action):
    return not context[CTX_PROP_IS_FRESH_INSTALL]

def is_fresh_install(context, action):
    return context[CTX_PROP_IS_FRESH_INSTALL]

def is_run_profile_p1(context, action):
    return context[CTX_PROP_RUN_PROFILE] == "p1"

def is_run_profile_p2(context, action):
    return context[CTX_PROP_RUN_PROFILE] == "p2"

def is_run_profile_normal(context, action):
    return context[CTX_PROP_RUN_PROFILE] == None

def is_run_profile_normal_or_p1(context, action):
    return is_run_profile_normal(context, action) or is_run_profile_p1(context, action)

def is_run_profile_normal_or_p2(context, action):
    return is_run_profile_normal(context, action) or is_run_profile_p2(context, action)



# --- Functions that specify whether an action should be triggered or not. ----

# -- Part 1 --
def should_check_internet(context, action):
    return is_run_profile_normal_or_p1(context, action)

def should_fetch_version_file(context, action):
    return is_run_profile_normal_or_p1(context, action)

def should_fetch_current_geo_version(context, action):
    return is_not_fresh_install(context, action) and is_run_profile_normal_or_p1(context, action)

def should_negociate_geo_next_version(context, action):
    return is_not_fresh_install(context, action) and is_run_profile_normal_or_p1(context, action)

def should_check_services_before_installer(context, action):
    return is_not_fresh_install(context, action) and is_run_profile_normal_or_p1(context, action)

def should_negociate_plugins_versions(context, action):
    return is_not_fresh_install(context, action) and is_run_profile_normal_or_p1(context, action)

def should_build_auto_install_file(context, action):
    return is_run_profile_normal_or_p1(context, action)

def should_download_geo_installer(context, action):
    return is_run_profile_normal_or_p1(context, action)

def should_download_geo_solutions(context, action):
    return is_run_profile_normal_or_p1(context, action)

def should_write_context(context, action):
    return is_run_profile_p1(context, action)

def should_wait_for_confirm(context, action):
    return is_run_profile_p1(context, action)

# -- Part 2 --

def should_stop_geo_services(context, action):
    return is_not_fresh_install(context, action) and is_run_profile_normal_or_p2(context, action)

def should_start_geo_installer(context, action):
    return is_run_profile_normal_or_p2(context, action)

def should_remplace_geo_solutions(context, action):
    return is_not_fresh_install(context, action) and is_run_profile_normal_or_p2(context, action)

def should_deploy(context, action):
    return is_run_profile_normal_or_p2(context, action)

def should_check_services_after_installer(context, action):
    return is_run_profile_normal_or_p2(context, action)

def should_run_maintenance(context, action):
    return is_not_fresh_install(context, action) and is_run_profile_normal_or_p2(context, action)

def should_clean(context, action):
    return is_run_profile_normal_or_p2(context, action)
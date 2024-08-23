from geo_auto_install.geo_config import *
from geo_auto_install.geo_check import *
from geo_auto_install.geo_download import *
from geo_auto_install.utils.g_logger import *
from geo_auto_install.geo_action import *
from geo_auto_install.geo_update import *
from geo_auto_install.geo_clean import * 
from geo_auto_install.geo_versions import *
from geo_auto_install.geo_signal import *
from geo_auto_install.geo_enable import * 
import click


# Steps List
defaultSteps = [
    ## -- Part 1 --
    [
        {
            'id': 'CHECK_INTERNET',
            'name': 'Verify whether the machine has internet access',
            'enable': should_check_internet,
            'handle': check_internet,
        }
    ],
    [
        {
            'id': 'CHECK_SERVICES',
            'name': 'Check if all geo services are on the current machine',
            'enable': should_check_services_before_installer,
            'handle': check_geo_services_on_same_host,
        }
    ],
    [
        {
            'id': 'FETCH_VERSIONS_FILE',
            'name': 'Fetch the version file',
            'enable': should_fetch_version_file,
            'handle': download_version_file,
        }
    ],
    # [
    #     {
    #         'id': 'GEO_VERSION_CHOICE',
    #         'name': 'Choose the version to install',
    #         'enable': is_fresh_install,
    #         'handle': choose_geo_version,
    #     }
    # ],
    [
        {
            'id': 'FETCH_CURRENT_GEO_VERSION',
            'name': 'Retrieve the current geo version from a internal geo file',
            'enable': should_fetch_current_geo_version,
            'handle': fetch_current_geo_version,
        }
    ],
    [
        {
            'id': 'GEO_VERSION_NEGOCIATION',
            'name': 'Negotiate the geo version that will be used to update',
            'enable': should_negociate_geo_next_version,
            'handle': negociate_new_geo_version,
        }
    ],
    [
        {
            'id': 'GEO_PLUGINS_VERSIONS_NEGOCIATION',
            'name': 'Fetch the plugins versions and negociate their version',
            'enable': should_negociate_plugins_versions,
            'handle': negociate_plugins_versions,
        }
    ],
    [
        {
            'id': 'AUTO_INSTALL_FILE',
            'name': "Verify whether the file auto-install.xml exists in the installation path. If it doesn't exist, generate it.",
            'enable': should_build_auto_install_file,
            'handle': write_auto_install_file,
        }
    ],
    [
        {
            'id': 'DOWNLOAD_GEO_INSTALLER',
            'name': 'Download the correct intaller',
            'enable': should_download_geo_installer,
            'handle': download_geo_installer,
        }
    ],
    [
        {
            'id': 'DOWNLOAD_GEO_SOLUTIONS',
            'name': 'Download geo solutions',
            'enable': should_download_geo_solutions,
            'handle': download_geo_solutions,
        }
    ],
    [
        {
            'id': 'WRITE_CONTEXT',
            'name': 'Write the context file if we are in separate execution',
            'enable': should_write_context,
            'handle': write_ctx_file,
        }
    ],
    [
        {
            'id': 'WAIT_FOR_CONFIRM',
            'name': 'Wait for confirm in separate execution',
            'enable': should_wait_for_confirm,
            'handle': wait_for_confirm,
        }
    ],
    
    ## -- Part 2 --
    
    [
        {
            'id': 'STOP_GEO_SERVICES',
            'name': 'Stop geo services before update',
            'enable': should_stop_geo_services,
            'handle': stop_geo_services,
        }
    ],
    [
        {
            'id': 'GEO_INSTALLER_UPDATE',
            'name': 'Start the geo installer update ',
            'enable': should_start_geo_installer,
            'handle': run_geo_installer_update,
        }
    ],
    [
        {
            'id': 'GEO_SOL_REPLACE',
            'name': 'Replace geo solutions artefacts',
            'enable': should_remplace_geo_solutions,
            'handle': remplace_geo_solutions_artefacts,
        }
    ],
    [
        {
            'id': 'GEO_DEPLOY',
            'name': 'Deploy and start geo services',
            'enable': should_deploy,
            'handle': deploy_geo_services,
        }
    ],
    [
        {
            'id': 'CHECK_GEO_SERVICES',
            'name': 'Check GEO Services',
            'enable': should_check_services_after_installer,
            'handle': check_geo_services,
        }
    ],
    [
        {
            'id': 'RUN_GEO_MAINTENANCE',
            'name': 'Run GEO maintenance endpoint',
            'enable': should_run_maintenance,
            'handle': trigger_geo_maintenance,
        }
    ],
    [
        {
            'id': 'CLEAN_UPDATE_FILES',
            'name': 'The final step is to clean up some files that were created by the update system.',
            'enable': should_clean,
            'handle': clean_updates_files,
        }
    ]
]


def summary(actions_result):
    log("Action summary :", Color.DARKCYAN_UNDERLINE)
    for key in actions_result:
        value = actions_result[key]
        
        color = Color.GREEN if value else Color.RED
        res = "success" if value else "failed"

        log("{} : {}".format(key,res),color)


def run(config_file, run_profile=None, steps=defaultSteps, context_file=None):
    # Signal init
    config_signal()
    
    context = get_context(config_file=config_file, run_profile=run_profile, context_file=context_file)
    if context is None:
        print("Error : Context is None")
        sys.exit(1)
        
    # Logger init
    Logger(context)

    log("-- GEO AUTOINSTALL --")
    log("PPID : {}  PID : {}".format(os.getppid(), os.getpid()))
    actions_result = {}
    
    should_continue = True

    for step in steps:
        for action in step:
            should_continue = exec_action(action, context, actions_result)

            if not should_continue:
                log("Action {} has failed!".format(action['id']), Color.RED)  
                break
            else :
                log("Action {} OK".format(action['id']), Color.PURPLE)  
            
        
        if not should_continue:
            break


    summary(actions_result)
    sys.exit(0)

def exec_action(action, context, actions_result):
    enable_fn = action['enable']
    handle_fn = action['handle']

    should_handle = True
    if not enable_fn(context, action):
        should_handle = False
    
    should_continue = True    
    if should_handle:
        log("--> Action {} : {} ".format(action['id'], action['name']), Color.YELLOW_UNDERLINE)   
        
        is_successed = handle_fn(context, action)
        actions_result[action['id']] = is_successed
        
        # If the action failed we wont continue
        should_continue = is_successed

    return should_continue

def get_context(config_file, run_profile, context_file):
    if not run_profile or run_profile == "p1":   # Parse the context
        context = parse_config_file(config_file)
        context[CTX_PROP_RUN_PROFILE] = run_profile
        context[CTX_PROP_CTX_FILE] = context_file
    elif run_profile == "p2":
        context = parse_ctx_file(context_file)
        context[CTX_PROP_RUN_PROFILE] = run_profile
        context[CTX_PROP_CTX_FILE] = context_file
        
    return context

@click.command()
@click.option('-c', '--config', help='The config file', type=str)
@click.option('-p1', flag_value=True, help='Sometimes we have to separate the update execution. This option will execute the first part.')
@click.option('-p2', flag_value=True, help='Sometimes we have to separate the update execution. This option will execute the second part.')
@click.option('-ctx', help='Path to the context file when using separate execution.', type=str)
def main(config, p1, p2, ctx):
    """
    Acceptable config:\n
        geo-auto-install \n
        geo-auto-install -c path/to/config \n
        geo-auto-install -c path/to/config -p1 -ctx path/to/context \n
        geo-auto-install -p2 -ctx path/to/context \n

    Error cases:\n
        geo-auto-install -p1 \n
            Raises UsageError: Cannot use -p1 and -p2 without -ctx option.\n
        geo-auto-install -p2 \n
            Raises UsageError: Cannot use -p1 and -p2 without -ctx option.\n
        geo-auto-install -p1 -p2 -ctx path/to/context \n
            Raises UsageError: Cannot use -p1 and -p2 options together.\n
        geo-auto-install -p2 -ctx path/to/non_existing_context \n
            Raises UsageError: Cannot use -p2 option if the context file does not exist.\n
        geo-auto-install -c path/to/config -p2 \n
            Raises UsageError: Cannot use -p2 with -c option.\n
        geo-auto-install -c path/to/non_existing_config \n
            Raises UsageError: The given configuration file doesn't exist.\n
    """
    validate_options(p1, p2, config, ctx)
    run_profile, run_cli = determine_execution_mode(p1, p2, ctx, config)

    if run_cli:
        run(generate_config(), run_profile=run_profile, context_file=ctx)
    else:
        run(config, run_profile=run_profile, context_file=ctx)
        
def validate_options(p1, p2, config, ctx):
    """Validate the options and raise usage errors if invalid."""
    if (p1 or p2) and not ctx:
        raise click.UsageError("Cannot use -p1 and -p2 without -ctx option.")
    
    if p1 and p2:
        raise click.UsageError("Cannot use -p1 and -p2 options together.")
    
    if p2 and ctx and not os.path.isfile(ctx):
        raise click.UsageError("Cannot use -p2 option if the context file does not exist.")
    
    if config and p2:
        raise click.UsageError("Cannot use -p2 with -c option.")
    
    if config and not os.path.isfile(config):
        raise click.UsageError("The given configuration file doesn't exist.")
    
def determine_execution_mode(p1, p2, ctx, config):
    """Determine the execution mode based on options."""
    
    run_profile = None
    run_cli = None
    
    if p1:
        run_profile = "p1"
    elif p2:
        run_profile = "p2"
    
    if not config and not p2:
        run_cli = True
    else :
        run_cli = False        
    
    return run_profile, run_cli


if __name__ == '__main__':
    main()
    
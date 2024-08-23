# Geo Auto Install

This project aims to simplify the updating of the GEO platform.

## Project Structure

The repository is organized as follows:

- **`geo_auto_install/`**  

- **`scripts/`**  

- **`tests/`**  

- **`docker-testing/`**  

Note: All subfolders are documented within their respective directories.

# Usage
To test this script, you need to build and install it via pip.

To build the script, use the following command:

```bash
python -m build  # run this in the parent directory of the project
```

After building, a .whl file will be generated in the newly created dist subdirectory.

You can install this file using:

```bash
pip install dist/filename.whl
```

And now you normally execute the following command to launch the script:

```bash
geo-auto-install
```

### Shortcuts :
```bash
build_install.sh # to build and install
build_install_test.sh # to build, clean install and launch units tests
```


# Interaction Between Geo-Account and This Script

To acheive the best communication with geo-account during the auto-update, we decided to give the possibility to execute the geo-auto-script in a separate execution mode.

Indeed, we can distinct two major phase during a gea-auto-install execution : 

- **Configuration and Download Phase**: The initial phase involves configuring and downloading the necessary components.
- **Artifact Replacement Phase**: The second phase involves replacing the existing artifacts.

*Notice that you can see each of these steps in the file autoinstall.py*

During the first phase, geo-account must interact with the script. Since geo-account is programmed in Java 17 (as of the current writing), it is not possible to attach a process via its PID or to detach a process.

What does this mean? When the script stops the geo-account service, as well as other geo services, to update them, it will also terminate itself. This is due to the inability to manage processes in the way needed to keep the script running while updating.

To address this, when a user start a update, geo-account will start the first part of the script cleanly using the Java classic API. During this phase, geo-account and the script will communicate via a custom protocol, which will be detailed later.

After the first phase, the geo-account will re-initiate the script using an intermediate Python script. This Python script is capable of launching detached or daemon processes, which allows the script to continue running while the geo-account services are being updated.

### Custom protocol 
During the first phase, geo-account will listen to the script's standard output for a specific sequence. The script may, if necessary, request user actions such as confirmation or download links. These requests will appear in the following forms:

```
USER_ACTION:NEXTCLOUD:{"code":"link_nextcloud","folder":"/path/to/file","filename":"test.jar"}
USER_ACTION:CONFIRM
...
```

- `USER_ACTION` : this sequence will indicate to geo-account that it needs to provide input to the script's standard input.
- `NEXTCLOUD` ou `CONFIRM` this sequence will indicate the request type
- Additionally, a JSON should be used to successfully accomplish the request.


### Which commands does geo-account use to launch geo-auto-install?

For the first phase :
```bash
geo-auto-install -c /path/to/the/config/file -p1 -ctx /path/to/the/context/file
```

For the second phase :
```bash
python launch_detached_update.py -p2 -ctx /path/to/the/context/file
```

- `-c` tag is used to provide the config file which avoid to complete a form
- `-p1` or `-p2` tags allows to launch the first or the second part of the script
- `-ctx` tag must be defined in a separate execution to pass the running context from one execution to another.

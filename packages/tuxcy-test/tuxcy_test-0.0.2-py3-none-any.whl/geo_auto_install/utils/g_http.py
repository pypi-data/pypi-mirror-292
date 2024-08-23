from geo_auto_install.utils.g_common import *
from geo_auto_install.utils.g_logger import *
import requests

##
## HTTP ACTIONS
##

def execute_get_request(url, headers):
    try:
        log("running {}".format(url))
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for 4xx or 5xx errors
        data = response.json()
        return data
    except requests.exceptions.HTTPError as e:
        log(">> Error, Status:{}: {}".format(response.status_code, response.reason))
    except requests.exceptions.RequestException as e:
        log("ERROR: {}".format(e))
    except Exception as e:
        log("ERROR: {}".format(e))

def execute_post_request(url, data, payload, headers):
    try:
        log("running {}".format(url))
        response = requests.post(url, data=data, params=payload, headers=headers)
        response.raise_for_status()  
        data = response.json()
        return data
    except requests.exceptions.HTTPError as e:
        log(">> Error, Status:{}: {}".format(response.status_code, response.reason))
    except requests.exceptions.RequestException as e:
        log("ERROR2: {}".format(e))
        return None
    except Exception as e:
        log("ERROR1: {}".format(e))

def execute_download_request(url, headers, target_path):
    try:
        log("running {}".format(url))
        response = requests.get(url, headers=headers, stream=True)
        response.raise_for_status()  

        with open(target_path, 'wb') as out_file:
            for chunk in response.iter_content(chunk_size=1024 * 1000 * 5):
                if chunk:
                    out_file.write(chunk)

        log("Downloaded file from '{}' to '{}'".format(url, target_path))
        return True
    except requests.exceptions.HTTPError as e:
        log(">> Error, Status:{}: {}".format(response.status_code, response.reason))
    except requests.exceptions.RequestException as e:
        log("ERROR: {}".format(e))
        return False
    except Exception as e:
        log("ERROR: {}".format(e))

def ping(url, headers):
    try:
        log("Ping {}".format(url))
        response = requests.get(url, headers=headers)
        return response.status_code == 200
    except requests.exceptions.HTTPError as e:
        log(">> Error, Status:{}: {}".format(response.status_code, response.reason))
    except requests.exceptions.RequestException as e:
        log("ERROR: {}".format(e))
    except Exception as e:
        log("ERROR: {}".format(e))

def session_download_request(session, url, params, target_path):
    print("running {}".format(url))
    try:
        response = session.post(url, stream=True, params=params)
        response.raise_for_status()
        
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        with open(target_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        
        print("File saved successfully at {}".format(target_path))

    except requests.exceptions.RequestException as e:
        print("ERROR: {}".format(e))

def session_get_request(session, url, headers):
    log("running {}".format(url))
    try:
        response = session.get(url, headers=headers)
        response.raise_for_status()
        
        return response.text 
    except requests.exceptions.RequestException as e:
        log("ERROR: {}".format(e))
        return False
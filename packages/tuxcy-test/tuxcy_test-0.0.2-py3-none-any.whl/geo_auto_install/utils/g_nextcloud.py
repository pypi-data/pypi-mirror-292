from geo_auto_install.utils.g_http import *
import json

next_cloud_download_bas_url = "https://telechargement.cirilgroup.com/index.php/s/"
next_cloud_download_suffix = "/download"
next_cloud_download_auth_suffix = "/authenticate/downloadshare"
next_cloud_get_token_url =  "https://telechargement.cirilgroup.com/index.php/csrftoken"

def get_nextcloud_token(session):
    response = session_get_request(session,url=next_cloud_get_token_url, headers={})
    return json.loads(response)["token"]  
    
def check_nextcloud_url(url_to_test,token):
    build_url = next_cloud_download_bas_url + token
    if url_to_test == build_url:
        return True 
    else :
        return False

def download_nextcloud(url, password, target_path):
    url_temp = url.rstrip('/')
    elts = url_temp.split('/')
    share_token = elts[-1]
    
    if not check_nextcloud_url(url_temp,share_token):
        return False
    
    if password != "":
        session = requests.Session()
        
        # https://telechargement.cirilgroup.com/index.php/s/{shareID}/download
        download_url = next_cloud_download_bas_url + share_token + next_cloud_download_suffix
        session_get_request(session=session, url=download_url, headers={})
        
        # https://telechargement.cirilgroup.com/index.php/csrftoken
        token = get_nextcloud_token(session)
        
        
        # https://telechargement.cirilgroup.com/index.php/s/{shareID}/authenticate/downloadshare
        download_auth_url = next_cloud_download_bas_url + share_token + next_cloud_download_auth_suffix
        params = {
            "requesttoken" : token ,
            "password" : password,
            "sharingToken" : share_token,
            "sharingType" : 3
        }   
        session_download_request(session=session, url=download_auth_url,params=params, target_path=target_path)
    else :
        # https://telechargement.cirilgroup.com/index.php/s/{shareID}/download
        download_url = next_cloud_download_bas_url + share_token + next_cloud_download_suffix
        execute_download_request(url=download_url, headers={}, target_path=target_path)
        
    return True
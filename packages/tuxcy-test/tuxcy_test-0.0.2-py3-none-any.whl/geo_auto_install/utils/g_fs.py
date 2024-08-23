from geo_auto_install.utils.g_common import *

def safe_append(filename, content):
    try:
        with open(filename, "a") as file:
            file.write(content+"\n")
    except FileNotFoundError:
        print("File '{}' not found!".format(filename))
    except Exception as e:
        print("An error occurred:", e)